from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

import numpy as np
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from core.bot_runtime import BotRuntime
    from core.vision.models import ScreenClassification


class StateName(StrEnum):
    BOOTING = "BOOTING"
    EMULATOR_READY = "EMULATOR_READY"
    GAME_LAUNCHING = "GAME_LAUNCHING"
    LOGIN_SCREEN = "LOGIN_SCREEN"
    SERVER_SELECT_SCREEN = "SERVER_SELECT_SCREEN"
    CHARACTER_SELECT_SCREEN = "CHARACTER_SELECT_SCREEN"
    LOADING_SCREEN = "LOADING_SCREEN"
    HOME_SCREEN = "HOME_SCREEN"
    REWARD_SCREEN = "REWARD_SCREEN"
    MAIL_SCREEN = "MAIL_SCREEN"
    QUEST_SCREEN = "QUEST_SCREEN"
    TRAIN_SCREEN = "TRAIN_SCREEN"
    POPUP_SCREEN = "POPUP_SCREEN"
    DISCONNECTED_SCREEN = "DISCONNECTED_SCREEN"
    UNKNOWN_SCREEN = "UNKNOWN_SCREEN"
    RECOVERY_STATE = "RECOVERY_STATE"
    STOPPED = "STOPPED"


class TaskName(StrEnum):
    LAUNCH = "launch"
    CLAIM_REWARD = "claim_reward"
    CLAIM_MAIL = "claim_mail"
    DAILY = "daily"
    QUEST = "quest"
    TRAIN = "train"


class StateSnapshot(BaseModel):
    state_name: StateName
    confidence: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    anchors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskResult(BaseModel):
    name: str
    success: bool
    message: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


class BotStatus(BaseModel):
    running: bool = False
    started_at: datetime | None = None
    current_task: str | None = None
    current_state: StateName = StateName.STOPPED
    emulator_online: bool = False
    last_action: str | None = None
    run_id: str | None = None
    recovery_level: int = 0
    queue: list[str] = Field(default_factory=list)
    latest_screenshot: str | None = None
    last_error: str | None = None
    uptime_sec: float = 0.0


@dataclass(slots=True)
class Observation:
    image: np.ndarray
    classification: "ScreenClassification"
    snapshot: StateSnapshot


@dataclass(slots=True)
class TaskContext:
    task_name: str
    runtime: "BotRuntime"

