from __future__ import annotations

import logging
from typing import Any

from .const import CONF_WEBHOOK_ID, DOMAIN, NAME

_LOGGER = logging.getLogger(__name__)
_ALLOWED_METHODS = ("GET", "POST", "PUT")


async def async_setup(hass: Any, config: dict[str, Any]) -> bool:
    return True


async def async_setup_entry(hass: Any, entry: Any) -> bool:
    from homeassistant.components import webhook

    from .webhook import async_handle_protect_webhook

    webhook_id = entry.data[CONF_WEBHOOK_ID]
    webhook.async_register(
        hass,
        DOMAIN,
        NAME,
        webhook_id,
        async_handle_protect_webhook,
        local_only=False,
        allowed_methods=_ALLOWED_METHODS,
    )
    _LOGGER.info(
        "Registered HA Protect Bridge webhook at %s",
        webhook.async_generate_path(webhook_id),
    )
    return True


async def async_unload_entry(hass: Any, entry: Any) -> bool:
    from homeassistant.components import webhook

    webhook.async_unregister(hass, entry.data[CONF_WEBHOOK_ID])
    return True
