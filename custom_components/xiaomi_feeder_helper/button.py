"""Button platform for Xiaomi Feeder Helper: adds a 'Feed now' button."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_PORTIONS, FEED_AIID, FEED_SIID, XIAOMI_HOME_DOMAIN
from .discovery import discover_feeders

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create one 'Feed now' button for every feeder found under xiaomi_home."""
    entities = [
        XiaomiFeedNowButton(miot_client, did, info)
        for miot_client, did, info in discover_feeders(hass)
    ]
    if not entities:
        _LOGGER.warning(
            "xiaomi_feeder_helper: no feeder found under xiaomi_home right now; "
            "reload this integration (Settings -> Devices & services) after "
            "your feeder shows up there"
        )
    async_add_entities(entities)


class XiaomiFeedNowButton(ButtonEntity):
    """A 'Feed now' button for one Xiaomi pet feeder."""

    _attr_has_entity_name = True
    _attr_name = "Feed now"
    _attr_icon = "mdi:paw"

    def __init__(self, miot_client, did: str, info: dict) -> None:
        self._miot_client = miot_client
        self._did = did
        did_tag = f"{miot_client.cloud_server}_{did}"
        self._attr_unique_id = f"{did_tag}_feed_now"
        # Attach to the SAME Home Assistant device xiaomi_home already
        # created for this feeder (identifiers must match exactly what
        # xiaomi_home's own MIoTDevice.device_info uses), so this button
        # shows up right next to the feeder's other entities instead of
        # creating a separate device card.
        self._attr_device_info = DeviceInfo(
            identifiers={(XIAOMI_HOME_DOMAIN, did_tag)}
        )

    async def async_press(self) -> None:
        result = await self._miot_client.miot_http.action_async(
            did=self._did,
            siid=FEED_SIID,
            aiid=FEED_AIID,
            in_list=[{"value": DEFAULT_PORTIONS}],
        )
        _LOGGER.info("feed now pressed for %s -> %s", self._did, result)
