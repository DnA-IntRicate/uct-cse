import numpy as np

from viewscope_core.pose import forward_vector


def _template():
    vertices = np.array(
        [[1, 1, 1], [-1, 1, 1], [-1, -1, 1], [1, -1, 1],
         [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, -1],
         [0, 0, 1.5], [0, 0, 0]], dtype=np.float64)
    aspect = 1368.0 / 912.0
    vertices[:4, 0] *= aspect
    vertices[:4] *= 0.4
    vertices[4:8, 0] *= aspect
    vertices[:, 2] *= 0.7
    vertices -= vertices.mean(axis=0)
    groups = [
        [0, 1, 3, 1, 2, 3], [0, 3, 4, 0, 4, 5], [0, 5, 1, 1, 5, 6],
        [1, 6, 2, 2, 6, 7], [2, 7, 3, 3, 7, 4], [4, 7, 5, 5, 7, 6],
        [0, 1, 8, 1, 2, 8], [2, 3, 8, 3, 0, 8],
    ]
    faces = np.array([g[i:i + 3] for g in groups for i in (0, 3)], dtype=np.int64)
    body = np.array([26, 230, 230], dtype=np.uint8)
    lens = np.array([255, 31, 31], dtype=np.uint8)
    face_colors = np.vstack([np.tile(body, (12, 1)), np.tile(lens, (4, 1))])
    edges = np.array(
        [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4],
         [0, 5], [1, 6], [2, 7], [3, 4], [0, 8], [1, 8], [2, 8], [3, 8]],
        dtype=np.int64)
    return vertices, faces, face_colors, edges


def _rotation_between(a, b):
    a = np.asarray(a, dtype=np.float64)
    a = a / np.linalg.norm(a)
    b = np.asarray(b, dtype=np.float64)
    b = b / np.linalg.norm(b)
    c = np.cross(a, b)
    d = float(np.dot(a, b))
    k = np.array([[0, -c[2], c[1]], [c[2], 0, -c[0]], [-c[1], c[0], 0]])
    return np.eye(3) + k + k @ k * ((1.0 - d) / np.linalg.norm(c) ** 2)


def _euler_rxzx(angle_i, angle_j, angle_k):
    i, j, k = 0, 2, 1
    angle_i, angle_k = angle_k, angle_i
    angle_i, angle_j, angle_k = -angle_i, -angle_j, -angle_k
    si, sj, sk = np.sin(angle_i), np.sin(angle_j), np.sin(angle_k)
    ci, cj, ck = np.cos(angle_i), np.cos(angle_j), np.cos(angle_k)
    m = np.identity(4)
    m[i, i] = cj
    m[i, j] = sj * si
    m[i, k] = sj * ci
    m[j, i] = sj * sk
    m[j, j] = -cj * si * sk + ci * ck
    m[j, k] = -cj * ci * sk - si * ck
    m[k, i] = -sj * ck
    m[k, j] = cj * si * ck + ci * sk
    m[k, k] = cj * ci * ck - si * sk
    return m


def camera_glyph(position, yaw_deg, pitch_deg, scale=0.5):
    template, faces, face_colors, edges = _template()
    heading = float(np.mod(90.0 - float(yaw_deg), 360.0))
    initial = _rotation_between([0.0, 0.0, 1.0], [0.0, -1.0, 0.0])
    rotation = _euler_rxzx(np.deg2rad(-float(pitch_deg)),
                           np.deg2rad(heading), 0.0).T[:3, :3] @ initial
    glyph_forward = rotation @ np.array([0.0, 0.0, -1.0])
    expected = forward_vector(yaw_deg, pitch_deg)
    if float(np.dot(glyph_forward, expected)) < 1.0 - 1e-9:
        raise AssertionError("glyph orientation disagrees with forward_vector")
    vertices = template @ rotation.T * float(scale) + np.asarray(position, dtype=np.float64)
    return vertices, faces, face_colors, edges
