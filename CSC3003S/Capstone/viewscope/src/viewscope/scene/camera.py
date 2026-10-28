from __future__ import annotations

import math
from dataclasses import dataclass, replace
from enum import Enum, auto

import numpy as np
import vtk

import viewscope_core as vc


class CameraMode(Enum):
    LOOK_AT = (auto(),)
    TRACKBALL = auto()


@dataclass(frozen=True)
class CameraOrbitState:
    """
    Explicit free-look camera state: pivot + distance + yaw/pitch.

    Deliberately not derived from scene bounds after construction, so
    nothing in the renderer can perturb it as a side effect.
    """

    pivot: tuple[float, float, float]
    distance: float
    yaw: float  # Radians
    pitch: float  # Radians
    view_angle: float  # Degrees

    def pose(self) -> np.ndarray:
        """The 4x4 camera-to-world pose matrix for this state."""
        yaw_deg = math.degrees(self.yaw) - 90.0
        pitch_deg = math.degrees(self.pitch)
        forward = vc.forward_vector(yaw_deg, pitch_deg)
        position = np.asarray(self.pivot, dtype=np.float64) + self.distance * forward

        return vc.camera_pose(position, yaw_deg, pitch_deg)

    def camera_position(self) -> tuple[float, ...]:
        return tuple(self.pose()[:3, 3])

    def camera_up(self) -> tuple[float, float, float]:
        """The pose's local Y axis in world space."""
        return tuple(self.pose()[:3, 1])


