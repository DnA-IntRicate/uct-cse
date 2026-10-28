"""Unit tests for src/viewscope/scene/target_gizmos.py.

The overlay drawn for the picked target: the marker, the rays out to the
cameras that can see it, and the scale that reads the ray colours back. All
of it is actors, so none of it needs a window.
"""

import colorsys

import numpy as np
import pytest
import vtk

from viewscope.config import (
    COLOUR_BY_SECTOR,
    COLOUR_BY_WEIGHT,
    SECTOR_COLOURS,
    TARGET_MARKER_COLOUR,
    TOP_OBSERVER_COLOUR,
    WEIGHT_HUE,
    OverlayOptions,
)
from viewscope.scene import target_gizmos as tg
from viewscope.scene.target_gizmos import TargetOverlay, observer_colour, weight_lut
from viewscope.scene.target_report import Observer, build_report

ORIGIN = np.zeros(3)
UP = np.array([0.0, 0.0, 1.0])


@pytest.fixture
def renderer():
    return vtk.vtkRenderer()


@pytest.fixture
def overlay():
    return TargetOverlay()


def camera_at(azimuth_deg, distance=10.0, height=6.0):
    radians = np.radians(azimuth_deg)
    return [distance * np.cos(radians), distance * np.sin(radians), height]


@pytest.fixture
def report():
    """Three observers of a target at the origin, spread round the compass."""
    positions = np.array([camera_at(0.0), camera_at(120.0), camera_at(240.0)])
    return build_report(0, ORIGIN, UP, positions, np.arange(3), 8)


@pytest.fixture
def positions():
    return np.array([camera_at(0.0), camera_at(120.0), camera_at(240.0)])


def observer(camera_index=0, weight=0.5, sector=0, best=False):
    return Observer(camera_index, weight, 0.7, 0.7, sector, best)


# -----------------------------------------------------------------------------
# The colours
# -----------------------------------------------------------------------------


def test_the_weight_table_ramps_linearly_over_the_whole_range():
    """VTK's S-curve would bunch the middle weights together."""
    lut = weight_lut()

    assert lut.GetRamp() == vtk.VTK_RAMP_LINEAR
    assert lut.GetTableRange() == pytest.approx((0.0, 1.0))
    assert lut.GetHueRange() == pytest.approx((WEIGHT_HUE, WEIGHT_HUE))


def test_a_heavier_weight_reads_darker_off_the_table():
    lut = weight_lut()

    light = tg.weight_colour(lut, 0.05)
    dark = tg.weight_colour(lut, 0.95)

    assert sum(dark) < sum(light)


def test_a_weight_outside_the_range_is_pulled_back_into_it():
    lut = weight_lut()

    assert tg.weight_colour(lut, 5.0) == pytest.approx(tg.weight_colour(lut, 1.0))
    assert tg.weight_colour(lut, -5.0) == pytest.approx(tg.weight_colour(lut, 0.0))


def test_each_wedge_walks_the_colour_wheel_as_it_walks_the_compass():
    assert tg.sector_colour(0, 8) == pytest.approx(colorsys.hsv_to_rgb(0.0, 0.72, 1.0))
    assert tg.sector_colour(4, 8) == pytest.approx(colorsys.hsv_to_rgb(0.5, 0.72, 1.0))


def test_a_wedge_past_the_last_one_wraps_round():
    assert tg.sector_colour(9, 8) == pytest.approx(tg.sector_colour(1, 8))


def test_the_fixed_wedge_colours_are_taken_in_order():
    assert tg.sector_colour_2(0) == SECTOR_COLOURS[0]
    assert tg.sector_colour_2(len(SECTOR_COLOURS)) == SECTOR_COLOURS[0]


def test_an_observer_coloured_by_sector_wears_its_wedges_colour():
    colour = observer_colour(observer(sector=3), COLOUR_BY_SECTOR, weight_lut())

    assert colour == pytest.approx(tg.sector_colour(3, 8))


def test_an_observer_coloured_by_weight_wears_its_weight():
    lut = weight_lut()

    colour = observer_colour(observer(weight=0.4), COLOUR_BY_WEIGHT, lut)

    assert colour == pytest.approx(tg.weight_colour(lut, 0.4))


