# Home Assistant TNA-OS Canaan

Independent, unofficial Home Assistant integration for Canaan miners running [TNA-OS-CANAAN](https://github.com/CryptoIceMLH/TNA-OS-CANAAN), including **Avalon Nano 3s** and Avalon Q.

> Status: early alpha. Tested live against a LAN **Avalon Nano 3s** running TNA-OS `0.2.6`.
>
> This project is not affiliated with, endorsed by, or maintained by the TNA-OS-CANAAN project unless stated otherwise.

## Features

- Local polling via the unauthenticated HTTP API (`http://<miner-ip>/api/system/info`)
- Sensors for hashrate, power, temperatures, shares, fan duty, voltage/current and difficulty
- Binary sensors for pool connectivity, power telemetry validity and shitcoin detection
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
| `sensor.nano3s_power` | Miner power in W |
| `sensor.nano3s_temperature` | Reported temperature in °C |
| `sensor.nano3s_chip_max_temperature` | Maximum chip temperature in °C |
| `sensor.nano3s_fan_duty` | Fan duty in % |
| `sensor.nano3s_frequency` | ASIC frequency in MHz |
| `sensor.nano3s_core_voltage` | Core voltage in mV |
| `sensor.nano3s_input_voltage` | Input voltage in mV |
| `sensor.nano3s_input_current` | Input current in A |
| `sensor.nano3s_shares_accepted` | Accepted shares |
| `sensor.nano3s_shares_rejected` | Rejected shares |
| `binary_sensor.nano3s_pool_connected` | Pool connectivity |
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

- `sensor.*_fan_rpm` may show `0` on some TNA-OS/Canaan builds even while fan duty is valid. This appears to be firmware/API-side behaviour and is intentionally not corrected in the integration.
- Pool editing is not exposed yet. TNA-OS requires sending the full pool list, so accidental UI edits could lock a miner out of its pool.
- The HTTP API has no authentication. Network isolation is expected.

## Credits

This integration is built for miners running [TNA-OS-CANAAN](https://github.com/CryptoIceMLH/TNA-OS-CANAAN).
TNA-OS-CANAAN is developed by CryptoIceMLH and contributors.

This repository provides an independent Home Assistant integration for that API. It is not an official TNA-OS-CANAAN component and is not affiliated with, endorsed by, or maintained by the TNA-OS-CANAAN project unless explicitly stated by that project.

## Notes

- Hashrate is reported by TNA-OS in GH/s and displayed in TH/s.
- `PATCH /api/system` writes are persistent on the miner; verify changes after writing.
- Polling interval is currently 5 seconds.
