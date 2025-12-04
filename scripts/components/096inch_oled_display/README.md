# Overview
This project demonstrates how to use a 0.96 inch OLED display with a microcontroller. The OLED display is connected via I2C interface, allowing for easy communication and control. The display can show text, graphics, and other information, making it suitable for various applications such as status displays, user interfaces, and more.
The module is called GME12864-50. It is 0.96 inches in size and has a resolution of 128x64 pixels. The display uses the SSD1306 driver, which is widely supported and easy to use with various libraries.

# How to connect the OLED display
The OLED display uses the I2C interface for communication. Here are the connections:
| OLED Pin | ESP32 Pin | Description        |
|----------|-----------|--------------------|
| VCC      | 3.3V      | Power supply       |
| GND      | GND       | Ground             |
| SCL      | GPIO 22   | I2C Clock          |
| SDA      | GPIO 23   | I2C Data           |
Make sure to connect the pins correctly to avoid any damage to the components.

# How to install the required libraries
To use the OLED display, you need to install the `ssd1306` library. You can find it in the `libs` directory of this repository.

# How to display text on the OLED display
Here is a simple example of how to display text on the OLED display using MicroPython:
[Open hello_world.py](hello_world.py)


# How to display text on the OLED display in BIG font
The built-in SSD1306 driver only supports one small 8×8 font.
To get BIG text, you must either:

✅ Option A — Scale up the small font (easy)
[open big_text_scale.py](big_text_scale.py)
scale=2 → medium

scale=3 → large

scale=4 → fills almost entire screen

✅ Option B — Use a custom large bitmap font (cleaner, looks better)


