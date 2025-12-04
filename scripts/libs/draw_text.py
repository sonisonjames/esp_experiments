# draw_text.py - helper to draw FreeSans20 on SSD1306
from writer import Writer

class TextDrawer:
    def __init__(self, oled, font):
        self.oled = oled
        self.font = font
        self.writer = Writer(oled, font)

    def draw(self, text, x=0, y=0):
        """
        Draw text at position (x, y)
        Handles multi-line if text has \n
        """
        self.writer.set_textpos(y, x)
        self.writer.printstring(text)
        self.oled.show()

    def clear(self):
        """Clear the screen"""
        self.oled.fill(0)
        self.oled.show()
