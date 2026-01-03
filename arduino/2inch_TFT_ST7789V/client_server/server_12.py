import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import serial
import numpy as np
import time

# --- MATCH ARDUINO BAUD ---
ser = serial.Serial('COM6', 115200, timeout=1)
WIDTH, HEIGHT = 320, 240  # Render size
SEND_W, SEND_H = 160, 120  # Data size


def init_gl():
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (WIDTH / HEIGHT), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)


def draw_cube(angle):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0, -3.0)
    glRotatef(angle, 1, 1, 1)
    glBegin(GL_QUADS)
    glColor3f(1, 0, 0);
    glVertex3f(-0.5, -0.5, 0.5);
    glVertex3f(0.5, -0.5, 0.5);
    glVertex3f(0.5, 0.5, 0.5);
    glVertex3f(-0.5, 0.5, 0.5)
    glColor3f(0, 1, 0);
    glVertex3f(-0.5, -0.5, -0.5);
    glVertex3f(-0.5, 0.5, -0.5);
    glVertex3f(0.5, 0.5, -0.5);
    glVertex3f(0.5, -0.5, -0.5)
    glEnd()


def get_frame():
    data = glReadPixels(0, 0, WIDTH, HEIGHT, GL_RGB, GL_UNSIGNED_BYTE)
    img = np.frombuffer(data, dtype=np.uint8).reshape(HEIGHT, WIDTH, 3)
    img = np.flipud(img)

    # Use simple downsampling
    img_small = img[::2, ::2]

    r = (img_small[:, :, 0] >> 3).astype(np.uint16)
    g = (img_small[:, :, 1] >> 2).astype(np.uint16)
    b = (img_small[:, :, 2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b
    return rgb565.byteswap().tobytes()


pygame.init()
pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
init_gl()
angle = 0

print("Waiting for ESP32...")
while True:
    if ser.in_waiting > 0:
        if ser.read() == b'R':
            draw_cube(angle)
            pygame.display.flip()

            frame = get_frame()
            ser.write(b'\xAA')  # Header
            ser.write(frame)
            angle += 5

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()