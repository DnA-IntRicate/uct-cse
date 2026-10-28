"""Unit tests for src/viewscope/scene/visibility.py.

Shipped rows are a lookup and are checked as one. The recomputed path runs
against a real offscreen SceneRenderer, since that is the whole point of it:
a camera the bundle has never heard of still has to get an answer.
"""

import numpy as np
import pytest

from viewscope.scene.visibility import TargetVisibility


def masked(visibility: TargetVisibility, index: int) -> np.ndarray:
    """The mask for a camera that is known to have one."""
    mask = visibility.mask_for(index)
    assert mask is not None
    return mask


@pytest.fixture
def scene(make_scene):
    """Two shipped cameras above a box, and a shipped visibility matrix."""
    return make_scene(visibility=np.array([[True, False], [False, True]]))


# -----------------------------------------------------------------------------
# No camera, or no such camera
# -----------------------------------------------------------------------------


def test_no_camera_selected_has_no_mask(scene):
    assert TargetVisibility(scene).mask_for(None) is None


def test_a_camera_past_the_end_of_the_plan_has_no_mask(scene):
    assert TargetVisibility(scene).mask_for(2) is None


def test_a_negative_camera_has_no_mask(scene):
    assert TargetVisibility(scene).mask_for(-1) is None


# -----------------------------------------------------------------------------
# Shipped rows
# -----------------------------------------------------------------------------


def test_a_shipped_camera_reads_its_row_out_of_the_bundle(scene):
    visibility = TargetVisibility(scene)

    assert masked(visibility, 0).tolist() == [True, False]
    assert masked(visibility, 1).tolist() == [False, True]


def test_the_row_comes_back_as_booleans_whatever_the_bundle_stored(make_scene):
    """visibility.npz round-trips as uint8 on some bundles."""
    scene = make_scene(visibility=np.array([[1, 0], [0, 1]], dtype=np.uint8))

    mask = masked(TargetVisibility(scene), 0)

    assert mask.dtype == bool
    assert mask.tolist() == [True, False]


def test_a_row_is_only_looked_up_once(scene):
    visibility = TargetVisibility(scene)

    assert visibility.mask_for(0) is visibility.mask_for(0)


# -----------------------------------------------------------------------------
# Recomputing for cameras the bundle never knew about
# -----------------------------------------------------------------------------


def test_a_camera_past_the_shipped_matrix_is_recomputed(make_scene):
    """The user added this one, so nothing on disk describes it."""
    scene = make_scene(
        positions=((0.0, 0.0, 12.0), (12.0, 0.0, 6.0), (0.0, -12.0, 6.0)),
        visibility=np.array([[True, False], [False, True]]),  # only two rows
    )
    visibility = TargetVisibility(scene)

    mask = visibility.mask_for(2)

    assert mask is not None
    assert mask.dtype == bool
    assert len(mask) == len(scene.targets)
    visibility.close()


def test_a_bundle_with_no_visibility_at_all_recomputes_every_camera(make_scene):
    visibility = TargetVisibility(make_scene())

    assert visibility.mask_for(0) is not None
    visibility.close()


def test_a_recomputed_row_is_only_computed_once(make_scene):
    visibility = TargetVisibility(make_scene())

    assert visibility.mask_for(0) is visibility.mask_for(0)
    visibility.close()


def test_every_recomputed_camera_shares_the_one_renderer(make_scene):
    """Building a SceneRenderer costs a GL context, so there is only ever one."""
    visibility = TargetVisibility(make_scene())

    visibility.mask_for(0)
    renderer = visibility._renderer
    visibility.mask_for(1)

    assert visibility._renderer is renderer
    visibility.close()


# -----------------------------------------------------------------------------
# The union over a route
# -----------------------------------------------------------------------------


def test_the_union_is_what_any_one_of_them_can_see(scene):
    assert TargetVisibility(scene).union_mask([0, 1]).tolist() == [True, True]


def test_the_union_of_one_camera_is_that_cameras_mask(scene):
    assert TargetVisibility(scene).union_mask([0]).tolist() == [True, False]


def test_the_union_of_nothing_sees_nothing(scene):
    union = TargetVisibility(scene).union_mask([])

    assert union.tolist() == [False, False]


def test_cameras_that_are_not_in_the_plan_are_skipped_by_the_union(scene):
    """A stale route can name rows the plan no longer has."""
    assert TargetVisibility(scene).union_mask([0, 99, None]).tolist() == [True, False]


# -----------------------------------------------------------------------------
# Forgetting
# -----------------------------------------------------------------------------


def test_forgetting_one_camera_leaves_the_others_cached(scene):
    visibility = TargetVisibility(scene)
    first, second = visibility.mask_for(0), visibility.mask_for(1)

    visibility.forget(0)

    assert visibility.mask_for(0) is not first
    assert visibility.mask_for(1) is second


def test_forgetting_everything_drops_every_cached_row(scene):
    visibility = TargetVisibility(scene)
    first = visibility.mask_for(0)

    visibility.forget()

    assert visibility.mask_for(0) is not first


def test_forgetting_a_camera_that_was_never_cached_is_harmless(scene):
    visibility = TargetVisibility(scene)

    visibility.forget(1)

    assert masked(visibility, 1).tolist() == [False, True]


# -----------------------------------------------------------------------------
# Closing
# -----------------------------------------------------------------------------


def test_closing_before_anything_was_rendered_is_harmless(scene):
    visibility = TargetVisibility(scene)

    visibility.close()

    assert visibility.mask_for(0) is not None


def test_closing_releases_the_renderer_and_closing_twice_is_harmless(make_scene):
    visibility = TargetVisibility(make_scene())
    visibility.mask_for(0)
    assert visibility._renderer is not None

    visibility.close()
    visibility.close()

    assert visibility._renderer is None
