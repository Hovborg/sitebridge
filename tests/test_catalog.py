from custom_components.unifi_protect_bridge.catalog import build_camera_catalog, resolve_cameras


def test_build_camera_catalog_maps_normal_camera_and_doorbell_capabilities() -> None:
    catalog = build_camera_catalog(
        {
            "nvr": {"id": "nvr1", "name": "UDM SE"},
            "cameras": [
                {
                    "id": "cam-front",
                    "mac": "1C:6A:1B:0E:81:73",
                    "name": "Front Door",
                    "lastMotion": 1234567890,
                    "lastRing": 1234567999,
                    "featureFlags": {"isDoorbell": True},
                    "smartDetectSettings": {
                        "objectTypes": ["person", "package", "face"],
                        "audioTypes": [],
                    },
                },
                {
                    "id": "cam-kitchen",
                    "mac": "84784828725C",
                    "name": "Kitchen",
                    "featureFlags": {"isDoorbell": False},
                    "smartDetectSettings": {
                        "objectTypes": ["person", "vehicle", "animal", "licensePlate"],
                        "audioTypes": ["alrmSmoke", "alrmGlassBreak", "alrmBabyCry"],
                    },
                },
            ],
        }
    )

    assert catalog["nvr_id"] == "nvr1"
    assert catalog["nvr_name"] == "UDM SE"
    assert catalog["managed_sources"] == [
        "motion",
        "person",
        "vehicle",
        "animal",
        "package",
        "license_plate_of_interest",
        "ring",
        "face",
        "face_unknown",
        "face_known",
        "face_of_interest",
        "audio_alarm_baby_cry",
        "audio_alarm_glass_break",
        "audio_alarm_smoke",
    ]

    front_door = next(camera for camera in catalog["cameras"] if camera["camera_id"] == "cam-front")
    assert front_door["last_motion_ms"] == 1234567890
    assert front_door["last_ring_ms"] == 1234567999
    assert front_door["supported_sources"] == [
        "motion",
        "person",
        "package",
        "ring",
        "face",
        "face_unknown",
        "face_known",
        "face_of_interest",
    ]

    kitchen = next(camera for camera in catalog["cameras"] if camera["camera_id"] == "cam-kitchen")
    assert kitchen["supported_sources"] == [
        "motion",
        "person",
        "vehicle",
        "animal",
        "license_plate_of_interest",
        "audio_alarm_baby_cry",
        "audio_alarm_glass_break",
        "audio_alarm_smoke",
    ]


def test_resolve_cameras_matches_on_normalized_mac() -> None:
    catalog = build_camera_catalog(
        {
            "cameras": [
                {
                    "id": "cam-kitchen",
                    "mac": "84:78:48:28:72:5C",
                    "name": "Kitchen",
                    "featureFlags": {"isDoorbell": False},
                    "smartDetectSettings": {"objectTypes": ["person"], "audioTypes": []},
                }
            ]
        }
    )

    resolved = resolve_cameras(catalog, ["84784828725c"])

    assert len(resolved) == 1
    assert resolved[0]["name"] == "Kitchen"


def test_build_camera_catalog_skips_motion_when_explicitly_disabled() -> None:
    catalog = build_camera_catalog(
        {
            "cameras": [
                {
                    "id": "cam-no-motion",
                    "mac": "84:78:48:28:72:5C",
                    "name": "No Motion",
                    "featureFlags": {"hasMotionZones": False},
                    "smartDetectSettings": {"objectTypes": ["person"], "audioTypes": []},
                },
                {
                    "id": "cam-motion-off",
                    "mac": "1C:6A:1B:0E:81:73",
                    "name": "Motion Off",
                    "motionSettings": {"enabled": False},
                    "smartDetectSettings": {"objectTypes": [], "audioTypes": []},
                },
            ]
        }
    )

    no_motion = next(
        camera for camera in catalog["cameras"] if camera["camera_id"] == "cam-no-motion"
    )
    motion_off = next(
        camera for camera in catalog["cameras"] if camera["camera_id"] == "cam-motion-off"
    )

    assert no_motion["supported_sources"] == ["person"]
    assert motion_off["supported_sources"] == []
    assert catalog["managed_sources"] == ["person"]


def test_build_camera_catalog_skips_motion_without_history_zones_or_algorithms() -> None:
    catalog = build_camera_catalog(
        {
            "cameras": [
                {
                    "id": "third-party",
                    "mac": "84:78:48:28:72:5C",
                    "marketName": "Third Party Camera",
                    "featureFlags": {
                        "hasMotionZones": True,
                        "motionAlgorithms": [],
                    },
                    "motionZones": [],
                    "smartDetectSettings": {"objectTypes": [], "audioTypes": []},
                },
                {
                    "id": "native",
                    "mac": "1C:6A:1B:0E:81:73",
                    "marketName": "G6 Instant",
                    "featureFlags": {
                        "hasMotionZones": True,
                        "motionAlgorithms": ["enhanced"],
                    },
                    "motionZones": [],
                    "smartDetectSettings": {"objectTypes": [], "audioTypes": []},
                },
            ]
        }
    )

    third_party = next(
        camera for camera in catalog["cameras"] if camera["camera_id"] == "third-party"
    )
    native = next(camera for camera in catalog["cameras"] if camera["camera_id"] == "native")

    assert third_party["supported_sources"] == []
    assert native["supported_sources"] == ["motion"]
