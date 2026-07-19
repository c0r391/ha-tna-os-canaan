from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TnaOsCoordinator
from .entity import TnaOsEntity


CORE_VOLTAGE_KEY = "coreVoltage"

NUMBERS = (
    NumberEntityDescription(key="frequency", name="Frequency", native_min_value=100, native_max_value=600, native_step=1, native_unit_of_measurement="MHz", mode=NumberMode.BOX),
    NumberEntityDescription(key=CORE_VOLTAGE_KEY, name="Core voltage", native_min_value=3.1, native_max_value=3.9, native_step=0.01, native_unit_of_measurement="V", mode=NumberMode.BOX),
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
    def _is_core_voltage(self) -> bool:
        return self.entity_description.key == CORE_VOLTAGE_KEY

    @property
    def _core_voltage_is_volts(self) -> bool:
        """Return True when firmware reports/writes core voltage in volts.

        Nano 3s firmware reports ASIC Vcore in millivolts (for example 3650).
        Avalon Q currently reports the exposed voltage control in volts (about
        21.5-26.0).  Treat small numeric values as volts and larger values as mV.
        """
        value = self.coordinator.data.get(CORE_VOLTAGE_KEY)
        try:
            return value is not None and abs(float(value)) < 100
        except (TypeError, ValueError):
            return False

    @property
    def native_min_value(self) -> float | None:
        if self._is_core_voltage:
            return 21.5 if self._core_voltage_is_volts else 3.1
        return self.entity_description.native_min_value

    @property
    def native_max_value(self) -> float | None:
        if self._is_core_voltage:
            return 26.0 if self._core_voltage_is_volts else 3.9
        return self.entity_description.native_max_value

    @property
    def native_step(self) -> float | None:
        if self._is_core_voltage:
            return 0.1 if self._core_voltage_is_volts else 0.01
        return self.entity_description.native_step

    @property
    def native_unit_of_measurement(self) -> str | None:
        if self._is_core_voltage:
            return "V"
        return self.entity_description.native_unit_of_measurement

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            return None
        if self._is_core_voltage and not self._core_voltage_is_volts:
            return numeric_value / 1000
        return numeric_value

    async def async_set_native_value(self, value: float) -> None:
        if self._is_core_voltage:
            payload_value: int | float = float(value) if self._core_voltage_is_volts else int(round(float(value) * 1000))
        else:
            payload_value = int(value)
        await self.coordinator.client.patch_system({self.entity_description.key: payload_value})
        await self.coordinator.async_request_refresh()
