"""Unit tests for src/viewscope/panels/viewpoints_panel.py.

The panel end of adding a camera: the button now asks how, rather than going
straight to the dialog it always used. What happens after the clicks is the
viewport's, and is exercised against a real render window instead.
"""

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

import viewscope_core as vc
from viewscope.panels import ViewpointsPanel


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def panel(app):
    return ViewpointsPanel()


# -----------------------------------------------------------------------------
# The button asks how
# -----------------------------------------------------------------------------


def test_the_button_offers_both_ways_of_saying_where(panel):
    assert [action.text() for action in panel.menu.actions()] == [
        "Enter co-ordinates...",
        "Place in the view",
    ]


def test_the_button_opens_the_menu_rather_than_a_dialog(panel):
    """Clicking it must not go straight to the one it always used to."""
    assert panel.button.menu() is panel.menu


def test_placing_in_the_view_is_asked_for_and_not_done_here(panel):
    """The panel has no viewport; all it can do is say that this is wanted."""
    asked = []
    panel.place_requested.connect(lambda: asked.append(True))

    panel.place_action.trigger()

    assert asked == [True]


def test_entering_co_ordinates_does_nothing_without_a_scene(panel, monkeypatch):
    """No scene, no dialog: there is nothing for a camera to be added to."""

    class NoScene:
        scene = None

    monkeypatch.setattr("viewscope.panels.viewpoints_panel.SCENE_STORE", NoScene())
    monkeypatch.setattr(
        "viewscope.panels.viewpoints_panel.AddCameraDialog",
        lambda parent: pytest.fail("a dialog was opened with no scene to add to"),
    )

    panel._on_button_add_camera_clicked()


# -----------------------------------------------------------------------------
# What the two clicks are turned into
# -----------------------------------------------------------------------------


def test_a_camera_faces_the_point_it_was_aimed_at():
    """The angles the viewport hands over are the ones that look at click two."""
    standpoint = np.array([10.0, 0.0, 5.0])
    target = np.array([0.0, 0.0, 0.0])

    yaw, pitch = vc.look_at_angles(standpoint, target)

    assert yaw == pytest.approx(180.0)
    assert pitch < 0.0, "looking down at something below it"


def test_standing_off_the_surface_is_what_keeps_a_camera_out_of_the_model():
    """The first click is a point on the model; the camera goes out along it."""
    surface = np.array([1.0, 2.0, 3.0])
    outward = np.array([0.0, 0.0, 1.0])

    standpoint = surface + outward * vc.constants.MU_RHO_M

    assert np.linalg.norm(standpoint - surface) == pytest.approx(vc.constants.MU_RHO_M)
    assert vc.look_at_angles(standpoint, surface)[1] == pytest.approx(-90.0)


# -----------------------------------------------------------------------------
# The table
# -----------------------------------------------------------------------------


@pytest.fixture
def loaded(store, make_scene, panel):
    """A scene in the store, with the panel already showing it."""
    store.set_scene(make_scene(positions=((0.0, 0.0, 12.0), (12.5, -3.25, 6.0))))
    panel.refresh()
    return store


def row_of(panel, index):
    return [panel.table.item(index, col).text() for col in range(panel.table.columnCount())]


def test_the_table_holds_one_row_per_viewpoint(loaded, panel):
    assert panel.table.rowCount() == 2


def test_a_row_names_the_viewpoint_and_its_pose(loaded, panel):
    assert row_of(panel, 1) == ["vp001", "12.5, -3.2, 6.0", "0.0", "-45.0"]


def test_the_table_empties_when_the_scene_goes(loaded, panel, store):
    store.clear()

    panel.refresh()

    assert panel.table.rowCount() == 0


def test_the_table_follows_the_plan_without_being_asked(loaded, panel, store):
    """Adding a camera has to show up here; nothing calls refresh."""
    store.add_camera((1.0, 2.0, 3.0), 10.0, -20.0)

    assert panel.table.rowCount() == 3
    assert row_of(panel, 2)[0] == "vp2"


# -----------------------------------------------------------------------------
# Selecting
# -----------------------------------------------------------------------------


