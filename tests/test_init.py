from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from custom_components.unifi_protect_bridge import async_migrate_entry, async_setup_entry
from custom_components.unifi_protect_bridge.const import (
    CONF_VERIFY_SSL,
    CONF_WEBHOOK_ID,
    CONFIG_ENTRY_VERSION,
    DEFAULT_VERIFY_SSL,
    SUPPORTED_METHODS,
)
from custom_components.unifi_protect_bridge.protect_api import ProtectApiError, ProtectAuthError


class _FakeRuntime:
    def __init__(self, initialize_error: Exception | None = None) -> None:
        self.initialize_error = initialize_error
        self.initialized = False
        self.shutdown_calls = 0

    async def async_initialize(self) -> None:
        self.initialized = True
        if self.initialize_error is not None:
            raise self.initialize_error

    async def async_shutdown(self) -> None:
        self.shutdown_calls += 1


class _FakeConfigEntries:
    def __init__(self, forward_error: Exception | None = None) -> None:
        self.forward_error = forward_error
        self.forward_calls: list[tuple[object, tuple[str, ...]]] = []

    async def async_forward_entry_setups(self, entry, platforms) -> None:
        self.forward_calls.append((entry, tuple(platforms)))
        if self.forward_error is not None:
            raise self.forward_error


class _FakeHass:
    def __init__(self, *, forward_error: Exception | None = None) -> None:
        self.config_entries = _FakeConfigEntries(forward_error=forward_error)


def _entry() -> SimpleNamespace:
    return SimpleNamespace(
        entry_id="entry-1",
        data={"webhook_id": "webhook-1"},
        runtime_data=None,
    )


def test_async_setup_entry_cleans_up_on_auth_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    entry = _entry()
    hass = _FakeHass()
    runtime = _FakeRuntime(ProtectAuthError("bad auth"))
    register_calls: list[tuple[str, dict[str, object]]] = []
    unregister_calls: list[str] = []

    monkeypatch.setattr(
        "custom_components.unifi_protect_bridge.runtime.HaProtectBridgeRuntime",
        lambda _hass, _entry: runtime,
    )
    monkeypatch.setattr(
        "homeassistant.components.webhook.async_register",
        lambda _hass, _domain, _name, webhook_id, _handler, **_kwargs: (
            register_calls.append((webhook_id, _kwargs))
        ),
    )
    monkeypatch.setattr(
        "homeassistant.components.webhook.async_unregister",
        lambda _hass, webhook_id: unregister_calls.append(webhook_id),
    )

    with pytest.raises(ConfigEntryAuthFailed, match="bad auth"):
        asyncio.run(async_setup_entry(hass, entry))

    assert runtime.shutdown_calls == 1
    assert [call[0] for call in register_calls] == ["webhook-1"]
    assert register_calls[0][1]["local_only"] is False
    assert register_calls[0][1]["allowed_methods"] == SUPPORTED_METHODS
    assert unregister_calls == ["webhook-1"]
    assert entry.runtime_data is None


def test_async_setup_entry_cleans_up_on_api_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    entry = _entry()
    hass = _FakeHass()
    runtime = _FakeRuntime(ProtectApiError("offline"))
    unregister_calls: list[str] = []

    monkeypatch.setattr(
        "custom_components.unifi_protect_bridge.runtime.HaProtectBridgeRuntime",
        lambda _hass, _entry: runtime,
    )
    monkeypatch.setattr(
        "homeassistant.components.webhook.async_register",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "homeassistant.components.webhook.async_unregister",
        lambda _hass, webhook_id: unregister_calls.append(webhook_id),
    )

    with pytest.raises(ConfigEntryNotReady, match="offline"):
        asyncio.run(async_setup_entry(hass, entry))

    assert runtime.shutdown_calls == 1
    assert unregister_calls == ["webhook-1"]
    assert entry.runtime_data is None


def test_async_setup_entry_cleans_up_if_platform_forwarding_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = _entry()
    hass = _FakeHass(forward_error=RuntimeError("platform boom"))
    runtime = _FakeRuntime()
    unregister_calls: list[str] = []

    monkeypatch.setattr(
        "custom_components.unifi_protect_bridge.runtime.HaProtectBridgeRuntime",
        lambda _hass, _entry: runtime,
    )
    monkeypatch.setattr(
        "homeassistant.components.webhook.async_register",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "homeassistant.components.webhook.async_unregister",
        lambda _hass, webhook_id: unregister_calls.append(webhook_id),
    )

    with pytest.raises(RuntimeError, match="platform boom"):
        asyncio.run(async_setup_entry(hass, entry))

    assert runtime.shutdown_calls == 1
    assert unregister_calls == ["webhook-1"]
    assert entry.runtime_data is None


