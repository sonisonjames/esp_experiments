"""
ir_detect_keys.py

Simple NEC-protocol IR remote decoder for MicroPython running on ESP chips.
Designed to read an HX1838 (or similar) IR receiver module on a GPIO pin and
print decoded key names based on a learned keymap.

Usage:
- Connect the HX1838 signal pin to the GPIO defined by PIN_NUM.
- Run this script on the device; it will block in a loop and print detected keys.
- KEYMAP contains the known 32-bit NEC codes -> human-readable labels.

Notes:
- This implementation samples transitions and attempts a basic NEC timing
  decode. It is intended for experimentation and learning, not production use.
- Timings (µs) and thresholds are tuned for typical NEC signals but may need
  adjustment for different remotes or hardware.
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
        list of tuples: Each tuple is (level, duration_us) where level is the
        previous pin value (0 or 1) and duration_us is how long that level
        persisted in microseconds.
    Behavior:
        - Waits for the line to go low (IR pulse start).
        - Samples changes until MAX_WINDOW_MS has elapsed.
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
        - Expects leading 9ms low pulse followed by ~4.5ms high space.
        - Follows with 32 bits encoded as a 562µs mark (low) + space:
            ~562µs -> logical 0, ~1.69ms -> logical 1.
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
