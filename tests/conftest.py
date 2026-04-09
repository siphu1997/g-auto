from __future__ import annotations

import shutil
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from core.device.base import DeviceController
from core.vision.models import AnchorMatch, ScreenClassification


class FakeDeviceController(DeviceController):
    def __init__(self) -> None:
        self.online = True
        self.screen = "STOPPED"
        self.history: list[tuple[str, object]] = []
        self.reward_claimed = False
        self.mail_claimed = False
        self._loading_frames_remaining = 0

    def connect(self) -> bool:
        self.history.append(("connect", None))
        self.online = True
        return True

    def is_online(self) -> bool:
        self.history.append(("is_online", None))
        return self.online

    def screenshot(self) -> np.ndarray:
        if self.screen == "LOADING_SCREEN" and self._loading_frames_remaining > 0:
            self._loading_frames_remaining -= 1
            if self._loading_frames_remaining == 0:
                current = self.screen
                self.screen = "HOME_SCREEN"
                return self._image_for_state(current)
        return self._image_for_state(self.screen)

    def _image_for_state(self, state: str) -> np.ndarray:
        canvas = np.zeros((64, 64, 3), dtype=np.uint8)
        palette = {
            "STOPPED": (16, 16, 16),
            "HOME_SCREEN": (0, 128, 255),
            "LOADING_SCREEN": (255, 192, 0),
            "REWARD_SCREEN": (0, 180, 0),
            "MAIL_SCREEN": (180, 0, 180),
            "POPUP_SCREEN": (64, 64, 192),
        }
        canvas[:, :] = palette.get(state, (128, 128, 128))
        return canvas

    def tap(self, x: int, y: int) -> None:
        self.history.append(("tap", (x, y)))
        if self.screen == "HOME_SCREEN" and (x, y) == (100, 100):
            self.screen = "REWARD_SCREEN"
        elif self.screen == "HOME_SCREEN" and (x, y) == (200, 100):
            self.screen = "MAIL_SCREEN"
        elif self.screen == "REWARD_SCREEN" and (x, y) == (100, 200):
            self.reward_claimed = True
        elif self.screen == "MAIL_SCREEN" and (x, y) == (200, 200):
            self.mail_claimed = True
        elif self.screen == "POPUP_SCREEN" and (x, y) == (300, 50):
            self.screen = "HOME_SCREEN"

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int) -> None:
        self.history.append(("swipe", (x1, y1, x2, y2, duration_ms)))

    def input_text(self, text: str) -> None:
        self.history.append(("input_text", text))

    def key_back(self) -> None:
        self.history.append(("key_back", None))
        if self.screen in {"REWARD_SCREEN", "MAIL_SCREEN", "POPUP_SCREEN"}:
            self.screen = "HOME_SCREEN"

    def launch_app(self, package_name: str) -> None:
        self.history.append(("launch_app", package_name))
        self.screen = "LOADING_SCREEN"
        self._loading_frames_remaining = 1

    def stop_app(self, package_name: str) -> None:
        self.history.append(("stop_app", package_name))
        self.screen = "STOPPED"

    def restart_app(self, package_name: str) -> None:
        self.history.append(("restart_app", package_name))
        self.launch_app(package_name)


class FakeVisionService:
    ANCHORS = {
        "HOME_SCREEN": {
            "home_minimap": (10, 10, 20, 20),
            "home_menu": (20, 10, 30, 20),
            "reward_entry": (95, 95, 105, 105),
            "mail_entry": (195, 95, 205, 105),
        },
        "REWARD_SCREEN": {
            "reward_claim_all": (95, 195, 105, 205),
        },
        "MAIL_SCREEN": {
            "mail_claim_all": (195, 195, 205, 205),
        },
        "POPUP_SCREEN": {
            "popup_close": (295, 45, 305, 55),
        },
        "LOADING_SCREEN": {
            "loading_spinner": (30, 30, 34, 34),
        },
    }

    def __init__(self, device: FakeDeviceController) -> None:
        self.device = device

    def _matches(self) -> list[AnchorMatch]:
        matches = []
        for name, region in self.ANCHORS.get(self.device.screen, {}).items():
            x1, y1, x2, y2 = region
            matches.append(
                AnchorMatch(
                    name=name,
                    score=0.99,
                    region=region,
                    center=((x1 + x2) // 2, (y1 + y2) // 2),
                )
            )
        return matches

    def classify_screen(self, image: np.ndarray, profile: str) -> ScreenClassification:
        matches = self._matches()
        return ScreenClassification(
            state_name=self.device.screen if self.device.screen != "STOPPED" else "UNKNOWN_SCREEN",
            confidence=0.99 if matches else 0.0,
            matches=matches,
            metadata={"anchors": [match.name for match in matches]},
        )

    def find_anchor(self, image: np.ndarray, profile: str, anchor_name: str) -> AnchorMatch | None:
        for match in self._matches():
            if match.name == anchor_name:
                return match
        return None

    @staticmethod
    def draw_overlay(image: np.ndarray, matches: list[AnchorMatch]) -> np.ndarray:
        return image.copy()


def _rewrite_yaml(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False)


def _prepare_config_dir(target_dir: Path) -> Path:
    source_dir = ROOT / "config"
    shutil.copytree(source_dir, target_dir)

    app_config = yaml.safe_load((target_dir / "app.yaml").read_text(encoding="utf-8"))
    app_config["app"]["data_dir"] = str(target_dir.parent / "data")
    app_config["app"]["log_file"] = str(target_dir.parent / "data" / "logs" / "bot.jsonl")
    app_config["app"]["debug"] = False
    _rewrite_yaml(target_dir / "app.yaml", app_config)

    return target_dir


def pytest_configure() -> None:
    np.random.seed(0)


def make_test_config_dir(tmp_path: Path) -> Path:
    return _prepare_config_dir(tmp_path / "config")

