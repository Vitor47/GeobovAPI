# CowTrack LoRa firmware

Production sketches for the cattle collar (sender) and farm gateway (receiver).

## Packet format (LoRa air)

Fixed 17-byte packed binary packet:

| Offset | Field | Type | Notes |
|--------|-------|------|-------|
| 0 | `protocolVersion` | `uint8` | Currently `1` |
| 1–2 | `cowId` | `uint16` | Cattle ID (`Cattle.id`) |
| 3–6 | `latitude` | `int32` | Latitude × 1_000_000 |
| 7–10 | `longitude` | `int32` | Longitude × 1_000_000 |
| 11–14 | `sequence` | `uint32` | Transmission sequence |
| 15 | `satellites` | `uint8` | GPS satellite count |
| 16 | `hdopX10` | `uint8` | HDOP × 10 |

JSON is only used on Wi-Fi toward the API. The gateway adds SX127x `rssi`
and `snr` before posting.

## Collar identity

The collar stores `cow_id` in NVS (uint16). That value is sent in every LoRa
packet and must match the cattle ID in CowTrack (`Cattle.id`).

Each ESP32 also has a factory MAC used as hardware serial
`LORA-<12 hex digits from ESP.getEfuseMac()>`. Register that string as
`Device.serial_number` if you want last-seen tracking on the collar device.

Optional override: hold **BOOT** at power-on → captive portal `Collar-…` → set
cow ID / sleep interval / GPS fix timeout / GPS power GPIO / LoRa MHz (NVS).

## Collar power (deep sleep)

Each wake cycle:

```text
power GPS ON → wait fix (timeout) → LoRa TX → GPS OFF → ESP32 deep sleep
```

| Portal field | Meaning | Default |
|--------------|---------|---------|
| Deep sleep interval ms | Time asleep between TX | `30000` |
| GPS fix timeout ms | Max wait for satellites | `45000` |
| GPS power GPIO | EN / MOSFET gate (`-1` = always on) | `-1` |
| GPS power active high | `1` = HIGH powers GPS | `1` |

Wire GPS `EN` (or a P-MOSFET on VCC) to the configured GPIO for real savings.
Without that pin, Deep Sleep still cuts ESP32 draw; GPS may keep consuming.

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

{
  "protocol_version": 1,
  "cow_id": 1,
  "lat": -29.673200,
  "lon": -53.811300,
  "sequence": 27,
  "satellites": 9,
  "hdop": 1.2,
  "rssi": -83,
  "snr": 6.75
}
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

1. Create Company + Cattle in the API/admin. Note the cattle ID (`cow_id`).
2. Flash collar → set `cow_id` in the portal to that cattle ID.
3. Optionally `POST /api/v1/devices/` with the MAC-based `serial_number`
   linked to the same cattle (enables collar last-seen).
4. Create Gateway → copy `api_key` into gateway portal.
5. Set gateway URL to `/api/v1/gateways/ingest` (not `/devices/ingest`).
6. Same LoRa frequency and sync word on both boards.
