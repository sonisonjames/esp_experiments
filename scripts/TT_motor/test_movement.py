"""
test_movement.py

Simple motor control demo for a two-wire DC motor driver (H-bridge) using PWM.

Description
-----------
This script demonstrates basic forward/backward/stop control of a DC motor
connected to an H-bridge driver. It provides small helper functions to set the
motor direction and speed using two GPIO direction pins and one PWM-enabled
enable pin.

Hardware wiring (example)
-------------------------
- IN1  -> H-bridge input 1 (direction)
- IN2  -> H-bridge input 2 (direction)
- ENA  -> H-bridge enable / PWM input (speed control)
- Motor outputs connected to the H-bridge motor terminals
- Supply the H-bridge with an appropriate motor supply voltage and common
  ground with the microcontroller.

Notes
-----
- PWM duty range differs by board/port in MicroPython:
    - Some ports use 0..1023 (ESP32/ESP8266 legacy), others 0..65535 (RP2040).
  Adjust ENA.duty(...) scaling to match your board if the motor is not moving
  as expected.
- Keep the motor power supply rating and wiring safe. Motors can draw high
  stall currents—use appropriate wiring and protection.
"""
from machine import Pin, PWM
import time

# Motor driver pins (change values to match your hardware)
IN1 = Pin(18, Pin.OUT)   # Direction pin 1
IN2 = Pin(19, Pin.OUT)   # Direction pin 2
ENA = PWM(Pin(20))       # PWM pin for speed control (enable)

# Configure PWM frequency for the motor driver (in Hz)
ENA.freq(1000)  # 1 kHz is a common choice for motor control

def motor_forward(speed):
    """
    Drive the motor forward at the requested speed.

    Parameters:
        speed (float): 0.0 .. 1.0 where 0.0 is stop and 1.0 is full speed.

    Behavior:
        - Sets IN1 high and IN2 low to select the forward direction.
        - Sets the PWM duty on ENA according to `speed`.
    """
    IN1.value(1)
    IN2.value(0)

    # Scale speed into PWM duty range (0..1023). If your board uses a
    # different duty scale (e.g. 0..65535) change the multiplier.
    ENA.duty(int(1023 * max(0.0, min(1.0, speed))))

def motor_backward(speed):
    """
    Drive the motor in reverse at the requested speed.

    Parameters:
        speed (float): 0.0 .. 1.0 where 0.0 is stop and 1.0 is full reverse.
    """
    IN1.value(0)
    IN2.value(1)
    ENA.duty(int(1023 * max(0.0, min(1.0, speed))))

def motor_stop():
    """
    Stop the motor immediately.

    Behavior:
        - Sets both direction pins low and PWM duty to zero.
    """
    IN1.value(0)
    IN2.value(0)
    ENA.duty(0)

# Demo sequence to exercise the motor functions
def demo_move():
    """
    Run a short demo sequence:
      - forward at 80% for 2s
      - backward at 80% for 2s
      - stop for 1s

    Intended for manual testing; call demo_move() from the REPL or run the
    script directly.
    """
    print("Forward")
    motor_forward(0.8)
    time.sleep(2)

    print("Backward")
    motor_backward(0.8)
    time.sleep(2)

    print("Stop")
    motor_stop()
    time.sleep(1)

# Run demo when executed as a script (prevents running on import)
if __name__ == "__main__":
    # Running twice as in the original example
    demo_move()
    demo_move()