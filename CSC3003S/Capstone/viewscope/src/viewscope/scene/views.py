from __future__ import annotations

import numpy as np
import trimesh
import vtk
from vtkmodules.util import numpy_support as vtknp

from viewscope.config import (
    EDGE_COLOUR,
    GEOMETRY_COLOUR,
    OCCLUDED_COLOUR,
    UNOBSERVED_COLOUR,
    UNOBSERVED_POINT_GROWTH,
    VISIBLE_COLOUR,
)

from .stats import FieldStats
from .transform import cloud_polydata, texture_from_mesh, trimesh_to_polydata


class MeshView:
    """The scene mesh, shown either textured or as plain geometry."""

    def __init__(self, mesh: trimesh.Geometry):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(trimesh_to_polydata(mesh))

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)

        self.texture = texture_from_mesh(mesh)
        if self.texture is not None:
            self.actor.SetTexture(self.texture)

    def add_to(self, renderer: vtk.vtkRenderer):
        renderer.AddActor(self.actor)

    def remove_from(self, renderer: vtk.vtkRenderer):
        renderer.RemoveActor(self.actor)

    def set_visible(self, visible: bool):
        self.actor.SetVisibility(visible)

    def show_textured(self):
        prop = self.actor.GetProperty()

        if self.texture:
            self.actor.SetTexture(self.texture)

        self.actor.GetMapper().ScalarVisibilityOn()
        prop.SetRepresentationToSurface()
        prop.SetColor(1.0, 1.0, 1.0)
        prop.EdgeVisibilityOff()

    def show_geometry(self):
        prop = self.actor.GetProperty()
        # self.actor.SetTexture(None)
        self.actor.GetMapper().ScalarVisibilityOff()
        prop.SetRepresentationToSurface()
        prop.SetColor(*GEOMETRY_COLOUR)
        prop.EdgeVisibilityOn()
        prop.SetEdgeColor(*EDGE_COLOUR)
        prop.SetLineWidth(1.0)


class UnobservedTargets:
    """The targets nothing can see, as a cloud of their own.

    A separate cloud rather than a recolouring of the targets, because while
    these are up they are the only targets drawn: the viewport takes the
    cloud they were picked out of off the screen, and what is left is the
    answer to where the gaps are. Recolouring would have meant hunting for a
    colour among sixty thousand points that are still there.

    Rebuilt whenever what it marks changes, which is cheap: a point cloud is
    a block of coordinates, and there is nothing to update in place.
    """

    def __init__(self, point_size: float = 2.0):
        self.actor: vtk.vtkActor | None = None
        self._point_size = float(point_size)
        self._visible = True

    def show(self, renderer: vtk.vtkRenderer, targets):
        """Mark these targets. An empty set marks nothing, which is the aim."""
        self.remove_from(renderer)

        points = np.asarray(targets, dtype=np.float64).reshape(-1, 3)
        if not len(points):
            return

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(cloud_polydata(points))
        # No scalars of its own: one flat colour is the whole point of it.
        mapper.ScalarVisibilityOff()

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.GetProperty().SetColor(*UNOBSERVED_COLOUR)
        self.actor.GetProperty().SetPointSize(self._point_size + UNOBSERVED_POINT_GROWTH)
        self.actor.SetVisibility(self._visible)

        renderer.AddActor(self.actor)

    def set_point_size(self, size: float):
        """Follow the cloud's point size, staying the larger of the two."""
        self._point_size = float(size)
        if self.actor is not None:
            self.actor.GetProperty().SetPointSize(self._point_size + UNOBSERVED_POINT_GROWTH)

    def set_visible(self, visible: bool):
        self._visible = visible
        if self.actor is not None:
            self.actor.SetVisibility(visible)

    def remove_from(self, renderer: vtk.vtkRenderer):
        if self.actor is not None:
            renderer.RemoveActor(self.actor)
            self.actor = None


