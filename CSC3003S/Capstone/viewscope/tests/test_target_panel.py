"""Unit tests for src/viewscope/panels/target_panel.py.

The panel restates a report and reports what was clicked; it does neither the
scoring nor the drawing. That split is what is checked here.
"""

import numpy as np
import pytest

from viewscope.config import COLOUR_BY_SECTOR, SECTOR_COUNTS, TARGET_COLOUR_MODES
from viewscope.panels.target_panel import HINT, TargetPanel
from viewscope.scene.target_report import build_report

ORIGIN = np.zeros(3)
UP = np.array([0.0, 0.0, 1.0])


@pytest.fixture
def panel(app):
    return TargetPanel()


def camera_at(azimuth_deg, distance=10.0, height=6.0):
    radians = np.radians(azimuth_deg)
    return [distance * np.cos(radians), distance * np.sin(radians), height]


@pytest.fixture
def report():
    """Three observers of a target at the origin, in three different wedges."""
    positions = np.array([camera_at(0.0), camera_at(120.0), camera_at(240.0)])
    return build_report(7, ORIGIN, UP, positions, np.array([0, 2, 5]), 8)


def rows_of(table):
    return [
        [table.item(r, c).text() for c in range(table.columnCount())]
        for r in range(table.rowCount())
    ]


# -----------------------------------------------------------------------------
# With nothing picked
# -----------------------------------------------------------------------------


def test_the_panel_opens_asking_for_a_target(panel):
    assert panel.hint.text() == HINT
    assert not panel.clear_button.isEnabled()


def test_the_summary_starts_blank(panel):
    assert all(label.text() == "--" for label in panel.rows.values())
    assert panel.source.text() == ""


def test_both_tables_start_empty(panel):
    assert panel.sector_table.rowCount() == 0
    assert panel.observer_table.rowCount() == 0


def test_the_summary_rows_are_the_ones_the_panel_names(panel):
    assert list(panel.rows) == list(TargetPanel.SUMMARY_KEYS)


# -----------------------------------------------------------------------------
# The decomposition controls
# -----------------------------------------------------------------------------


def test_the_sector_counts_are_the_ones_the_config_names(panel):
    offered = [panel.sectors.itemText(i) for i in range(panel.sectors.count())]

    assert offered == [str(count) for count in SECTOR_COUNTS]


def test_the_sector_count_is_read_back_as_a_number(panel):
    assert panel.sector_count == SECTOR_COUNTS[0]


def test_changing_the_sector_count_asks_for_the_report_to_be_rebuilt(panel):
    asked = []
    panel.sector_count_changed.connect(asked.append)

    panel.sectors.setCurrentText(str(SECTOR_COUNTS[1]))

    assert asked == [SECTOR_COUNTS[1]]
    assert panel.sector_count == SECTOR_COUNTS[1]


def test_the_colour_modes_are_the_ones_the_config_names(panel):
    offered = [panel.colour_by.itemText(i) for i in range(panel.colour_by.count())]

    assert offered == TARGET_COLOUR_MODES


def test_changing_the_colour_mode_only_redraws_the_overlay(panel):
    """Nothing needs rescoring: it is the same numbers in another colour."""
    redrawn, rebuilt = [], []
    panel.overlay_changed.connect(lambda: redrawn.append(True))
    panel.sector_count_changed.connect(rebuilt.append)

    panel.colour_by.setCurrentText(COLOUR_BY_SECTOR)

    assert redrawn == [True]
    assert rebuilt == []


def test_toggling_the_rays_only_redraws_the_overlay(panel):
    redrawn = []
    panel.overlay_changed.connect(lambda: redrawn.append(True))

    panel.rays.setChecked(False)

    assert redrawn == [True]


def test_the_options_say_how_the_overlay_should_be_drawn(panel):
    panel.rays.setChecked(False)
    panel.colour_by.setCurrentText(COLOUR_BY_SECTOR)

    options = panel.options()

    assert options.rays is False
    assert options.colour_by == COLOUR_BY_SECTOR


