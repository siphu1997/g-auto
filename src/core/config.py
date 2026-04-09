from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AppSection(StrictModel):
    env: str = "local"
    debug: bool = True
    log_level: str = "INFO"
    data_dir: str = "./data"
    log_file: str = "./data/logs/bot.jsonl"


class ResolutionConfig(StrictModel):
    width: int
    height: int


class EmulatorSection(StrictModel):
    provider: str = "ldplayer"
    adb_path: str = "adb"
    adb_serial: str
    profile: str
    resolution: ResolutionConfig
    dpi: int
    app_package: str
    launch_activity: str | None = None
    restart_on_failure: bool = True
    connect_timeout_sec: int = 10


class BotSection(StrictModel):
    tick_interval_ms: int = 1200
    screenshot_interval_ms: int = 1500
    verify_after_action: bool = True
    save_debug_screenshots: bool = True
    action_delay_ms: int = 700
    max_unknown_retries: int = 3


class VisionTemplateConfig(StrictModel):
    name: str
    screen: str
    file: str
    threshold: float = 0.9
    search_region: tuple[int, int, int, int] | None = None
    profile: str
    version: int = 1


class VisionSection(StrictModel):
    template_dir: str = "./src/games/tlbb/templates"
    min_confidence: float = 0.8
    ocr_enabled: bool = True
    ocr_languages: str = "eng"
    templates: list[VisionTemplateConfig] = Field(default_factory=list)


class RecoverySection(StrictModel):
    detect_retry: int = 3
    action_retry: int = 2
    state_timeout_sec: int = 20
    loading_timeout_sec: int = 60
    recovery_timeout_sec: int = 60
    restart_app_after_failures: int = 3
    restart_emulator_after_failures: int = 5


class TaskEntryConfig(StrictModel):
    enabled: bool = True
    max_duration_sec: int = 120


class TasksSection(StrictModel):
    launch: TaskEntryConfig = Field(default_factory=TaskEntryConfig)
    claim_reward: TaskEntryConfig = Field(default_factory=TaskEntryConfig)
    claim_mail: TaskEntryConfig = Field(default_factory=TaskEntryConfig)
    daily: TaskEntryConfig = Field(default_factory=lambda: TaskEntryConfig(enabled=False, max_duration_sec=600))
    quest: TaskEntryConfig = Field(default_factory=lambda: TaskEntryConfig(enabled=False, max_duration_sec=900))
    train: TaskEntryConfig = Field(default_factory=lambda: TaskEntryConfig(enabled=False, max_duration_sec=1800))

    def as_dict(self) -> dict[str, TaskEntryConfig]:
        return {
            "launch": self.launch,
            "claim_reward": self.claim_reward,
            "claim_mail": self.claim_mail,
            "daily": self.daily,
            "quest": self.quest,
            "train": self.train,
        }


class ScheduleJob(StrictModel):
    name: str
    task: str
    cron: str


class SchedulesSection(StrictModel):
    enabled: bool = False
    jobs: list[ScheduleJob] = Field(default_factory=list)


class AppSettings(StrictModel):
    app: AppSection
    emulator: EmulatorSection
    bot: BotSection
    tasks: TasksSection
    vision: VisionSection
    recovery: RecoverySection
    schedules: SchedulesSection

    @property
    def data_dir(self) -> Path:
        return Path(self.app.data_dir)

    @property
    def log_path(self) -> Path:
        return Path(self.app.log_file)


CONFIG_FILES = [
    "app.yaml",
    "emulator.yaml",
    "bot.yaml",
    "tasks.yaml",
    "vision.yaml",
    "recovery.yaml",
    "schedules.yaml",
]


def _deep_merge(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in incoming.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _read_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        content = yaml.safe_load(handle) or {}
    if not isinstance(content, dict):
        raise ValueError(f"{path} must contain a YAML object at the top level")
    return content


def load_settings(config_dir: str | Path = "config") -> AppSettings:
    config_path = Path(config_dir)
    payload: dict[str, Any] = {}
    for filename in CONFIG_FILES:
        payload = _deep_merge(payload, _read_yaml_file(config_path / filename))
    return AppSettings.model_validate(payload)


class SettingsManager:
    def __init__(self, config_dir: str | Path = "config") -> None:
        self.config_dir = Path(config_dir)
        self._settings = load_settings(self.config_dir)

    @property
    def settings(self) -> AppSettings:
        return self._settings

    def reload(self) -> AppSettings:
        self._settings = load_settings(self.config_dir)
        return self._settings

