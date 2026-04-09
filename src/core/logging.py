from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from core.config import AppSettings


class JsonLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "module": record.name,
            "event": getattr(record, "event", record.msg if isinstance(record.msg, str) else "log"),
            "message": record.getMessage(),
        }
        if hasattr(record, "payload") and isinstance(record.payload, dict):
            payload.update(record.payload)
        return json.dumps(payload, ensure_ascii=True)


def configure_logging(settings: AppSettings) -> None:
    log_path = settings.log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, settings.app.log_level.upper(), logging.INFO)
    formatter = JsonLineFormatter()

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    root.addHandler(stream_handler)
    root.addHandler(file_handler)


class ArtifactStore:
    def __init__(self, settings: AppSettings) -> None:
        self.data_dir = settings.data_dir
        self.screenshots_dir = self.data_dir / "screenshots"
        self.logs_dir = self.data_dir / "logs"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    @property
    def latest_screenshot_path(self) -> Path:
        return self.screenshots_dir / "latest.png"

    def save_latest(self, image: np.ndarray) -> Path:
        path = self.latest_screenshot_path
        cv2.imwrite(str(path), image)
        return path

    def save_event(self, image: np.ndarray, run_id: str, state: str, event: str) -> Path:
        timestamp = datetime.now(UTC)
        date_dir = self.screenshots_dir / timestamp.strftime("%Y-%m-%d") / run_id
        date_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{timestamp.strftime('%H%M%S')}_{state}_{event}.png"
        path = date_dir / filename
        cv2.imwrite(str(path), image)
        return path

    def save_overlay(self, image: np.ndarray, run_id: str, state: str, event: str) -> Path:
        timestamp = datetime.now(UTC)
        date_dir = self.screenshots_dir / timestamp.strftime("%Y-%m-%d") / run_id
        date_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{timestamp.strftime('%H%M%S')}_{state}_{event}_overlay.png"
        path = date_dir / filename
        cv2.imwrite(str(path), image)
        return path


def read_recent_logs(
    log_path: str | Path,
    limit: int = 100,
    module: str | None = None,
    level: str | None = None,
) -> list[dict[str, Any]]:
    path = Path(log_path)
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    results: list[dict[str, Any]] = []
    for line in reversed(lines):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if module and payload.get("module") != module:
            continue
        if level and payload.get("level") != level.upper():
            continue
        results.append(payload)
        if len(results) >= limit:
            break
    return list(reversed(results))

