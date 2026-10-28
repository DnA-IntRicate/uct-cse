"""
Drawing one target's weights and its sector decomposition.

The picked target gets a marker, and every camera that can see it gets a ray
out to it, so a strong sector can be traced back to the camera that made it
strong. The rays carry the numbers: coloured by weight they show how useful
each camera is, and coloured by sector they show the compass around the
target normal that the observers fall into.
"""

from __future__ import annotations

import colorsys

import numpy as np
import vtk
from vtkmodules.util import numpy_support as vtknp

from viewscope.config import (
    COLOUR_BY_SECTOR,
    COLOUR_BY_WEIGHT,
    SECTOR_COLOURS,
    TARGET_MARKER_COLOUR,
    TOP_OBSERVER_COLOUR,
    WEIGHT_HUE,
    WEIGHT_SATURATION_RANGE,
    WEIGHT_VALUE_RANGE,
    OverlayOptions,
)

from .target_report import TargetReport
from .transform import cells, points


def weight_lut() -> vtk.vtkLookupTable:
    """One blue, light for a weak camera through to dark for a strong one, over [0, 1]."""
    lut = vtk.vtkLookupTable()
    # VTK ramps on an S-curve unless told otherwise, which bunches the middle
    # weights together and pulls the ends apart. Weight is linear, so the
    # colour is too, and what is read off the bar is what was measured.
    lut.SetRampToLinear()
    lut.SetHueRange(WEIGHT_HUE, WEIGHT_HUE)
    lut.SetSaturationRange(*WEIGHT_SATURATION_RANGE)
    lut.SetValueRange(*WEIGHT_VALUE_RANGE)
    lut.SetTableRange(0.0, 1.0)
    lut.Build()

    return lut


def sector_colour_2(sector: int) -> tuple[float, float, float]:
    """The colour that belongs to one wedge, taken in order from the fixed set."""
    return SECTOR_COLOURS[sector % len(SECTOR_COLOURS)]


def sector_colour(sector: int, sector_count: int) -> tuple[float, float, float]:
    """A hue per wedge, walking the colour wheel the way the wedges walk the compass."""
    return colorsys.hsv_to_rgb((sector % sector_count) / sector_count, 0.72, 1.0)


def weight_colour(lut: vtk.vtkLookupTable, weight: float) -> tuple[float, float, float]:
    """Read one weight off the same table the scalar bar draws."""
    rgb = [0.0, 0.0, 0.0]
    lut.GetColor(float(np.clip(weight, 0.0, 1.0)), rgb)

    return rgb[0], rgb[1], rgb[2]


def observer_colour(
    observer, colour_by: str, lut: vtk.vtkLookupTable, top_camera: int | None = None
) -> tuple[float, float, float]:
    """The one colour that stands for an observer, whatever is drawing it.

    The ray out to a camera and the camera's own frustum are the same fact
    twice over, so both read it off here and cannot drift apart.

    `top_camera` is the target's heaviest observer, which weight mode takes off
    the ramp and hands the one colour that is not a weight. Sector mode ignores
    it: there the colour already answers a different question.
    """
    if colour_by == COLOUR_BY_SECTOR:
        return sector_colour(observer.sector, 8)

    if observer.camera_index == top_camera:
        return TOP_OBSERVER_COLOUR

    return weight_colour(lut, observer.weight)


