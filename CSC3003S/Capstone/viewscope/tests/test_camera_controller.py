"""Unit tests for src/viewscope/camera/controller.py.

The controller moves a real vtkCamera on a real vtkRenderer; neither needs a
window. What it reads the plan out of is the global store, so these load one.
"""

import numpy as np
import pytest
import vtk

from viewscope.camera.controller import CameraController


@pytest.fixture
def controller():
    renderer = vtk.vtkRenderer()
    return CameraController(renderer, yfov_deg=53.13)


@pytest.fixture
def loaded(store, make_scene):
    store.set_scene(make_scene(positions=((0.0, 0.0, 12.0), (12.0, 0.0, 6.0), (0.0, 12.0, 6.0))))
    return store


# -----------------------------------------------------------------------------
# How many cameras there are
# -----------------------------------------------------------------------------


def test_with_no_scene_there_are_no_cameras(store, controller):
    assert controller.count == 0


def test_the_count_follows_the_loaded_plan(loaded, controller):
    assert controller.count == 3


# -----------------------------------------------------------------------------
# Jumping to a viewpoint
# -----------------------------------------------------------------------------


def test_jumping_to_a_viewpoint_moves_the_camera_there(loaded, controller):
    info = controller.show(1)

    assert info is not None
    assert info.index == 1
    assert info.position == pytest.approx([12.0, 0.0, 6.0])
    assert controller.renderer.GetActiveCamera().GetPosition() == pytest.approx([12.0, 0.0, 6.0])


def test_the_viewpoint_carries_its_own_angles(loaded, controller):
    info = controller.show(0)

    assert info is not None
    assert info.yaw == pytest.approx(0.0)
    assert info.pitch == pytest.approx(-45.0)


def test_an_index_past_the_end_wraps_round_to_the_start(loaded, controller):
    info = controller.show(3)

    assert info is not None
    assert info.index == 0


def test_a_negative_index_wraps_round_to_the_end(loaded, controller):
    info = controller.show(-1)

    assert info is not None
    assert info.index == 2


def test_jumping_with_no_scene_does_nothing(store, controller):
    assert controller.show(0) is None
    assert controller.index is None


def test_jumping_when_the_scene_went_away_under_the_count(controller, monkeypatch):
    """A guard, not a state the store can reach on its own: the count is read
    off the scene, so it answers zero the moment there is no scene."""

    class Emptied:
        camera_count = 3
        scene = None

    monkeypatch.setattr("viewscope.camera.controller.SCENE_STORE", Emptied())

    assert controller.show(0) is None


def test_jumping_with_a_plan_of_no_cameras(store, make_scene, controller):
    """camera_count is zero, so there is nowhere to jump to."""
    store.set_scene(make_scene(positions=np.zeros((0, 3))))

    assert controller.show(0) is None


# -----------------------------------------------------------------------------
# The overview, and getting back to it
# -----------------------------------------------------------------------------


def test_the_first_jump_away_remembers_where_the_free_look_camera_was(loaded, controller):
    cam = controller.renderer.GetActiveCamera()
    cam.SetPosition(3.0, 4.0, 5.0)
    cam.SetFocalPoint(0.0, 0.0, 0.0)

    controller.show(0)
    controller.show_overview()

    assert cam.GetPosition() == pytest.approx([3.0, 4.0, 5.0])
    assert controller.index is None


def test_a_later_jump_does_not_overwrite_the_remembered_overview(loaded, controller):
    """Only the move out of free-look is a snapshot; the rest are not."""
    cam = controller.renderer.GetActiveCamera()
    cam.SetPosition(3.0, 4.0, 5.0)

    controller.show(0)
    controller.show(1)
    controller.show_overview()

    assert cam.GetPosition() == pytest.approx([3.0, 4.0, 5.0])


def test_asking_for_the_overview_first_snapshots_rather_than_jumping(controller):
    """There is nothing remembered yet, so where the camera is becomes it."""
    cam = controller.renderer.GetActiveCamera()
    cam.SetPosition(7.0, 8.0, 9.0)

    controller.show_overview()

    assert cam.GetPosition() == pytest.approx([7.0, 8.0, 9.0])
    assert controller.index is None


def test_the_overview_restores_the_focal_point_and_the_view_angle(loaded, controller):
    cam = controller.renderer.GetActiveCamera()
    cam.SetPosition(3.0, 4.0, 5.0)
    cam.SetFocalPoint(1.0, 1.0, 1.0)
    cam.SetViewUp(0.0, 0.0, 1.0)
    cam.SetViewAngle(41.0)

    controller.show(0)
    controller.show_overview()

    assert cam.GetFocalPoint() == pytest.approx([1.0, 1.0, 1.0])
    assert cam.GetViewUp() == pytest.approx([0.0, 0.0, 1.0])
    assert cam.GetViewAngle() == pytest.approx(41.0)


# -----------------------------------------------------------------------------
# Stepping
# -----------------------------------------------------------------------------


def test_stepping_forward_from_free_look_starts_at_the_first_viewpoint(loaded, controller):
    info = controller.step(1)

    assert info is not None
    assert info.index == 0


def test_stepping_back_from_free_look_starts_at_the_last(loaded, controller):
    info = controller.step(-1)

    assert info is not None
    assert info.index == 2


def test_stepping_moves_relative_to_where_it_already_is(loaded, controller):
    controller.show(1)

    info = controller.step(1)

    assert info is not None
    assert info.index == 2


def test_stepping_past_the_end_wraps(loaded, controller):
    controller.show(2)

    info = controller.step(1)

    assert info is not None
    assert info.index == 0


def test_stepping_with_no_scene_does_nothing(store, controller):
    assert controller.step(1) is None
