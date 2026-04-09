from __future__ import annotations

from core.bot_runtime import BotRuntime
from core.models import StateName

from tests.conftest import FakeDeviceController, FakeVisionService, make_test_config_dir


def test_launch_reward_and_mail_flows_with_fakes(tmp_path) -> None:
    config_dir = make_test_config_dir(tmp_path)
    device = FakeDeviceController()
    vision = FakeVisionService(device)
    runtime = BotRuntime(config_dir=config_dir, device=device, vision=vision)

    launch = runtime.task_engine.run("launch")
    assert launch.success is True
    assert runtime.state_machine.current_state == StateName.HOME_SCREEN

    reward = runtime.task_engine.run("claim_reward")
    assert reward.success is True
    assert device.reward_claimed is True
    assert runtime.state_machine.current_state == StateName.HOME_SCREEN

    mail = runtime.task_engine.run("claim_mail")
    assert mail.success is True
    assert device.mail_claimed is True
    assert runtime.state_machine.current_state == StateName.HOME_SCREEN

