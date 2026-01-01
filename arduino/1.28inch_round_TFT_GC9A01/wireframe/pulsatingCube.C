#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();

// Cube Vertices
float nodes[8][3] = {
  {-40,-40,-40}, {-40,-40,40}, {-40,40,-40}, {-40,40,40},
  {40,-40,-40}, {40,-40,40}, {40,40,-40}, {40,40,40}
};

int edges[12][2] = {
  {0,1}, {1,3}, {3,2}, {2,0}, {4,5}, {5,7}, {7,6}, {6,4}, {0,4}, {1,5}, {2,6}, {3,7}
};

int old_px[8], old_py[8];
float angleX = 0, angleY = 0, angleZ = 0;
float morphPhase = 0;

void setup() {
  tft.init();
  tft.setRotation(0);
  tft.invertDisplay(true);
  tft.fillScreen(TFT_BLACK);
}

void loop() {
  int px[8], py[8];

  // Calculate Morph Factor (oscillates between 0.6 and 1.6)
  float morph = 1.1 + sin(morphPhase) * 0.5;

  float radX = angleX * 0.0174533;
  float radY = angleY * 0.0174533;
  float radZ = angleZ * 0.0174533;

  for (int i = 0; i < 8; i++) {
    // Apply "Morph" to the raw coordinates
    float x = nodes[i][0] * morph;
    float y = nodes[i][1] * morph;
    float z = nodes[i][2] * morph;

    // Rotate Y
    float nx = x * cos(radY) - z * sin(radY);
    float nz = x * sin(radY) + z * cos(radY);
    // Rotate X
    float ny = y * cos(radX) - nz * sin(radX);
    nz = y * sin(radX) + nz * cos(radX);
    // Rotate Z (The "Shape-Shift" looks better with triple-axis rotation)
    float nx2 = nx * cos(radZ) - ny * sin(radZ);
    float ny2 = nx * sin(radZ) + ny * cos(radZ);

    // Project 3D to 2D
    float factor = 220 / (nz + 200);
    px[i] = (nx2 * factor) + 120;
    py[i] = (ny2 * factor) + 120;
  }

  // Erase Old Frame
  for (int i = 0; i < 12; i++) {
    tft.drawLine(old_px[edges[i][0]], old_py[edges[i][0]], old_px[edges[i][1]], old_py[edges[i][1]], TFT_BLACK);
  }

  // Draw New Frame with dynamic color
  // Use a simple color gradient based on the morph phase
  uint16_t color = (morph > 1.1) ? TFT_CYAN : TFT_MAGENTA;
  for (int i = 0; i < 12; i++) {
    tft.drawLine(px[edges[i][0]], py[edges[i][0]], px[edges[i][1]], py[edges[i][1]], color);
  }

  // Save for next erase
  for (int i = 0; i < 8; i++) {
    old_px[i] = px[i];
    old_py[i] = py[i];
  }

  // Increment all animations
  angleX += 0.04;
  angleY += 0.06;
  angleZ += 0.02;
  morphPhase += 0.05; // Controls the speed of the shape-shifting

  delay(10);
}