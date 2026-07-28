/*
 * CowTrack LoRa Collar (Sender) — deep-sleep duty cycle
 *
 * Wake cycle:
 *   power GPS (optional GPIO) → wait for fix → LoRa TX → power GPS off → deep sleep
 *
 * Packet over LoRa (not JSON):
 *   <device_serial>|<lat>|<lon>|<seq>
 *
 * Device identity defaults to the ESP32 factory MAC (unique per chip).
 * Config portal when BOOT is held at wake, or on first boot.
 *
 * Libraries: TinyGPSPlus, LoRa, WiFiManager, Preferences
 * Board: ESP32 + SX127x + GPS UART
 *
 * GPS power (optional):
 *   Wire module EN / MOSFET gate to gps_pwr_gpio (active HIGH by default).
 *   Set gps_pwr_gpio = -1 in portal to leave GPS always powered.
 */

#include <Arduino.h>
#include <Preferences.h>
#include <SPI.h>
#include <LoRa.h>
#include <TinyGPS++.h>
#include <WiFi.h>
#include <WiFiManager.h>
#include <esp_sleep.h>

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

// Hold BOOT (GPIO0) low during wake to open config portal.
static const int CONFIG_BUTTON_PIN = 0;

// Default GPS power pin when NVS has never been configured (-1 = always on).
static const int DEFAULT_GPS_POWER_PIN = -1;

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
static uint32_t g_sleepIntervalMs = 30000;
static uint32_t g_gpsFixTimeoutMs = 45000;
static int g_gpsPowerPin = DEFAULT_GPS_POWER_PIN;
static bool g_gpsPowerActiveHigh = true;
static long g_loraFrequencyHz = 915E6;

