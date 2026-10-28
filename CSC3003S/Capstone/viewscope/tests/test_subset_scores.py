"""Unit tests for src/viewscope/scene/subset_scores.py.

The rescorer's whole claim is that filtering the shipped observation table
gives the same answer the library would give from scratch, so that is what is
checked: every case is compared against `viewscope_core` itself rather than
against numbers written down here.
"""

from types import SimpleNamespace

import numpy as np
import pytest

import viewscope_core as vc
from viewscope.scene import SubsetScores

CAMERAS = 3
TARGETS = 4

#: Which target each row belongs to, as the offsets say: target 0 has two
#: observers, target 1 has three, target 2 has none at all, target 3 has two.
OFFSETS = np.array([0, 2, 5, 5, 7], dtype=np.int64)
CAMERA_INDEX = np.array([0, 1, 0, 1, 2, 2, 0], dtype=np.int64)
WEIGHT = np.array([0.8, 0.4, 0.2, 0.9, 0.5, 0.3, 0.6], dtype=np.float64)
SECTOR_8 = np.array([0, 3, 1, 1, 5, 2, 2], dtype=np.int64)
SECTOR_4 = np.array([0, 1, 0, 0, 2, 1, 1], dtype=np.int64)


def rows_of(target: int):
    """The window of the table belonging to one target."""
    return slice(int(OFFSETS[target]), int(OFFSETS[target + 1]))


def by_hand(field: str, selected) -> np.ndarray:
    """What the library makes of the same rows, one target at a time."""
    kind, sectors = field.split("_")
    sectors = int(sectors)
    column = SECTOR_8 if sectors == 8 else SECTOR_4
    keep = set(int(row) for row in selected)

    out = np.zeros(TARGETS, dtype=np.float64)
    for target in range(TARGETS):
        window = rows_of(target)
        mine = np.array([camera in keep for camera in CAMERA_INDEX[window]], dtype=bool)
        weights, buckets = WEIGHT[window][mine], column[window][mine]
        if not len(weights):
            continue

        out[target] = (
            vc.target_score(buckets, weights, sectors)
            if kind == "score"
            else vc.angular_diversity(buckets, sectors)
        )

    return out


@pytest.fixture
def scores():
    """A small scores table, with its columns filled in by the library."""
    return vc.Scores(
        offsets=OFFSETS,
        camera_index=CAMERA_INDEX,
        weight=WEIGHT,
        f_rho=np.ones_like(WEIGHT),
        f_theta=np.ones_like(WEIGHT),
        sector_8=SECTOR_8,
        sector_4=SECTOR_4,
        best_8=np.zeros(len(WEIGHT), dtype=bool),
        best_4=np.zeros(len(WEIGHT), dtype=bool),
        diversity_8=by_hand("diversity_8", range(CAMERAS)),
        diversity_4=by_hand("diversity_4", range(CAMERAS)),
        score_8=by_hand("score_8", range(CAMERAS)),
        score_4=by_hand("score_4", range(CAMERAS)),
        meta={"target_count": TARGETS, "camera_count": CAMERAS},
    )


@pytest.fixture
def subset(scores):
    return SubsetScores(scores, TARGETS, CAMERAS)


ALL_FIELDS = ("score_8", "score_4", "diversity_8", "diversity_4")


# -----------------------------------------------------------------------------
# It says what the library says
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("field", ALL_FIELDS)
def test_the_whole_plan_reproduces_the_column_the_bundle_shipped(subset, scores, field):
    """Every camera in means the answer the bundle already wrote down."""
    assert subset.values(field, range(CAMERAS)) == pytest.approx(getattr(scores, field))


@pytest.mark.parametrize("field", ALL_FIELDS)
@pytest.mark.parametrize("selected", [(0,), (1,), (2,), (0, 2), (1, 2), (0, 1)])
def test_a_subset_says_what_the_library_says_of_the_same_rows(subset, field, selected):
    """Which is the whole claim: struck-out rows, same reduction, same answer."""
    assert subset.values(field, selected) == pytest.approx(by_hand(field, selected))


