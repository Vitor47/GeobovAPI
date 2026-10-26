/*
 * CowTrack LoRa Gateway - Binary Receiver
 *
 * Hardware:
 *   ESP32
 *   SX127x LoRa
 *
 * Recebe pacote binário CowTrack de 17 bytes:
 *
 *   [0]      protocolVersion    uint8_t
 *   [1..2]   cowId              uint16_t
 *   [3..6]   latitude           int32_t
 *   [7..10]  longitude          int32_t
 *   [11..14] sequence           uint32_t
 *   [15]     satellites         uint8_t
 *   [16]     hdopX10            uint8_t
 *
 * Depois adiciona informações medidas pelo próprio Gateway:
 *
 *   RSSI
 *   SNR
 *
 * E envia para:
 *
 *   https://54.94.137.227/api/v1/gateways/ingest
 *
 * Header:
 *
 *   X-Gateway-Api-Key
 *
 * JSON:
 *
 * {
 *   "cow_id": 1,
 *   "lat": -29.673200,
 *   "lon": -53.811300,
 *   "sequence": 15,
 *   "satellites": 8,
 *   "hdop": 1.2,
 *   "rssi": -87,
 *   "snr": 7.5,
 *   "protocol_version": 1
 * }
 *
 * IMPORTANTE:
 *
 * O Sender e o Receiver precisam utilizar exatamente
 * a mesma estrutura LoRaPacket.
 *
 * Bibliotecas:
 *   LoRa
 *   WiFiManager
 *   Preferences
 *   HTTPClient
 *
 * Hardware:
 *   ESP32 + SX127x
 */

// ===========================================================================
// INCLUDES
// ===========================================================================

#include <Arduino.h>
#include <Preferences.h>
#include <SPI.h>
#include <LoRa.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <WiFiManager.h>
#include "isrg_root_x1.h"

// ===========================================================================
// HARDWARE - LORA
// ===========================================================================

static const int LORA_SCK  = 5;
static const int LORA_MISO = 19;
static const int LORA_MOSI = 27;
static const int LORA_SS   = 18;
static const int LORA_RST  = 14;
static const int LORA_DIO0 = 26;

// BOOT
static const int CONFIG_BUTTON_PIN = 0;

// ===========================================================================
// LOG
// ===========================================================================

#ifndef LOG_ENABLED
#define LOG_ENABLED 1
#endif

#if LOG_ENABLED

#define LOGF(...)                     \
  do {                                \
    Serial.printf(__VA_ARGS__);       \
  } while (0)

#else

#define LOGF(...)                     \
  do {                                \
  } while (0)

#endif

// ===========================================================================
// CONSTANTS
// ===========================================================================

// Versão do protocolo
static constexpr uint8_t PROTOCOL_VERSION = 1;

// Coordenadas recebidas:
// graus * 1.000.000
static constexpr double COORD_SCALE = 1000000.0;

// Tamanho exato do pacote
static constexpr size_t LORA_PACKET_SIZE = 17;

// Frequência padrão
static constexpr uint32_t DEFAULT_LORA_MHZ = 915;

// Production ingest endpoint. A saved LAN address is replaced on boot.
static const char DEFAULT_API_URL[] =
    "https://54.94.137.227/api/v1/gateways/ingest";
static const char LEGACY_LAN_API_URL[] =
    "http://192.168.0.44:8000/api/v1/gateways/ingest";

// ===========================================================================
// BINARY PACKET
// ===========================================================================
//
// Must match the sender exactly.
//
// Sender:
//   sizeof(LoRaPacket) == 17
//
// Receiver:
//   sizeof(LoRaPacket) == 17
//

struct __attribute__((packed)) LoRaPacket {

  uint8_t protocolVersion;

  uint16_t cowId;

  int32_t latitude;

  int32_t longitude;

  uint32_t sequence;

  uint8_t satellites;

  uint8_t hdopX10;
};

static_assert(
    sizeof(LoRaPacket) == 17,
    "LoRaPacket must be exactly 17 bytes"
);

