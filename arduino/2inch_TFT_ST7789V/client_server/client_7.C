#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();
TFT_eSprite img = TFT_eSprite(&tft); // Create a Sprite object

struct Point { int16_t x, y; };
Point p[4];
uint8_t shades[4];

void setup() {
  Serial.begin(115200);
  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);

  // Create a sprite that is 160x160 (uses ~51KB RAM)
  // This fits easily and covers the center of the screen
  img.createSprite(160, 160);
}

void loop() {
  if (Serial.available() >= 13) {
    if (Serial.read() == 0xFF) {
      for (int i = 0; i < 4; i++) {
        p[i].x = Serial.read();
        p[i].y = Serial.read();
      }
      for (int i = 0; i < 4; i++) shades[i] = Serial.read();

      // 1. Draw EVERYTHING to the Sprite (off-screen buffer)
      img.fillSprite(TFT_BLACK); // This happens in RAM (invisible)

      // Adjust coordinates to sprite-space (centered)
      int offset = 80;
      for(int i=0; i<4; i++) {
        p[i].x = (p[i].x - 160) + offset;
        p[i].y = (p[i].y - 120) + offset;
      }

      // 2. Draw the solid faces to the Sprite
      img.fillTriangle(p[0].x, p[0].y, p[1].x, p[1].y, p[2].x, p[2].y, img.color565(shades[0], shades[0], shades[0]));
      img.fillTriangle(p[0].x, p[0].y, p[2].x, p[2].y, p[3].x, p[3].y, img.color565(shades[1], shades[1], shades[1]));
      img.fillTriangle(p[0].x, p[0].y, p[3].x, p[3].y, p[1].x, p[1].y, img.color565(shades[2], shades[2], shades[2]));
      img.fillTriangle(p[1].x, p[1].y, p[3].x, p[3].y, p[2].x, p[2].y, img.color565(shades[3], shades[3], shades[3]));

      // 3. Push the entire RAM buffer to the screen at once
      img.pushSprite(80, 40);
    }
  }
}