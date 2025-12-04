from machine import Pin, I2C
import ssd1306
import time
from freesans20 import FreeSans20
from draw_text import TextDrawer

# Initialize I2C and OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(23))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Create TextDrawer
drawer = TextDrawer(oled, FreeSans20)

# Example 1: Display HELLO for 5 seconds
drawer.clear()
drawer.draw("HELLO", x=0, y=0)
time.sleep(5)

# Example 2: Clear and display another message
drawer.clear()
drawer.draw("WORLD!", x=0, y=0)
time.sleep(5)

# Example 3: Simple animation - scrolling text
for i in range(0, 64, 2):   # move down
    drawer.clear()
    drawer.draw("HELLO", x=0, y=i)
    time.sleep(0.1)
