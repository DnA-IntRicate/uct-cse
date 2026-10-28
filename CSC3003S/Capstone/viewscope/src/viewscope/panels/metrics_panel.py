"""
Dockable panels.

Each panel reports user intent through signals and accepts state through
`show_*` methods. None of them touch VTK or the scene directly.

ImplNote: Could potentially subdivide into separate panel classes.
"""

from __future__ import annotations

import trimesh
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from viewscope.camera import CameraInfo
from viewscope.data import SCENE_STORE
from viewscope.scene import FieldStats


class MetricsPanel(QWidget):
    """Read-only figures about the bundle and the current viewpoint."""

    SECTIONS = (
        ("Bundle", ["Vertices", "Triangles", "Diagonal", "Targets", "Cameras"]),
        ("Scalar field", ["Field", "Min", "Mean", "Max"]),
        ("Viewpoint", ["Camera", "Position", "Yaw", "Pitch"]),
    )

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.rows = {}
        for title, keys in self.SECTIONS:
            box = QGroupBox(title)
            form = QFormLayout(box)
            for key in keys:
                label = QLabel("--")
                label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                form.addRow(key, label)
                self.rows[key] = label

            layout.addWidget(box)

        layout.addStretch(1)

        SCENE_STORE.plan_changed.connect(self._on_plan_changed)

    def set(self, key, value):
        if key in self.rows:
            self.rows[key].setText(str(value))

    def clear(self, keys):
        for key in keys:
            self.set(key, "--")

    def show_bundle(self):
        vertices = 0
        triangles = 0
        diagonal = 0.0
        targets = 0
        cameras = 0

        if SCENE_STORE.scene is not None:
            mesh = SCENE_STORE.scene.mesh
            if isinstance(mesh, trimesh.Trimesh):
                vertices = len(mesh.vertices)
                triangles = len(mesh.faces)

            diagonal = SCENE_STORE.scene.diagonal
            targets = len(SCENE_STORE.scene.targets)
            cameras = SCENE_STORE.camera_count

        self.set("Vertices", f"{vertices:,}")
        self.set("Triangles", f"{triangles:,}")
        self.set("Diagonal", f"{diagonal:.2f}")
        self.set("Targets", f"{targets:,}")
        self.set("Cameras", f"{cameras:,}")

    def _on_plan_changed(self, info: CameraInfo):
        self.set("Cameras", f"{SCENE_STORE.camera_count:,}")

    def show_field(self, stats: FieldStats | None):
        if stats is None:
            self.set("Field", "unavailable")
            self.clear(["Min", "Mean", "Max"])
            return

        self.set("Field", stats.field)
        self.set("Min", f"{stats.minimum:.4f}")
        self.set("Mean", f"{stats.mean:.4f}")
        self.set("Max", f"{stats.maximum:.4f}")

    def show_camera(self, info: CameraInfo | None):
        if info is None:
            self.clear(["Camera", "Position", "Yaw", "Pitch"])
            return

        pos = info.position
        self.set("Camera", f"{info.index + 1} of {SCENE_STORE.camera_count}")
        self.set("Position", f"{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}")
        self.set("Yaw", f"{info.yaw:.2f}")
        self.set("Pitch", f"{info.pitch:.2f}")
