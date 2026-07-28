/*
 * CowTrack LoRa Collar (Sender)
 *
 * Packet over LoRa (not JSON):
 *   <device_serial>|<lat>|<lon>|<seq>
 *
 * Device identity defaults to the ESP32 factory MAC (unique per chip).
 * Optional override and radio settings via captive portal when BOOT is held
 * at power-on (or on first boot with empty NVS).
 *
 * Libraries: TinyGPSPlus, LoRa, WiFiManager, Preferences
 * Board: ESP32 + SX127x + GPS UART
 */

#include <Arduino.h>
#include <Preferences.h>
#include <SPI.h>
#include <LoRa.h>
#include <TinyGPS++.h>
#include <WiFi.h>
#include <WiFiManager.h>

// ---------------------------------------------------------------------------
// PCB wiring (hardware — not farm secrets)
// ---------------------------------------------------------------------------

static const int GPS_RX_PIN = 13;
static const int GPS_TX_PIN = 12;
static const uint32_t GPS_BAUD = 9600;

static const int LORA_SCK = 5;
static const int LORA_MISO = 19;
static const int LORA_MOSI = 27;
static const int LORA_SS = 18;
static const int LORA_RST = 14;
static const int LORA_DIO0 = 26;

// Hold BOOT (GPIO0) low during reset to open config portal.
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
static TinyGPSPlus gps;
static HardwareSerial SerialGPS(2);

static String g_deviceSerial;
static uint32_t g_sendIntervalMs = 30000;
static long g_loraFrequencyHz = 915E6;
static uint32_t g_sequence = 0;
static uint32_t g_lastSendMs = 0;

static String buildHardwareSerial() {
  // Factory eFuse MAC — stable unique ID burned into the chip.
  const uint64_t mac = ESP.getEfuseMac();
  char buf[24];
  snprintf(
      buf,
      sizeof(buf),
      "LORA-%02X%02X%02X%02X%02X%02X",
      (uint8_t)(mac >> 0),
      (uint8_t)(mac >> 8),
      (uint8_t)(mac >> 16),
      (uint8_t)(mac >> 24),
      (uint8_t)(mac >> 32),
      (uint8_t)(mac >> 40));
  return String(buf);
}

static void loadSettings() {
  prefs.begin("collar", true);
  g_deviceSerial = prefs.getString("serial", "");
  g_sendIntervalMs = prefs.getUInt("interval_ms", 30000);
  const uint32_t mhz = prefs.getUInt("lora_mhz", 915);
  prefs.end();

  if (g_deviceSerial.isEmpty()) {
    g_deviceSerial = buildHardwareSerial();
  }
  if (g_sendIntervalMs < 5000) {
    g_sendIntervalMs = 5000;
  }
  g_loraFrequencyHz = static_cast<long>(mhz) * 1000000L;
}

static bool shouldOpenConfigPortal() {
  pinMode(CONFIG_BUTTON_PIN, INPUT_PULLUP);
  delay(50);
  if (digitalRead(CONFIG_BUTTON_PIN) == LOW) {
    return true;
  }

  prefs.begin("collar", true);
  const bool configured = prefs.getBool("configured", false);
  prefs.end();
  return !configured;
}

static void runConfigPortal() {
  WiFi.mode(WIFI_STA);

  const String hwSerial = buildHardwareSerial();
  char serialBuf[40];
  char intervalBuf[16];
  char mhzBuf[8];

  prefs.begin("collar", true);
  String savedSerial = prefs.getString("serial", "");
  const uint32_t savedInterval = prefs.getUInt("interval_ms", 30000);
  const uint32_t savedMhz = prefs.getUInt("lora_mhz", 915);
  prefs.end();

  if (savedSerial.isEmpty()) {
    savedSerial = hwSerial;
  }

  savedSerial.toCharArray(serialBuf, sizeof(serialBuf));
  snprintf(intervalBuf, sizeof(intervalBuf), "%u", savedInterval);
  snprintf(mhzBuf, sizeof(mhzBuf), "%u", savedMhz);

  WiFiManager wm;
  wm.setConfigPortalTimeout(180);

  WiFiManagerParameter p_serial(
      "serial",
      "Device serial (blank = chip MAC)",
      serialBuf,
      39);
  WiFiManagerParameter p_interval(
      "interval_ms",
      "Send interval ms (>=5000)",
      intervalBuf,
      15);
  WiFiManagerParameter p_mhz("lora_mhz", "LoRa MHz (915/868)", mhzBuf, 7);

  wm.addParameter(&p_serial);
  wm.addParameter(&p_interval);
  wm.addParameter(&p_mhz);

  // SoftAP name includes chip id so farm tech can tell collars apart.
  const String apName = String("Collar-") + hwSerial.substring(5);
  wm.startConfigPortal(apName.c_str());

  String newSerial = String(p_serial.getValue());
  newSerial.trim();
  uint32_t newInterval = static_cast<uint32_t>(atoi(p_interval.getValue()));
  uint32_t newMhz = static_cast<uint32_t>(atoi(p_mhz.getValue()));

  if (newSerial.isEmpty() || newSerial == hwSerial) {
    newSerial = "";  // store empty → runtime uses hardware serial
  }
  if (newInterval < 5000) {
    newInterval = 5000;
  }
  if (newMhz != 868 && newMhz != 915) {
    newMhz = 915;
  }

  prefs.begin("collar", false);
  prefs.putString("serial", newSerial);
  prefs.putUInt("interval_ms", newInterval);
  prefs.putUInt("lora_mhz", newMhz);
  prefs.putBool("configured", true);
  prefs.end();

  WiFi.mode(WIFI_OFF);
  delay(200);
  ESP.restart();
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

static void sendLocation() {
  if (!gps.location.isValid()) {
    return;
  }

  ++g_sequence;

  char packet[96];
  snprintf(
      packet,
      sizeof(packet),
      "%s|%.6f|%.6f|%lu",
      g_deviceSerial.c_str(),
      gps.location.lat(),
      gps.location.lng(),
      static_cast<unsigned long>(g_sequence));

  LoRa.beginPacket();
  LoRa.print(packet);
  LoRa.endPacket();

  LOGF("tx %s\n", packet);
}

void setup() {
#if LOG_ENABLED
  Serial.begin(115200);
  delay(200);
#endif

  if (shouldOpenConfigPortal()) {
    runConfigPortal();
  }

  loadSettings();
  LOGF("serial=%s interval=%u freq=%ld\n",
       g_deviceSerial.c_str(),
       g_sendIntervalMs,
       g_loraFrequencyHz);

  SerialGPS.begin(GPS_BAUD, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);

  if (!initLoRa()) {
    while (true) {
      delay(1000);
    }
  }
}

void loop() {
  while (SerialGPS.available() > 0) {
    gps.encode(static_cast<char>(SerialGPS.read()));
  }

  if (!gps.location.isValid()) {
    return;
  }

  const uint32_t now = millis();
  if (now - g_lastSendMs >= g_sendIntervalMs) {
    g_lastSendMs = now;
    sendLocation();
  }
}
