#include <WiFi.h>
#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* host = "192.168.68.53";
const int port = 9001;

const uint8_t TEXT_MAGIC[4] = {'T', 'X', 'T', '1'};

WiFiClient client;

bool readExact(uint8_t* buf, size_t len) {
  size_t got = 0;
  while (got < len) {
    while (client.connected() && client.available() == 0) {
      delay(5);
    }

    if (!client.connected()) {
      return false;
    }

    int n = client.read(buf + got, len - got);
    if (n <= 0) {
      return false;
    }
    got += (size_t)n;
  }
  return true;
}

void setup() {
  Serial.begin(115200);

  tft.init();
  tft.setRotation(0);
  tft.invertDisplay(true);
  tft.fillScreen(TFT_BLACK);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Connected. IP: ");
  Serial.println(WiFi.localIP());

  tft.fillScreen(TFT_BLACK);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.setTextSize(1);
  tft.setCursor(10, 10);
  tft.print("Ready for text");

  delay(1000);
}

void loop() {
  if (!client.connected()) {
    Serial.println("Connecting to server...");
    if (!client.connect(host, port)) {
      delay(500);
      return;
    }
    Serial.println("Connected to server");
    client.setTimeout(2000);
  }

  uint8_t header[8];
  if (!readExact(header, 8)) {
    Serial.println("Failed to read header");
    client.stop();
    return;
  }

  bool isMagicText = (header[0] == TEXT_MAGIC[0]) &&
                     (header[1] == TEXT_MAGIC[1]) &&
                     (header[2] == TEXT_MAGIC[2]) &&
                     (header[3] == TEXT_MAGIC[3]);

  if (!isMagicText) {
    Serial.printf("Bad magic: %02X %02X %02X %02X\n",
                  header[0], header[1], header[2], header[3]);
    client.stop();
    return;
  }

  uint16_t textLen = (uint16_t)header[4] | ((uint16_t)header[5] << 8);
  uint8_t msgId = header[6];

  if (textLen > 256) {
    Serial.printf("Text too long: %u\n", textLen);
    client.stop();
    return;
  }

  uint8_t textBuf[257];
  if (!readExact(textBuf, textLen)) {
    Serial.println("Failed to read text");
    client.stop();
    return;
  }

  textBuf[textLen] = '\0';

  tft.fillScreen(TFT_BLACK);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.setTextSize(2);
  tft.setCursor(10, 20);
  tft.print((const char*)textBuf);

  tft.setTextSize(1);
  tft.setTextColor(TFT_CYAN, TFT_BLACK);
  tft.setCursor(10, 100);
  tft.printf("Msg %u", msgId);

  Serial.printf("Text msg %u: %s\n", msgId, (const char*)textBuf);
}
