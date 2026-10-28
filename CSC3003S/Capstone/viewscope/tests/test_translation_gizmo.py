"""Unit tests for src/viewscope/scene/gizmos/translation.py.

The gizmo picks handles out of the viewport and turns mouse positions into
world-space points, so it is driven against a real offscreen render window
rather than a bare renderer: both need a viewport with a size to work at all.
"""

import math

import numpy as np
import pytest
import vtk

from viewscope.scene.gizmos.translation import TranslationGizmo


@pytest.fixture
def window():
    one = vtk.vtkRenderWindow()
    one.SetOffScreenRendering(1)
    one.SetSize(400, 400)
    return one


@pytest.fixture
def renderer(window):
    one = vtk.vtkRenderer()
    window.AddRenderer(one)
    return one


@pytest.fixture
def target(renderer):
    source = vtk.vtkSphereSource()
    source.SetRadius(1.0)
    source.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(source.GetOutput())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    renderer.AddActor(actor)
    return actor


@pytest.fixture
def gizmo(renderer):
    return TranslationGizmo(renderer)


@pytest.fixture
def attached(gizmo, target, renderer, window):
    """A gizmo pointed at the sphere, with the scene framed and drawn once."""
    gizmo.attach(target)
    renderer.ResetCamera()
    window.Render()
    return gizmo


def a_handle_pixel(gizmo) -> tuple[int, int]:
    """A viewport position that picks one of the arrows."""
    for x in range(0, 400, 5):
        for y in range(0, 400, 5):
            if gizmo.try_start_drag(x, y):
                gizmo.end_drag()
                return x, y

    raise AssertionError("no handle was pickable anywhere in the viewport")


# -----------------------------------------------------------------------------
# What gets built
# -----------------------------------------------------------------------------


def test_there_is_one_arrow_per_world_axis(gizmo, renderer):
    assert len(gizmo._actors) == 3
    assert renderer.GetActors().GetNumberOfItems() == 3


def test_each_arrow_knows_the_axis_it_slides_along(gizmo):
    axes = sorted(tuple(axis) for axis in gizmo._axis_of.values())

    assert axes == [(0.0, 0.0, 1.0), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0)]


def test_the_arrows_are_coloured_per_axis(gizmo):
    colours = {
        tuple(np.round(gizmo._axis_of[actor])): actor.GetProperty().GetColor()
        for actor in gizmo._actors
    }

    assert colours[(1.0, 0.0, 0.0)] == pytest.approx((0.85, 0.20, 0.20), abs=1 / 255)
    assert colours[(0.0, 1.0, 0.0)] == pytest.approx((0.20, 0.85, 0.20), abs=1 / 255)
    assert colours[(0.0, 0.0, 1.0)] == pytest.approx((0.20, 0.45, 0.90), abs=1 / 255)


def test_the_gizmo_starts_hidden_and_idle(gizmo):
    assert all(actor.GetVisibility() == 0 for actor in gizmo._actors)
    assert not gizmo.active


# -----------------------------------------------------------------------------
# Pointing it at something
# -----------------------------------------------------------------------------


def test_attaching_shows_the_handles_at_the_targets_centre(gizmo, target):
    target.SetPosition(5.0, 6.0, 7.0)

    gizmo.attach(target)

    assert all(actor.GetVisibility() == 1 for actor in gizmo._actors)
    for actor in gizmo._actors:
        assert actor.GetUserTransform().GetPosition() == pytest.approx([5.0, 6.0, 7.0])


def test_the_handles_are_sized_to_the_target(gizmo, target, renderer):
    gizmo.attach(target)
    small = gizmo._actors[0].GetUserTransform().GetScale()[0]

    bigger = vtk.vtkSphereSource()
    bigger.SetRadius(10.0)
    bigger.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(bigger.GetOutput())
    large_actor = vtk.vtkActor()
    large_actor.SetMapper(mapper)

    gizmo.attach(large_actor)

    assert gizmo._actors[0].GetUserTransform().GetScale()[0] > small


def test_a_target_of_no_size_still_gets_handles(gizmo, renderer):
    """A zero length arrow would not be pickable."""
    empty = vtk.vtkActor()

    gizmo.attach(empty)

    assert gizmo._actors[0].GetUserTransform().GetScale()[0] > 0.0


def test_detaching_hides_the_handles(gizmo, target):
    gizmo.attach(target)

    gizmo.detach()

    assert all(actor.GetVisibility() == 0 for actor in gizmo._actors)
    assert gizmo._target is None


