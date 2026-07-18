# Home Assistant TNA-OS Canaan

Independent, unofficial Home Assistant integration for Canaan miners running [TNA-OS-CANAAN](https://github.com/CryptoIceMLH/TNA-OS-CANAAN), including **Avalon Nano 3s** and **Avalon Q**.

> Status: alpha. Tracks the public TNA-OS-CANAAN HTTP API documentation for firmware `0.3.5`.
>
> This project is not affiliated with, endorsed by, or maintained by the TNA-OS-CANAAN project unless stated otherwise.

## Features

- Local polling via the unauthenticated HTTP API (`http://<miner-ip>/api/system/info`)
- Sensors for hashrate, efficiency, power, temperatures, fan RPM/duty, voltage/current and share statistics
- New TNA-OS `0.3.5` telemetry for Avalon Q PSU/string-rail values, fan arrays, chip/board state, Ethernet/WiFi quality and uptime
- Binary sensors for pool connectivity, power telemetry validity, network link state, PSU mode, board enablement and shitcoin detection
- Config entities for frequency, core voltage, fan speed, hashboard power and auto-fan
- Config buttons for reboot and board reset
- UI config flow: add the miner by LAN IP/hostname

## Entity coverage

Example entity set from a miner named `nano3s` or `avalon_q`:

| Entity suffix | Purpose |
|---|---|
| `hashrate`, `hashrate_1m`, `hashrate_10m`, `hashrate_1h`, `hashrate_1d` | Hashrate in TH/s |
| `power`, `max_power`, `hash_efficiency`, `efficiency` | Power and efficiency telemetry |
| `shares_accepted`, `shares_rejected`, `shares_submitted` | Share counters |
| `best_difficulty`, `best_session_difficulty`, `pool_difficulty` | Difficulty telemetry |
| `temperature`, `vr_temperature`, `board_probe_temperature`, `overheat_threshold` | Board/VR thermal telemetry |
| `chip_max_temperature`, `chip_average_temperature`, `responding_chips`, `chip_share_attribution` | Per-board/per-chip summary |
| `fan_rpm`, `fan_rpms`, `fan_duty` | Single-fan and Avalon Q multi-fan telemetry |
| `frequency`, `target_frequency` | Current/target ASIC frequency |
| `core_voltage_setpoint`, `core_voltage_actual` | ASIC Vcore setpoint and live readback |
| `input_voltage`, `input_current`, `psu_negotiated_voltage` | Nano 3s USB-C PD telemetry |
| `psu_string_voltage_setpoint`, `psu_string_voltage_actual`, `psu_output_current`, `psu_output_power` | Avalon Q PSU/string-rail telemetry |
| `network_mode`, `wifi_signal`, `wifi_link_quality`, `wifi_rssi`, `wifi_status`, `wifi_ssid` | Network telemetry |
| `ethernet_rx`, `ethernet_tx`, `ethernet_rx_total`, `ethernet_tx_total`, `ethernet_ipv4` | Ethernet counters |
| `pool_mode`, `active_pool_status`, `active_pool_protocol`, `active_pool_effective_quota` | Pool status |
| `board_state`, `runtime_state`, `thermal_zone`, `fault_reason` | Board health state |
| `miner_uptime`, `system_uptime`, `asic_count`, `core_count` | Identity/runtime counters |
| `binary_sensor.*_pool_connected` | Pool connectivity |
| `binary_sensor.*_power_telemetry_valid` | Power readings are valid |
| `binary_sensor.*_shitcoin_detected` | Non-Bitcoin SHA-256 pool work detected by firmware |
| `binary_sensor.*_ethernet_*`, `binary_sensor.*_wifi_setup_ap_active` | Network state |
| `binary_sensor.*_usb_c_pd_active`, `binary_sensor.*_psu_bypass` | PSU mode state |
| `switch.*_hashboard_power` | Hashboard on/off |
| `switch.*_auto_fan` | Auto fan on/off |
| `number.*_fan_speed`, `number.*_frequency`, `number.*_core_voltage` | Persistent miner configuration values |
| `button.*_reboot`, `button.*_board_reset` | Restart/reset controls |

Fields that do not apply to the connected board appear as unavailable/empty. For example, Avalon Q exposes string-rail PSU values and `fanRpms`; Nano 3s exposes USB-C PD/input values.

## Security warning

TNA-OS-CANAAN exposes an **unauthenticated HTTP API**. Anyone who can reach the miner on the LAN can read telemetry and change settings.

Do **not** expose the miner or this integration through the public internet without a VPN/reverse-proxy/auth layer. Treat these controls as privileged LAN administration:

- `switch.*_hashboard_power` stops/starts mining.
- `button.*_reboot` reboots the device.
- `button.*_board_reset` resets the hashboard.
- Frequency, voltage and fan settings are persistent miner configuration writes.

## HACS installation

Until this is added to HACS default repositories:

1. HACS → Integrations → three-dot menu → Custom repositories
2. Add this repository URL
3. Category: Integration
4. Install **TNA-OS Canaan**
5. Restart Home Assistant
6. Settings → Devices & services → Add integration → **TNA-OS Canaan**

## Manual installation

Copy `custom_components/tna_os_canaan` to your Home Assistant `custom_components` directory and restart Home Assistant.

## Configuration

Add through the UI. Use only the host/IP, for example:

```text
<miner-ip-or-hostname>
```

## Known limitations

- Pool editing is not exposed yet. TNA-OS requires sending the full pool list, so accidental UI edits could lock a miner out of its pool.
- Advanced controls such as presets, thermal PID/threshold tuning, LED/OLED, BDOC, immersion settings, PSU bypass and WiFi credential writes are intentionally not exposed because they are persistent and safety-sensitive.
- The HTTP API has no authentication. Network isolation is expected.

## Credits

This integration is built for miners running [TNA-OS-CANAAN](https://github.com/CryptoIceMLH/TNA-OS-CANAAN).
TNA-OS-CANAAN is developed by CryptoIceMLH and contributors.

This repository provides an independent Home Assistant integration for that API. It is not an official TNA-OS-CANAAN component and is not affiliated with, endorsed by, or maintained by the TNA-OS-CANAAN project unless explicitly stated by that project.

## Notes

- Hashrate is reported by TNA-OS in GH/s and displayed in TH/s.
- `PATCH /api/system` writes are persistent on the miner; verify changes after writing.
- Polling interval is currently 5 seconds.
