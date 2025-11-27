from lib.irsensor import decode_nec, capture_transitions, keymap
from lib.ttmotor import Motor
import time


def run_motor(motor, speed, direction):
    if direction == "FWD":
        print(f"Forward {speed}% speed")
        motor.forward(speed)
    elif direction == "REV":
        print(f"Backward {speed}% speed")
        motor.backward(-speed)
    elif direction == "STOP":
        print("\nStopping...")
        motor.stop()

print("This is new code")

speed = 0
direction = "FWD"
motor = Motor(in1_pin=25, in2_pin=26)

while True:
    run_motor(motor, speed, direction)
    trans = capture_transitions()
    code = decode_nec(trans)
    if not code:
        continue

    if code in keymap:
        print("Button pressed:", keymap[code])
        if code == 0xFFA25D:
            speed = 10
        elif code == 0xFF629D:
            speed = 20
        elif code == 0xFFE21D:
            speed = 30
        elif code == 0xFF22DD:
            speed = 40
        elif code == 0xFF02FD:
            speed = 50
        elif code == 0xFFC23D:
            speed = 60
        elif code == 0xFFE01F:
            speed = 70
        elif code == 0xFFA857:
            speed = 80
        elif code == 0xFF906F:
            speed = 90
        elif code == 0xFF9867:
            speed = 100
        elif code == 0xFF38C7:
            direction = "STOP"
        elif code == 0xFF18E7:
            speed = speed + 10
            if speed > 0:
                direction = "FWD"
        elif code == 0xFF4AB5:
            speed = speed - 10
            if speed < 0:
                direction = "REV"
    elif code == 0xFFFFFFFF:
        # NEC repeat code (indicates the previous key is being held)
        print("(repeat)")
    else:
        # Unknown/unmapped code: print in hex for debugging or learning new keys
        print("Unknown code:", hex(code))

    
    time.sleep_ms(200)
