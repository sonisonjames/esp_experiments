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

void setup() {
  SPI.begin(TFT_SCLK, -1, TFT_MOSI, TFT_CS);
  tft.init(W, H);
  tft.setRotation(1);
  tft.fillScreen(ST77XX_BLACK);

  randomSeed(esp_random());

  // Random attractor parameters
  a = random(-200, 200) / 100.0;
  b = random(-200, 200) / 100.0;
  c = random(-200, 200) / 100.0;
  d = random(-200, 200) / 100.0;
}

void loop() {
  // Draw MANY points per frame
  for (int i = 0; i < 3000; i++) {
    float nx = sin(a * y) + c * cos(a * x);
    float ny = sin(b * x) + d * cos(b * y);

    x = nx;
    y = ny;

    int px = W/2 + x * 60;
    int py = H/2 + y * 80;

    if (px >= 0 && px < W && py >= 0 && py < H) {
      tft.drawPixel(px, py, ST77XX_WHITE);
    }
  }
}