// ===========================================================================
// TELEMETRY DECODED
// ===========================================================================

struct TelemetryPacket {

  uint8_t protocolVersion;

  uint16_t cowId;

  double lat;

  double lon;

  uint32_t sequence;

  uint8_t satellites;

  double hdop;

  int rssi;

  float snr;

  bool valid;
};

static String resolveApiUrl(const String& saved) {
  if (saved.length() == 0 || saved == LEGACY_LAN_API_URL) {
    return String(DEFAULT_API_URL);
  }
  return saved;
}

// ===========================================================================
// GLOBALS
// ===========================================================================

static Preferences prefs;

static String g_apiUrl;

static String g_gatewayApiKey;

static long g_loraFrequencyHz =
    static_cast<long>(
        DEFAULT_LORA_MHZ
    ) * 1000000L;

// ===========================================================================
// LOAD SETTINGS
// ===========================================================================

static void loadSettings() {

  prefs.begin(
      "gateway",
      true
  );

  const String savedUrl =
      prefs.getString(
          "api_url",
          DEFAULT_API_URL
      );

  g_gatewayApiKey =
      prefs.getString(
          "api_key",
          ""
      );

  const uint32_t mhz =
      prefs.getUInt(
          "lora_mhz",
          DEFAULT_LORA_MHZ
      );

  prefs.end();

  g_apiUrl = resolveApiUrl(savedUrl);

  if (g_apiUrl != savedUrl) {
    prefs.begin(
        "gateway",
        false
    );
    prefs.putString(
        "api_url",
        g_apiUrl
    );
    prefs.end();
  }

  // -------------------------------------------------------------------------
  // Validate frequency
  // -------------------------------------------------------------------------

  if (
      mhz != 868 &&
      mhz != 915
  ) {

    g_loraFrequencyHz =
        static_cast<long>(
            DEFAULT_LORA_MHZ
        ) * 1000000L;

  } else {

    g_loraFrequencyHz =
        static_cast<long>(
            mhz
        ) * 1000000L;
  }
}

// ===========================================================================
// SETTINGS READY
// ===========================================================================

static bool settingsReady() {

  return
      g_apiUrl.length() > 0 &&
      g_gatewayApiKey.length() > 0;
}

// ===========================================================================
// FORCE CONFIG PORTAL
// ===========================================================================

static bool shouldForcePortal() {

  pinMode(
      CONFIG_BUTTON_PIN,
      INPUT_PULLUP
  );

  delay(50);

  return
      digitalRead(
          CONFIG_BUTTON_PIN
      ) == LOW;
}

// ===========================================================================
// SAVE SETTINGS
// ===========================================================================

static void saveSettings(
    const String& apiUrl,
    const String& apiKey,
    uint32_t loraMhz) {

  prefs.begin(
      "gateway",
      false
  );

  prefs.putString(
      "api_url",
      apiUrl
  );

  prefs.putString(
      "api_key",
      apiKey
  );

  prefs.putUInt(
      "lora_mhz",
      loraMhz
  );

  prefs.putBool(
      "configured",
      true
  );

  prefs.end();
}

// ===========================================================================
// CONFIG PORTAL
// ===========================================================================

