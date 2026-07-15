# Changelog

## 0.2.0 - 2026-07-15

- Update integration against the TNA-OS-CANAAN `0.2.7` API documentation.
- Add sensors for 1-hour and 1-day hashrate, GH/W efficiency and calculated J/TH efficiency.
- Add submitted shares, best session difficulty and active pool difficulty sensors.
- Add network mode, WiFi RSSI, pool mode and active pool status/protocol/quota sensors.
- Treat `fanRpm` as a supported live tachometer value for current TNA-OS builds.
- Document Avalon Q compatibility and keep advanced persistent controls intentionally out of the first alpha UI surface.

## 0.1.0 - 2026-07-15

- Initial HACS-ready custom integration.
- Add UI config flow.
- Add telemetry sensors for hashrate, power, temperatures, shares, fan duty, voltage/current and difficulty.
- Add binary sensors for pool connectivity, power telemetry validity and shitcoin detection.
- Add config entities for hashboard power, auto fan, fan speed, frequency and core voltage.
- Add config buttons for reboot and board reset.
- Live-tested with Avalon Nano 3s on TNA-OS 0.2.6.
