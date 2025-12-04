# bigtext.py
# Draw large text on SSD1306 by scaling the built-in 8x8 font.
# Works reliably on MicroPython + ESP32.

import framebuf

def draw_big_text(oled, text, x=0, y=0, scale=3, spacing=1):
    """
    Draw `text` on `oled` at (x,y) using the built-in 8x8 font scaled up.
    - scale: integer multiplier (2..8). 3 -> 24px tall (good for FreeSans20-like)
    - spacing: extra pixels between characters (at scaled units)
    """
    # Temporary 8x8 framebuf to render each char using built-in font
    temp_buf = bytearray(8)              # 8 rows, 1 byte per row (MONO_VLSB)
    temp_fb = framebuf.FrameBuffer(temp_buf, 8, 8, framebuf.MONO_VLSB)

    cursor_x = x
    for ch in text:
        # Clear temp buffer then draw the single character into it
        for i in range(len(temp_buf)):
            temp_buf[i] = 0
        temp_fb.fill(0)
        temp_fb.text(ch, 0, 0, 1)

        # For every pixel in the 8x8 temp buffer, if set -> draw a scale×scale block
        for row in range(8):
            for col in range(8):
                if temp_fb.pixel(col, row):
                    # Draw scaled block on OLED
                    base_x = cursor_x + col * scale
                    base_y = y + row * scale
                    for dy in range(scale):
                        for dx in range(scale):
                            # Make sure not to write outside bounds (safe)
                            if 0 <= base_x + dx < oled.width and 0 <= base_y + dy < oled.height:
                                oled.pixel(base_x + dx, base_y + dy, 1)

        # Advance cursor: char width (8*scale) + spacing*scale
        cursor_x += 8 * scale + spacing * scale

def centered_big_text(oled, text, scale=3, y=None):
    """Helper: draw centered horizontally. If y is None, center vertically."""
    if y is None:
        y = (oled.height - 8*scale) // 2
    total_width = len(text) * (8*scale) + (len(text)-1) * (1*scale)
    x = max(0, (oled.width - total_width) // 2)
    draw_big_text(oled, text, x=x, y=y, scale=scale)