def test_refreshing_follows_a_target_that_moved_by_other_means(gizmo, target):
    gizmo.attach(target)
    target.SetPosition(3.0, 0.0, 0.0)

    gizmo.refresh()

    assert gizmo._actors[0].GetUserTransform().GetPosition() == pytest.approx([3.0, 0.0, 0.0])


def test_refreshing_can_be_told_a_new_heading(gizmo, target):
    gizmo.attach(target, heading_deg=0.0)

    gizmo.refresh(heading_deg=90.0)

    assert gizmo._heading_deg == 90.0


def test_refreshing_with_nothing_attached_is_harmless(gizmo):
    gizmo.refresh(heading_deg=45.0)

    assert gizmo._heading_deg == 45.0


def test_the_handles_can_be_hidden_by_hand(gizmo, target):
    gizmo.attach(target)

    gizmo.set_visible(False)

    assert all(actor.GetVisibility() == 0 for actor in gizmo._actors)


def test_removing_takes_every_arrow_off_the_renderer(gizmo, renderer):
    gizmo.remove_from(renderer)

    assert renderer.GetActors().GetNumberOfItems() == 0


# -----------------------------------------------------------------------------
# Aligning an arrow onto its axis
# -----------------------------------------------------------------------------


def rotated(matrix, vector):
    out = [0.0, 0.0, 0.0, 0.0]
    matrix.MultiplyPoint([*vector, 0.0], out)
    return np.array(out[:3])


def test_an_axis_that_is_already_right_is_left_alone():
    matrix = TranslationGizmo._align_matrix(np.array([1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0]))

    assert rotated(matrix, [1.0, 0.0, 0.0]) == pytest.approx([1.0, 0.0, 0.0])


def test_a_quarter_turn_lands_on_the_axis_asked_for():
    matrix = TranslationGizmo._align_matrix(np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]))

    assert rotated(matrix, [1.0, 0.0, 0.0]) == pytest.approx([0.0, 1.0, 0.0], abs=1e-9)


def test_an_axis_pointing_the_other_way_is_turned_right_round():
    matrix = TranslationGizmo._align_matrix(np.array([0.0, 1.0, 0.0]), np.array([0.0, -1.0, 0.0]))

    assert rotated(matrix, [0.0, 1.0, 0.0]) == pytest.approx([0.0, -1.0, 0.0], abs=1e-9)


def test_reversing_x_finds_an_axis_to_turn_about():
    """The obvious perpendicular is degenerate here, so another is taken."""
    matrix = TranslationGizmo._align_matrix(np.array([1.0, 0.0, 0.0]), np.array([-1.0, 0.0, 0.0]))

    assert rotated(matrix, [1.0, 0.0, 0.0]) == pytest.approx([-1.0, 0.0, 0.0], abs=1e-9)


def test_the_alignment_is_a_rotation_and_nothing_else():
    matrix = TranslationGizmo._align_matrix(np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0]))
    basis = np.array([rotated(matrix, axis) for axis in np.eye(3)])

    assert basis @ basis.T == pytest.approx(np.eye(3), abs=1e-9)
    assert np.linalg.det(basis) == pytest.approx(1.0)


# -----------------------------------------------------------------------------
# Starting a drag
# -----------------------------------------------------------------------------


def test_nothing_is_dragged_when_nothing_is_attached(gizmo):
    assert gizmo.try_start_drag(200, 200) is False
    assert not gizmo.active


def test_clicking_a_handle_starts_a_drag(attached):
    x, y = a_handle_pixel(attached)

    assert attached.try_start_drag(x, y) is True
    assert attached.active


def test_clicking_away_from_the_handles_starts_nothing(attached):
    assert attached.try_start_drag(2, 2) is False
    assert not attached.active


def test_a_handle_pointing_at_the_camera_cannot_be_dragged(gizmo, target, renderer, window):
    """Edge on there is no sensible plane to slide it in."""
    gizmo.attach(target)
    camera = renderer.GetActiveCamera()
    camera.SetFocalPoint(0.0, 0.0, 0.0)
    camera.SetPosition(10.0, 0.0, 0.0)  # straight down the x axis
    window.Render()

    x_handle = next(a for a, axis in gizmo._axis_of.items() if axis[0] == 1.0)

    assert gizmo._try_start_translate(x_handle, 200, 200) is False


def test_a_camera_sitting_on_the_target_has_no_plane_to_offer(gizmo, target, renderer):
    gizmo.attach(target)
    camera = renderer.GetActiveCamera()
    camera.SetPosition(0.0, 0.0, 0.0)
    camera.SetFocalPoint(0.0, 0.0, 1.0)

    assert gizmo._camera_facing_plane(np.array([0.0, 1.0, 0.0]), np.zeros(3)) is None


