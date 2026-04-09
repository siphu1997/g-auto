from __future__ import annotations

from core.config import load_settings

from tests.conftest import make_test_config_dir


def test_load_settings_merges_yaml_sections(tmp_path) -> None:
    config_dir = make_test_config_dir(tmp_path)
    settings = load_settings(config_dir)

    assert settings.app.env == "local"
    assert settings.emulator.profile == "ldplayer_1280x720"
    assert settings.tasks.launch.enabled is True
    assert settings.tasks.train.enabled is False
    assert settings.recovery.loading_timeout_sec == 60

