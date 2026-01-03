import serial
import time
import math

ser = serial.Serial('COM6', 115200)
WIDTH, HEIGHT = 320, 240

# Vertices for a pyramid (Tetrahedron)
points = [
    [1, 1, 1], [-1, -1, 1], [-1, 1, -1], [1, -1, -1]
]

angle = 0


def rotate(x, y, z, angle):
    # Simultaneous rotation on two axes
    rad = angle
    # Y-axis
    nx = x * math.cos(rad) - z * math.sin(rad)
    nz = x * math.sin(rad) + z * math.cos(rad)
    # X-axis
    ny = y * math.cos(rad * 0.7) - nz * math.sin(rad * 0.7)
    nz = y * math.sin(rad * 0.7) + nz * math.cos(rad * 0.7)
    return nx, ny, nz


while True:
    payload = bytearray([0xFF])

    for p in points:
        rx, ry, rz = rotate(p[0], p[1], p[2], angle)

        # Perspective
        factor = 150 / (rz + 4)
        px = int(rx * factor + WIDTH / 2)
        py = int(ry * factor + HEIGHT / 2)

        payload.append(max(0, min(254, px)))
        payload.append(max(0, min(254, py)))

    ser.write(payload)
    angle += 0.05
    time.sleep(0.01)