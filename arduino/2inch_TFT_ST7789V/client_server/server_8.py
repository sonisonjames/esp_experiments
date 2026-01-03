import serial
import time
import math
import numpy as np

# --- CONFIG ---
# Increase to 921600 for smoother performance
ser = serial.Serial('COM6', 921600, timeout=1)
WIDTH, HEIGHT = 320, 240


def dot_product_matrix(v, m):
    return [sum(v[i] * m[i][j] for i in range(3)) for j in range(3)]


# Pyramid vertices (larger base)
vertices = np.array([
    [0, 1.5, 0], [-1, -1, 1], [1, -1, 1], [0, -1, -1]
])

faces = [(0, 1, 2), (0, 2, 3), (0, 3, 1), (1, 3, 2)]
light_dir = np.array([0.5, 0.5, 1])  # Slightly angled light
light_dir = light_dir / np.linalg.norm(light_dir)

angle = 0

while True:
    c, s = math.cos(angle), math.sin(angle)
    ry = [[c, 0, s], [0, 1, 0], [-s, 0, c]]

    projected_points = []
    transformed = []

    for v in vertices:
        rv = dot_product_matrix(v, ry)
        transformed.append(rv)

        # INCREASED FACTOR: Changed from 80/150 to 250 for a larger size
        factor = 250 / (rv[2] + 5)
        px = int(rv[0] * factor + WIDTH / 2)
        py = int(rv[1] * factor + HEIGHT / 2)
        projected_points.append([px, py])

    face_shades = []
    for face in faces:
        v0, v1, v2 = [np.array(transformed[i]) for i in face]
        normal = np.cross(v1 - v0, v2 - v0)
        norm_val = np.linalg.norm(normal)
        if norm_val > 0:
            normal = normal / norm_val

        brightness = max(0.1, np.dot(normal, light_dir))
        face_shades.append(int(brightness * 255))

    payload = bytearray([0xFF])
    for p in projected_points:
        payload.append(max(0, min(254, p[0])))
        payload.append(max(0, min(254, p[1])))
    for sh in face_shades:
        payload.append(sh)

    ser.write(payload)
    angle += 0.08
    time.sleep(0.01)