"""
The red line joining the viewpoints of a route, in the order they get flown.

One polyline from frustum to frustum. The order comes from
`viewscope.data.flight_path`, which is where the thinking is; this only draws
what it is handed. Rebuilt whenever the route changes, which is cheap: a
route is a few hundred points, and the actor is thrown away and remade rather
than edited in place.

The line is drawn over the model rather than through it. A flight path that
disappears inside the mesh every time it passes behind it is unreadable, and
the thing being looked at is the shape of the path, not where it sits in the
depth buffer.
"""

from __future__ import annotations

import numpy as np
import vtk

from viewscope.config import FLIGHT_PATH_COLOUR, FLIGHT_PATH_WIDTH
from viewscope.scene import transform


class FlightPathLine:
    """A polyline through the route, added to and taken off a renderer."""

    def __init__(self):
        self.actor: vtk.vtkActor | None = None
        self._visible = True

    def show(self, renderer: vtk.vtkRenderer, positions):
        """Draw the path through these points, in this order.

        Replaces whatever was drawn before. Fewer than two points is not a
        path, so it clears instead.
        """
        self.remove_from(renderer)

        points = np.asarray(positions, dtype=np.float64).reshape(-1, 3)
        if len(points) < 2:
            return

        self.actor = self._build(points)
        self.actor.SetVisibility(self._visible)
        renderer.AddActor(self.actor)

    def set_visible(self, visible: bool):
        self._visible = visible
        if self.actor is not None:
            self.actor.SetVisibility(visible)

    def remove_from(self, renderer: vtk.vtkRenderer):
        """Take the line off, leaving nothing behind to be drawn again."""
        if self.actor is not None:
            renderer.RemoveActor(self.actor)
            self.actor = None

    @staticmethod
    def _build(points: np.ndarray) -> vtk.vtkActor:
        polyline = vtk.vtkPolyLine()
        polyline.GetPointIds().SetNumberOfIds(len(points))
        for step in range(len(points)):
            polyline.GetPointIds().SetId(step, step)

        cells = vtk.vtkCellArray()
        cells.InsertNextCell(polyline)

        poly = vtk.vtkPolyData()
        poly.SetPoints(transform.points(points))
        poly.SetLines(cells)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        prop = actor.GetProperty()
        prop.SetColor(*FLIGHT_PATH_COLOUR)
        prop.SetLineWidth(FLIGHT_PATH_WIDTH)
        # Lighting would shade the line by its direction, so a path that turns
        # would fade in and out along its own length.
        prop.LightingOff()

        # The line is left to the depth buffer like everything else, so it
        # goes behind the model when it passes behind it. Pulling it forward
        # with a coincident-topology offset is not worth what it costs: that
        # setting is static on vtkMapper, so one mapper asking for it turns
        # it on for every mapper in the process, and the floor grid - which
        # lies in the same plane as the ground the model sits on - starts
        # drawing over the model instead of being hidden by it. Nor is there
        # anything to gain: the path is kept a clearance away from the model
        # by the planner, so there is no coincident geometry to resolve.

        return actor
