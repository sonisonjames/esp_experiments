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
    if key != None:
        print("Pressed key:", key)
    else:
        continue

    if key == '1':
        speed  = 10
    elif key == '2':
        speed  = 20
    elif key == '3':
        speed  = 30
    elif key == '4':
        speed  = 40
    elif key == '5':
        speed  = 50
    elif key == '6':
        speed  = 60
    elif key == '7':
        speed  = 70
    elif key == '8':
        speed  = 80
    elif key == '9':
        speed  = 90
    elif key == '0':
        speed  = 100
    elif key == 'OK': # OK/STOP, reset speed to 0 and direction to 0
        direction = 0
        speed = 0
    elif key == '#': # HASH/Accelerate
        if speed < 100:
            speed = speed + 10
    elif key == '*': # STAR/Decelerate
        if speed > 0:
            speed = speed - 10
    elif key == 'UP': # UP
        if direction > 0:
            direction = direction - 10
        elif direction < 0:
            direction = direction + 10
    elif key == 'DOWN': # DOWN
        if 0 <= direction < 180:
            direction = direction + 10
        elif -180 < direction < 0:
            direction = direction - 10
    elif key == 'LEFT': # LEFT
        if direction == -180:
            # flip direction for faster turning
            direction = 180
        if -180 < direction < 90:
            direction = direction + 10
        elif 180 <= direction < 90:
            direction = direction - 10
    elif key == 'RIGHT': # RIGHT
        if 180 >= direction > -90:
            direction = direction - 10
        elif -180 <= direction < -90:
            direction = direction + 10
    else:
        # Unknown/unmapped code: print in hex for debugging or learning new keys
        print("Unknown key:", key)

    time.sleep_ms(200)
