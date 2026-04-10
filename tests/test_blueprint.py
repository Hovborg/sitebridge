from __future__ import annotations

from pathlib import Path

from custom_components.unifi_protect_bridge.const import SELECTABLE_DETECTION_EVENTS


def test_detection_blueprint_options_match_emitted_detection_events() -> None:
    blueprint = Path(
        "blueprints/automation/unifi_protect_bridge/react_to_detection.yaml"
    ).read_text(encoding="utf-8")
    options = [
        line.strip().removeprefix("- ")
        for line in blueprint.splitlines()
        if line.strip().startswith("- unifi_protect_bridge_")
    ]

    assert options == list(SELECTABLE_DETECTION_EVENTS)
