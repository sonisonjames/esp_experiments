#include <TFT_eSPI.h>
#include <SPI.h>

TFT_eSPI tft = TFT_eSPI();

void setup() {
  Serial.begin(115200); // Lower speed for reliability
  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);
  tft.setTextColor(TFT_GREEN, TFT_BLACK);
  tft.setTextSize(2);

  tft.println("Waiting for PC...");
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming string until a newline character
    String incoming = Serial.readStringUntil('\n');

    tft.fillScreen(TFT_BLACK);
    tft.setCursor(0, 100);
    tft.printf("PC says: %s", incoming.c_str());

    // Send acknowledgment back to PC
    Serial.println("ACK");
  }
}