#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();
TFT_eSprite img = TFT_eSprite(&tft);

struct Point { int16_t x, y; };
Point p[4];
uint8_t shades[4];

// Sprite Dimensions
const int S_RES = 200;

void setup() {
  Serial.begin(921600); // High speed for larger data
  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);

  if (img.createSprite(S_RES, S_RES) == NULL) {
    Serial.println("Sprite too big! Try a smaller S_RES.");
  }
}

void loop() {
  // Header (1) + Points (8) + Shades (4) = 13 bytes
  if (Serial.available() >= 13) {
    if (Serial.read() == 0xFF) {
      for (int i = 0; i < 4; i++) {
        p[i].x = Serial.read();
        p[i].y = Serial.read();
      }
      for (int i = 0; i < 4; i++) shades[i] = Serial.read();

      img.fillSprite(TFT_BLACK);

      // Map PC coordinates (320x240) to Sprite coordinates (200x200)
      // PC center is 160,120. Sprite center is 100,100.
      for(int i=0; i<4; i++) {
        p[i].x = (p[i].x - 160) + (S_RES / 2);
        p[i].y = (p[i].y - 120) + (S_RES / 2);
      }

      // Draw faces
      img.fillTriangle(p[0].x, p[0].y, p[1].x, p[1].y, p[2].x, p[2].y, img.color565(shades[0], shades[0], shades[0]));
      img.fillTriangle(p[0].x, p[0].y, p[2].x, p[2].y, p[3].x, p[3].y, img.color565(shades[1], shades[1], shades[1]));
      img.fillTriangle(p[0].x, p[0].y, p[3].x, p[3].y, p[1].x, p[1].y, img.color565(shades[2], shades[2], shades[2]));
      img.fillTriangle(p[1].x, p[1].y, p[3].x, p[3].y, p[2].x, p[2].y, img.color565(shades[3], shades[3], shades[3]));

      // Push to center of the 320x240 screen
      img.pushSprite((320 - S_RES) / 2, (240 - S_RES) / 2);
    }
  }
}