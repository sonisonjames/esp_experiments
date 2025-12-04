from machine import Pin, I2C
import ssd1306
import framebuf
import time

i2c = I2C(0, scl=Pin(22), sda=Pin(23))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.big_text("HELLO", 0, 0, scale=3)   # 3× size = big!
oled.show()

# Wait for 5 seconds
time.sleep(5)

# Clear the screen
oled.clear()
