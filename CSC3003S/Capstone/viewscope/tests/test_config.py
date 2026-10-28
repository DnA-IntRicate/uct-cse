"""Unit tests for src/viewscope/config.py.

Constants need no tests; the behaviour attached to them does.
"""

from viewscope.config import COLOUR_BY_WEIGHT, TARGET_MARKER_FRACTION, OverlayOptions


def test_the_overlay_starts_drawing_rays_coloured_by_weight():
    """The defaults the panels read before the user has touched anything."""
    options = OverlayOptions()

    assert options.rays is True
    assert options.colour_by == COLOUR_BY_WEIGHT


def test_the_marker_scales_with_the_model_rather_than_being_fixed():
    """A marker sized in absolute metres vanishes on a large model."""
    small = OverlayOptions().marker_radius(10.0)
    large = OverlayOptions().marker_radius(1000.0)

    assert small == 10.0 * TARGET_MARKER_FRACTION
    assert large == 100.0 * small


def test_the_marker_radius_is_a_float_whatever_it_is_handed():
    """Callers measure the diagonal, so a whole number arrives often enough."""
    radius = OverlayOptions().marker_radius(20)

    assert isinstance(radius, float)
