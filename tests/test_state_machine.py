from __future__ import annotations

from core.config import load_settings
from core.state_machine import BotStateMachine
from core.vision.models import ScreenClassification

from tests.conftest import make_test_config_dir


def test_state_machine_escalates_after_unknown_retries(tmp_path) -> None:
    config_dir = make_test_config_dir(tmp_path)
    settings = load_settings(config_dir)
    machine = BotStateMachine(settings)

    for _ in range(settings.bot.max_unknown_retries + 1):
        snapshot = machine.observe(ScreenClassification("UNKNOWN_SCREEN", 0.0))

    assert snapshot.state_name.value == "RECOVERY_STATE"

