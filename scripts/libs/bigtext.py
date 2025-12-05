# bigtext.py
# Draw large text on SSD1306 by scaling the built-in 8x8 font.
# Works reliably on MicroPython + ESP32.

import framebuf

def render_big_text_to_fb(text, scale=3):
    """Return (fb, width, height) for a pre-rendered big text framebuffer."""
    import framebuf

    # Calculate required width
    char_w = 8 * scale + scale
    w = len(text) * char_w
    h = 8 * scale

    buf = bytearray((w * h) // 8)
    fb = framebuf.FrameBuffer(buf, w, h, framebuf.MONO_VLSB)

    # Fill blank
    fb.fill(0)

    # Temporary small fb for rendering 8x8 chars
    temp_buf = bytearray(8)
    temp_fb = framebuf.FrameBuffer(temp_buf, 8, 8, framebuf.MONO_VLSB)

    cursor_x = 0
    for ch in text:
        for i in range(8):
            temp_buf[i] = 0
        temp_fb.fill(0)
        temp_fb.text(ch, 0, 0, 1)

        # scale into large fb
        for row in range(8):
            for col in range(8):
                if temp_fb.pixel(col, row):
                    for dy in range(scale):
                        for dx in range(scale):
                            fb.pixel(cursor_x + col*scale + dx, row*scale + dy, 1)

        cursor_x += char_w

    return fb, w, h

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
