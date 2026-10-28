"""Unit tests for what a loaded route leaves working, in src/viewscope/window.py.

Loading a route can bring viewpoints the plan has never held. That grows the
plan, and growing the plan used to throw the rescorer away, which left the
heat map answering what the whole plan covers while a route was being chosen:
the colours stopped moving with the route for the rest of the session. The
window is run against a stand-in here, because the parts that would need a
window -- glyphs, targets, the path line -- are not the parts under test.
"""

import pytest

from viewscope.data import RoutePlan
from viewscope.window import MainWindow


class Panel:
    def __init__(self):
        self.loaded = None

    def show_loaded(self, path, added=0, unscored=0):
        self.loaded = (path, added, unscored)


class Scorer:
    """Stands in for SubsetScores: only the rows it knows are scored."""

    def __init__(self, cameras: int):
        self._cameras = cameras

    def unscored(self, selected):
        return tuple(int(row) for row in selected if int(row) >= self._cameras)


SCORE_WARNING = "The heat map counts nothing for a viewpoint the bundle never scored"


class Bar:
    def __init__(self):
        self.messages = []

    def showMessage(self, text, _timeout=0):
        self.messages.append(text)


class Window:
    """Enough of a MainWindow for a plan change to run against."""

    def __init__(self, scorer=None, planning=True):
        self.route = RoutePlan()
        if planning:
            self.route.start(3)

        self.subset_scores = scorer
        self.plan_mask = "counted"
        self.reports = None
        self.selected_camera = None
        self.plan_route_panel = Panel()
        self.viewpoints_panel = Panel()
        self.bar = Bar()
        self.refreshes = 0
        self.rebuilt = 0

        class Viewport:
            def on_plan_changed(self_):
                pass

        self.viewport = Viewport()

    def statusBar(self):
        return self.bar

    def _rebuild_target(self):
        self.rebuilt += 1

    def _refresh_route(self):
        self.refreshes += 1

    _on_plan_changed = MainWindow._on_plan_changed
    _unscored = MainWindow._unscored


@pytest.fixture(autouse=True)
def scene(monkeypatch):
    """A loaded scene of four viewpoints, one more than the bundle scored."""

    class Store:
        scene = object()
        camera_count = 4

    monkeypatch.setattr("viewscope.window.SCENE_STORE", Store())


# -----------------------------------------------------------------------------
# The heat map survives the plan growing
# -----------------------------------------------------------------------------


def test_a_viewpoint_added_to_the_plan_keeps_the_rescorer():
    """Without this the heat map stops following the route, for good."""
    scorer = Scorer(cameras=3)
    window = Window(scorer)

    window._on_plan_changed(None)

    assert window.subset_scores is scorer


def test_the_new_viewpoint_is_said_to_count_for_nothing():
    window = Window(Scorer(cameras=3))

    window._on_plan_changed(None)

    assert SCORE_WARNING in window.bar.messages


def test_nothing_is_said_about_scores_when_no_route_is_being_planned():
    """Outside planning the heat map is the shipped column either way."""
    window = Window(Scorer(cameras=3), planning=False)

    window._on_plan_changed(None)

    assert SCORE_WARNING not in window.bar.messages


def test_a_bundle_without_scores_stays_without_them():
    window = Window(scorer=None)

    window._on_plan_changed(None)

    assert window.subset_scores is None
    assert SCORE_WARNING not in window.bar.messages


def test_the_route_is_repainted_around_the_new_viewpoint():
    window = Window(Scorer(cameras=3))

    window._on_plan_changed(None)

    assert window.refreshes == 1
    assert window.plan_mask is None, "a new camera can see what nothing could see before"


# -----------------------------------------------------------------------------
# Counting what the heat map cannot credit
# -----------------------------------------------------------------------------


def test_viewpoints_past_the_score_table_are_counted():
    window = Window(Scorer(cameras=3))

    assert window._unscored([0, 1, 3, 4]) == 2


def test_a_route_the_bundle_scored_has_none():
    window = Window(Scorer(cameras=3))

    assert window._unscored([0, 1, 2]) == 0


def test_a_bundle_without_scores_counts_none():
    """There is no heat map to be wrong about, so there is nothing to report."""
    window = Window(scorer=None)

    assert window._unscored([0, 9]) == 0