def test_the_heaviest_observer_is_taken_off_the_ramp_in_weight_mode():
    """The one colour that is not a weight, so it can be picked out."""
    colour = observer_colour(observer(camera_index=2), COLOUR_BY_WEIGHT, weight_lut(), 2)

    assert colour == pytest.approx(TOP_OBSERVER_COLOUR)


def test_sector_mode_ignores_which_observer_is_heaviest():
    """There the colour already answers a different question."""
    colour = observer_colour(observer(camera_index=2, sector=3), COLOUR_BY_SECTOR, weight_lut(), 2)

    assert colour == pytest.approx(tg.sector_colour(3, 8))


# -----------------------------------------------------------------------------
# Putting the overlay up
# -----------------------------------------------------------------------------


def test_nothing_is_showing_to_start_with(overlay):
    assert not overlay.showing


def test_showing_puts_the_marker_the_rays_and_the_scale_up(overlay, renderer, report, positions):
    overlay.show(renderer, report, positions, diagonal=100.0, options=OverlayOptions())

    assert overlay.showing
    assert renderer.GetActors().GetNumberOfItems() >= 2  # marker plus rays
    assert renderer.GetActors2D().GetNumberOfItems() == 1  # the weight scale


def test_the_marker_sits_on_the_picked_point(overlay, renderer, report, positions):
    overlay.show(renderer, report, positions, diagonal=100.0, options=OverlayOptions())

    marker = overlay._actors[0]
    assert marker.GetCenter() == pytest.approx(ORIGIN, abs=1e-9)
    assert marker.GetProperty().GetColor() == pytest.approx(TARGET_MARKER_COLOUR, abs=1 / 255)


def test_the_marker_scales_with_the_model(overlay, renderer, report, positions):
    overlay.show(renderer, report, positions, diagonal=100.0, options=OverlayOptions())
    big = overlay._actors[0].GetBounds()

    overlay.show(renderer, report, positions, diagonal=10.0, options=OverlayOptions())
    small = overlay._actors[0].GetBounds()

    assert (big[1] - big[0]) > (small[1] - small[0])


def test_a_marker_on_a_model_of_no_size_is_still_drawn(overlay, renderer, report, positions):
    """A zero radius sphere is not a sphere."""
    overlay.show(renderer, report, positions, diagonal=0.0, options=OverlayOptions())

    bounds = overlay._actors[0].GetBounds()
    assert bounds[1] > bounds[0]


def test_switching_off_the_rays_leaves_only_the_marker_and_the_scale(
    overlay, renderer, report, positions
):
    overlay.show(renderer, report, positions, diagonal=100.0, options=OverlayOptions(rays=False))

    assert renderer.GetActors().GetNumberOfItems() == 1


def test_colouring_by_sector_drops_the_weight_scale(overlay, renderer, report, positions):
    """The scale reads weights; in sector mode it explains nothing."""
    overlay.show(
        renderer,
        report,
        positions,
        diagonal=100.0,
        options=OverlayOptions(colour_by=COLOUR_BY_SECTOR),
    )

    assert renderer.GetActors2D().GetNumberOfItems() == 0


def test_showing_again_replaces_what_was_up(overlay, renderer, report, positions):
    overlay.show(renderer, report, positions, diagonal=100.0, options=OverlayOptions())
    before = renderer.GetActors().GetNumberOfItems()

    overlay.show(renderer, report, positions, diagonal=100.0, options=OverlayOptions())

    assert renderer.GetActors().GetNumberOfItems() == before


# -----------------------------------------------------------------------------
# The rays
# -----------------------------------------------------------------------------


def test_the_sector_winners_are_drawn_heavier_than_the_rest(overlay, renderer, positions):
    """Two bundles: one for the winners, one for everything else."""
    crowded = np.array([camera_at(0.0), camera_at(5.0), camera_at(120.0)])
    report = build_report(0, ORIGIN, UP, crowded, np.arange(3), 8)

    overlay.show(renderer, report, crowded, diagonal=100.0, options=OverlayOptions())

    widths = sorted(
        actor.GetProperty().GetLineWidth()
        for actor in overlay._actors
        if isinstance(actor, vtk.vtkActor)
        and actor.GetMapper().GetInput() is not None
        and actor.GetMapper().GetInput().GetNumberOfLines()
    )
    assert widths == pytest.approx([1.25, 3.5])


