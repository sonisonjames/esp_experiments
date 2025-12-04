# writer.py - MicroPython font/text writer for framebuf displays
# From Peter Hinch's micropython-font-to-py project

class Writer:
    def __init__(self, device, font, verbose=False):
        self.device = device
        self.font = font
        self.screenwidth = device.width
        self.screenheight = device.height
        self.row = 0
        self.col = 0

        if verbose:
            import gc
            print("Device: {}x{}".format(self.screenwidth, self.screenheight))
            print("Font height:", font.height())
            print("Font max width:", font.max_width())
            print("RAM free:", gc.mem_free())

    def set_textpos(self, row, col):
        self.row = row
        self.col = col

    def printstring(self, s):
        for c in s:
            if c == '\n':
                self.row += self.font.height()
                self.col = 0
            else:
                glyph, w = self.font.get_ch(c)
                self.device.blit(glyph, self.col, self.row)
                self.col += w
