# python
"""
sensors/ir_module/scripts/remote_keys_decoder.py

IR Code Learner and NEC decoder for a microcontroller running MicroPython.

Purpose
- Capture raw transitions from an IR receiver (e.g., HX1838) connected to a GPIO pin.
- Decode NEC-formatted IR signals into 32-bit integer codes.
- Provide a simple interactive learning loop that maps expected button names
  to learned NEC codes.

Hardware / environment assumptions
- MicroPython (or similar) with `machine.Pin`, `time.ticks_us`, `time.sleep_us`, etc.
- An IR receiver data pin connected to the GPIO defined by `PIN_NUM`.
- The IR receiver idles at logic high and produces low/high pulses when a signal is received.

Key functions
- capture_transitions(): sample the IR input and return a list of (level, duration_us) tuples.
- decode_nec(trans): attempt to decode a NEC protocol code from captured transitions.

Usage
- Run the script on the device and press the remote buttons when prompted.
- The learning loop maps buttons listed in `EXPECTED_BUTTONS` to their NEC codes
  and prints the final mapping.

Notes
- Timing thresholds are tuned for typical NEC timings but may require adjustment
  for different receivers or environmental conditions.
- The decoder is tolerant to some spurious transitions but expects a leading
  ~9ms low and ~4.5ms high NEC header before 32 bit timing pairs.
"""

from machine import Pin
import time

PIN_NUM = 13          # GPIO13 for HX1838 signal pin
MAX_WINDOW_MS = 200
EXPECTED_BUTTONS = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "*", "#", "UP", "DOWN", "LEFT", "RIGHT", "OK"
]

ir = Pin(PIN_NUM, Pin.IN, Pin.PULL_UP)

def capture_transitions():
    """
    Capture a window of level transitions from the IR input pin.

    Returns:
        list of tuples (level, duration_us)
            - level: 0 or 1 indicating the logic level during the interval
            - duration_us: duration in microseconds that the pin held that level

    Behavior:
    - Waits until the pin goes low (start of signal).
    - Samples transitions until MAX_WINDOW_MS has elapsed since the start.
    - Uses `time.ticks_us` for microsecond timing and `time.sleep_us(30)` to
      yield between checks to avoid busy-waiting too tightly.
    """
    # Wait for signal start (pin goes low)
    while ir.value() == 1:
        pass

    transitions = []
    last = 0
    last_t = time.ticks_us()
    deadline = time.ticks_add(last_t, MAX_WINDOW_MS * 1000)

    # Record transitions (level and duration) until the deadline
    while time.ticks_diff(deadline, time.ticks_us()) > 0:
        v = ir.value()
        if v != last:
            now = time.ticks_us()
            dur = time.ticks_diff(now, last_t)
            transitions.append((last, dur))
            last = v
            last_t = now
        # small delay to reduce CPU usage while remaining responsive
        time.sleep_us(30)

    # Append final segment duration
    now = time.ticks_us()
    transitions.append((last, time.ticks_diff(now, last_t)))
    return transitions

def decode_nec(trans):
    """
    Decode a NEC protocol 32-bit code from a list of transitions.

    Args:
        trans: list of (level, duration_us) tuples as produced by capture_transitions()

    Returns:
        int: 32-bit NEC code if successfully decoded, otherwise None

    Decoding details / thresholds:
    - Expects a leading header: ~9ms low then ~4.5ms high.
    - Data bits are encoded as pairs: ~560us low followed by a high of ~560us (logical 0)
      or ~1690us (logical 1). The implementation uses a simple threshold of 1200us
      to distinguish 0 vs 1.
    - The function tolerates some noise by skipping non 0/1 pairs.
    """
    if len(trans) < 4:
        return None

    low, low_dur = trans[0]
    high, high_dur = trans[1] if len(trans) > 1 else (None, 0)

    # Validate NEC header: ~9ms low followed by ~4.5ms high
    if low != 0 or not (7000 < low_dur < 10000):
        return None
    if high != 1 or not (3500 < high_dur < 5000):
        return None

    bits = []
    i = 2
    # Parse subsequent low/high pairs into bits until we have 32 bits or run out
    while i + 1 < len(trans) and len(bits) < 32:
        l0, d0 = trans[i]
        l1, d1 = trans[i + 1]
        # Expect low then high for each bit; if not present, skip one entry and continue
        if l0 != 0 or l1 != 1:
            i += 1
            continue
        # Use threshold 1200us on high pulse to distinguish bit value
        bits.append(1 if d1 > 1200 else 0)
        i += 2

    if len(bits) < 32:
        return None

    # Pack bits into a 32-bit integer (MSB first)
    val = 0
    for b in bits[:32]:
        val = (val << 1) | b
    return val

# Main learning loop
print("IR Code Learner")
print("Press each of the following buttons once:")
print(", ".join(EXPECTED_BUTTONS))
print("-" * 40)

learned = {}

while len(learned) < len(EXPECTED_BUTTONS):
    trans = capture_transitions()
    code = decode_nec(trans)
    if not code:
        continue
    if code not in learned.values():
        btn = EXPECTED_BUTTONS[len(learned)]
        learned[btn] = code
        print(f"Learned {btn}: {hex(code)} ({len(learned)}/{len(EXPECTED_BUTTONS)})")
    time.sleep_ms(500)

print("\nAll buttons captured!\n")
print("Final mapping:")
for k, v in learned.items():
    print(f"{k}: 0x{v:08X}")
