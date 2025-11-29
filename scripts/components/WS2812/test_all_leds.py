"""
WS2812 8x8 Matrix Color Test

Module purpose
--------------
Utilities and interactive test routines for driving an 8x8 WS2812 (NeoPixel)
matrix from an ESP board running MicroPython. The script provides several
visual tests (color wheel, rainbow, primary colors, and RGB fades) intended
for manual verification, prototyping, and demonstration.

Highlights
----------
- Works with a 64-LED (8x8) NeoPixel matrix connected to the configured GPIO.
- Includes convenience helpers for HSV->RGB conversion and common display
  patterns.
- Auto-starts the color wheel test when executed as a script.

Hardware / safety
-----------------
- Designed for 3.3V logic MCUs (ESP8266/ESP32). Verify your LED matrix power
  requirements: WS2812 strips/matrices can draw significant current at full
  white/brightness. Use a proper external 5V supply (or as required by your
  matrix) and common ground. Do NOT power the LEDs from the MCU 3.3V rail if
  they require 5V and the current draw is high.
- Default BRIGHTNESS is conservative (0.3). Lower this value to reduce
  current draw and protect your eyes when testing.

Usage
-----
- Edit PIN, NUM_LEDS and BRIGHTNESS as appropriate for your hardware.
- Upload this file to the device and run it. It will auto-start the color
  wheel test after a short delay. You can import and call individual test
  functions from the REPL for manual control:
    from test_all_leds import color_wheel_test, rainbow_test, primary_colors_test, fade_test, clear_all

Notes
-----
- The code uses time.sleep* and will block the interpreter while running tests.
- Designed for MicroPython's NeoPixel driver (neopixel.NeoPixel) and
  machine.Pin.
"""
from machine import Pin
from neopixel import NeoPixel
import time

# Configuration
PIN = 5           # GPIO pin connected to DIN
NUM_LEDS = 64     # 8x8 matrix = 64 LEDs
BRIGHTNESS = 0.3  # 0.0 to 1.0 (30% brightness to protect your eyes!)

# Initialize the LED strip
np = NeoPixel(Pin(PIN), NUM_LEDS)

def hsv_to_rgb(h, s, v):
    """
    Convert an HSV color to an RGB tuple suitable for NeoPixel.

    Parameters:
        h (int or float): Hue in degrees [0,360).
        s (float): Saturation in range [0.0, 1.0].
        v (float): Value/brightness in range [0.0, 1.0].

    Returns:
        tuple: (r, g, b) with integer components in [0, 255].

    Notes:
        - This function expects typical HSV semantics. The returned RGB values
          are not scaled by the module BRIGHTNESS constant; callers should
          apply BRIGHTNESS where required.
    """
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)

    return (r, g, b)

def set_all_leds(color):
    """
    Set every LED in the matrix to the same RGB color and write to the strip.

    Parameters:
        color (tuple): (r, g, b) integers in [0,255].

    Side-effects:
        - Updates the global NeoPixel buffer and calls np.write().
    """
    for i in range(NUM_LEDS):
        np[i] = color
    np.write()

def color_wheel_test(speed=2):
    """
    Smoothly cycle all LEDs through the full color wheel.

    Parameters:
        speed (int): Hue increment per loop iteration (higher = faster).

    Behavior:
        - Runs until interrupted (KeyboardInterrupt).
        - Prints current hue and RGB value for debugging/monitoring.
    """
    print("Starting color wheel test...")
    print("Press Ctrl+C to stop")

    try:
        hue = 0
        while True:
            # Convert HSV to RGB (full saturation, brightness controlled)
            color = hsv_to_rgb(hue, 1.0, BRIGHTNESS)
            set_all_leds(color)

            # Print current color info
            print(f"Hue: {hue:3d}° | RGB: {color}")

            # Increment hue
            hue = (hue + speed) % 360

            # Small delay for smooth transition
            time.sleep(0.02)  # 20ms = ~50 FPS

    except KeyboardInterrupt:
        print("\nTest stopped!")
        clear_all()

