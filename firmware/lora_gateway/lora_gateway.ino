/*
 * CowTrack LoRa Gateway (Receiver)
 *
 * Receives compact LoRa packets:
 *   <device_serial>|<lat>|<lon>[|<seq>]
 *
 * Forwards to CowTrack API:
 *   POST /api/v1/gateways/ingest
 *   Header: X-Gateway-Api-Key
 *   Body:   {"device_serial":"...","lat":...,"lon":...}
 *
 * Wi-Fi + API URL + gateway API key + LoRa MHz via WiFiManager portal.
 * Opens portal when BOOT is held at reset, or on first boot / failed Wi-Fi.
 *
 * Libraries: LoRa, WiFiManager, Preferences, HTTPClient
 * Board: ESP32 + SX127x
 */

#include <Arduino.h>
#include <Preferences.h>
#include <SPI.h>
#include <LoRa.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiManager.h>

// ---------------------------------------------------------------------------
// PCB wiring (hardware — not farm secrets)
// ---------------------------------------------------------------------------

static const int LORA_SCK = 5;
static const int LORA_MISO = 19;
static const int LORA_MOSI = 27;
static const int LORA_SS = 18;
static const int LORA_RST = 14;
static const int LORA_DIO0 = 26;

static const int CONFIG_BUTTON_PIN = 0;

#ifndef LOG_ENABLED
#define LOG_ENABLED 0
#endif

#if LOG_ENABLED
#define LOGF(...)                \
  do {                           \
    Serial.printf(__VA_ARGS__);  \
  } while (0)
#else
#define LOGF(...) \
  do {            \
  } while (0)
#endif

static Preferences prefs;

static String g_apiUrl;
static String g_gatewayApiKey;
static long g_loraFrequencyHz = 915E6;

struct TelemetryPacket {
  String deviceSerial;
  double lat;
  double lon;
  bool valid;
};

static void loadSettings() {
  prefs.begin("gateway", true);
  g_apiUrl = prefs.getString("api_url", "");
  g_gatewayApiKey = prefs.getString("api_key", "");
  const uint32_t mhz = prefs.getUInt("lora_mhz", 915);
  prefs.end();
  g_loraFrequencyHz = static_cast<long>(mhz) * 1000000L;
}

static bool settingsReady() {
  return g_apiUrl.length() > 0 && g_gatewayApiKey.length() > 0;
}

static bool shouldForcePortal() {
  pinMode(CONFIG_BUTTON_PIN, INPUT_PULLUP);
  delay(50);
  return digitalRead(CONFIG_BUTTON_PIN) == LOW;
}

static void saveSettings(
    const String& apiUrl,
    const String& apiKey,
    uint32_t loraMhz) {
  prefs.begin("gateway", false);
  prefs.putString("api_url", apiUrl);
  prefs.putString("api_key", apiKey);
  prefs.putUInt("lora_mhz", loraMhz);
  prefs.putBool("configured", true);
  prefs.end();
}

static bool runConfigPortal(bool force) {
  char apiUrlBuf[160];
  char apiKeyBuf[96];
  char mhzBuf[8];

  prefs.begin("gateway", true);
  String savedUrl = prefs.getString(
      "api_url",
      "http://192.168.0.44:8000/api/v1/gateways/ingest");
  String savedKey = prefs.getString("api_key", "");
  const uint32_t savedMhz = prefs.getUInt("lora_mhz", 915);
  prefs.end();

  savedUrl.toCharArray(apiUrlBuf, sizeof(apiUrlBuf));
  savedKey.toCharArray(apiKeyBuf, sizeof(apiKeyBuf));
  snprintf(mhzBuf, sizeof(mhzBuf), "%u", savedMhz);

  WiFiManager wm;
  wm.setConfigPortalTimeout(force ? 0 : 180);

  WiFiManagerParameter p_url(
      "api_url",
      "API ingest URL",
      apiUrlBuf,
      159);
  WiFiManagerParameter p_key(
      "api_key",
      "X-Gateway-Api-Key",
      apiKeyBuf,
      95);
  WiFiManagerParameter p_mhz("lora_mhz", "LoRa MHz (915/868)", mhzBuf, 7);

  wm.addParameter(&p_url);
  wm.addParameter(&p_key);
  wm.addParameter(&p_mhz);

  bool connected = false;
  if (force || !settingsReady()) {
    connected = wm.startConfigPortal("Gateway-Config");
  } else {
    connected = wm.autoConnect("Gateway-Config");
  }

  if (!connected) {
    return false;
  }

  String newUrl = String(p_url.getValue());
  String newKey = String(p_key.getValue());
  uint32_t newMhz = static_cast<uint32_t>(atoi(p_mhz.getValue()));

  newUrl.trim();
  newKey.trim();
  if (newMhz != 868 && newMhz != 915) {
    newMhz = 915;
  }

  // WiFiManager may not re-apply custom params on autoConnect success path;
  // only overwrite NVS when portal values are non-empty.
  if (newUrl.length() > 0 && newKey.length() > 0) {
    saveSettings(newUrl, newKey, newMhz);
  }

  loadSettings();
  return settingsReady() && WiFi.status() == WL_CONNECTED;
}

