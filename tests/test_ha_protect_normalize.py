from custom_components.ha_protect_bridge.normalize import normalize_webhook_payload


def test_normalize_official_motion_sample_shape() -> None:
    payload = {
        "alarm": {
            "name": "Camera has detected motion",
            "sources": [],
            "conditions": [{"condition": {"type": "is", "source": "motion"}}],
            "triggers": [{"key": "motion", "device": "74ACB99F4E24"}],
        },
        "timestamp": 1727382771168,
    }

    normalized = normalize_webhook_payload(payload, {})

    assert normalized["alarm_name"] == "Camera has detected motion"
    assert normalized["primary_detection_type"] == "motion"
    assert normalized["detection_types"] == ["motion"]
    assert normalized["device_ids"] == ["74ACB99F4E24"]
    assert normalized["timestamp_iso"] is not None


def test_normalize_person_detection_from_alarm_manager_style_payload() -> None:
    payload = {
        "alarm": {
            "name": "Front Door detected a person",
            "conditions": [{"condition": {"type": "is", "source": "person"}}],
            "triggers": [{"key": "person", "device": "CAMERA01"}],
        }
    }

    normalized = normalize_webhook_payload(payload, {})

    assert normalized["primary_detection_type"] == "person"
    assert "person" in normalized["event_types"][0]


def test_normalize_query_only_animal_detection() -> None:
    normalized = normalize_webhook_payload(
        {},
        {
            "alarm": "Backyard animal detected",
            "key": "animal",
            "device": "CAMERA02",
        },
    )

    assert normalized["alarm_name"] == "Backyard animal detected"
    assert normalized["detection_types"] == ["animal"]
    assert normalized["device_ids"] == ["CAMERA02"]
