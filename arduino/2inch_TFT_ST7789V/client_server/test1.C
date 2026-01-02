#include <TFT_eSPI.h>
#include <SPI.h>

/*
    This is a test program to check if the User_Setup.h
    configuration for a 2.0 inch TFT with ST7789V driver
    is correct.
*/

TFT_eSPI tft = TFT_eSPI();

void setup() {
  Serial.begin(115200);
  Serial.println("Starting TFT Test...");

  tft.init();
  tft.setRotation(1); // Landscape

  // Fill screen with a bright color to test the backlight/LCD
  tft.fillScreen(TFT_BLUE);

  // Draw some text
  tft.setTextColor(TFT_WHITE);
  tft.setTextSize(3);
  tft.setCursor(20, 100);
  tft.println("Hello ESP32!");

  tft.drawRect(0, 0, 320, 240, TFT_RED); // Draw a border
  Serial.println("Test complete. You should see a blue screen.");
}

void loop() {
  // Blink the border to show the ESP32 is alive
  tft.drawRect(0, 0, 320, 240, TFT_RED);
  delay(500);
  tft.drawRect(0, 0, 320, 240, TFT_GREEN);
  delay(500);
}