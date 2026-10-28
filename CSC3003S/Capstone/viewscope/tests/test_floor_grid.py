"""Unit tests for src/viewscope/scene/gizmos/floor_grid.py."""

import pytest
import vtk

from viewscope.scene.gizmos.floor_grid import FloorGrid


@pytest.fixture
def renderer():
    return vtk.vtkRenderer()


@pytest.fixture
def grid(renderer):
    return FloorGrid(renderer, grid_size=5)


# -----------------------------------------------------------------------------
# Building
# -----------------------------------------------------------------------------


def test_building_adds_the_grid_and_both_axes(renderer):
    FloorGrid(renderer, grid_size=5)

    assert renderer.GetActors().GetNumberOfItems() == 3


def test_the_lattice_is_square_and_flat(grid):
    """2.5D: the z layer is never used."""
    dims = [0, 0, 0]
    grid.structured_grid.GetDimensions(dims)
    assert dims == [5, 5, 1]
    assert grid.structured_grid.GetNumberOfPoints() == 25


def test_the_lattice_is_centred_on_its_own_origin(grid):
    """So that moving it puts its middle where it was told, not its corner."""
    assert grid.structured_grid is not None
    bounds = grid.structured_grid.GetBounds()

    assert bounds == (-2.0, 2.0, -2.0, 2.0, 0.0, 0.0)


def test_an_even_sided_lattice_is_centred_too(renderer):
    grid = FloorGrid(renderer, grid_size=4)

    assert grid.structured_grid is not None
    assert grid.structured_grid.GetBounds() == (-1.5, 1.5, -1.5, 1.5, 0.0, 0.0)


def test_the_grid_is_drawn_faintly_as_wireframe(grid):
    prop = grid.grid_actor.GetProperty()

    assert prop.GetOpacity() == pytest.approx(0.1)
    assert prop.GetRepresentation() == vtk.VTK_WIREFRAME


def test_the_axes_are_coloured_red_for_x_and_green_for_y(grid):
    x_axis, y_axis = grid.axes_actors

    assert x_axis.GetProperty().GetColor() == (1.0, 0.0, 0.0)
    assert y_axis.GetProperty().GetColor() == (0.0, 1.0, 0.0)


def test_the_grid_is_built_where_it_is_told(renderer):
    grid = FloorGrid(renderer, grid_size=5, spawn_position=(10.0, -4.0, 2.0))

    assert grid.grid_actor is not None and grid.axes_actors is not None
    assert grid.grid_actor.GetPosition() == pytest.approx([10.0, -4.0, 2.0])
    assert grid.axes_actors[0].GetPosition() == pytest.approx([10.0, -4.0, 2.0])


def test_the_scale_applies_to_the_grid_and_the_axes_alike(renderer):
    grid = FloorGrid(renderer, grid_size=5, scale=3.0)

    assert grid.grid_actor is not None and grid.axes_actors is not None
    assert grid.grid_actor.GetScale() == pytest.approx([3.0, 3.0, 3.0])
    assert grid.axes_actors[1].GetScale() == pytest.approx([3.0, 3.0, 3.0])


# -----------------------------------------------------------------------------
# Re-anchoring
# -----------------------------------------------------------------------------


def test_moving_takes_the_grid_and_both_axes_with_it(grid):
    """Bundles do not share a frame, so the ground moves once a scene loads."""
    grid.move_to((100.0, 200.0, 5.0))

    assert grid.spawn_position == (100.0, 200.0, 5.0)
    assert grid.grid_actor.GetPosition() == pytest.approx([100.0, 200.0, 5.0])
    for axis in grid.axes_actors:
        assert axis.GetPosition() == pytest.approx([100.0, 200.0, 5.0])


def test_moving_takes_whatever_numbers_it_is_handed(grid):
    """Callers pass the scene centre, which arrives out of numpy."""
    import numpy as np

    grid.move_to(np.array([1, 2, 3]))

    assert grid.spawn_position == (1.0, 2.0, 3.0)


def test_moving_a_grid_that_has_been_removed_is_harmless(grid, renderer):
    grid.remove_from(renderer)

    grid.move_to((1.0, 2.0, 3.0))

    assert grid.spawn_position == (1.0, 2.0, 3.0)


# -----------------------------------------------------------------------------
# Hiding and removing
# -----------------------------------------------------------------------------


def test_hiding_turns_the_grid_and_both_axes_off(grid):
    grid.set_visible(False)

    assert grid.grid_actor.GetVisibility() == 0
    assert all(axis.GetVisibility() == 0 for axis in grid.axes_actors)


def test_showing_turns_them_all_back_on(grid):
    grid.set_visible(False)

    grid.set_visible(True)

    assert grid.grid_actor.GetVisibility() == 1
    assert all(axis.GetVisibility() == 1 for axis in grid.axes_actors)


def test_hiding_a_grid_that_has_been_removed_is_harmless(grid, renderer):
    grid.remove_from(renderer)

    grid.set_visible(False)

    assert grid.grid_actor is None


def test_removing_takes_everything_off_and_forgets_it(grid, renderer):
    grid.remove_from(renderer)

    assert grid.grid_actor is None
    assert grid.axes_actors is None
    assert renderer.GetActors().GetNumberOfItems() == 0


def test_removing_twice_is_harmless(grid, renderer):
    grid.remove_from(renderer)
    grid.remove_from(renderer)

    assert grid.grid_actor is None
