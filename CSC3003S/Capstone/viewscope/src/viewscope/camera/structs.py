"""Structures for camera control and state."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CameraInfo:
    """Where the viewer currently is, in terms the panels can display."""

    index: int
    position: np.ndarray
    yaw: float
    pitch: float
