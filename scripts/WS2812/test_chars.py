"""
WS2812 8x8 Matrix - Display Numbers and Symbols

Module purpose
--------------
Utilities to display digits (0-9), directional arrows, and common symbols
on an 8x8 WS2812 (NeoPixel) matrix using MicroPython on ESP boards.

This file provides:
- Predefined 8x8 bitmaps for digits and symbols.
- Helpers to map (x,y) coordinates to the NeoPixel linear index for common
  zig-zag matrix layouts.
- Convenience functions to display individual digits/symbols, run simple
  demos and animations, and control brightness.

Hardware wiring and safety
--------------------------
- DIN -> configured GPIO (PIN)
- VCC -> 5V (or required supply for your matrix)
- GND -> MCU GND (common ground required)
Note: WS2812 LEDs can draw significant current at high brightness/white.
Use an appropriate power supply and avoid powering large matrices from the
MCU 3.3V rail.

Coordinate mapping / layout
---------------------------
Most 8x8 matrices use a "zig-zag" (serpentine) wiring where adjacent rows
alternate direction. The set_pixel() helper implements a common mapping:
- x: 0..7 left-to-right
- y: 0..7 top-to-bottom
- even rows: left->right
- odd rows: right->left

If your matrix uses a different ordering, adjust set_pixel() accordingly.

API / Usage
-----------
Configure PIN, NUM_LEDS and BRIGHTNESS for your hardware, then:
- show_digit(digit, color, duration)
- show_symbol(name, color, duration)
- countdown(start)
- show_all_digits()
- show_all_arrows()
- show_all_symbols()
- demo()  # runs a short demo sequence
- clear_matrix()

Example (in REPL)
-----------------
from test_chars import show_digit, clear_matrix
show_digit(5)          # show digit 5 (default color/duration)
time.sleep(1)
clear_matrix()
"""
from machine import Pin
from neopixel import NeoPixel
import time

# Configuration
PIN = 5
NUM_LEDS = 64
BRIGHTNESS = 0.2  # Adjust overall brightness (0.0 to 1.0)

# Initialize NeoPixel object
np = NeoPixel(Pin(PIN), NUM_LEDS)

# Color definitions (base RGB tuples)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
OFF = (0, 0, 0)
PINK = (255, 192, 203)  # defined early because used by show_all_digits()

def apply_brightness(color):
    """Return a color tuple scaled by the module BRIGHTNESS setting."""
    return tuple(int(c * BRIGHTNESS) for c in color)

def clear_matrix():
    """Turn off all LEDs and write the buffer."""
    for i in range(NUM_LEDS):
        np[i] = OFF
    np.write()

def set_pixel(x, y, color):
    """
    Set a pixel at coordinate (x, y) to `color`.

    Coordinates:
      x: 0..7 (left to right)
      y: 0..7 (top to bottom)

    This function applies the common zig-zag (serpentine) mapping used by
    many 8x8 NeoPixel matrices. If your matrix uses a different layout,
    adjust the index calculation here.
    """
    if 0 <= x < 8 and 0 <= y < 8:
        # Common zig-zag pattern: even rows left->right, odd rows right->left
        if y % 2 == 0:  # Even rows go left to right
            index = y * 8 + x
        else:  # Odd rows go right to left
            index = y * 8 + (7 - x)
        np[index] = apply_brightness(color)

def display_pattern(pattern, color=WHITE):
    """
    Display an 8x8 pattern.

    pattern: iterable of 8 rows, each row is iterable of 8 values (1 = ON, 0 = OFF)
    color: RGB tuple applied to every '1' cell
    """
    clear_matrix()
    for y in range(8):
        for x in range(8):
            if pattern[y][x] == 1:
                set_pixel(x, y, color)
    np.write()

# 8x8 Patterns for digits 0-9
DIGITS = {
    '0': [
        [0, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    '1': [
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    '2': [
        [0, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    '3': [
        [0, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    '4': [
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 0, 0],
        [0, 1, 0, 0, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    '5': [
        [1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 1, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    '6': [
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0],
        [1, 1, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    '7': [
        [1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    '8': [
        [0, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    '9': [
        [0, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [1, 1, 0, 0, 0, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
}

# Symbols
SYMBOLS = {
    'left': [  # ←
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
    ],
    'right': [  # →
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
    ],
    'up': [  # ↑
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 0, 1, 1, 0, 1, 1],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
       