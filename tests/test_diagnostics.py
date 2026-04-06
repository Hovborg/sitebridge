from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace

from custom_components.ha_protect_bridge.diagnostics import async_get_config_entry_diagnostics
from custom_components.ha_protect_bridge.runtime import BridgeSensorSpec


class _FakeRuntime:
    def __init__(self) -> None:
        self.catalog = {
            "cameras": [
                {
                    "name": "Front Door",
                    "model": "G4 Doorbell Pro",
                    "is_doorbell": True,
                    "supported_sources": ["motion", "ring", "package"],
                },
                {
                    "name": "Kitchen",
                    "model": "G6 Instant",
                    "is_doorbell": False,
                    "supported_sources": ["motion", "audio_alarm_baby_cry"],
                },
            ]
        }
        self._managed_automations = {
            "audio_alarm_baby_cry": {},
            "motion": {},
            "ring": {},
        }
        self._sensor_specs = {
            "global:motion": BridgeSensorSpec(
                key="global:motion",
                unique_id="bridge_motion",
                name="Bridge Last motion",
                icon="mdi:motion-sensor",
                source="motion",
            ),
            "global:ring": BridgeSensorSpec(
                key="global:ring",
                unique_id="bridge_ring",
                name="Bridge Last ring",
                icon="mdi:bell-ring",
                source="ring",
            ),
            "kitchen:audio_alarm_baby_cry": BridgeSensorSpec(
                key="kitchen:audio_alarm_baby_cry",
                unique_id="kitchen_baby_cry",
                name="Kitchen Last baby cry alarm",
                icon="mdi:baby-face-outline",
                source="audio_alarm_baby_cry",
                camera_key="kitchen",
            ),
        }
        self._states = {
            "global:motion": datetime(2026, 4, 6, 1, 0, tzinfo=UTC),
        }

    def get_status_attributes(self) -> dict[str, object]:
        return {
            "host": "192.168.1.1",
            "verify_ssl": False,
            "event_backfill_limit": 0,
            "webhook_path": "/api/webhook/secret",
            "webhook_url": "http://ha.local/api/webhook/secret",
            "webhook_base_url_override": None,
            "nvr_id": "nvr-id",
            "nvr_name": "Dream Machine",
            "camera_count": 2,
            "managed_sources": ["motion", "ring", "audio_alarm_baby_cry"],
            "managed_automation_count": 3,
            "last_sync_at": "2026-04-06T01:00:00+00:00",
            "last_sync_error": None,
            "last_webhook_at": None,
        }

    def iter_sensor_specs(self) -> list[BridgeSensorSpec]:
        return list(self._sensor_specs.values())

    def get_sensor_state(self, sensor_key: str):
        return self._states.get(sensor_key)


def test_config_entry_diagnostics_redacts_and_summarizes_runtime() -> None:
    entry = SimpleNamespace(
        entry_id="entry-1",
        title="Dream Machine",
        state="loaded",
        data={
            "host": "192.168.1.1",
            "username": "hovborg",
            "password": "secret",
            "verify_ssl": False,
            "webhook_base_url": "http://ha.local",
            "webhook_id": "secret-webhook-id",
        },
        options={"event_backfill_limit": 0},
        runtime_data=_FakeRuntime(),
    )

    diagnostics = asyncio.run(async_get_config_entry_diagnostics(None, entry))

    assert diagnostics["entry"]["data"]["host"] == "REDACTED"
    assert diagnostics["entry"]["data"]["username"] == "REDACTED"
    assert diagnostics["entry"]["data"]["password"] == "REDACTED"
    assert diagnostics["entry"]["data"]["webhook_base_url"] == "REDACTED"
    assert diagnostics["entry"]["data"]["webhook_id"] == "REDACTED"
    assert diagnostics["entry"]["options"] == {"event_backfill_limit": 0}

    runtime = diagnostics["runtime"]
    assert runtime["status"]["host"] == "REDACTED"
    assert runtime["status"]["webhook_url"] == "REDACTED"
    assert runtime["status"]["nvr_id"] == "REDACTED"
    assert runtime["status"]["managed_sources"] == ["motion", "ring", "audio_alarm_baby_cry"]
    assert runtime["catalog"]["camera_count"] == 2
    assert runtime["catalog"]["doorbell_count"] == 1
    assert runtime["catalog"]["models"] == {"G4 Doorbell Pro": 1, "G6 Instant": 1}
    assert runtime["catalog"]["source_camera_counts"] == {
        "audio_alarm_baby_cry": 1,
        "motion": 2,
        "package": 1,
        "ring": 1,
    }
    assert runtime["catalog"]["cameras"] == [
        {
            "index": 1,
            "model": "G4 Doorbell Pro",
            "is_doorbell": True,
            "supported_sources": ["motion", "ring", "package"],
        },
        {
            "index": 2,
            "model": "G6 Instant",
            "is_doorbell": False,
            "supported_sources": ["motion", "audio_alarm_baby_cry"],
        },
    ]
    assert runtime["managed_automation_sources"] == [
        "audio_alarm_baby_cry",
        "motion",
        "ring",
    ]
    assert runtime["sensors"] == {
        "defined": 3,
        "by_source": {
            "audio_alarm_baby_cry": 1,
            "motion": 1,
            "ring": 1,
        },
        "active": 1,
        "active_by_source": {"motion": 1},
    }


def test_config_entry_diagnostics_handles_unloaded_runtime() -> None:
    entry = SimpleNamespace(
        entry_id="entry-1",
        title="Dream Machine",
        state="not_loaded",
        data={
            "host": "192.168.1.1",
            "username": "hovborg",
            "password": "secret",
            "verify_ssl": False,
            "webhook_id": "secret-webhook-id",
        },
        options={},
        runtime_data=None,
    )

    diagnostics = asyncio.run(async_get_config_entry_diagnostics(None, entry))

    assert diagnostics["entry"]["data"]["host"] == "REDACTED"
    assert diagnostics["entry"]["data"]["username"] == "REDACTED"
    assert diagnostics["entry"]["data"]["password"] == "REDACTED"
    assert diagnostics["entry"]["data"]["webhook_id"] == "REDACTED"
    assert diagnostics["runtime"] is None
