# main.py
from machine import Pin, I2C
import ssd1306
import time
from bigtext import draw_big_text, centered_big_text

# I2C pins for typical ESP32
i2c = I2C(0, scl=Pin(22), sda=Pin(23))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Example 1: Big centered title (scale 3 => 24px high)
oled.fill(0)
centered_big_text(oled, "HELLO", scale=3)   # fits nicely
oled.show()
time.sleep(3)

# Example 2: BIGGER (scale 4 => 32px high)
oled.fill(0)
centered_big_text(oled, "WORLD", scale=4)
oled.show()
time.sleep(3)

# Example 3: scroll / marquee across screen horizontally
text = "HELLO WORLD"
scale = 3
step = 2
width_text = len(text) * (8*scale + 1*scale)
# start from right off-screen
for offset in range(oled.width, -width_text, -step):
    oled.fill(0)
    draw_big_text(oled, text, x=offset, y=16, scale=scale)
    oled.show()
    time.sleep(0.05)

# Clear at end
oled.fill(0)
oled.show()
