import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import serial
import numpy as np

# --- CONFIGURATION ---
SERIAL_PORT = 'COM6'
BAUD_RATE = 921600
WIDTH, HEIGHT = 320, 240

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)


def init_gl():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0, 0, 0, 1)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (WIDTH / HEIGHT), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)


def draw_test_cube(angle):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -3.0)
    glRotatef(angle, 1, 1, 1)

    glBegin(GL_QUADS)
    # Front Face (Red)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-0.5, -0.5, 0.5);
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5);
    glVertex3f(-0.5, 0.5, 0.5)
    # Back Face (Green)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(-0.5, -0.5, -0.5);
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5);
    glVertex3f(0.5, -0.5, -0.5)
    glEnd()


def get_frame_as_rgb565():
    data = glReadPixels(0, 0, WIDTH, HEIGHT, GL_RGB, GL_UNSIGNED_BYTE)
    img = np.frombuffer(data, dtype=np.uint8).reshape(HEIGHT, WIDTH, 3)
    img = np.flipud(img)

    # Fast Numpy conversion to RGB565
    r = (img[:, :, 0] >> 3).astype(np.uint16)
    g = (img[:, :, 1] >> 2).astype(np.uint16)
    b = (img[:, :, 2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b
    return rgb565.byteswap().tobytes()  # Big-Endian


def main():
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    init_gl()

    angle = 0
    print("Waiting for ESP32...")

    while True:
        # Check for Handshake 'R'
        if ser.in_waiting > 0:
            msg = ser.read()
            if msg == b'R':
                draw_test_cube(angle)
                pygame.display.flip()

                frame_bytes = get_frame_as_rgb565()
                ser.write(frame_bytes)

                angle += 2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return


if __name__ == "__main__":
    main()