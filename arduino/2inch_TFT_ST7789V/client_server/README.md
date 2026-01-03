# What the different pairs of client and server do
1. client_1 and server_1: Sends a text message from the PC to the TFT
2. client_2 and server_2: Send wireframe 3D cube from the PC to the TFT - however the cube is not well formed
3. client_3 and server_3: Send a wireframe 3D cube from the PC to the TFT - better formed cube
4. client_4 and server_4: Send a pyramid 3D cube from the PC to the TFT

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

# How to run the client and server
client_n communicates with server_n
where n is the same number on both sides.
For example client_1 with server_1, client_2 with server_2, etc