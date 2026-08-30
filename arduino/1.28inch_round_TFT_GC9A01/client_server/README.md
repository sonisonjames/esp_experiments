# GC9A01 TCP Frame Streaming Demo

This example streams animated frames from a Windows server to an ESP32 display using the GC9A01 round TFT.

The design is intentionally simple:
- the Windows machine does all the heavy rendering
- the ESP32 only receives frame data and pushes it to the TFT
- the display is updated with full-frame RGB565 images instead of drawLine/drawPixel per object, which avoids flicker

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

- `esp32_gc9a01_stream_client.ino` – ESP32 client that receives RGB565 frames and displays them
- `server/Cargo.toml` – Rust project definition
- `server/src/main.rs` – Rust server that renders a simple cartoon animation and streams it to the ESP32

## How it works

1. The Rust server listens on TCP port `9001`
2. The ESP32 connects to the Windows machine
3. The server renders a 240x240 cartoon frame as RGB565
4. The server sends a small header followed by the pixel payload
5. The ESP32 calls `tft.pushImage(0, 0, 240, 240, frameBuffer)`
6. The process repeats for the next frame

This creates a smooth animation with no flicker from repeated full-screen clears.

## Windows server run steps

From a terminal in `client_server/server`:

```bash
cargo run --release
```

The server will listen on `0.0.0.0:9001`.

## ESP32 client run steps

1. Open `esp32_gc9a01_stream_client.ino` in the Arduino IDE
2. Update WiFi credentials:

```cpp
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* host = "192.168.1.50";
const int port = 9001;
```

3. Compile and upload to the ESP32
4. Power the TFT and ensure the pins match the `User_Setup.h` block above
5. Run the Rust server on the Windows machine

## Notes

- The server sends one full frame at a time, not per-object drawing commands
- This is the easiest way to get smooth animation on a small TFT display
- For a more advanced cartoon scene, replace the simple frame renderer in `server/src/main.rs` with sprite layers or a sprite sheet

## Suggested next step

Replace the simple cartoon face in the Rust server with:
- a Cuphead-inspired character
- parallax background layers
- animated eyes, mouth, and body
- comic-style shadows and outlines
