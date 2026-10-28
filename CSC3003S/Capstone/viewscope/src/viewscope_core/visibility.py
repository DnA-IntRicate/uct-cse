
import numpy as np

from viewscope_core.constants import (
    DEPTH_TOLERANCE_ABS_M,
    DEPTH_TOLERANCE_REL,
    ZNEAR_M,
)
from viewscope_core.pose import camera_pose, project


def camera_visibility(depth_map, target_positions, target_normals, camera_position, pose, camera):
    width, height = camera["width"], camera["height"]
    pixels, depths = project(target_positions, pose, width, height, camera["yfov_deg"])
    towards = np.asarray(camera_position, dtype=np.float64) - target_positions
    rho = np.linalg.norm(towards, axis=1)
    cosine = np.einsum("ij,ij->i", towards, target_normals) / np.maximum(rho, 1e-12)
    col = np.round(pixels[:, 0]).astype(np.int64)
    row = np.round(pixels[:, 1]).astype(np.int64)
    candidate = (
        (depths > ZNEAR_M)
        & (cosine > 0.0)
        & (col >= 0)
        & (col < width)
        & (row >= 0)
        & (row < height)
    )
    visible = np.zeros(len(target_positions), dtype=bool)
    idx = np.flatnonzero(candidate)
    sampled = depth_map[row[idx], col[idx]]
    tolerance = np.maximum(DEPTH_TOLERANCE_ABS_M, DEPTH_TOLERANCE_REL * depths[idx])
    visible[idx] = (sampled > 0.0) & (depths[idx] <= sampled + tolerance)
    return visible


def compute_visibility(renderer, target_positions, target_normals, plan):
    rows = []
    for j in range(len(plan.ids)):
        pose = camera_pose(plan.positions[j], plan.yaws_deg[j], plan.pitches_deg[j])
        rows.append(camera_visibility(
            renderer.render_depth(pose), target_positions, target_normals,
            plan.positions[j], pose, plan.camera))
    return np.stack(rows)
