"""Unit tests for src/viewscope/scene/camera.py.

The free-look camera, driven against a real vtkCamera on a real vtkRenderer.
Neither needs a window, so the pose can be read straight back off the camera
after every move.
"""

import math

import numpy as np
import pytest
import vtk

from viewscope.scene.camera import CameraMode, CameraOrbitState, SceneCameraController


@pytest.fixture
def renderer():
    scene = vtk.vtkRenderer()
    cam = scene.GetActiveCamera()
    # Standing 10 m out along -Y, level with the pivot, looking at the origin.
    cam.SetFocalPoint(0.0, 0.0, 0.0)
    cam.SetPosition(0.0, -10.0, 0.0)
    cam.SetViewUp(0.0, 0.0, 1.0)
    cam.SetViewAngle(45.0)
    return scene


@pytest.fixture
def controller(renderer):
    return SceneCameraController(renderer, yfov_deg=45.0)


def camera_of(controller):
    return controller.renderer.GetActiveCamera()


# -----------------------------------------------------------------------------
# The modes
# -----------------------------------------------------------------------------


def test_the_two_camera_modes_are_distinct():
    assert CameraMode.LOOK_AT is not CameraMode.TRACKBALL


# -----------------------------------------------------------------------------
# The orbit state itself
# -----------------------------------------------------------------------------


def test_a_level_state_stands_the_distance_it_says_from_its_pivot():
    state = CameraOrbitState(
        pivot=(0.0, 0.0, 0.0), distance=10.0, yaw=0.0, pitch=0.0, view_angle=45.0
    )

    assert np.linalg.norm(state.camera_position()) == pytest.approx(10.0)


def test_the_pose_and_the_position_agree():
    state = CameraOrbitState(
        pivot=(1.0, 2.0, 3.0), distance=7.0, yaw=0.4, pitch=-0.2, view_angle=45.0
    )

    assert state.camera_position() == pytest.approx(state.pose()[:3, 3])


def test_the_up_axis_is_the_poses_own_and_stays_unit_length():
    state = CameraOrbitState(
        pivot=(0.0, 0.0, 0.0), distance=10.0, yaw=0.3, pitch=0.2, view_angle=45.0
    )

    up = np.array(state.camera_up())

    assert np.linalg.norm(up) == pytest.approx(1.0)
    assert up == pytest.approx(state.pose()[:3, 1])


def test_a_state_moved_about_keeps_its_pivot():
    """Nothing in the renderer may perturb it as a side effect."""
    state = CameraOrbitState(
        pivot=(5.0, 6.0, 7.0), distance=3.0, yaw=0.0, pitch=0.0, view_angle=45.0
    )

    assert state.pivot == (5.0, 6.0, 7.0)


# -----------------------------------------------------------------------------
# Adopting whatever pose the camera is in
# -----------------------------------------------------------------------------


def test_syncing_reads_the_pivot_and_distance_off_the_camera(controller):
    controller.sync_from_camera()

    assert controller._orbit.pivot == pytest.approx([0.0, 0.0, 0.0])
    assert controller._orbit.distance == pytest.approx(10.0)
    assert controller._orbit.view_angle == pytest.approx(45.0)


def test_syncing_recovers_the_pitch_the_camera_was_at(controller, renderer):
    renderer.GetActiveCamera().SetPosition(0.0, -10.0, 10.0)

    controller.sync_from_camera()

    assert controller._orbit.pitch == pytest.approx(math.radians(45.0))


def test_a_camera_sitting_on_its_pivot_is_held_off_it(controller, renderer):
    """Zero distance would divide the direction by nothing."""
    renderer.GetActiveCamera().SetPosition(0.0, 0.0, 0.0)

    controller.sync_from_camera()

    assert controller._orbit.distance == pytest.approx(controller.MIN_DISTANCE)


def test_the_pitch_is_never_taken_all_the_way_to_the_pole(controller, renderer):
    """At the pole VTK's camera basis goes singular and pan starts returning NaN."""
    renderer.GetActiveCamera().SetPosition(0.0, 0.0, 10.0)
    renderer.GetActiveCamera().SetViewUp(0.0, 1.0, 0.0)

    controller.sync_from_camera()

    assert controller._orbit.pitch == pytest.approx(controller.PITCH_LIMIT)


