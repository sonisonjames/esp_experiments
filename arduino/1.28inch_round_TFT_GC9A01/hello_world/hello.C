/*
 * GC9A01 Round LCD Display - Hello World
 *
 * Library: Adafruit GC9A01A + Adafruit GFX
 * Display: 1.28" 240x240 Round TFT LCD
 *
 */

#include <Adafruit_GFX.h>
#include <Adafruit_GC9A01A.h>
#include <SPI.h>

// Pin definitions - matching your wiring
#define TFT_CS   4   // Chip Select
#define TFT_DC   16  // Data/Command
#define TFT_RST  17  // Reset
#define TFT_SCL  18   
#define TFT_MOSI 5   // Aka SDA

// Create display object
Adafruit_GC9A01A tft(TFT_CS, TFT_DC, TFT_RST);

// Color definitions (RGB565 format)
#define BLACK    0x0000
#define BLUE     0x001F
#define RED      0xF800
#define GREEN    0x07E0
#define CYAN     0x07FF
#define MAGENTA  0xF81F
#define YELLOW   0xFFE0
#define WHITE    0xFFFF

void setup() {
  Serial.begin(115200);
  Serial.println("GC9A01 Hello World Test");

  // Initialize SPI with custom pins
  SPI.begin(TFT_SCL, -1, TFT_MOSI, TFT_CS);  // SCK=TFT_SCL, MISO=-1(not used), MOSI=TFT_MOSI, SS=TFT_CS

  // Initialize display
  tft.begin();
  tft.setRotation(2);  // 0-3 for different orientations

  // Clear screen with black background
  tft.fillScreen(BLACK);

  // Display "Hello World" in the center
  tft.setCursor(60, 100);
  tft.setTextColor(WHITE);
  tft.setTextSize(3);
  tft.println("Hello");

  tft.setCursor(60, 130);
  tft.println("World!");

  Serial.println("Display initialized!");
}

void loop() {
  // Optional: Add some animation
  static int colorIndex = 0;
  uint16_t colors[] = {RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE};

  delay(1000);

  // Change text color every second
  tft.fillScreen(BLACK);
  tft.setCursor(60, 100);
  tft.setTextColor(colors[colorIndex]);
  tft.setTextSize(3);
  tft.println("Hello");

  tft.setCursor(60, 130);
  tft.println("World!");

  colorIndex = (colorIndex + 1) % 7;
}