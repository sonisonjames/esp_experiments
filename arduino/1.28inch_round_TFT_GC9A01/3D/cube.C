#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();

// Cube Vertices
float vertices[8][3] = {
  {-40,-40, 40}, { 40,-40, 40}, { 40, 40, 40}, {-40, 40, 40},
  {-40,-40,-40}, { 40,-40,-40}, { 40, 40,-40}, {-40, 40,-40}
};

// Faces (defined by 4 vertex indices)
int faces[6][4] = {
  {0, 1, 2, 3}, {1, 5, 6, 2}, {5, 4, 7, 6},
  {4, 0, 3, 7}, {3, 2, 6, 7}, {1, 0, 4, 5}
};

float angleX = 0, angleY = 0;

void setup() {
  tft.init();
  tft.setRotation(0);
  tft.invertDisplay(true);
  tft.fillScreen(TFT_BLACK);
}

void loop() {
  float radX = angleX;
  float radY = angleY;
  int px[8], py[8];
  float rz[8]; // To store depth for culling

  // 1. Rotate and Project Points
  for (int i = 0; i < 8; i++) {
    float x = vertices[i][0];
    float y = vertices[i][1];
    float z = vertices[i][2];

    // Rotation
    float ny = y * cos(radX) - z * sin(radX);
    float nz = y * sin(radX) + z * cos(radX);
    float nx = x * cos(radY) - nz * sin(radY);
    nz = x * sin(radY) + nz * cos(radY);

    rz[i] = nz; // Store rotated Z for lighting/culling
    float factor = 240 / (nz + 200);
    px[i] = (nx * factor) + 120;
    py[i] = (ny * factor) + 120;
  }

  // 2. Clear Screen
  tft.fillScreen(TFT_BLACK);

  // 3. Draw Faces
  for (int i = 0; i < 6; i++) {
    // Basic Back-face Culling: Calculate if the face is pointing at us
    // (Cross product of two edges of the face)
    long v1x = px[faces[i][1]] - px[faces[i][0]];
    long v1y = py[faces[i][1]] - py[faces[i][0]];
    long v2x = px[faces[i][2]] - px[faces[i][0]];
    long v2y = py[faces[i][2]] - py[faces[i][0]];

    // If the cross product is positive, the face is visible
    if ((v1x * v2y - v1y * v2x) > 0) {
      // Shading based on average Z depth of the face
      float avgZ = (rz[faces[i][0]] + rz[faces[i][1]] + rz[faces[i][2]] + rz[faces[i][3]]) / 4.0;
      int intensity = map(avgZ, -40, 40, 50, 255);
      uint16_t color = tft.color565(0, intensity, intensity); // Teal shading

      // Draw filled face (approximated with two triangles)
      tft.fillTriangle(px[faces[i][0]], py[faces[i][0]], px[faces[i][1]], py[faces[i][1]], px[faces[i][2]], py[faces[i][2]], color);
      tft.fillTriangle(px[faces[i][0]], py[faces[i][0]], px[faces[i][2]], py[faces[i][2]], px[faces[i][3]], py[faces[i][3]], color);

      // Draw a white outline for a "clean" look
      tft.drawLine(px[faces[i][0]], py[faces[i][0]], px[faces[i][1]], py[faces[i][1]], TFT_WHITE);
      tft.drawLine(px[faces[i][1]], py[faces[i][1]], px[faces[i][2]], py[faces[i][2]], TFT_WHITE);
      tft.drawLine(px[faces[i][2]], py[faces[i][2]], px[faces[i][3]], py[faces[i][3]], TFT_WHITE);
      tft.drawLine(px[faces[i][3]], py[faces[i][3]], px[faces[i][0]], py[faces[i][0]], TFT_WHITE);
    }
  }

  angleX += 0.05;
  angleY += 0.03;
}