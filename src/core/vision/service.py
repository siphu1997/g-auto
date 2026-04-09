from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
import pytesseract

from core.config import AppSettings
from core.vision.models import AnchorMatch, ScreenClassification, TemplateDefinition
from games.tlbb.screens import SCREEN_SIGNATURES


class OCRAdapter:
    def __init__(self, enabled: bool = True, languages: str = "eng") -> None:
        self.enabled = enabled
        self.languages = languages

    def read_text(self, image: np.ndarray) -> str:
        if not self.enabled:
            return ""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return pytesseract.image_to_string(rgb_image, lang=self.languages).strip()


class VisionService:
    def __init__(
        self,
        template_dir: Path,
        templates: Iterable[TemplateDefinition],
        min_confidence: float = 0.8,
        screen_signatures: dict[str, dict[str, set[str]]] | None = None,
        ocr_adapter: OCRAdapter | None = None,
    ) -> None:
        self.template_dir = template_dir
        self.templates = list(templates)
        self.min_confidence = min_confidence
        self.screen_signatures = screen_signatures or SCREEN_SIGNATURES
        self.ocr_adapter = ocr_adapter or OCRAdapter()
        self.logger = logging.getLogger("vision")
        self._template_cache: dict[Path, np.ndarray] = {}

    @classmethod
    def from_settings(cls, settings: AppSettings) -> "VisionService":
        template_dir = Path(settings.vision.template_dir)
        definitions = [
            TemplateDefinition(
                name=template.name,
                screen=template.screen,
                path=template_dir / template.file,
                threshold=template.threshold,
                search_region=template.search_region,
                profile=template.profile,
                version=template.version,
            )
            for template in settings.vision.templates
        ]
        return cls(
            template_dir=template_dir,
            templates=definitions,
            min_confidence=settings.vision.min_confidence,
            ocr_adapter=OCRAdapter(settings.vision.ocr_enabled, settings.vision.ocr_languages),
        )

    def _load_template(self, path: Path) -> np.ndarray | None:
        if path in self._template_cache:
            return self._template_cache[path]
        if not path.exists():
            self.logger.warning(
                "template_missing",
                extra={"event": "template_missing", "payload": {"path": str(path)}},
            )
            return None
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            self.logger.warning(
                "template_unreadable",
                extra={"event": "template_unreadable", "payload": {"path": str(path)}},
            )
            return None
        self._template_cache[path] = image
        return image

    @staticmethod
    def _crop(image: np.ndarray, region: tuple[int, int, int, int] | None) -> tuple[np.ndarray, tuple[int, int]]:
        if region is None:
            return image, (0, 0)
        x1, y1, x2, y2 = region
        return image[y1:y2, x1:x2], (x1, y1)

    def detect_anchors(self, image: np.ndarray, profile: str) -> list[AnchorMatch]:
        matches: list[AnchorMatch] = []
        for template in [item for item in self.templates if item.profile == profile]:
            template_image = self._load_template(template.path)
            if template_image is None:
                continue
            crop, offset = self._crop(image, template.search_region)
            if crop.size == 0:
                continue
            if crop.shape[0] < template_image.shape[0] or crop.shape[1] < template_image.shape[1]:
                continue
            result = cv2.matchTemplate(crop, template_image, cv2.TM_CCOEFF_NORMED)
            _, score, _, max_loc = cv2.minMaxLoc(result)
            if score < max(template.threshold, self.min_confidence):
                continue
            x1 = max_loc[0] + offset[0]
            y1 = max_loc[1] + offset[1]
            x2 = x1 + template_image.shape[1]
            y2 = y1 + template_image.shape[0]
            matches.append(
                AnchorMatch(
                    name=template.name,
                    score=float(score),
                    region=(x1, y1, x2, y2),
                    center=(x1 + template_image.shape[1] // 2, y1 + template_image.shape[0] // 2),
                )
            )
        matches.sort(key=lambda item: item.score, reverse=True)
        return matches

    def find_anchor(self, image: np.ndarray, profile: str, anchor_name: str) -> AnchorMatch | None:
        matches = self.detect_anchors(image, profile)
        for match in matches:
            if match.name == anchor_name:
                return match
        return None

    def classify_screen(self, image: np.ndarray, profile: str) -> ScreenClassification:
        matches = self.detect_anchors(image, profile)
        anchor_scores = {match.name: match.score for match in matches}
        anchors = set(anchor_scores)

        best_state = "UNKNOWN_SCREEN"
        best_confidence = 0.0
        for state_name, signature in self.screen_signatures.items():
            required = signature.get("all_of", set())
            optional = signature.get("any_of", set())
            excluded = signature.get("none_of", set())
            if excluded & anchors:
                continue
            if required and not required.issubset(anchors):
                continue
            relevant = required | optional
            if not relevant:
                continue
            scored = [anchor_scores[name] for name in relevant if name in anchor_scores]
            if not scored:
                continue
            confidence = sum(scored) / len(scored)
            if confidence > best_confidence:
                best_state = state_name
                best_confidence = confidence

        if best_state == "UNKNOWN_SCREEN":
            return ScreenClassification(best_state, 0.0, matches, {"anchors": list(anchors)})
        return ScreenClassification(best_state, best_confidence, matches, {"anchors": list(anchors)})

    def extract_text(self, image: np.ndarray, region: tuple[int, int, int, int]) -> str:
        crop, _ = self._crop(image, region)
        if crop.size == 0:
            return ""
        return self.ocr_adapter.read_text(crop)

    @staticmethod
    def draw_overlay(image: np.ndarray, matches: list[AnchorMatch]) -> np.ndarray:
        overlay = image.copy()
        for match in matches:
            x1, y1, x2, y2 = match.region
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                overlay,
                f"{match.name}:{match.score:.2f}",
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )
        return overlay

