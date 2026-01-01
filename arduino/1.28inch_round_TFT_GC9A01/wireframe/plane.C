#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();

// F-15 Simplified Vertices (X, Y, Z)
// Nose is at Z=80, Tail is at Z=-60
float nodes[11][3] = {
  {0, 0, 80},    // 0: Nose
  {0, 5, 20},    // 1: Top of Cockpit
  {-50, 0, -20}, // 2: Left Wing Tip
  {50, 0, -20},  // 3: Right Wing Tip
  {-15, 0, 30},  // 4: Left Intake/Wing Root
  {15, 0, 30},   // 5: Right Intake/Wing Root
  {-15, 0, -60}, // 6: Left Engine/Tail base
  {15, 0, -60},  // 7: Right Engine/Tail base
  {-15, 25, -70},// 8: Left Vertical Stabilizer Tip
  {15, 25, -70}, // 9: Right Vertical Stabilizer Tip
  {0, -5, 0}     // 10: Bottom fuselage belly
};

// F-15 Edges (Connecting the dots)
int edges[17][2] = {
  {0, 1}, {1, 4}, {1, 5},     // Cockpit & Nose
  {4, 2}, {2, 6}, {6, 4},     // Left Wing
  {5, 3}, {3, 7}, {7, 5},     // Right Wing
  {6, 7},                     // Back merge
  {6, 8}, {8, 7},             // Left Tail Fin
  {7, 9}, {9, 6},             // Right Tail Fin
  {0, 10}, {10, 6}, {10, 7}   // Underbelly
};

int old_px[11], old_py[11];
float angleX = -0.5, angleY = 0, angleZ = 0;

void setup() {
  tft.init();
  tft.setRotation(0);
  tft.invertDisplay(true);
  tft.fillScreen(TFT_BLACK);

  // Draw a static "Targeting" ring for a cockpit feel
  tft.drawCircle(120, 120, 118, 0x2104);
}

void loop() {
  int px[11], py[11];
  float radX = angleX;
  float radY = angleY;
  float radZ = angleZ;

  // 1. Rotate and Project Vertices
  for (int i = 0; i < 11; i++) {
    float x = nodes[i][0];
    float y = nodes[i][1];
    float z = nodes[i][2];

    // Y Rotation
    float nx = x * cos(radY) - z * sin(radY);
    float nz = x * sin(radY) + z * cos(radY);
    // X Rotation
    float ny = y * cos(radX) - nz * sin(radX);
    nz = y * sin(radX) + nz * cos(radX);
    // Z Rotation
    float nx2 = nx * cos(radZ) - ny * sin(radZ);
    float ny2 = nx * sin(radZ) + ny * cos(radZ);

    // Perspective Projection (Adjusted for F15 length)
    float factor = 240 / (nz + 180);
    px[i] = (nx2 * factor) + 120;
    py[i] = (ny2 * factor) + 120;
  }

  // 2. Erase Old Plane
  for (int i = 0; i < 17; i++) {
    tft.drawLine(old_px[edges[i][0]], old_py[edges[i][0]],
                 old_px[edges[i][1]], old_py[edges[i][1]], TFT_BLACK);
  }

  // 3. Draw New Plane (Neon Cyan)
  for (int i = 0; i < 17; i++) {
    tft.drawLine(px[edges[i][0]], py[edges[i][0]],
                 px[edges[i][1]], py[edges[i][1]], TFT_CYAN);
  }

  // 4. Update Previous Coords
  for (int i = 0; i < 11; i++) {
    old_px[i] = px[i];
    old_py[i] = py[i];
  }

  // Rotation speed - slow it down for a majestic feel
  angleY += 0.03;
  angleZ += 0.01;

  delay(15);
}