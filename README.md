# Home Assistant TNA-OS Canaan

Independent, unofficial Home Assistant integration for Canaan miners running [TNA-OS-CANAAN](https://github.com/CryptoIceMLH/TNA-OS-CANAAN), including **Avalon Nano 3s** and Avalon Q.

> Status: alpha. Tested live against a LAN **Avalon Nano 3s** running TNA-OS `0.2.7`; updated against the public TNA-OS-CANAAN `0.3.5` API documentation.
>
> This project is not affiliated with, endorsed by, or maintained by the TNA-OS-CANAAN project unless stated otherwise.

## Features

- Local polling via the unauthenticated HTTP API (`http://<miner-ip>/api/system/info`)
- Sensors for hashrate, efficiency, power, temperatures, shares, fan RPM/duty, voltage/current, network mode, pool status and TNA-OS `0.3.5` telemetry
- Binary sensors for pool connectivity, power telemetry validity, network/PSU/board state and shitcoin detection
- Config entities for frequency, core voltage, fan speed, hashboard power and auto-fan
- Config buttons for reboot and board reset
- UI config flow: add the miner by LAN IP/hostname

## Live-tested entities

Example entity set from an Avalon Nano 3s named `nano3s`:

| Entity | Purpose |
|---|---|
| `sensor.nano3s_hashrate` | Current hashrate in TH/s |
| `sensor.nano3s_hashrate_1m` | 1-minute hashrate in TH/s |
| `sensor.nano3s_hashrate_10m` | 10-minute hashrate in TH/s |
| `sensor.nano3s_hashrate_1h` | 1-hour hashrate in TH/s |
| `sensor.nano3s_hashrate_1d` | 1-day hashrate in TH/s |
| `sensor.nano3s_power` | Miner power in W |
| `sensor.nano3s_hash_efficiency` | API-reported efficiency in GH/W |
| `sensor.nano3s_efficiency` | Mining efficiency in J/TH |
| `sensor.nano3s_temperature` | Reported temperature in °C |
| `sensor.nano3s_chip_max_temperature` | Maximum chip temperature in °C |
| `sensor.nano3s_fan_rpm` | Live fan tachometer RPM |
| `sensor.nano3s_fan_duty` | Fan duty in % |
| `sensor.nano3s_frequency` | ASIC frequency in MHz |
| `sensor.nano3s_core_voltage` | Core voltage in mV |
| `sensor.nano3s_input_voltage` | Input voltage in mV |
| `sensor.nano3s_input_current` | Input current in A |
| `sensor.nano3s_shares_accepted` | Accepted shares |
| `sensor.nano3s_shares_rejected` | Rejected shares |
| `sensor.nano3s_shares_submitted` | Submitted shares |
| `sensor.nano3s_best_session_difficulty` | Best session difficulty |
| `sensor.nano3s_pool_difficulty` | Current/active pool difficulty |
| `sensor.nano3s_network_mode` | Active network mode |
| `sensor.nano3s_wifi_rssi` | WiFi signal strength in dBm |
| `sensor.nano3s_pool_mode` | Failover or multipool mode |
| `sensor.nano3s_active_pool_status` | Active pool status |
| `sensor.nano3s_active_pool_protocol` | Active pool protocol, e.g. v1/v2 |
| `sensor.nano3s_active_pool_effective_quota` | Active pool effective quota |
| `sensor.nano3s_max_power` | API-reported maximum board power in W |
| `sensor.nano3s_core_voltage_actual` | Live Vcore readback in mV |
| `sensor.nano3s_vr_temperature` | VR / board temperature alias in °C |
| `sensor.nano3s_board_probe_temperature` | Raw board probe temperature in °C |
| `sensor.nano3s_overheat_threshold` | Active overheat threshold in °C |
| `sensor.nano3s_chip_average_temperature` | Average chip temperature in °C |
| `sensor.nano3s_fan_rpms` | Avalon Q multi-fan RPM list |
| `sensor.nano3s_psu_negotiated_voltage` | Nano 3s USB-C PD negotiated voltage in V |
| `sensor.nano3s_psu_string_voltage_setpoint` | Avalon Q PSU string voltage setpoint in V |
| `sensor.nano3s_psu_string_voltage_actual` | Avalon Q PSU string voltage readback in V |
| `sensor.nano3s_psu_output_current` | Avalon Q PSU output current in A |
| `sensor.nano3s_psu_output_power` | Avalon Q PSU output power in W |
| `sensor.nano3s_wifi_signal` | WiFi signal strength in % |
| `sensor.nano3s_wifi_link_quality` | WiFi link quality in % |
| `sensor.nano3s_ethernet_rx` | Ethernet RX throughput in kbps |
| `sensor.nano3s_ethernet_tx` | Ethernet TX throughput in kbps |
| `sensor.nano3s_miner_uptime` | Miner daemon uptime in seconds |
| `sensor.nano3s_system_uptime` | Linux system uptime in seconds |
| `sensor.nano3s_board_state` | Board state from `boards[0].state` |
| `sensor.nano3s_runtime_state` | Board runtime state |
| `sensor.nano3s_thermal_zone` | Board thermal zone |
| `sensor.nano3s_fault_reason` | Board/API fault reason |
| `sensor.nano3s_responding_chips` | Responding ASIC chip count |
| `binary_sensor.nano3s_pool_connected` | Pool connectivity |
| `binary_sensor.nano3s_ethernet_available` | Ethernet interface present |
| `binary_sensor.nano3s_ethernet_link_up` | Ethernet PHY link up |
| `binary_sensor.nano3s_ethernet_connected` | Ethernet connectivity |
| `binary_sensor.nano3s_wifi_setup_ap_active` | TNA setup AP active |
| `binary_sensor.nano3s_usb_c_pd_active` | USB-C PD contract active |
| `binary_sensor.nano3s_psu_bypass` | PSU bypass mode enabled |
| `binary_sensor.nano3s_board_enabled` | Hashboard enabled |
| `switch.nano3s_hashboard_power` | Hashboard on/off |
| `switch.nano3s_auto_fan` | Auto fan on/off |
| `number.nano3s_fan_speed` | Manual fan duty |
| `number.nano3s_frequency` | Frequency setting |
| `number.nano3s_core_voltage` | Core voltage setting |
| `button.nano3s_reboot` | Reboot miner control board |
| `button.nano3s_board_reset` | Reset board 0 |

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
- Advanced TNA-OS `0.3.5` controls such as pool editing, presets, thermal PID/thresholds, LED/OLED, BDOC, immersion settings, PSU bypass and WiFi credential writes are intentionally not exposed yet because they are persistent and safety-sensitive.
- The HTTP API has no authentication. Network isolation is expected.

## Support this project

If this integration is useful for your miner dashboard or automation setup, BTC support is appreciated and helps keep the project maintained.

```text
bc1qqe5l9e36h49wm9kkjrek7v746gej3s3j2hrkgd
```

## Credits

This integration is built for miners running [TNA-OS-CANAAN](https://github.com/CryptoIceMLH/TNA-OS-CANAAN).
TNA-OS-CANAAN is developed by CryptoIceMLH and contributors.

This repository provides an independent Home Assistant integration for that API. It is not an official TNA-OS-CANAAN component and is not affiliated with, endorsed by, or maintained by the TNA-OS-CANAAN project unless explicitly stated by that project.

## Notes

- Hashrate is reported by TNA-OS in GH/s and displayed in TH/s.
- `PATCH /api/system` writes are persistent on the miner; verify changes after writing.
- Polling interval is currently 5 seconds.
