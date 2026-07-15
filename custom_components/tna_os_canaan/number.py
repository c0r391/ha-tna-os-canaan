from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TnaOsCoordinator
from .entity import TnaOsEntity


NUMBERS = (
    NumberEntityDescription(key="frequency", name="Frequency", native_min_value=100, native_max_value=600, native_step=1, native_unit_of_measurement="MHz", mode=NumberMode.BOX),
    NumberEntityDescription(key="coreVoltage", name="Core voltage", native_min_value=3100, native_max_value=3900, native_step=1, native_unit_of_measurement="mV", mode=NumberMode.BOX),
    NumberEntityDescription(key="fanspeed", name="Fan speed", native_min_value=0, native_max_value=100, native_step=1, native_unit_of_measurement="%", mode=NumberMode.SLIDER),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: TnaOsCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(TnaOsNumber(coordinator, desc) for desc in NUMBERS)


class TnaOsNumber(TnaOsEntity, NumberEntity):
    def __init__(self, coordinator: TnaOsCoordinator, description: NumberEntityDescription) -> None:
        super().__init__(coordinator, f"set_{description.key}")
        self.entity_description = description
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get(self.entity_description.key)
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.client.patch_system({self.entity_description.key: int(value)})
        await self.coordinator.async_request_refresh()
