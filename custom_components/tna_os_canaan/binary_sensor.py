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


def active_pools(data: dict[str, Any]) -> list[dict[str, Any]]:
    return (data.get("stratum") or {}).get("pools") or []


def board(data: dict[str, Any]) -> dict[str, Any]:
    boards = data.get("boards") or []
    return boards[0] if boards else {}


def truthy(data: dict[str, Any], key: str) -> bool:
    value = data.get(key)
    return bool(value) and value not in ("0", "false", "False")


BINARY_SENSORS = (
    TnaBinaryDescription(
        key="pool_connected",
        name="Pool connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda d: any(p.get("connected") or p.get("status") == "alive" for p in active_pools(d)),
    ),
    TnaBinaryDescription(key="power_valid", name="Power telemetry valid", value_fn=lambda d: bool(d.get("powerValid", False))),
    TnaBinaryDescription(key="shitcoin_detected", name="Shitcoin detected", device_class=BinarySensorDeviceClass.PROBLEM, value_fn=lambda d: bool(d.get("shitcoinDetected", False))),
    TnaBinaryDescription(key="eth_available", name="Ethernet available", device_class=BinarySensorDeviceClass.CONNECTIVITY, value_fn=lambda d: truthy(d, "ethAvailable")),
    TnaBinaryDescription(key="eth_link_up", name="Ethernet link up", device_class=BinarySensorDeviceClass.CONNECTIVITY, value_fn=lambda d: truthy(d, "ethLinkUp")),
    TnaBinaryDescription(key="eth_connected", name="Ethernet connected", device_class=BinarySensorDeviceClass.CONNECTIVITY, value_fn=lambda d: truthy(d, "ethConnected")),
    TnaBinaryDescription(key="wifi_ap_mode", name="WiFi setup AP active", device_class=BinarySensorDeviceClass.CONNECTIVITY, value_fn=lambda d: bool(d.get("apMode", False))),
    TnaBinaryDescription(key="auto_fan_enabled", name="Auto fan enabled", value_fn=lambda d: bool(d.get("autofanspeed"))),
    TnaBinaryDescription(key="auto_power_on", name="Auto power on", value_fn=lambda d: bool(d.get("autoPowerOn", False))),
    TnaBinaryDescription(key="psu_pd_active", name="USB-C PD active", value_fn=lambda d: bool(d.get("psuPdActive", False))),
    TnaBinaryDescription(key="psu_bypass", name="PSU bypass", value_fn=lambda d: bool(d.get("psuBypass", False))),
    TnaBinaryDescription(key="board_enabled", name="Board enabled", value_fn=lambda d: bool(board(d).get("enabled", False))),
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
