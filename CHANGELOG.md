# Changelog

## 0.3.3 - 2026-07-19

- Restore `coreVoltage`, `coreVoltageActual` and input `voltage` to the API-defined mV units.
- Add Avalon Q `number.*_psu_string_voltage` for the `psuVoutV` string-rail setpoint in V, written via `stringVoltage`.
- Keep Avalon Q measured `psuVoutActualV` as a sensor-only readback.

## 0.3.2 - 2026-07-19

- Fix core-voltage units for Avalon Q in Home Assistant controls.
- Display core-voltage telemetry in volts and normalize Nano-style mV values for HA.
- Keep Nano writes compatible by converting V back to mV, while Avalon Q volt-range writes stay in V.

## 0.3.1 - 2026-07-18

- Restore the previous README/info style and BTC support section.
- Keep the TNA-OS `0.3.5` entity additions documented in the existing entity-table schema.

## 0.3.0 - 2026-07-18

- Update integration against the TNA-OS-CANAAN `0.3.5` API documentation.
- Add Avalon Q PSU/string-rail telemetry sensors (`psuVoutV`, `psuVoutActualV`, `psuIoutA`, `psuPoutW`) while keeping Nano 3s USB-C PD values.
- Add live Vcore readback (`coreVoltageActual`), max power, negotiated PSU voltage and bypass voltage telemetry.
- Add expanded thermal sensors for VR/board probe/overheat threshold, chip average temperature and board/chip health summary.
- Add Avalon Q multi-fan RPM string sensor and keep `fanRpm` as the headline live tachometer.
- Add Ethernet throughput/counter sensors, WiFi signal/link-quality sensors, setup-AP fields, uptime and identity counters.
- Add binary sensors for Ethernet link/connectivity, setup AP, auto power-on, USB-C PD active, PSU bypass and board enabled state.
- Document TNA-OS `0.3.5` limitations and keep pools, presets, thermal thresholds, WiFi credential writes, BDOC, immersion and PSU-bypass controls intentionally unexposed.

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
