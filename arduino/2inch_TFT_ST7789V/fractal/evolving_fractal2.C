#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>
#include <math.h>

#define TFT_CS   4
#define TFT_DC   16
#define TFT_RST  17
#define TFT_SCLK 18
#define TFT_MOSI 5

#define W 240
#define H 320

Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

float x = 0.01, y = 0.01;
float a, b, c, d;
float da, db, dc, dd;

uint32_t lastReset = 0;

void randomizeAttractor() {
  a = random(-200, 200) / 100.0;
  b = random(-200, 200) / 100.0;
  c = random(-200, 200) / 100.0;
  d = random(-200, 200) / 100.0;

  da = random(-5, 5) / 15000.0;
  db = random(-5, 5) / 15000.0;
  dc = random(-5, 5) / 15000.0;
  dd = random(-5, 5) / 15000.0;

  x = 0.01;
  y = 0.01;

  tft.fillScreen(ST77XX_BLACK);
}

inline void plot(int px, int py, uint16_t c) {
  if (px < 0 || px >= W || py < 0 || py >= H) return;

  // 2x2 thickness
  tft.drawPixel(px, py, c);
  tft.drawPixel(px + 1, py, c);
  tft.drawPixel(px, py + 1, c);
  tft.drawPixel(px + 1, py + 1, c);
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

  for (int i = 0; i < 4000; i++) {
    float nx = sin(a * y) + c * cos(a * x);
    float ny = sin(b * x) + d * cos(b * y);

    x = nx;
    y = ny;

    // Scale UP aggressively (key fix)
    int px = W / 2 + x * 110;
    int py = H / 2 + y * 140;

    uint8_t r = (uint8_t)(fabs(x) * 200) + 40;
    uint8_t g = (uint8_t)(fabs(y) * 200) + 40;
    uint8_t bcol = 180;

    uint16_t col = tft.color565(r, g, bcol);

    // Main point
    plot(px, py, col);

    // Kaleidoscope symmetry
    plot(W - px - 1, py, col);
    plot(px, H - py - 1, col);
    plot(W - px - 1, H - py - 1, col);

    // Subtle jitter for density
    plot(px + (i & 1), py - (i & 1), col);
  }

  // Periodic refresh
  if (millis() - lastReset > 18000) {
    lastReset = millis();
    randomizeAttractor();
  }
}