class SceneCameraController:
    """Perspective look-at scene camera."""

    YAW_SENSITIVITY: float = 0.005  # Rad/px
    YAW_SINGULARITY_RATIO: float = 1e-3  # Horizontal/Distance
    PITCH_SENSITIVITY: float = 0.005  # Rad/px
    PAN_SENSITIVITY: float = 0.0015  # Fraction of distance/px
    ZOOM_SENSITIVITY: float = 0.0025  # Fraction of distance/Unit
    PITCH_LIMIT: float = math.radians(89.0)  # Camera can't be 90deg overhead/below
    MIN_DISTANCE: float = 1e-3

    def __init__(self, renderer: vtk.vtkRenderer, yfov_deg: float):
        self.renderer = renderer
        self.yfov_deg = yfov_deg
        self._orbit: CameraOrbitState | None = None

    def sync_from_camera(self):
        """Resync orbit state from the camera's current pose."""
        self._orbit = self._orbit_from_camera()

    def begin_transition_to_orbit(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """
        Capture the camera's current raw pose (e.g. wherever trackball left
        it) and compute the nearest pose the look-at model can represent, as
        a target without moving the camera yet.

        Returns the captured start pose; the target ends up in self._orbit.
        Callers interpolate toward it with apply_transition(), then call
        finish_transition() to land exactly on it.
        """
        cam = self.renderer.GetActiveCamera()
        start = (
            np.array(cam.GetPosition(), dtype=float),
            np.array(cam.GetFocalPoint(), dtype=float),
            np.array(cam.GetViewUp(), dtype=float),
            cam.GetViewAngle(),
        )

        # Projects the current (possibly rolled) trackball pose onto the
        # nearest yaw/pitch/no-roll pose - same position and pivot, roll discarded.
        self.sync_from_camera()
        return start

    def apply_transition(self, start: tuple[np.ndarray, np.ndarray, np.ndarray, float], t: float):
        """
        Lerp the camera part-way (t in [0, 1]) from a captured start pose
        toward the current _orbit target.
        """
        assert self._orbit is not None
        start_position, start_focal, start_up, start_angle = start

        target_position = np.array(self._orbit.camera_position(), dtype=float)
        target_focal = np.array(self._orbit.pivot, dtype=float)
        target_up = np.array(self._orbit.camera_up(), dtype=float)

        position = start_position + (target_position - start_position) * t
        focal = start_focal + (target_focal - start_focal) * t
        up = start_up + (target_up - start_up) * t

        norm = np.linalg.norm(up)
        if norm > 1e-9:
            up = up / norm

        view_angle = start_angle + (self._orbit.view_angle - start_angle) * t

        cam = self.renderer.GetActiveCamera()
        cam.SetPosition(*position)
        cam.SetFocalPoint(*focal)
        cam.SetViewUp(*up)
        cam.SetViewAngle(view_angle)

        distance = float(np.linalg.norm(position - focal))
        near_clip = max(distance * 0.001, 1e-5)
        far_clip = max(distance * 100.0, near_clip + 1.0)
        cam.SetClippingRange(near_clip, far_clip)

    def finish_transition(self):
        """
        Land exactly on the projected target, clearing any residual
        interpolation error from the lerp.
        """
        self._apply_orbit()

    # -- Orbit state -----------------------------------------------------

    def _orbit_from_camera(self) -> CameraOrbitState:
        """
        Derive pivot/distance/yaw/pitch from wherever the camera currently is.

        Used to capture state after a deliberate reframe (ResetCamera) and
        to adopt whatever pose we're in when manipulation resumes from a
        planned viewpoint.
        """
        cam = self.renderer.GetActiveCamera()
        position = np.array(cam.GetPosition(), dtype=float)
        focal = np.array(cam.GetFocalPoint(), dtype=float)
        up = np.array(cam.GetViewUp(), dtype=float)
        offset = position - focal

        distance = float(np.linalg.norm(offset))
        if distance < self.MIN_DISTANCE:
            distance = self.MIN_DISTANCE

        horizontal = math.hypot(offset[0], offset[1])
        pitch = math.atan2(offset[2], horizontal)

        # NOTE: Clamp the pitch as seen in orbit().
        #       Without this, a pose adopted from outside this controller
        #       (the orientation widget's top/bottom) can land us
        #       exactly at the pole. At pitch == +-90deg the view direction is
        #       parallel to our fixed world-up (0, 0, 1).
        #
        #       VTK's camera basis is singular - GetViewTransformMatrix() (used
        #       by pan()) starts returning garbage/NaN, which then corrupts every
        #       subsequent orbit/pan/dolly, including making zoom look broken.
        pitch = max(-self.PITCH_LIMIT, min(self.PITCH_LIMIT, pitch))

        # Near a pole, offset[0]/offset[1] are noise, not a direction;
        # atan2 on them would give a near-random yaw. The yaw is still
        # recoverable from the actual up vector reported by VTK.
        sp = math.sin(pitch)
        if (horizontal < (distance * self.YAW_SINGULARITY_RATIO)) and (abs(sp) > 1e-6):
            yaw = math.atan2(-up[0] / sp, up[1] / sp)
        else:
            yaw = math.atan2(offset[0], -offset[1])

        return CameraOrbitState(
            pivot=tuple(focal),
            distance=distance,
            yaw=yaw,
            pitch=pitch,
            view_angle=cam.GetViewAngle(),
        )

    def _apply_orbit(self):
        # INVARIANT: The orbit should never be uninitialized!
        assert self._orbit is not None

        cam = self.renderer.GetActiveCamera()
        cam.SetFocalPoint(*self._orbit.pivot)
        cam.SetPosition(*self._orbit.camera_position())
        cam.SetViewUp(*self._orbit.camera_up())
        cam.SetViewAngle(self._orbit.view_angle)

        # Keep the near plane close enough that geometry doesn't disappear
        # when the camera gets close to the pivot.
        distance = self._orbit.distance
        near_clip = max(distance * 0.001, 1e-5)
        far_clip = max(distance * 100.0, near_clip + 1.0)

        cam.SetClippingRange(near_clip, far_clip)

    def _ensure_orbit_active(self):
        """Lazily adopt the current camera pose the first time we're used."""
        if self._orbit is None:
            self.sync_from_camera()

    # -- Pose manipulation -----------------------------------------------

    def orbit(self, dx: float, dy: float):
        """
        Rotate around the pivot. Yaw/pitch are independent and clamped.
        """
        self._ensure_orbit_active()

        # INVARIANT: The orbit should never be uninitialized!
        assert self._orbit is not None

        yaw = self._orbit.yaw - dx * self.YAW_SENSITIVITY
        pitch = self._orbit.pitch + dy * self.PITCH_SENSITIVITY
        pitch = max(-self.PITCH_LIMIT, min(self.PITCH_LIMIT, pitch))
        self._orbit = replace(self._orbit, yaw=yaw, pitch=pitch)
        self._apply_orbit()

    def pan(self, dx: float, dy: float):
        """
        Translate the pivot (and camera) along the screen's right/up axes.
        Never changes orientation, and never reads scene bounds.
        """
        self._ensure_orbit_active()

        # INVARIANT: The orbit should never be uninitialized!
        assert self._orbit is not None

        cam = self.renderer.GetActiveCamera()
        matrix = cam.GetViewTransformMatrix()  # VTK's actual camera basis
        right = np.array([matrix.GetElement(0, i) for i in range(3)])
        true_up = np.array([matrix.GetElement(1, i) for i in range(3)])

        # Scale by distance so pan speed feels consistent at any zoom level.
        scale = self._orbit.distance * self.PAN_SENSITIVITY
        offset = (-right * dx + true_up * dy) * scale
        pivot = tuple(np.array(self._orbit.pivot, dtype=float) + offset)
        self._orbit = replace(self._orbit, pivot=pivot)
        self._apply_orbit()

    def dolly(self, amount: float):
        """Move toward/away from the pivot. Positive amount = zoom in."""
        self._ensure_orbit_active()

        # INVARIANT: The orbit should never be uninitialized!
        assert self._orbit is not None

        distance = self._orbit.distance * (1.0 - amount * self.ZOOM_SENSITIVITY)
        distance = max(self.MIN_DISTANCE, distance)
        self._orbit = replace(self._orbit, distance=distance)
        self._apply_orbit()

    # -- Overview --------------------------------------------------------

    def save_overview(self):
        self._orbit = self._orbit_from_camera()

    def show_overview(self):
        """Return to the free-look camera."""
        if self._orbit is None:
            self.save_overview()
        else:
            self._apply_orbit()
