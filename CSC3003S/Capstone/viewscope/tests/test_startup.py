# Unit tests for src/viewscope/startup.py

import os

# Must be set before Qt picks a platform plugin, so these run without a display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


import json  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
from PySide6.QtCore import (
    QSettings,  # noqa: E402
    Qt,  # noqa: E402
)
from PySide6.QtWidgets import QApplication  # noqa: E402

from viewscope import startup  # noqa: E402
from viewscope.config import Project  # noqa: E402
from viewscope.data.loader import STAGE_COUNT  # noqa: E402
from viewscope.dialogs import build_bundle_dialog  # noqa: E402
from viewscope.dialogs.build_bundle_dialog import BuildBundleDialog  # noqa: E402
from viewscope.startup import (  # noqa: E402
    QUALITY_HIGH,
    QUALITY_LOW,
    QUALITY_MEDIUM,
    ProjectCard,
    StartupWindow,
    _Build,
)

PROJECTS = (Project(name="Kiri Building", subtitle="A test bundle", data_dir=Path("data/kiri")),)


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def settings(tmp_path):
    """A throwaway ini, so the tests never touch the real saved project list."""
    return QSettings(str(tmp_path / "viewscope.ini"), QSettings.Format.IniFormat)


@pytest.fixture
def page(app, settings):
    window = StartupWindow(PROJECTS, settings=settings)
    yield window
    window.close()


def test_lists_every_project(page):
    """One card per project, keyed by the bundle it opens."""
    assert list(page.cards) == ["data/kiri"]
    assert page.cards["data/kiri"].project is PROJECTS[0]


def test_card_click_asks_for_its_project(app):
    card = ProjectCard(PROJECTS[0])
    picked = []
    card.clicked.connect(picked.append)

    card.activate()

    assert picked == [PROJECTS[0]]


def test_busy_card_ignores_further_clicks(app):
    card = ProjectCard(PROJECTS[0])
    picked = []
    card.clicked.connect(picked.append)

    card.set_busy(True)
    card.activate()

    assert picked == []
    assert card.property("busy") is True


def test_opening_shows_the_bar_and_marks_the_card_busy(page):
    """The viewer itself is built on the next event loop turn, which the test never runs."""
    page.open_project(PROJECTS[0])

    assert page.cards["data/kiri"].property("busy") is True
    assert not page.bar.isHidden()
    assert page.bar.value() == 0
    assert page.bar.maximum() == STAGE_COUNT
    assert "Kiri Building" in page.status.text()


def test_the_full_budget_is_the_default(page):
    """6G is picked when the page opens, so a project loads everything it ships."""
    assert page.quality_buttons[QUALITY_MEDIUM].isChecked()
    assert not page.quality_buttons[QUALITY_LOW].isChecked()
    assert not page.quality_buttons[QUALITY_HIGH].isChecked()
    assert page.load_photo_mesh is True
    assert page.full_resolution_mesh is False


def test_the_three_budgets_are_offered_in_order(page):
    """400MB, 6G, 10G, left to right in the corner."""
    assert list(page.quality_buttons) == [QUALITY_LOW, QUALITY_MEDIUM, QUALITY_HIGH]


def test_the_max_budget_reads_the_model_whole(page):
    """Picking 10G still loads the model, but uncapped and uncached."""
    page.quality_buttons[QUALITY_HIGH].click()

    assert page.load_photo_mesh is True
    assert page.full_resolution_mesh is True
    assert not page.quality_buttons[QUALITY_MEDIUM].isChecked()


def test_only_the_max_budget_asks_for_full_resolution(page):
    """The other two leave the loader on its capped, cached path."""
    for label in (QUALITY_LOW, QUALITY_MEDIUM):
        page.quality_buttons[label].click()
        assert page.full_resolution_mesh is False, label


def test_the_max_budget_still_has_a_second_phase(page):
    """10G reads the same model as 6G, so the bar switches over just the same."""
    page.quality_buttons[QUALITY_HIGH].click()
    page.open_project(PROJECTS[0])

    page._on_scene_loaded(None)

    assert page.bar.maximum() == 100
    assert "full-resolution" in page.status.text()


