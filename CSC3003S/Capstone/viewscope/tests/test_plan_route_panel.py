"""Unit tests for src/viewscope/panels/plan_route_panel.py.

The panel end of the route: it reports what was pressed and shows what it is
told, and does neither the planning nor the writing itself. That split is what
is checked here.
"""

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from viewscope.data.flight_path import FlightPath
from viewscope.data.route import RouteStatus
from viewscope.panels.plan_route_panel import PATH_IDLE, PATH_SHOWN, PlanRoutePanel


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def panel(app):
    return PlanRoutePanel()


@pytest.fixture
def status():
    return RouteStatus(
        planning=True,
        selected=(0, 1),
        labels=("vp000", "vp001"),
        camera_count=4,
        observed=10,
        targets=100,
        sectors=(1, 0, 0, 1, 0, 0, 0, 0),
    )


# -----------------------------------------------------------------------------
# Generating a report
# -----------------------------------------------------------------------------


def test_the_report_button_sits_under_the_flight_path(panel):
    """It is a document about the path, so it belongs with the path."""
    box = panel.path_button.parent()

    assert panel.report_button.parent() is box


def test_pressing_it_is_asked_for_and_not_done_here(panel, status):
    """The panel has no scene and no path: all it can do is say this is wanted."""
    panel.show_route(status)
    asked = []
    panel.report_requested.connect(lambda: asked.append(True))

    panel.report_button.click()

    assert asked == [True]


def test_a_report_needs_a_scene_and_nothing_more(panel, status):
    """Not a route: the path falls back to the plan, and so does the report."""
    panel.show_route(None)
    assert not panel.report_button.isEnabled()

    panel.show_route(status)
    assert panel.report_button.isEnabled()


def test_a_report_can_be_asked_for_without_planning_a_route(panel, status):
    panel.show_route(
        RouteStatus(
            planning=False,
            selected=(),
            labels=(),
            camera_count=4,
            observed=0,
            targets=100,
            sectors=(0,) * 8,
        )
    )

    assert panel.report_button.isEnabled()


def test_where_the_report_went_is_shown(panel):
    panel.show_report("/tmp/route_report.pdf")

    assert "route_report.pdf" in panel.report_note.text()


def test_another_bundle_clears_the_line(panel):
    """The report belongs to the route it was written of, not to the panel."""
    panel.show_report("/tmp/route_report.pdf")

    panel.show_route(None)

    assert panel.report_note.text() == ""


# -----------------------------------------------------------------------------
# The flight path
# -----------------------------------------------------------------------------


def a_path(
    *,
    order=(0, 1, 2),
    length=1234.0,
    detours=0,
    climbs=0,
    crossings=0,
    checked=True,
) -> FlightPath:
    """A planned path, with only the fields a test cares about spelled out."""
    return FlightPath(
        order=order,
        points=np.zeros((len(order), 3)),
        length=length,
        detours=detours,
        climbs=climbs,
        crossings=crossings,
        checked=checked,
    )


def test_the_path_is_described_by_how_far_it_runs_and_what_it_flies(panel):
    panel.show_path(a_path())

    assert "1,234 m through 3 viewpoints" in panel.path_note.text()


def test_a_path_through_one_viewpoint_is_not_pluralised(panel):
    panel.show_path(a_path(order=(0,)))

    assert "1 viewpoint" in panel.path_note.text()
    assert "viewpoints" not in panel.path_note.text()


def test_a_clear_path_says_so_plainly(panel):
    """The one thing the path promises, so it is said in as many words."""
    panel.show_path(a_path())

    assert "Nothing flies through the model." in panel.path_note.text()


def test_the_ways_it_kept_off_the_model_are_counted(panel):
    panel.show_path(a_path(detours=2, climbs=1))

    text = panel.path_note.text()
    assert "Keeping off the model: 2 round, 1 over." in text


def test_a_path_that_only_went_round_does_not_mention_climbing(panel):
    panel.show_path(a_path(detours=2))

    assert "2 round." in panel.path_note.text()
    assert "over" not in panel.path_note.text()


def test_a_path_that_only_climbed_does_not_mention_going_round(panel):
    panel.show_path(a_path(climbs=3))

    assert "3 over." in panel.path_note.text()
    assert "round" not in panel.path_note.text()


