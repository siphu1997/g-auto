from __future__ import annotations

import logging
import queue
import threading
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

from core.config import AppSettings, SettingsManager
from core.device import AdbDeviceController, DeviceController
from core.logging import ArtifactStore, configure_logging, read_recent_logs
from core.models import BotStatus, Observation, StateName, TaskResult
from core.recovery import RecoveryManager
from core.state_machine import BotStateMachine
from core.task_engine import TaskEngine
from core.vision import VisionService


class BotRuntime:
    def __init__(
        self,
        config_dir: str | Path = "config",
        device: DeviceController | None = None,
        vision: VisionService | None = None,
    ) -> None:
        self.settings_manager = SettingsManager(config_dir)
        self._external_device = device is not None
        self._external_vision = vision is not None

        configure_logging(self.settings)
        self.logger = logging.getLogger("runtime")
        self.artifacts = ArtifactStore(self.settings)
        self.device = device or AdbDeviceController(self.settings.emulator)
        self.vision = vision or VisionService.from_settings(self.settings)
        self.state_machine = BotStateMachine(self.settings)
        self.recovery = RecoveryManager(self.settings)
        self.task_engine = TaskEngine(self)

        self._lock = threading.RLock()
        self._task_queue: queue.Queue[str] = queue.Queue()
        self._worker_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._running = False
        self._started_at: datetime | None = None
        self._run_id: str | None = None
        self._current_task: str | None = None
        self._last_action: str | None = None
        self._last_error: str | None = None
        self._latest_screenshot: str | None = None
        self._emulator_online = False
        self._last_screenshot_monotonic = 0.0

    @property
    def settings(self) -> AppSettings:
        return self.settings_manager.settings

    @property
    def run_id(self) -> str:
        return self._run_id or "no_run"

    def _queue_snapshot(self) -> list[str]:
        with self._task_queue.mutex:
            return list(self._task_queue.queue)

    def begin_task(self, name: str) -> None:
        with self._lock:
            self._current_task = name
            self._last_action = f"task:{name}:start"

    def end_task(self, result: TaskResult) -> None:
        with self._lock:
            self._current_task = None
            self._last_action = f"task:{result.name}:{'success' if result.success else 'failure'}"
            if not result.success:
                self._last_error = result.message

    def note_action(self, action: str) -> None:
        with self._lock:
            self._last_action = action

    def get_status(self) -> BotStatus:
        with self._lock:
            uptime = 0.0
            if self._started_at and self._running:
                uptime = (datetime.now(UTC) - self._started_at).total_seconds()
            return BotStatus(
                running=self._running,
                started_at=self._started_at,
                current_task=self._current_task,
                current_state=self.state_machine.current_state,
                emulator_online=self._emulator_online,
                last_action=self._last_action,
                run_id=self._run_id,
                recovery_level=self.recovery.level,
                queue=self._queue_snapshot(),
                latest_screenshot=self._latest_screenshot,
                last_error=self._last_error,
                uptime_sec=uptime,
            )

    def latest_logs(self, limit: int = 100, module: str | None = None, level: str | None = None) -> list[dict[str, object]]:
        return read_recent_logs(self.settings.log_path, limit=limit, module=module, level=level)

    def available_tasks(self) -> list[dict[str, object]]:
        return self.task_engine.describe_tasks()

    def start(self) -> BotStatus:
        with self._lock:
            self._running = True
            self._started_at = datetime.now(UTC)
            self._run_id = f"run_{uuid.uuid4().hex[:8]}"
            self._last_error = None
            self._stop_event.clear()
            self.state_machine.force_state(StateName.BOOTING, metadata={"reason": "runtime_started"})
            if self._worker_thread is None or not self._worker_thread.is_alive():
                self._worker_thread = threading.Thread(target=self._worker_loop, name="tlbb-worker", daemon=True)
                self._worker_thread.start()
        self.enqueue_task("launch", dedupe=True)
        return self.get_status()

    def stop(self) -> BotStatus:
        self._running = False
        self._stop_event.set()
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2)
        self._task_queue = queue.Queue()
        self.state_machine.mark_stopped()
        return self.get_status()

    def restart(self) -> BotStatus:
        self.stop()
        return self.start()

    def reload_config(self) -> AppSettings:
        settings = self.settings_manager.reload()
        configure_logging(settings)
        self.artifacts = ArtifactStore(settings)
        if not self._external_device:
            self.device = AdbDeviceController(settings.emulator)
        if not self._external_vision:
            self.vision = VisionService.from_settings(settings)
        self.state_machine.update_settings(settings)
        self.recovery.update_settings(settings)
        self.task_engine = TaskEngine(self)
        return settings

    def enqueue_task(self, name: str, dedupe: bool = False) -> None:
        if not self._running:
            raise RuntimeError("Bot is stopped")
        if dedupe and (name == self._current_task or name in self._queue_snapshot()):
            return
        self._task_queue.put(name)

    def capture_state(self, event: str = "poll", persist_event: bool = False) -> Observation:
        image = self.device.screenshot()
        latest_path = self.artifacts.save_latest(image)
        classification = self.vision.classify_screen(image, self.settings.emulator.profile)
        snapshot = self.state_machine.observe(classification)
        if persist_event:
            self.artifacts.save_event(image, self.run_id, snapshot.state_name.value, event)
            if self.settings.app.debug:
                overlay = self.vision.draw_overlay(image, classification.matches)
                self.artifacts.save_overlay(overlay, self.run_id, snapshot.state_name.value, event)
        with self._lock:
            self._latest_screenshot = str(latest_path)
        return Observation(image=image, classification=classification, snapshot=snapshot)

    def perform_recovery(self, reason: str) -> None:
        decision = self.recovery.record_failure(reason)
        self.logger.warning(
            "recovery_triggered",
            extra={"event": "recovery_triggered", "payload": {"level": decision.level, "reason": reason}},
        )

        try:
            self.capture_state(event="recovery_start", persist_event=True)
        except Exception:
            self.logger.exception("recovery_capture_failed")

        if decision.level == 1:
            time.sleep(self.settings.bot.action_delay_ms / 1000)
        elif decision.level == 2:
            self.device.key_back()
            self.note_action("recovery:key_back")
        elif decision.level == 3:
            self.device.restart_app(self.settings.emulator.app_package)
            self.note_action("recovery:restart_app")
        else:
            self._running = False
            self.state_machine.mark_stopped()
            self._last_error = f"Recovery level 4 reached: {reason}"
            return

        time.sleep(self.settings.bot.action_delay_ms / 1000)
        try:
            observation = self.capture_state(event="recovery_result", persist_event=True)
        except Exception:
            self.logger.exception("recovery_followup_failed")
            return
        if observation.snapshot.state_name not in {StateName.RECOVERY_STATE, StateName.UNKNOWN_SCREEN}:
            self.recovery.reset()

    def _worker_loop(self) -> None:
        while not self._stop_event.is_set():
            if not self._running:
                time.sleep(0.1)
                continue
            try:
                if time.monotonic() - self._last_screenshot_monotonic >= self.settings.bot.screenshot_interval_ms / 1000:
                    observation = self.capture_state(event="poll")
                    self._emulator_online = True
                    self._last_screenshot_monotonic = time.monotonic()
                    if observation.snapshot.state_name == StateName.RECOVERY_STATE and self._current_task is None:
                        self.perform_recovery("state_machine_recovery")
                task_name = self._task_queue.get_nowait()
            except queue.Empty:
                time.sleep(self.settings.bot.tick_interval_ms / 1000)
                continue
            except Exception as exc:
                self._emulator_online = False
                self._last_error = str(exc)
                self.logger.exception("worker_poll_failed")
                self.perform_recovery("worker_poll_failed")
                time.sleep(self.settings.bot.tick_interval_ms / 1000)
                continue

            try:
                self.task_engine.run(task_name)
            finally:
                self._task_queue.task_done()

