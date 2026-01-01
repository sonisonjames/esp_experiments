#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();

const int rings = 12;
const int slices = 12;
const int num_vertices = rings * slices;
float v[num_vertices][3];

float angleX = 0, angleY = 0;
float hue = 0; // Color controller (0 to 360)

// Helper function to convert HSV to RGB565 for the display
uint16_t getRainbowColor(float h) {
  float r, g, b;
  float s = 1.0;
  float v = 1.0;

  int i = floor(h * 6);
  float f = h * 6 - i;
  float p = v * (1 - s);
  float q = v * (1 - f * s);
  float t = v * (1 - (1 - f) * s);

  switch (i % 6) {
    case 0: r = v, g = t, b = p; break;
    case 1: r = q, g = v, b = p; break;
    case 2: r = p, g = v, b = t; break;
    case 3: r = p, g = q, b = v; break;
    case 4: r = t, g = p, b = v; break;
    case 5: r = v, g = p, b = q; break;
  }
  return tft.color565(r * 255, g * 255, b * 255);
}

void setup() {
  tft.init();
  tft.setRotation(0);
  tft.invertDisplay(true);
  tft.fillScreen(TFT_BLACK);

  // Generate Sphere Vertices
  float radius = 65.0;
  int count = 0;
  for (int i = 0; i < rings; i++) {
    float phi = PI * (float)i / (rings - 1);
    for (int j = 0; j < slices; j++) {
      float theta = 2.0 * PI * (float)j / (slices);
      v[count][0] = radius * sin(phi) * cos(theta);
      v[count][1] = radius * sin(phi) * sin(theta);
      v[count][2] = radius * cos(phi);
      count++;
    }
  }
}

void loop() {
  int px[num_vertices], py[num_vertices];

  // 1. Calculate the color for this frame
  uint16_t mainColor = getRainbowColor(hue);
  hue += 0.005; // Change speed of color cycle
  if (hue > 1.0) hue = 0;

  // 2. Project Vertices
  for (int i = 0; i < num_vertices; i++) {
    float x = v[i][0];
    float y = v[i][1];
    float z = v[i][2];

    // X & Y Rotation
    float ny = y * cos(angleX) - z * sin(angleX);
    float nz = y * sin(angleX) + z * cos(angleX);
    float nx = x * cos(angleY) - nz * sin(angleY);
    nz = x * sin(angleY) + nz * cos(angleY);

    float factor = 240 / (nz + 160);
    px[i] = (nx * factor) + 120;
    py[i] = (ny * factor) + 120;
  }

  // 3. Draw Frame
  tft.fillScreen(TFT_BLACK); // Clear for next frame

  for (int i = 0; i < rings; i++) {
    for (int j = 0; j < slices; j++) {
      int curr = i * slices + j;
      int next_slice = i * slices + (j + 1) % slices;
      int next_ring = (i + 1) * slices + j;

      tft.drawLine(px[curr], py[curr], px[next_slice], py[next_slice], mainColor);

      if (i < rings - 1) {
        // Draw vertical lines in a slightly different shade for depth
        tft.drawLine(px[curr], py[curr], px[next_ring], py[next_ring], mainColor);
      }
    }
  }

  angleX += 0.03;
  angleY += 0.02;
}