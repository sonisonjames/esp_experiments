from machine import Pin, I2C
import ssd1306
import time
from bigtext import centered_big_text, render_big_text_to_fb

# I2C pins for typical ESP32
i2c = I2C(0, scl=Pin(22), sda=Pin(23))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def do_demo():
    for scale in range(1, 5, 1):
        oled.fill(0)
        centered_big_text(oled, "HELLO WORLD", scale)
        oled.show()
        time.sleep(3)

    text = "HELLO WORLD"
    scale = 3

    # Pre-render full text once
    fb, tw, th = render_big_text_to_fb(text, scale)

    # Scroll across the screen
    for x in range(oled.width, -tw, -2):   # reduce -2 to -4 or -6 for faster motion
        oled.fill(0)
        oled.blit(fb, x, (oled.height - th) // 2)
        oled.show()

while True:
    do_demo()