def test_near_the_pole_the_yaw_is_recovered_from_the_up_vector(controller, renderer):
    """Straight overhead the horizontal offset is noise, not a direction."""
    cam = renderer.GetActiveCamera()
    cam.SetPosition(0.0, 0.0, 10.0)
    cam.SetViewUp(0.0, -1.0, 0.0)

    controller.sync_from_camera()

    # up = -Y with the camera overhead reads as facing the other way round.
    assert abs(controller._orbit.yaw) == pytest.approx(math.pi)


def test_away_from_the_pole_the_yaw_comes_off_the_offset(controller, renderer):
    renderer.GetActiveCamera().SetPosition(10.0, 0.0, 0.0)

    controller.sync_from_camera()

    assert controller._orbit.yaw == pytest.approx(math.pi / 2.0)


# -----------------------------------------------------------------------------
# Orbiting, panning and dollying
# -----------------------------------------------------------------------------


def test_orbiting_turns_the_camera_about_its_pivot(controller):
    controller.sync_from_camera()
    before = controller._orbit.yaw

    controller.orbit(dx=100.0, dy=0.0)

    assert controller._orbit.yaw == pytest.approx(before - 100.0 * controller.YAW_SENSITIVITY)
    assert controller._orbit.pivot == pytest.approx([0.0, 0.0, 0.0])


def test_orbiting_keeps_the_camera_the_same_distance_out(controller):
    controller.sync_from_camera()

    controller.orbit(dx=50.0, dy=30.0)

    position = np.array(camera_of(controller).GetPosition())
    assert np.linalg.norm(position) == pytest.approx(10.0)


def test_the_pitch_is_clamped_however_far_it_is_dragged(controller):
    controller.sync_from_camera()

    controller.orbit(dx=0.0, dy=100_000.0)

    assert controller._orbit.pitch == pytest.approx(controller.PITCH_LIMIT)


def test_the_pitch_is_clamped_the_other_way_too(controller):
    controller.sync_from_camera()

    controller.orbit(dx=0.0, dy=-100_000.0)

    assert controller._orbit.pitch == pytest.approx(-controller.PITCH_LIMIT)


def test_orbiting_adopts_the_current_pose_when_nothing_was_synced(controller):
    """The first use has to pick up wherever the camera already is."""
    assert controller._orbit is None

    controller.orbit(dx=10.0, dy=0.0)

    assert controller._orbit is not None


def test_panning_moves_the_pivot_without_turning_the_camera(controller):
    controller.sync_from_camera()
    before = controller._orbit.yaw, controller._orbit.pitch

    controller.pan(dx=50.0, dy=0.0)

    assert (controller._orbit.yaw, controller._orbit.pitch) == before
    assert controller._orbit.pivot != pytest.approx([0.0, 0.0, 0.0])


def test_panning_moves_further_the_further_out_the_camera_is(controller, renderer):
    controller.sync_from_camera()
    controller.pan(dx=50.0, dy=0.0)
    near = np.linalg.norm(controller._orbit.pivot)

    renderer.GetActiveCamera().SetPosition(0.0, -100.0, 0.0)
    controller.sync_from_camera()
    controller.pan(dx=50.0, dy=0.0)
    far = np.linalg.norm(np.array(controller._orbit.pivot))

    assert far > near


def test_panning_adopts_the_current_pose_when_nothing_was_synced(controller):
    controller.pan(dx=10.0, dy=10.0)

    assert controller._orbit is not None


def test_dollying_in_brings_the_camera_closer(controller):
    controller.sync_from_camera()

    controller.dolly(amount=100.0)

    assert controller._orbit.distance < 10.0


def test_dollying_out_takes_it_further_away(controller):
    controller.sync_from_camera()

    controller.dolly(amount=-100.0)

    assert controller._orbit.distance > 10.0


def test_dollying_never_takes_the_camera_onto_its_pivot(controller):
    controller.sync_from_camera()

    controller.dolly(amount=1e9)

    assert controller._orbit.distance == pytest.approx(controller.MIN_DISTANCE)


def test_dollying_adopts_the_current_pose_when_nothing_was_synced(controller):
    controller.dolly(amount=10.0)

    assert controller._orbit is not None


