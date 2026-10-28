"""
What one target is seen by, and from which directions.

A target's usefulness is not one number. Every camera that can see it carries
a weight in [0, 1] - the product of a distance factor `f_rho` and a viewing
angle factor `f_theta` - and falls in exactly one sector: one of a fixed
number of equal wedges measured around the target's normal, like compass
directions around the point. Eight is the default and four is also supplied.
Cameras in different sectors see the target from genuinely different
directions, which is what photogrammetry needs.

Reports come out of the bundle's score table when it still describes the
plan on screen, and are recomputed through viewscope_core when the user has
added cameras the bundle never scored.

Nothing here touches Qt or VTK, so it can be exercised without a window.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import viewscope_core as vc
from viewscope.data import SceneData

#: Sector counts the bundle stores columns for; any other count is derived.
STORED_SECTOR_COUNTS = (
    vc.constants.DEFAULT_SECTOR_COUNT,
    vc.constants.ALTERNATE_SECTOR_COUNT,
)

#: How far apart the two factors must be before one of them is named as the
#: thing holding a camera back. Below this they are called even.
FACTOR_MARGIN = 0.02

DISTANCE = "Distance"
ANGLE = "Angle"
EVEN = "Even"


@dataclass(frozen=True)
class Observer:
    """One camera's view of one target."""

    camera_index: int
    weight: float
    f_rho: float
    f_theta: float
    sector: int
    best: bool

    @property
    def limited_by(self) -> str:
        """Which of the two factors is costing this camera the most."""
        if abs(self.f_rho - self.f_theta) <= FACTOR_MARGIN:
            return EVEN

        return DISTANCE if self.f_rho < self.f_theta else ANGLE


@dataclass(frozen=True)
class SectorSummary:
    """One wedge of the compass around the target normal."""

    index: int
    observers: int
    best_weight: float
    best_camera: int | None

    @property
    def occupied(self) -> bool:
        return self.observers > 0


@dataclass(frozen=True)
class TargetReport:
    """The weights and the sector decomposition of a single target."""

    index: int
    position: np.ndarray
    normal: np.ndarray
    sector_count: int
    #: Every observing camera, heaviest first.
    observers: tuple[Observer, ...]
    #: One entry per sector, in sector order, occupied or not.
    sectors: tuple[SectorSummary, ...]
    diversity: float
    score: float
    #: True when the numbers were recomputed here rather than read from the
    #: bundle, which is what happens once the user adds a camera.
    live: bool = False
    #: True when no visibility information was available and every camera was
    #: treated as an observer.
    assumed_visibility: bool = False

    @property
    def occupied_sectors(self) -> int:
        return sum(1 for sector in self.sectors if sector.occupied)

    @property
    def best_observers(self) -> tuple[Observer, ...]:
        """The sector winners, one per occupied sector."""
        return tuple(observer for observer in self.observers if observer.best)

    @property
    def top_observer(self) -> Observer | None:
        """The one camera that sees this target best, or None if nothing does.

        Not the same as a sector winner: there is one of these per target,
        where `best_observers` holds one per occupied wedge.
        """
        return self.observers[0] if self.observers else None

    def weights(self) -> dict[int, float]:
        """Weight per camera index, for colouring things that are not rows."""
        return {observer.camera_index: observer.weight for observer in self.observers}


def build_report(
    index: int,
    position: np.ndarray,
    normal: np.ndarray,
    camera_positions: np.ndarray,
    camera_ids: np.ndarray,
    sector_count: int,
    *,
    weights: tuple[np.ndarray, np.ndarray, np.ndarray] | None = None,
    sectors: np.ndarray | None = None,
    best: np.ndarray | None = None,
    diversity: float | None = None,
    score: float | None = None,
    live: bool = False,
    assumed_visibility: bool = False,
) -> TargetReport:
    """Assemble a report, computing through the library whatever is not given.

    `camera_ids` are plan rows, `camera_positions` the matching positions.
    Pass `weights` as the (weight, f_rho, f_theta) triple the bundle stores to
    keep the viewer's figures identical to the ones on disk.
    """
    ids = np.asarray(camera_ids, dtype=np.int64)
    positions = np.asarray(camera_positions, dtype=np.float64).reshape(len(ids), 3)

    if weights is None:
        rho, theta = vc.observer_geometry(position, normal, positions)
        weight, f_rho, f_theta = vc.weight_factors(rho, theta)

        # The bundle leaves out pairs whose weight underflows float32, so a
        # recomputed report has to drop them too or it would list observers
        # the stored table never would.
        keep = np.float32(weight) > 0
        ids, positions = ids[keep], positions[keep]
        weight, f_rho, f_theta = weight[keep], f_rho[keep], f_theta[keep]
    else:
        weight, f_rho, f_theta = (np.asarray(a, dtype=np.float64) for a in weights)

    if sectors is None:
        sectors = (
            vc.sector_indices(position, normal, positions, sector_count)
            if len(ids)
            else np.zeros(0, dtype=np.int64)
        )
    sectors = np.asarray(sectors, dtype=np.int64)

    if best is None:
        best, _ = vc.best_per_sector(sectors, weight, sector_count)
    best = np.asarray(best, dtype=bool)

    if diversity is None:
        diversity = vc.angular_diversity(sectors, sector_count)

    if score is None:
        score = vc.target_score(sectors, weight, sector_count) if len(ids) else 0.0

    observers = tuple(
        Observer(
            camera_index=int(ids[i]),
            weight=float(weight[i]),
            f_rho=float(f_rho[i]),
            f_theta=float(f_theta[i]),
            sector=int(sectors[i]),
            best=bool(best[i]),
        )
        for i in np.argsort(-np.asarray(weight, dtype=np.float64), kind="stable")
    )

    return TargetReport(
        index=int(index),
        position=np.asarray(position, dtype=float),
        normal=np.asarray(normal, dtype=float),
        sector_count=int(sector_count),
        observers=observers,
        sectors=summarise_sectors(observers, sector_count),
        diversity=float(diversity),
        score=float(score),
        live=live,
        assumed_visibility=assumed_visibility,
    )


