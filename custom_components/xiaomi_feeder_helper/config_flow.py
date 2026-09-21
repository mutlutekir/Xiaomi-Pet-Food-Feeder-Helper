"""Config flow for Xiaomi Feeder Helper.

Zero manual input: it scans the already-running xiaomi_home integration for
known feeder models and, if it finds at least one, lets you add a single
entry that creates a 'Feed now' button for each one found.
"""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN
from .discovery import discover_feeders


class XiaomiFeederHelperConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Xiaomi Feeder Helper."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        feeders = discover_feeders(self.hass)
        if not feeders:
            return self.async_abort(reason="no_feeder_found")

        if user_input is not None:
            return self.async_create_entry(title="Xiaomi Feeder Helper", data={})

        names = ", ".join(
            (info or {}).get("name") or did for _, did, info in feeders
        )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={"feeders": names},
        )
