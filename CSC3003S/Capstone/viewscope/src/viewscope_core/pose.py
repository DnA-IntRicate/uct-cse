import numpy as np


def forward_vector(yaw_deg, pitch_deg):
    yaw = np.radians(float(yaw_deg))
    pitch = np.radians(float(pitch_deg))
    cp = np.cos(pitch)
    return np.array([cp * np.cos(yaw), cp * np.sin(yaw), np.sin(pitch)], dtype=np.float64)


def camera_pose(position, yaw_deg, pitch_deg):
    if abs(float(pitch_deg)) > 89.9:
        raise ValueError(f"pitch {pitch_deg} deg is too close to vertical, the camera roll is undefined")
    p = np.asarray(position, dtype=np.float64)
    if p.shape != (3,) or not np.all(np.isfinite(p)):
        raise ValueError("position must be three finite coordinates")
    f = forward_vector(yaw_deg, pitch_deg)
    right = np.cross(f, np.array([0.0, 0.0, 1.0]))
    right = right / np.linalg.norm(right)
    up = np.cross(right, f)
    pose = np.eye(4, dtype=np.float64)
    pose[:3, 0] = right
    pose[:3, 1] = up
    pose[:3, 2] = -f
    pose[:3, 3] = p
    return pose


def look_at_angles(position, target):
    d = np.asarray(target, dtype=np.float64) - np.asarray(position, dtype=np.float64)
    n = np.linalg.norm(d)
    if n < 1e-9:
        raise ValueError("camera position and look target coincide")
    d = d / n
    yaw = float(np.degrees(np.arctan2(d[1], d[0])))
    pitch = float(np.degrees(np.arcsin(np.clip(d[2], -1.0, 1.0))))
    return yaw, pitch


def intrinsics(width, height, yfov_deg):
    fy = (float(height) / 2.0) / np.tan(np.radians(float(yfov_deg)) / 2.0)
    return fy, fy, float(width) / 2.0, float(height) / 2.0


def project(points, pose, width, height, yfov_deg):
    fx, fy, cx, cy = intrinsics(width, height, yfov_deg)
    p = np.atleast_2d(np.asarray(points, dtype=np.float64))
    rotation = pose[:3, :3]
    translation = pose[:3, 3]
    q = (p - translation) @ rotation
    depth = -q[:, 2]
    safe = np.where(np.abs(depth) < 1e-12, 1e-12, depth)
    x = cx + fx * q[:, 0] / safe
    y = cy - fy * q[:, 1] / safe
    return np.stack([x, y], axis=1), depth


def frustum_corners(pose, width, height, yfov_deg, depth):
    fx, fy, cx, cy = intrinsics(width, height, yfov_deg)
    d = float(depth)
    px = np.array([[0.0, 0.0], [width, 0.0], [width, height], [0.0, height]], dtype=np.float64)
    cam = np.stack([(px[:, 0] - cx) / fx * d, (cy - px[:, 1]) / fy * d, np.full(4, -d)], axis=1)
    return cam @ pose[:3, :3].T + pose[:3, 3]
