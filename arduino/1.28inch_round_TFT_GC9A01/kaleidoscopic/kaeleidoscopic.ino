// Kaleidoscopic generative art on ESP32 + 240x240 TFT
// Requires: TFT_eSPI library, correctly configured for your display

#include <TFT_eSPI.h>
#include <SPI.h>

TFT_eSPI tft = TFT_eSPI();  // Invoke custom library

#define SCREEN_W 240
#define SCREEN_H 240
#define CX (SCREEN_W / 2)
#define CY (SCREEN_H / 2)

// Number of symmetric sectors (must divide 360). 8 => 45° steps.
#define SECTORS 36
#define HALF_SECTORS (SECTORS / 2)

// Number of mirrored strokes drawn per frame.
#define STROKES 18

void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.println("Kaleidoscope starting");

  tft.init();
  tft.setRotation(0);          // adjust for your orientation
  tft.fillScreen(TFT_BLACK);
  randomSeed(analogRead(34));  // noisy seed from floating pin
  Serial.println("Display initialized");
}

// Convert polar (r, angleDeg) around centre to screen x,y
void polarToCart(float r, float angleDeg, int &x, int &y) {
  float rad = angleDeg * DEG_TO_RAD;
  x = CX + (int)(r * cos(rad));
  y = CY + (int)(r * sin(rad));
}

// Draw one animated stroke and all its kaleidoscopic mirrors.
void drawKaleidoStroke(float r1, float r2, float baseAngle, uint16_t color) {
  int x1, y1, x2, y2;

  // Rotate and reflect the stroke around the centre.
  for (int s = 0; s < SECTORS; s++) {
    float angle = baseAngle + s * (360.0f / SECTORS);
    polarToCart(r1, angle, x1, y1);
    polarToCart(r2, angle + 3.0f, x2, y2);

    tft.drawLine(x1, y1, x2, y2, color);
    tft.drawLine(SCREEN_W - 1 - x1, y1, SCREEN_W - 1 - x2, y2, color);
  }
}

void loop() {
  static uint32_t frameNumber = 0;
  float time = frameNumber * 0.045f;

  //tft.fillScreen(TFT_BLACK);

  // Slowly breathing rings make the centre feel alive.
  for (int ring = 0; ring < 4; ring++) {
    float radius = 18.0f + ring * 22.0f + 8.0f * sin(time * 1.7f + ring);
    uint16_t ringColor = tft.color565(
      25 + ring * 20,
      50 + ring * 25,
      100 + ring * 30
    );
    tft.drawCircle(CX, CY, (int)radius, ringColor);
  }

  // Long rotating strokes create a much stronger kaleidoscope pattern.
  for (int stroke = 0; stroke < STROKES; stroke++) {
    float phase = stroke * 21.0f;
    float radius = 12.0f + 68.0f * (0.5f + 0.5f * sin(time * 1.3f + phase));
    float length = 10.0f + 25.0f * (0.5f + 0.5f * cos(time * 1.8f + phase));
    float angle = time * (18.0f + stroke * 0.7f) + phase;
    uint16_t color = tft.color565(
      80 + (stroke * 37) % 176,
      70 + (stroke * 61) % 176,
      100 + (stroke * 47) % 156
    );
    drawKaleidoStroke(radius, min(radius + length, 108.0f), angle, color);
  }

  frameNumber++;
  if ((frameNumber % 100) == 0) {
    Serial.print("Frames: ");
    Serial.println(frameNumber);
  }
  delay(10);
}