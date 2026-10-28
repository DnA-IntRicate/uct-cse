"""Unit tests for src/viewscope/scene/gizmos/camera_outline.py."""

import vtk

from viewscope.scene.gizmos.camera_outline import CameraOutline


def test_the_outline_is_added_to_the_renderer():
    outline, renderer = CameraOutline(), vtk.vtkRenderer()

    outline.build(renderer, (1.0, 2.0, 3.0))

    assert outline.outline_actor is not None
    assert renderer.GetActors().GetNumberOfItems() == 1


def test_the_outline_is_a_box_around_the_position_it_was_given():
    outline = CameraOutline()

    outline.build(vtk.vtkRenderer(), (1.0, 2.0, 3.0))

    assert outline.outline_actor is not None
    bounds = outline.outline_actor.GetBounds()
    assert bounds == (0.0, 2.0, 1.0, 3.0, 2.0, 4.0)


def test_the_outline_is_drawn_thick_enough_to_read():
    outline = CameraOutline()

    outline.build(vtk.vtkRenderer(), (0.0, 0.0, 0.0))

    assert outline.outline_actor is not None
    assert outline.outline_actor.GetProperty().GetLineWidth() == 4.0


def test_building_a_second_outline_leaves_the_first_on_the_renderer():
    """The caller removes the old one; build does not do it for them."""
    outline, renderer = CameraOutline(), vtk.vtkRenderer()

    outline.build(renderer, (0.0, 0.0, 0.0))
    first = outline.outline_actor
    outline.build(renderer, (5.0, 0.0, 0.0))

    assert outline.outline_actor is not first
    assert renderer.GetActors().GetNumberOfItems() == 2


def test_removing_takes_the_outline_off_and_forgets_it():
    outline, renderer = CameraOutline(), vtk.vtkRenderer()
    outline.build(renderer, (0.0, 0.0, 0.0))

    outline.remove_from(renderer)

    assert outline.outline_actor is None
    assert renderer.GetActors().GetNumberOfItems() == 0


def test_removing_an_outline_that_was_never_built_is_harmless():
    outline = CameraOutline()

    outline.remove_from(vtk.vtkRenderer())

    assert outline.outline_actor is None
