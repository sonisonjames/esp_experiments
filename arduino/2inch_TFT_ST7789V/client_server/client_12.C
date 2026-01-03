#include <TFT_eSPI.h>
TFT_eSPI tft = TFT_eSPI();

const int W = 160;
const int H = 120;
uint16_t pixel;

void setup() {
  // Use a slightly lower, more stable baud for this test
  Serial.begin(115200);
  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLUE); // Start Blue so we know the screen is ON

  delay(1000);
  tft.fillScreen(TFT_BLACK);
  Serial.write('R'); // Send "Ready" to PC
}

void loop() {
  if (Serial.available() > 0) {
    if (Serial.read() == 0xAA) { // Header check

      // Define a window in the center of the screen
      // 320w: (320-160)/2 = 80. 240h: (240-120)/2 = 60.
      tft.setAddrWindow(80, 60, W, H);

      tft.startWrite(); // Lock SPI for high-speed streaming
      for (int i = 0; i < (W * H); i++) {
        byte buf[2];
        // Wait for two bytes for each pixel
        while(Serial.available() < 2);
        Serial.readBytes(buf, 2);
        pixel = (buf[0] << 8) | buf[1];
        tft.pushColor(pixel);
      }
      tft.endWrite();

      Serial.write('R'); // Ask for next frame
    }
  }
}