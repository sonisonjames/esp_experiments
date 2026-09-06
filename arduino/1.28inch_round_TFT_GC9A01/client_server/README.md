# GC9A01 Display Demo

This example sends text or a static full-screen cartoon from a Windows Rust server to an ESP32 using the GC9A01 round TFT.

The server chooses the random word, position, and color for text mode. Image mode sends one original mouse-like cartoon as a 240x240 RGB565 frame; the ESP32 displays it once and keeps it static.

## Required TFT_eSPI macros

Add these to `C:\Users\sonis\OneDrive\Documents\Arduino\libraries\TFT_eSPI\User_Setup.h`:

```cpp
#define USER_SETUP_LOADED
#define GC9A01_DRIVER
#define TFT_WIDTH  240
#define TFT_HEIGHT 240

#define TFT_MISO  -1
#define TFT_MOSI   5
#define TFT_SCLK  18
#define TFT_CS    4
#define TFT_DC    16
#define TFT_RST   17

#define SPI_FREQUENCY  27000000
```

## Files in this folder

- `esp32_gc9a01_stream_client.ino` - ESP32 network display client
- `server/` - Rust TCP server

## Protocol

Each text packet contains `TXT1`, text length, message ID, center x/y coordinates, and RGB565 color, followed by the text bytes.

## Server setup

From `client_server/server`:

```bash
cargo build --release
.\target\release\gc9a01_tcp_server.exe random
```

The `random` command sends a new word, location, and color every five seconds. Use `random --repeat 10` for ten messages. The server listens on TCP port 9001.

For a fixed-message connection, use `text "Hello"`.

For the static full-screen cartoon, use:

```bash
.\target\release\gc9a01_tcp_server.exe image
```

The image is sent once at 240x240. The ESP32 receives it in small 8-row chunks, displays it, and holds the image on the TFT. This avoids requiring a full 115 KB framebuffer in ESP32 RAM.

After changing the sketch, upload the new firmware to the ESP32. The message `Could not allocate image buffer` belongs to the previous full-frame-buffer implementation and should no longer appear.

## ESP32 setup

1. Open `esp32_gc9a01_stream_client.ino` in the Arduino IDE
2. Set `ssid`, `password`, and `host` near the top of the sketch.
3. Upload the sketch to the ESP32 board.
4. Open Serial Monitor at 115200 baud to see each received word and its position.

Start the server before or after the ESP32; the client retries the TCP connection once per second.
