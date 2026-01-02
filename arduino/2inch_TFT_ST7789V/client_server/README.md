# Client side
Find your Arduino libraries folder (usually Documents/Arduino/libraries/TFT_eSPI/) and open User_Setup.h. Comment out any existing defines and add/uncomment these specific lines:
```
#define ST7789_DRIVER      // Full color display
#define TFT_WIDTH  240
#define TFT_HEIGHT 320

// Define the pins you chose
#define TFT_MOSI 5         // SDA pin
#define TFT_SCLK 18        // SCL pin
#define TFT_CS   4         // CS pin
#define TFT_DC   16        // DC pin
#define TFT_RST  17        // RST pin

#define LOAD_GLCD          // Standard font
#define SPI_FREQUENCY  40000000 // Set to 40MHz for speed
```

# Server side
First install the required Python packages:
```
pip install pygame PyOpenGL PyOpenGL_accelerate pyserial numpy
```
