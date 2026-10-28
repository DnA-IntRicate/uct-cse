"""Unit tests for src/viewscope/scene/flight_path.py.

The line is drawn against a real vtkRenderer. Nothing here needs a window:
actors can be added to and taken off a renderer without one ever being shown.
"""

import numpy as np
import vtk

from viewscope.config import FLIGHT_PATH_WIDTH
from viewscope.scene.flight_path import FlightPathLine

SQUARE = [[0.0, 0.0, 5.0], [10.0, 0.0, 5.0], [10.0, 10.0, 5.0]]


def renderer() -> vtk.vtkRenderer:
    return vtk.vtkRenderer()


# -----------------------------------------------------------------------------
# Drawing
# -----------------------------------------------------------------------------


def test_a_route_of_two_or_more_points_is_drawn():
    line, scene = FlightPathLine(), renderer()

    line.show(scene, SQUARE)

    assert line.actor is not None
    assert scene.GetActors().GetNumberOfItems() == 1
    assert line.actor.GetProperty().GetLineWidth() == FLIGHT_PATH_WIDTH


def test_the_polyline_keeps_every_point_in_the_order_given():
    line = FlightPathLine()
    line.show(renderer(), SQUARE)

    assert line.actor is not None
    drawn = line.actor.GetMapper().GetInput()
    assert drawn.GetNumberOfPoints() == 3
    assert drawn.GetPoint(0) == (0.0, 0.0, 5.0)
    assert drawn.GetPoint(2) == (10.0, 10.0, 5.0)


def test_a_single_point_is_not_a_path_and_draws_nothing():
    line, scene = FlightPathLine(), renderer()

    line.show(scene, [[0.0, 0.0, 5.0]])

    assert line.actor is None
    assert scene.GetActors().GetNumberOfItems() == 0


def test_an_empty_route_draws_nothing():
    line, scene = FlightPathLine(), renderer()

    line.show(scene, np.zeros((0, 3)))

    assert line.actor is None


def test_redrawing_replaces_the_line_rather_than_stacking_them_up():
    """The actor is thrown away and remade on every route change."""
    line, scene = FlightPathLine(), renderer()

    line.show(scene, SQUARE)
    first = line.actor
    line.show(scene, SQUARE[::-1])

    assert line.actor is not first
    assert scene.GetActors().GetNumberOfItems() == 1


def test_a_shorter_route_clears_the_line_that_was_there():
    """Dropping to one camera must leave nothing behind from the old route."""
    line, scene = FlightPathLine(), renderer()

    line.show(scene, SQUARE)
    line.show(scene, [[0.0, 0.0, 5.0]])

    assert line.actor is None
    assert scene.GetActors().GetNumberOfItems() == 0


# -----------------------------------------------------------------------------
# Hiding and removing
# -----------------------------------------------------------------------------


def test_hiding_the_line_leaves_the_actor_in_place():
    line, scene = FlightPathLine(), renderer()
    line.show(scene, SQUARE)

    line.set_visible(False)

    assert line.actor is not None
    assert line.actor.GetVisibility() == 0
    assert scene.GetActors().GetNumberOfItems() == 1


def test_showing_it_again_turns_the_actor_back_on():
    line, scene = FlightPathLine(), renderer()
    line.show(scene, SQUARE)
    line.set_visible(False)

    line.set_visible(True)

    assert line.actor is not None
    assert line.actor.GetVisibility() == 1


def test_a_line_hidden_before_it_is_drawn_comes_back_hidden():
    """The route can be switched off while no route is loaded."""
    line, scene = FlightPathLine(), renderer()
    line.set_visible(False)

    line.show(scene, SQUARE)

    assert line.actor is not None
    assert line.actor.GetVisibility() == 0


def test_hiding_with_nothing_drawn_is_harmless():
    line = FlightPathLine()

    line.set_visible(False)

    assert line.actor is None


def test_removing_takes_the_actor_off_and_forgets_it():
    line, scene = FlightPathLine(), renderer()
    line.show(scene, SQUARE)

    line.remove_from(scene)

    assert line.actor is None
    assert scene.GetActors().GetNumberOfItems() == 0


def test_removing_a_line_that_was_never_drawn_is_harmless():
    line, scene = FlightPathLine(), renderer()

    line.remove_from(scene)

    assert line.actor is None