def test_the_light_budget_drops_the_full_resolution_model(page):
    """Picking 400MB unpicks 6G, and the viewer is told to stay on the simplified mesh."""
    page.quality_buttons[QUALITY_LOW].click()

    assert not page.quality_buttons[QUALITY_MEDIUM].isChecked()
    assert page.load_photo_mesh is False


def test_the_light_budget_leaves_the_bar_on_stages(page):
    """There is no second, full-resolution phase to switch the bar over to."""
    page.quality_buttons[QUALITY_LOW].click()
    page.open_project(PROJECTS[0])

    page._on_scene_loaded(None)

    assert page.bar.maximum() == STAGE_COUNT
    assert "full-resolution" not in page.status.text()


def test_the_full_budget_switches_the_bar_to_the_second_phase(page):
    page.open_project(PROJECTS[0])

    page._on_scene_loaded(None)

    assert page.bar.maximum() == 100
    assert "full-resolution" in page.status.text()


def test_the_budget_is_frozen_while_a_project_opens(page):
    """It is read once, when the project opens, so it must not be moved after that."""
    page.open_project(PROJECTS[0])
    assert not any(b.isEnabled() for b in page.quality_buttons.values())
    assert len(page.quality_buttons) == 3

    page._on_failed("no such bundle")
    assert all(b.isEnabled() for b in page.quality_buttons.values())


def test_stages_advance_the_bar(page):
    page.open_project(PROJECTS[0])

    page._on_stage(3, STAGE_COUNT)

    assert page.bar.value() == 3
    assert page.bar.maximum() == STAGE_COUNT


def test_failure_puts_the_page_back(page):
    page.open_project(PROJECTS[0])

    page._on_failed("no such bundle")

    assert page.viewer is None
    assert page.cards["data/kiri"].property("busy") is False
    assert page.bar.isHidden()
    assert "try again" in page.status.text()


# -- adding a project ------------------------------------------------------


def bundle(folder: Path) -> Path:
    """A folder holding the six files a bundle must have."""
    folder.mkdir(parents=True, exist_ok=True)
    for name in ("scene.obj", "targets.ply", "plan.json", *NPZ_FILES):
        (folder / name).write_text("")
    return folder


NPZ_FILES = ("scores.npz", "visibility.npz", "flyable.npz")


def test_adding_a_complete_bundle(page, tmp_path):
    folder = bundle(tmp_path / "seahawk")

    assert page.add_folder(folder) is True
    assert str(folder) in page.cards
    assert page.projects[-1].name == "seahawk"
    assert "Added seahawk" in page.status.text()


def test_adding_an_incomplete_folder_is_refused(page, tmp_path):
    folder = tmp_path / "half"
    folder.mkdir()
    (folder / "scene.obj").write_text("")

    assert page.add_folder(folder) is False
    assert str(folder) not in page.cards
    assert "plan.json" in page.status.text()


def test_the_same_folder_is_not_added_twice(page, tmp_path):
    folder = bundle(tmp_path / "seahawk")
    page.add_folder(folder)

    assert page.add_folder(folder) is False
    assert len(page.cards) == 2  # the shipped one and the one added once


def test_added_projects_come_back_next_run(app, settings, tmp_path):
    folder = bundle(tmp_path / "seahawk")
    first = StartupWindow(PROJECTS, settings=settings)
    first.add_folder(folder)
    first.close()

    second = StartupWindow(PROJECTS, settings=settings)
    try:
        assert str(folder) in second.cards
        assert second.projects[-1].data_dir == folder
    finally:
        second.close()


def test_removing_an_added_project(page, tmp_path):
    folder = bundle(tmp_path / "seahawk")
    page.add_folder(folder)

    page.remove_project(page.projects[-1])

    assert str(folder) not in page.cards
    assert [p.name for p in page.projects] == ["Kiri Building"]

    # and it stays gone
    revisit = StartupWindow(PROJECTS, settings=page.settings)
    try:
        assert str(folder) not in revisit.cards
    finally:
        revisit.close()


