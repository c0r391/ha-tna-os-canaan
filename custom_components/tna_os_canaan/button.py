from __future__ import annotations

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TnaOsCoordinator
from .entity import TnaOsEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: TnaOsCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TnaOsRebootButton(coordinator), TnaOsBoardResetButton(coordinator)])


class TnaOsRebootButton(TnaOsEntity, ButtonEntity):
    _attr_name = "Reboot"
    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: TnaOsCoordinator) -> None:
        super().__init__(coordinator, "reboot")

    async def async_press(self) -> None:
        await self.coordinator.client.reboot()


class TnaOsBoardResetButton(TnaOsEntity, ButtonEntity):
    _attr_name = "Board reset"
    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: TnaOsCoordinator) -> None:
        super().__init__(coordinator, "board_reset")

    async def async_press(self) -> None:
        await self.coordinator.client.reset_board()
        await self.coordinator.async_request_refresh()
