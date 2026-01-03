#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();
TFT_eSprite img = TFT_eSprite(&tft);

struct Point { uint8_t x, y; };
Point v[64]; // Support up to 64 vertices

void setup() {
  Serial.begin(921600);
  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);
  img.createSprite(220, 220); // Maximized sprite
}

void loop() {
  if (Serial.available() > 0) {
    if (Serial.read() == 0xFF) { // Frame Header
      uint8_t numVertices = Serial.read();
      uint8_t numFaces = Serial.read();

      // 1. Read all vertex coordinates
      for (int i = 0; i < numVertices; i++) {
        v[i].x = Serial.read();
        v[i].y = Serial.read();
      }

      img.fillSprite(TFT_BLACK);

      // 2. Read faces and draw them immediately
      for (int i = 0; i < numFaces; i++) {
        uint8_t v1 = Serial.read();
        uint8_t v2 = Serial.read();
        uint8_t v3 = Serial.read();
        uint8_t shade = Serial.read();

        // Map to Sprite center (PC 160,120 -> Sprite 110,110)
        int x1 = v[v1].x - 160 + 110;
        int y1 = v[v1].y - 120 + 110;
        int x2 = v[v2].x - 160 + 110;
        int y2 = v[v2].y - 120 + 110;
        int x3 = v[v3].x - 160 + 110;
        int y3 = v[v3].y - 120 + 110;

        img.fillTriangle(x1, y1, x2, y2, x3, y3, img.color565(shade, shade, shade));
      }

      img.pushSprite(50, 10); // Center on 320x240 screen
    }
  }
}