def test_hops_left_crossing_the_model_are_owned_up_to(panel):
    panel.show_path(a_path(crossings=2))

    text = panel.path_note.text()
    assert "2 hops cross the model" in text
    assert "no way round or over was found" in text


def test_a_single_crossing_is_not_pluralised(panel):
    panel.show_path(a_path(crossings=1))

    assert "1 hop cross" in panel.path_note.text()


def test_an_unchecked_path_says_nothing_was_measured(panel):
    """No obstacle, so a clear-looking path promises nothing."""
    panel.show_path(a_path(checked=False))

    assert "The model was not measured" in panel.path_note.text()
    assert "Nothing flies through" not in panel.path_note.text()


def test_no_path_blanks_the_line(panel):
    panel.show_path(a_path())

    panel.show_path(None)

    assert panel.path_note.text() == "--"


# -----------------------------------------------------------------------------
# The path button
# -----------------------------------------------------------------------------


def test_pressing_the_path_button_asks_for_the_path(panel):
    asked = []
    panel.path_requested.connect(asked.append)

    panel.path_button.setChecked(True)

    assert asked == [True]
    assert panel.path_button.text() == PATH_SHOWN


def test_letting_the_path_button_up_asks_for_it_to_go_and_blanks_the_line(panel):
    panel.path_button.setChecked(True)
    panel.show_path(a_path())
    asked = []
    panel.path_requested.connect(asked.append)

    panel.path_button.setChecked(False)

    assert asked == [False]
    assert panel.path_button.text() == PATH_IDLE
    assert panel.path_note.text() == "--"


def test_losing_the_scene_lets_the_path_button_back_up(panel, status):
    """Nothing to draw a path through, so the button must not stay pressed."""
    panel.show_route(status)
    panel.path_button.setChecked(True)

    panel.show_route(None)

    assert not panel.path_button.isChecked()
    assert not panel.path_button.isEnabled()


# -----------------------------------------------------------------------------
# Where things were written
# -----------------------------------------------------------------------------


def test_saving_the_route_says_where_it_went(panel):
    panel.show_saved("/tmp/route.json")

    assert panel.note.text() == "Saved to /tmp/route.json"


def test_clearing_the_saved_line_empties_it(panel):
    panel.show_saved("/tmp/route.json")

    panel.show_saved(None)

    assert panel.note.text() == ""


def test_writing_a_report_says_where_it_went(panel):
    panel.show_report("/tmp/report.md")

    assert panel.report_note.text() == "Report written to /tmp/report.md"


def test_clearing_the_report_line_empties_it(panel):
    panel.show_report("/tmp/report.md")

    panel.show_report(None)

    assert panel.report_note.text() == ""


def test_a_report_written_of_another_bundle_is_not_this_ones(panel, status):
    panel.show_report("/tmp/report.md")

    panel.show_route(None)

    assert panel.report_note.text() == ""


# -----------------------------------------------------------------------------
# Loading a route
# -----------------------------------------------------------------------------


def test_loading_says_where_the_route_came_from(panel):
    panel.show_loaded("/tmp/route.json")

    text = panel.note.text()
    assert "Loaded from /tmp/route.json." in text
    assert "the rest of the plan is still on screen" in text


def test_a_route_that_brought_viewpoints_with_it_says_how_many(panel):
    panel.show_loaded("/tmp/route.json", added=3)

    assert "adding 3 viewpoints to the plan" in panel.note.text()


def test_one_added_viewpoint_is_not_pluralised(panel):
    panel.show_loaded("/tmp/route.json", added=1)

    assert "adding 1 viewpoint to" in panel.note.text()


def test_viewpoints_the_bundle_never_scored_are_flagged(panel):
    """The route still flies; it is the heat map that cannot speak for them."""
    panel.show_loaded("/tmp/route.json", added=2, unscored=2)

    assert "the heat map counts nothing for 2 of them" in panel.note.text()


def test_a_fully_scored_route_says_nothing_about_the_heat_map(panel):
    panel.show_loaded("/tmp/route.json")

    assert "heat map" not in panel.note.text()
