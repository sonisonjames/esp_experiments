// Kaleidoscopic generative art on ESP32 + 240x240 TFT
// Requires: TFT_eSPI library, correctly configured for your display

#include <TFT_eSPI.h>
#include <SPI.h>
#include <time.h>

TFT_eSPI tft = TFT_eSPI();  // Invoke custom library
time_t clockStart;

#define SCREEN_W 240
#define SCREEN_H 240
#define CX (SCREEN_W / 2)
#define CY (SCREEN_H / 2)

// Number of symmetric sectors (must divide 360). 8 => 45° steps.
#define SECTORS 36
#define HALF_SECTORS (SECTORS / 2)

// Number of mirrored strokes drawn per frame.
#define STROKES 18

void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.println("Kaleidoscope starting");

  char monthText[4];
  int day, year, hour, minute, second;
  sscanf(__DATE__, "%3s %d %d", monthText, &day, &year);
  sscanf(__TIME__, "%d:%d:%d", &hour, &minute, &second);

  const char *months = "JanFebMarAprMayJunJulAugSepOctNovDec";
  int month = (strstr(months, monthText) - months) / 3;
  struct tm buildTime = {};
  buildTime.tm_year = year - 1900;
  buildTime.tm_mon = month;
  buildTime.tm_mday = day;
  buildTime.tm_hour = hour;
  buildTime.tm_min = minute;
  buildTime.tm_sec = second;
  buildTime.tm_isdst = -1;
  clockStart = mktime(&buildTime);

  tft.init();
  tft.setRotation(0);          // adjust for your orientation
  tft.fillScreen(TFT_BLACK);
  randomSeed(analogRead(34));  // noisy seed from floating pin
  Serial.println("Display initialized");
}

// Convert polar (r, angleDeg) around centre to screen x,y
void polarToCart(float r, float angleDeg, int &x, int &y) {
  float rad = angleDeg * DEG_TO_RAD;
  x = CX + (int)(r * cos(rad));
  y = CY + (int)(r * sin(rad));
}

// Draw one animated stroke and all its kaleidoscopic mirrors.
void drawKaleidoStroke(float r1, float r2, float baseAngle, uint16_t color) {
  int x1, y1, x2, y2;

  // Rotate and reflect the stroke around the centre.
  for (int s = 0; s < SECTORS; s++) {
    float angle = baseAngle + s * (360.0f / SECTORS);
    polarToCart(r1, angle, x1, y1);
    polarToCart(r2, angle + 3.0f, x2, y2);

    tft.drawLine(x1, y1, x2, y2, color);
    tft.drawLine(SCREEN_W - 1 - x1, y1, SCREEN_W - 1 - x2, y2, color);
  }
}

void drawClockHand(float length, float angle, uint16_t color, uint8_t width) {
  int endX, endY;
  polarToCart(length, angle - 90.0f, endX, endY);
  tft.drawLine(CX, CY, endX, endY, color);
  if (width > 1) {
    tft.drawLine(CX + 1, CY, endX + 1, endY, color);
    tft.drawLine(CX, CY + 1, endX, endY + 1, color);
  }
}

void drawClock() {
  time_t currentEpoch = clockStart + millis() / 1000;
  struct tm currentTime;
  localtime_r(&currentEpoch, &currentTime);

  const int radius = 93;
  tft.fillCircle(CX, CY, radius, TFT_BLACK);
  tft.drawCircle(CX, CY, radius, TFT_CYAN);
  tft.drawCircle(CX, CY, radius - 3, TFT_DARKGREY);

  for (int tick = 0; tick < 60; tick++) {
    float angle = tick * 6.0f - 90.0f;
    float outerRadius = radius - 7.0f;
    float innerRadius = (tick % 5 == 0) ? radius - 17.0f : radius - 12.0f;
    int outerX, outerY, innerX, innerY;
    polarToCart(outerRadius, angle, outerX, outerY);
    polarToCart(innerRadius, angle, innerX, innerY);
    tft.drawLine(innerX, innerY, outerX, outerY,
      (tick % 5 == 0) ? TFT_WHITE : TFT_DARKGREY);
  }

  float secondAngle = currentTime.tm_sec * 6.0f;
  float minuteAngle = (currentTime.tm_min + currentTime.tm_sec / 60.0f) * 6.0f;
  float hourAngle = ((currentTime.tm_hour % 12) + currentTime.tm_min / 60.0f) * 30.0f;
  drawClockHand(52.0f, hourAngle, TFT_WHITE, 3);
  drawClockHand(70.0f, minuteAngle, TFT_YELLOW, 2);
  drawClockHand(78.0f, secondAngle, TFT_RED, 1);
  tft.fillCircle(CX, CY, 5, TFT_RED);

  char timeText[9];
  char dateText[11];
  const char *weekdays[] = {
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday"
  };
  snprintf(timeText, sizeof(timeText), "%02d:%02d:%02d",
    currentTime.tm_hour, currentTime.tm_min, currentTime.tm_sec);
  snprintf(dateText, sizeof(dateText), "%02d/%02d/%04d",
    currentTime.tm_mday, currentTime.tm_mon + 1, currentTime.tm_year + 1900);

  tft.setTextDatum(MC_DATUM);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.setTextSize(2);
  tft.drawString(timeText, CX, 144);
  tft.setTextSize(1);
  tft.drawString(dateText, CX, 164);
  tft.drawString(weekdays[currentTime.tm_wday], CX, 178);
}

void loop() {
  static uint32_t frameNumber = 0;
  float time = frameNumber * 0.045f;

  //tft.fillScreen(TFT_BLACK);

  // Slowly breathing rings make the centre feel alive.
  for (int ring = 0; ring < 4; ring++) {
    float radius = 18.0f + ring * 22.0f + 8.0f * sin(time * 1.7f + ring);
    uint16_t ringColor = tft.color565(
      25 + ring * 20,
      50 + ring * 25,
      100 + ring * 30
    );
    tft.drawCircle(CX, CY, (int)radius, ringColor);
  }

  // Long rotating strokes create a much stronger kaleidoscope pattern.
  for (int stroke = 0; stroke < STROKES; stroke++) {
    float phase = stroke * 21.0f;
    float radius = 12.0f + 68.0f * (0.5f + 0.5f * sin(time * 1.3f + phase));
    float length = 10.0f + 25.0f * (0.5f + 0.5f * cos(time * 1.8f + phase));
    float angle = time * (18.0f + stroke * 0.7f) + phase;
    uint16_t color = tft.color565(
      80 + (stroke * 37) % 176,
      70 + (stroke * 61) % 176,
      100 + (stroke * 47) % 156
    );
    drawKaleidoStroke(radius, min(radius + length, 108.0f), angle, color);
  }

  drawClock();

  frameNumber++;
  if ((frameNumber % 100) == 0) {
    Serial.print("Frames: ");
    Serial.println(frameNumber);
  }
  delay(10);
}