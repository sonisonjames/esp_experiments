# python
"""
simple_decoder.py — Robust NEC IR protocol reader for MicroPython

This module implements a simple, robust NEC (NEC/NECx) infrared remote
control decoder suitable for MicroPython on boards with a `machine.Pin`
and `time` module (for example, ESP8266/ESP32).

Usage:
- Configure `PIN_NUM` to the GPIO number connected to the IR receiver.
- Run the module; it will block in a loop, capturing IR pulse transitions
  and attempting to decode NEC 32-bit codes. Decoded codes are printed
  in hexadecimal.

Design notes:
- The decoder captures raw level transitions (level, duration_us) for a
  short window after the first falling edge (burst start). It then looks
  for the NEC leader (long low then long high) and decodes subsequent
  pulses into 32 bits (address + command).
- Tolerances are intentionally wide to accommodate timing jitter and
  cheap IR receivers.
"""

from machine import Pin
import time

PIN_NUM = 13          # GPIO13 (D13) — change if needed
MAX_WINDOW_MS = 200   # capture window (milliseconds) for one burst

ir = Pin(PIN_NUM, Pin.IN, Pin.PULL_UP)


def capture_transitions():
    """
    Capture consecutive signal transitions from the IR receiver.

    Waits until a falling edge is observed (start of an IR burst) and then
    records pairs of (level, duration_us) until `MAX_WINDOW_MS` elapses.

    Returns:
        list of tuples (level: int, duration_us: int)
            A list describing each contiguous level and how long it lasted,
            measured in microseconds. Levels are `0` for LOW and `1` for HIGH.

    Notes:
    - The first returned tuple represents the level immediately after the
      detected falling edge (typically LOW) and its duration.
    - Uses `time.ticks_us()` and `time.ticks_diff()` for robust microsecond
      timing on MicroPython.
    - Sleeps `time.sleep_us(30)` between polls to avoid starving the CPU;
      this value balances missed edges and CPU usage.
    """
    # wait for idle-high -> falling edge (start of a burst)
    while ir.value() == 1:
        pass
    # now we saw a falling edge; capture until timeout
    transitions = []
    last = ir.value()
    last_t = time.ticks_us()
    deadline = time.ticks_add(last_t, MAX_WINDOW_MS * 1000)
    # include the initial change
    # we already passed a falling edge so set last and last_t accordingly
    last = 0
    last_t = time.ticks_us()
    while time.ticks_diff(deadline, time.ticks_us()) > 0:
        v = ir.value()
        if v != last:
            now = time.ticks_us()
            dur = time.ticks_diff(now, last_t)
            transitions.append((last, dur))  # record previous level and how long it lasted
            last = v
            last_t = now
        # small delay to avoid starving CPU
        # don't sleep too long or we miss edges
        time.sleep_us(30)
    # record final level duration (approx)
    now = time.ticks_us()
    dur = time.ticks_diff(now, last_t)
    transitions.append((last, dur))
    return transitions


def pretty_print(trans):
    """
    Print a human-readable listing of captured transitions.

    Args:
        trans (list of (int, int)): Output from `capture_transitions()`.

    Output format:
        Captured N transitions:
        00: lvl=0   009000us
        01: lvl=1   004500us
        ...
    """
    print("Captured", len(trans), "transitions:")
    for i, (lvl, dur) in enumerate(trans):
        print("{:02d}: lvl={}  {:6d}us".format(i, lvl, dur))


def decode_nec_from_transitions(trans):
    """
    Attempt to decode an NEC 32-bit code from captured transitions.

    The function expects `trans` to start with the NEC leader sequence:
    - A long LOW (leader low, ~9000us), then
    - A long HIGH (leader high, ~4500us),
    followed by 32 data bits where each bit is represented by:
    - LOW pulse ~560us, then
    - HIGH pulse: short (~560us) for a 0 bit, long (~1690us) for a 1 bit.

    Args:
        trans (list of (int, int)): List of (level, duration_us) tuples.

    Returns:
        int or None:
            The decoded 32-bit integer (most-significant-bit first) if a valid
            NEC leader and 32 bits are found; otherwise `None`.

    Notes on tolerances:
    - Leader low: accepted 7000..10000 us
    - Leader high: accepted 3500..5000 us
    - Bit high threshold: >1200 us considered a '1', otherwise '0'
    - The function is forgiving about alignment and will skip misaligned
      entries until it can read 32 bits or decides decoding failed.
    """
    if len(trans) < 10:
        return None
    # Find leader: should start with a long LOW (~9000) then a long HIGH (~4500)
    # transitions list contains tuples (level, duration) in order.
    # We expect trans[0] to be (0, ~9000) and trans[1] (1, ~4500)
    leader_low, leader_low_dur = trans[0]
    leader_high, leader_high_dur = trans[1] if len(trans) > 1 else (None, 0)
    if leader_low != 0 or leader_low_dur < 7000 or leader_low_dur > 10000:
        return None
    if leader_high != 1 or leader_high_dur < 3500 or leader_high_dur > 5000:
        return None
    # Bits start at trans[2] onward: pattern LOW (~560) then HIGH (560 => 0, ~1690 => 1)
    bits = []
    i = 2
    # ensure we have pairs of (0 dur, 1 dur)
    while i + 1 < len(trans) and len(bits) < 32:
        lvl0, dur0 = trans[i]
        lvl1, dur1 = trans[i + 1]
        # we expect lvl0==0 and lvl1==1
        if lvl0 != 0 or lvl1 != 1:
            # skip bad alignment
            i += 1
            continue
        # interpret high duration
        if dur1 > 1200:   # long high → bit 1
            bits.append(1)
        else:             # short high → bit 0
            bits.append(0)
        i += 2
    if len(bits) < 32:
        return None
    # construct value from first 32 bits
    val = 0
    for b in bits[:32]:
        val = (val << 1) | b
    return val


print("Robust NEC reader on GPIO", PIN_NUM)
print("Press a button on the remote...")

while True:
    trans = capture_transitions()
    if not trans:
        continue
    pretty_print(trans)
    code = decode_nec_from_transitions(trans)
    if code is not None:
        print("Decoded NEC 32-bit code:", hex(code))
    else:
        print("Could not decode NEC from this capture.")
    print("-" * 30)
    time.sleep_ms(200)
