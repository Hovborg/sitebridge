from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace
from typing import Any

from custom_components.unifi_protect_bridge.const import (
    CONF_WEBHOOK_ID,
    EVENT_DETECTION,
    EVENT_WEBHOOK,
)
from custom_components.unifi_protect_bridge.webhook import (
    _read_payload,
    async_handle_protect_webhook,
)


class _FakeRequest:
    def __init__(
        self,
        *,
        method: str = "POST",
        body: str = "",
        headers: dict[str, str] | None = None,
        query: dict[str, str] | None = None,
        content_length: int | None = None,
    ) -> None:
        self.method = method
        self._body = body
        self.headers = headers or {}
        self.query = query or {}
        self.content_length = content_length if content_length is not None else len(body.encode())

    async def text(self) -> str:
        return self._body


class _FakeBus:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []

    def async_fire(self, event_type: str, event_data: dict[str, Any]) -> None:
        self.events.append((event_type, event_data))


class _FakeConfigEntries:
    def __init__(self, entries: list[Any]) -> None:
        self._entries = entries

    def async_entries(self, _domain: str) -> list[Any]:
        return self._entries


class _FakeRuntime:
    def __init__(self) -> None:
        self.entry = SimpleNamespace(data={CONF_WEBHOOK_ID: "webhook-1"})
        self.normalized: dict[str, Any] | None = None

    async def async_process_webhook(self, normalized: dict[str, Any]) -> list[dict[str, str]]:
        self.normalized = normalized
        return [{"name": "Front Door", "camera_key": "front_door"}]


def test_read_payload_handles_get_without_body() -> None:
    assert asyncio.run(_read_payload(_FakeRequest(method="GET", body='{"ok": true}'))) == {}


def test_read_payload_handles_post_json_dict() -> None:
    payload = asyncio.run(
        _read_payload(
            _FakeRequest(
                body='{"alarm": {"name": "Person"}}',
                headers={"Content-Type": "application/json"},
            )
        )
    )

    assert payload == {"alarm": {"name": "Person"}}


def test_read_payload_wraps_non_dict_json() -> None:
    payload = asyncio.run(
        _read_payload(
            _FakeRequest(
                body='["person"]',
                headers={"Content-Type": "application/json"},
            )
        )
    )

    assert payload == {"raw_body": ["person"]}


def test_read_payload_wraps_invalid_json_body() -> None:
    payload = asyncio.run(
        _read_payload(
            _FakeRequest(
                body='{"alarm":',
                headers={"Content-Type": "application/json"},
            )
        )
    )

    assert payload == {"raw_body": '{"alarm":'}


def test_read_payload_wraps_text_body() -> None:
    payload = asyncio.run(
        _read_payload(
            _FakeRequest(
                body="person detected",
                headers={"Content-Type": "text/plain"},
            )
        )
    )

    assert payload == {"raw_body": "person detected"}


def test_handle_webhook_rejects_oversized_body_before_event_processing() -> None:
    runtime = _FakeRuntime()
    hass = SimpleNamespace(
        bus=_FakeBus(),
        config_entries=_FakeConfigEntries([SimpleNamespace(runtime_data=runtime)]),
    )

    response = asyncio.run(
        async_handle_protect_webhook(
            hass,
            "webhook-1",
            _FakeRequest(
                body="{}",
                headers={"Content-Type": "application/json"},
                content_length=300 * 1024,
            ),
        )
    )

    assert response.status == 413
    assert hass.bus.events == []
    assert runtime.normalized is None


def test_handle_webhook_rejects_get_before_event_processing() -> None:
    runtime = _FakeRuntime()
    hass = SimpleNamespace(
        bus=_FakeBus(),
        config_entries=_FakeConfigEntries([SimpleNamespace(runtime_data=runtime)]),
    )
    response = asyncio.run(
        async_handle_protect_webhook(
            hass,
            "webhook-1",
            _FakeRequest(method="GET", query={"source": "person", "device": "CAM1"}),
        )
    )

    assert response.status == 405
    assert hass.bus.events == []
    assert runtime.normalized is None


def test_handle_webhook_fires_sanitized_detection_events() -> None:
    runtime = _FakeRuntime()
    hass = SimpleNamespace(
        bus=_FakeBus(),
        config_entries=_FakeConfigEntries([SimpleNamespace(runtime_data=runtime)]),
    )
    response = asyncio.run(
        async_handle_protect_webhook(
            hass,
            "webhook-1",
            _FakeRequest(
                body=json.dumps(
                    {
                        "alarm": {
                            "name": "Front person",
                            "sources": [{"device": "CAM1", "type": "include"}],
                            "conditions": [{"condition": {"source": "person"}}],
                        },
                        "timestamp": 1770000000000,
                    }
                ),
                headers={
                    "Content-Type": "application/json",
                    "X-Forwarded-For": "192.0.2.10",
                },
                query={"source": "person", "token": "do-not-expose"},
            ),
        )
    )

    assert response.status == 200
    response_payload = json.loads(response.text)
    assert response_payload["primary_detection_type"] == "person"
    assert response_payload["matched_cameras"] == ["Front Door"]

    event_types = [event_type for event_type, _event_data in hass.bus.events]
    assert event_types == [EVENT_WEBHOOK, EVENT_DETECTION, "unifi_protect_bridge_person"]

    event_data = hass.bus.events[0][1]
    assert event_data["detection_types"] == ["person"]
    assert event_data["device_ids"] == ["CAM1"]
    assert event_data["method"] == "POST"
    assert event_data["matched_camera_names"] == ["Front Door"]
    assert event_data["matched_camera_keys"] == ["front_door"]
    assert "raw_payload" not in event_data
    assert "query" not in event_data
    assert "headers" not in event_data
    assert "webhook_id" not in event_data
    assert "path" not in event_data