static String buildHardwareSerial() {
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

static uint32_t loadAndBumpSequence() {
  prefs.begin("collar", false);
  uint32_t seq = prefs.getUInt("seq", 0);
  ++seq;
  prefs.putUInt("seq", seq);
  prefs.end();
  return seq;
}

static void loadSettings() {
  prefs.begin("collar", true);
  g_deviceSerial = prefs.getString("serial", "");
  g_sleepIntervalMs = prefs.getUInt("interval_ms", 30000);
  g_gpsFixTimeoutMs = prefs.getUInt("fix_timeout", 45000);
  g_gpsPowerPin = prefs.getInt("gps_pwr_pin", DEFAULT_GPS_POWER_PIN);
  g_gpsPowerActiveHigh = prefs.getBool("gps_pwr_high", true);
  const uint32_t mhz = prefs.getUInt("lora_mhz", 915);
  prefs.end();

  if (g_deviceSerial.isEmpty()) {
    g_deviceSerial = buildHardwareSerial();
  }
  if (g_sleepIntervalMs < 5000) {
    g_sleepIntervalMs = 5000;
  }
  if (g_gpsFixTimeoutMs < 5000) {
    g_gpsFixTimeoutMs = 5000;
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
  char fixTimeoutBuf[16];
  char gpsPinBuf[8];
  char gpsActiveBuf[4];
  char mhzBuf[8];

  prefs.begin("collar", true);
  String savedSerial = prefs.getString("serial", "");
  const uint32_t savedInterval = prefs.getUInt("interval_ms", 30000);
  const uint32_t savedFixTimeout = prefs.getUInt("fix_timeout", 45000);
  const int savedGpsPin = prefs.getInt("gps_pwr_pin", DEFAULT_GPS_POWER_PIN);
  const bool savedGpsHigh = prefs.getBool("gps_pwr_high", true);
  const uint32_t savedMhz = prefs.getUInt("lora_mhz", 915);
  prefs.end();

  if (savedSerial.isEmpty()) {
    savedSerial = hwSerial;
  }

  savedSerial.toCharArray(serialBuf, sizeof(serialBuf));
  snprintf(intervalBuf, sizeof(intervalBuf), "%u", savedInterval);
  snprintf(fixTimeoutBuf, sizeof(fixTimeoutBuf), "%u", savedFixTimeout);
  snprintf(gpsPinBuf, sizeof(gpsPinBuf), "%d", savedGpsPin);
  snprintf(gpsActiveBuf, sizeof(gpsActiveBuf), "%d", savedGpsHigh ? 1 : 0);
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
      "Deep sleep interval ms (>=5000)",
      intervalBuf,
      15);
  WiFiManagerParameter p_fix_timeout(
      "fix_timeout",
      "GPS fix timeout ms (>=5000)",
      fixTimeoutBuf,
      15);
  WiFiManagerParameter p_gps_pin(
      "gps_pwr_pin",
      "GPS power GPIO (-1 = always on)",
      gpsPinBuf,
      7);
  WiFiManagerParameter p_gps_active(
      "gps_pwr_high",
      "GPS power active high (1/0)",
      gpsActiveBuf,
      3);
  WiFiManagerParameter p_mhz("lora_mhz", "LoRa MHz (915/868)", mhzBuf, 7);

  wm.addParameter(&p_serial);
  wm.addParameter(&p_interval);
  wm.addParameter(&p_fix_timeout);
  wm.addParameter(&p_gps_pin);
  wm.addParameter(&p_gps_active);
  wm.addParameter(&p_mhz);

  const String apName = String("Collar-") + hwSerial.substring(5);
  wm.startConfigPortal(apName.c_str());

  String newSerial = String(p_serial.getValue());
  newSerial.trim();
  uint32_t newInterval = static_cast<uint32_t>(atoi(p_interval.getValue()));
  uint32_t newFixTimeout = static_cast<uint32_t>(atoi(p_fix_timeout.getValue()));
  int newGpsPin = atoi(p_gps_pin.getValue());
  const bool newGpsHigh = atoi(p_gps_active.getValue()) != 0;
  uint32_t newMhz = static_cast<uint32_t>(atoi(p_mhz.getValue()));

  if (newSerial.isEmpty() || newSerial == hwSerial) {
    newSerial = "";
  }
  if (newInterval < 5000) {
    newInterval = 5000;
  }
  if (newFixTimeout < 5000) {
    newFixTimeout = 5000;
  }
  if (newMhz != 868 && newMhz != 915) {
    newMhz = 915;
  }

  prefs.begin("collar", false);
  prefs.putString("serial", newSerial);
  prefs.putUInt("interval_ms", newInterval);
  prefs.putUInt("fix_timeout", newFixTimeout);
  prefs.putInt("gps_pwr_pin", newGpsPin);
  prefs.putBool("gps_pwr_high", newGpsHigh);
  prefs.putUInt("lora_mhz", newMhz);
  prefs.putBool("configured", true);
  prefs.end();

  WiFi.mode(WIFI_OFF);
  delay(200);
  ESP.restart();
}

static void setGpsPower(bool on) {
  if (g_gpsPowerPin < 0) {
    return;
  }
  const bool level = g_gpsPowerActiveHigh ? on : !on;
  digitalWrite(g_gpsPowerPin, level ? HIGH : LOW);
}

static void initGpsPowerPin() {
  if (g_gpsPowerPin < 0) {
    return;
  }
  pinMode(g_gpsPowerPin, OUTPUT);
  setGpsPower(false);
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

static bool waitForGpsFix(uint32_t timeoutMs) {
  const uint32_t started = millis();
  while (millis() - started < timeoutMs) {
    while (SerialGPS.available() > 0) {
      gps.encode(static_cast<char>(SerialGPS.read()));
    }
    if (gps.location.isValid() && gps.location.age() < 2000) {
      return true;
    }
    delay(10);
  }
  return false;
}

static bool sendLocation(uint32_t sequence) {
  if (!gps.location.isValid()) {
    return false;
  }

  char packet[96];
  snprintf(
      packet,
      sizeof(packet),
      "%s|%.6f|%.6f|%lu",
      g_deviceSerial.c_str(),
      gps.location.lat(),
      gps.location.lng(),
      static_cast<unsigned long>(sequence));

  LoRa.beginPacket();
  LoRa.print(packet);
  const bool ok = LoRa.endPacket() == 1;
  LOGF("tx %s ok=%d\n", packet, ok ? 1 : 0);
  return ok;
}

static void enterDeepSleep() {
  // esp_sleep_enable_timer_wakeup expects microseconds.
  const uint64_t sleepUs =
      static_cast<uint64_t>(g_sleepIntervalMs) * 1000ULL;
  esp_sleep_enable_timer_wakeup(sleepUs);
  LOGF("sleep %u ms\n", g_sleepIntervalMs);
#if LOG_ENABLED
  Serial.flush();
#endif
  esp_deep_sleep_start();
}

void setup() {
#if LOG_ENABLED
  Serial.begin(115200);
  delay(200);
#endif

  // Config portal before duty cycle (keeps Wi-Fi out of the sleep path).
  if (shouldOpenConfigPortal()) {
    runConfigPortal();
  }

  loadSettings();
  LOGF(
      "serial=%s sleep=%u fix_timeout=%u gps_pin=%d freq=%ld\n",
      g_deviceSerial.c_str(),
      g_sleepIntervalMs,
      g_gpsFixTimeoutMs,
      g_gpsPowerPin,
      g_loraFrequencyHz);

  initGpsPowerPin();
  setGpsPower(true);

  SerialGPS.begin(GPS_BAUD, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);

  if (!initLoRa()) {
    setGpsPower(false);
    enterDeepSleep();
  }

  const bool gotFix = waitForGpsFix(g_gpsFixTimeoutMs);
  if (gotFix) {
    const uint32_t seq = loadAndBumpSequence();
    sendLocation(seq);
  } else {
    LOGF("gps fix timeout\n");
  }

  // Put LoRa radio to sleep; ESP deep sleep follows.
  LoRa.sleep();
  setGpsPower(false);
  delay(20);
  enterDeepSleep();
}

void loop() {
  // Unreachable: deep sleep restarts into setup().
}