static bool runConfigPortal(
    bool force) {

  char apiUrlBuf[160];

  char apiKeyBuf[96];

  char mhzBuf[8];

  // -------------------------------------------------------------------------
  // Load saved values
  // -------------------------------------------------------------------------

  prefs.begin(
      "gateway",
      true
  );

  String savedUrl =
      resolveApiUrl(
          prefs.getString(
              "api_url",
              DEFAULT_API_URL
          )
      );

  String savedKey =
      prefs.getString(
          "api_key",
          ""
      );

  const uint32_t savedMhz =
      prefs.getUInt(
          "lora_mhz",
          DEFAULT_LORA_MHZ
      );

  prefs.end();

  // -------------------------------------------------------------------------
  // Convert values
  // -------------------------------------------------------------------------

  savedUrl.toCharArray(
      apiUrlBuf,
      sizeof(apiUrlBuf)
  );

  savedKey.toCharArray(
      apiKeyBuf,
      sizeof(apiKeyBuf)
  );

  snprintf(
      mhzBuf,
      sizeof(mhzBuf),
      "%lu",
      static_cast<unsigned long>(
          savedMhz
      )
  );

  // -------------------------------------------------------------------------
  // WiFiManager
  // -------------------------------------------------------------------------

  WiFiManager wm;

  wm.setConfigPortalTimeout(
      force ? 0 : 180
  );

  WiFiManagerParameter p_url(
      "api_url",
      "API ingest URL",
      apiUrlBuf,
      159
  );

  WiFiManagerParameter p_key(
      "api_key",
      "X-Gateway-Api-Key",
      apiKeyBuf,
      95
  );

  WiFiManagerParameter p_mhz(
      "lora_mhz",
      "LoRa MHz (915/868)",
      mhzBuf,
      7
  );

  wm.addParameter(
      &p_url
  );

  wm.addParameter(
      &p_key
  );

  wm.addParameter(
      &p_mhz
  );

  // -------------------------------------------------------------------------
  // Connect
  // -------------------------------------------------------------------------

  bool connected = false;

  if (
      force ||
      !settingsReady()
  ) {

    LOGF(
        "Starting Gateway configuration portal...\n"
    );

    connected =
        wm.startConfigPortal(
            "GeoBov-Gateway"
        );

  } else {

    LOGF(
        "Connecting to saved Wi-Fi...\n"
    );

    connected =
        wm.autoConnect(
            "Gateway-Config"
        );
  }

  if (!connected) {

    LOGF(
        "Wi-Fi connection failed\n"
    );

    return false;
  }

  // -------------------------------------------------------------------------
  // Read configuration
  // -------------------------------------------------------------------------

  String newUrl =
      String(
          p_url.getValue()
      );

  String newKey =
      String(
          p_key.getValue()
      );

  uint32_t newMhz =
      static_cast<uint32_t>(
          atoi(
              p_mhz.getValue()
          )
      );

  newUrl.trim();

  newKey.trim();

  // -------------------------------------------------------------------------
  // Validate frequency
  // -------------------------------------------------------------------------

  if (
      newMhz != 868 &&
      newMhz != 915
  ) {

    newMhz =
        DEFAULT_LORA_MHZ;
  }

  // -------------------------------------------------------------------------
  // Save only valid values
  // -------------------------------------------------------------------------

  if (
      newUrl.length() > 0 &&
      newKey.length() > 0
  ) {

    saveSettings(
        newUrl,
        newKey,
        newMhz
    );
  }

  // -------------------------------------------------------------------------
  // Reload
  // -------------------------------------------------------------------------

  loadSettings();

  LOGF(
      "Wi-Fi connected\n"
  );

  LOGF(
      "IP: %s\n",
      WiFi.localIP().toString().c_str()
  );

  LOGF(
      "API URL: %s\n",
      g_apiUrl.c_str()
  );

  LOGF(
      "LoRa frequency: %ld Hz\n",
      g_loraFrequencyHz
  );

  return
      settingsReady() &&
      WiFi.status() ==
          WL_CONNECTED;
}

// ===========================================================================
// INIT LORA
// ===========================================================================

static bool initLoRa() {

  LOGF(
      "Initializing LoRa...\n"
  );

  SPI.begin(
      LORA_SCK,
      LORA_MISO,
      LORA_MOSI,
      LORA_SS
  );

  LoRa.setPins(
      LORA_SS,
      LORA_RST,
      LORA_DIO0
  );

  if (
      !LoRa.begin(
          g_loraFrequencyHz
      )
  ) {

    LOGF(
        "ERROR: LoRa initialization failed\n"
    );

    return false;
  }

  // Mesmo SyncWord do Sender
  LoRa.setSyncWord(
      0x12
  );

  // CRC
  LoRa.enableCrc();

  LOGF(
      "LoRa initialized successfully\n"
  );

  LOGF(
      "Frequency: %ld Hz\n",
      g_loraFrequencyHz
  );

  LOGF(
      "SyncWord: 0x12\n"
  );

  LOGF(
      "CRC: enabled\n"
  );

  return true;
}