def test_the_options_start_out_showing_rays(panel):
    assert panel.options().rays is True


# -----------------------------------------------------------------------------
# Showing a target
# -----------------------------------------------------------------------------


def test_picking_a_target_names_it_and_lets_it_be_cleared(panel, report):
    panel.show_target(report)

    assert panel.hint.text() == "Target 7"
    assert panel.clear_button.isEnabled()


def test_the_summary_restates_the_report(panel, report):
    panel.show_target(report)

    assert panel.rows["Target"].text() == "7"
    assert panel.rows["Position"].text() == "0.00, 0.00, 0.00"
    assert panel.rows["Normal"].text() == "0.00, 0.00, 1.00"
    assert panel.rows["Observers"].text() == "3"
    assert panel.rows["Score"].text() == f"{report.score:.4f}"
    assert panel.rows["Diversity"].text() == f"{report.diversity:.4f}"


def test_the_summary_says_how_many_wedges_are_occupied(panel, report):
    panel.show_target(report)

    assert panel.rows["Sectors"].text() == f"{report.occupied_sectors} of 8 occupied"


def test_there_is_one_sector_row_per_wedge_occupied_or_not(panel, report):
    panel.show_target(report)

    assert panel.sector_table.rowCount() == 8


def test_an_empty_wedge_shows_no_weight_and_no_camera(panel, report):
    panel.show_target(report)

    empty = [row for row in rows_of(panel.sector_table) if row[1] == "0"]
    assert empty
    assert all(row[2] == "--" and row[3] == "--" for row in empty)


def test_an_occupied_wedge_names_its_best_camera_counted_from_one(panel, report):
    """The tables are read by people, who count viewpoints from one."""
    panel.show_target(report)

    occupied = [row for row in rows_of(panel.sector_table) if row[1] != "0"]
    assert occupied
    assert all(row[3] in {"1", "3", "6"} for row in occupied)


def test_there_is_one_observer_row_per_camera(panel, report):
    panel.show_target(report)

    assert panel.observer_table.rowCount() == 3


def test_an_observer_row_carries_its_weight_and_both_factors(panel, report):
    panel.show_target(report)

    first = rows_of(panel.observer_table)[0]
    top = report.observers[0]
    assert first[0] == str(top.camera_index + 1)
    assert first[2] == f"{top.weight:.3f}"
    assert first[3] == f"{top.f_rho:.3f}"
    assert first[4] == f"{top.f_theta:.3f}"
    assert first[5] == top.limited_by


def test_a_sector_winner_is_marked_in_its_row(panel, report):
    panel.show_target(report)

    marks = [row[6] for row in rows_of(panel.observer_table)]
    assert "yes" in marks


def test_the_bar_chart_follows_the_picked_target(panel, report):
    panel.show_target(report)

    assert "Target: 7" in panel.sector_bar_chart.chart.title()


# -----------------------------------------------------------------------------
# Where the numbers came from
# -----------------------------------------------------------------------------


def test_a_recomputed_report_says_so(panel):
    positions = np.array([camera_at(0.0)])
    live = build_report(0, ORIGIN, UP, positions, np.array([0]), 8, live=True)

    panel.show_target(live)

    assert "Recomputed for the edited plan" in panel.source.text()


def test_an_assumed_report_says_so(panel):
    positions = np.array([camera_at(0.0)])
    assumed = build_report(0, ORIGIN, UP, positions, np.array([0]), 8, assumed_visibility=True)

    panel.show_target(assumed)

    assert "assumed to see this target" in panel.source.text()


def test_a_report_read_straight_off_the_bundle_says_nothing(panel, report):
    panel.show_target(report)

    assert panel.source.text() == ""


# -----------------------------------------------------------------------------
# Dropping the target
# -----------------------------------------------------------------------------