def summarise_sectors(observers, sector_count: int) -> tuple[SectorSummary, ...]:
    """Fold the observers into one row per wedge, empty wedges included."""
    leaders: dict[int, Observer] = {}
    counts = [0] * sector_count

    for observer in observers:
        sector = observer.sector
        if not 0 <= sector < sector_count:
            continue

        counts[sector] += 1
        if sector not in leaders or observer.weight > leaders[sector].weight:
            leaders[sector] = observer

    return tuple(
        SectorSummary(
            index=sector,
            observers=counts[sector],
            best_weight=leaders[sector].weight if sector in leaders else 0.0,
            best_camera=leaders[sector].camera_index if sector in leaders else None,
        )
        for sector in range(sector_count)
    )


class TargetReports:
    """Builds and caches the report for whichever target is selected."""

    def __init__(self, scene: SceneData, visibility=None):
        """`visibility` is a TargetVisibility, used only for added cameras."""
        self._scene = scene
        self._visibility = visibility
        self._cache: dict[tuple[int, int], TargetReport] = {}

    def report(self, index: int, sector_count: int) -> TargetReport | None:
        """The report for one target, or None when the index is not a target."""
        if not 0 <= index < len(self._scene.targets):
            return None

        key = (int(index), int(sector_count))
        if key not in self._cache:
            self._cache[key] = self._build(int(index), int(sector_count))

        return self._cache[key]

    def forget(self):
        """Drop every cached report, for when the plan changes underneath."""
        self._cache.clear()

    @property
    def stored(self) -> bool:
        """True while the bundle's score table still describes the whole plan."""
        scores = self._scene.scores
        if scores is None:
            return False

        return int(scores.meta.get("camera_count", -1)) == len(self._scene.plan.ids)

    # -- internals -----------------------------------------------------

    def _build(self, index: int, sector_count: int) -> TargetReport:
        position = self._scene.targets[index]
        normal = self._scene.normals[index]

        if self.stored:
            return self._from_scores(index, position, normal, sector_count)

        return self._from_geometry(index, position, normal, sector_count)

    def _from_scores(self, index, position, normal, sector_count) -> TargetReport:
        """Read the stored row, deriving only what the bundle has no column for."""
        scores = self._scene.scores
        assert scores is not None  # self.stored is the only route here
        row = scores.observers(index)
        ids = np.asarray(row["camera_index"], dtype=np.int64)
        derived = sector_count not in STORED_SECTOR_COUNTS

        return build_report(
            index,
            position,
            normal,
            self._scene.plan.positions[ids],
            ids,
            sector_count,
            weights=(row["weight"], row["f_rho"], row["f_theta"]),
            sectors=None if derived else row[f"sector_{sector_count}"],
            best=None if derived else row[f"best_{sector_count}"],
            diversity=None
            if derived
            else float(getattr(scores, f"diversity_{sector_count}")[index]),
            score=None if derived else float(getattr(scores, f"score_{sector_count}")[index]),
        )

    def _from_geometry(self, index, position, normal, sector_count) -> TargetReport:
        """Recompute from the plan, for a plan the bundle no longer covers."""
        ids, assumed = self._observer_ids(index)

        return build_report(
            index,
            position,
            normal,
            self._scene.plan.positions[ids],
            ids,
            sector_count,
            live=True,
            assumed_visibility=assumed,
        )

    def _observer_ids(self, index: int) -> tuple[np.ndarray, bool]:
        """Which cameras can see this target, and whether that had to be assumed."""
        count = len(self._scene.plan.ids)
        shipped = self._scene.visibility

        seen = np.zeros(count, dtype=bool)
        assumed = False

        for camera in range(count):
            if shipped is not None and camera < len(shipped):
                seen[camera] = bool(shipped[camera][index])
                continue

            mask = None if self._visibility is None else self._visibility.mask_for(camera)
            if mask is None:
                # Nothing can say what this camera sees, so let it observe and
                # flag the report: better an approximate row than a blank one.
                seen[camera] = True
                assumed = True
            else:
                seen[camera] = bool(mask[index])

        return np.flatnonzero(seen), assumed
