import serial
import time
import math

ser = serial.Serial('COM6', 115200)
WIDTH, HEIGHT = 320, 240

# Define vertices in a specific order:
# 0-3: Front (Top-L, Top-R, Bot-R, Bot-L)
# 4-7: Back  (Top-L, Top-R, Bot-R, Bot-L)
points = [
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]
]

angle = 0


def rotate(x, y, z, ax, ay):
    # Rotate Y
    nx = x * math.cos(ay) - z * math.sin(ay)
    nz = x * math.sin(ay) + z * math.cos(ay)
    # Rotate X
    ny = y * math.cos(ax) - nz * math.sin(ax)
    nz = y * math.sin(ax) + nz * math.cos(ax)
    return nx, ny, nz


while True:
    payload = bytearray([0xFF])  # Sync Header

    for p in points:
        rx, ry, rz = rotate(p[0], p[1], p[2], angle, angle * 0.5)

        # Perspective projection
        factor = 120 / (rz + 3)
        px = int(rx * factor + WIDTH / 2)
        py = int(ry * factor + HEIGHT / 2)

        # Clamp to 0-254 (avoid 255 because it's our header)
        payload.append(max(0, min(254, px)))
        payload.append(max(0, min(254, py)))

    ser.write(payload)
    angle += 0.05
    time.sleep(0.03)