#include <WiFi.h>
#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();
WiFiClient client;

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* host = "192.168.68.53";
const uint16_t port = 9001;
const uint8_t textHeaderSize = 14;

bool readExact(uint8_t* buffer, size_t length) {
  size_t received = 0;
  while (received < length) {
    while (client.connected() && client.available() == 0) {
      delay(5);
    }
    if (!client.connected()) {
      return false;
    }

    int count = client.read(buffer + received, length - received);
    if (count <= 0) {
      return false;
    }
    received += (size_t)count;
  }
  return true;
}

void setup() {
  Serial.begin(115200);
  tft.init();
  tft.setRotation(0);
  tft.invertDisplay(true);
  tft.fillScreen(TFT_BLACK);
  tft.setTextSize(2);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected. IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (!client.connected()) {
    Serial.println("Connecting to server...");
    if (!client.connect(host, port)) {
      delay(1000);
      return;
    }
    client.setTimeout(2000);
    Serial.println("Connected to server");
  }

  uint8_t header[textHeaderSize];
  if (!readExact(header, textHeaderSize)) {
    Serial.println("Server connection lost");
    client.stop();
    return;
  }

  if (header[0] != 'T' || header[1] != 'X' || header[2] != 'T' || header[3] != '1') {
    Serial.println("Invalid text packet");
    client.stop();
    return;
  }

  uint16_t textLength = (uint16_t)header[4] | ((uint16_t)header[5] << 8);
  uint16_t x = (uint16_t)header[8] | ((uint16_t)header[9] << 8);
  uint16_t y = (uint16_t)header[10] | ((uint16_t)header[11] << 8);
  uint16_t color = (uint16_t)header[12] | ((uint16_t)header[13] << 8);

  if (textLength == 0 || textLength > 64 || x >= 240 || y >= 240) {
    Serial.println("Invalid text packet data");
    client.stop();
    return;
  }

  char text[65];
  if (!readExact((uint8_t*)text, textLength)) {
    Serial.println("Failed to read text");
    client.stop();
    return;
  }
  text[textLength] = '\0';

  tft.fillScreen(TFT_BLACK);
  tft.setTextDatum(MC_DATUM);
  tft.setTextColor(color, TFT_BLACK);
  tft.drawString(text, x, y);
  Serial.printf("Displayed %s at (%u, %u), color 0x%04X\n", text, x, y, color);
}

