https://www.aliexpress.com/item/1005006589727895.html

I have a 2.0 inch TFT Display OLED LCD Drive IC ST7789V 240RGBx320 Dot-Matrix SPI Interface for Arduio Full Color LCD Display Module. How do I control it with an ESP32 using Arduino IDE. I want to connect the pins as: GND VCC D18 - SCL D5 - SDA D17 - RST D16 - DC D4 - CS

| TFT Pin |	ESP32 Pin|	Notes|
|---------|-----------|------|
|GND	|GND	|Ground|
|VCC	|3.3V	|Use 3.3V, not 5V|
|SCL	|GPIO18	|SPI Clock (SCK)|
|SDA	|GPIO5	|SPI Data (MOSI)|
|RST	|GPIO17	|Reset|
|DC	|GPIO16	|Data / Command|
|CS	|GPIO4	|Chip Select|

**No BL / LED pin?**
That’s normal for some ST7789 modules.

It usually means the backlight is permanently ON and internally tied to VCC.
As soon as you power it, the backlight will light up.

# How to fix errors
## Compilation error
If you get an error like:
```
D:\UNO R4 WiFi\experiments\tetris\tetris.ino:1:10: fatal error: Adafruit_GFX.h: No such file or directory
    1 | #include <Adafruit_GFX.h>
      |          ^~~~~~~~~~~~~~~~
compilation terminated.
exit status 1

Compilation error: Adafruit_GFX.h: No such file or directory
```

It simply means the Adafruit GFX library is not installed (or not installed for this Arduino setup).

Install the Adafruit GFX Library (Correct Way). In Arduino IDE

Open Arduino IDE

Go to Sketch → Include Library → Manage Libraries…

In the search box, type:

Adafruit GFX


Install “Adafruit GFX Library” by Adafruit
(⚠️ Not similarly named ones)

Also install (if not already):

Adafruit ST7789

Adafruit BusIO (often auto-installed, but check)

After installing libraries:

Close Arduino IDE completely

Open it again

This ensures the compiler can see the new headers.