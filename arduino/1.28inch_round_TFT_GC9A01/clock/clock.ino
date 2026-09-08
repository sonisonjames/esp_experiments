// Smooth analog and digital clock on ESP32 + 240x240 TFT
// Requires: TFT_eSPI library, correctly configured for your display

#include <TFT_eSPI.h>
#include <SPI.h>
#include <time.h>

TFT_eSPI tft = TFT_eSPI();  // Invoke custom library
TFT_eSprite clockFrame = TFT_eSprite(&tft);
time_t clockStart;

#define SCREEN_W 240
#define SCREEN_H 240
#define FRAME_SIZE 200
#define FRAME_X ((SCREEN_W - FRAME_SIZE) / 2)
#define FRAME_Y ((SCREEN_H - FRAME_SIZE) / 2)
#define CX (FRAME_SIZE / 2)
#define CY (FRAME_SIZE / 2)

void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.println("Clock starting");

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
  clockFrame.setColorDepth(16);
  if (clockFrame.createSprite(FRAME_SIZE, FRAME_SIZE) == NULL) {
    Serial.println("Clock sprite allocation failed");
    while (true) {
      tft.fillScreen(TFT_RED);
      delay(500);
      tft.fillScreen(TFT_BLACK);
      delay(500);
    }
  }
  randomSeed(analogRead(34));  // noisy seed from floating pin
  Serial.println("Display initialized");
}

// Convert polar (r, angleDeg) around centre to screen x,y
void polarToCart(float r, float angleDeg, int &x, int &y) {
  float rad = angleDeg * DEG_TO_RAD;
  x = CX + (int)(r * cos(rad));
  y = CY + (int)(r * sin(rad));
}

void drawClockHand(float length, float angle, uint16_t color, uint8_t width) {
  int endX, endY;
  polarToCart(length, angle - 90.0f, endX, endY);
  clockFrame.drawLine(CX, CY, endX, endY, color);
  if (width > 1) {
    clockFrame.drawLine(CX + 1, CY, endX + 1, endY, color);
    clockFrame.drawLine(CX, CY + 1, endX, endY + 1, color);
  }
}

void drawClock() {
  time_t currentEpoch = clockStart + millis() / 1000;
  struct tm currentTime;
  localtime_r(&currentEpoch, &currentTime);

  const int radius = 93;
  clockFrame.fillCircle(CX, CY, radius, TFT_BLACK);
  clockFrame.drawCircle(CX, CY, radius, TFT_CYAN);
  clockFrame.drawCircle(CX, CY, radius - 3, TFT_DARKGREY);

  for (int tick = 0; tick < 60; tick++) {
    float angle = tick * 6.0f - 90.0f;
    float outerRadius = radius - 7.0f;
    float innerRadius = (tick % 5 == 0) ? radius - 17.0f : radius - 12.0f;
    int outerX, outerY, innerX, innerY;
    polarToCart(outerRadius, angle, outerX, outerY);
    polarToCart(innerRadius, angle, innerX, innerY);
    clockFrame.drawLine(innerX, innerY, outerX, outerY,
      (tick % 5 == 0) ? TFT_WHITE : TFT_DARKGREY);
  }

  float secondAngle = currentTime.tm_sec * 6.0f;
  float minuteAngle = (currentTime.tm_min + currentTime.tm_sec / 60.0f) * 6.0f;
  float hourAngle = ((currentTime.tm_hour % 12) + currentTime.tm_min / 60.0f) * 30.0f;
  drawClockHand(52.0f, hourAngle, TFT_WHITE, 3);
  drawClockHand(70.0f, minuteAngle, TFT_YELLOW, 2);
  drawClockHand(78.0f, secondAngle, TFT_RED, 1);
  clockFrame.fillCircle(CX, CY, 5, TFT_RED);

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

  clockFrame.setTextDatum(MC_DATUM);
  clockFrame.setTextColor(TFT_WHITE, TFT_BLACK);
  clockFrame.setTextSize(2);
  clockFrame.drawString(timeText, CX, 142);
  clockFrame.setTextSize(1);
  clockFrame.drawString(dateText, CX, 163);
  clockFrame.drawString(weekdays[currentTime.tm_wday], CX, 178);
}

void loop() {
  clockFrame.fillSprite(TFT_BLACK);
  drawClock();
  clockFrame.pushSprite(FRAME_X, FRAME_Y);
  delay(16);
}