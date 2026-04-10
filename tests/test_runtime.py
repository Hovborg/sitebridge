from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace

from custom_components.unifi_protect_bridge.const import (
    CONF_EVENT_BACKFILL_LIMIT,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    CONF_WEBHOOK_ID,
    DEFAULT_EVENT_BACKFILL_LIMIT,
    MAX_EVENT_BACKFILL_LIMIT,
)
from custom_components.unifi_protect_bridge.runtime import HaProtectBridgeRuntime


def test_runtime_backfill_limit_uses_default_and_clamps_options() -> None:
    runtime = HaProtectBridgeRuntime(SimpleNamespace(), _mock_entry({}))
    assert runtime._event_backfill_limit() == DEFAULT_EVENT_BACKFILL_LIMIT

    runtime = HaProtectBridgeRuntime(SimpleNamespace(), _mock_entry({CONF_EVENT_BACKFILL_LIMIT: 0}))
    assert runtime._event_backfill_limit() == 0

    runtime = HaProtectBridgeRuntime(
        SimpleNamespace(),
        _mock_entry({CONF_EVENT_BACKFILL_LIMIT: 999}),
    )
    assert runtime._event_backfill_limit() == MAX_EVENT_BACKFILL_LIMIT


def test_runtime_backfill_skips_event_fetch_when_limit_is_zero() -> None:
    runtime = HaProtectBridgeRuntime(
        SimpleNamespace(),
        _mock_entry({CONF_EVENT_BACKFILL_LIMIT: 0}),
    )
    called = False

    async def _async_get_events(**kwargs):
        nonlocal called
        del kwargs
        called = True
        return []

    runtime._api.async_get_events = _async_get_events

    asyncio.run(runtime._async_backfill_recent_events())

    assert called is False


def test_runtime_status_attributes_do_not_expose_webhook_secret() -> None:
    runtime = HaProtectBridgeRuntime(SimpleNamespace(), _mock_entry({}))
    runtime._webhook_url = "http://ha.local/api/webhook/secret"

    attributes = runtime.get_status_attributes()

    assert "webhook_url" not in attributes
    assert "webhook_path" not in attributes
    assert attributes["webhook_configured"] is True
    assert attributes["webhook_base_url_override_configured"] is False


def test_runtime_last_webhook_at_uses_receive_time_not_event_timestamp() -> None:
    runtime = HaProtectBridgeRuntime(SimpleNamespace(), _mock_entry({}))
    normalized = {
        "alarm_name": "old_person",
        "detection_types": ["person"],
        "primary_detection_type": "person",
        "device_ids": [],
        "source_values": ["person"],
        "timestamp_ms": 946684800000,
        "timestamp_iso": "2000-01-01T00:00:00+00:00",
        "query": {},
        "raw_payload": {},
        "event_types": ["unifi_protect_bridge_person"],
    }

    before = datetime.now(UTC)
    asyncio.run(runtime.async_process_webhook(normalized))

    assert runtime.last_webhook_at is not None
    assert runtime.last_webhook_at >= before


def test_runtime_sync_removes_duplicate_managed_automations() -> None:
    runtime = HaProtectBridgeRuntime(SimpleNamespace(), _mock_entry({}))
    runtime.catalog = {
        "nvr_id": "nvr",
        "nvr_name": "Protect",
        "lookup": {},
        "managed_sources": ["person"],
        "cameras": [
            {
                "device_mac": "84784828725C",
                "supported_sources": ["person"],
            }
        ],
    }
    runtime._webhook_url = "http://ha.local/api/webhook/test"
    deleted: list[str] = []
    created: list[dict[str, object]] = []

    async def _async_delete_automation(automation_id: str) -> None:
        deleted.append(automation_id)

    async def _async_create_automation(payload: dict[str, object]) -> dict[str, object]:
        created.append(payload)
        return {"id": "created", **payload}

    runtime._api.async_delete_automation = _async_delete_automation
    runtime._api.async_create_automation = _async_create_automation

    current = {
        "id": "current",
        "name": "UniFi Protect Bridge: person",
        "enable": True,
        "sources": [{"device": "84784828725C"}],
        "conditions": [{"condition": {"type": "is", "source": "person"}}],
        "actions": [
            {
                "type": "HTTP_REQUEST",
                "metadata": {
                    "url": "http://ha.local/api/webhook/test?source=person",
                    "method": "POST",
                    "timeout": 30000,
                    "useThumbnail": True,
                    "headers": [],
                },
            }
        ],
    }
    legacy_duplicate = {**current, "id": "legacy", "name": "HA Protect Bridge: person"}
    user_automation = {
        **current,
        "id": "user",
        "name": "User managed person webhook",
    }

    asyncio.run(
        runtime._async_sync_managed_automations(
            [legacy_duplicate, user_automation, current],
        )
    )

    assert deleted == ["legacy"]
    assert created == []
    assert runtime._managed_automations["person"]["id"] == "current"


def _mock_entry(options: dict[str, int]) -> SimpleNamespace:
    return SimpleNamespace(
        entry_id="entry-1",
        data={
            CONF_HOST: "protect.local",
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "secret",
            CONF_VERIFY_SSL: False,
            CONF_WEBHOOK_ID: "webhook-id",
        },
        options=options,
    )
