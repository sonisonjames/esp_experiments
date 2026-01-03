import serial
import time
import math

# --- CONFIG ---
ser = serial.Serial('COM6', 115200)  # Match your port
WIDTH, HEIGHT = 320, 240

# Define 8 corners of a cube (x, y, z)
points = [
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]
]

angle = 0


def rotate(x, y, z, angle):
    # Rotate around Y axis
    nx = x * math.cos(angle) - z * math.sin(angle)
    nz = x * math.sin(angle) + z * math.cos(angle)
    # Rotate around X axis
    ny = y * math.cos(angle) - nz * math.sin(angle)
    nz = y * math.sin(angle) + nz * math.cos(angle)
    return nx, ny, nz


def project(x, y, z):
    # Simple perspective projection
    factor = 200 / (z + 4)
    px = int(x * factor + WIDTH / 2)
    py = int(y * factor + HEIGHT / 2)
    return px, py


print("Streaming 3D Cube to ESP32...")

while True:
    data_to_send = []
    for p in points:
        rx, ry, rz = rotate(p[0], p[1], p[2], angle)
        px, py = project(rx, ry, rz)

        # Constrain to byte range (0-255) for simplicity
        data_to_send.append(max(0, min(255, px)))
        data_to_send.append(max(0, min(255, py)))

    ser.write(bytearray(data_to_send))
    angle += 0.05
    time.sleep(0.05)  # Control framerate