"""
Xiaomi Feeder Helper
---------------------
Standalone helper integration. It does NOT modify or depend on the
xiaomi_home integration's own files, so it survives xiaomi_home updates.

Two things are provided:

1. A config flow ("Add integration" in the UI) that scans the already
   running xiaomi_home integration for known pet feeder models and, if
   found, adds a "Feed now" button entity attached to that same device
   (see button.py / discovery.py).

2. A generic service, `xiaomi_feeder_helper.call_action`, for calling ANY
   MIoT action by siid/aiid on any device xiaomi_home already manages, in
   case you need to work around a different missing entity later.

Both work by reaching into hass.data["xiaomi_home"]["miot_clients"] at
call/setup time - the same already-connected client objects xiaomi_home's
own entities use internally - rather than touching any of its files.
"""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, XIAOMI_HOME_DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["button"]

SERVICE_CALL_ACTION = "call_action"
SERVICE_CALL_ACTION_SCHEMA = vol.Schema(
    {
        vol.Required("did"): cv.string,
        vol.Required("siid"): vol.Coerce(int),
        vol.Required("aiid"): vol.Coerce(int),
        vol.Optional("params", default=[]): list,
    }
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the generic call_action service."""

    async def _async_handle_call_action(call: ServiceCall) -> None:
        did: str = str(call.data["did"])
        siid: int = call.data["siid"]
        aiid: int = call.data["aiid"]
        params: list = call.data.get("params", [])

        xiaomi_data = hass.data.get(XIAOMI_HOME_DOMAIN)
        if not xiaomi_data or "miot_clients" not in xiaomi_data:
            raise HomeAssistantError(
                "xiaomi_home integration is not loaded / not ready yet"
            )

        for miot_client in xiaomi_data["miot_clients"].values():
            if did not in miot_client.device_list:
                continue
            result = await miot_client.miot_http.action_async(
                did=did,
                siid=siid,
                aiid=aiid,
                in_list=[{"value": v} for v in params],
            )
            _LOGGER.info(
                "call_action result, %s.%s.%s -> %s", did, siid, aiid, result
            )
            return

        raise HomeAssistantError(
            f"xiaomi_feeder_helper: no xiaomi_home device found with did={did}"
        )

    if not hass.services.has_service(DOMAIN, SERVICE_CALL_ACTION):
        hass.services.async_register(
            DOMAIN,
            SERVICE_CALL_ACTION,
            _async_handle_call_action,
            schema=SERVICE_CALL_ACTION_SCHEMA,
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xiaomi Feeder Helper from a config entry: create Feed buttons."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
