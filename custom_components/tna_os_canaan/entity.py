from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TnaOsCoordinator


class TnaOsEntity(CoordinatorEntity[TnaOsCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: TnaOsCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._key = key
        serial = coordinator.data.get("eepromSerial") or coordinator.data.get("macAddr") or coordinator.client.host
        self._attr_unique_id = f"{serial}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(serial))},
            "name": coordinator.data.get("hostname") or coordinator.data.get("deviceModel") or "TNA-OS Miner",
            "manufacturer": "Canaan / TNA-OS",
            "model": coordinator.data.get("deviceModel") or coordinator.data.get("minerModel"),
            "sw_version": coordinator.data.get("version"),
            "configuration_url": coordinator.client.base_url,
        }