// ===========================================================================
// DECODE PACKET
// ===========================================================================

static TelemetryPacket decodeLoRaPacket(
    const uint8_t* data,
    size_t length,
    int rssi,
    float snr) {

  TelemetryPacket out{};

  out.valid = false;

  // -------------------------------------------------------------------------
  // Tamanho obrigatório
  // -------------------------------------------------------------------------

  if (
      data == nullptr ||
      length != sizeof(LoRaPacket)
  ) {

    LOGF(
        "Invalid packet size: %u bytes\n",
        static_cast<unsigned int>(
            length
        )
    );

    return out;
  }

  // -------------------------------------------------------------------------
  // Copy binary packet
  // -------------------------------------------------------------------------

  LoRaPacket packet{};

  memcpy(
      &packet,
      data,
      sizeof(packet)
  );

  // -------------------------------------------------------------------------
  // Protocol version
  // -------------------------------------------------------------------------

  if (
      packet.protocolVersion !=
      PROTOCOL_VERSION
  ) {

    LOGF(
        "Unsupported protocol version: %u\n",
        packet.protocolVersion
    );

    return out;
  }

  // -------------------------------------------------------------------------
  // Cow ID
  // -------------------------------------------------------------------------

  if (
      packet.cowId == 0
  ) {

    LOGF(
        "Invalid Cow ID: 0\n"
    );

    return out;
  }

  // -------------------------------------------------------------------------
  // Coordinates
  // -------------------------------------------------------------------------

  const double lat =
      packet.latitude /
      COORD_SCALE;

  const double lon =
      packet.longitude /
      COORD_SCALE;

  if (
      lat < -90.0 ||
      lat > 90.0
  ) {

    LOGF(
        "Invalid latitude: %.6f\n",
        lat
    );

    return out;
  }

  if (
      lon < -180.0 ||
      lon > 180.0
  ) {

    LOGF(
        "Invalid longitude: %.6f\n",
        lon
    );

    return out;
  }

  // Não aceitar 0,0
  if (
      lat == 0.0 &&
      lon == 0.0
  ) {

    LOGF(
        "Invalid coordinates: 0,0\n"
    );

    return out;
  }

  // -------------------------------------------------------------------------
  // Satellite validation
  // -------------------------------------------------------------------------

  if (
      packet.satellites == 0
  ) {

    LOGF(
        "Invalid satellite count: 0\n"
    );

    return out;
  }

  // -------------------------------------------------------------------------
  // HDOP
  // -------------------------------------------------------------------------

  const double hdop =
      packet.hdopX10 /
      10.0;

  // -------------------------------------------------------------------------
  // Fill telemetry
  // -------------------------------------------------------------------------

  out.protocolVersion =
      packet.protocolVersion;

  out.cowId =
      packet.cowId;

  out.lat =
      lat;

  out.lon =
      lon;

  out.sequence =
      packet.sequence;

  out.satellites =
      packet.satellites;

  out.hdop =
      hdop;

  out.rssi =
      rssi;

  out.snr =
      snr;

  out.valid = true;

  return out;
}

// ===========================================================================
// PRINT TELEMETRY
// ===========================================================================

