#include <TFT_eSPI.h>
TFT_eSPI tft = TFT_eSPI();

const int W = 160;
const int H = 120;
uint16_t lineBuffer[W]; 

void setup() {
  Serial.begin(921600);
  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);
  Serial.write('R'); // Initial request
}

void loop() {
  if (Serial.available() > 0) {
    if (Serial.read() == 0xAA) {
      for (int y = 0; y < H; y++) {
        // Read one 160-pixel line
        Serial.readBytes((char*)lineBuffer, W * 2);
        
        // Draw the line twice (vertical scaling)
        // pushImage handles the horizontal scaling if we set window width
        tft.pushImage(0, y * 2, W, 1, lineBuffer);
        tft.pushImage(0, y * 2 + 1, W, 1, lineBuffer);
      }
      Serial.write('R'); // Request next frame
    }
  }
}