def test_clearing_empties_the_panel(panel, report):
    panel.show_target(report)

    panel.show_target(None)

    assert panel.hint.text() == HINT
    assert all(label.text() == "--" for label in panel.rows.values())
    assert panel.sector_table.rowCount() == 0
    assert panel.observer_table.rowCount() == 0
    assert panel.source.text() == ""


def test_clearing_takes_the_note_about_the_numbers_off_too(panel):
    positions = np.array([camera_at(0.0)])
    panel.show_target(build_report(0, ORIGIN, UP, positions, np.array([0]), 8, live=True))

    panel.show_target(None)

    assert panel.source.text() == ""


def test_the_clear_button_asks_for_the_selection_to_be_dropped(panel, report):
    panel.show_target(report)
    asked = []
    panel.cleared.connect(lambda: asked.append(True))

    panel.clear_button.click()

    assert asked == [True]


def test_a_chart_that_will_not_draw_does_not_stop_the_panel(panel, report, monkeypatch):
    """The breakdown is worth more than the picture of it."""

    def broken(_report):
        raise RuntimeError("no chart today")

    monkeypatch.setattr(panel.sector_bar_chart, "update_chart", broken)

    panel.show_target(report)

    assert panel.observer_table.rowCount() == 3


# -----------------------------------------------------------------------------
# Picking a camera out of the table
# -----------------------------------------------------------------------------


def test_with_no_target_no_camera_is_selected(panel):
    assert panel.selected_camera_row() is None


def test_with_nothing_highlighted_no_camera_is_selected(panel, report):
    panel.show_target(report)

    assert panel.selected_camera_row() is None


def test_highlighting_a_row_reports_its_plan_index(panel, report):
    """The row is counted from zero; the camera keeps its own plan row."""
    panel.show_target(report)

    panel.observer_table.selectRow(1)

    assert panel.selected_camera_row() == report.observers[1].camera_index


def test_clicking_a_row_asks_for_that_camera(panel, report):
    panel.show_target(report)
    picked = []
    panel.camera_picked.connect(picked.append)

    panel.observer_table.selectRow(2)

    assert picked == [report.observers[2].camera_index]


def test_filling_the_table_does_not_look_like_a_click(panel, report):
    """Otherwise showing a target would jump the viewport to a camera."""
    picked = []
    panel.camera_picked.connect(picked.append)

    panel.show_target(report)

    assert picked == []


# -----------------------------------------------------------------------------
# Following a selection made elsewhere
# -----------------------------------------------------------------------------


def test_a_camera_selected_elsewhere_is_highlighted_without_being_echoed(panel, report):
    panel.show_target(report)
    picked = []
    panel.camera_picked.connect(picked.append)

    panel.select_camera(report.observers[1].camera_index)

    assert [i.row() for i in panel.observer_table.selectionModel().selectedRows()] == [1]
    assert picked == []


def test_selecting_no_camera_clears_the_highlight(panel, report):
    panel.show_target(report)
    panel.select_camera(report.observers[0].camera_index)

    panel.select_camera(None)

    assert panel.observer_table.selectionModel().selectedRows() == []


def test_selecting_a_camera_that_does_not_observe_this_target_clears_it(panel, report):
    """The viewport's camera need not be one of the observers."""
    panel.show_target(report)
    panel.select_camera(report.observers[0].camera_index)

    panel.select_camera(99)

    assert panel.observer_table.selectionModel().selectedRows() == []


def test_selecting_a_camera_with_no_target_up_is_harmless(panel):
    panel.select_camera(3)

    assert panel.observer_table.selectionModel().selectedRows() == []


def test_clearing_the_highlight_in_the_table_picks_no_camera(panel, report):
    """Deselecting is not a pick, so the viewport is not jumped anywhere."""
    panel.show_target(report)
    panel.observer_table.selectRow(0)
    picked = []
    panel.camera_picked.connect(picked.append)

    panel.observer_table.clearSelection()

    assert picked == []
