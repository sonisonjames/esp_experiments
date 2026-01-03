import serial
import time
import math
import numpy as np

# --- CONFIG ---
ser = serial.Serial('COM6', 115200)  # Ensure this matches your port
WIDTH, HEIGHT = 320, 240


def dot_product_matrix(v, m):
    return [sum(v[i] * m[i][j] for i in range(3)) for j in range(3)]


# Pyramid vertices
vertices = np.array([
    [0, 1.2, 0], [-1, -0.8, 1], [1, -0.8, 1], [0, -0.8, -1]
])

# Define the 4 faces by vertex indices
faces = [(0, 1, 2), (0, 2, 3), (0, 3, 1), (1, 3, 2)]
light_dir = np.array([0, 0, 1])  # Light from camera

angle = 0
print("Streaming Solid Shaded Pyramid...")

while True:
    c, s = math.cos(angle), math.sin(angle)
    # Rotation Matrix for Y axis
    ry = [[c, 0, s], [0, 1, 0], [-s, 0, c]]

    projected_points = []
    transformed = []

    for v in vertices:
        rv = dot_product_matrix(v, ry)
        transformed.append(rv)
        # Perspective projection
        # Shrunk scale to fit in the Sprite
        factor = 80 / (rv[2] + 4)
        px = int(rv[0] * factor + WIDTH / 2)
        py = int(rv[1] * factor + HEIGHT / 2)
        projected_points.append([px, py])

    # Calculate shading for each face
    face_shades = []
    for face in faces:
        v0 = np.array(transformed[face[0]])
        v1 = np.array(transformed[face[1]])
        v2 = np.array(transformed[face[2]])

        # Normal vector calculation
        normal = np.cross(v1 - v0, v2 - v0)
        norm_val = np.linalg.norm(normal)
        if norm_val > 0:
            normal = normal / norm_val

        # Shading intensity (dot product)
        brightness = max(0.1, np.dot(normal, light_dir))
        face_shades.append(int(brightness * 255))

    # Package: Header (0xFF) + 8 coords + 4 shades
    payload = bytearray([0xFF])
    for p in projected_points:
        payload.append(max(0, min(254, p[0])))
        payload.append(max(0, min(254, p[1])))
    for sh in face_shades:
        payload.append(sh)

    ser.write(payload)
    # Increase the speed of movement
    angle += 0.1
    time.sleep(0.02)