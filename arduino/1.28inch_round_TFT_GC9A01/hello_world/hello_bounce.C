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
  randomSeed(analogRead(0));

  // Clear screen with black background
  tft.fillScreen(BLACK);

  Serial.println("Display initialized!");
}

void loop() {
  static int16_t x = 0;
  static int16_t y = 0;
  static int8_t xSpeed = 2;
  static int8_t ySpeed = 1;
  static int colorIndex = 0;
  uint16_t colors[] = {RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE};
  int16_t textX1, textY1;
  uint16_t textWidth, textHeight;

  tft.setTextSize(3);
  tft.getTextBounds("Hello World!", x, y, &textX1, &textY1, &textWidth, &textHeight);

  tft.fillScreen(BLACK);
  tft.setTextColor(colors[colorIndex]);
  tft.setCursor(x, y);
  tft.print("Hello World!");

  x += xSpeed;
  y += ySpeed;

  if (x <= 0 || x + textWidth >= tft.width()) {
    xSpeed = -xSpeed;
    x = constrain(x, 0, tft.width() - textWidth);
    colorIndex = (colorIndex + 1) % 7;
    tft.setRotation(random(4));
  }
  if (y <= 0 || y + textHeight >= tft.height()) {
    ySpeed = -ySpeed;
    y = constrain(y, 0, tft.height() - textHeight);
    colorIndex = (colorIndex + 1) % 7;
    tft.setRotation(random(4));
  }

  delay(20);
}