from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TnaOsCoordinator
from .entity import TnaOsEntity


@dataclass(frozen=True, kw_only=True)
class TnaBinaryDescription(BinarySensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], bool]


BINARY_SENSORS = (
    TnaBinaryDescription(key="pool_connected", name="Pool connected", device_class=BinarySensorDeviceClass.CONNECTIVITY, value_fn=lambda d: any(p.get("connected") or p.get("status") == "alive" for p in (d.get("stratum") or {}).get("pools", []))),
    TnaBinaryDescription(key="power_valid", name="Power telemetry valid", value_fn=lambda d: bool(d.get("powerValid", False))),
    TnaBinaryDescription(key="shitcoin_detected", name="Shitcoin detected", device_class=BinarySensorDeviceClass.PROBLEM, value_fn=lambda d: bool(d.get("shitcoinDetected", False))),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: TnaOsCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(TnaOsBinarySensor(coordinator, desc) for desc in BINARY_SENSORS)


class TnaOsBinarySensor(TnaOsEntity, BinarySensorEntity):
    entity_description: TnaBinaryDescription

    def __init__(self, coordinator: TnaOsCoordinator, description: TnaBinaryDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool:
        return self.entity_description.value_fn(self.coordinator.data)
