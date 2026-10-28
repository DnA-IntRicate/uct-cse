import numpy as np

from viewscope_core.constants import SAFE_DISTANCE_M


def check_placement(mesh, target_positions, position):
    p = np.asarray(position, dtype=np.float64)
    if p.shape != (3,) or not np.all(np.isfinite(p)):
        return False, "position must be three finite coordinates"
    try:
        inside = bool(mesh.contains(p[None, :])[0])
    except BaseException:
        inside = False
    if inside:
        return False, "position is inside the structure"
    gap = float(np.min(np.linalg.norm(np.asarray(target_positions, dtype=np.float64) - p, axis=1)))
    if gap < SAFE_DISTANCE_M:
        return False, (
            f"position is {gap:.1f} m from the surface, closer than the safe distance of "
            f"{SAFE_DISTANCE_M:.1f} m"
        )
    return True, "ok"
