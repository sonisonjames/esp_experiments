import serial
import time
import math
import numpy as np

# --- CONFIG ---
ser = serial.Serial('COM6', 921600)
WIDTH, HEIGHT = 320, 240


# --- OBJECT DEFINITIONS ---
def get_pyramid():
    v = np.array([[0, 1.2, 0], [-1, -1, 1], [1, -1, 1], [0, -1, -1]])
    f = [(0, 1, 2), (0, 2, 3), (0, 3, 1), (1, 3, 2)]
    return v, f


def get_cube():
    v = np.array([[-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1], [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]])
    f = [(0, 1, 2), (0, 2, 3), (1, 5, 6), (1, 6, 2), (5, 4, 7), (5, 7, 6), (4, 0, 3), (4, 3, 7), (3, 2, 6), (3, 6, 7),
         (4, 5, 1), (4, 1, 0)]
    return v, f


def get_diamond():
    v = np.array([[0, 1.5, 0], [1, 0, 1], [1, 0, -1], [-1, 0, -1], [-1, 0, 1], [0, -1.5, 0]])
    f = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (5, 2, 1), (5, 3, 2), (5, 4, 3), (5, 1, 4)]
    return v, f


# --- RENDER LOGIC ---
def rotate_and_project(points, angle):
    # Slower rotation: angle is incremented more slowly now
    c, s = math.cos(angle), math.sin(angle)
    rot_y = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    rot_x = np.array([[1, 0, 0], [0, math.cos(0.3), -math.sin(0.3)], [0, math.sin(0.3), math.cos(0.3)]])

    transformed = []
    projected = []
    for p in points:
        rp = p @ rot_y @ rot_x
        transformed.append(rp)
        factor = 240 / (rp[2] + 6)
        x = int(rp[0] * factor + 160)
        y = int(rp[1] * factor + 120)
        projected.append((max(0, min(254, x)), max(0, min(254, y))))
    return transformed, projected


# --- MAIN LOOP ---
objects = [get_pyramid, get_cube, get_diamond]
obj_index = 0
angle = 0
last_switch = time.time()
light_dir = np.array([0.5, 0.5, 1])
light_dir /= np.linalg.norm(light_dir)

print("Streaming rotating objects... Press Ctrl+C to stop.")

while True:
    # Switch object every 5 seconds
    if time.time() - last_switch > 5:
        obj_index = (obj_index + 1) % len(objects)
        last_switch = time.time()
        print(f"Switching to object {obj_index}")

    verts, faces = objects[obj_index]()
    trans, proj = rotate_and_project(verts, angle)

    payload = bytearray([0xFF, len(verts), len(faces)])
    for p in proj: payload.extend([p[0], p[1]])

    for f in faces:
        v0, v1, v2 = trans[f[0]], trans[f[1]], trans[f[2]]
        normal = np.cross(v1 - v0, v2 - v0)
        norm_val = np.linalg.norm(normal)
        sh = int(max(0.1, np.dot(normal / norm_val, light_dir)) * 255) if norm_val > 0 else 30
        if normal[2] > 0: sh = int(sh * 0.3)  # Darken backfaces
        payload.extend([f[0], f[1], f[2], sh])

    ser.write(payload)

    # SLOW ROTATION: Using a smaller increment
    angle += 0.02
    time.sleep(0.01)