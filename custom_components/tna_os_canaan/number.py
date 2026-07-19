from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TnaOsCoordinator
from .entity import TnaOsEntity


_LOGGER = logging.getLogger(__name__)
PSU_STRING_VOLTAGE_KEY = "psuVoutV"
PSU_STRING_VOLTAGE_PATCH_KEY = "stringVoltage"
PSU_STRING_VOLTAGE_VERIFY_DELAY = 1
PSU_STRING_VOLTAGE_TOLERANCE = 0.05


@dataclass(frozen=True, kw_only=True)
class TnaNumberDescription(NumberEntityDescription):
    patch_key: str | None = None


NUMBERS = (
    TnaNumberDescription(key="frequency", name="Frequency", native_min_value=100, native_max_value=600, native_step=1, native_unit_of_measurement="MHz", mode=NumberMode.BOX),
    TnaNumberDescription(key="coreVoltage", name="Core voltage", native_min_value=3100, native_max_value=3900, native_step=1, native_unit_of_measurement="mV", mode=NumberMode.BOX),
    TnaNumberDescription(key=PSU_STRING_VOLTAGE_KEY, name="PSU string voltage", native_min_value=21.5, native_max_value=26.0, native_step=0.1, native_unit_of_measurement="V", mode=NumberMode.BOX, patch_key=PSU_STRING_VOLTAGE_PATCH_KEY),
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
        if self.entity_description.key == PSU_STRING_VOLTAGE_KEY:
            return self.coordinator.data.get(PSU_STRING_VOLTAGE_KEY) is not None
        return super().available

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get(self.entity_description.key)
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        patch_key = self.entity_description.patch_key or self.entity_description.key
        payload_value: int | float = float(value) if patch_key == PSU_STRING_VOLTAGE_PATCH_KEY else int(value)
        await self.coordinator.client.patch_system({patch_key: payload_value})

        if patch_key == PSU_STRING_VOLTAGE_PATCH_KEY:
            await asyncio.sleep(PSU_STRING_VOLTAGE_VERIFY_DELAY)

        await self.coordinator.async_request_refresh()

        if patch_key == PSU_STRING_VOLTAGE_PATCH_KEY:
            self._warn_if_psu_string_voltage_not_applied(float(payload_value))

    def _warn_if_psu_string_voltage_not_applied(self, requested_value: float) -> None:
        readback = self.coordinator.data.get(PSU_STRING_VOLTAGE_KEY)
        try:
            actual_value = float(readback)
        except (TypeError, ValueError):
            _LOGGER.warning(
                "TNA-OS did not provide %s after writing %s=%.2f V; cannot verify PSU string voltage",
                PSU_STRING_VOLTAGE_KEY,
                PSU_STRING_VOLTAGE_PATCH_KEY,
                requested_value,
            )
            return

        if abs(actual_value - requested_value) > PSU_STRING_VOLTAGE_TOLERANCE:
            _LOGGER.warning(
                "TNA-OS did not apply %s=%.2f V; %s readback remains %.2f V. "
                "Keeping Home Assistant state at the API readback value. Verify the writable field in the upstream TNA-OS API.",
                PSU_STRING_VOLTAGE_PATCH_KEY,
                requested_value,
                PSU_STRING_VOLTAGE_KEY,
                actual_value,
            )
