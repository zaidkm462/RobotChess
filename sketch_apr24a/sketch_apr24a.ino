#include <ESP8266WiFi.h>

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println();
  Serial.println("================================");
  Serial.println("ESP8266 WiFi Diagnostic");
  Serial.println("================================");

  // معلومات أساسية
  Serial.print("Chip ID: ");
  Serial.println(ESP.getChipId(), HEX);

  Serial.print("MAC: ");
  Serial.println(WiFi.macAddress());

  Serial.print("SDK: ");
  Serial.println(ESP.getSdkVersion());

  Serial.print("Core version: ");
  Serial.println(ESP.getCoreVersion());

  Serial.println();

  // ------------------------------------------------
  // TEST 1: WiFi Scan
  // ------------------------------------------------

  Serial.println("TEST 1: WiFi Scan");

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(500);

  int networks = WiFi.scanNetworks();

  Serial.print("Networks found: ");
  Serial.println(networks);

  for (int i = 0; i < networks; i++) {
    Serial.print(i);
    Serial.print(": ");
    Serial.print(WiFi.SSID(i));

    Serial.print(" | RSSI: ");
    Serial.print(WiFi.RSSI(i));

    Serial.print(" | Channel: ");
    Serial.println(WiFi.channel(i));
  }

  Serial.println();

  // ------------------------------------------------
  // TEST 2: AP
  // ------------------------------------------------

  Serial.println("TEST 2: Access Point");

  WiFi.mode(WIFI_AP_STA);

  bool apResult = WiFi.softAP(
    "ESP8266_TEST",
    nullptr,
    1,
    false,
    4
  );

  Serial.print("AP result: ");
  Serial.println(apResult ? "SUCCESS" : "FAILED");

  Serial.print("AP IP: ");
  Serial.println(WiFi.softAPIP());

  Serial.print("AP MAC: ");
  Serial.println(WiFi.softAPmacAddress());

  Serial.print("Station MAC: ");
  Serial.println(WiFi.macAddress());

  Serial.println();

  // ------------------------------------------------
  // TEST 3: Scan while AP is running
  // ------------------------------------------------

  Serial.println("TEST 3: Scan while AP is running");

  int networks2 = WiFi.scanNetworks();

  Serial.print("Networks found: ");
  Serial.println(networks2);

  for (int i = 0; i < networks2; i++) {
    Serial.print(i);
    Serial.print(": ");
    Serial.print(WiFi.SSID(i));

    Serial.print(" | RSSI: ");
    Serial.print(WiFi.RSSI(i));

    Serial.print(" | Channel: ");
    Serial.println(WiFi.channel(i));
  }

  Serial.println();
  Serial.println("================================");
  Serial.println("Diagnostic finished");
  Serial.println("================================");
}

void loop() {
  Serial.print("AP clients: ");
  Serial.println(WiFi.softAPgetStationNum());

  delay(3000);
}