def test_async_setup_entry_ignores_setup_info_notification_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = _entry()
    hass = _FakeHass()
    runtime = _FakeRuntime()

    monkeypatch.setattr(
        "custom_components.unifi_protect_bridge.runtime.HaProtectBridgeRuntime",
        lambda _hass, _entry: runtime,
    )
    monkeypatch.setattr(
        "homeassistant.components.webhook.async_register",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "homeassistant.components.webhook.async_unregister",
        lambda *args, **kwargs: None,
    )

    async def _raise_setup_info(_hass, _runtime) -> None:
        raise RuntimeError("notification boom")

    monkeypatch.setattr(
        "custom_components.unifi_protect_bridge.async_show_setup_info",
        _raise_setup_info,
    )

    assert asyncio.run(async_setup_entry(hass, entry)) is True
    assert runtime.shutdown_calls == 0
    assert entry.runtime_data is runtime
    assert hass.config_entries.forward_calls == [(entry, ("sensor",))]


def test_async_setup_entry_wraps_runtime_constructor_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = _entry()
    hass = _FakeHass()
    unregister_calls: list[str] = []

    def _raise_runtime(_hass, _entry):
        raise ProtectApiError("bad host")

    monkeypatch.setattr(
        "custom_components.unifi_protect_bridge.runtime.HaProtectBridgeRuntime",
        _raise_runtime,
    )
    monkeypatch.setattr(
        "homeassistant.components.webhook.async_register",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "homeassistant.components.webhook.async_unregister",
        lambda _hass, webhook_id: unregister_calls.append(webhook_id),
    )

    with pytest.raises(ConfigEntryNotReady, match="bad host"):
        asyncio.run(async_setup_entry(hass, entry))

    assert unregister_calls == []
    assert entry.runtime_data is None


def test_async_migrate_entry_backfills_required_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "custom_components.unifi_protect_bridge.secrets.token_hex",
        lambda _size: "migrated-webhook",
    )
    updates: list[dict[str, object]] = []
    entry = SimpleNamespace(
        version=1,
        data={"host": "protect.local", "username": "admin", "password": "secret"},
    )
    hass = SimpleNamespace(
        config_entries=SimpleNamespace(
            async_update_entry=lambda _entry, **kwargs: updates.append(kwargs)
        )
    )

    assert asyncio.run(async_migrate_entry(hass, entry)) is True

    assert updates == [
        {
            "data": {
                "host": "protect.local",
                "username": "admin",
                "password": "secret",
                CONF_VERIFY_SSL: DEFAULT_VERIFY_SSL,
                CONF_WEBHOOK_ID: "migrated-webhook",
            },
            "version": CONFIG_ENTRY_VERSION,
        }
    ]


def test_async_migrate_entry_updates_version_for_entries_with_current_data() -> None:
    updates: list[dict[str, object]] = []
    entry = SimpleNamespace(
        version=1,
        data={
            "host": "protect.local",
            "username": "admin",
            "password": "secret",
            CONF_VERIFY_SSL: True,
            CONF_WEBHOOK_ID: "existing-webhook",
        },
    )
    hass = SimpleNamespace(
        config_entries=SimpleNamespace(
            async_update_entry=lambda _entry, **kwargs: updates.append(kwargs)
        )
    )

    assert asyncio.run(async_migrate_entry(hass, entry)) is True
    assert updates == [
        {
            "data": {
                "host": "protect.local",
                "username": "admin",
                "password": "secret",
                CONF_VERIFY_SSL: True,
                CONF_WEBHOOK_ID: "existing-webhook",
            },
            "version": CONFIG_ENTRY_VERSION,
        }
    ]


def test_async_migrate_entry_leaves_current_version_unchanged() -> None:
    updates: list[dict[str, object]] = []
    entry = SimpleNamespace(
        version=CONFIG_ENTRY_VERSION,
        data={
            "host": "protect.local",
            "username": "admin",
            "password": "secret",
            CONF_VERIFY_SSL: True,
            CONF_WEBHOOK_ID: "existing-webhook",
        },
    )
    hass = SimpleNamespace(
        config_entries=SimpleNamespace(
            async_update_entry=lambda _entry, **kwargs: updates.append(kwargs)
        )
    )

    assert asyncio.run(async_migrate_entry(hass, entry)) is True
    assert updates == []
