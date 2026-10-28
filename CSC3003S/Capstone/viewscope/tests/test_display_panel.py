"""Unit tests for src/viewscope/panels/display_panel.py.

The panel owns no state of its own: every control just announces what the
user did, so the signals are what is checked.
"""

import pytest

from viewscope.config import MODE_ALL, MODES, SCALAR_FIELDS
from viewscope.panels.display_panel import DisplayPanel


@pytest.fixture
def panel(app):
    return DisplayPanel()


def heard(signal):
    """Collect whatever a signal emits."""
    seen = []
    signal.connect(seen.append)
    return seen


# -----------------------------------------------------------------------------
# What the panel starts out saying
# -----------------------------------------------------------------------------


def test_the_display_modes_are_the_ones_the_config_names(panel):
    assert [panel.mode.itemText(i) for i in range(panel.mode.count())] == MODES


def test_the_panel_opens_showing_everything(panel):
    assert panel.mode.currentText() == MODE_ALL


def test_the_scalar_fields_are_the_ones_the_config_names(panel):
    assert [panel.field.itemText(i) for i in range(panel.field.count())] == SCALAR_FIELDS


def test_the_point_size_starts_small_and_stays_in_range(panel):
    assert panel.point_size.value() == 2
    assert (panel.point_size.minimum(), panel.point_size.maximum()) == (1, 10)


def test_the_frustums_and_the_grid_start_on_and_the_wireframe_starts_off(panel):
    assert panel.glyphs.isChecked()
    assert panel.grid.isChecked()
    assert not panel.glyph_wireframe.isChecked()


def test_the_flags_and_the_occlusion_button_start_off(panel):
    assert not panel.unobserved.isChecked()
    assert not panel.occlusion.isChecked()


def test_the_occlusion_button_stays_pressed_until_pressed_again(panel):
    assert panel.occlusion.isCheckable()


# -----------------------------------------------------------------------------
# What it announces
# -----------------------------------------------------------------------------


def test_changing_the_display_mode_is_announced(panel):
    seen = heard(panel.mode_changed)

    panel.mode.setCurrentText(MODES[0])

    assert seen == [MODES[0]]


def test_changing_the_scalar_field_is_announced(panel):
    seen = heard(panel.field_changed)

    panel.field.setCurrentText(SCALAR_FIELDS[2])

    assert seen == [SCALAR_FIELDS[2]]


def test_moving_the_point_size_is_announced(panel):
    seen = heard(panel.point_size_changed)

    panel.point_size.setValue(7)

    assert seen == [7]


def test_toggling_the_frustums_is_announced(panel):
    seen = heard(panel.glyphs_toggled)

    panel.glyphs.setChecked(False)

    assert seen == [False]


def test_toggling_the_grid_is_announced(panel):
    seen = heard(panel.grid_toggled)

    panel.grid.setChecked(False)

    assert seen == [False]


def test_toggling_the_wireframe_is_announced(panel):
    seen = heard(panel.glyph_wireframe_toggled)

    panel.glyph_wireframe.setChecked(True)

    assert seen == [True]


def test_toggling_the_unobserved_flag_is_announced(panel):
    seen = heard(panel.unobserved_toggled)

    panel.unobserved.setChecked(True)

    assert seen == [True]


def test_pressing_the_occlusion_button_is_announced_both_ways(panel):
    seen = heard(panel.occlusion_toggled)

    panel.occlusion.setChecked(True)
    panel.occlusion.setChecked(False)

    assert seen == [True, False]


# -----------------------------------------------------------------------------
# A bundle with no scores
# -----------------------------------------------------------------------------


def test_the_field_picker_can_be_switched_off(panel):
    """Nothing to colour by, so the control must not offer to."""
    panel.disable_fields()

    assert not panel.field.isEnabled()
    assert panel.mode.isEnabled()
