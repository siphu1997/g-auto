from __future__ import annotations

from dataclasses import dataclass

from core.config import AppSettings


@dataclass(slots=True)
class RecoveryDecision:
    level: int
    reason: str


class RecoveryManager:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.failure_count = 0
        self.level = 0

    def update_settings(self, settings: AppSettings) -> None:
        self.settings = settings

    def reset(self) -> None:
        self.failure_count = 0
        self.level = 0

    def record_failure(self, reason: str) -> RecoveryDecision:
        self.failure_count += 1
        if self.failure_count >= self.settings.recovery.restart_emulator_after_failures:
            self.level = 4
        elif self.failure_count >= self.settings.recovery.restart_app_after_failures:
            self.level = 3
        elif self.failure_count > self.settings.recovery.action_retry:
            self.level = 2
        else:
            self.level = 1
        return RecoveryDecision(level=self.level, reason=reason)