class TargetOverlay:
    """Every actor that belongs to the picked target, added and dropped together."""

    def __init__(self):
        self._renderer = None
        self._actors: list[vtk.vtkProp] = []
        self._lut = weight_lut()

    @property
    def showing(self) -> bool:
        return bool(self._actors)

    def show(
        self,
        renderer: vtk.vtkRenderer,
        report: TargetReport,
        camera_positions: np.ndarray,
        diagonal: float,
        options: OverlayOptions,
    ):
        """Redraw the overlay for one report. Replaces whatever was up before."""
        self.clear()

        self._renderer = renderer
        position = np.asarray(report.position, dtype=np.float64)

        actors: list[vtk.vtkProp] = [self._marker(position, options.marker_radius(diagonal))]

        if options.rays:
            actors.extend(self._rays(report, position, camera_positions, options.colour_by))

        if options.colour_by == COLOUR_BY_WEIGHT:
            actors.append(self._scalar_bar())

        for actor in actors:
            if isinstance(actor, vtk.vtkActor2D):
                renderer.AddActor2D(actor)
            else:
                renderer.AddActor(actor)

        self._actors = actors

    def clear(self):
        """Take the overlay down. Safe to call when nothing is up."""
        if self._renderer is not None:
            for actor in self._actors:
                if isinstance(actor, vtk.vtkActor2D):
                    self._renderer.RemoveActor2D(actor)
                else:
                    self._renderer.RemoveActor(actor)

        self._actors = []

    def set_visible(self, visible: bool):
        for actor in self._actors:
            actor.SetVisibility(visible)

    # -- pieces --------------------------------------------------------

    def _marker(self, position, radius) -> vtk.vtkActor:
        """The picked point itself, big enough to find again."""
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(*position)
        sphere.SetRadius(max(float(radius), 1e-6))
        sphere.SetThetaResolution(24)
        sphere.SetPhiResolution(24)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*TARGET_MARKER_COLOUR)

        return actor

    def _rays(self, report, position, camera_positions, colour_by) -> list[vtk.vtkActor]:
        """A line out to every observing camera, the sector winners drawn heavier."""
        positions = np.asarray(camera_positions, dtype=np.float64)
        groups = {True: [], False: []}
        top_camera = None if report.top_observer is None else report.top_observer.camera_index

        for observer in report.observers:
            if not 0 <= observer.camera_index < len(positions):
                continue

            colour = self._ray_colour(observer, colour_by, top_camera)
            groups[observer.best].append((positions[observer.camera_index], colour))

        actors = []
        for best, rays in groups.items():
            if not rays:
                continue

            actor = _actor_for_polydata(_ray_bundle(position, rays))
            actor.GetMapper().SetScalarModeToUseCellData()
            actor.GetMapper().SetColorModeToDirectScalars()
            actor.GetProperty().SetLineWidth(3.5 if best else 1.25)
            actor.GetProperty().SetOpacity(1.0 if best else 0.55)
            actor.GetProperty().LightingOff()
            actors.append(actor)

        return actors

    def _ray_colour(self, observer, colour_by, top_camera):
        return observer_colour(observer, colour_by, self._lut, top_camera)

    def _scalar_bar(self) -> vtk.vtkScalarBarActor:
        """Reads the ray colours back as weights."""
        bar = vtk.vtkScalarBarActor()
        bar.SetLookupTable(self._lut)
        bar.SetTitle("weight")
        bar.SetNumberOfLabels(5)
        bar.SetWidth(0.055)
        bar.SetHeight(0.32)
        bar.SetPosition(0.93, 0.14)

        return bar


# -- helpers ---------------------------------------------------------------


def _actor_for_polydata(poly: vtk.vtkPolyData) -> vtk.vtkActor:
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor


def _ray_bundle(position, rays) -> vtk.vtkPolyData:
    """One two-point line per camera, each carrying its own colour."""
    vertices = np.empty((2 * len(rays), 3), dtype=np.float64)
    edges = np.empty((len(rays), 2), dtype=np.int64)
    colours = np.empty((len(rays), 3), dtype=np.uint8)

    for i, (camera, colour) in enumerate(rays):
        vertices[2 * i] = position
        vertices[2 * i + 1] = camera
        edges[i] = (2 * i, 2 * i + 1)
        colours[i] = np.round(np.asarray(colour) * 255.0)

    poly = vtk.vtkPolyData()
    poly.SetPoints(points(vertices))
    poly.SetLines(cells(edges, 2))

    scalars = vtknp.numpy_to_vtk(np.ascontiguousarray(colours), deep=True)
    scalars.SetName("ray")
    poly.GetCellData().SetScalars(scalars)

    return poly
