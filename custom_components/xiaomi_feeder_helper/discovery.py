"""Helpers to find Xiaomi pet feeders already set up via ha_xiaomi_home."""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .const import FEEDER_MODELS, XIAOMI_HOME_DOMAIN


def discover_feeders(hass: HomeAssistant) -> list[tuple[Any, str, dict]]:
    """Return (miot_client, did, device_info) tuples for known feeder models.

    Reads hass.data["xiaomi_home"]["miot_clients"], which is where the
    ha_xiaomi_home integration keeps its already-connected client objects
    (one per configured Xiaomi account), and checks each client's own
    device_list for a model we know is a pet feeder.
    """
    xiaomi_data = hass.data.get(XIAOMI_HOME_DOMAIN)
    if not xiaomi_data or "miot_clients" not in xiaomi_data:
        return []

    found: list[tuple[Any, str, dict]] = []
    for miot_client in xiaomi_data["miot_clients"].values():
        for did, info in miot_client.device_list.items():
            model = (info or {}).get("model", "") or ""
            if model in FEEDER_MODELS or "feeder" in model:
                found.append((miot_client, did, info))
    return found
