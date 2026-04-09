from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class TemplateDefinition:
    name: str
    screen: str
    path: Path
    threshold: float
    search_region: tuple[int, int, int, int] | None
    profile: str
    version: int


@dataclass(slots=True)
class AnchorMatch:
    name: str
    score: float
    region: tuple[int, int, int, int]
    center: tuple[int, int]


@dataclass(slots=True)
class ScreenClassification:
    state_name: str
    confidence: float
    matches: list[AnchorMatch] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

