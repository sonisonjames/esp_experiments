# MicroPython SSD1306 OLED driver, I2C and SPI interfaces

import time
import framebuf


class SSD1306:
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.framebuf = framebuf.FrameBuffer(
            self.buffer, self.width, self.height, framebuf.MONO_VLSB
        )
        self.poweron()
        self.init_display()

    def init_display(self):
        self.write_cmd(0xAE)  # display off
        self.write_cmd(0x20)  # set memory addressing mode
        self.write_cmd(0x00)  # horizontal addressing mode
        self.write_cmd(0x40)  # set display start line
        self.write_cmd(0xA1)  # segment remap
        self.write_cmd(0xC8)  # COM output scan direction
        self.write_cmd(0xDA)  # COM pins hardware configuration
        self.write_cmd(0x12)
        self.write_cmd(0x81)  # set contrast
        self.write_cmd(0x7F)
        self.write_cmd(0xA4)  # display follows RAM content
        self.write_cmd(0xA6)  # normal display
        self.write_cmd(0xD5)  # set display clock divide ratio/oscillator freq
        self.write_cmd(0x80)
        self.write_cmd(0x8D)  # charge pump
        self.write_cmd(0x14)
        self.write_cmd(0xAF)  # display ON
        self.fill(0)
        self.show()

    def poweron(self):
        pass

    def write_cmd(self, cmd):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    def fill(self, col):
        self.framebuf.fill(col)

    def pixel(self, x, y, col):
        self.framebuf.pixel(x, y, col)

    def text(self, string, x, y, col=1):
        self.framebuf.text(string, x, y, col)

    def scroll(self, dx, dy):
        self.framebuf.scroll(dx, dy)

    def blit(self, fbuf, x, y):
        self.framebuf.blit(fbuf, x, y)


class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3C, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, bytearray([0x00, cmd]))

    def show(self):
        for page in range(self.pages):
            self.write_cmd(0xB0 | page)
            self.write_cmd(0x00)
            self.write_cmd(0x10)
            start = self.width * page
            end = start + self.width
            self.i2c.writeto(self.addr, b'\x40' + self.buffer[start:end])
