# python
"""
Simple IR input checker for MicroPython.

Purpose:
  Listen to an IR receiver (or a simple signal) on a GPIO and print timing
  of logic-level changes. Useful for quick diagnostics of remote control
  signals or simple pulse debugging.

Wiring (example for GPIO13):
  - Signal (S) -> GPIO13 (change PIN_NUM if needed)
  - Ground (-) -> GND
  - VCC (middle) -> 3.3V or 5V

Requirements:
  - MicroPython board with `machine.Pin` and `time` functions:
    `time.ticks_us()`, `time.ticks_diff()`, `time.sleep_ms()`
  - Run on the device (not regular CPython). A small import fallback is
    included to allow static checking / local testing.

Usage:
  - Copy to `sensors/ir_module/scripts/simple_checker.py` on the device
  - Run the script; press remote buttons or short S to GND to see changes

Notes:
  - Adjust `PIN_NUM` to test a different GPIO.
  - The script prints change events with delta time in microseconds.
"""

# Provide a safe fallback for desktop editors / local testing so IDEs don't show
# unresolved reference errors for `machine.Pin`. On MicroPython the real `machine`
# module will be used.
try:
    from machine import Pin
except Exception:
    # Lightweight stub for local testing / static analysis only
    import random
    class Pin:
        IN = 0
        PULL_UP = 1
        def __init__(self, num, mode=None, pull=None):
            self._num = num
            self._val = 1
        def value(self):
            # return a pseudo-random but stable-ish value for local runs
            self._val ^= random.getrandbits(1)
            return self._val

import time

PIN_NUM = 13   # change if you want another GPIO for testing
ir = Pin(PIN_NUM, Pin.IN, Pin.PULL_UP)  # use internal pull-up

def main():
    """Run the IR pin change listener loop (prints change events)."""
    print("Diagnostic: pin", PIN_NUM, "using internal PULL_UP")
    print("Connect S -> pin, - -> GND, middle -> VCC (3.3V or 5V).")
    print("Listening... Press remote buttons. Also try shorting S to GND to test.")

    last = ir.value()
    last_t = time.ticks_us()

    while True:
        v = ir.value()
        if v != last:
            now = time.ticks_us()
            dt = time.ticks_diff(now, last_t)
            print("CHANGE ->", v, "  dt(us):", dt)
            last = v
            last_t = now
        time.sleep_ms(1)

if __name__ == '__main__':
    main()
