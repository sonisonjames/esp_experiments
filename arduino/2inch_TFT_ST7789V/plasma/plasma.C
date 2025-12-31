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

void initSpi() {
  // Initialize SPI
  SPI.begin(TFT_SCLK, -1, TFT_MOSI, TFT_CS);
}

void initDisplay() {
  // Initialize display
  tft.init(240, 320);   // Width, Height
  tft.setRotation(0);  // Try 0–3 if orientation is wrong

    // Clear screen
  tft.fillScreen(ST77XX_BLACK);
}

void drawHello() {
  tft.setTextColor(ST77XX_WHITE);
  tft.setTextSize(2);
  tft.setCursor(20, 20);
  tft.println("ESP32 + ST7789");
  tft.println("Hello World");
}

void drawShapes() {
  tft.drawRect(0, 0, 240, 320, ST77XX_GREEN);
  tft.fillCircle(120, 180, 30, ST77XX_RED);
}

void init() {
  initSpi();
  initDisplay();
  //drawShapes();
}

void setup() {
  Serial.begin(115200);

  init();
}

uint16_t rainbow(int x) {
  x = x % 256;
  if (x < 85) return tft.color565(x * 3, 255 - x * 3, 0);
  if (x < 170) {
    x -= 85;
    return tft.color565(255 - x * 3, 0, x * 3);
  }
  x -= 170;
  return tft.color565(0, x * 3, 255 - x * 3);
}

void loop() {
  for (int y = 0; y < 320; y++) {
    uint16_t c = rainbow(y * 2);
    tft.drawFastHLine(0, y, 240, c);
  }
}
