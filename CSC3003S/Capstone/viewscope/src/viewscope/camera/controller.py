"""Moving the active camera between the overview and planned viewpoints."""

from __future__ import annotations

import numpy as np

import viewscope_core as vc
from viewscope.data import SCENE_STORE
from viewscope.scene import transform

from .structs import CameraInfo


class CameraController:
    """Owns the overview snapshot and the current viewpoint index."""

    def __init__(self, renderer, yfov_deg: float):
        self.renderer = renderer
        self.yfov_deg = yfov_deg
        self.index = None
        self._overview = None

    @property
    def count(self) -> int:
        return SCENE_STORE.camera_count

    def save_overview(self):
        cam = self.renderer.GetActiveCamera()
        self._overview = (
            cam.GetPosition(),
            cam.GetFocalPoint(),
            cam.GetViewUp(),
            cam.GetViewAngle(),
        )

    def show_overview(self):
        """Return to the free-look camera. Returns None, matching `show`."""
        if self._overview is None:
            self.save_overview()
        else:
            cam = self.renderer.GetActiveCamera()
            position, focal, up, angle = self._overview
            cam.SetPosition(*position)
            cam.SetFocalPoint(*focal)
            cam.SetViewUp(*up)
            cam.SetViewAngle(angle)
            self.renderer.ResetCameraClippingRange()

        self.index = None

    def show(self, index: int) -> CameraInfo | None:
        """Jump to a planned viewpoint. Index wraps at both ends."""
        if self.count == 0:
            return None

        if SCENE_STORE.scene is None:
            return None

        # First jump away from free-look: remember where we were.
        if self.index is None:
            self.save_overview()

        self.index = index % self.count
        i = self.index

        plan = SCENE_STORE.scene.plan
        diagonal = SCENE_STORE.scene.diagonal

        pose = vc.camera_pose(plan.positions[i], plan.yaws_deg[i], plan.pitches_deg[i])
        transform.apply_pose(self.renderer.GetActiveCamera(), pose, self.yfov_deg, diagonal)

        return CameraInfo(
            index=i,
            position=np.asarray(plan.positions[i], dtype=float),
            yaw=float(plan.yaws_deg[i]),
            pitch=float(plan.pitches_deg[i]),
        )

    def step(self, delta: int) -> CameraInfo | None:
        """Move relative to the current viewpoint, starting from either end."""
        if self.index is None:
            return self.show(0 if delta > 0 else -1)

        return self.show(self.index + delta)