static bool initLoRa() {
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(g_loraFrequencyHz)) {
    return false;
  }
  LoRa.setSyncWord(0x12);
  LoRa.enableCrc();
  return true;
}

static TelemetryPacket parseLoRaPayload(const String& raw) {
  TelemetryPacket out;
  out.valid = false;

  // Expected: serial|lat|lon  or  serial|lat|lon|seq
  const int p1 = raw.indexOf('|');
  if (p1 <= 0) {
    return out;
  }
  const int p2 = raw.indexOf('|', p1 + 1);
  if (p2 <= p1 + 1) {
    return out;
  }

  out.deviceSerial = raw.substring(0, p1);
  out.deviceSerial.trim();

  const String latStr = raw.substring(p1 + 1, p2);
  String lonStr;
  const int p3 = raw.indexOf('|', p2 + 1);
  if (p3 > p2) {
    lonStr = raw.substring(p2 + 1, p3);
  } else {
    lonStr = raw.substring(p2 + 1);
  }
  latStr.trim();
  lonStr.trim();

  out.lat = atof(latStr.c_str());
  out.lon = atof(lonStr.c_str());

  if (out.deviceSerial.isEmpty()) {
    return out;
  }
  if (out.lat < -90.0 || out.lat > 90.0 || out.lon < -180.0 || out.lon > 180.0) {
    return out;
  }
  if (out.lat == 0.0 && out.lon == 0.0) {
    return out;
  }

  out.valid = true;
  return out;
}

static String escapeJsonString(const String& value) {
  String out;
  out.reserve(value.length() + 8);
  for (size_t i = 0; i < value.length(); ++i) {
    const char c = value[i];
    if (c == '\\' || c == '"') {
      out += '\\';
      out += c;
    } else if (static_cast<uint8_t>(c) < 0x20) {
      // skip control chars
    } else {
      out += c;
    }
  }
  return out;
}

static bool postTelemetry(const TelemetryPacket& packet) {
  if (WiFi.status() != WL_CONNECTED) {
    return false;
  }

  const String serialJson = escapeJsonString(packet.deviceSerial);
  char body[192];
  snprintf(
      body,
      sizeof(body),
      "{\"device_serial\":\"%s\",\"lat\":%.6f,\"lon\":%.6f}",
      serialJson.c_str(),
      packet.lat,
      packet.lon);

  HTTPClient http;
  http.setTimeout(8000);
  http.begin(g_apiUrl);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Gateway-Api-Key", g_gatewayApiKey);

  const int code = http.POST(String(body));
  http.end();

  LOGF("http %d body=%s\n", code, body);
  return code >= 200 && code < 300;
}

void setup() {
#if LOG_ENABLED
  Serial.begin(115200);
  delay(200);
#endif

  loadSettings();

  const bool forcePortal = shouldForcePortal() || !settingsReady();
  if (!runConfigPortal(forcePortal)) {
    delay(3000);
    ESP.restart();
  }

  if (!initLoRa()) {
    while (true) {
      delay(1000);
    }
  }

  LOGF("gateway ready url=%s freq=%ld\n", g_apiUrl.c_str(), g_loraFrequencyHz);
}

void loop() {
  const int packetSize = LoRa.parsePacket();
  if (packetSize <= 0) {
    delay(5);
    return;
  }

  String payload;
  payload.reserve(static_cast<unsigned int>(packetSize) + 1);
  while (LoRa.available()) {
    payload += static_cast<char>(LoRa.read());
  }
  payload.trim();

  LOGF("rx %s\n", payload.c_str());

  const TelemetryPacket packet = parseLoRaPayload(payload);
  if (!packet.valid) {
    return;
  }

  postTelemetry(packet);
}
