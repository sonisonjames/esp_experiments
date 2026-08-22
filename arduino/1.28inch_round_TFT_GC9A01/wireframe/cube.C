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

// Arrays to store the coordinates from the PREVIOUS frame so we can erase them
int old_px[8], old_py[8];
float angleX = 0, angleY = 0;

void setup() {
  tft.init();
  tft.setRotation(0);
  tft.invertDisplay(true);
  tft.fillScreen(TFT_BLACK);
}

void loop() {
  int px[8], py[8];
  float radX = angleX * 0.0174533;
  float radY = angleY * 0.0174533;

  // 1. Calculate New Positions
  for (int i = 0; i < 8; i++) {
    float x = nodes[i][0];
    float y = nodes[i][1];
    float z = nodes[i][2];

    // Rotate Y
    float nx = x * cos(radY) - z * sin(radY);
    float nz = x * sin(radY) + z * cos(radY);
    // Rotate X
    float ny = y * cos(radX) - nz * sin(radX);
    nz = y * sin(radX) + nz * cos(radX);

    // Project 3D to 2D
    float factor = 200 / (nz + 150);
    px[i] = (nx * factor) + 120;
    py[i] = (ny * factor) + 120;
  }

  // 2. Erase Old Cube (Draw the old edges in Black)
  for (int i = 0; i < 12; i++) {
    tft.drawLine(old_px[edges[i][0]], old_py[edges[i][0]], old_px[edges[i][1]], old_py[edges[i][1]], TFT_BLACK);
  }

  // 3. Draw New Cube (Draw the current edges in Green)
  for (int i = 0; i < 12; i++) {
    tft.drawLine(px[edges[i][0]], py[edges[i][0]], px[edges[i][1]], py[edges[i][1]], TFT_GREEN);
  }

  // 4. Update "Old" coordinates for the next loop
  for (int i = 0; i < 8; i++) {
    old_px[i] = px[i];
    old_py[i] = py[i];
  }

  angleX += 0.05; // Control speed
  angleY += 0.03;

  // A tiny delay helps reduce "ghosting" on some LCDs
  delay(5);
}