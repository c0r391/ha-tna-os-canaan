from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfElectricCurrent, UnitOfPower, UnitOfTemperature
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


def first_present(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = data.get(key)
        if value is not None:
            return value
    return None


def first_board(data: dict[str, Any]) -> dict[str, Any]:
    boards = data.get("boards") or []
    return boards[0] if boards else {}


def max_chip_temp(data: dict[str, Any]) -> Any:
    temps = first_board(data).get("chipTemps") or []
    return max(temps) if temps else None


def avg_chip_temp(data: dict[str, Any]) -> Any:
    temps = first_board(data).get("chipTemps") or []
    return round(sum(temps) / len(temps), 1) if temps else None


def chip_count(data: dict[str, Any]) -> Any:
    return first_board(data).get("chips") or data.get("asicCount")


def fan_rpms(data: dict[str, Any]) -> Any:
    rpms = data.get("fanRpms")
    if isinstance(rpms, list) and rpms:
        return ", ".join(str(int(rpm)) for rpm in rpms if rpm is not None)
    return None


def pool_mode(data: dict[str, Any]) -> str | None:
    mode = (data.get("stratum") or {}).get("poolMode", data.get("poolMode"))
    if mode == 0:
        return "failover"
    if mode == 1:
        return "multipool"
    return None if mode is None else str(mode)


def board_state(data: dict[str, Any]) -> Any:
    return first_board(data).get("state") or data.get("state")


def runtime_state(data: dict[str, Any]) -> Any:
    return first_board(data).get("runtimeState") or data.get("runtimeState")


def thermal_zone(data: dict[str, Any]) -> Any:
    return first_board(data).get("thermalZone") or data.get("thermalZone")


def chip_nonce_sum(data: dict[str, Any]) -> Any:
    nonces = first_board(data).get("chipNonces30s") or []
    return sum(nonces) if nonces else None


SENSORS: tuple[TnaSensorDescription, ...] = (
    # Hashrate, shares and efficiency. TNA-OS reports hashrate in GH/s; expose TH/s for HA.
    TnaSensorDescription(key="hashRate_10m", name="Hashrate 10m", native_unit_of_measurement="TH/s", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: gh_to_th(d.get("hashRate_10m"))),
    TnaSensorDescription(key="hashRate_1m", name="Hashrate 1m", native_unit_of_measurement="TH/s", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: gh_to_th(d.get("hashRate_1m"))),
    TnaSensorDescription(key="hashRate", name="Hashrate", native_unit_of_measurement="TH/s", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: gh_to_th(d.get("hashRate"))),
    TnaSensorDescription(key="hashRate_1h", name="Hashrate 1h", native_unit_of_measurement="TH/s", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: gh_to_th(d.get("hashRate_1h"))),
    TnaSensorDescription(key="hashRate_1d", name="Hashrate 1d", native_unit_of_measurement="TH/s", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: gh_to_th(d.get("hashRate_1d"))),
    TnaSensorDescription(key="power", name="Power", device_class=SensorDeviceClass.POWER, native_unit_of_measurement=UnitOfPower.WATT, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("power")),
    TnaSensorDescription(key="maxPower", name="Max power", device_class=SensorDeviceClass.POWER, native_unit_of_measurement=UnitOfPower.WATT, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("maxPower")),
    TnaSensorDescription(key="hashEfficiency", name="Hash efficiency", native_unit_of_measurement="GH/W", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("hashEfficiency")),
    TnaSensorDescription(key="j_per_th", name="Efficiency", native_unit_of_measurement="J/TH", state_class=SensorStateClass.MEASUREMENT, value_fn=j_per_th),
    TnaSensorDescription(key="sharesAccepted", name="Shares accepted", state_class=SensorStateClass.TOTAL_INCREASING, value_fn=lambda d: d.get("sharesAccepted")),
    TnaSensorDescription(key="sharesRejected", name="Shares rejected", state_class=SensorStateClass.TOTAL_INCREASING, value_fn=lambda d: d.get("sharesRejected")),
    TnaSensorDescription(key="sharesSubmitted", name="Shares submitted", state_class=SensorStateClass.TOTAL_INCREASING, value_fn=lambda d: d.get("sharesSubmitted")),
    TnaSensorDescription(key="bestDiff", name="Best difficulty", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("bestDiff")),
    TnaSensorDescription(key="bestSessionDiff", name="Best session difficulty", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("bestSessionDiff")),
    TnaSensorDescription(key="poolDifficulty", name="Pool difficulty", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("poolDifficulty") or active_pool(d).get("poolDifficulty")),

    # Temperatures and fan telemetry. API v0.3.x adds board/VR aliases and Avalon Q fanRpms.
    TnaSensorDescription(key="temp", name="Temperature", device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("temp")),
    TnaSensorDescription(key="vr_temp", name="VR temperature", device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: first_present(d, "vrTemp", "boardtemp1", "boardtemp2")),
    TnaSensorDescription(key="board_probe_temp", name="Board probe temperature", device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("boardProbeTemp")),
    TnaSensorDescription(key="overheat_temp", name="Overheat threshold", device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("overheat_temp")),
    TnaSensorDescription(key="chip_max_temp", name="Chip max temperature", device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS, state_class=SensorStateClass.MEASUREMENT, value_fn=max_chip_temp),
    TnaSensorDescription(key="chip_avg_temp", name="Chip average temperature", device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS, state_class=SensorStateClass.MEASUREMENT, value_fn=avg_chip_temp),
    TnaSensorDescription(key="fanRpm", name="Fan RPM", native_unit_of_measurement="rpm", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("fanRpm")),
    TnaSensorDescription(key="fanRpms", name="Fan RPMs", value_fn=fan_rpms),
    TnaSensorDescription(key="fanspeed", name="Fan duty", native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: first_present(d, "fanspeed", "manualFanSpeed", "fanDuty")),

    # Frequency and voltage/power rails. Covers Nano 3s USB-C PD and Avalon Q string-rail fields.
    TnaSensorDescription(key="frequency", name="Frequency", native_unit_of_measurement="MHz", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("frequency") or d.get("defaultFrequency")),
    TnaSensorDescription(key="defaultFrequency", name="Target frequency", native_unit_of_measurement="MHz", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("defaultFrequency")),
    TnaSensorDescription(key="coreVoltage", name="Core voltage setpoint", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement="mV", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("coreVoltage")),
    TnaSensorDescription(key="coreVoltageActual", name="Core voltage actual", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement="mV", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("coreVoltageActual")),
    TnaSensorDescription(key="voltage", name="Input voltage", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement="mV", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("voltage")),
    TnaSensorDescription(key="current", name="Input current", device_class=SensorDeviceClass.CURRENT, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("current")),
    TnaSensorDescription(key="psu_voltage", name="PSU negotiated voltage", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement="V", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: first_present(d, "vcoreV", "psuVoltageV")),
    TnaSensorDescription(key="psuVoutV", name="PSU string voltage setpoint", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement="V", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("psuVoutV")),
    TnaSensorDescription(key="psuVoutActualV", name="PSU string voltage actual", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement="V", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("psuVoutActualV")),
    TnaSensorDescription(key="psuIoutA", name="PSU output current", device_class=SensorDeviceClass.CURRENT, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("psuIoutA")),
    TnaSensorDescription(key="psuPoutW", name="PSU output power", device_class=SensorDeviceClass.POWER, native_unit_of_measurement=UnitOfPower.WATT, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("psuPoutW")),
    TnaSensorDescription(key="bypassVoltage", name="Bypass voltage", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement="V", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("bypassVoltage")),

    # Network and identity.
    TnaSensorDescription(key="networkMode", name="Network mode", value_fn=lambda d: d.get("networkMode")),
    TnaSensorDescription(key="wifiSignalPct", name="WiFi signal", native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("wifiSignalPct")),
    TnaSensorDescription(key="wifiLinkQualityPct", name="WiFi link quality", native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("wifiLinkQualityPct")),
    TnaSensorDescription(key="wifiRSSI", name="WiFi RSSI", native_unit_of_measurement="dBm", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("wifiRSSI")),
    TnaSensorDescription(key="ethRxKbps", name="Ethernet RX", native_unit_of_measurement="kbps", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("ethRxKbps")),
    TnaSensorDescription(key="ethTxKbps", name="Ethernet TX", native_unit_of_measurement="kbps", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("ethTxKbps")),
    TnaSensorDescription(key="ethRxTotalMB", name="Ethernet RX total", native_unit_of_measurement="MB", state_class=SensorStateClass.TOTAL_INCREASING, value_fn=lambda d: d.get("ethRxTotalMB")),
    TnaSensorDescription(key="ethTxTotalMB", name="Ethernet TX total", native_unit_of_measurement="MB", state_class=SensorStateClass.TOTAL_INCREASING, value_fn=lambda d: d.get("ethTxTotalMB")),
    TnaSensorDescription(key="ethIPv4", name="Ethernet IPv4", value_fn=lambda d: d.get("ethIPv4") or d.get("hostip")),
    TnaSensorDescription(key="ssid", name="WiFi SSID", value_fn=lambda d: d.get("ssid")),
    TnaSensorDescription(key="wifiStatus", name="WiFi status", value_fn=lambda d: d.get("wifiStatus")),
    TnaSensorDescription(key="apSsid", name="Setup AP SSID", value_fn=lambda d: d.get("apSsid")),
    TnaSensorDescription(key="apIp", name="Setup AP IP", value_fn=lambda d: d.get("apIp")),
    TnaSensorDescription(key="uptimeSeconds", name="Miner uptime", native_unit_of_measurement="s", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("uptimeSeconds")),
    TnaSensorDescription(key="systemUptimeSecs", name="System uptime", native_unit_of_measurement="s", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("systemUptimeSecs")),
    TnaSensorDescription(key="asicCount", name="ASIC count", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("asicCount")),
    TnaSensorDescription(key="smallCoreCount", name="Core count", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("smallCoreCount")),

    # Pool and board state.
    TnaSensorDescription(key="pool_mode", name="Pool mode", value_fn=pool_mode),
    TnaSensorDescription(key="active_pool_status", name="Active pool status", value_fn=lambda d: active_pool(d).get("status")),
    TnaSensorDescription(key="active_pool_protocol", name="Active pool protocol", value_fn=lambda d: active_pool(d).get("protocol")),
    TnaSensorDescription(key="active_pool_quota", name="Active pool effective quota", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: active_pool(d).get("effectiveQuota")),
    TnaSensorDescription(key="board_state", name="Board state", value_fn=board_state),
    TnaSensorDescription(key="runtime_state", name="Runtime state", value_fn=runtime_state),
    TnaSensorDescription(key="thermal_zone", name="Thermal zone", value_fn=thermal_zone),
    TnaSensorDescription(key="fault_reason", name="Fault reason", value_fn=lambda d: first_board(d).get("faultReason") or d.get("faultReason")),
    TnaSensorDescription(key="board_chips", name="Responding chips", state_class=SensorStateClass.MEASUREMENT, value_fn=chip_count),
    TnaSensorDescription(key="chip_nonce_sum", name="Chip share attribution", state_class=SensorStateClass.TOTAL_INCREASING, value_fn=chip_nonce_sum),
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
