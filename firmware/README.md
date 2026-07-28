# CowTrack LoRa firmware

Production sketches for the cattle collar (sender) and farm gateway (receiver).

## Packet format (LoRa air)

```text
LORA-A1B2C3D4E5F6|-29.673218|-53.811286|42
```

Fields: `device_serial|lat|lon|seq` (`seq` optional).

JSON is only used on Wi-Fi toward the API.

## Collar identity (no hardcoded serial)

Each ESP32 has a factory MAC in eFuse. The collar builds:

```text
LORA-<12 hex digits from ESP.getEfuseMac()>
```

That value is stable for the life of the chip. Register the **same** string as
`Device.serial_number` in CowTrack (admin / API).

Optional override: hold **BOOT** at power-on → captive portal `Collar-…` → set
serial / interval / LoRa MHz (stored in NVS).

## Gateway config

Hold **BOOT** at reset (or first boot) → portal `Gateway-Config`:

| Field | Example |
|-------|---------|
| API ingest URL | `http://<host>:8000/api/v1/gateways/ingest` |
| X-Gateway-Api-Key | key returned when creating the Gateway |
| LoRa MHz | `915` or `868` (must match collar) |

## API call

```http
POST /api/v1/gateways/ingest
X-Gateway-Api-Key: <gateway key>
Content-Type: application/json

{"device_serial":"LORA-A1B2C3D4E5F6","lat":-29.673218,"lon":-53.811286}
```

## Libraries (Arduino IDE / PlatformIO)

- LoRa (Sandeep Mistry)
- TinyGPSPlus (collar only)
- WiFiManager (tzapu)
- Preferences, HTTPClient, WiFi (ESP32 core)

## Debug logs

By default logs are off. To enable Serial logging, compile with:

```cpp
-DLOG_ENABLED=1
```

or change `#define LOG_ENABLED 0` to `1` at the top of the sketch.

## Provisioning checklist

1. Create Company + Cattle in the API/admin.
2. Flash collar → open portal once (or read MAC-based serial with `LOG_ENABLED=1`).
3. `POST /api/v1/devices/` with that `serial_number` linked to the cattle.
4. Create Gateway → copy `api_key` into gateway portal.
5. Set gateway URL to `/api/v1/gateways/ingest` (not `/devices/ingest`).
6. Same LoRa frequency and sync word on both boards.
