from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldStats:
    """Summary of the scalar field currently colouring the cloud."""

    field: str
    minimum: float
    mean: float
    maximum: float
