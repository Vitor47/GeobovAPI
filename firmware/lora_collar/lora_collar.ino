/*
 * CowTrack LoRa Collar - Binary Sender
 *
 * ESP32 + SX127x LoRa + GY-NE06 / NEO-6 GPS
 *
 * FUNCIONAMENTO:
 *
 *   1. ESP32 acorda
 *   2. Inicializa GPS
 *   3. Aguarda posição válida
 *   4. Verifica satélites + HDOP
 *   5. Envia 1 pacote LoRa de 17 bytes
 *   6. Coloca LoRa em sleep
 *   7. Desliga UART do GPS
 *   8. ESP32 entra em Deep Sleep
 *   9. Após ~20 minutos acorda e repete
 *
 * PACOTE:
 *
 *   [0]      protocolVersion    uint8_t
 *   [1..2]   cowId              uint16_t
 *   [3..6]   latitude           int32_t
 *   [7..10]  longitude          int32_t
 *   [11..14] sequence           uint32_t
 *   [15]     satellites         uint8_t
 *   [16]     hdopX10            uint8_t
 *
 * TOTAL: 17 bytes
 */

 #include <Arduino.h>
 #include <Preferences.h>
 #include <SPI.h>
 #include <LoRa.h>
 #include <TinyGPS++.h>
 #include <WiFi.h>
 #include <WiFiManager.h>
 #include "esp_sleep.h"
 
 // ===========================================================================
 // HARDWARE
 // ===========================================================================
 
 // GPS
 static const int GPS_RX_PIN = 13;
 static const int GPS_TX_PIN = 12;
 static const uint32_t GPS_BAUD = 9600;
 
 // LoRa SX127x
 static const int LORA_SCK  = 5;
 static const int LORA_MISO = 19;
 static const int LORA_MOSI = 27;
 static const int LORA_SS   = 18;
 static const int LORA_RST  = 14;
 static const int LORA_DIO0 = 26;
 
 // BOOT button
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
 
 static constexpr uint8_t PROTOCOL_VERSION = 1;
 
 // Coordenadas x 1.000.000
 static constexpr int32_t COORD_SCALE = 1000000L;
 
 // Frequência LoRa padrão
 static constexpr uint32_t DEFAULT_LORA_MHZ = 915;
 
 // ===========================================================================
 // DEEP SLEEP
 // ===========================================================================
 
 // 20 minutos = 1200 segundos
 static constexpr uint32_t DEFAULT_SLEEP_SECONDS = 1200;
 
 // Tempo máximo tentando conseguir GPS
 //
 // 5 minutos.
 // Se não conseguir posição válida nesse período,
 // não transmite e vai dormir mesmo assim.
 static constexpr uint32_t GPS_FIX_TIMEOUT_MS = 300000;
 
 // Mínimo de satélites aceitos
 static constexpr uint8_t MIN_SATELLITES = 4;
 
 // ===========================================================================
 // GLOBALS
 // ===========================================================================
 
 static Preferences prefs;
 
 static TinyGPSPlus gps;
 
 static HardwareSerial SerialGPS(2);
 
 static uint16_t g_cowId = 1;
 
 static uint32_t g_sleepSeconds =
     DEFAULT_SLEEP_SECONDS;
 
 static long g_loraFrequencyHz =
     static_cast<long>(DEFAULT_LORA_MHZ) * 1000000L;
 
 
 // ===========================================================================
 // SEQUENCE
 // ===========================================================================
 //
 // RTC_DATA_ATTR permanece durante Deep Sleep.
 //
 // Portanto:
 //
 // envio 1 -> sequence 1
 // dorme
 // acorda
 // envio 2 -> sequence 2
 // dorme
 // acorda
 // envio 3 -> sequence 3
 //
 // IMPORTANTE:
 // Se a bateria for totalmente desconectada/zerada,
 // a memória RTC será perdida.
 //
 
 RTC_DATA_ATTR uint32_t g_sequence = 0;
 
 // ===========================================================================
 // PACKET
 // ===========================================================================
 
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
 // HARDWARE SERIAL
 // ===========================================================================
 
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
       (uint8_t)(mac >> 40)
   );
 
   return String(buf);
 }
 
 // ===========================================================================
 // LOAD SETTINGS
 // ===========================================================================
 
 static void loadSettings() {
 
   prefs.begin("collar", true);
 
   g_cowId =
       prefs.getUShort(
           "cow_id",
           1
       );
 
   g_sleepSeconds =
       prefs.getUInt(
           "sleep_sec",
           DEFAULT_SLEEP_SECONDS
       );
 
   const uint32_t mhz =
       prefs.getUInt(
           "lora_mhz",
           DEFAULT_LORA_MHZ
       );
 
   prefs.end();
 
   // -------------------------------------------------------------------------
   // Cow ID
   // -------------------------------------------------------------------------
 
   if (g_cowId == 0) {
     g_cowId = 1;
   }
 
   // -------------------------------------------------------------------------
   // Sleep
   // -------------------------------------------------------------------------
 
   if (g_sleepSeconds < 60) {
     g_sleepSeconds = DEFAULT_SLEEP_SECONDS;
   }
 
   // -------------------------------------------------------------------------
   // LoRa
   // -------------------------------------------------------------------------
 
   if (mhz != 868 && mhz != 915) {
 
     g_loraFrequencyHz =
         static_cast<long>(
             DEFAULT_LORA_MHZ
         ) * 1000000L;
 
   } else {
 
     g_loraFrequencyHz =
         static_cast<long>(mhz) * 1000000L;
   }
 }
 
 // ===========================================================================
 // SHOULD OPEN CONFIG PORTAL?
 // ===========================================================================
 
 static bool shouldOpenConfigPortal() {
 
   pinMode(
       CONFIG_BUTTON_PIN,
       INPUT_PULLUP
   );
 
   delay(50);
 
   // BOTÃO BOOT pressionado
   if (digitalRead(CONFIG_BUTTON_PIN) == LOW) {
     return true;
   }
 
   prefs.begin("collar", true);
 
   const bool configured =
       prefs.getBool(
           "configured",
           false
       );
 
   prefs.end();
 
   return !configured;
 }
 
 // ===========================================================================
 // SAVE SETTINGS
 // ===========================================================================
 
 static void saveSettings(
     uint16_t cowId,
     uint32_t sleepSeconds,
     uint32_t loraMhz) {
 
   prefs.begin(
       "collar",
       false
   );
 
   prefs.putUShort(
       "cow_id",
       cowId
   );
 
   prefs.putUInt(
       "sleep_sec",
       sleepSeconds
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
 
 static void runConfigPortal() {
 
   WiFi.mode(WIFI_STA);
 
   const String hwSerial =
       buildHardwareSerial();
 
   char cowIdBuf[8];
 
   char sleepBuf[16];
 
   char mhzBuf[8];
 
   // -------------------------------------------------------------------------
   // Load saved values
   // -------------------------------------------------------------------------
 
   prefs.begin(
       "collar",
       true
   );
 
   const uint16_t savedCowId =
       prefs.getUShort(
           "cow_id",
           1
       );
 
   const uint32_t savedSleep =
       prefs.getUInt(
           "sleep_sec",
           DEFAULT_SLEEP_SECONDS
       );
 
   const uint32_t savedMhz =
       prefs.getUInt(
           "lora_mhz",
           DEFAULT_LORA_MHZ
       );
 
   prefs.end();
 
   // -------------------------------------------------------------------------
   // Convert to text
   // -------------------------------------------------------------------------
 
   snprintf(
       cowIdBuf,
       sizeof(cowIdBuf),
       "%u",
       savedCowId
   );
 
   snprintf(
       sleepBuf,
       sizeof(sleepBuf),
       "%lu",
       static_cast<unsigned long>(
           savedSleep
       )
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
 
   wm.setConfigPortalTimeout(180);
 
   WiFiManagerParameter p_cowId(
       "cow_id",
       "Cow ID (1-65535)",
       cowIdBuf,
       7
   );
 
   WiFiManagerParameter p_sleep(
       "sleep_sec",
       "Sleep time seconds (>=60)",
       sleepBuf,
       15
   );
 
   WiFiManagerParameter p_mhz(
       "lora_mhz",
       "LoRa MHz (915/868)",
       mhzBuf,
       7
   );
 
   wm.addParameter(
       &p_cowId
   );
 
   wm.addParameter(
       &p_sleep
   );
 
   wm.addParameter(
       &p_mhz
   );
 
   // -------------------------------------------------------------------------
   // Access Point
   // -------------------------------------------------------------------------
 
   const String apName =
       String("CowTrack-Collar-") +
       hwSerial.substring(5);
 
   LOGF(
       "Starting configuration portal: %s\n",
       apName.c_str()
   );
 
   wm.startConfigPortal(
       apName.c_str()
   );
 
   // -------------------------------------------------------------------------
   // Read values
   // -------------------------------------------------------------------------
 
   uint32_t cowIdRaw =
       static_cast<uint32_t>(
           atoi(
               p_cowId.getValue()
           )
       );
 
   uint32_t sleepRaw =
       static_cast<uint32_t>(
           atoi(
               p_sleep.getValue()
           )
       );
 
   uint32_t mhzRaw =
       static_cast<uint32_t>(
           atoi(
               p_mhz.getValue()
           )
       );
 
   // -------------------------------------------------------------------------
   // Validate Cow ID
   // -------------------------------------------------------------------------
 
   if (
       cowIdRaw < 1 ||
       cowIdRaw > 65535
   ) {
 
     cowIdRaw = 1;
   }
 
   // -------------------------------------------------------------------------
   // Validate sleep
   // -------------------------------------------------------------------------
 
   if (sleepRaw < 60) {
 
     sleepRaw =
         DEFAULT_SLEEP_SECONDS;
   }
 
   // -------------------------------------------------------------------------
   // Validate frequency
   // -------------------------------------------------------------------------
 
   if (
       mhzRaw != 868 &&
       mhzRaw != 915
   ) {
 
     mhzRaw =
         DEFAULT_LORA_MHZ;
   }
 
   // -------------------------------------------------------------------------
   // Save
   // -------------------------------------------------------------------------
 
   saveSettings(
       static_cast<uint16_t>(
           cowIdRaw
       ),
       sleepRaw,
       mhzRaw
   );
 
   LOGF(
       "Configuration saved:\n"
   );
 
   LOGF(
       "  Cow ID: %lu\n",
       static_cast<unsigned long>(
           cowIdRaw
       )
   );
 
   LOGF(
       "  Sleep: %lu seconds\n",
       static_cast<unsigned long>(
           sleepRaw
       )
   );
 
   LOGF(
       "  LoRa: %lu MHz\n",
       static_cast<unsigned long>(
           mhzRaw
       )
   );
 
   WiFi.mode(WIFI_OFF);
 
   delay(200);
 
   ESP.restart();
 }
 
 // ===========================================================================
 // LORA INIT
 // ===========================================================================
 
 static bool initLoRa() {
 
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
 
   // Mesmo SyncWord do Gateway
   LoRa.setSyncWord(
       0x12
   );
 
   // CRC
   LoRa.enableCrc();
 
   return true;
 }
 
 // ===========================================================================
 // GPS QUALITY
 // ===========================================================================
 
 static bool gpsQualityIsUsable() {
 
   // Posição válida
   if (
       !gps.location.isValid()
   ) {
 
     return false;
   }
 
   // Satélites válidos
   if (
       !gps.satellites.isValid()
   ) {
 
     return false;
   }
 
   // Mínimo de 4 satélites
   if (
       gps.satellites.value() <
       MIN_SATELLITES
   ) {
 
     return false;
   }
 
   // HDOP válido
   if (
       !gps.hdop.isValid()
   ) {
 
     return false;
   }
 
   return true;
 }
 
 // ===========================================================================
 // PROCESS GPS
 // ===========================================================================
 
 static void processGPS() {
 
   while (
       SerialGPS.available() > 0
   ) {
 
     const char c =
         static_cast<char>(
             SerialGPS.read()
         );
 
     gps.encode(c);
   }
 }
 
 // ===========================================================================
 // WAIT GPS FIX
 // ===========================================================================
 
 static bool waitForGPSFix() {
 
   LOGF(
       "Waiting for GPS fix...\n"
   );
 
   const uint32_t start =
       millis();
 
   while (
       millis() - start <
       GPS_FIX_TIMEOUT_MS
   ) {
 
     processGPS();
 
     // -------------------------------------------------------------
     // Mostra informações periodicamente
     // -------------------------------------------------------------
 
     static uint32_t lastGpsLog = 0;
 
     if (
         millis() - lastGpsLog >=
         5000
     ) {
 
       lastGpsLog =
           millis();
 
       LOGF(
           "GPS: sats=%u HDOP=%.2f valid=%d\n",
           gps.satellites.isValid()
               ? gps.satellites.value()
               : 0,
           gps.hdop.isValid()
               ? gps.hdop.hdop()
               : 0.0,
           gps.location.isValid()
               ? 1
               : 0
       );
     }
 
     // -------------------------------------------------------------
     // Encontrou uma posição utilizável
     // -------------------------------------------------------------
 
     if (
         gpsQualityIsUsable()
     ) {
 
       LOGF(
           "GPS FIX OK!\n"
       );
 
       LOGF(
           "Latitude: %.6f\n",
           gps.location.lat()
       );
 
       LOGF(
           "Longitude: %.6f\n",
           gps.location.lng()
       );
 
       LOGF(
           "Satellites: %u\n",
           gps.satellites.value()
       );
 
       LOGF(
           "HDOP: %.2f\n",
           gps.hdop.hdop()
       );
 
       return true;
     }
 
     delay(10);
   }
 
   LOGF(
       "GPS timeout: no usable fix\n"
   );
 
   return false;
 }
 
 // ===========================================================================
 // COORDINATES
 // ===========================================================================
 
 static int32_t latitudeToInt(
     double latitude) {
 
   return static_cast<int32_t>(
       latitude *
       COORD_SCALE
   );
 }
 
 static int32_t longitudeToInt(
     double longitude) {
 
   return static_cast<int32_t>(
       longitude *
       COORD_SCALE
   );
 }
 
 // ===========================================================================
 // HDOP
 // ===========================================================================
 
 static uint8_t compressHdop() {
 
   double hdop =
       gps.hdop.hdop();
 
   if (
       hdop < 0.0
   ) {
 
     hdop = 0.0;
   }
 
   if (
       hdop > 25.5
   ) {
 
     hdop = 25.5;
   }
 
   return static_cast<uint8_t>(
       round(
           hdop * 10.0
       )
   );
 }
 
 // ===========================================================================
 // BUILD PACKET
 // ===========================================================================
 
 static LoRaPacket buildPacket() {
 
   LoRaPacket packet{};
 
   packet.protocolVersion =
       PROTOCOL_VERSION;
 
   packet.cowId =
       g_cowId;
 
   packet.latitude =
       latitudeToInt(
           gps.location.lat()
       );
 
   packet.longitude =
       longitudeToInt(
           gps.location.lng()
       );
 
   // Incrementa a cada transmissão
   packet.sequence =
       ++g_sequence;
 
   uint32_t satellites =
       gps.satellites.value();
 
   if (
       satellites > 255
   ) {
 
     satellites = 255;
   }
 
   packet.satellites =
       static_cast<uint8_t>(
           satellites
       );
 
   packet.hdopX10 =
       compressHdop();
 
   return packet;
 }
 
 // ===========================================================================
 // PRINT PACKET
 // ===========================================================================
 
 static void printPacket(
     const LoRaPacket& packet) {
 
 #if LOG_ENABLED
 
   LOGF("\n");
   LOGF("========== TX ==========\n");
 
   LOGF(
       "Protocol: %u\n",
       packet.protocolVersion
   );
 
   LOGF(
       "Cow ID: %u\n",
       packet.cowId
   );
 
   LOGF(
       "Latitude: %.6f\n",
       packet.latitude /
           1000000.0
   );
 
   LOGF(
       "Longitude: %.6f\n",
       packet.longitude /
           1000000.0
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
       packet.hdopX10 / 10.0
   );
 
   LOGF(
       "Packet size: %u bytes\n",
       static_cast<unsigned int>(
           sizeof(LoRaPacket)
       )
   );
 
   LOGF(
       "========================\n"
   );
 
 #endif
 }
 
 // ===========================================================================
 // SEND LOCATION
 // ===========================================================================
 
 static bool sendLocation() {
 
   if (
       !gpsQualityIsUsable()
   ) {
 
     LOGF(
         "GPS fix not usable - not transmitting\n"
     );
 
     return false;
   }
 
   const LoRaPacket packet =
       buildPacket();
 
   printPacket(packet);
 
   // -------------------------------------------------------------
   // Begin packet
   // -------------------------------------------------------------
 
   LoRa.beginPacket();
 
   const size_t written =
       LoRa.write(
           reinterpret_cast<
               const uint8_t*
           >(&packet),
           sizeof(packet)
       );
 
   const int result =
       LoRa.endPacket();
 
   // -------------------------------------------------------------
   // Validate
   // -------------------------------------------------------------
 
   if (
       result == 0
   ) {
 
     LOGF(
         "ERROR: LoRa transmission failed\n"
     );
 
     return false;
   }
 
   if (
       written != sizeof(packet)
   ) {
 
     LOGF(
         "ERROR: only %u/%u bytes written\n",
         static_cast<unsigned int>(
             written
         ),
         static_cast<unsigned int>(
             sizeof(packet)
         )
     );
 
     return false;
   }
 
   LOGF(
       "LoRa TX OK - %u bytes\n",
       static_cast<unsigned int>(
           sizeof(packet)
       )
   );
 
   return true;
 }
 
 // ===========================================================================
 // PREPARE FOR DEEP SLEEP
 // ===========================================================================
 
 static void prepareForDeepSleep() {
 
   LOGF(
       "\nPreparing for Deep Sleep...\n"
   );
 
   // -------------------------------------------------------------------------
   // Put LoRa into sleep
   // -------------------------------------------------------------------------
 
   LoRa.sleep();
 
   LOGF(
       "LoRa -> sleep\n"
   );
 
   // -------------------------------------------------------------------------
   // Stop GPS UART
   // -------------------------------------------------------------------------
 
   SerialGPS.flush();
 
   SerialGPS.end();
 
   LOGF(
       "GPS UART -> off\n"
   );
 
   // -------------------------------------------------------------------------
   // WiFi off
   // -------------------------------------------------------------------------
 
   WiFi.disconnect(
       true
   );
 
   WiFi.mode(
       WIFI_OFF
   );
 
   // -------------------------------------------------------------------------
   // Calculate sleep
   // -------------------------------------------------------------------------
 
   const uint64_t sleepUs =
       static_cast<uint64_t>(
           g_sleepSeconds
       ) *
       1000000ULL;
 
   LOGF(
       "Deep Sleep: %lu seconds\n",
       static_cast<unsigned long>(
           g_sleepSeconds
       )
   );
 
   LOGF(
       "Deep Sleep: %.2f minutes\n",
       g_sleepSeconds / 60.0
   );
 
   LOGF(
       "====================================\n"
   );
 
   delay(100);
 
   // -------------------------------------------------------------------------
   // Configure timer wake-up
   // -------------------------------------------------------------------------
 
   esp_sleep_enable_timer_wakeup(
       sleepUs
   );
 
   // -------------------------------------------------------------------------
   // Deep Sleep
   // -------------------------------------------------------------------------
 
   esp_deep_sleep_start();
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
       "       COWTRACK LORA COLLAR         \n"
       "       BINARY PROTOCOL V1           \n"
       "       DEEP SLEEP MODE              \n"
       "====================================\n"
   );
 
   // -------------------------------------------------------------------------
   // Wake reason
   // -------------------------------------------------------------------------
 
   const esp_sleep_wakeup_cause_t wakeupReason =
       esp_sleep_get_wakeup_cause();
 
   if (
       wakeupReason ==
       ESP_SLEEP_WAKEUP_TIMER
   ) {
 
     LOGF(
         "Wake reason: TIMER\n"
     );
 
   } else {
 
     LOGF(
         "Wake reason: POWER/RESET/OTHER\n"
     );
   }
 
   // -------------------------------------------------------------------------
   // Configuration portal
   // -------------------------------------------------------------------------
 
   if (
       shouldOpenConfigPortal()
   ) {
 
     LOGF(
         "Opening configuration portal...\n"
     );
 
     runConfigPortal();
   }
 
   // -------------------------------------------------------------------------
   // Load settings
   // -------------------------------------------------------------------------
 
   loadSettings();
 
   LOGF(
       "Cow ID: %u\n",
       g_cowId
   );
 
   LOGF(
       "Sleep: %lu seconds\n",
       static_cast<unsigned long>(
           g_sleepSeconds
       )
   );
 
   LOGF(
       "Sleep: %.2f minutes\n",
       g_sleepSeconds / 60.0
   );
 
   LOGF(
       "LoRa frequency: %ld Hz\n",
       g_loraFrequencyHz
   );
 
   LOGF(
       "Hardware serial: %s\n",
       buildHardwareSerial().c_str()
   );
 
   LOGF(
       "Current sequence: %lu\n",
       static_cast<unsigned long>(
           g_sequence
       )
   );
 
   // -------------------------------------------------------------------------
   // GPS UART
   // -------------------------------------------------------------------------
 
   SerialGPS.begin(
       GPS_BAUD,
       SERIAL_8N1,
       GPS_RX_PIN,
       GPS_TX_PIN
   );
 
   LOGF(
       "GPS UART started at %lu baud\n",
       static_cast<unsigned long>(
           GPS_BAUD
       )
   );
 
   // -------------------------------------------------------------------------
   // LoRa
   // -------------------------------------------------------------------------
 
   if (
       !initLoRa()
   ) {
 
     LOGF(
         "FATAL: LoRa initialization failed\n"
     );
 
     // Se LoRa falhar, não fica acordado eternamente.
     // Dorme e tenta novamente no próximo ciclo.
 
     prepareForDeepSleep();
   }
 
   LOGF(
       "LoRa initialized\n"
   );
 
   LOGF(
       "Binary packet size: %u bytes\n",
       static_cast<unsigned int>(
           sizeof(LoRaPacket)
       )
   );
 
   // -------------------------------------------------------------------------
   // GPS
   // -------------------------------------------------------------------------
 
   const bool gpsOK =
       waitForGPSFix();
 
   // -------------------------------------------------------------------------
   // Send
   // -------------------------------------------------------------------------
 
   if (
       gpsOK
   ) {
 
     sendLocation();
 
   } else {
 
     LOGF(
         "No valid GPS position.\n"
         "Nothing transmitted this cycle.\n"
     );
   }
 
   // -------------------------------------------------------------------------
   // Sleep
   // -------------------------------------------------------------------------
 
   prepareForDeepSleep();
 }
 
 // ===========================================================================
 // LOOP
 // ===========================================================================
 //
 // Não será utilizado.
 //
 // O ESP32 entra em Deep Sleep dentro do setup().
 //
 // Quando acordar pelo timer:
 //
 //     setup()
 //        ↓
 //     GPS
 //        ↓
 //     LoRa
 //        ↓
 //     transmite
 //        ↓
 //     Deep Sleep novamente
 //
 // ===========================================================================
 
 void loop() {
 
   // Nunca deveria chegar aqui.
   //
   // Por segurança, se chegar,
   // entra em Deep Sleep.
 
   prepareForDeepSleep();
 }