from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfElectricCurrent, UnitOfPower, UnitOfTemperature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TnaOsCoordinator
from .entity import TnaOsEntity


@dataclass(frozen=True, kw_only=True)
class TnaSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]


def gh_to_th(value: Any) -> Any:
    return round(float(value) / 1000, 3) if value is not None else None


def j_per_th(data: dict[str, Any]) -> Any:
    power = data.get("power")
    hashrate = data.get("hashRate_10m") or data.get("hashRate")
    if power is None or not hashrate:
        return None
    ths = float(hashrate) / 1000
    return round(float(power) / ths, 2) if ths else None


def active_pool(data: dict[str, Any]) -> dict[str, Any]:
    pools = (data.get("stratum") or {}).get("pools") or []
    for pool in pools:
        if pool.get("connected") or pool.get("status") == "alive":
            return pool
    return pools[0] if pools else {}


def pool_mode(data: dict[str, Any]) -> str | None:
    mode = (data.get("stratum") or {}).get("poolMode")
    if mode == 0:
        return "failover"
    if mode == 1:
        return "multipool"
    return None if mode is None else str(mode)


SENSORS: tuple[TnaSensorDescription, ...] = (
    TnaSensorDescription(key="hashRate_10m", name="Hashrate 10m", native_unit_of_measurement="TH/s", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: gh_to_th(d.get("hashRate_10m"))),
    TnaSensorDescription(key="hashRate_1m", name="Hashrate 1m", native_unit_of_measurement="TH/s", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: gh_to_th(d.get("hashRate_1m"))),
    TnaSensorDescription(key="hashRate", name="Hashrate", native_unit_of_measurement="TH/s", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: gh_to_th(d.get("hashRate"))),
    TnaSensorDescription(key="hashRate_1h", name="Hashrate 1h", native_unit_of_measurement="TH/s", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: gh_to_th(d.get("hashRate_1h"))),
    TnaSensorDescription(key="hashRate_1d", name="Hashrate 1d", native_unit_of_measurement="TH/s", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: gh_to_th(d.get("hashRate_1d"))),
    TnaSensorDescription(key="power", name="Power", device_class=SensorDeviceClass.POWER, native_unit_of_measurement=UnitOfPower.WATT, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("power")),
    TnaSensorDescription(key="hashEfficiency", name="Hash efficiency", native_unit_of_measurement="GH/W", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("hashEfficiency")),
    TnaSensorDescription(key="j_per_th", name="Efficiency", native_unit_of_measurement="J/TH", state_class=SensorStateClass.MEASUREMENT, value_fn=j_per_th),
    TnaSensorDescription(key="temp", name="Temperature", device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("temp")),
    TnaSensorDescription(key="chip_max_temp", name="Chip max temperature", device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: max((d.get("boards") or [{}])[0].get("chipTemps") or []) if (d.get("boards") or [{}])[0].get("chipTemps") else None),
    TnaSensorDescription(key="fanRpm", name="Fan RPM", native_unit_of_measurement="rpm", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("fanRpm")),
    TnaSensorDescription(key="fanspeed", name="Fan duty", native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("fanspeed")),
    TnaSensorDescription(key="frequency", name="Frequency", native_unit_of_measurement="MHz", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("frequency") or d.get("defaultFrequency")),
    TnaSensorDescription(key="coreVoltage", name="Core voltage", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement="mV", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("coreVoltage")),
    TnaSensorDescription(key="voltage", name="Input voltage", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement="mV", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("voltage")),
    TnaSensorDescription(key="current", name="Input current", device_class=SensorDeviceClass.CURRENT, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("current")),
    TnaSensorDescription(key="sharesAccepted", name="Shares accepted", state_class=SensorStateClass.TOTAL_INCREASING, value_fn=lambda d: d.get("sharesAccepted")),
    TnaSensorDescription(key="sharesRejected", name="Shares rejected", state_class=SensorStateClass.TOTAL_INCREASING, value_fn=lambda d: d.get("sharesRejected")),
    TnaSensorDescription(key="sharesSubmitted", name="Shares submitted", state_class=SensorStateClass.TOTAL_INCREASING, value_fn=lambda d: d.get("sharesSubmitted")),
    TnaSensorDescription(key="bestDiff", name="Best difficulty", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("bestDiff")),
    TnaSensorDescription(key="bestSessionDiff", name="Best session difficulty", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("bestSessionDiff")),
    TnaSensorDescription(key="poolDifficulty", name="Pool difficulty", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("poolDifficulty") or active_pool(d).get("poolDifficulty")),
    TnaSensorDescription(key="networkMode", name="Network mode", value_fn=lambda d: d.get("networkMode")),
    TnaSensorDescription(key="wifiRSSI", name="WiFi RSSI", native_unit_of_measurement="dBm", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("wifiRSSI")),
    TnaSensorDescription(key="pool_mode", name="Pool mode", value_fn=pool_mode),
    TnaSensorDescription(key="active_pool_status", name="Active pool status", value_fn=lambda d: active_pool(d).get("status")),
    TnaSensorDescription(key="active_pool_protocol", name="Active pool protocol", value_fn=lambda d: active_pool(d).get("protocol")),
    TnaSensorDescription(key="active_pool_quota", name="Active pool effective quota", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: active_pool(d).get("effectiveQuota")),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: TnaOsCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(TnaOsSensor(coordinator, desc) for desc in SENSORS)


class TnaOsSensor(TnaOsEntity, SensorEntity):
    entity_description: TnaSensorDescription

    def __init__(self, coordinator: TnaOsCoordinator, description: TnaSensorDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)
