from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TnaOsApiError, TnaOsClient
from .const import DEFAULT_NAME, DOMAIN


class TnaOsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            client = TnaOsClient(async_get_clientsession(self.hass), host)
            try:
                info = await client.info()
            except TnaOsApiError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(str(info.get("macAddr") or info.get("eepromSerial") or host))
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                title = user_input.get(CONF_NAME) or info.get("hostname") or info.get("deviceModel") or DEFAULT_NAME
                return self.async_create_entry(title=title, data={CONF_HOST: host, CONF_NAME: title})

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
