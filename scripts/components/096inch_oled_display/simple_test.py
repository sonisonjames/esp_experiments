from machine import Pin, I2C
import ssd1306
import time

# Initialize I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Create OLED object
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Clear screen first
oled.fill(0)

# Show text
oled.text("Hello World", 0, 0)
oled.show()

# Wait for 5 seconds
time.sleep(5)

# Clear the screen
oled.fill(0)
oled.show()
