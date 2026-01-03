import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import serial
import numpy as np
import time

# --- CONFIG ---
SERIAL_PORT = 'COM6'
BAUD_RATE = 921600
WIDTH, HEIGHT = 320, 240
SEND_W, SEND_H = 160, 120  # Scaling down for smooth FPS

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)
    print("Connected!")
except:
    print("Check Serial Port Connection")
    exit()


def init_gl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (5, 5, 10, 1))
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (WIDTH / HEIGHT), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)


def draw_sphere(radius, subdivisions):
    # Manually generating a sphere to avoid glutSolidTeapot crashes
    for i in range(subdivisions):
        lat0 = np.pi * (-0.5 + float(i) / subdivisions)
        z0 = np.sin(lat0)
        zr0 = np.cos(lat0)

        lat1 = np.pi * (-0.5 + float(i + 1) / subdivisions)
        z1 = np.sin(lat1)
        zr1 = np.cos(lat1)

        glBegin(GL_QUAD_STRIP)
        for j in range(subdivisions + 1):
            lng = 2 * np.pi * float(j - 1) / subdivisions
            x = np.cos(lng)
            y = np.sin(lng)
            glNormal3f(x * zr0, y * zr0, z0)
            glVertex3f(radius * x * zr0, radius * y * zr0, radius * z0)
            glNormal3f(x * zr1, y * zr1, z1)
            glVertex3f(radius * x * zr1, radius * y * zr1, radius * z1)
        glEnd()


def get_frame():
    # Read OpenGL buffer
    data = glReadPixels(0, 0, WIDTH, HEIGHT, GL_RGB, GL_UNSIGNED_BYTE)
    img = np.frombuffer(data, dtype=np.uint8).reshape(HEIGHT, WIDTH, 3)
    img = np.flipud(img)

    # Fast resize using slicing (No OpenCV needed)
    img_small = img[::2, ::2]

    # Convert to RGB565
    r = (img_small[:, :, 0] >> 3).astype(np.uint16)
    g = (img_small[:, :, 1] >> 2).astype(np.uint16)
    b = (img_small[:, :, 2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b
    return rgb565.byteswap().tobytes()


def main():
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    init_gl()
    angle = 0

    while True:
        if ser.in_waiting > 0 and ser.read() == b'R':
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            glTranslatef(0, 0, -3.0)
            glRotatef(angle, 1, 1, 0)

            glMaterialfv(GL_FRONT, GL_DIFFUSE, (0.8, 0.2, 0.2, 1.0))
            draw_sphere(1.0, 16)

            pygame.display.flip()
            ser.write(b'\xAA' + get_frame())
            angle += 2

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return


main()