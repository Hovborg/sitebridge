import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v0_2_22_release_metadata_is_aligned() -> None:
    manifest = json.loads(
        (ROOT / "custom_components/unifi_protect_bridge/manifest.json").read_text()
    )
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    hacs = json.loads((ROOT / "hacs.json").read_text())
    ci_workflow = (ROOT / ".github/workflows/ci.yml").read_text()

    assert manifest["version"] == "0.2.22"
    assert project["project"]["version"] == "0.2.22"
    assert hacs["homeassistant"] == "2026.3.0"
    assert "requirement: homeassistant==2026.3.0" in ci_workflow