@pytest.mark.parametrize("field", ALL_FIELDS)
def test_no_cameras_scores_nothing(subset, field):
    """An empty route is a cold map, not a blank one or a divide by zero."""
    assert subset.values(field, []) == pytest.approx(np.zeros(TARGETS))


def test_a_target_nothing_observes_stays_at_nought(subset):
    """Target 2 has no rows at all, whoever is in the route."""
    for selected in ([], [0], [0, 1, 2]):
        assert subset.values("score_8", selected)[2] == 0.0
        assert subset.values("diversity_8", selected)[2] == 0.0


def test_adding_a_camera_never_lowers_a_score(subset):
    """A camera can only add an observer, and the score takes the best of them."""
    one = subset.values("score_8", [0])
    two = subset.values("score_8", [0, 1])

    assert np.all(two >= one - 1e-12)


def test_rows_beyond_the_plan_are_ignored(subset):
    """A route carried over from a longer plan must not index off the end."""
    assert subset.values("score_8", [0, 99]) == pytest.approx(subset.values("score_8", [0]))


# -----------------------------------------------------------------------------
# The scale the map is coloured on
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("field", ALL_FIELDS)
def test_the_scale_is_the_whole_plans_not_the_routes(subset, scores, field):
    """Rescaled to the route, one camera would paint its patch full coverage."""
    low, high = subset.full_range(field)

    assert low == 0.0
    assert high == pytest.approx(float(np.asarray(getattr(scores, field)).max()))
    assert high >= subset.values(field, [0]).max()


def test_the_scale_does_not_move_with_the_selection(subset):
    """It is what makes a colour mean the same thing from one click to the next."""
    before = subset.full_range("score_8")
    subset.values("score_8", [0])

    assert subset.full_range("score_8") == before


# -----------------------------------------------------------------------------
# What it will and will not answer
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("field", ALL_FIELDS)
def test_every_scored_field_is_handled(field):
    assert SubsetScores.handles(field)


def test_a_field_it_cannot_rescore_is_turned_down(subset):
    """So the caller falls back to the shipped column instead of guessing."""
    assert not SubsetScores.handles("f_rho")
    assert not SubsetScores.handles("nonsense")


# -----------------------------------------------------------------------------
# Viewpoints the table never knew about
# -----------------------------------------------------------------------------


def test_a_viewpoint_past_the_table_is_named_as_unscored(subset):
    """A loaded route can bring one; the heat map has nothing to credit it with."""
    assert subset.unscored([0, 1, CAMERAS, CAMERAS + 4]) == (CAMERAS, CAMERAS + 4)


def test_a_route_the_bundle_scored_has_nothing_unscored(subset):
    assert subset.unscored(range(CAMERAS)) == ()


def test_an_unscored_viewpoint_does_not_stop_the_rest_being_rescored(subset):
    """The route still colours: what it cannot answer for is one viewpoint."""
    assert subset.values("score_8", [0, CAMERAS + 7]) == pytest.approx(
        subset.values("score_8", [0])
    )


# -----------------------------------------------------------------------------
# A table with nothing in it
# -----------------------------------------------------------------------------


def empty_scores():
    """A bundle whose target is seen by nobody: a real, if unusual, table."""
    return SimpleNamespace(
        offsets=np.array([0, 0], dtype=np.int64),
        camera_index=np.zeros(0, dtype=np.int32),
        weight=np.zeros(0, dtype=np.float32),
        sector_8=np.zeros(0, dtype=np.int8),
        sector_4=np.zeros(0, dtype=np.int8),
    )


def test_a_target_nobody_observes_scores_zero_rather_than_raising():
    """There is nothing to reduce over, which is an answer, not an error."""
    subset = SubsetScores(empty_scores(), target_count=1, camera_count=2)

    assert subset.values("score_8", [0, 1]) == pytest.approx([0.0])


def test_a_target_nobody_observes_has_no_diversity_either():
    subset = SubsetScores(empty_scores(), target_count=1, camera_count=2)

    assert subset.values("diversity_8", [0, 1]) == pytest.approx([0.0])
