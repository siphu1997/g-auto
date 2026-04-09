from __future__ import annotations

import logging
import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.models import StateName, TaskResult
from games.tlbb.flows import TASK_RULES, UNIMPLEMENTED_TASKS

if TYPE_CHECKING:
    from core.bot_runtime import BotRuntime
    from core.models import Observation


class TaskEngine:
    def __init__(self, runtime: "BotRuntime") -> None:
        self.runtime = runtime
        self.logger = logging.getLogger("task")

    def describe_tasks(self) -> list[dict[str, object]]:
        return [
            {
                "name": name,
                "enabled": config.enabled,
                "max_duration_sec": config.max_duration_sec,
            }
            for name, config in self.runtime.settings.tasks.as_dict().items()
        ]

    def run(self, name: str) -> TaskResult:
        started_at = datetime.now(UTC)
        config = self.runtime.settings.tasks.as_dict().get(name)
        if config is None:
            return self._result(name, False, f"Unknown task '{name}'", started_at)
        if not config.enabled:
            return self._result(name, False, f"Task '{name}' is disabled", started_at)
        if name in UNIMPLEMENTED_TASKS:
            return self._result(name, False, f"Task '{name}' is not implemented in MVP", started_at)

        self.runtime.begin_task(name)
        try:
            if name == "launch":
                result = self._run_launch(started_at)
            elif name == "claim_reward":
                result = self._run_claim_flow(name, "reward_entry", "reward_claim_all", StateName.REWARD_SCREEN, started_at)
            elif name == "claim_mail":
                result = self._run_claim_flow(name, "mail_entry", "mail_claim_all", StateName.MAIL_SCREEN, started_at)
            else:
                result = self._result(name, False, f"No dispatcher for task '{name}'", started_at)
        except Exception as exc:
            self.logger.exception(
                "task_failed",
                extra={"event": "task_failed", "payload": {"task": name, "error": str(exc)}},
            )
            self.runtime.perform_recovery(f"task_exception:{name}")
            result = self._result(name, False, str(exc), started_at)
        self.runtime.end_task(result)
        return result

    def _result(self, name: str, success: bool, message: str, started_at: datetime, **metadata: object) -> TaskResult:
        return TaskResult(
            name=name,
            success=success,
            message=message,
            started_at=started_at,
            finished_at=datetime.now(UTC),
            metadata=dict(metadata),
        )

    def _sleep(self, seconds: float | None = None) -> None:
        delay = seconds if seconds is not None else self.runtime.settings.bot.action_delay_ms / 1000
        time.sleep(delay)

    def _wait_for_states(
        self,
        target_states: set[StateName],
        timeout_sec: int,
        allow_popup: bool = True,
    ) -> "Observation | None":
        deadline = time.monotonic() + timeout_sec
        while time.monotonic() < deadline:
            observation = self.runtime.capture_state(event="task_poll")
            state = observation.snapshot.state_name
            if state in target_states:
                return observation
            if allow_popup and state == StateName.POPUP_SCREEN:
                self._resolve_popup()
            elif state == StateName.RECOVERY_STATE:
                self.runtime.perform_recovery("task_wait_recovery")
            self._sleep(self.runtime.settings.bot.tick_interval_ms / 1000)
        return None

    def _tap_anchor(self, anchor_name: str) -> bool:
        observation = self.runtime.capture_state(event=f"locate_{anchor_name}")
        match = self.runtime.vision.find_anchor(observation.image, self.runtime.settings.emulator.profile, anchor_name)
        if match is None:
            self.logger.warning(
                "anchor_missing",
                extra={"event": "anchor_missing", "payload": {"anchor": anchor_name}},
            )
            self.runtime.capture_state(event=f"missing_{anchor_name}", persist_event=True)
            return False
        self.runtime.device.tap(*match.center)
        self.runtime.note_action(f"tap:{anchor_name}")
        self._sleep()
        if self.runtime.settings.bot.verify_after_action:
            self.runtime.capture_state(event=f"verify_{anchor_name}")
        return True

    def _resolve_popup(self) -> None:
        observation = self.runtime.capture_state(event="popup_detected", persist_event=True)
        match = self.runtime.vision.find_anchor(observation.image, self.runtime.settings.emulator.profile, "popup_close")
        if match is not None:
            self.runtime.device.tap(*match.center)
            self.runtime.note_action("tap:popup_close")
        else:
            self.runtime.device.key_back()
            self.runtime.note_action("key_back:popup")
        self._sleep()

    def _return_home(self, timeout_sec: int = 30) -> bool:
        deadline = time.monotonic() + timeout_sec
        while time.monotonic() < deadline:
            observation = self.runtime.capture_state(event="return_home")
            if observation.snapshot.state_name == StateName.HOME_SCREEN:
                return True
            if observation.snapshot.state_name == StateName.POPUP_SCREEN:
                self._resolve_popup()
                continue
            self.runtime.device.key_back()
            self.runtime.note_action("key_back:return_home")
            self._sleep()
        return False

    def _run_launch(self, started_at: datetime) -> TaskResult:
        if not self.runtime.device.connect():
            return self._result("launch", False, "Unable to connect to emulator", started_at)
        self.runtime.note_action("device_connect")
        self.runtime.state_machine.force_state(StateName.BOOTING, metadata={"task": "launch"})

        if not self.runtime.device.is_online():
            return self._result("launch", False, "Emulator is offline after connect", started_at)
        self.runtime.state_machine.force_state(StateName.EMULATOR_READY, metadata={"task": "launch"})

        self.runtime.device.launch_app(self.runtime.settings.emulator.app_package)
        self.runtime.note_action("launch_app")
        self.runtime.state_machine.force_state(StateName.GAME_LAUNCHING, metadata={"task": "launch"})

        observation = self._wait_for_states(
            {
                StateName.HOME_SCREEN,
                StateName.LOADING_SCREEN,
                StateName.LOGIN_SCREEN,
                StateName.SERVER_SELECT_SCREEN,
                StateName.CHARACTER_SELECT_SCREEN,
                StateName.POPUP_SCREEN,
            },
            timeout_sec=self.runtime.settings.tasks.launch.max_duration_sec,
        )
        if observation is None:
            self.runtime.capture_state(event="launch_timeout", persist_event=True)
            return self._result("launch", False, "Timed out waiting for launch flow", started_at)

        if observation.snapshot.state_name == StateName.HOME_SCREEN:
            self.runtime.capture_state(event="launch_complete", persist_event=True)
            self.runtime.recovery.reset()
            return self._result("launch", True, "Reached HOME_SCREEN", started_at)

        observation = self._wait_for_states({StateName.HOME_SCREEN}, timeout_sec=45)
        if observation is None:
            self.runtime.capture_state(event="launch_not_home", persist_event=True)
            return self._result("launch", False, "Launch flow did not settle on HOME_SCREEN", started_at)
        self.runtime.capture_state(event="launch_complete", persist_event=True)
        self.runtime.recovery.reset()
        return self._result("launch", True, "Reached HOME_SCREEN", started_at)

    def _run_claim_flow(
        self,
        task_name: str,
        entry_anchor: str,
        claim_anchor: str,
        target_state: StateName,
        started_at: datetime,
    ) -> TaskResult:
        current_state = self.runtime.capture_state(event=f"{task_name}_precheck").snapshot.state_name
        if current_state != StateName.HOME_SCREEN:
            return self._result(
                task_name,
                False,
                f"Task '{task_name}' requires HOME_SCREEN, current state is {current_state.value}",
                started_at,
            )

        if not self._tap_anchor(entry_anchor):
            return self._result(task_name, False, f"Anchor '{entry_anchor}' not found", started_at)

        observation = self._wait_for_states({target_state}, timeout_sec=20)
        if observation is None:
            self.runtime.capture_state(event=f"{task_name}_navigate_timeout", persist_event=True)
            return self._result(task_name, False, f"Timed out reaching {target_state.value}", started_at)

        if not self._tap_anchor(claim_anchor):
            self.logger.info(
                "claim_anchor_missing",
                extra={"event": "claim_anchor_missing", "payload": {"task": task_name, "anchor": claim_anchor}},
            )
        else:
            self.runtime.capture_state(event=f"{task_name}_claimed", persist_event=True)

        if not self._return_home():
            self.runtime.capture_state(event=f"{task_name}_return_home_failed", persist_event=True)
            return self._result(task_name, False, "Could not return to HOME_SCREEN", started_at)

        self.runtime.capture_state(event=f"{task_name}_complete", persist_event=True)
        self.runtime.recovery.reset()
        return self._result(task_name, True, f"Completed {task_name}", started_at)

