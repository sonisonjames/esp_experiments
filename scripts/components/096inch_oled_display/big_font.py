# main.py
from machine import Pin, I2C
import ssd1306
import time
from bigtext import draw_big_text, centered_big_text

# I2C pins for typical ESP32
i2c = I2C(0, scl=Pin(22), sda=Pin(23))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def do_demo():
    for scale in range(1, 5, 1):
        oled.fill(0)
        centered_big_text(oled, "HELLO WORLD", scale)
        oled.show()
        time.sleep(3)

    # Example 3: scroll / marquee across screen horizontally
    text = "HELLO WORLD"
    scale = 5
    step = 2
    width_text = len(text) * (8 * scale + 1 * scale)
    # start from right off-screen
    for offset in range(oled.width, -width_text, -step):
        oled.fill(0)
        draw_big_text(oled, text, x=offset, y=16, scale=scale)
        oled.show()
        time.sleep(0.05)

    # Clear at end
    oled.fill(0)
    oled.show()

while True:
    do_demo()