def test_three_cards_keep_their_height_and_do_not_overlap(page, tmp_path):
    """A card that re-lays-out its own subtitle used to loop until the stack blew."""
    page.resize(880, 680)
    page.show()
    QApplication.processEvents()

    for index in range(2):
        page.add_folder(bundle(tmp_path / f"bundle{index}"))
    QApplication.processEvents()

    rows = [card.geometry() for card in page.cards.values()]
    assert [row.height() for row in rows] == [ProjectCard.HEIGHT] * 3
    for above, below in zip(rows, rows[1:], strict=False):  # consecutive pairs
        assert above.bottom() < below.top()


def test_a_long_subtitle_is_elided_into_the_card(page, tmp_path):
    folder = bundle(tmp_path / ("deeply/" * 12 + "nested"))
    page.resize(880, 680)
    page.show()
    page.add_folder(folder)
    QApplication.processEvents()

    card = page.cards[str(folder)]
    assert card.subtitle.text() != str(folder)  # shortened to fit
    assert "…" in card.subtitle.text()


# -- coming back, and building --------------------------------------------


def test_back_shows_the_page_and_resets_it(page):
    page.hide()
    page.status.setText("Ready")
    page.bar.show()
    next(iter(page.cards.values())).set_busy(True)

    page.show_projects()

    assert page.isVisible()
    assert page.viewer is None
    assert page.bar.isHidden()
    assert not next(iter(page.cards.values())).property("busy")
    assert "Select a project" in page.status.text()


def test_a_running_build_holds_off_opening(page):
    page.builder = object()  # stands in for the QProcess
    page._build = _Build(name="Seahawk", out_dir=Path("Seahawk"))

    page.open_project(PROJECTS[0])

    assert page.viewer is None
    assert not next(iter(page.cards.values())).property("busy")
    assert "Seahawk" in page.status.text()
    page.builder = None


def test_build_settings_come_from_the_dialog(app, tmp_path):
    model = tmp_path / "Seahawk.obj"
    model.write_text("")
    dialog = BuildBundleDialog(model)
    dialog.name.setText("Sea Hawk")
    dialog.length.setValue(19.76)
    dialog.up.setCurrentText("z")
    dialog.targets.setValue(12000)
    dialog.viewpoints.setValue(48)

    settings = dialog.settings()

    assert settings["name"] == "Sea Hawk"
    assert settings["out_dir"] == tmp_path  # beside the model, by default
    assert settings["length"] == 19.76
    assert settings["up"] == "z"
    assert (settings["targets"], settings["viewpoints"]) == (12000, 48)
    dialog.deleteLater()


# -----------------------------------------------------------------------------
# Browsing for the bundle directory
# -----------------------------------------------------------------------------


def test_browsing_for_an_out_dir_replaces_what_was_there(app, tmp_path, monkeypatch):
    model = tmp_path / "Seahawk.obj"
    model.write_text("")
    dialog = BuildBundleDialog(model)
    chosen = tmp_path / "bundles"

    monkeypatch.setattr(
        build_bundle_dialog.QFileDialog, "getExistingDirectory", lambda *args, **kwargs: str(chosen)
    )
    dialog._choose_out_dir()

    assert dialog.settings()["out_dir"] == chosen


def test_cancelling_the_browse_leaves_the_default_out_dir_alone(app, tmp_path, monkeypatch):
    """QFileDialog hands back an empty string when the user backs out."""
    model = tmp_path / "Seahawk.obj"
    model.write_text("")
    dialog = BuildBundleDialog(model)
    before = dialog.out_dir.text()

    monkeypatch.setattr(
        build_bundle_dialog.QFileDialog, "getExistingDirectory", lambda *args, **kwargs: ""
    )
    dialog._choose_out_dir()

    assert dialog.out_dir.text() == before


