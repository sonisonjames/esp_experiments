import serial
import time
import math
import numpy as np

ser = serial.Serial('COM6', 921600)

# --- DEFINE OBJECT (CUBE) ---
verts = np.array([
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],  # Front
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]  # Back
])

# Triangulated faces (2 triangles per square side)
faces = [
    (0, 1, 2), (0, 2, 3), (1, 5, 6), (1, 6, 2), (5, 4, 7), (5, 7, 6),
    (4, 0, 3), (4, 3, 7), (3, 2, 6), (3, 6, 7), (4, 5, 1), (4, 1, 0)
]


def rotate_and_project(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    # Rotation on Y and X
    rot_y = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    rot_x = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])

    transformed = []
    projected = []
    for p in points:
        rp = p @ rot_y @ rot_x
        transformed.append(rp)
        factor = 280 / (rp[2] + 6)
        x = int(rp[0] * factor + 160)
        y = int(rp[1] * factor + 120)
        projected.append((max(0, min(254, x)), max(0, min(254, y))))
    return transformed, projected


angle = 0
light_dir = np.array([0.5, 0.5, 1])
light_dir /= np.linalg.norm(light_dir)

while True:
    trans, proj = rotate_and_project(verts, angle)

    payload = bytearray([0xFF, len(verts), len(faces)])

    # Add Vertices
    for p in proj:
        payload.extend([p[0], p[1]])

    # Add Faces with Shading
    for f in faces:
        v0, v1, v2 = trans[f[0]], trans[f[1]], trans[f[2]]
        normal = np.cross(v1 - v0, v2 - v0)
        # Back-face culling: Only send faces pointing towards camera
        if normal[2] < 0:
            norm_val = np.linalg.norm(normal)
            shade = int(max(0.1, np.dot(normal / norm_val, light_dir)) * 255) if norm_val > 0 else 25
            payload.extend([f[0], f[1], f[2], shade])
        else:
            # If we skip backfaces, we need to adjust the face count
            pass

            # Note: To simplify, the ESP32 code above expects ALL faces.
    # Let's send a slightly modified payload for consistency:
    full_payload = bytearray([0xFF, len(verts), len(faces)])
    for p in proj: full_payload.extend([p[0], p[1]])
    for f in faces:
        v0, v1, v2 = trans[f[0]], trans[f[1]], trans[f[2]]
        normal = np.cross(v1 - v0, v2 - v0)
        # Simple Lambertian shade
        norm_val = np.linalg.norm(normal)
        sh = int(max(0.1, np.dot(normal / norm_val, light_dir)) * 255) if norm_val > 0 else 30
        # If normal points away, make it very dark (fake culling)
        if normal[2] > 0: sh = 10
        full_payload.extend([f[0], f[1], f[2], sh])

    ser.write(full_payload)
    angle += 0.05
    time.sleep(0.01)