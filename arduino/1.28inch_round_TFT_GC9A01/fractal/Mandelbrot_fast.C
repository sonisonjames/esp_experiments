/*
 * FAST Infinite Mandelbrot Zoom (Optimized Single Core)
 *
 * Optimizations:
 * - Lower resolution rendering (adjustable)
 * - Reduced iterations for speed
 * - Faster zoom rate
 * - Line-by-line rendering (no frame buffer needed)
 * - Optimized math
 *
 * Pin Configuration:
 * SCL -> GPIO 18, SDA -> GPIO 5, RST -> GPIO 17, DC -> GPIO 16, CS -> GPIO 4
 */

#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();

// Display dimensions
#define SCREEN_WIDTH 240
#define SCREEN_HEIGHT 240
#define CENTER_X 120
#define CENTER_Y 120

// Speed vs Quality (lower = faster)
#define PIXEL_SIZE 2      // Render 2x2 pixel blocks (1=full quality, 2=4x faster, 3=9x faster)
#define MAX_ITER 48       // Lower = faster but less detail (was 128)

// Mandelbrot parameters
double centerX = -0.7463;
double centerY = 0.1102;
double zoom = 1.0;
double zoomSpeed = 0.88;  // Lower = faster zoom (was 0.95)

// Line buffer for rendering
uint16_t lineBuffer[SCREEN_WIDTH];

// Color palette
uint16_t palette[256];

// Performance tracking
unsigned long lastTime = 0;
int frames = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("Fast Mandelbrot Zoom Starting...");

  // Initialize display
  tft.init();
  tft.setRotation(0);
  tft.fillScreen(TFT_BLACK);

  // Generate colorful palette
  generatePalette();

  Serial.println("Display initialized. Starting zoom...");
  lastTime = millis();
}

void loop() {
  // Render current frame
  renderMandelbrot();

  // Update zoom
  zoom *= zoomSpeed;

  // Reset when too deep
  if (zoom < 1e-10) {
    zoom = 1.0;
    jumpToNewLocation();
  }

  // Show FPS every second
  frames++;
  unsigned long now = millis();
  if (now - lastTime >= 1000) {
    float fps = frames * 1000.0 / (now - lastTime);
    Serial.printf("FPS: %.1f, Zoom: %.2e\n", fps, zoom);
    frames = 0;
    lastTime = now;
  }
}

void renderMandelbrot() {
  // Render in blocks for speed
  for (int py = 0; py < SCREEN_HEIGHT; py += PIXEL_SIZE) {
    for (int px = 0; px < SCREEN_WIDTH; px += PIXEL_SIZE) {
      // Check if pixel is within circle
      int dx = px - CENTER_X;
      int dy = py - CENTER_Y;

      uint16_t color;

      if (dx*dx + dy*dy > CENTER_X*CENTER_X) {
        color = TFT_BLACK;
      } else {
        // Map to Mandelbrot coordinates
        double x0 = centerX + (px - CENTER_X) * zoom * 4.0 / SCREEN_WIDTH;
        double y0 = centerY + (py - CENTER_Y) * zoom * 4.0 / SCREEN_HEIGHT;

        // Calculate Mandelbrot
        int iter = mandelbrotFast(x0, y0);

        // Color mapping
        if (iter >= MAX_ITER) {
          color = TFT_BLACK;
        } else {
          color = palette[iter % 256];
        }
      }

      // Draw pixel block
      if (PIXEL_SIZE == 1) {
        tft.drawPixel(px, py, color);
      } else {
        tft.fillRect(px, py, PIXEL_SIZE, PIXEL_SIZE, color);
      }
    }
  }
}

int mandelbrotFast(double x0, double y0) {
  double x = 0.0;
  double y = 0.0;
  double x2 = 0.0;
  double y2 = 0.0;
  int iter = 0;

  while (iter < MAX_ITER && (x2 + y2) <= 4.0) {
    y = 2.0 * x * y + y0;
    x = x2 - y2 + x0;
    x2 = x * x;
    y2 = y * y;
    iter++;
  }

  return iter;
}

void generatePalette() {
  for (int i = 0; i < 256; i++) {
    // Create vibrant, smooth color transitions
    float t = i / 256.0;

    int r = (int)(128 + 127 * sin(t * 6.283));
    int g = (int)(128 + 127 * sin(t * 6.283 + 2.094));
    int b = (int)(128 + 127 * sin(t * 6.283 + 4.189));

    palette[i] = tft.color565(r, g, b);
  }
}

void jumpToNewLocation() {
  struct Loc { double x, y; };

  Loc spots[] = {
    {-0.7463, 0.1102},      // Classic spiral
    {-0.7269, 0.1889},      // Seahorse valley
    {0.285, 0.01},          // Triple spiral
    {-0.748, 0.1},          // Double helix
    {-0.16, 1.0405},        // Elephant valley
    {-0.75, 0.1},           // Deep zoom classic
    {-0.235125, 0.827215},  // Dendrite
    {-0.7453, 0.1127},      // Fine details
  };

  int idx = random(sizeof(spots) / sizeof(spots[0]));
  centerX = spots[idx].x;
  centerY = spots[idx].y;

  Serial.printf("Jump to: (%.4f, %.4f)\n", centerX, centerY);
}

/*
 * SPEED TUNING GUIDE:
 *
 * MAXIMUM SPEED (~5-8 FPS):
 *   #define PIXEL_SIZE 3
 *   #define MAX_ITER 32
 *   double zoomSpeed = 0.85;
 *
 * BALANCED (Current, ~2-4 FPS):
 *   #define PIXEL_SIZE 2
 *   #define MAX_ITER 48
 *   double zoomSpeed = 0.88;
 *
 * BEST QUALITY (~0.5-1 FPS):
 *   #define PIXEL_SIZE 1
 *   #define MAX_ITER 128
 *   double zoomSpeed = 0.95;
 *
 * Try different settings and find your preferred balance!
 */