def test_a_camera_almost_exactly_on_the_target_gives_no_usable_plane(gizmo, target, renderer):
    """Far enough out to have a direction, too close for that direction to
    survive being crossed twice."""
    gizmo.attach(target)
    camera = renderer.GetActiveCamera()
    # Just past the distance floor, at an angle that clears the edge-on test,
    # so it is the plane normal that underflows rather than the view.
    cosine = 0.95
    offset = 1.5e-6 * np.array([cosine, math.sqrt(1.0 - cosine**2), 0.0])
    camera.SetPosition(*offset)

    assert gizmo._camera_facing_plane(np.array([1.0, 0.0, 0.0]), np.zeros(3)) is None


def test_a_ray_that_never_meets_the_plane_gives_no_point(attached):
    """Parallel to it, so there is nothing to intersect."""
    normal = np.array([0.0, 0.0, 1.0])
    far_off = np.array([0.0, 0.0, 1e12])

    assert attached._ray_plane_point(normal, far_off, 200, 200) is None


# -----------------------------------------------------------------------------
# Dragging
# -----------------------------------------------------------------------------


def test_dragging_moves_the_target_along_the_handles_axis(attached, target):
    x, y = a_handle_pixel(attached)
    attached.try_start_drag(x, y)
    axis = attached._drag_axis
    before = attached._target_centre()

    attached.drag(x + 60, y + 60)

    moved = attached._target_centre() - before
    assert np.linalg.norm(moved) > 0.0
    # Everything off the handle's own axis stays where it was.
    assert moved - np.dot(moved, axis) * axis == pytest.approx(np.zeros(3), abs=1e-9)


def test_the_handles_follow_the_target_as_it_is_dragged(attached, target):
    x, y = a_handle_pixel(attached)
    attached.try_start_drag(x, y)

    attached.drag(x + 60, y + 60)

    centre = attached._target_centre()
    assert attached._actors[0].GetUserTransform().GetPosition() == pytest.approx(centre)


def test_each_drag_tick_reports_the_new_centre(attached, target):
    seen = []
    attached.attach(target, on_move=seen.append)
    x, y = a_handle_pixel(attached)
    attached.try_start_drag(x, y)

    attached.drag(x + 60, y + 60)

    assert len(seen) == 1
    assert seen[0] == pytest.approx(attached._target_centre())


def test_a_drag_that_was_never_started_moves_nothing(attached):
    before = attached._target_centre()

    attached.drag(300, 300)

    assert attached._target_centre() == pytest.approx(before)


def test_a_drag_with_nothing_attached_moves_nothing(gizmo):
    gizmo.active = True

    gizmo.drag(300, 300)

    assert gizmo._target is None


def test_a_drag_tick_that_misses_the_plane_is_passed_over(attached, monkeypatch):
    x, y = a_handle_pixel(attached)
    attached.try_start_drag(x, y)
    before = attached._target_centre()
    monkeypatch.setattr(attached, "_ray_plane_point", lambda *args: None)

    attached.drag(x + 60, y + 60)

    assert attached._target_centre() == pytest.approx(before)


def test_ending_the_drag_puts_the_gizmo_back_to_idle(attached):
    x, y = a_handle_pixel(attached)
    attached.try_start_drag(x, y)

    attached.end_drag()

    assert not attached.active


def test_dragging_twice_moves_from_where_it_was_left(attached):
    x, y = a_handle_pixel(attached)
    attached.try_start_drag(x, y)
    attached.drag(x + 40, y + 40)
    once = attached._target_centre()

    attached.drag(x + 80, y + 80)

    assert np.linalg.norm(attached._target_centre() - once) > 0.0


def test_a_target_that_already_has_a_transform_is_moved_on_top_of_it(attached, target):
    existing = vtk.vtkTransform()
    existing.Translate(2.0, 0.0, 0.0)
    target.SetUserTransform(existing)

    attached._translate_target(np.array([1.0, 0.0, 0.0]))

    assert target.GetUserTransform().GetPosition() == pytest.approx([3.0, 0.0, 0.0])


def test_a_target_with_no_transform_yet_is_moved_from_the_origin(attached, target):
    target.SetUserTransform(None)

    attached._translate_target(np.array([0.0, 4.0, 0.0]))

    assert target.GetUserTransform().GetPosition() == pytest.approx([0.0, 4.0, 0.0])


def test_a_handle_whose_plane_the_click_misses_starts_no_drag(attached, monkeypatch):
    """The plane is there, but the mouse ray never reaches it."""
    handle = attached._actors[0]
    monkeypatch.setattr(attached, "_ray_plane_point", lambda *args: None)

    assert attached._try_start_translate(handle, 200, 200) is False
    assert not attached.active
