from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TnaOsCoordinator
from .entity import TnaOsEntity


@dataclass(frozen=True, kw_only=True)
class TnaNumberDescription(NumberEntityDescription):
    patch_key: str | None = None


NUMBERS = (
    TnaNumberDescription(key="frequency", name="Frequency", native_min_value=100, native_max_value=600, native_step=1, native_unit_of_measurement="MHz", mode=NumberMode.BOX),
    TnaNumberDescription(key="coreVoltage", name="Core voltage", native_min_value=3100, native_max_value=3900, native_step=1, native_unit_of_measurement="mV", mode=NumberMode.BOX),
    TnaNumberDescription(key="psuVoutV", name="PSU string voltage", native_min_value=21.5, native_max_value=26.0, native_step=0.1, native_unit_of_measurement="V", mode=NumberMode.BOX, patch_key="stringVoltage"),
    TnaNumberDescription(key="fanspeed", name="Fan speed", native_min_value=0, native_max_value=100, native_step=1, native_unit_of_measurement="%", mode=NumberMode.SLIDER),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: TnaOsCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(TnaOsNumber(coordinator, desc) for desc in NUMBERS)


class TnaOsNumber(TnaOsEntity, NumberEntity):
    entity_description: TnaNumberDescription

    def __init__(self, coordinator: TnaOsCoordinator, description: TnaNumberDescription) -> None:
        super().__init__(coordinator, f"set_{description.key}")
        self.entity_description = description
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def available(self) -> bool:
        if self.entity_description.key == "psuVoutV":
            return self.coordinator.data.get("psuVoutV") is not None
        return super().available

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get(self.entity_description.key)
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        patch_key = self.entity_description.patch_key or self.entity_description.key
        payload_value: int | float = float(value) if patch_key == "stringVoltage" else int(value)
        await self.coordinator.client.patch_system({patch_key: payload_value})
        await self.coordinator.async_request_refresh()
