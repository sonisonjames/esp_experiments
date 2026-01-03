#include <TFT_eSPI.h>
#include <SPI.h>

TFT_eSPI tft = TFT_eSPI();

struct Point {
  int16_t x;
  int16_t y;
};

void setup() {
  Serial.begin(115200);
  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);
}

void loop() {
  // 1 Header + 4 points (8 bytes) = 9 bytes total
  if (Serial.available() >= 9) {
    if (Serial.read() == 0xFF) {
      Point p[4];
      for (int i = 0; i < 4; i++) {
        p[i].x = Serial.read();
        p[i].y = Serial.read();
      }

      tft.startWrite();
      tft.fillScreen(TFT_BLACK);

      // Define the 4 faces of a tetrahedron
      // Face 1: Bottom (Blue-ish)
      tft.fillTriangle(p[0].x, p[0].y, p[1].x, p[1].y, p[2].x, p[2].y, 0x001F);
      // Face 2: Left (Red-ish)
      tft.fillTriangle(p[0].x, p[0].y, p[1].x, p[1].y, p[3].x, p[3].y, 0xF800);
      // Face 3: Right (Green-ish)
      tft.fillTriangle(p[1].x, p[1].y, p[2].x, p[2].y, p[3].x, p[3].y, 0x07E0);
      // Face 4: Back (Yellow-ish)
      tft.fillTriangle(p[2].x, p[2].y, p[0].x, p[0].y, p[3].x, p[3].y, 0xFFE0);

      tft.endWrite();
    }
  }
}