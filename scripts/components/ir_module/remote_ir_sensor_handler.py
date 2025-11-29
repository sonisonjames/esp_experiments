# ...existing code...
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
import time

PIN_NUM = 13          # HX1838 signal pin (GPIO number)
MAX_WINDOW_MS = 200   # Maximum capture window (ms) for a single IR frame
ir = Pin(PIN_NUM, Pin.IN, Pin.PULL_UP)

# === Your learned IR codes ===
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
    0xFF6897: "*",
    0xFFB04F: "#",
    0xFF18E7: "UP",
    0xFF4AB5: "DOWN",
    0xFF10EF: "LEFT",
    0xFF5AA5: "RIGHT",
    0xFF38C7: "OK"
}

# --- NEC decoder functions ---
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

# --- Main loop ---
print("Ready to detect IR remote keys on GPIO", PIN_NUM)

while True:
    trans = capture_transitions()
    code = decode_nec(trans)
    if not code:
        continue

    if code in keymap:
        print("Button pressed:", keymap[code])
    elif code == 0xFFFFFFFF:
        # NEC repeat code (indicates the previous key is being held)
        print("(repeat)")
    else:
        # Unknown/unmapped code: print in hex for debugging or learning new keys
        print("Unknown code:", hex(code))

    time.sleep_ms(200)
# ...existing code...
