from __future__ import annotations

import time

from fastapi.testclient import TestClient

from core.api import create_app
from core.bot_runtime import BotRuntime

from tests.conftest import FakeDeviceController, FakeVisionService, make_test_config_dir


def test_api_start_status_logs_and_screenshot(tmp_path) -> None:
    config_dir = make_test_config_dir(tmp_path)
    device = FakeDeviceController()
    vision = FakeVisionService(device)
    runtime = BotRuntime(config_dir=config_dir, device=device, vision=vision)
    runtime.capture_state(event="seed")

    client = TestClient(create_app(runtime))

    assert client.get("/health").json()["status"] == "ok"

    start_response = client.post("/bot/start")
    assert start_response.status_code == 200

    time.sleep(0.1)

    status_payload = client.get("/status").json()
    assert status_payload["running"] is True

    logs_payload = client.get("/logs").json()
    assert isinstance(logs_payload, list)

    screenshot_response = client.get("/screenshots/latest")
    assert screenshot_response.status_code == 200
    assert screenshot_response.headers["content-type"] == "image/png"

    task_response = client.post("/tasks/run", json={"task": "launch"})
    assert task_response.status_code == 200

    reload_response = client.post("/config/reload")
    assert reload_response.status_code == 200

    stop_response = client.post("/bot/stop")
    assert stop_response.status_code == 200

