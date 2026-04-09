from __future__ import annotations

import subprocess
import time
from pathlib import Path

import cv2
import numpy as np

from core.config import EmulatorSection
from core.device.base import DeviceController


class AdbDeviceController(DeviceController):
    def __init__(self, config: EmulatorSection) -> None:
        self.config = config
        self.adb_path = str(Path(config.adb_path))
        self.serial = config.adb_serial

    def _run(self, args: list[str], timeout: int | None = None, binary: bool = False) -> subprocess.CompletedProcess[bytes | str]:
        return subprocess.run(
            [self.adb_path, *args],
            capture_output=True,
            check=True,
            timeout=timeout or self.config.connect_timeout_sec,
            text=not binary,
        )

    def connect(self) -> bool:
        if ":" in self.serial:
            self._run(["connect", self.serial])
        return self.is_online()

    def is_online(self) -> bool:
        try:
            result = self._run(["-s", self.serial, "get-state"])
        except subprocess.CalledProcessError:
            return False
        output = (result.stdout or "").strip()
        return output == "device"

    def screenshot(self) -> np.ndarray:
        result = self._run(["-s", self.serial, "exec-out", "screencap", "-p"], timeout=20, binary=True)
        raw = (result.stdout or b"").replace(b"\r\r\n", b"\n")
        buffer = np.frombuffer(raw, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        if image is None:
            raise RuntimeError("ADB screenshot decode failed")
        return image

    def tap(self, x: int, y: int) -> None:
        self._run(["-s", self.serial, "shell", "input", "tap", str(x), str(y)])

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int) -> None:
        self._run(
            [
                "-s",
                self.serial,
                "shell",
                "input",
                "swipe",
                str(x1),
                str(y1),
                str(x2),
                str(y2),
                str(duration_ms),
            ]
        )

    def input_text(self, text: str) -> None:
        sanitized = text.replace(" ", "%s")
        self._run(["-s", self.serial, "shell", "input", "text", sanitized])

    def key_back(self) -> None:
        self._run(["-s", self.serial, "shell", "input", "keyevent", "4"])

    def launch_app(self, package_name: str) -> None:
        if self.config.launch_activity:
            component = f"{package_name}/{self.config.launch_activity}"
            self._run(["-s", self.serial, "shell", "am", "start", "-n", component])
            return
        self._run(
            [
                "-s",
                self.serial,
                "shell",
                "monkey",
                "-p",
                package_name,
                "-c",
                "android.intent.category.LAUNCHER",
                "1",
            ]
        )

    def stop_app(self, package_name: str) -> None:
        self._run(["-s", self.serial, "shell", "am", "force-stop", package_name])

    def restart_app(self, package_name: str) -> None:
        self.stop_app(package_name)
        time.sleep(1)
        self.launch_app(package_name)

