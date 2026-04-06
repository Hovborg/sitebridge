from __future__ import annotations

from collections import Counter
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_WEBHOOK_BASE_URL,
    CONF_WEBHOOK_ID,
)
from .entry_runtime import get_entry_runtime

_ENTRY_REDACT = {
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_WEBHOOK_BASE_URL,
    CONF_WEBHOOK_ID,
}
_STATUS_REDACT = {
    CONF_HOST,
    "nvr_id",
    "nvr_name",
    "webhook_base_url_override",
    "webhook_path",
    "webhook_url",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: Any,
) -> dict[str, Any]:
    del hass
    runtime = get_entry_runtime(entry)
    return {
        "entry": {
            "entry_id": getattr(entry, "entry_id", None),
            "title": getattr(entry, "title", None),
            "state": getattr(entry, "state", None),
            "data": async_redact_data(dict(getattr(entry, "data", {})), _ENTRY_REDACT),
            "options": dict(getattr(entry, "options", {})),
        },
        "runtime": _runtime_diagnostics(runtime) if runtime is not None else None,
    }


def _runtime_diagnostics(runtime: Any) -> dict[str, Any]:
    cameras = list(runtime.catalog.get("cameras") or [])
    sensor_specs = runtime.iter_sensor_specs()

    model_counts = Counter((camera.get("model") or "Unknown") for camera in cameras)
    source_camera_counts = Counter(
        source
        for camera in cameras
        for source in (camera.get("supported_sources") or [])
    )
    sensor_counts = Counter(spec.source for spec in sensor_specs)
    active_sensor_counts = Counter(
        spec.source for spec in sensor_specs if runtime.get_sensor_state(spec.key) is not None
    )

    return {
        "status": async_redact_data(runtime.get_status_attributes(), _STATUS_REDACT),
        "catalog": {
            "camera_count": len(cameras),
            "doorbell_count": sum(bool(camera.get("is_doorbell")) for camera in cameras),
            "models": dict(sorted(model_counts.items())),
            "source_camera_counts": dict(sorted(source_camera_counts.items())),
            "cameras": [
                {
                    "index": index,
                    "model": camera.get("model") or "Unknown",
                    "is_doorbell": bool(camera.get("is_doorbell")),
                    "supported_sources": list(camera.get("supported_sources") or []),
                }
                for index, camera in enumerate(cameras, start=1)
            ],
        },
        "managed_automation_sources": sorted(runtime._managed_automations),
        "sensors": {
            "defined": len(sensor_specs),
            "by_source": dict(sorted(sensor_counts.items())),
            "active": sum(active_sensor_counts.values()),
            "active_by_source": dict(sorted(active_sensor_counts.items())),
        },
    }