def rainbow_test():
    """
    Display a moving rainbow across the matrix where each LED has a different hue.

    Behavior:
        - Runs until interrupted (KeyboardInterrupt).
        - Shifts the hue offset over time to animate the rainbow.
    """
    print("Rainbow pattern test...")
    try:
        hue_offset = 0
        while True:
            for i in range(NUM_LEDS):
                # Each LED gets a slightly different hue
                hue = (hue_offset + i * 360 // NUM_LEDS) % 360
                color = hsv_to_rgb(hue, 1.0, BRIGHTNESS)
                np[i] = color
            np.write()

            hue_offset = (hue_offset + 2) % 360
            time.sleep(0.03)

    except KeyboardInterrupt:
        print("Rainbow test stopped!")
        clear_all()

def primary_colors_test():
    """
    Cycle through a small list of primary/secondary colors for inspection.

    Behavior:
        - Displays each named color in turn for a short pause.
        - Applies BRIGHTNESS scaling to the base RGB values.
    """
    colors = {
        'Red': (255, 0, 0),
        'Green': (0, 255, 0),
        'Blue': (0, 0, 255),
        'Yellow': (255, 255, 0),
        'Cyan': (0, 255, 255),
        'Magenta': (255, 0, 255),
        'White': (255, 255, 255),
        'Orange': (255, 165, 0),
    }

    print("Testing primary and secondary colors...")

    try:
        for name, rgb in colors.items():
            # Apply brightness reduction
            color = tuple(int(c * BRIGHTNESS) for c in rgb)
            print(f"Displaying: {name} - {color}")
            set_all_leds(color)
            time.sleep(1.5)

        clear_all()
        print("Primary colors test complete!")

    except KeyboardInterrupt:
        print("\nTest stopped!")
        clear_all()

def clear_all():
    """
    Turn off all LEDs (set to black) and write the change.

    Also prints a confirmation message.
    """
    set_all_leds((0, 0, 0))
    print("All LEDs off")

def fade_test():
    """
    Smoothly fade between red, green, and blue across the whole matrix.

    Behavior:
        - Runs until interrupted (KeyboardInterrupt).
        - Gradually interpolates between color channels using BRIGHTNESS scaling.
    """
    print("RGB fade test...")

    try:
        while True:
            # Fade red up
            for i in range(0, 256, 5):
                color = (int(i * BRIGHTNESS), 0, 0)
                set_all_leds(color)
                time.sleep(0.02)

            # Fade red down, green up
            for i in range(0, 256, 5):
                color = (int((255 - i) * BRIGHTNESS), int(i * BRIGHTNESS), 0)
                set_all_leds(color)
                time.sleep(0.02)

            # Fade green down, blue up
            for i in range(0, 256, 5):
                color = (0, int((255 - i) * BRIGHTNESS), int(i * BRIGHTNESS))
                set_all_leds(color)
                time.sleep(0.02)

            # Fade blue down
            for i in range(0, 256, 5):
                color = (0, 0, int((255 - i) * BRIGHTNESS))
                set_all_leds(color)
                time.sleep(0.02)

    except KeyboardInterrupt:
        print("\nFade test stopped!")
        clear_all()

# Main menu
def main():
    """Print a short interactive help menu and start the default test."""
    print("\n" + "="*50)
    print("WS2812 8x8 Matrix Color Test")
    print("="*50)
    print("\nAvailable tests:")
    print("1. Color Wheel (smooth cycle through all hues)")
    print("2. Rainbow Pattern (different color per LED)")
    print("3. Primary Colors (test basic colors)")
    print("4. RGB Fade Test (smooth RGB transitions)")
    print("5. Clear All LEDs")
    print("\nTo run a test, call the function:")
    print("  color_wheel_test()    # Recommended!")
    print("  rainbow_test()")
    print("  primary_colors_test()")
    print("  fade_test()")
    print("  clear_all()")
    print("\nStarting Color Wheel test in 2 seconds...")
    time.sleep(2)

    # Auto-start the color wheel test
    color_wheel_test(speed=3)

# Run the main program
if __name__ == "__main__":
    main()