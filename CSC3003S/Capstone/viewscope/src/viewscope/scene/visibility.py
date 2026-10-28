"""
Highlight targets that a given camera can see.
Just needs to be passed a Camera object
"""

from __future__ import annotations

import numpy as np

import viewscope_core as vc
from viewscope.data import SceneData


class TargetVisibility:
    """
    Which targets a viewpoint can see, as a boolean mask over the targets.

    Shipped viewpoints are looked up in the bundle's visibility matrix.
    Cameras the user has added are recomputed through the library, off a
    single offscreen renderer that is built on first use and kept alive for
    the life of the scene.
    """

    def __init__(self, scene: SceneData):
        self._scene = scene
        self._renderer = None
        self._cache: dict[int, np.ndarray] = {}

    def mask_for(self, index: int | None) -> np.ndarray | None:
        """The visibility mask for one camera, or None when there is no camera."""
        if index is None:
            return None

        plan = self._scene.plan
        if not 0 <= index < len(plan.ids):
            return None

        if index not in self._cache:
            shipped = self._shipped(index)
            self._cache[index] = self._computed(index) if shipped is None else shipped

        return self._cache[index]

    def union_mask(self, indices) -> np.ndarray:
        """The targets at least one of these cameras can see."""
        union = np.zeros(len(self._scene.targets), dtype=bool)
        for index in indices:
            mask = self.mask_for(index)
            if mask is not None:
                union |= mask

        return union

    def forget(self, index: int | None = None):
        """Drop cached masks, for when a camera moves or the plan changes."""
        if index is None:
            self._cache.clear()
        else:
            self._cache.pop(index, None)

    def close(self):
        """Release the offscreen GL context, if one was ever built."""
        if self._renderer is not None:
            self._renderer.close()
            self._renderer = None

    # -- internals -----------------------------------------------------

    def _shipped(self, index: int) -> np.ndarray | None:
        """The precomputed row, when the bundle ships one for this camera."""
        visibility = self._scene.visibility
        if visibility is None or index >= len(visibility):
            return None

        return np.asarray(visibility[index], dtype=bool)

    def _computed(self, index: int) -> np.ndarray:
        """Recompute one row through the library."""
        plan = self._scene.plan
        position = plan.positions[index]
        pose = vc.camera_pose(position, plan.yaws_deg[index], plan.pitches_deg[index])

        return vc.camera_visibility(
            self._depth_renderer().render_depth(pose),
            self._scene.targets,
            self._scene.normals,
            position,
            pose,
            plan.camera,
        )

    def _depth_renderer(self) -> vc.SceneRenderer:
        """One live SceneRenderer per scene; building it needs a GL context."""
        if self._renderer is None:
            camera = self._scene.plan.camera
            self._renderer = vc.SceneRenderer(
                self._scene.mesh, camera["width"], camera["height"], camera["yfov_deg"]
            )

        return self._renderer