static void printTelemetry(
    const TelemetryPacket& packet) {

  LOGF(
      "\n"
  );

  LOGF(
      "====================================\n"
  );

  LOGF(
      "         COWTRACK LORA RX           \n"
  );

  LOGF(
      "====================================\n"
  );

  LOGF(
      "Protocol version: %u\n",
      packet.protocolVersion
  );

  LOGF(
      "Cow ID: %u\n",
      packet.cowId
  );

  LOGF(
      "Latitude: %.6f\n",
      packet.lat
  );

  LOGF(
      "Longitude: %.6f\n",
      packet.lon
  );

  LOGF(
      "Sequence: %lu\n",
      static_cast<unsigned long>(
          packet.sequence
      )
  );

  LOGF(
      "Satellites: %u\n",
      packet.satellites
  );

  LOGF(
      "HDOP: %.1f\n",
      packet.hdop
  );

  LOGF(
      "RSSI: %d dBm\n",
      packet.rssi
  );

  LOGF(
      "SNR: %.2f dB\n",
      packet.snr
  );

  LOGF(
      "====================================\n"
  );
}

// ===========================================================================
// POST TELEMETRY
// ===========================================================================

static bool postTelemetry(
    const TelemetryPacket& packet) {

  // -------------------------------------------------------------------------
  // Wi-Fi
  // -------------------------------------------------------------------------

  if (
      WiFi.status() !=
      WL_CONNECTED
  ) {

    LOGF(
        "ERROR: Wi-Fi disconnected\n"
    );

    return false;
  }

  // -------------------------------------------------------------------------
  // JSON
  // -------------------------------------------------------------------------

  char body[512];

  snprintf(
      body,
      sizeof(body),

      "{"
        "\"protocol_version\":%u,"
        "\"cow_id\":%u,"
        "\"lat\":%.6f,"
        "\"lon\":%.6f,"
        "\"sequence\":%lu,"
        "\"satellites\":%u,"
        "\"hdop\":%.1f,"
        "\"rssi\":%d,"
        "\"snr\":%.2f"
      "}",

      static_cast<unsigned int>(
          packet.protocolVersion
      ),

      static_cast<unsigned int>(
          packet.cowId
      ),

      packet.lat,

      packet.lon,

      static_cast<unsigned long>(
          packet.sequence
      ),

      static_cast<unsigned int>(
          packet.satellites
      ),

      packet.hdop,

      packet.rssi,

      packet.snr
  );

  LOGF(
      "POST %s\n",
      g_apiUrl.c_str()
  );

  LOGF(
      "BODY: %s\n",
      body
  );

  // -------------------------------------------------------------------------
  // HTTP
  // -------------------------------------------------------------------------

  HTTPClient http;
  WiFiClientSecure secureClient;

  http.setTimeout(
      8000
  );

  bool began = false;
  if (g_apiUrl.startsWith("https://")) {
    secureClient.setCACert(ISRG_ROOT_X1);
    began = http.begin(secureClient, g_apiUrl);
  } else {
    began = http.begin(g_apiUrl);
  }

  if (!began) {

    LOGF(
        "ERROR: HTTP begin failed\n"
    );

    return false;
  }

  http.addHeader(
      "Content-Type",
      "application/json"
  );

  http.addHeader(
      "X-Gateway-Api-Key",
      g_gatewayApiKey
  );

  const int code =
      http.POST(
          String(body)
      );

  LOGF(
      "HTTP response: %d\n",
      code
  );

  if (
      code > 0
  ) {

    const String response =
        http.getString();

    LOGF(
        "API response: %s\n",
        response.c_str()
    );
  }

  http.end();

  // -------------------------------------------------------------------------
  // Result
  // -------------------------------------------------------------------------

  if (
      code >= 200 &&
      code < 300
  ) {

    LOGF(
        "API ingest OK\n"
    );

    return true;
  }

  LOGF(
      "API ingest FAILED\n"
  );

  return false;
}

// ===========================================================================
// RECEIVE ONE PACKET
// ===========================================================================

