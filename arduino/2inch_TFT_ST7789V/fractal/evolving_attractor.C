#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>

#define TFT_CS   4
#define TFT_DC   16
#define TFT_RST  17
#define TFT_SCLK 18
#define TFT_MOSI 5

#define W 240
#define H 320

Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

float x = 0.1, y = 0.1;
float a, b, c, d;
float da, db, dc, dd;

uint32_t lastReset = 0;

void randomizeAttractor() {
  a = random(-200, 200) / 100.0;
  b = random(-200, 200) / 100.0;
  c = random(-200, 200) / 100.0;
  d = random(-200, 200) / 100.0;

  da = random(-5, 5) / 10000.0;
  db = random(-5, 5) / 10000.0;
  dc = random(-5, 5) / 10000.0;
  dd = random(-5, 5) / 10000.0;

  x = 0.1;
  y = 0.1;

  tft.fillScreen(ST77XX_BLACK);
}

void setup() {
  SPI.begin(TFT_SCLK, -1, TFT_MOSI, TFT_CS);
  tft.init(W, H);
  tft.setRotation(1);

  randomSeed(esp_random());
  randomizeAttractor();
}

void loop() {
  // Slowly evolve parameters
  a += da;
  b += db;
  c += dc;
  d += dd;

  // Draw many points per frame
  for (int i = 0; i < 2500; i++) {
    float nx = sin(a * y) + c * cos(a * x);
    float ny = sin(b * x) + d * cos(b * y);

    x = nx;
    y = ny;

    int px = W / 2 + x * 70;
    int py = H / 2 + y * 90;

    if (px >= 0 && px < W && py >= 0 && py < H) {
      uint16_t col = tft.color565(
        (uint8_t)(abs(x) * 120) + 50,
        (uint8_t)(abs(y) * 120) + 50,
        200
      );
      tft.drawPixel(px, py, col);
    }
  }

  // Auto-reset every ~15 seconds
  if (millis() - lastReset > 15000) {
    lastReset = millis();
    randomizeAttractor();
  }
}
