#include <TFT_eSPI.h>
#include <SPI.h>

TFT_eSPI tft = TFT_eSPI();

struct Point {
  uint8_t x;
  uint8_t y;
};

// Define which points connect to each other (12 edges)
const uint8_t edges[12][2] = {
  {0,1}, {1,2}, {2,3}, {3,0}, // Front face
  {4,5}, {5,6}, {6,7}, {7,4}, // Back face
  {0,4}, {1,5}, {2,6}, {3,7}  // Connecting lines
};

void setup() {
  Serial.begin(115200);
  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);
}

void loop() {
  // Wait for Header (0xFF) + 16 bytes of data
  if (Serial.available() >= 17) {
    if (Serial.read() == 0xFF) {
      Point p[8];
      for (int i = 0; i < 8; i++) {
        p[i].x = Serial.read();
        p[i].y = Serial.read();
      }

      tft.startWrite(); // Start SPI transaction for speed
      tft.fillScreen(TFT_BLACK);

      // Draw lines based on the edge table
      for (int i = 0; i < 12; i++) {
        tft.drawLine(p[edges[i][0]].x, p[edges[i][1]].y, // Error fix: use correct indices
                     p[edges[i][0]].x, p[edges[i][1]].y, TFT_WHITE); // Wait, let's fix the logic below
      }

      // Corrected Drawing Loop
      for (int i = 0; i < 12; i++) {
        uint8_t startNode = edges[i][0];
        uint8_t endNode = edges[i][1];
        tft.drawLine(p[startNode].x, p[startNode].y, p[endNode].x, p[endNode].y, TFT_GREEN);
      }
      tft.endWrite();
    }
  }
}