def test_picking_a_row_says_which_camera_it_is(loaded, panel):
    picked = []
    panel.camera_picked.connect(picked.append)

    panel.table.selectRow(1)

    assert picked == [1]


def test_picking_a_row_lets_it_be_duplicated(loaded, panel):
    assert not panel.duplicate_camera_button.isEnabled()

    panel.table.selectRow(0)

    assert panel.duplicate_camera_button.isEnabled()


def test_a_selection_made_elsewhere_is_reflected_without_being_echoed(loaded, panel):
    """Otherwise the viewport and the table would drive each other in circles."""
    picked = []
    panel.camera_picked.connect(picked.append)

    panel.select_row(1)

    assert picked == []
    assert [i.row() for i in panel.table.selectionModel().selectedRows()] == [1]
    assert panel.duplicate_camera_button.isEnabled()


def test_clearing_the_selection_from_elsewhere_disables_duplicating(loaded, panel):
    panel.select_row(1)

    panel.select_row(None)

    assert panel.table.selectionModel().selectedRows() == []
    assert not panel.duplicate_camera_button.isEnabled()


# -----------------------------------------------------------------------------
# Adding and duplicating
# -----------------------------------------------------------------------------


@pytest.fixture
def dialog(monkeypatch):
    """Stand in for AddCameraDialog, which would otherwise block on exec()."""
    from PySide6.QtWidgets import QDialog

    # Defined per test, so the recorded arguments start out empty each time.
    class Stub:
        accepted = True
        answer = (1.0, 2.0, 3.0, 45.0, -30.0)
        #: What the panel asked the dialog to open on.
        opened: dict = {}

        def __init__(self, **kwargs):
            Stub.opened.update(kwargs)

        def exec(self):
            return QDialog.DialogCode.Accepted if Stub.accepted else QDialog.DialogCode.Rejected

        def values(self):
            return Stub.answer

    monkeypatch.setattr("viewscope.panels.viewpoints_panel.AddCameraDialog", Stub)
    return Stub


def test_typing_co_ordinates_adds_the_camera(loaded, panel, store, dialog):
    panel.enter_action.trigger()

    assert store.camera_count == 3
    assert store.scene.plan.positions[-1] == pytest.approx([1.0, 2.0, 3.0])
    assert store.scene.plan.yaws_deg[-1] == 45.0


def test_backing_out_of_the_dialog_adds_nothing(loaded, panel, store, dialog):
    dialog.accepted = False

    panel.enter_action.trigger()

    assert store.camera_count == 2


def test_duplicating_opens_on_the_selected_cameras_pose(loaded, panel, store, dialog):
    panel.table.selectRow(1)

    panel.duplicate_camera_button.click()

    assert dialog.opened["position"] == pytest.approx((12.5, -3.25, 6.0))
    assert dialog.opened["yaw"] == pytest.approx(0.0)
    assert dialog.opened["pitch"] == pytest.approx(-45.0)


def test_duplicating_adds_the_camera_the_dialog_came_back_with(loaded, panel, store, dialog):
    panel.table.selectRow(0)

    panel.duplicate_camera_button.click()

    assert store.camera_count == 3
    assert store.scene.plan.positions[-1] == pytest.approx([1.0, 2.0, 3.0])


def test_backing_out_of_the_duplicate_dialog_adds_nothing(loaded, panel, store, dialog):
    dialog.accepted = False
    panel.table.selectRow(0)

    panel.duplicate_camera_button.click()

    assert store.camera_count == 2


def test_neither_button_does_anything_without_a_scene(panel, store, dialog):
    panel._on_button_add_camera_clicked()
    panel._on_button_duplicate_camera_clicked()

    assert store.scene is None


def test_clearing_the_selection_in_the_table_picks_no_camera(loaded, panel):
    """Deselecting is not a pick, so nothing is jumped to."""
    panel.table.selectRow(0)
    picked = []
    panel.camera_picked.connect(picked.append)

    panel.table.clearSelection()

    assert picked == []
    assert not panel.duplicate_camera_button.isEnabled()
