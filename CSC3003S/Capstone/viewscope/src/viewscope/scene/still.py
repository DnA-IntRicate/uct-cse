"""
Stills of the viewport's shot, rendered by pyrender rather than by VTK.
VTK draws the interactive view, because that is what a window full of pickers
and widgets needs. pyrender answers with an array of pixels instead of a
window, which is what an exported image needs, and it is the renderer the
planning library was written against: a still taken here is shaded the same
way the view-planning results were.
It draws the bundle's simplified mesh, the one trimesh loaded. The
full-resolution model is VTK's, read by the importer the camera view uses.
"""

from __future__ import annotations

import numpy as np
from trimesh import Geometry

from viewscope_core.render import SceneRenderer


class StillRenderer:
    """
    A pyrender view of the scene mesh, held between shots.
    Building one costs a fraction of a second and takes an offscreen GL
    context with it, so it is made once and rebuilt only when the shot
    changes shape: a different mesh, a different size, a different lens.
    """

    def __init__(self):
        self._renderer = None
        self._mesh = None
        self._shape = None

    def render(
        self, mesh: Geometry, pose: np.ndarray, width: int, height: int, yfov_deg: float
    ) -> np.ndarray:
        """The scene as seen from `pose`, as height x width x 3 uint8."""
        self._ensure(mesh, int(width), int(height), float(yfov_deg))

        # INVARIANT: The renderer should not be uninitialized at this stage!
        assert self._renderer is not None
        return self._renderer.render_color(np.asarray(pose, dtype=np.float64))

    def _ensure(self, mesh: Geometry, width: int, height: int, yfov_deg: float):
        shape = (width, height, round(yfov_deg, 4))
        if self._mesh is mesh and self._shape == shape:
            return

        self.close()
        self._renderer = SceneRenderer(mesh, width, height, yfov_deg)
        self._mesh = mesh
        self._shape = shape

    def close(self):
        """Give the GL context back. Safe to call on a renderer never built."""
        if self._renderer is not None:
            self._renderer.close()
            self._renderer = None

        self._mesh = None
        self._shape = None
