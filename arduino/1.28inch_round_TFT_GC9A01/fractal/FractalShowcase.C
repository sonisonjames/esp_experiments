/*
 * Multi-Fractal Kaleidoscope for GC9A01 Round Display
 *
 * Fractals included:
 * - Mandelbrot Set
 * - Julia Sets (multiple variations)
 * - Burning Ship
 * - Tricorn (Mandelbar)
 * - Phoenix
 * - Newton's Method
 *
 * Automatically switches between fractals with smooth zoom animations
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

// Rendering settings
#define PIXEL_SIZE 2      // 2x2 blocks for speed
#define MAX_ITER 48       // Iteration limit

// Fractal types
enum FractalType {
  MANDELBROT,
  JULIA_1,
  JULIA_2,
  JULIA_3,
  BURNING_SHIP,
  TRICORN,
  PHOENIX,
  NEWTON
};

// Current fractal state
FractalType currentFractal = MANDELBROT;
double centerX = -0.5;
double centerY = 0.0;
double zoom = 1.0;
double zoomSpeed = 0.88;
int framesInCurrentFractal = 0;
int framesBeforeSwitch = 150;  // Change fractal after ~150 frames

// Julia set parameters
double juliaC_real = -0.7;
double juliaC_imag = 0.27;

// Color palettes
uint16_t palette[256];
int paletteMode = 0;

// Performance
unsigned long lastTime = 0;
int frames = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("Multi-Fractal Kaleidoscope Starting...");

  tft.init();
  tft.setRotation(0);
  tft.fillScreen(TFT_BLACK);

  generatePalette();

  Serial.println("Ready! Watch fractals morph and change...");
  lastTime = millis();
}

void loop() {
  // Render current fractal
  renderFractal();

  // Update zoom
  zoom *= zoomSpeed;
  framesInCurrentFractal++;

  // Check if it's time to switch fractals
  if (zoom < 1e-8 || framesInCurrentFractal >= framesBeforeSwitch) {
    switchToNewFractal();
  }

  // Show FPS
  frames++;
  unsigned long now = millis();
  if (now - lastTime >= 1000) {
    float fps = frames * 1000.0 / (now - lastTime);
    Serial.printf("FPS: %.1f, Fractal: %s, Zoom: %.2e\n",
                  fps, getFractalName(), zoom);
    frames = 0;
    lastTime = now;
  }
}

void renderFractal() {
  for (int py = 0; py < SCREEN_HEIGHT; py += PIXEL_SIZE) {
    for (int px = 0; px < SCREEN_WIDTH; px += PIXEL_SIZE) {
      // Circular clipping
      int dx = px - CENTER_X;
      int dy = py - CENTER_Y;

      uint16_t color;

      if (dx*dx + dy*dy > CENTER_X*CENTER_X) {
        color = TFT_BLACK;
      } else {
        // Map to fractal coordinates
        double x0 = centerX + (px - CENTER_X) * zoom * 4.0 / SCREEN_WIDTH;
        double y0 = centerY + (py - CENTER_Y) * zoom * 4.0 / SCREEN_HEIGHT;

        // Calculate based on current fractal type
        int iter = calculateFractal(x0, y0);

        // Apply coloring
        if (iter >= MAX_ITER) {
          // Interior - metallic gradient
          float depth = sqrt((x0 - centerX) * (x0 - centerX) +
                            (y0 - centerY) * (y0 - centerY)) / zoom;
          int depthColor = (int)(depth * 1000) % 256;
          color = palette[depthColor];
        } else {
          color = palette[iter % 256];
        }
      }

      // Draw block
      if (PIXEL_SIZE == 1) {
        tft.drawPixel(px, py, color);
      } else {
        tft.fillRect(px, py, PIXEL_SIZE, PIXEL_SIZE, color);
      }
    }
  }
}

int calculateFractal(double x0, double y0) {
  switch(currentFractal) {
    case MANDELBROT:
      return mandelbrot(x0, y0);

    case JULIA_1:
    case JULIA_2:
    case JULIA_3:
      return julia(x0, y0, juliaC_real, juliaC_imag);

    case BURNING_SHIP:
      return burningShip(x0, y0);

    case TRICORN:
      return tricorn(x0, y0);

    case PHOENIX:
      return phoenix(x0, y0);

    case NEWTON:
      return newton(x0, y0);

    default:
      return mandelbrot(x0, y0);
  }
}

// Mandelbrot Set
int mandelbrot(double x0, double y0) {
  double x = 0.0, y = 0.0;
  double x2 = 0.0, y2 = 0.0;
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

// Julia Set
int julia(double x, double y, double cReal, double cImag) {
  double x2 = x * x;
  double y2 = y * y;
  int iter = 0;

  while (iter < MAX_ITER && (x2 + y2) <= 4.0) {
    y = 2.0 * x * y + cImag;
    x = x2 - y2 + cReal;
    x2 = x * x;
    y2 = y * y;
    iter++;
  }
  return iter;
}

// Burning Ship Fractal
int burningShip(double x0, double y0) {
  double x = 0.0, y = 0.0;
  int iter = 0;

  while (iter < MAX_ITER && (x*x + y*y) <= 4.0) {
    double xtemp = x*x - y*y + x0;
    y = fabs(2.0 * x * y) + y0;  // Take absolute value
    x = fabs(xtemp);              // Take absolute value
    iter++;
  }
  return iter;
}

// Tricorn (Mandelbar)
int tricorn(double x0, double y0) {
  double x = 0.0, y = 0.0;
  double x2 = 0.0, y2 = 0.0;
  int iter = 0;

  while (iter < MAX_ITER && (x2 + y2) <= 4.0) {
    y = -2.0 * x * y + y0;  // Negative conjugate
    x = x2 - y2 + x0;
    x2 = x * x;
    y2 = y * y;
    iter++;
  }
  return iter;
}

// Phoenix Fractal
int phoenix(double x0, double y0) {
  double x = 0.0, y = 0.0;
  double xprev = 0.0, yprev = 0.0;
  double p = 0.5667;
  int iter = 0;

  while (iter < MAX_ITER && (x*x + y*y) <= 4.0) {
    double xtemp = x*x - y*y + x0 + p * xprev;
    double ytemp = 2.0 * x * y + y0 + p * yprev;
    xprev = x;
    yprev = y;
    x = xtemp;
    y = ytemp;
    iter++;
  }
  return iter;
}

// Newton's Method (z^3 - 1 = 0)
int newton(double x0, double y0) {
  double x = x0, y = y0;
  int iter = 0;

  while (iter < MAX_ITER) {
    // Calculate z^3
    double x2 = x * x;
    double y2 = y * y;
    double x3 = x * (x2 - 3.0 * y2);
    double y3 = y * (3.0 * x2 - y2);

    // Calculate z^3 - 1
    double fx = x3 - 1.0;
    double fy = y3;

    // Calculate derivative 3z^2
    double dfx = 3.0 * (x2 - y2);
    double dfy = 6.0 * x * y;

    // Newton iteration: z = z - f(z)/f'(z)
    double denominator = dfx * dfx + dfy * dfy;
    if (denominator < 0.0001) break;

    double xnew = x - (fx * dfx + fy * dfy) / denominator;
    double ynew = y - (fy * dfx - fx * dfy) / denominator;

    if (fabs(xnew - x) < 0.001 && fabs(ynew - y) < 0.001) break;

    x = xnew;
    y = ynew;
    iter++;
  }
  return iter;
}

void switchToNewFractal() {
  // Pick a new random fractal
  int oldFractal = currentFractal;
  currentFractal = (FractalType)random(8);

  // Set appropriate parameters for each fractal
  switch(currentFractal) {
    case MANDELBROT:
      centerX = random(0, 3) == 0 ? -0.7463 : -0.5;
      centerY = random(0, 3) == 0 ? 0.1102 : 0.0;
      zoom = 1.0;
      break;

    case JULIA_1:
      juliaC_real = -0.7;
      juliaC_imag = 0.27;
      centerX = 0.0;
      centerY = 0.0;
      zoom = 1.0;
      break;

    case JULIA_2:
      juliaC_real = 0.285;
      juliaC_imag = 0.01;
      centerX = 0.0;
      centerY = 0.0;
      zoom = 1.0;
      break;

    case JULIA_3:
      juliaC_real = -0.4;
      juliaC_imag = 0.6;
      centerX = 0.0;
      centerY = 0.0;
      zoom = 1.0;
      break;

    case BURNING_SHIP:
      centerX = -0.5;
      centerY = -0.5;
      zoom = 0.8;
      break;

    case TRICORN:
      centerX = 0.0;
      centerY = 0.0;
      zoom = 1.0;
      break;

    case PHOENIX:
      centerX = 0.0;
      centerY = 0.0;
      zoom = 1.2;
      break;

    case NEWTON:
      centerX = 0.0;
      centerY = 0.0;
      zoom = 1.5;
      break;
  }

  // Change color palette occasionally
  if (random(0, 3) == 0) {
    paletteMode = random(0, 3);
    generatePalette();
  }

  framesInCurrentFractal = 0;
  Serial.printf("\n>>> Switched to: %s <<<\n", getFractalName());
}

const char* getFractalName() {
  switch(currentFractal) {
    case MANDELBROT: return "Mandelbrot";
    case JULIA_1: return "Julia Set 1";
    case JULIA_2: return "Julia Set 2";
    case JULIA_3: return "Julia Set 3";
    case BURNING_SHIP: return "Burning Ship";
    case TRICORN: return "Tricorn";
    case PHOENIX: return "Phoenix";
    case NEWTON: return "Newton's Method";
    default: return "Unknown";
  }
}

void generatePalette() {
  for (int i = 0; i < 256; i++) {
    float t = i / 256.0;
    int r, g, b;

    switch(paletteMode) {
      case 0: // Metallic
        if (t < 0.25) {
          float local = t * 4;
          r = (int)(30 + local * 162);
          g = (int)(40 + local * 152);
          b = (int)(80 + local * 128);
        } else if (t < 0.5) {
          float local = (t - 0.25) * 4;
          r = (int)(192 + local * 63);
          g = (int)(192 + local * 63);
          b = (int)(208 + local * 47);
        } else if (t < 0.75) {
          float local = (t - 0.5) * 4;
          r = 255;
          g = (int)(255 - local * 40);
          b = (int)(255 - local * 255);
        } else {
          float local = (t - 0.75) * 4;
          r = (int)(255 - local * 70);
          g = (int)(215 - local * 105);
          b = (int)(0 + local * 60);
        }
        break;

      case 1: // Fire
        r = (int)(t * 255);
        g = (int)(t * t * 255);
        b = (int)(t * t * t * 128);
        break;

      case 2: // Ocean
        r = (int)(t * t * 100);
        g = (int)(100 + t * 155);
        b = (int)(150 + t * 105);
        break;
    }

    palette[i] = tft.color565(r, g, b);
  }
}

/*
 * FRACTAL SHOWCASE:
 *
 * This program displays 8 different fractals:
 * 1. Mandelbrot - Classic fractal
 * 2. Julia Set 1 - Dragon-like patterns
 * 3. Julia Set 2 - Swirly spirals
 * 4. Julia Set 3 - Dendrite patterns
 * 5. Burning Ship - Ship-like structures
 * 6. Tricorn - Reflected Mandelbrot
 * 7. Phoenix - Feather-like patterns
 * 8. Newton - Root-finding basins
 *
 * Each fractal zooms in for ~150 frames, then switches to a new one.
 * Color palettes also change randomly (metallic, fire, ocean).
 *
 * Adjust framesBeforeSwitch to change how long each fractal displays.
 */