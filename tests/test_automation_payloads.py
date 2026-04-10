from custom_components.unifi_protect_bridge.automation_payloads import (
    automation_needs_replace,
    build_managed_automation_name,
    build_managed_automation_payload,
    build_webhook_target_url,
    group_managed_automations,
    managed_source_from_automation,
    map_managed_automations,
)


def test_build_webhook_target_url_preserves_existing_query() -> None:
    url = build_webhook_target_url("http://ha.local/api/webhook/test?foo=bar", "person")

    assert "foo=bar" in url
    assert "source=person" in url


def test_build_managed_automation_payload_has_expected_shape() -> None:
    payload = build_managed_automation_payload(
        "person",
        ["84784828725C", "1C6A1B0E8173"],
        "http://ha.local/api/webhook/test",
    )

    assert payload["name"] == build_managed_automation_name("person")
    assert payload["conditions"] == [{"condition": {"type": "is", "source": "person"}}]
    assert payload["actions"][0]["metadata"]["url"].endswith("source=person")
    assert payload["actions"][0]["metadata"]["useThumbnail"] is True


def test_managed_source_from_automation_reads_name_prefix() -> None:
    payload = build_managed_automation_payload(
        "audio_alarm_smoke",
        ["84784828725C"],
        "http://ha.local/api/webhook/test",
    )

    assert managed_source_from_automation(payload) == "audio_alarm_smoke"


def test_managed_source_from_automation_accepts_legacy_name_prefix() -> None:
    payload = build_managed_automation_payload(
        "person",
        ["84784828725C"],
        "http://ha.local/api/webhook/test",
    )
    payload["name"] = "HA Protect Bridge: person"

    assert managed_source_from_automation(payload) == "person"


def test_managed_source_from_automation_ignores_unprefixed_webhook_url() -> None:
    payload = build_managed_automation_payload(
        "person",
        ["84784828725C"],
        "http://ha.local/api/webhook/test",
    )
    payload["name"] = "User managed person webhook"

    assert managed_source_from_automation(payload) is None


def test_automation_needs_replace_accepts_legacy_name_prefix() -> None:
    existing = build_managed_automation_payload(
        "person",
        ["84784828725C"],
        "http://ha.local/api/webhook/test",
    )
    existing["name"] = "HA Protect Bridge: person"
    desired = build_managed_automation_payload(
        "person",
        ["84784828725C"],
        "http://ha.local/api/webhook/test",
    )

    assert automation_needs_replace(existing, desired) is False


def test_managed_automation_mapping_prefers_current_prefix_and_groups_duplicates() -> None:
    legacy = build_managed_automation_payload(
        "person",
        ["84784828725C"],
        "http://ha.local/api/webhook/test",
    )
    legacy["id"] = "legacy"
    legacy["name"] = "HA Protect Bridge: person"
    current = build_managed_automation_payload(
        "person",
        ["84784828725C"],
        "http://ha.local/api/webhook/test",
    )
    current["id"] = "current"

    grouped = group_managed_automations([legacy, current])

    assert [item["id"] for item in grouped["person"]] == ["current", "legacy"]
    assert map_managed_automations([legacy, current])["person"]["id"] == "current"


def test_automation_needs_replace_detects_url_change() -> None:
    existing = build_managed_automation_payload(
        "person",
        ["84784828725C"],
        "http://ha.local/api/webhook/test",
    )
    desired = build_managed_automation_payload(
        "person",
        ["84784828725C"],
        "http://ha.local/api/webhook/other",
    )

    assert automation_needs_replace(existing, desired) is True
