1.28 inch 7PIN SPI TFT LCD Module Color Round Screen display Adapter PCB Board GC9A01 Drive.

| TFT Pin |	ESP32 Pin|	Notes|
|---------|-----------|------|
|GND	|GND	|Ground|
|VCC	|3.3V	|Use 3.3V, not 5V|
|SCL	|GPIO18	|SPI Clock (SCK)|
|SDA	|GPIO5	|SPI Data (MOSI)|
|RST	|GPIO17	|Reset|
|DC	|GPIO16	|Data / Command|
|CS	|GPIO4	|Chip Select|



# Using TFT_eSPI.h driver
When using this driver we don't need to specify the PIN configuration explicitly in the code. The pin config is specified in the file - **C:\Users\sonis\OneDrive\Documents\Arduino\libraries\TFT_eSPI\User_Setup.h** like this

```
#define USER_SETUP_LOADED
#define GC9A01_DRIVER

#define TFT_WIDTH  240
#define TFT_HEIGHT 240

#define TFT_MISO  -1
#define TFT_MOSI  5  // Automatically assigned with ESP8266 if not defined
#define TFT_SCLK  18  // Automatically assigned with ESP8266 if not defined
#define TFT_CS    4  // Chip select control pin D8
#define TFT_DC    16  // Data Command control pin
#define TFT_RST   17  // Reset pin (could connect to NodeMCU RST, see next line)
//#define TFT_RST  -1     // Set TFT_RST to -1 if the display RESET is connected to NodeMCU RST or 3.3V
```