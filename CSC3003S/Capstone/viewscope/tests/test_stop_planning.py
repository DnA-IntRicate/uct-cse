"""Unit tests for stopping route planning in src/viewscope/window.py.

Stopping asks which of two things is meant: save the route, or leave planning
and keep nothing. Only the choosing is exercised here; building a whole window
would drag in VTK for no gain, so the method is run against a stand-in that
carries only the few things it touches.
"""

from pathlib import Path

import pytest

from viewscope.config import ROUTE_FILENAME
from viewscope.window import MainWindow


class Panel:
    """The one line of the panel stopping writes to."""

    def __init__(self):
        self.saved = "untouched"

    def show_saved(self, path):
        self.saved = path


class Route:
    """A route mid-planning, counting the calls that end it."""

    planning = True

    def __init__(self, path=None):
        self.stopped = 0
        self.writes = []
        self.path = path

    def __len__(self):
        return 3

    def stop(self):
        self.stopped += 1
        self.planning = False

    def save(self, path, plan, observed, targets):
        self.writes.append(path)
        self.path = path
        return path


class Bar:
    def __init__(self):
        self.messages = []

    def showMessage(self, text, _timeout=0):
        self.messages.append(text)


class Window:
    """Enough of a MainWindow for stop_route_planning to run against."""

    def __init__(self, choice, path=Path("route.json"), belongs_to=None):
        self.route = Route(belongs_to)
        self.route_mask = None
        self.plan_route_panel = Panel()
        self.bar = Bar()
        self.refreshes = 0
        self._choice = choice
        self._path = path
        self.asked_where = 0

    def statusBar(self):
        return self.bar

    def _refresh_route(self):
        self.refreshes += 1

    def _ask_stop_choice(self):
        return self._choice

    def _ask_route_path(self):
        self.asked_where += 1
        return self._path

    stop_route_planning = MainWindow.stop_route_planning


class Scene:
    plan = object()
    targets = ()


@pytest.fixture(autouse=True)
def scene(monkeypatch):
    """A loaded scene, which stopping needs before it will do anything."""

    class Store:
        scene = Scene()

    monkeypatch.setattr("viewscope.window.SCENE_STORE", Store())


# -----------------------------------------------------------------------------
# The two ways out
# -----------------------------------------------------------------------------


def test_saving_writes_the_route_and_leaves_planning():
    window = Window(choice=True)

    window.stop_route_planning()

    assert window.route.writes == [Path("route.json")]
    assert window.route.stopped == 1
    assert window.plan_route_panel.saved == Path("route.json")


def test_exiting_leaves_planning_and_writes_nothing():
    window = Window(choice=False)

    window.stop_route_planning()

    assert window.route.writes == []
    assert window.asked_where == 0, "exiting must not ask where to save"
    assert window.route.stopped == 1
    assert window.plan_route_panel.saved is None
    assert window.bar.messages == ["Left planning: the route was not saved"]


def test_exiting_still_repaints_the_scene():
    """The route colours are only worn while planning, so they must come off."""
    window = Window(choice=False)

    window.stop_route_planning()

    assert window.refreshes == 1


# -----------------------------------------------------------------------------
# Backing out
# -----------------------------------------------------------------------------


def test_closing_the_dialog_keeps_planning_on():
    window = Window(choice=None)

    window.stop_route_planning()

    assert window.route.planning
    assert window.route.stopped == 0
    assert window.plan_route_panel.saved == "untouched"


def test_backing_out_of_the_save_dialog_keeps_planning_on():
    window = Window(choice=True, path=None)

    window.stop_route_planning()

    assert window.route.planning
    assert window.route.writes == []
    assert window.bar.messages == ["Still planning: nothing was saved"]


# -----------------------------------------------------------------------------
# Saving goes back to the file the route came from
# -----------------------------------------------------------------------------


class Loader:
    def __init__(self, data_dir):
        self.data_dir = data_dir


class Asking(Window):
    """Runs the real _ask_route_path, and records what the dialog opened on."""

    def __init__(self, belongs_to, data_dir):
        super().__init__(choice=True, belongs_to=belongs_to)
        self.loader = Loader(data_dir)
        self.opened_on = None

    _ask_route_path = MainWindow._ask_route_path


@pytest.fixture
def dialog(monkeypatch):
    """A save dialog that accepts whatever it was opened on."""
    seen = {}

    class FileDialog:
        @staticmethod
        def getSaveFileName(parent, title, start, filters):
            seen["start"] = start
            return start, filters

    monkeypatch.setattr("viewscope.window.QFileDialog", FileDialog)

    return seen


def test_a_loaded_route_is_offered_back_to_its_own_file(dialog, tmp_path):
    """Load a route, stop, save: it goes where it came from, not to route.json."""
    loaded = tmp_path / "north_face.json"
    window = Asking(belongs_to=loaded, data_dir=tmp_path / "bundle")

    assert window._ask_route_path() == loaded
    assert dialog["start"] == str(loaded)


def test_a_route_from_no_file_is_offered_the_bundles_own_name(dialog, tmp_path):
    window = Asking(belongs_to=None, data_dir=tmp_path / "bundle")

    assert window._ask_route_path() == tmp_path / "bundle" / ROUTE_FILENAME


def test_saving_a_loaded_route_writes_to_that_file(tmp_path):
    """The whole path, end to end: stop -> save -> the file it was read from."""
    loaded = tmp_path / "north_face.json"
    window = Window(choice=True, path=loaded, belongs_to=loaded)

    window.stop_route_planning()

    assert window.route.writes == [loaded]


def test_exiting_leaves_the_file_it_came_from_alone(tmp_path):
    loaded = tmp_path / "north_face.json"
    window = Window(choice=False, belongs_to=loaded)

    window.stop_route_planning()

    assert window.route.writes == []
    assert window.route.path == loaded, "still the route that file holds"
