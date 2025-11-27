"""
test_movement.py

DRV8833 motor control helper for MicroPython

Overview
--------
Small, self-contained helper for controlling a single DC motor via a DRV8833
dual H-bridge using two PWM-capable GPIO pins. The Motor class exposes simple
methods to drive the motor forward, backward, stop (brake), and coast.

Driver / Hardware
-----------------
- Target driver: DRV8833 dual H-bridge.
- The DRV8833 uses two logic inputs per motor (IN1, IN2). By driving these
  inputs with complementary PWM signals you can control direction and speed.
- Ensure the motor supply (VM) and microcontroller share a common ground.
- Use appropriate decoupling and a power source capable of motor stall current.

Wiring example
- Microcontroller PWM-capable pin A -> DRV8833 IN1
- Microcontroller PWM-capable pin B -> DRV8833 IN2
- Motor connected to the DRV8833 motor outputs
- VM -> motor supply (check DRV8833 voltage limits)
- GND -> common ground with microcontroller

Notes
-----
- MicroPython PWM duty resolution varies by port:
    - ESP8266/ESP32 commonly use 0..1023 (this code uses that range).
    - RP2040 and others may use 0..65535 — adjust duty scaling if needed.
- Methods accept speed as a percentage (0..100).
- brake (stop) sets both outputs low; coast sets both high (device-dependent).
- This module is synchronous/blocking and intended for simple manual tests
  and small projects.

Example
-------
from test_movement import Motor
m = Motor(in1_pin=25, in2_pin=26)
m.forward(50)   # 50% forward
time.sleep(1)
m.stop()
"""
from machine import Pin, PWM
import time


class Motor:
    """
    Motor control abstraction for a single DRV8833-controlled motor.

    Usage:
        motor = Motor(in1_pin=25, in2_pin=26, freq=1000)
        motor.forward(75)   # 75% forward
        motor.backward(40)  # 40% reverse
        motor.stop()        # active brake (both low)
        motor.coast()       # coast (both high)

    Parameters:
        in1_pin (int): GPIO pin number connected to DRV8833 IN1.
        in2_pin (int): GPIO pin number connected to DRV8833 IN2.
        freq (int): PWM frequency in Hz (default 1000).

    Behavior:
        - The constructor configures two PWM objects and calls stop() to
          ensure the motor is initially not driven.
        - forward/backward accept `speed` as integer 0..100 (percentage).
        - Internally speeds are scaled to a 0..1023 duty range (adjust if
          your platform uses a different PWM resolution).
    """

    def __init__(self, in1_pin, in2_pin, freq=1000):
        """
        Initialize PWM outputs for the motor and put the motor into stop state.

        Args:
            in1_pin (int): pin number for IN1
            in2_pin (int): pin number for IN2
            freq (int): PWM frequency in Hz
        """
        self.in1 = PWM(Pin(in1_pin), freq=freq)
        self.in2 = PWM(Pin(in2_pin), freq=freq)
        self.stop()

    def forward(self, speed):
        """
        Rotate motor forward.

        Args:
            speed (int | float): 0..100 percentage of full speed.

        Notes:
            - Values outside 0..100 are clamped.
            - Speed is converted to PWM duty in 0..1023 range.
        """
        s = max(0.0, min(100.0, float(speed)))
        duty = int((s / 100.0) * 1023)  # Convert to 0-1023 range
        self.in1.duty(duty)
        self.in2.duty(0)

    def backward(self, speed):
        """
        Rotate motor backward.

        Args:
            speed (int | float): 0..100 percentage of full speed.
        """
        s = max(0.0, min(100.0, float(speed)))
        duty = int((s / 100.0) * 1023)
        self.in1.duty(0)
        self.in2.duty(duty)

    def stop(self):
        """
        Stop the motor using active braking.

        Behavior:
            - Sets both PWM duties to 0 which results in both H-bridge inputs
              low. On DRV8833 this commonly produces a braking effect.
        """
        self.in1.duty(0)
        self.in2.duty(0)

    def coast(self):
        """
        Let the motor coast/free-spin.

        Behavior:
            - Sets both PWM duties to max (1023) so both inputs are driven
              high. On some drivers this disables braking and allows coasting.
            - Device behaviour for coast/brake can vary; consult DRV8833 datasheet.
        """
        self.in1.duty(1023)
        self.in2.duty(1023)


# Example usage as a script for manual testing
if __name__ == "__main__":
    # Create motor object - adjust pin numbers to match your wiring
    # Example: IN1 connected to GPIO 25, IN2 connected to GPIO 26
    motor = Motor(in1_pin=25, in2_pin=26)

    print("Motor Test Starting...")
    print("After each speed step, you'll be asked if the motor moved.")
    print("Press Enter to continue to the next step.\n")

    # Test forward - increase speed in 10% steps
    print("=== Forward Direction ===")
    for speed in range(0, 101, 10):
        print(f"Forward {speed}% speed")
        motor.forward(speed)
        input("Did the motor move? (Press Enter to continue): ")

    # Stop
    print("\nStopping...")
    motor.stop()
    input("Motor stopped. Press Enter to test backward direction: ")

    # Test backward - increase speed in 10% steps
    print("\n=== Backward Direction ===")
    for speed in range(0, 101, 10):
        print(f"Backward {speed}% speed")
        motor.backward(speed)
        input("Did the motor move? (Press Enter to continue): ")

    # Stop
    print("\nStopping...")
    motor.stop()

    print("\nTest complete!")