def test_every_ray_runs_from_the_target_out_to_its_camera(overlay, renderer, report, positions):
    overlay.show(renderer, report, positions, diagonal=100.0, options=OverlayOptions())

    rays = [
        actor
        for actor in overlay._actors
        if isinstance(actor, vtk.vtkActor)
        and actor.GetMapper().GetInput() is not None
        and actor.GetMapper().GetInput().GetNumberOfLines()
    ]
    drawn = sum(actor.GetMapper().GetInput().GetNumberOfLines() for actor in rays)
    assert drawn == len(report.observers)


def test_an_observer_that_is_not_in_the_plan_is_left_undrawn(overlay, renderer):
    """A stale report can name a camera the plan no longer has."""
    positions = np.array([camera_at(0.0)])
    report = build_report(
        0, ORIGIN, UP, np.array([camera_at(0.0), camera_at(90.0)]), np.array([0, 9]), 8
    )

    overlay.show(renderer, report, positions, diagonal=100.0, options=OverlayOptions())

    drawn = sum(
        actor.GetMapper().GetInput().GetNumberOfLines()
        for actor in overlay._actors
        if isinstance(actor, vtk.vtkActor)
        and actor.GetMapper().GetInput() is not None
        and actor.GetMapper().GetInput().GetNumberOfLines()
    )
    assert drawn == 1


def test_a_target_nobody_observes_gets_a_marker_and_no_rays(overlay, renderer):
    report = build_report(0, ORIGIN, UP, np.zeros((0, 3)), np.zeros(0, dtype=np.int64), 8)

    overlay.show(renderer, report, np.zeros((0, 3)), diagonal=100.0, options=OverlayOptions())

    assert renderer.GetActors().GetNumberOfItems() == 1


def test_each_ray_carries_its_own_colour(overlay, renderer, report, positions):
    overlay.show(renderer, report, positions, diagonal=100.0, options=OverlayOptions())

    rays = next(
        actor
        for actor in overlay._actors
        if isinstance(actor, vtk.vtkActor)
        and actor.GetMapper().GetInput() is not None
        and actor.GetMapper().GetInput().GetNumberOfLines()
    )
    scalars = rays.GetMapper().GetInput().GetCellData().GetScalars()
    assert scalars.GetName() == "ray"
    assert scalars.GetNumberOfComponents() == 3


# -----------------------------------------------------------------------------
# The scale
# -----------------------------------------------------------------------------


def test_the_scale_is_titled_with_what_it_reads(overlay, renderer, report, positions):
    overlay.show(renderer, report, positions, diagonal=100.0, options=OverlayOptions())

    bar = next(a for a in overlay._actors if isinstance(a, vtk.vtkActor2D))
    assert bar.GetTitle() == "weight"


# -----------------------------------------------------------------------------
# Hiding and taking it down
# -----------------------------------------------------------------------------


def test_the_overlay_can_be_hidden_and_shown(overlay, renderer, report, positions):
    overlay.show(renderer, report, positions, diagonal=100.0, options=OverlayOptions())

    overlay.set_visible(False)
    assert all(actor.GetVisibility() == 0 for actor in overlay._actors)

    overlay.set_visible(True)
    assert all(actor.GetVisibility() == 1 for actor in overlay._actors)


def test_hiding_an_overlay_that_is_not_up_is_harmless(overlay):
    overlay.set_visible(False)

    assert not overlay.showing


def test_clearing_takes_everything_off_the_renderer(overlay, renderer, report, positions):
    overlay.show(renderer, report, positions, diagonal=100.0, options=OverlayOptions())

    overlay.clear()

    assert not overlay.showing
    assert renderer.GetActors().GetNumberOfItems() == 0
    assert renderer.GetActors2D().GetNumberOfItems() == 0


def test_clearing_an_overlay_that_was_never_shown_is_harmless(overlay):
    overlay.clear()

    assert not overlay.showing