def test_the_near_plane_follows_the_camera_in_so_geometry_does_not_vanish(controller):
    controller.sync_from_camera()
    controller.dolly(amount=1e9)

    near, far = camera_of(controller).GetClippingRange()

    assert near == pytest.approx(1e-5)
    assert far > near


# -----------------------------------------------------------------------------
# Coming back from trackball
# -----------------------------------------------------------------------------


def test_beginning_the_transition_captures_where_the_camera_was(controller):
    start = controller.begin_transition_to_orbit()

    assert start[0] == pytest.approx([0.0, -10.0, 0.0])
    assert start[1] == pytest.approx([0.0, 0.0, 0.0])
    assert start[3] == pytest.approx(45.0)


def test_beginning_the_transition_projects_onto_the_nearest_look_at_pose(controller):
    """Roll is discarded; the position and the pivot are kept."""
    controller.renderer.GetActiveCamera().SetViewUp(0.3, 0.0, 1.0)

    controller.begin_transition_to_orbit()

    assert controller._orbit is not None
    assert controller._orbit.distance == pytest.approx(10.0)


def test_the_transition_does_not_move_the_camera_at_zero(controller):
    start = controller.begin_transition_to_orbit()

    controller.apply_transition(start, 0.0)

    assert camera_of(controller).GetPosition() == pytest.approx([0.0, -10.0, 0.0])


def test_the_transition_lands_on_the_target_at_one(controller):
    start = controller.begin_transition_to_orbit()

    controller.apply_transition(start, 1.0)

    target = controller._orbit.camera_position()
    assert camera_of(controller).GetPosition() == pytest.approx(target)


def test_the_transition_goes_part_way_in_between(controller):
    controller.renderer.GetActiveCamera().SetPosition(0.0, -20.0, 0.0)
    start = controller.begin_transition_to_orbit()
    controller._orbit = CameraOrbitState(
        pivot=(0.0, 0.0, 0.0), distance=10.0, yaw=0.0, pitch=0.0, view_angle=45.0
    )

    controller.apply_transition(start, 0.5)

    moved = np.array(camera_of(controller).GetPosition())
    assert 10.0 < np.linalg.norm(moved) < 20.0


def test_an_up_vector_that_cancels_out_is_passed_on_unnormalised(controller):
    """Halfway between opposite hints there is no direction left to normalise,
    so it is handed to the camera as it is rather than divided by nothing."""
    controller._orbit = CameraOrbitState(
        pivot=(0.0, 0.0, 0.0), distance=10.0, yaw=0.0, pitch=0.0, view_angle=45.0
    )
    target_up = np.array(controller._orbit.camera_up())
    start = (np.array([0.0, -10.0, 0.0]), np.zeros(3), -target_up, 45.0)

    controller.apply_transition(start, 0.5)

    # The position still lerps, which is what says the call went through.
    assert camera_of(controller).GetPosition() == pytest.approx(
        (np.array([0.0, -10.0, 0.0]) + np.array(controller._orbit.camera_position())) / 2.0
    )


def test_finishing_lands_exactly_on_the_projected_target(controller):
    start = controller.begin_transition_to_orbit()
    controller.apply_transition(start, 0.4)

    controller.finish_transition()

    assert camera_of(controller).GetPosition() == pytest.approx(controller._orbit.camera_position())


# -----------------------------------------------------------------------------
# The overview
# -----------------------------------------------------------------------------


def test_saving_the_overview_captures_the_current_pose(controller):
    controller.save_overview()

    assert controller._orbit is not None
    assert controller._orbit.distance == pytest.approx(10.0)


def test_showing_the_overview_puts_the_camera_back(controller):
    controller.save_overview()
    controller.renderer.GetActiveCamera().SetPosition(50.0, 50.0, 50.0)

    controller.show_overview()

    assert np.linalg.norm(camera_of(controller).GetPosition()) == pytest.approx(10.0)


def test_asking_for_the_overview_first_captures_rather_than_restoring(controller):
    """Nothing is remembered yet, so where the camera is becomes the overview."""
    controller.show_overview()

    assert controller._orbit is not None
    assert controller._orbit.distance == pytest.approx(10.0)
