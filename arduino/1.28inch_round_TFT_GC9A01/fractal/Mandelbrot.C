/*
 * Infinite Mandelbrot Zoom Animation for GC9A01 Round Display
 *
 * Creates a mesmerizing infinite zoom into the Mandelbrot set
 * Optimized for ESP32 with double precision floating point
 *
 * Pin Configuration:
 * SCL -> GPIO 18
 * SDA -> GPIO 5
 * RST -> GPIO 17
 * DC  -> GPIO 16
 * CS  -> GPIO 4
 */

#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();

// Display dimensions
#define SCREEN_WIDTH 240
#define SCREEN_HEIGHT 240
#define CENTER_X 120
#define CENTER_Y 120

// Mandelbrot parameters
double centerX = -0.7463;  // Interesting zoom point
double centerY = 0.1102;   // Interesting zoom point
double zoom = 1.0;
double zoomFactor = 0.95;  // Zoom speed (smaller = faster zoom)
int maxIterations = 128;   // Detail level

// Frame buffer for smooth rendering
uint16_t frameBuffer[SCREEN_WIDTH];

// Color palette
uint16_t palette[256];

void setup() {
  Serial.begin(115200);
  Serial.println("Mandelbrot Infinite Zoom");

  // Initialize display
  tft.init();
  tft.setRotation(0);
  tft.fillScreen(TFT_BLACK);

  // Generate smooth color palette
  generatePalette();

  Serial.println("Starting infinite zoom...");
}

void loop() {
  // Render current frame
  renderMandelbrot();

  // Zoom in
  zoom *= zoomFactor;

  // Increase detail as we zoom in
  if (maxIterations < 512) {
    maxIterations += 1;
  }

  // Reset zoom after reaching extreme depth (to avoid floating point limits)
  if (zoom < 1e-12) {
    zoom = 1.0;
    maxIterations = 128;
    // Jump to a new interesting location
    jumpToNewLocation();
  }

  // Display stats
  if (random(100) < 5) {  // Print occasionally
    Serial.printf("Zoom: %.2e, Iterations: %d\n", zoom, maxIterations);
  }
}

void renderMandelbrot() {
  double aspectRatio = (double)SCREEN_WIDTH / (double)SCREEN_HEIGHT;

  // Render line by line for better performance
  for (int py = 0; py < SCREEN_HEIGHT; py++) {
    for (int px = 0; px < SCREEN_WIDTH; px++) {
      // Map pixel coordinates to Mandelbrot space
      // Use circular clipping for round display
      int dx = px - CENTER_X;
      int dy = py - CENTER_Y;
      double distFromCenter = sqrt(dx * dx + dy * dy);

      if (distFromCenter > CENTER_X) {
        frameBuffer[px] = TFT_BLACK;
        continue;
      }

      double x0 = centerX + (px - CENTER_X) * zoom * 4.0 / SCREEN_WIDTH;
      double y0 = centerY + (py - CENTER_Y) * zoom * 4.0 / SCREEN_HEIGHT;

      // Calculate Mandelbrot iteration
      int iteration = mandelbrot(x0, y0);

      // Map iteration to color
      if (iteration == maxIterations) {
        frameBuffer[px] = TFT_BLACK;
      } else {
        // Smooth coloring
        frameBuffer[px] = palette[iteration % 256];
      }
    }

    // Draw the line
    tft.pushImage(0, py, SCREEN_WIDTH, 1, frameBuffer);
  }
}

int mandelbrot(double x0, double y0) {
  double x = 0.0;
  double y = 0.0;
  int iteration = 0;

  while (x*x + y*y <= 4.0 && iteration < maxIterations) {
    double xtemp = x*x - y*y + x0;
    y = 2*x*y + y0;
    x = xtemp;
    iteration++;
  }

  return iteration;
}

void generatePalette() {
  // Generate a smooth rainbow-like palette
  for (int i = 0; i < 256; i++) {
    // Create smooth color transitions
    int r, g, b;

    if (i < 64) {
      r = i * 4;
      g = 0;
      b = 255 - i * 4;
    } else if (i < 128) {
      r = 255;
      g = (i - 64) * 4;
      b = 0;
    } else if (i < 192) {
      r = 255 - (i - 128) * 4;
      g = 255;
      b = 0;
    } else {
      r = 0;
      g = 255 - (i - 192) * 4;
      b = (i - 192) * 4;
    }

    // Convert to RGB565
    palette[i] = tft.color565(r, g, b);
  }
}

void jumpToNewLocation() {
  // Array of interesting Mandelbrot locations
  struct Location {
    double x;
    double y;
  };

  Location locations[] = {
    {-0.7463, 0.1102},   // Spiral
    {-0.7269, 0.1889},   // Seahorse valley
    {0.285, 0.01},       // Triple spiral
    {-0.748, 0.1},       // Double spiral
    {-0.16, 1.0405},     // Elephant valley
    {-0.7453, 0.1127},   // Another spiral
    {-0.75, 0.1},        // Classic zoom point
    {-0.7269, 0.1889},   // Seahorse
  };

  int numLocations = sizeof(locations) / sizeof(locations[0]);
  int randomIndex = random(numLocations);

  centerX = locations[randomIndex].x;
  centerY = locations[randomIndex].y;

  Serial.printf("Jumped to location: (%.4f, %.4f)\n", centerX, centerY);
}

/*
 * TFT_eSPI Configuration (User_Setup.h)
 *
 * Make sure your User_Setup.h has:
 *
 * #define GC9A01_DRIVER
 * #define TFT_WIDTH  240
 * #define TFT_HEIGHT 240
 *
 * #define TFT_SCLK 18
 * #define TFT_MOSI 5
 * #define TFT_RST  17
 * #define TFT_DC   16
 * #define TFT_CS   4
 *
 * #define SPI_FREQUENCY  40000000
 *
 * PERFORMANCE TIPS:
 * - The zoom will be smooth but not extremely fast due to double precision math
 * - Each frame takes ~1-2 seconds to render on ESP32
 * - For faster rendering, reduce maxIterations or screen resolution
 * - ESP32 has hardware floating point, so double precision works well
 * - The circular clipping keeps the fractal within the round display
 */