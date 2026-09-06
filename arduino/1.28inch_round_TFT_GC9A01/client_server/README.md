# GC9A01 Random Word Demo

This example sends a new word, position, and color from a Windows Rust server to an ESP32 using the GC9A01 round TFT.

The server chooses the random word, position, and color. The ESP32 only receives and displays the values every five seconds.

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

- `esp32_gc9a01_stream_client.ino` - ESP32 random word display sketch
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

## ESP32 setup

1. Open `esp32_gc9a01_stream_client.ino` in the Arduino IDE
2. Set `ssid`, `password`, and `host` near the top of the sketch.
3. Upload the sketch to the ESP32 board.
4. Open Serial Monitor at 115200 baud to see each received word and its position.

Start the server before or after the ESP32; the client retries the TCP connection once per second.
