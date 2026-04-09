from __future__ import annotations

import logging
import time

from core.config import AppSettings
from core.models import StateName, StateSnapshot
from core.vision.models import ScreenClassification


class BotStateMachine:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.logger = logging.getLogger("state_machine")
        self._current_state = StateName.STOPPED
        self._state_entered_at = time.monotonic()
        self._unknown_retries = 0
        self._snapshot = StateSnapshot(state_name=StateName.STOPPED, confidence=1.0)

    @property
    def current_state(self) -> StateName:
        return self._current_state

    @property
    def snapshot(self) -> StateSnapshot:
        return self._snapshot

    def update_settings(self, settings: AppSettings) -> None:
        self.settings = settings

    def force_state(
        self,
        state: StateName,
        confidence: float = 1.0,
        anchors: list[str] | None = None,
        metadata: dict[str, object] | None = None,
    ) -> StateSnapshot:
        previous = self._current_state
        self._current_state = state
        self._state_entered_at = time.monotonic()
        self._snapshot = StateSnapshot(
            state_name=state,
            confidence=confidence,
            anchors=anchors or [],
            metadata=metadata or {},
        )
        if previous != state:
            self.logger.info(
                "state_changed",
                extra={
                    "event": "state_changed",
                    "payload": {
                        "from_state": previous.value,
                        "to_state": state.value,
                        "confidence": confidence,
                    },
                },
            )
        return self._snapshot

    def mark_stopped(self) -> StateSnapshot:
        return self.force_state(StateName.STOPPED, metadata={"reason": "runtime_stopped"})

    def observe(self, classification: ScreenClassification | None) -> StateSnapshot:
        metadata = dict(classification.metadata) if classification else {}
        anchors = list(metadata.get("anchors", []))
        candidate_name = classification.state_name if classification else StateName.UNKNOWN_SCREEN.value
        try:
            candidate = StateName(candidate_name)
        except ValueError:
            candidate = StateName.UNKNOWN_SCREEN

        confidence = classification.confidence if classification else 0.0
        if candidate == StateName.UNKNOWN_SCREEN:
            self._unknown_retries += 1
            if self._unknown_retries > self.settings.bot.max_unknown_retries:
                metadata["reason"] = "unknown_retry_limit"
                return self.force_state(StateName.RECOVERY_STATE, confidence=1.0, anchors=anchors, metadata=metadata)
        else:
            self._unknown_retries = 0

        elapsed = time.monotonic() - self._state_entered_at
        if self._current_state == StateName.LOADING_SCREEN and elapsed > self.settings.recovery.loading_timeout_sec:
            metadata["reason"] = "loading_timeout"
            return self.force_state(StateName.RECOVERY_STATE, confidence=1.0, anchors=anchors, metadata=metadata)
        if (
            self._current_state not in {StateName.STOPPED, StateName.RECOVERY_STATE}
            and candidate == self._current_state
            and elapsed > self.settings.recovery.state_timeout_sec
        ):
            metadata["reason"] = "state_timeout"
            return self.force_state(StateName.RECOVERY_STATE, confidence=1.0, anchors=anchors, metadata=metadata)

        if candidate != self._current_state:
            metadata["previous_state"] = self._current_state.value
            return self.force_state(candidate, confidence=confidence, anchors=anchors, metadata=metadata)

        self._snapshot = StateSnapshot(
            state_name=self._current_state,
            confidence=confidence,
            anchors=anchors,
            metadata=metadata,
        )
        return self._snapshot

