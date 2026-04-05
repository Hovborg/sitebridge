from homeassistant.helpers.config_entry_flow import register_webhook_flow

from .const import DOMAIN, NAME

register_webhook_flow(DOMAIN, NAME, {}, allow_multiple=False)
