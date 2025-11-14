"""
WS2812 8x8 Matrix — Character Display Utilities

Purpose
-------
Utilities to display single characters (digits 0-9), directional arrows and
simple symbols on an 8x8 WS2812 (NeoPixel) matrix using MicroPython.

This module provides:
- A set of 8x8 bitmaps (PATTERNS) for digits and symbols.
- Helpers to apply global brightness, clear the matrix and render patterns.
- Interactive helpers: show_all() to step through characters, show_char(), and
  a simple test function.

Hardware / wiring
-----------------
- Connect DIN on the LED matrix to the configured PIN.
- Provide an appropriate external power supply for the matrix and share
  ground with the MCU. WS2812 matrices can draw significant current at
  high brightness—use a suitable power source.

Layout / mapping
----------------
This script uses simple row-major mapping: the first row occupies indices
0..7, the second row 8..15, etc. If your matrix uses a zig-zag/serpentine
layout, adjust the index computation in display_pattern accordingly.

Usage
-----
- Configure PIN, NUM_LEDS and BRIGHTNESS for your hardware.
- Upload this file to the board and call functions from the REPL:
    show_all()        # interactive, press ENTER to advance
    show_char('5')    # show a specific character
    test_simple()     # quick check
    clear()           # turn off all LEDs

Notes
-----
- Functions that pause (e.g. show_all(), test_simple()) are blocking and
  use input()/time.sleep(); use carefully when running other tasks.
"""
from machine import Pin
from neopixel import NeoPixel
import time

# Configuration
WS2812_PIN = 5
NUM_LEDS = 64
BRIGHTNESS = 0.2

# Initialize
np = NeoPixel(Pin(WS2812_PIN), NUM_LEDS)

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
OFF = (0, 0, 0)

def apply_brightness(color):
    """
    Return a color tuple scaled by the global BRIGHTNESS.

    Parameters:
        color (tuple): (r,g,b) each 0..255

    Returns:
        tuple: scaled (r,g,b) integers.
    """
    return tuple(int(c * BRIGHTNESS) for c in color)

def clear():
    """
    Turn off all LEDs immediately.

    This writes black to every LED and calls np.write() to update the strip.
    """
    for i in range(NUM_LEDS):
        np[i] = OFF
    np.write()

def display_pattern(pattern, color=WHITE):
    """
    Render an 8x8 pattern to the matrix.

    Parameters:
        pattern (list[list[int]]): 8 rows x 8 cols, values 1 = ON, 0 = OFF.
        color (tuple): RGB tuple applied to 'ON' pixels (unscaled).
    Behavior:
        - Applies the module BRIGHTNESS to the color before writing.
        - Uses row-major mapping: index = row*8 + col.
        - Calls np.write() once after the full buffer is prepared.
    """
    clear()
    color = apply_brightness(color)

    for row in range(8):
        for col in range(8):
            if pattern[row][col] == 1:
                index = row * 8 + col
                np[index] = color

    np.write()

# Character patterns (8x8 grid)
PATTERNS = {
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
    'left': [
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
    ],
    'right': [
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
    ],
    'up': [
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 0, 1, 1, 0, 1, 1],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
    ],
    'down': [
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [1, 1, 0, 1, 1, 0, 1, 1],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
    ],
    'stop': [
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
    ],
    'star': [
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [1, 0, 1, 1, 1, 1, 0, 1],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 0, 0, 1, 1, 0],
        [1, 1, 0, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
    ],
    'hash': [
        [0, 1, 0, 0, 1, 0, 0, 0],
        [0, 1, 0, 0, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 1, 0, 0, 0],
        [0, 1, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
}

def show_all():
    """
    Interactive: display all characters in PATTERNS one by one.

    Waits for the user to press ENTER to advance; entering 'q' quits early.
    """
    print("\n" + "="*50)
    print("Character Display - Press ENTER to advance")
    print("="*50)

    # List of all characters in order
    characters = [
        ('0', BLUE),
        ('1', BLUE),
        ('2', BLUE),
        ('3', BLUE),
        ('4', BLUE),
        ('5', BLUE),
        ('6', BLUE),
        ('7', BLUE),
        ('8', BLUE),
        ('9', BLUE),
        ('left', GREEN),
        ('right', GREEN),
        ('up', CYAN),
        ('down', CYAN),
        ('stop', RED),
        ('star', YELLOW),
        ('hash', MAGENTA),
    ]

    for char, color in characters:
        display_pattern(PATTERNS[char], color)
        print(f"\nDisplaying: {char}")

        response = input("Press ENTER for next (or 'q' to quit): ").strip().lower()
        if response == 'q':
            break

    clear()
    print("\n✓ Complete!")

def show_char(char, color=WHITE):
    """
    Display a specific character from PATTERNS.

    If the character key is not found, prints available keys.
    """
    if char in PATTERNS:
        display_pattern(PATTERNS[char], color)
        print(f"Displaying: {char}")
    else:
        print(f"Character '{char}' not found!")
        print(f"Available: {', '.join(PATTERNS.keys())}")

def test_simple():
    """Show digit '1' and wait for ENTER to clear (quick manual test)."""
    print("\nSimple test: Showing digit '1'")
    display_pattern(PATTERNS['1'], BLUE)
    input("Press ENTER to clear...")
    clear()

# Main
print("\n" + "="*50)
print("WS2812 8x8 Character Display")
print("="*50)
print("\nQuick start:")
print("  show_all()           - Show all characters (press ENTER between each)")
print("  show_char('5', RED)  - Show specific character")
print("  test_simple()        - Just show digit 1")
print("  clear()              - Turn off display")
print("\nAvailable characters:")
print("  Digits: 0-9")
print("  Arrows: 'left', 'right', 'up', 'down'")
print("  Symbols: 'stop', 'star', 'hash'")
print("="*50)
print("\nTo start: show_all()")