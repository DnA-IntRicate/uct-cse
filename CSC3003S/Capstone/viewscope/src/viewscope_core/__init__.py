from viewscope_core import constants
from viewscope_core.loaders import (
    Plan,
    Scores,
    load_plan,
    load_reference,
    load_scene,
    load_scores,
    load_targets,
)
from viewscope_core.placement import check_placement
from viewscope_core.pose import (
    camera_pose,
    forward_vector,
    frustum_corners,
    intrinsics,
    look_at_angles,
    project,
)
from viewscope_core.glyph import camera_glyph
from viewscope_core.render import SceneRenderer
from viewscope_core.visibility import camera_visibility, compute_visibility
from viewscope_core.scoring import (
    angular_diversity,
    best_per_sector,
    observer_geometry,
    sector_indices,
    tangent_basis,
    target_score,
    weight_factors,
)

__version__ = "2.1.0"

__all__ = [
    "Plan",
    "SceneRenderer",
    "Scores",
    "angular_diversity",
    "best_per_sector",
    "camera_glyph",
    "camera_pose",
    "camera_visibility",
    "check_placement",
    "compute_visibility",
    "constants",
    "forward_vector",
    "frustum_corners",
    "intrinsics",
    "load_plan",
    "load_reference",
    "load_scene",
    "load_scores",
    "load_targets",
    "look_at_angles",
    "observer_geometry",
    "project",
    "sector_indices",
    "tangent_basis",
    "target_score",
    "weight_factors",
]
