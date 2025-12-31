#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>

// Pin definitions
#define TFT_CS   4
#define TFT_DC   16
#define TFT_RST  17
#define TFT_SCLK 18
#define TFT_MOSI 5

// Create display object
Adafruit_ST7789 tft = Adafruit_ST7789(
  TFT_CS, TFT_DC, TFT_RST
);

void setup() {
  Serial.begin(115200);

  // Initialize SPI
  SPI.begin(TFT_SCLK, -1, TFT_MOSI, TFT_CS);

  // Initialize display
  tft.init(240, 320);   // Width, Height
  tft.setRotation(1);  // Try 0–3 if orientation is wrong

  // Clear screen
  tft.fillScreen(ST77XX_BLACK);

  // Draw something
  tft.setTextColor(ST77XX_WHITE);
  tft.setTextSize(2);
  tft.setCursor(20, 20);
  tft.println("ESP32 + ST7789");
  tft.println("Hello World");

  tft.drawRect(10, 60, 200, 100, ST77XX_GREEN);
  tft.fillCircle(120, 180, 30, ST77XX_RED);
}

void loop() {
  // Nothing here
}
