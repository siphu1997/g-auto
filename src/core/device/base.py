from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class DeviceController(ABC):
    @abstractmethod
    def connect(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_online(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def screenshot(self) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def tap(self, x: int, y: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def input_text(self, text: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def key_back(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def launch_app(self, package_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop_app(self, package_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def restart_app(self, package_name: str) -> None:
        raise NotImplementedError

