"""
remote_ir_sensor_handler.py

NEC IR remote decoder & handler for MicroPython on ESP chips.

Purpose
-------
This module reads an HX1838-style IR receiver connected to a GPIO pin, decodes
NEC-protocol frames, and maps decoded 32-bit NEC codes to human-readable
button labels. It is intended for experimentation, learning, and simple
automation tasks on ESP8266/ESP32 boards running MicroPython.

Features
--------
- Captures level transitions and timing (µs) from the IR receiver pin.
- Performs a basic NEC timing decode (leader + 32 bits).
- Provides a simple keymap to map decoded codes to labels.
- Detects NEC repeat frames (0xFFFFFFFF) and prints a repeat indicator.

Hardware Wiring
----------------
- IR receiver module VCC -> 3.3V
- IR receiver module GND -> GND
- IR receiver module OUT -> GPIO defined by PIN_NUM (default GPIO13)
Do NOT connect the IR module to 5V when using ESP boards that expect 3.3V.

Constants / Configuration
-------------------------
- PIN_NUM: GPIO number where the HX1838 signal pin is connected.
- MAX_WINDOW_MS: Maximum capture window (ms) for a single IR frame. Increase
  slightly if captures are being cut off; decrease to reduce blocking time.

API / Usage
-----------
This script is typically run as a top-level blocking script on a device.
Functions of interest:
- capture_transitions() -> list[(level:int, duration_us:int)]
    Block until a low pulse is detected, then record (level, duration) pairs
    for up to MAX_WINDOW_MS milliseconds. Useful for inspecting raw signal
    timing when learning new remotes.

- decode_nec(trans: list) -> int | None
    Decode a list of transitions produced by capture_transitions() into a
    32-bit NEC integer code. Returns None for invalid frames.

Example (on-device)
-------------------
Run the module on the board. It prints detected button labels (or the raw
hex code for unknown buttons). Use the printed hex values to extend the
keymap dictionary for new remotes.

Tuning & Troubleshooting
------------------------
- Timing thresholds in decode_nec() (leader/bit thresholds, 1200µs for `1`)
  are conservative defaults for many NEC remotes. Adjust if decoding fails.
- If no frames are captured, verify wiring and that the IR LED on the
  receiver blinks when pressing a remote button (some modules have LEDs).
- Increase MAX_WINDOW_MS if long frames are being truncated.

Limitations
-----------
- This implementation is a simple software decoder and is not real-time
  perfect. For robust operation, use hardware-timed capture or dedicated IR
  libraries when available.
- Not hardened for noisy signals or different IR protocols (Samsung, RC5, ...)
"""
from machine import Pin
from neopixel import NeoPixel
import time
import math

# ---- WS2812 Configuration
WS2812_PIN = 5
BRIGHTNESS = 0.2
WIDTH = 8
HEIGHT = 8
NUM_LEDS = WIDTH * HEIGHT

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
# ---- WS2812 Configuration

# ---- IR sensor Configuration
IR_SENSOR_PIN = 13          # HX1838 signal pin (GPIO number)
MAX_WINDOW_MS = 200   # Maximum capture window (ms) for a single IR frame
ir = Pin(IR_SENSOR_PIN, Pin.IN, Pin.PULL_UP)
# ---- IR sensor Configuration

# -----WS2812 Initialize
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

# simple color name -> tuple map
COLOR_MAP = {
    "red": RED, "green": GREEN, "blue": BLUE, "yellow": YELLOW,
    "cyan": CYAN, "magenta": MAGENTA, "white": WHITE, "orange": ORANGE,
    "off": OFF
}

def parse_color(s):
    """
    Convert a user string to an (r,g,b) tuple.
    Accepts:
      - Named colors (red, green, ...)
      - Hex like '#RRGGBB'
      - Comma-separated 'r,g,b'
    Falls back to WHITE on parse error.
    """
    if not s:
        return WHITE
    s = s.strip().lower()
    if s in COLOR_MAP:
        return COLOR_MAP[s]
    if s.startswith('#') and len(s) == 7:
        try:
            return tuple(int(s[i:i+2], 16) for i in (1, 3, 5))
        except Exception:
            return WHITE
    if ',' in s:
        parts = s.split(',')
        try:
            vals = tuple(int(p.strip()) for p in parts)
            if len(vals) == 3 and all(0 <= v <= 255 for v in vals):
                return vals
        except Exception:
            return WHITE
    return WHITE

# -----WS2812 Initialize

# -----IR sensor Initialize
# === The learned IR codes ===
# Map of 32-bit NEC codes (as integers) to human-readable button labels.
keymap = {
    0xFF9867: "0",
    0xFFA25D: "1",
    0xFF629D: "2",
    0xFFE21D: "3",
    0xFF22DD: "4",
    0xFF02FD: "5",
    0xFFC23D: "6",
    0xFFE01F: "7",
    0xFFA857: "8",
    0xFF906F: "9",
    0xFF6897: "star",
    0xFFB04F: "hash",
    0xFF18E7: "up",
    0xFF4AB5: "down",
    0xFF10EF: "left",
    0xFF5AA5: "right",
    0xFF38C7: "stop"
}
# -----IR sensor Initialize

