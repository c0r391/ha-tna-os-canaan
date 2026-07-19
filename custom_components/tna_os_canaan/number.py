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
CORE_VOLTAGE_KEY = "coreVoltage"
PSU_STRING_VOLTAGE_KEY = "psuVoutV"
VOLTAGE_VERIFY_DELAY = 1
AVALON_Q_VOLTAGE_TOLERANCE = 0.05
NANO_VOLTAGE_TOLERANCE = 1.0


@dataclass(frozen=True, kw_only=True)
class TnaNumberDescription(NumberEntityDescription):
    patch_key: str | None = None


NUMBERS = (
    TnaNumberDescription(key="frequency", name="Frequency", native_min_value=100, native_max_value=600, native_step=1, native_unit_of_measurement="MHz", mode=NumberMode.BOX),
    TnaNumberDescription(key=CORE_VOLTAGE_KEY, name="Core voltage", native_min_value=3100, native_max_value=3900, native_step=1, native_unit_of_measurement="mV", mode=NumberMode.BOX),
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
    def native_min_value(self) -> float | None:
        if self._is_core_voltage and self._is_avalon_q:
            return 21.5
        return self.entity_description.native_min_value

    @property
    def native_max_value(self) -> float | None:
        if self._is_core_voltage and self._is_avalon_q:
            return 26.0
        return self.entity_description.native_max_value

    @property
    def native_step(self) -> float | None:
        if self._is_core_voltage and self._is_avalon_q:
            return 0.1
        return self.entity_description.native_step

    @property
    def native_unit_of_measurement(self) -> str | None:
        if self._is_core_voltage and self._is_avalon_q:
            return "V"
        return self.entity_description.native_unit_of_measurement

    @property
    def native_value(self) -> float | None:
        if self._is_core_voltage and self._is_avalon_q:
            value = self._avalon_q_voltage_readback()
        else:
            value = self.coordinator.data.get(self.entity_description.key)
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        patch_key = self.entity_description.patch_key or self.entity_description.key
        payload_value: int | float = self._payload_value(value, patch_key)
        await self.coordinator.client.patch_system({patch_key: payload_value})

        if patch_key == CORE_VOLTAGE_KEY:
            await asyncio.sleep(VOLTAGE_VERIFY_DELAY)

        await self.coordinator.async_request_refresh()

        if patch_key == CORE_VOLTAGE_KEY:
            self._warn_if_core_voltage_not_applied(float(payload_value))

    @property
    def _is_core_voltage(self) -> bool:
        return self.entity_description.key == CORE_VOLTAGE_KEY

    @property
    def _is_avalon_q(self) -> bool:
        model = " ".join(
            str(self.coordinator.data.get(key) or "")
            for key in ("minerModel", "deviceModel")
        ).lower()
        return "avalon q" in model

    def _payload_value(self, value: float, patch_key: str) -> int | float:
        if patch_key == CORE_VOLTAGE_KEY and self._is_avalon_q:
            return float(value)
        return int(value)

    def _avalon_q_voltage_readback(self) -> float | int | None:
        # Current Q firmware applies string-rail voltage via coreVoltage in volts, while
        # psuVoutV remains the UI/setpoint readback. Prefer psuVoutV when available.
        for key in (PSU_STRING_VOLTAGE_KEY, CORE_VOLTAGE_KEY):
            value = self.coordinator.data.get(key)
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                continue
            if numeric <= 0:
                continue
            # Be defensive if a future/older build reports coreVoltage in mV despite Q mode.
            if key == CORE_VOLTAGE_KEY and numeric > 100:
                return numeric / 1000
            return numeric
        return None

    def _warn_if_core_voltage_not_applied(self, requested_value: float) -> None:
        if self._is_avalon_q:
            readback = self._avalon_q_voltage_readback()
            readback_key = PSU_STRING_VOLTAGE_KEY if self.coordinator.data.get(PSU_STRING_VOLTAGE_KEY) not in (None, 0, 0.0, "0") else CORE_VOLTAGE_KEY
            tolerance = AVALON_Q_VOLTAGE_TOLERANCE
            unit = "V"
        else:
            readback = self.coordinator.data.get(CORE_VOLTAGE_KEY)
            readback_key = CORE_VOLTAGE_KEY
            tolerance = NANO_VOLTAGE_TOLERANCE
            unit = "mV"

        if readback is None:
            _LOGGER.warning(
                "TNA-OS did not provide %s after writing %s=%.2f %s; cannot verify core voltage",
                readback_key,
                CORE_VOLTAGE_KEY,
                requested_value,
                unit,
            )
            return

        try:
            actual_value = float(readback)
        except (TypeError, ValueError):
            _LOGGER.warning(
                "TNA-OS did not provide %s after writing %s=%.2f %s; cannot verify core voltage",
                readback_key,
                CORE_VOLTAGE_KEY,
                requested_value,
                unit,
            )
            return

        if abs(actual_value - requested_value) > tolerance:
            _LOGGER.warning(
                "TNA-OS did not apply %s=%.2f %s; %s readback remains %.2f %s. "
                "Keeping Home Assistant state at the API readback value.",
                CORE_VOLTAGE_KEY,
                requested_value,
                unit,
                readback_key,
                actual_value,
                unit,
            )
