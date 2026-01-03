#include <TFT_eSPI.h>
#include <SPI.h>

TFT_eSPI tft = TFT_eSPI();

// Structure to hold a 2D point
struct Point {
  int16_t x;
  int16_t y;
};

void setup() {
  Serial.begin(115200);
  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);
  tft.setCursor(0,0);
  tft.println("Waiting for Cube Data...");
}

void loop() {
  // We expect 8 points (16 bytes) for a cube
  if (Serial.available() >= 16) {
    Point p[8];
    for (int i = 0; i < 8; i++) {
      p[i].x = Serial.read(); // Reading simplified bytes (0-255)
      p[i].y = Serial.read();
    }

    tft.fillScreen(TFT_BLACK); // Clear screen

    // Draw the 12 edges of a cube
    // Front face
    tft.drawLine(p[0].x, p[0].y, p[1].x, p[1].y, TFT_WHITE);
    tft.drawLine(p[1].x, p[1].y, p[2].x, p[2].y, TFT_WHITE);
    tft.drawLine(p[2].x, p[2].y, p[3].x, p[3].y, TFT_WHITE);
    tft.drawLine(p[3].x, p[3].y, p[0].x, p[0].y, TFT_WHITE);

    // Back face
    tft.drawLine(p[4].x, p[4].y, p[5].x, p[5].y, TFT_CYAN);
    tft.drawLine(p[5].x, p[5].y, p[6].x, p[6].y, TFT_CYAN);
    tft.drawLine(p[6].x, p[6].y, p[7].x, p[7].y, TFT_CYAN);
    tft.drawLine(p[7].x, p[7].y, p[4].x, p[4].y, TFT_CYAN);

    // Connecting lines
    for (int i = 0; i < 4; i++) {
      tft.drawLine(p[i].x, p[i].y, p[i+4].x, p[i+4].y, TFT_YELLOW);
    }
  }
}