from __future__ import annotations

import asyncio
from types import SimpleNamespace

from custom_components.ha_protect_bridge.const import (
    CONF_EVENT_BACKFILL_LIMIT,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    CONF_WEBHOOK_ID,
    DEFAULT_EVENT_BACKFILL_LIMIT,
    MAX_EVENT_BACKFILL_LIMIT,
)
from custom_components.ha_protect_bridge.runtime import HaProtectBridgeRuntime


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
