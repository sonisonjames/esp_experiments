#include <TFT_eSPI.h>
#include <SPI.h>

TFT_eSPI tft = TFT_eSPI();

void setup() {
  // Use the maximum stable baud rate for the ESP32
  Serial.begin(921600); 
  tft.init();
  tft.setRotation(1); // Landscape
  tft.fillScreen(TFT_BLACK);
  
  // Set the address window to the full screen once
  tft.setAddrWindow(0, 0, 320, 240);
}

void loop() {
  // We expect 2 bytes per pixel (RGB565)
  if (Serial.available() >= 2) {
    uint8_t hibyte = Serial.read();
    uint8_t lobyte = Serial.read();
    uint16_t color = (hibyte << 8) | lobyte;
    tft.pushColor(color);
  }
}