# -----------------------------------------------------------------------------
# The cards themselves
# -----------------------------------------------------------------------------


def test_clicking_a_card_with_the_left_button_opens_it(app):
    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QMouseEvent

    card = ProjectCard(PROJECTS[0])
    card.resize(200, 60)
    picked = []
    card.clicked.connect(picked.append)

    card.mouseReleaseEvent(
        QMouseEvent(
            QMouseEvent.Type.MouseButtonRelease,
            QPointF(10, 10),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
    )

    assert picked == [PROJECTS[0]]


def test_releasing_the_button_outside_the_card_does_not_open_it(app):
    """Dragging off a card and letting go is not a click."""
    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QMouseEvent

    card = ProjectCard(PROJECTS[0])
    card.resize(200, 60)
    picked = []
    card.clicked.connect(picked.append)

    card.mouseReleaseEvent(
        QMouseEvent(
            QMouseEvent.Type.MouseButtonRelease,
            QPointF(500, 500),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
    )

    assert picked == []


def test_the_right_button_does_not_open_a_card(app):
    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QMouseEvent

    card = ProjectCard(PROJECTS[0])
    card.resize(200, 60)
    picked = []
    card.clicked.connect(picked.append)

    card.mouseReleaseEvent(
        QMouseEvent(
            QMouseEvent.Type.MouseButtonRelease,
            QPointF(10, 10),
            Qt.MouseButton.RightButton,
            Qt.MouseButton.RightButton,
            Qt.KeyboardModifier.NoModifier,
        )
    )

    assert picked == []


@pytest.mark.parametrize("key", [Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space])
def test_a_card_can_be_opened_from_the_keyboard(app, key):
    from PySide6.QtGui import QKeyEvent

    card = ProjectCard(PROJECTS[0])
    picked = []
    card.clicked.connect(picked.append)

    card.keyPressEvent(QKeyEvent(QKeyEvent.Type.KeyPress, key, Qt.KeyboardModifier.NoModifier))

    assert picked == [PROJECTS[0]]


def test_other_keys_do_not_open_a_card(app):
    from PySide6.QtGui import QKeyEvent

    card = ProjectCard(PROJECTS[0])
    picked = []
    card.clicked.connect(picked.append)

    card.keyPressEvent(
        QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_A, Qt.KeyboardModifier.NoModifier)
    )

    assert picked == []


def test_eliding_a_subtitle_does_not_elide_it_again(app):
    """Setting the text lays the card out again, which lands back in resizeEvent."""
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QResizeEvent

    card = ProjectCard(PROJECTS[0])
    card._eliding = True
    before = card.subtitle.text()

    card.resizeEvent(QResizeEvent(QSize(40, 60), QSize(200, 60)))

    assert card.subtitle.text() == before


# -----------------------------------------------------------------------------
# Choosing folders and models
# -----------------------------------------------------------------------------


def test_choosing_a_folder_adds_the_bundle_in_it(page, tmp_path, monkeypatch, bundle):
    monkeypatch.setattr(startup.QFileDialog, "getExistingDirectory", lambda *a, **k: str(bundle))

    page.choose_project()

    assert str(bundle) in page.cards


def test_backing_out_of_the_folder_chooser_adds_nothing(page, monkeypatch):
    monkeypatch.setattr(startup.QFileDialog, "getExistingDirectory", lambda *a, **k: "")
    before = dict(page.cards)

    page.choose_project()

    assert page.cards == before


def test_a_folder_that_cannot_be_read_is_explained(page, tmp_path, monkeypatch):
    def refuse(_path):
        raise OSError(13, "Permission denied")

    monkeypatch.setattr(startup, "validate_required_files", refuse)

    assert page.add_folder(tmp_path / "locked") is False
    assert "Permission denied" in page.status.text()


def test_choosing_a_model_builds_from_it(page, tmp_path, monkeypatch):
    model = tmp_path / "model.obj"
    model.write_text("")
    built = []

    monkeypatch.setattr(startup.QFileDialog, "getOpenFileName", lambda *a, **k: (str(model), ""))
    monkeypatch.setattr(
        startup, "BuildBundleDialog", _dialog_returning(True, {"name": "m", "out_dir": tmp_path})
    )
    monkeypatch.setattr(page, "build_bundle", lambda m, s: built.append((m, s)))

    page.choose_model()

    assert built == [(model, {"name": "m", "out_dir": tmp_path})]


def test_backing_out_of_the_model_chooser_builds_nothing(page, monkeypatch):
    built = []
    monkeypatch.setattr(startup.QFileDialog, "getOpenFileName", lambda *a, **k: ("", ""))
    monkeypatch.setattr(page, "build_bundle", lambda m, s: built.append(m))

    page.choose_model()

    assert built == []


def test_backing_out_of_the_build_dialog_builds_nothing(page, tmp_path, monkeypatch):
    model = tmp_path / "model.obj"
    model.write_text("")
    built = []

    monkeypatch.setattr(startup.QFileDialog, "getOpenFileName", lambda *a, **k: (str(model), ""))
    monkeypatch.setattr(startup, "BuildBundleDialog", _dialog_returning(False, {}))
    monkeypatch.setattr(page, "build_bundle", lambda m, s: built.append(m))

    page.choose_model()

    assert built == []


def test_a_second_build_is_refused_while_one_is_running(page, monkeypatch):
    page.builder = object()

    page.choose_model()

    assert "already running" in page.status.text()
    page.builder = None


def _dialog_returning(accepted, settings):
    from PySide6.QtWidgets import QDialog

    class Stub:
        def __init__(self, *args, **kwargs):
            pass

        def exec(self):
            return QDialog.DialogCode.Accepted if accepted else QDialog.DialogCode.Rejected

        def settings(self):
            return settings

    return Stub


# -----------------------------------------------------------------------------
# Building a bundle, in a process of its own
# -----------------------------------------------------------------------------


class FakeProcess:
    """Stands in for QProcess, so no builder is ever actually run."""

    last: FakeProcess | None = None
    ProcessChannelMode = type("ProcessChannelMode", (), {"MergedChannels": 0})

    def __init__(self, _parent=None):
        self.program = None
        self.arguments = []
        self.started = False
        self.killed = False
        self.deleted = False
        self.output = b""
        self.error = "boom"
        self.readyReadStandardOutput = _Hook()
        self.finished = _Hook()
        self.errorOccurred = _Hook()
        FakeProcess.last = self

    def setProgram(self, program):
        self.program = program

    def setArguments(self, arguments):
        self.arguments = list(arguments)

    def setProcessChannelMode(self, _mode):
        pass

    def start(self):
        self.started = True

    def kill(self):
        self.killed = True

    def waitForFinished(self, _ms):
        return True

    def deleteLater(self):
        self.deleted = True

    def errorString(self):
        return self.error

    def readAllStandardOutput(self):
        from PySide6.QtCore import QByteArray

        return QByteArray(self.output)


class _Hook:
    """The bit of a Qt signal that startup.py uses: connect."""

    def __init__(self):
        self.slots = []

    def connect(self, slot):
        self.slots.append(slot)


def last_process() -> FakeProcess:
    """The process the page started, which every caller here has just made."""
    assert FakeProcess.last is not None
    return FakeProcess.last


@pytest.fixture
def builder(page, monkeypatch, tmp_path):
    """Start a build with the process faked out, and hand back the page."""
    monkeypatch.setattr(startup, "QProcess", FakeProcess)
    page.build_bundle(
        tmp_path / "model.obj",
        {
            "name": "Seahawk",
            "out_dir": tmp_path / "out",
            "length": 20.0,
            "up": "y",
            "targets": 12000,
            "viewpoints": 48,
        },
    )
    return page


def test_building_runs_the_builder_as_its_own_process(builder, tmp_path):
    """Its renderer wants a GL context, and the library allows one per process."""
    process = last_process()

    assert process.started
    assert process.program == startup.sys.executable
    assert "viewscope.build_bundle" in process.arguments
    assert str(tmp_path / "out") in process.arguments


def test_the_build_settings_are_passed_on_the_command_line(builder, tmp_path):
    arguments = last_process().arguments

    assert arguments[arguments.index("--length") + 1] == "20.0"
    assert arguments[arguments.index("--up") + 1] == "y"
    assert arguments[arguments.index("--targets") + 1] == "12000"
    assert arguments[arguments.index("--viewpoints") + 1] == "48"


def test_the_builder_is_told_not_to_buffer_its_output(builder):
    """Otherwise the stage lines would all arrive at the end."""
    assert "-u" in last_process().arguments


def test_a_running_build_takes_the_buttons_and_shows_the_bar(builder):
    assert not builder.build_button.isEnabled()
    assert not builder.add_button.isEnabled()
    assert builder.cancel_button.isVisible() or not builder.isVisible()
    assert "Building Seahawk" in builder.status.text()


def test_an_out_dir_that_cannot_be_made_is_explained(page, monkeypatch, tmp_path):
    def refuse(*_args, **_kwargs):
        raise OSError(13, "Permission denied")

    monkeypatch.setattr(startup.Path, "mkdir", refuse)

    page.build_bundle(tmp_path / "model.obj", {"name": "x", "out_dir": tmp_path / "out"})

    assert "Cannot write to" in page.status.text()
    assert page.builder is None


# -----------------------------------------------------------------------------
# Following the build
# -----------------------------------------------------------------------------


def test_the_stage_lines_move_the_bar(builder):
    last_process().output = b"[3/6] planning 120 viewpoints\n"

    builder._on_build_output()

    assert builder.bar.maximum() == 6
    assert builder.bar.value() == 3
    assert "Seahawk: planning 120 viewpoints" in builder.status.text()


def test_lines_that_are_not_stages_are_only_logged(builder):
    last_process().output = b"      12345 faces\n\n"

    builder._on_build_output()

    assert builder._build.log == ["      12345 faces"]
    assert "Building Seahawk" in builder.status.text()


def test_output_arriving_after_the_build_is_over_is_ignored(page):
    page.builder = None
    page._build = None

    page._on_build_output()  # must not raise


def test_a_builder_that_will_not_run_is_reported(builder):
    last_process().error = "No such file or directory"

    builder._on_build_error(None)

    assert "Could not run the builder" in builder.status.text()
    assert builder.builder is None


def test_a_build_error_with_no_process_left_still_reports(page):
    page.builder = None

    page._on_build_error(None)

    assert "unknown error" in page.status.text()


def test_cancelling_kills_the_builder(builder):
    process = last_process()

    builder.cancel_build()

    assert process.killed
    assert builder.status.text() == "Build cancelled."


def test_cancelling_with_no_build_running_is_harmless(page):
    page.builder = None

    page.cancel_build()

    assert page.builder is None


def test_a_finished_build_is_added_to_the_list(builder, bundle, monkeypatch):
    builder._build = startup._Build(name="Seahawk", out_dir=bundle)

    builder._on_build_finished(0, None)

    assert str(bundle) in builder.cards
    assert "Built Seahawk" in builder.status.text()
    assert builder.builder is None


def test_a_build_that_wrote_an_unusable_bundle_says_so(builder, tmp_path):
    """It finished, but what it left behind is not a bundle."""
    empty = tmp_path / "empty"
    empty.mkdir()
    builder._build = startup._Build(name="Seahawk", out_dir=empty)

    builder._on_build_finished(0, None)

    assert str(empty) not in builder.cards
    assert "Built Seahawk" not in builder.status.text()


def test_a_failed_build_reports_the_last_thing_it_printed(builder):
    builder._build.log.extend(["[1/6] reading", "MemoryError: out of memory"])

    builder._on_build_finished(1, None)

    assert "Build failed: MemoryError: out of memory" in builder.status.text()


def test_a_failed_build_that_printed_nothing_still_reports(builder):
    builder._on_build_finished(1, None)

    assert "Build failed: no output" in builder.status.text()


def test_a_cancelled_build_keeps_saying_it_was_cancelled(builder):
    builder.cancel_build()

    builder._on_build_finished(1, None)

    assert builder.status.text() == "Build cancelled."


def test_a_finish_with_nothing_being_built_is_ignored(page):
    page._build = None

    page._on_build_finished(0, None)  # must not raise


def test_finishing_gives_the_buttons_back_and_hides_the_bar(builder):
    process = last_process()

    builder._finish_build("all done")

    assert process.deleted
    assert builder.builder is None
    assert builder.build_button.isEnabled()
    assert builder.add_button.isEnabled()
    assert builder.bar.maximum() == STAGE_COUNT
    assert builder.status.text() == "all done"


def test_finishing_without_a_message_leaves_the_status_alone(builder):
    builder.status.setText("something already said")

    builder._finish_build("")

    assert builder.status.text() == "something already said"


# -----------------------------------------------------------------------------
# Handing over to the viewer
# -----------------------------------------------------------------------------


class FakeViewer:
    """Stands in for MainWindow, which cannot be built without a GL context."""

    last: FakeViewer | None = None

    def __init__(self, data_dir, **kwargs):
        self.data_dir = data_dir
        self.kwargs = kwargs
        self.shown = False
        self.started = False
        self.closed = False
        self.deleted = False
        self.visible = False

        self.back_requested = _Hook()
        self.photo_mesh_progress = _Hook()
        self.photo_mesh_finished = _Hook()
        self.loader = _FakeLoader()
        FakeViewer.last = self

    def show(self):
        self.shown = True
        self.visible = True

    def raise_(self):
        pass

    def activateWindow(self):
        pass

    def start(self):
        self.started = True

    def close(self):
        self.closed = True

    def deleteLater(self):
        self.deleted = True

    def isVisible(self):
        return self.visible


class _FakeLoader:
    def __init__(self):
        self.progress = _Hook()
        self.stage = _Hook()
        self.failed = _Hook()
        self.loaded = _Hook()
        self.started = False

    def start(self):
        self.started = True


def last_viewer() -> FakeViewer:
    """The viewer the page built, which every caller here has just opened."""
    assert FakeViewer.last is not None
    return FakeViewer.last


@pytest.fixture
def viewer(page, monkeypatch):
    """Open a project with the viewer faked out."""
    monkeypatch.setattr(startup.wd, "MainWindow", FakeViewer)
    page.open_project(PROJECTS[0])
    page._start_pending_load()
    return page


def test_opening_a_project_builds_the_viewer_for_its_bundle(viewer):
    assert last_viewer().data_dir == PROJECTS[0].data_dir
    assert last_viewer().kwargs["defer_load"] is True
    assert last_viewer().loader.started


def test_the_viewer_is_told_which_budget_was_chosen(page, monkeypatch):
    monkeypatch.setattr(startup.wd, "MainWindow", FakeViewer)
    page.quality_buttons[QUALITY_LOW].click()

    page.open_project(PROJECTS[0])
    page._start_pending_load()

    assert last_viewer().kwargs["load_photo_mesh"] is False


def test_nothing_starts_when_the_open_was_called_off(page, monkeypatch):
    """Closing the page mid-open clears what was pending."""
    monkeypatch.setattr(startup.wd, "MainWindow", FakeViewer)
    FakeViewer.last = None
    page._pending_project = None

    page._start_pending_load()

    assert FakeViewer.last is None


def test_a_second_project_is_refused_while_one_is_opening(viewer):
    already = last_viewer()

    viewer.open_project(PROJECTS[0])

    assert last_viewer() is already


def test_the_full_resolution_phase_moves_the_bar(viewer):
    viewer._on_scene_loaded()  # switches the bar to percentages for this phase

    viewer._on_photo_mesh_progress("Decoding textures (2/4)...", 50)

    assert viewer.status.text() == "Decoding textures (2/4)..."
    assert viewer.bar.value() == 50


def test_the_viewer_comes_up_once_the_model_is_in(viewer):
    viewer._on_photo_mesh_finished(True)

    window = last_viewer()
    assert window.shown and window.started
    assert viewer.status.text() == "Ready"
    assert viewer.bar.value() == viewer.bar.maximum()


def test_the_page_hides_only_after_the_viewer_is_up(viewer):
    """So the application is never without a window and never quits on its own."""
    viewer._on_photo_mesh_finished(True)

    assert last_viewer().shown
    assert viewer.isHidden()


def test_there_is_nothing_to_run_once_the_viewer_has_gone(page):
    page.viewer = None

    page._run_viewer(None)  # must not raise


def test_coming_back_closes_the_viewer_and_resets_the_page(viewer):
    window = last_viewer()

    viewer.show_projects()

    assert window.closed and window.deleted
    assert viewer.viewer is None
    assert "Select a project to open it." in viewer.status.text()


def test_a_failed_load_closes_the_viewer_and_offers_another_go(viewer):
    window = last_viewer()

    viewer._on_failed("scene: no such file")

    assert window.closed and window.deleted
    assert viewer.viewer is None
    assert "try again" in viewer.status.text()


# -----------------------------------------------------------------------------
# Taking projects off the list
# -----------------------------------------------------------------------------


def test_removing_a_project_that_is_not_on_the_list_does_nothing(page):
    page.remove_project(Project(name="ghost", subtitle="", data_dir=Path("/nowhere")))

    assert list(page.cards) == ["data/kiri"]


def test_right_clicking_a_card_offers_to_remove_it(page, tmp_path, bundle, monkeypatch):
    page.add_folder(bundle)
    chosen = []

    class Menu:
        def __init__(self, _parent=None):
            self.action = None

        def addAction(self, text):
            chosen.append(text)
            return _Action()

        def exec(self, _point):
            return None

    class _Action:
        def __init__(self):
            self.triggered = _Hook()

    monkeypatch.setattr(startup, "QMenu", Menu)

    page._offer_removal(page.projects[-1], startup.Qt and _origin())

    assert chosen == ["Remove from the list"]


def _origin():
    from PySide6.QtCore import QPoint

    return QPoint(0, 0)


# -----------------------------------------------------------------------------
# The saved project list
# -----------------------------------------------------------------------------


def test_a_saved_list_that_will_not_parse_is_ignored(app, settings):
    settings.setValue("projects", "{ not json")

    window = StartupWindow(PROJECTS, settings=settings)

    assert list(window.cards) == ["data/kiri"]
    window.close()


def test_a_saved_list_that_is_not_a_list_is_ignored(app, settings):
    settings.setValue("projects", json.dumps({"projects": []}))

    window = StartupWindow(PROJECTS, settings=settings)

    assert list(window.cards) == ["data/kiri"]
    window.close()


def test_a_saved_entry_that_no_longer_reads_is_skipped(app, settings, bundle):
    """An entry written by an older version may be missing fields."""
    settings.setValue(
        "projects",
        json.dumps([{"nonsense": True}, {"name": "ok", "subtitle": "s", "data_dir": str(bundle)}]),
    )

    window = StartupWindow(PROJECTS, settings=settings)

    assert str(bundle) in window.cards
    window.close()


# -----------------------------------------------------------------------------
# Closing the page
# -----------------------------------------------------------------------------


def test_closing_calls_off_an_open_that_had_not_started(page):
    page._pending_project = PROJECTS[0]

    page.close()

    assert page._pending_project is None


def test_closing_stops_a_running_build(builder):
    process = last_process()

    builder.close()

    assert process.killed


def test_closing_mid_load_lets_the_viewer_shut_its_loader_down(viewer):
    window = last_viewer()
    window.visible = False

    viewer.close()

    assert window.closed
    assert viewer.viewer is None


def test_closing_with_the_viewer_already_up_leaves_it_alone(viewer):
    window = last_viewer()
    window.visible = True

    viewer.close()

    assert not window.closed
