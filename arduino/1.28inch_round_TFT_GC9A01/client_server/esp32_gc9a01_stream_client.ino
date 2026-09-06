#include <WiFi.h>
#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();
WiFiClient client;

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* host = "192.168.68.53";
const uint16_t port = 9001;
const uint8_t textHeaderSize = 14;
const uint16_t screenWidth = 240;
const uint16_t screenHeight = 240;
const uint16_t imageChunkPixels = 240 * 8;
uint16_t imageChunk[imageChunkPixels];

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

  uint8_t magic[4];
  if (!readExact(magic, sizeof(magic))) {
    Serial.println("Server connection lost");
    client.stop();
    return;
  }

  if (magic[0] == 'I' && magic[1] == 'M' && magic[2] == 'G' && magic[3] == '1') {
    handleImagePacket();
    return;
  }

  if (magic[0] != 'T' || magic[1] != 'X' || magic[2] != 'T' || magic[3] != '1') {
    Serial.println("Invalid packet");
    client.stop();
    return;
  }

  uint8_t header[textHeaderSize - 4];
  if (!readExact(header, sizeof(header))) {
    Serial.println("Failed to read text header");
    client.stop();
    return;
  }

  uint16_t textLength = (uint16_t)header[0] | ((uint16_t)header[1] << 8);
  uint16_t x = (uint16_t)header[4] | ((uint16_t)header[5] << 8);
  uint16_t y = (uint16_t)header[6] | ((uint16_t)header[7] << 8);
  uint16_t color = (uint16_t)header[8] | ((uint16_t)header[9] << 8);

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

void handleImagePacket() {
  uint8_t header[4];
  if (!readExact(header, sizeof(header))) {
    Serial.println("Failed to read image header");
    client.stop();
    return;
  }

  uint16_t width = (uint16_t)header[0] | ((uint16_t)header[1] << 8);
  uint16_t height = (uint16_t)header[2] | ((uint16_t)header[3] << 8);
  if (width != screenWidth || height != screenHeight) {
    Serial.printf("Unsupported image size: %ux%u\n", width, height);
    client.stop();
    return;
  }

  // Keep partially received rows hidden until the complete frame is ready.
  tft.writecommand(TFT_DISPOFF);
  tft.startWrite();
  tft.setAddrWindow(0, 0, screenWidth, screenHeight);

  for (uint16_t row = 0; row < screenHeight; row += 8) {
    const uint16_t rows = min((uint16_t)8, (uint16_t)(screenHeight - row));
    const size_t chunkBytes = (size_t)screenWidth * rows * sizeof(uint16_t);
    if (!readExact((uint8_t*)imageChunk, chunkBytes)) {
      tft.endWrite();
      Serial.println("Failed to read image data");
      client.stop();
      return;
    }
    tft.pushColors(imageChunk, screenWidth * rows, true);
  }
  tft.endWrite();
  tft.writecommand(TFT_DISPON);

  Serial.println("Displayed static full-screen image");

  while (true) {
    delay(1000);
  }
}

