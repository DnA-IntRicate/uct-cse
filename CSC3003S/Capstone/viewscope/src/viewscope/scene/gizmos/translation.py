from __future__ import annotations

import math
from collections.abc import Callable

import numpy as np
import vtk


class TranslationGizmo:
    """
    Three translate arrows (X/Y/Z).

    Translation: one arrow per world axis, dragged along its own axis by
    intersecting the mouse ray with the plane that contains that axis and
    best faces the camera.

    **Rotation is disabled entirely: no rings are built, and no rotate drag
    path exists. This gizmo is translate-only.**

    Claude was used to generate the initial version of this class, the building of handles,
    the picker and draggging logic, and handling translations.
    Wiring this into viewport.py and window.py, was done manually
    """

    _AXES: dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]] = {
        "x": ((1.0, 0.0, 0.0), (0.85, 0.20, 0.20)),
        "y": ((0.0, 1.0, 0.0), (0.20, 0.85, 0.20)),
        "z": ((0.0, 0.0, 1.0), (0.20, 0.45, 0.90)),
    }

    def __init__(self, renderer: vtk.vtkRenderer):
        self.renderer = renderer

        self.picker = vtk.vtkCellPicker()
        self.picker.SetTolerance(0.0)
        self.picker.PickFromListOn()

        self._axis_of: dict[vtk.vtkActor, np.ndarray] = {}
        self._actors: list[vtk.vtkActor] = []
        self._target: vtk.vtkActor | None = None

        self._heading_deg = 0.0

        self._on_move: Callable[[np.ndarray], None] | None = None

        self._build_translate_handles()

        self.active: bool = False

        # -- translate drag state --
        self._drag_axis = np.zeros(3)
        self._drag_plane_origin = np.zeros(3)
        self._drag_plane_normal = np.zeros(3)
        self._drag_last_t = 0.0

        self.set_visible(False)

    # -- construction: translate arrows ---------------------------------

    def _build_translate_handles(self):
        for direction, colour in self._AXES.values():
            arrow = vtk.vtkArrowSource()
            arrow.SetTipResolution(16)
            arrow.SetShaftResolution(16)
            arrow.SetShaftRadius(0.01)
            arrow.SetTipRadius(0.03)
            arrow.SetTipLength(0.25)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(arrow.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(*colour)
            actor.GetProperty().SetLighting(False)

            self._axis_of[actor] = np.array(direction, dtype=np.float64)
            self._actors.append(actor)
            self.renderer.AddActor(actor)
            self.picker.AddPickList(actor)

    # -- attach / detach -------------------------------------------------

    def attach(
        self,
        actor: vtk.vtkActor,
        *,
        heading_deg: float = 0.0,
        on_move: Callable[[np.ndarray], None] | None = None,
    ):
        """Point the gizmo at an actor: place the handles at its centre, sized
        to it.

        `on_move(new_centre)` is called with the target's new world-space
        centre after each translate drag tick.
        """
        self._target = actor
        self._heading_deg = heading_deg
        self._on_move = on_move
        self._place_handles()
        self.set_visible(True)

    def detach(self):
        self._target = None
        self._on_move = None
        self.set_visible(False)

    def refresh(self, *, heading_deg: float | None = None):
        """Re-place the handles after something else has moved/turned the target."""
        if heading_deg is not None:
            self._heading_deg = heading_deg
        if self._target is not None:
            self._place_handles()

    def set_visible(self, visible: bool):
        for actor in self._actors:
            actor.SetVisibility(visible)

    def remove_from(self, renderer: vtk.vtkRenderer):
        for actor in self._actors:
            renderer.RemoveActor(actor)

    def _place_handles(self):
        assert self._target is not None

        bounds = self._target.GetBounds()
        centre = np.array(
            [(bounds[0] + bounds[1]) / 2, (bounds[2] + bounds[3]) / 2, (bounds[4] + bounds[5]) / 2]
        )
        diag = math.sqrt(
            (bounds[1] - bounds[0]) ** 2
            + (bounds[3] - bounds[2]) ** 2
            + (bounds[5] - bounds[4]) ** 2
        )
        length = max(diag, 1e-3)

        for actor, direction in self._axis_of.items():
            actor.SetUserTransform(self._arrow_transform(centre, direction, length))

    @staticmethod
    def _arrow_transform(
        centre: np.ndarray, direction: np.ndarray, length: float
    ) -> vtk.vtkTransform:
        """vtkArrowSource points along +X by default; rotate it onto `direction`."""
        transform = vtk.vtkTransform()
        transform.Translate(*centre)
        transform.Concatenate(TranslationGizmo._align_matrix(np.array([1.0, 0.0, 0.0]), direction))
        transform.Scale(length, length, length)
        return transform

    @staticmethod
    def _align_matrix(from_axis: np.ndarray, to_axis: np.ndarray) -> vtk.vtkMatrix4x4:
        """A pure-rotation matrix taking `from_axis` onto `to_axis`."""
        from_axis = from_axis / np.linalg.norm(from_axis)
        to_axis = to_axis / np.linalg.norm(to_axis)

        dot = float(np.clip(np.dot(from_axis, to_axis), -1.0, 1.0))
        rotation = vtk.vtkTransform()

        if dot < -0.9999:
            perp = np.cross(from_axis, [1.0, 0.0, 0.0])
            if np.linalg.norm(perp) < 1e-6:
                perp = np.cross(from_axis, [0.0, 1.0, 0.0])
            perp /= np.linalg.norm(perp)
            rotation.RotateWXYZ(180.0, *perp)
        elif dot < 0.9999:
            rot_axis = np.cross(from_axis, to_axis)
            rot_axis /= np.linalg.norm(rot_axis)
            rotation.RotateWXYZ(math.degrees(math.acos(dot)), *rot_axis)

        return rotation.GetMatrix()

    # -- dragging ---------------------------------------------------------

    def try_start_drag(self, x: int, y: int) -> bool:
        """Pick a handle under (x, y). Returns whether a drag started."""
        if self._target is None:
            return False

        self.picker.Pick(x, y, 0, self.renderer)
        actor = self.picker.GetActor()

        if actor in self._axis_of:
            return self._try_start_translate(actor, x, y)
        return False

    def _try_start_translate(self, actor: vtk.vtkActor, x: int, y: int) -> bool:
        axis_world = self._axis_of[actor]
        origin = self._target_centre()

        plane = self._camera_facing_plane(axis_world, origin)
        if plane is None:
            return False
        normal, _view_dir = plane

        self._drag_axis = axis_world
        self._drag_plane_origin = origin
        self._drag_plane_normal = normal

        point = self._ray_plane_point(normal, origin, x, y)
        if point is None:
            return False

        self._drag_last_t = float(np.dot(point - origin, axis_world))
        self.active = True
        return True

    def drag(self, x: int, y: int):
        if not self.active or self._target is None:
            return

        self._drag_translate(x, y)

    def _drag_translate(self, x: int, y: int):
        point = self._ray_plane_point(self._drag_plane_normal, self._drag_plane_origin, x, y)
        if point is None:
            return

        t = float(np.dot(point - self._drag_plane_origin, self._drag_axis))
        delta = (t - self._drag_last_t) * self._drag_axis
        self._drag_last_t = t

        self._translate_target(delta)
        self._place_handles()

        if self._on_move is not None:
            self._on_move(self._target_centre())

    def end_drag(self):
        self.active = False

    # -- shared geometry helpers ------------------------------------------

    def _target_centre(self) -> np.ndarray:
        assert self._target is not None
        bounds = self._target.GetBounds()
        return np.array(
            [(bounds[0] + bounds[1]) / 2, (bounds[2] + bounds[3]) / 2, (bounds[4] + bounds[5]) / 2]
        )

    def _camera_facing_plane(
        self, axis_world: np.ndarray, origin: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray] | None:
        camera = self.renderer.GetActiveCamera()
        view_vec = np.array(camera.GetPosition()) - origin
        view_dist = np.linalg.norm(view_vec)
        if view_dist < 1e-6:
            return None
        view_dir = view_vec / view_dist

        if abs(np.dot(axis_world, view_dir)) > 0.97:
            return None

        normal = np.cross(np.cross(axis_world, view_vec), axis_world)
        normal_len = np.linalg.norm(normal)
        if normal_len < 1e-6:
            return None

        return normal / normal_len, view_dir

    def _ray_plane_point(
        self, normal: np.ndarray, origin: np.ndarray, x: int, y: int
    ) -> np.ndarray | None:
        """Where the mouse ray crosses a plane, as a world-space point."""
        self.renderer.SetDisplayPoint(x, y, 0.0)
        self.renderer.DisplayToWorld()
        near = np.array(self.renderer.GetWorldPoint())
        near = near[:3] / near[3]

        self.renderer.SetDisplayPoint(x, y, 1.0)
        self.renderer.DisplayToWorld()
        far = np.array(self.renderer.GetWorldPoint())
        far = far[:3] / far[3]

        intersection = [0.0, 0.0, 0.0]
        t_line = vtk.reference(0.0)
        hit = vtk.vtkPlane.IntersectWithLine(
            near.tolist(),
            far.tolist(),
            normal.tolist(),
            origin.tolist(),
            t_line,  # type: ignore[ty:invalid-argument-type]
            intersection,
        )
        if not hit:
            return None

        return np.array(intersection)

    def _translate_target(self, delta: np.ndarray):
        """Apply a world-space translation on top of whatever transform is
        already there."""
        assert self._target is not None

        matrix = vtk.vtkMatrix4x4()
        existing = self._target.GetUserTransform()
        if existing is not None:
            matrix.DeepCopy(existing.GetMatrix())

        for i in range(3):
            matrix.SetElement(i, 3, matrix.GetElement(i, 3) + delta[i])

        transform = vtk.vtkTransform()
        transform.SetMatrix(matrix)
        self._target.SetUserTransform(transform)