# --- WS2812 functions ---
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

# Convert matrix XY → index for zig-zag layout
def xy_to_i(x, y):
    if y % 2 == 0:
        return y * WIDTH + x
    else:
        return y * WIDTH + (WIDTH - 1 - x)
    
def radial_fade(steps=30, delay=0.05):
    # Compute center of matrix
    cx = (WIDTH - 1) / 2
    cy = (HEIGHT - 1) / 2

    # Precompute distance of each pixel from center
    distances = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            d = math.sqrt((x - cx)**2 + (y - cy)**2)
            distances.append((x, y, d))

    max_dist = max(d for (_, _, d) in distances)

    # Fade steps
    for s in range(steps):
        fade_level = s / steps  # 0 → 1

        for x, y, d in distances:
            i = xy_to_i(x, y)

            r, g, b = np[i]

            # How far along this pixel should fade based on radius
            ratio = d / max_dist

            # Only fade pixels with content
            if r or g or b:
                brightness = max(0, 1 - fade_level * (1 + ratio))
                np[i] = (int(r * brightness), int(g * brightness), int(b * brightness))

        np.write()
        time.sleep(delay)

    # Ensure fully black
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()

# --- WS2812 functions ---

# --- NEC IR decoder functions ---
def capture_transitions():
    """
    Capture a sequence of (level, duration_us) transitions from the IR input pin.

    Returns:
        list of tuples: Each tuple is (level, duration_us) where `level` is the
        previous pin value (0 or 1) and `duration_us` is how long that level
        persisted in microseconds.

    Behavior:
        - Blocks while the line is idle (high) waiting for a low pulse.
        - Records transitions until MAX_WINDOW_MS milliseconds have elapsed.
        - Uses time.ticks_us() for microsecond timing (MicroPython-specific).
    Notes:
        - This is a polling-based capture and will block the interpreter while
          running. Avoid calling from time-critical tasks.
    """
    while ir.value() == 1:
        pass
    transitions = []
    last = 0
    last_t = time.ticks_us()
    deadline = time.ticks_add(last_t, MAX_WINDOW_MS * 1000)
    while time.ticks_diff(deadline, time.ticks_us()) > 0:
        v = ir.value()
        if v != last:
            now = time.ticks_us()
            dur = time.ticks_diff(now, last_t)
            transitions.append((last, dur))
            last = v
            last_t = now
        time.sleep_us(30)
    now = time.ticks_us()
    transitions.append((last, time.ticks_diff(now, last_t)))
    return transitions

def stop():
    """Stop the WS2812 display (turn off all LEDs)."""
    radial_fade()
    clear()

def decode_nec(trans):
    """
    Decode an NEC-formatted frame from a list of transitions.

    Args:
        trans (list): List of (level, duration_us) tuples as produced by
                      capture_transitions().

    Returns:
        int or None: The decoded 32-bit NEC code as an integer, or None if the
                     transitions do not form a valid NEC frame.

    Decoding notes:
        - Expects leader: ~9ms low (mark) then ~4.5ms high (space).
        - Each data bit: ~562µs mark (low) followed by a space:
            ~562µs -> logical 0, ~1.69ms -> logical 1.
        - Uses a simple threshold (1200µs) to distinguish 0 vs 1.
    """
    if len(trans) < 4:
        return None
    low, low_dur = trans[0]
    high, high_dur = trans[1] if len(trans) > 1 else (None, 0)
    # Check NEC leader: ~9ms low then ~4.5ms high
    if low != 0 or not (7000 < low_dur < 10000):
        return None
    if high != 1 or not (3500 < high_dur < 5000):
        return None

    bits = []
    i = 2
    # Parse up to 32 bits: expect pairs (low mark, high space)
    while i + 1 < len(trans) and len(bits) < 32:
        l0, d0 = trans[i]
        l1, d1 = trans[i + 1]
        # Expect mark (low) then space (high)
        if l0 != 0 or l1 != 1:
            i += 1
            continue
        # Threshold: >1200us for logical 1 (space longer), else 0
        bits.append(1 if d1 > 1200 else 0)
        i += 2
    if len(bits) < 32:
        return None
    val = 0
    for b in bits[:32]:
        val = (val << 1) | b
    return val
# --- NEC IR decoder functions ---

# --- Main loop ---
clear()

print("Supported color names: RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE, ORANGE, OFF")
user_input = input("Enter color(name, '#RRGGBB' or 'r,g,b'): ")
display_color = parse_color(user_input)
print("Using color:", display_color)

print("Ready to detect IR remote keys on GPIO", IR_SENSOR_PIN)

while True:
    trans = capture_transitions()
    code = decode_nec(trans)
    if not code:
        continue

    if code in keymap:
        print("Button pressed:", keymap[code])
        show_char(keymap[code], display_color)
        if keymap[code] == "stop":
            stop()
    elif code == 0xFFFFFFFF:
        # NEC repeat code (indicates the previous key is being held)
        print("(repeat)")
    else:
        # Unknown/unmapped code: print in hex for debugging or learning new keys
        print("Unknown code:", hex(code))

    time.sleep_ms(200)

