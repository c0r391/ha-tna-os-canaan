from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TnaOsCoordinator
from .entity import TnaOsEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: TnaOsCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TnaOsPowerSwitch(coordinator), TnaOsAutoFanSwitch(coordinator)])


class TnaOsPowerSwitch(TnaOsEntity, SwitchEntity):
    _attr_name = "Hashboard power"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: TnaOsCoordinator) -> None:
        super().__init__(coordinator, "hashboard_power")

    @property
    def is_on(self) -> bool:
        boards = self.coordinator.data.get("boards") or []
        return bool(boards and boards[0].get("enabled") and boards[0].get("state") == "active")

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.client.set_power(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.client.set_power(False)
        await self.coordinator.async_request_refresh()


class TnaOsAutoFanSwitch(TnaOsEntity, SwitchEntity):
    _attr_name = "Auto fan"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: TnaOsCoordinator) -> None:
        super().__init__(coordinator, "auto_fan")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("autofanspeed"))

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.client.patch_system({"autofanspeed": 1})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.client.patch_system({"autofanspeed": 0})
        await self.coordinator.async_request_refresh()
