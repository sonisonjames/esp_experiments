#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();

const int rings = 12;
const int slices = 12;
const int num_vertices = rings * slices;
float v[num_vertices][3]; // Store sphere vertices

float angleX = 0, angleY = 0;
int old_px[num_vertices], old_py[num_vertices];

void setup() {
  tft.init();
  tft.setRotation(0);
  tft.invertDisplay(true);
  tft.fillScreen(TFT_BLACK);

  // 1. Generate Sphere Vertices
  float radius = 60.0;
  int count = 0;
  for (int i = 0; i < rings; i++) {
    float phi = PI * (float)i / (rings - 1); // Latitude
    for (int j = 0; j < slices; j++) {
      float theta = 2.0 * PI * (float)j / (slices); // Longitude
      v[count][0] = radius * sin(phi) * cos(theta); // X
      v[count][1] = radius * sin(phi) * sin(theta); // Y
      v[count][2] = radius * cos(phi);              // Z
      count++;
    }
  }
}

void loop() {
  int px[num_vertices], py[num_vertices];
  float radX = angleX;
  float radY = angleY;

  // 2. Project Vertices
  for (int i = 0; i < num_vertices; i++) {
    float x = v[i][0];
    float y = v[i][1];
    float z = v[i][2];

    // Rotation
    float ny = y * cos(radX) - z * sin(radX);
    float nz = y * sin(radX) + z * cos(radX);
    float nx = x * cos(radY) - nz * sin(radY);
    nz = x * sin(radY) + nz * cos(radY);

    float factor = 240 / (nz + 150);
    px[i] = (nx * factor) + 120;
    py[i] = (ny * factor) + 120;
  }

  // 3. Clear Screen (Fastest for complex shapes)
  tft.fillScreen(TFT_BLACK);

  // 4. Draw Wireframe Lines
  for (int i = 0; i < rings; i++) {
    for (int j = 0; j < slices; j++) {
      int curr = i * slices + j;
      int next_slice = i * slices + (j + 1) % slices;
      int next_ring = (i + 1) * slices + j;

      // Draw horizontal rings
      tft.drawLine(px[curr], py[curr], px[next_slice], py[next_slice], TFT_CYAN);

      // Draw vertical slices
      if (i < rings - 1) {
        tft.drawLine(px[curr], py[curr], px[next_ring], py[next_ring], TFT_BLUE);
      }
    }
  }

  angleX += 0.04;
  angleY += 0.03;
}