class TargetCloudView:
    """Score-coloured target points, plus the scalar bar that explains them."""

    def __init__(self, targets: np.ndarray, scores: object | None = None, point_size: float = 2.0):
        self.scores = scores
        self.polydata = cloud_polydata(targets)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.polydata)

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.GetProperty().SetPointSize(point_size)
        mapper.SetColorModeToMapScalars()

        self.lut = None
        self.scalar_bar = None
        self._field = None
        # What was last painted, so that occlusion can hand the cloud back
        # exactly as it took it. Reading the field off the bundle again would
        # undo a route's own colouring every time a camera was clicked.
        self._values = None
        self._range = None
        self._occluding = False
        self._occlusion_lut = self._build_occlusion_lut()
        if scores is not None:
            self.lut = vtk.vtkLookupTable()
            self.lut.SetHueRange(0.667, 0.0)  # blue low, red high
            self.lut.Build()
            mapper.SetLookupTable(self.lut)

            self.scalar_bar = vtk.vtkScalarBarActor()
            self.scalar_bar.SetLookupTable(self.lut)
            self.scalar_bar.SetNumberOfLabels(5)
            self.scalar_bar.SetWidth(0.055)
            self.scalar_bar.SetHeight(0.32)
            self.scalar_bar.SetPosition(0.93, 0.55)

    @property
    def has_scores(self) -> bool:
        return self.scores is not None

    @property
    def occluding(self) -> bool:
        return self._occluding

    def add_to(self, renderer: vtk.vtkRenderer):
        renderer.AddActor(self.actor)
        if self.scalar_bar is not None:
            renderer.AddActor2D(self.scalar_bar)

    def remove_from(self, renderer: vtk.vtkRenderer):
        renderer.RemoveActor(self.actor)
        if self.scalar_bar is not None:
            renderer.RemoveActor2D(self.scalar_bar)

    def set_visible(self, visible: bool):
        self.actor.SetVisibility(visible)
        if self.scalar_bar is not None:
            self.scalar_bar.SetVisibility(visible and not self._occluding)

    def set_point_size(self, size: float):
        self.actor.GetProperty().SetPointSize(float(size))

    def set_field(self, field: str):
        """Colour by one scalar field. Returns its stats, or None if unscored."""
        if self.scores is None:
            return None

        return self.set_values(field, getattr(self.scores, field))

    def set_values(self, field: str, values, value_range: tuple[float, float] | None = None):
        """Colour by these values, which need not be the ones the bundle shipped.

        `value_range` pins the scale. Left out, the values colour themselves,
        which is right for a field that covers the whole plan and wrong for
        one worked out from part of it: rescaled to whatever a few cameras
        reach, the first camera in a route would paint its own patch the
        colour of full coverage. Passed a fixed range, a colour means the
        same thing however much of the route is in.
        """
        self._field = field
        values = np.ascontiguousarray(values, dtype=np.float32)

        if self.scalar_bar is not None:
            self.scalar_bar.SetTitle(field)

        low, high = (
            (float(values.min()), float(values.max())) if value_range is None else value_range
        )
        self._values, self._range = values, (float(low), float(high))

        # Occlusion colouring owns the scalars while it is on; remember the
        # field so switching back picks up the one the panel is showing.
        if not self.occluding:
            array = vtknp.numpy_to_vtk(values, deep=True)
            array.SetName(field)
            self.polydata.GetPointData().SetScalars(array)

            mapper = self.actor.GetMapper()
            # A zero width range leaves the colours undefined, so an empty
            # route still gets a scale - every target at the cold end of it.
            mapper.SetScalarRange(float(low), float(max(high, low + 1e-6)))
            mapper.ScalarVisibilityOn()

        return FieldStats(field, float(values.min()), float(values.mean()), float(values.max()))

    def set_occlusion(self, mask: np.ndarray | None):
        """
        Colour points red where the selected camera can see them, grey elsewhere.

        Pass None to go back to the scalar field colouring.
        """
        was_occluding = self._occluding
        self._occluding = mask is not None
        mapper = self.actor.GetMapper()

        if mask is None and not was_occluding:
            # Nothing to give back: the cloud is already wearing whatever it
            # was painted with. Route planning asks for this on every click,
            # and pushing sixty thousand values back at the renderer to end
            # up where it started is the slowest thing a click could do.
            return

        if mask is None:
            if self.scalar_bar is not None:
                self.scalar_bar.SetVisibility(self.actor.GetVisibility())
            if self.lut is not None:
                mapper.SetLookupTable(self.lut)
            if self._field is not None and self._values is not None:
                # Back to what was on the cloud before, values and scale
                # alike - not to the column the bundle shipped, which may be
                # about a different set of cameras entirely.
                self.set_values(self._field, self._values, self._range)
            else:
                mapper.ScalarVisibilityOff()
            return

        values = np.ascontiguousarray(mask, dtype=np.float32)
        array = vtknp.numpy_to_vtk(values, deep=True)
        array.SetName("visible")
        self.polydata.GetPointData().SetScalars(array)

        mapper.SetLookupTable(self._occlusion_lut)
        mapper.SetScalarRange(0.0, 1.0)
        mapper.ScalarVisibilityOn()

        # The scalar bar explains the field, which is not what is on screen.
        if self.scalar_bar is not None:
            self.scalar_bar.SetVisibility(False)

    @staticmethod
    def _build_occlusion_lut():
        lut = vtk.vtkLookupTable()
        lut.SetNumberOfTableValues(2)
        lut.SetTableRange(0.0, 1.0)
        lut.SetTableValue(0, *OCCLUDED_COLOUR, 1.0)
        lut.SetTableValue(1, *VISIBLE_COLOUR, 1.0)
        lut.Build()
        return lut
