from irsensor import decode_nec, capture_transitions, keymap, get_key_pressed, listen_for_keys
from machine import Pin, I2C
import ssd1306
from bigtext import centered_big_text, render_big_text_to_fb
import time


# I2C pins for typical ESP32
i2c = I2C(0, scl=Pin(22), sda=Pin(23))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
scale = 1
speed = 0
direction = 0

"""
direction axis:
                       ^
                       |
                       0 degrees
                       | 
                       |
<-- (-90) degrees -- Origin -- (+90) degrees -->
                       |
                       |
                       +180/-180 degrees
                       |
                       v
"""
def update_display(direction, speed, scale=3):
    oled.fill(0)
    speed_str = "SPEED:{}".format(abs(speed))
    centered_big_text(oled, speed_str, scale, 0)
    dir_str = "DIR:{}".format(direction)
    centered_big_text(oled, dir_str, scale, 9)
    oled.show()

while True:
    update_display(direction, speed, scale)
    key = get_key_pressed()
    print("Pressed key:", key)
    continue

    trans = capture_transitions()
    code = decode_nec(trans)
    update_display(direction, speed, scale)
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
        elif code == 0xFF38C7: # OK/STOP
            direction = 0
            speed = 0
        elif code == 0xFFB04F:  # HASH/Accelerate
            if speed < 100:
                speed = speed + 10
        elif code == 0xFF6897:  # STAR/Decelerate
            if speed > 0:
                speed = speed - 10
        elif code == 0xFF18E7: # UP
            if direction > 0:
                direction = direction - 10
            elif direction < 0:
                direction = direction + 10
        elif code == 0xFF4AB5: # DOWN
            if 0 <= direction < 180:
                direction = direction + 10
            elif -180 < direction < 0:
                direction = direction - 10
        elif code == 0xFF10EF: # LEFT
            if -180 <= direction < 90:
                direction = direction + 10
            elif 180 <= direction < 90:
                direction = direction - 10
        elif code == 0xFF5AA5: # RIGHT
            if 180 >= direction > -90:
                direction = direction - 10
            elif -180 <= direction < -90:
                direction = direction + 10
    elif code == 0xFFFFFFFF:
        # NEC repeat code (indicates the previous key is being held)
        print("(repeat)")
    else:
        # Unknown/unmapped code: print in hex for debugging or learning new keys
        print("Unknown code:", hex(code))

    time.sleep_ms(200)
