"""
The target scores as they would be for some of the cameras rather than all.

A bundle ships one score per target, worked out from every viewpoint in the
plan. That is the wrong number while a route is being chosen: what is wanted
then is how well the route covers the model, which changes with every camera
put in or taken out.

Nothing has to be recomputed from the geometry to answer that. `scores.npz`
carries the whole observation table, not just the finished columns - one row
per target and camera that sees it, with the weight and the sector it sees
from - and a target's score is a reduction over those rows:

    score_k      the mean, over k sectors, of the best weight in each
    diversity_k  how evenly the observers are spread between the sectors

So scoring a subset is the shipped table with rows struck out. Filter to the
cameras in the route, reduce again, and the answer is exactly what the bundle
would have written had it only ever known about those cameras - this is
checked against the shipped columns in the tests.

Doing that a target at a time would mean sixty thousand reductions on every
click. Instead every row is keyed by the target and sector it belongs to and
sorted once, which turns the whole recount into one pass over a flat array.

No Qt and no VTK, so it can be exercised without a window.
"""

from __future__ import annotations

import numpy as np

import viewscope_core as vc

#: The fields this can answer for a subset, and the column each is derived
#: from. Anything else falls back to what the bundle shipped.
FIELDS = {
    "score_8": ("score", 8),
    "score_4": ("score", 4),
    "diversity_8": ("diversity", 8),
    "diversity_4": ("diversity", 4),
}


class SubsetScores:
    """Rescores every target for a subset of the cameras, quickly.

    Holds the bundle's observation table re-sorted for the reduction, one
    sorting per sector count, each built the first time it is asked for.
    """

    def __init__(self, scores: vc.Scores, target_count: int, camera_count: int):
        self._scores = scores
        self._targets = int(target_count)
        self._cameras = int(camera_count)
        self._sorted: dict[int, tuple] = {}

        # Which target each row of the table belongs to, read off the offsets
        # that make it a table in the first place.
        self._target_of_row = np.repeat(
            np.arange(self._targets, dtype=np.int64), np.diff(scores.offsets)
        )

    @staticmethod
    def handles(field: str) -> bool:
        """Whether a subset score can be worked out for this field at all."""
        return field in FIELDS

    def unscored(self, selected) -> tuple[int, ...]:
        """The rows of `selected` the shipped table knows nothing about.

        A viewpoint the user placed, or one a loaded route brought with it,
        has no rows in `scores.npz`: nothing was ever measured from there. It
        can still be in the route, and the route can still be flown and
        saved, but it earns the targets it sees nothing, so the heat map is
        an under-count wherever such a viewpoint is the only observer. Worth
        saying out loud, which is what this is for.
        """
        return tuple(int(row) for row in selected if int(row) >= self._cameras)

    def full_range(self, field: str) -> tuple[float, float]:
        """The scale to colour by, which is the whole plan's, not the route's.

        Fixed on purpose. Rescaled to whatever the route happens to reach,
        one camera would paint its own small patch the colour of full
        coverage, and adding a second would repaint everything darker. Held
        to the plan's range, a colour means one thing throughout: the route
        starts cold and fills in as cameras go back.
        """
        return 0.0, float(np.asarray(getattr(self._scores, field)).max(initial=0.0))

    def values(self, field: str, selected) -> np.ndarray:
        """One value per target, counting only the cameras in `selected`."""
        kind, sectors = FIELDS[field]
        key, cameras, weights, starts = self._by_sector(sectors)

        keep = np.zeros(self._cameras, dtype=bool)
        rows = [int(row) for row in selected if 0 <= int(row) < self._cameras]
        if rows:
            keep[rows] = True
        kept = keep[cameras]

        if kind == "score":
            return self._score(key, weights, starts, kept, sectors)

        return self._diversity(key, kept, sectors)

    # -- internals -----------------------------------------------------

    def _by_sector(self, sectors: int):
        """The table keyed by (target, sector) and sorted, built once each."""
        if sectors not in self._sorted:
            column = np.asarray(getattr(self._scores, f"sector_{sectors}"), dtype=np.int64)
            key = self._target_of_row * sectors + column

            order = np.argsort(key, kind="stable")
            key_sorted = key[order]
            # Where each run of one (target, sector) begins, which is what
            # the reduction steps over.
            starts = np.concatenate([[0], np.flatnonzero(np.diff(key_sorted)) + 1]).astype(np.int64)

            self._sorted[sectors] = (
                key_sorted,
                np.asarray(self._scores.camera_index, dtype=np.int64)[order],
                np.asarray(self._scores.weight, dtype=np.float64)[order],
                starts,
            )

        return self._sorted[sectors]

    def _score(self, key, weights, starts, kept, sectors: int) -> np.ndarray:
        """The mean over sectors of the best weight left in each."""
        cells = np.zeros(self._targets * sectors, dtype=np.float64)
        # `starts` always holds at least the opening zero, so it is the rows
        # themselves that say whether there is anything to reduce over.
        if len(weights):
            # Struck-out rows weigh nothing rather than being removed, so the
            # runs the reduction steps over stay where they were.
            best = np.maximum.reduceat(np.where(kept, weights, 0.0), starts)
            cells[key[starts]] = best

        return cells.reshape(self._targets, sectors).mean(axis=1)

    def _diversity(self, key, kept, sectors: int) -> np.ndarray:
        """How evenly what is left is spread between the sectors."""
        counts = np.bincount(key[kept], minlength=self._targets * sectors).reshape(
            self._targets, sectors
        )
        observers = counts.sum(axis=1)

        # A target nothing sees has no spread to measure, and dividing by its
        # ideal would be dividing by zero, so it is left at nought.
        ideal = np.where(observers > 0, observers / sectors, 1.0)[:, None]
        spread = (np.minimum(counts, ideal) / ideal).mean(axis=1)

        return np.where(observers > 0, spread, 0.0)