static void receivePacket() {

  const int packetSize =
      LoRa.parsePacket();

  if (
      packetSize <= 0
  ) {

    return;
  }

  LOGF(
      "\nReceived LoRa packet: %d bytes\n",
      packetSize
  );

  // -------------------------------------------------------------------------
  // O pacote precisa ter exatamente 17 bytes.
  // -------------------------------------------------------------------------

  if (
      packetSize !=
      static_cast<int>(
          sizeof(LoRaPacket)
      )
  ) {

    LOGF(
        "INVALID PACKET SIZE\n"
        "Expected: %u\n"
        "Received: %d\n",
        static_cast<unsigned int>(
            sizeof(LoRaPacket)
        ),
        packetSize
    );

    // Esvazia o buffer
    while (
        LoRa.available()
    ) {

      LoRa.read();
    }

    return;
  }

  // -------------------------------------------------------------------------
  // Read binary data
  // -------------------------------------------------------------------------

  uint8_t buffer[
      sizeof(LoRaPacket)
  ];

  size_t index = 0;

  while (
      LoRa.available() &&
      index < sizeof(buffer)
  ) {

    buffer[index++] =
        static_cast<uint8_t>(
            LoRa.read()
        );
  }

  // -------------------------------------------------------------------------
  // Confirm number of bytes
  // -------------------------------------------------------------------------

  if (
      index !=
      sizeof(buffer)
  ) {

    LOGF(
        "ERROR: incomplete packet %u/%u bytes\n",
        static_cast<unsigned int>(
            index
        ),
        static_cast<unsigned int>(
            sizeof(buffer)
        )
    );

    return;
  }

  // -------------------------------------------------------------------------
  // Read LoRa radio metrics
  // -------------------------------------------------------------------------

  const int rssi =
      LoRa.packetRssi();

  const float snr =
      LoRa.packetSnr();

  // -------------------------------------------------------------------------
  // Decode
  // -------------------------------------------------------------------------

  const TelemetryPacket packet =
      decodeLoRaPacket(
          buffer,
          sizeof(buffer),
          rssi,
          snr
      );

  if (
      !packet.valid
  ) {

    LOGF(
        "Invalid CowTrack packet\n"
    );

    return;
  }

  // -------------------------------------------------------------------------
  // Print
  // -------------------------------------------------------------------------

  printTelemetry(
      packet
  );

  // -------------------------------------------------------------------------
  // Forward API
  // -------------------------------------------------------------------------

  postTelemetry(
      packet
  );
}

// ===========================================================================
// SETUP
// ===========================================================================

void setup() {

#if LOG_ENABLED

  Serial.begin(
      115200
  );

  delay(500);

#endif

  LOGF(
      "\n\n"
      "====================================\n"
      "       COWTRACK LORA GATEWAY        \n"
      "       BINARY PROTOCOL V1           \n"
      "====================================\n"
  );

  // -------------------------------------------------------------------------
  // Load settings
  // -------------------------------------------------------------------------

  loadSettings();

  LOGF(
      "API URL: %s\n",
      g_apiUrl.c_str()
  );

  LOGF(
      "LoRa frequency: %ld Hz\n",
      g_loraFrequencyHz
  );

  // -------------------------------------------------------------------------
  // Configuration portal
  // -------------------------------------------------------------------------

  const bool forcePortal =
      shouldForcePortal() ||
      !settingsReady();

  if (
      !runConfigPortal(
          forcePortal
      )
  ) {

    LOGF(
        "Configuration/Wi-Fi failed\n"
    );

    delay(3000);

    ESP.restart();
  }

  // -------------------------------------------------------------------------
  // LoRa
  // -------------------------------------------------------------------------

  if (
      !initLoRa()
  ) {

    LOGF(
        "FATAL: LoRa initialization failed\n"
    );

    while (true) {

      delay(1000);
    }
  }

  // -------------------------------------------------------------------------
  // Ready
  // -------------------------------------------------------------------------

  LOGF(
      "\n"
      "====================================\n"
  );

  LOGF(
      "Gateway READY\n"
  );

  LOGF(
      "Waiting for 17-byte LoRa packets...\n"
  );

  LOGF(
      "====================================\n"
  );
}

// ===========================================================================
// LOOP
// ===========================================================================

void loop() {

  receivePacket();

  delay(5);
}