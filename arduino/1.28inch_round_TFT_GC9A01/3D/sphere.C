#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();

float lX = -0.3; // Light source X (-1.0 to 1.0)
float lY = -0.3; // Light source Y
float angle = 0;

void setup() {
  tft.init();
  tft.setRotation(0);
  tft.invertDisplay(true);
  tft.fillScreen(TFT_BLACK);
}

void drawShadedSphere(int centerX, int centerY, int radius, float lightX, float lightY) {
  // We draw the sphere from the outside in to create the shading layers
  for (int r = radius; r > 0; r--) {
    // Calculate intensity based on distance from the "light source"
    // This creates a 3D hemisphere effect
    float ratio = (float)r / radius;

    // Move the center of each circle slightly toward the light source
    int offsetX = centerX + (lightX * (radius - r) * 0.6);
    int offsetY = centerY + (lightY * (radius - r) * 0.6);

    // Dynamic Color: Transition from Dark Blue/Purple to Bright Cyan/White
    uint8_t red = 20 * (1.0 - ratio);
    uint8_t green = 150 * (1.0 - ratio) + 100 * ratio;
    uint8_t blue = 255 * (1.0 - ratio) + 200 * ratio;

    uint16_t color = tft.color565(red, green, blue);
    tft.drawCircle(offsetX, offsetY, r, color);

    // For a "Solid" look without gaps, we draw a few extra circles
    if (r % 2 == 0) tft.drawCircle(offsetX, offsetY, r-1, color);
  }
}

void loop() {
  // Orbiting light source logic
  lX = sin(angle);
  lY = cos(angle);

  // Draw the shaded sphere
  // Note: We don't fillScreen(BLACK) here because the sphere
  // redraws over itself, reducing flicker.
  drawShadedSphere(120, 120, 90, lX, lY);

  angle += 0.05;
  delay(10);
}