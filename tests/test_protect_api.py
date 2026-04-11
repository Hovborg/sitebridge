import asyncio

import aiohttp
import pytest

from custom_components.unifi_protect_bridge.protect_api import (
    PROTECT_EVENTS_REQUEST_LIMIT,
    ProtectApiClient,
    ProtectApiError,
    _normalize_base_url,
)


def test_protect_api_client_accepts_custom_timeout() -> None:
    client = ProtectApiClient(
        "https://protect.example",
        "user",
        "secret",
        True,
        timeout_seconds=7.5,
    )

    assert client._timeout_seconds == 7.5


def test_protect_api_rejects_non_http_hosts() -> None:
    with pytest.raises(ProtectApiError, match="http or https"):
        _normalize_base_url("ftp://protect.example")


def test_protect_api_rejects_hosts_with_paths() -> None:
    with pytest.raises(ProtectApiError, match="host or origin"):
        _normalize_base_url("https://protect.example/proxy/protect")


def test_protect_api_login_wraps_client_errors() -> None:
    client = ProtectApiClient("https://protect.example", "user", "secret", True)

    class FakeSession:
        def post(self, *args, **kwargs):
            del args, kwargs
            raise aiohttp.ClientConnectionError("network down")

    client._session = FakeSession()

    with pytest.raises(ProtectApiError, match="Could not connect to Protect"):
        asyncio.run(client.async_login())


def test_protect_api_request_wraps_timeouts() -> None:
    client = ProtectApiClient("https://protect.example", "user", "secret", True)

    class FakeSession:
        def request(self, *args, **kwargs):
            del args, kwargs
            raise TimeoutError("timed out")

    client._session = FakeSession()

    with pytest.raises(ProtectApiError, match="Protect API request failed"):
        asyncio.run(client._async_request("GET", "/proxy/protect/api/bootstrap"))


def test_protect_api_get_events_clamps_request_limit_and_sends_offset() -> None:
    client = ProtectApiClient("https://protect.example", "user", "secret", True)
    captured = {}

    async def _async_request(method, path, payload=None, params=None, allow_reauth=True):
        del payload, allow_reauth
        captured["method"] = method
        captured["path"] = path
        captured["params"] = params
        return [{"id": "event-1"}]

    client._async_request = _async_request

    events = asyncio.run(
        client.async_get_events(
            limit=PROTECT_EVENTS_REQUEST_LIMIT + 400,
            offset=200,
            types=["motion"],
            sorting="desc",
        )
    )

    assert events == [{"id": "event-1"}]
    assert captured["method"] == "GET"
    assert captured["path"] == "/proxy/protect/api/events"
    assert captured["params"]["limit"] == PROTECT_EVENTS_REQUEST_LIMIT
    assert captured["params"]["offset"] == 200
    assert captured["params"]["types"] == ["motion"]
