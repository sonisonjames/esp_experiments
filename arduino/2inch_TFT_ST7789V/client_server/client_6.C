#include <TFT_eSPI.h>
#include <SPI.h>

TFT_eSPI tft = TFT_eSPI();

struct Point { uint8_t x, y; };
Point p[4];
uint8_t shades[4]; // Brightness 0-255 for each of the 4 faces

// Helper to convert 0-255 brightness to a grayscale RGB565 color
uint16_t getGray(uint8_t b) {
  return tft.color565(b, b, b);
}

void setup() {
  Serial.begin(115200);
  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);
}

void loop() {
  // Header (1) + Points (8) + Shades (4) = 13 bytes
  if (Serial.available() >= 13) {
    if (Serial.read() == 0xFF) {
      for (int i = 0; i < 4; i++) {
        p[i].x = Serial.read();
        p[i].y = Serial.read();
      }
      for (int i = 0; i < 4; i++) shades[i] = Serial.read();

      tft.startWrite();
      // For solid objects, a full clear is often safer, but we can
      // minimize flicker by only clearing the area around the object
      // if needed. For now, let's use a fast fill.
      tft.fillScreen(TFT_BLACK);

      // Draw the 4 faces of the Tetrahedron
      tft.fillTriangle(p[0].x, p[0].y, p[1].x, p[1].y, p[2].x, p[2].y, getGray(shades[0]));
      tft.fillTriangle(p[0].x, p[0].y, p[1].x, p[1].y, p[3].x, p[3].y, getGray(shades[1]));
      tft.fillTriangle(p[1].x, p[1].y, p[2].x, p[2].y, p[3].x, p[3].y, getGray(shades[2]));
      tft.fillTriangle(p[2].x, p[2].y, p[0].x, p[0].y, p[3].x, p[3].y, getGray(shades[3]));

      tft.endWrite();
    }
  }
}