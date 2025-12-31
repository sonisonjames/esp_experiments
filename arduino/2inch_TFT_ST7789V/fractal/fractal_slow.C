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
#define G 80

Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

float A[G][G];
float B[G][G];

float DA = 1.0;
float DB = 0.5;
float FEED = 0.055;
float KILL = 0.062;

void setup() {
  SPI.begin(TFT_SCLK, -1, TFT_MOSI, TFT_CS);
  tft.init(W, H);
  tft.setRotation(1);
  tft.fillScreen(ST77XX_BLACK);

  randomSeed(esp_random());

  for (int x = 0; x < G; x++) {
    for (int y = 0; y < G; y++) {
      A[x][y] = 1.0;
      B[x][y] = 0.0;
    }
  }

  // Seed center
  for (int x = G/2 - 4; x < G/2 + 4; x++)
    for (int y = G/2 - 4; y < G/2 + 4; y++)
      B[x][y] = 1.0;
}

float laplace(float g[G][G], int x, int y) {
  float sum = 0;
  sum += g[x][y] * -1;
  sum += g[(x+1)%G][y] * 0.2;
  sum += g[(x+G-1)%G][y] * 0.2;
  sum += g[x][(y+1)%G] * 0.2;
  sum += g[x][(y+G-1)%G] * 0.2;
  sum += g[(x+1)%G][(y+1)%G] * 0.05;
  sum += g[(x+G-1)%G][(y+1)%G] * 0.05;
  sum += g[(x+1)%G][(y+G-1)%G] * 0.05;
  sum += g[(x+G-1)%G][(y+G-1)%G] * 0.05;
  return sum;
}

void loop() {
  for (int step = 0; step < 10; step++) {
    for (int x = 0; x < G; x++) {
      for (int y = 0; y < G; y++) {
        float a = A[x][y];
        float b = B[x][y];

        float reaction = a * b * b;

        A[x][y] = a + (DA * laplace(A, x, y) - reaction + FEED * (1 - a));
        B[x][y] = b + (DB * laplace(B, x, y) + reaction - (KILL + FEED) * b);

        A[x][y] = constrain(A[x][y], 0, 1);
        B[x][y] = constrain(B[x][y], 0, 1);
      }
    }
  }

  // Render
  for (int x = 0; x < G; x++) {
    for (int y = 0; y < G; y++) {
      uint8_t v = (uint8_t)(255 * (A[x][y] - B[x][y]));
      uint16_t c = tft.color565(v, v, v);

      int px = map(x, 0, G, 0, W);
      int py = map(y, 0, G, 0, H);

      tft.fillRect(px, py, W/G + 1, H/G + 1, c);
    }
  }
}
