from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from core.vision.models import TemplateDefinition
from core.vision.service import OCRAdapter, VisionService


def test_template_matching_and_screen_classification(tmp_path) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    home_minimap = np.zeros((10, 10, 3), dtype=np.uint8)
    home_minimap[:, :] = (30, 30, 30)
    home_minimap[2:8, 2:8] = (255, 255, 255)
    home_minimap[4:6, :] = (0, 0, 255)

    home_menu = np.zeros((8, 8, 3), dtype=np.uint8)
    home_menu[:, :] = (0, 60, 0)
    home_menu[:, 3:5] = (0, 255, 0)
    home_menu[3:5, :] = (0, 255, 0)

    cv2.imwrite(str(template_dir / "home_minimap.png"), home_minimap)
    cv2.imwrite(str(template_dir / "home_menu.png"), home_menu)

    screen = np.zeros((64, 64, 3), dtype=np.uint8)
    screen[5:15, 5:15] = home_minimap
    screen[30:38, 40:48] = home_menu

    service = VisionService(
        template_dir=template_dir,
        templates=[
            TemplateDefinition(
                name="home_minimap",
                screen="HOME_SCREEN",
                path=Path(template_dir / "home_minimap.png"),
                threshold=0.9,
                search_region=(0, 0, 32, 32),
                profile="ldplayer_1280x720",
                version=1,
            ),
            TemplateDefinition(
                name="home_menu",
                screen="HOME_SCREEN",
                path=Path(template_dir / "home_menu.png"),
                threshold=0.9,
                search_region=(32, 16, 64, 48),
                profile="ldplayer_1280x720",
                version=1,
            ),
        ],
        min_confidence=0.8,
        screen_signatures={
            "HOME_SCREEN": {"all_of": {"home_minimap", "home_menu"}, "any_of": set(), "none_of": set()},
        },
        ocr_adapter=OCRAdapter(enabled=False),
    )

    matches = service.detect_anchors(screen, "ldplayer_1280x720")
    classification = service.classify_screen(screen, "ldplayer_1280x720")

    assert {match.name for match in matches} == {"home_minimap", "home_menu"}
    assert classification.state_name == "HOME_SCREEN"
    assert classification.confidence >= 0.9
