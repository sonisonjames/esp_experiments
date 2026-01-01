#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();

// 12 Vertices for a solid simplified pot
float v[12][3] = {
  {0, 30, 0},    // 0: Top
  {-25, 10, 25}, {25, 10, 25}, {25, 10, -25}, {-25, 10, -25}, // Mid rim
  {-20, -20, 20}, {20, -20, 20}, {20, -20, -20}, {-20, -20, -20}, // Bottom rim
  {-45, 15, 0},  // 9: Spout tip
  {45, 15, 0},   // 10: Handle outer
  {0, -30, 0}    // 11: Base
};

// Defined triangles (Faces) - 3 vertex indices each
int faces[16][3] = {
  {0, 1, 2}, {0, 2, 3}, {0, 3, 4}, {0, 4, 1}, // Top cap
  {1, 5, 2}, {2, 5, 6}, {2, 6, 3}, {3, 6, 7}, // Sides
  {3, 7, 4}, {4, 7, 8}, {4, 8, 1}, {1, 8, 5}, // Sides
  {5, 11, 6}, {6, 11, 7}, {7, 11, 8}, {8, 11, 5} // Bottom cap
};

float angleY = 0;
float angleX = 0.4; // Fixed tilt to see the 3D shape better

void setup() {
  tft.init();
  tft.setRotation(0);
  tft.invertDisplay(true);
  tft.fillScreen(TFT_BLACK);
}

void loop() {
  int px[12], py[12];
  float rz[12];

  // 1. Project Vertices
  for (int i = 0; i < 12; i++) {
    float x = v[i][0];
    float y = v[i][1];
    float z = v[i][2];

    // Rotate Y
    float nx = x * cos(angleY) - z * sin(angleY);
    float nz = x * sin(angleY) + z * cos(angleY);
    // Rotate X (Tilt)
    float ny = y * cos(angleX) - nz * sin(angleX);
    nz = y * sin(angleX) + nz * cos(angleX);

    float factor = 240 / (nz + 180);
    px[i] = (nx * factor) + 120;
    py[i] = (ny * factor) + 120;
    rz[i] = nz; // Store depth
  }

  tft.fillScreen(TFT_BLACK);

  // 2. Draw Faces with Back-Face Culling
  for (int i = 0; i < 16; i++) {
    // Check face orientation (Normal calculation)
    int x1 = px[faces[i][0]], y1 = py[faces[i][0]];
    int x2 = px[faces[i][1]], y2 = py[faces[i][1]];
    int x3 = px[faces[i][2]], y3 = py[faces[i][2]];

    long winding = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1);

    if (winding > 0) {
      // Shading based on depth
      float avgZ = (rz[faces[i][0]] + rz[faces[i][1]] + rz[faces[i][2]]) / 3.0;
      int lum = map(avgZ, -30, 30, 255, 50); // Bright when close

      uint16_t color = tft.color565(lum, lum / 2, 0); // Golden/Bronze shade
      tft.fillTriangle(x1, y1, x2, y2, x3, y3, color);

      // Optional: draw lines to define edges clearly
      tft.drawTriangle(x1, y1, x2, y2, x3, y3, tft.color565(lum+20, lum/2+20, 20));
    }
  }

  angleY += 0.08;
  // delay(5); // Optional delay
}