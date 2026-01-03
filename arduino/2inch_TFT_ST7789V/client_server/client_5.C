#include <TFT_eSPI.h>
#include <SPI.h>

TFT_eSPI tft = TFT_eSPI();

struct Point {
  uint8_t x, y;
};

Point currP[4]; // Current frame coordinates
Point prevP[4]; // Previous frame coordinates
bool firstFrame = true;

void setup() {
  Serial.begin(115200);
  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);
}

void drawPyramid(Point p[], uint16_t color) {
  // We draw the 6 edges of the tetrahedron
  tft.drawLine(p[0].x, p[0].y, p[1].x, p[1].y, color);
  tft.drawLine(p[1].x, p[1].y, p[2].x, p[2].y, color);
  tft.drawLine(p[2].x, p[2].y, p[0].x, p[0].y, color);
  tft.drawLine(p[0].x, p[0].y, p[3].x, p[3].y, color);
  tft.drawLine(p[1].x, p[1].y, p[3].x, p[3].y, color);
  tft.drawLine(p[2].x, p[2].y, p[3].x, p[3].y, color);
}

void loop() {
  if (Serial.available() >= 9) {
    if (Serial.read() == 0xFF) {
      // 1. Store new points
      for (int i = 0; i < 4; i++) {
        currP[i].x = Serial.read();
        currP[i].y = Serial.read();
      }

      tft.startWrite();

      // 2. Erase the OLD object by drawing it in Black
      if (!firstFrame) {
        drawPyramid(prevP, TFT_BLACK);
      }

      // 3. Draw the NEW object in Green
      drawPyramid(currP, TFT_GREEN);

      tft.endWrite();

      // 4. Update previous points for next loop
      for (int i = 0; i < 4; i++) {
        prevP[i] = currP[i];
      }
      firstFrame = false;
    }
  }
}