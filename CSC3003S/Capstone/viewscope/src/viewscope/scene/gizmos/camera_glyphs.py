from __future__ import annotations

import vtk

import viewscope_core as vc
from viewscope.config import (
    GLYPH_SOLID_OPACITY,
    GLYPH_WIREFRAME_OPACITY,
    ROUTE_SELECTED_COLOUR,
    ROUTE_UNSELECTED_COLOUR,
)
from viewscope.scene import transform

from .camera_outline import CameraOutline


class CameraGlyphs:
    """One frustum per planned viewpoint."""

    # Camera Colours
    COLOUR_ACTIVE: tuple = (1.00, 0.85, 0.10)  # Gold
    COLOUR_NEW: tuple = (0.20, 0.80, 1.00)  # Cyan

    def __init__(self, plan: vc.Plan):
        self.glyphs: dict[vtk.vtkActor, int] = {}
        #: The plan id of every row, so a loaded file can name the viewpoints
        #: it wants drawn by id rather than by position in the plan.
        self.ids: tuple[str, ...] = tuple(plan.ids)
        for i in range(len(plan.positions)):
            vertices, faces, colours, edges = vc.camera_glyph(
                plan.positions[i], plan.yaws_deg[i], plan.pitches_deg[i]
            )
            actor = self._build(transform.glyph_polydata(vertices, faces, colours, edges))
            self.glyphs[actor] = i

        self._visible: bool = True
        self._active: int | None = None
        self._route: set[int] | None = None
        self._shown: set[str] | None = None
        #: The camera the user has selected, wearing COLOUR_ACTIVE.
        self._selected: int | None = None
        #: Camera index -> colour, for the observers of the picked target.
        self._observers: dict[int, tuple[float, float, float]] = {}
        self._outline: type = CameraOutline
        self.wireframe_enabled: bool = False

        self.new_ids: set[str] = set()  # Draw the new camera's in color: CYAN

    @property
    def actors(self) -> list[vtk.vtkActor]:
        return list(self.glyphs.keys())

    def add_to(self, renderer: vtk.vtkRenderer):
        for actor in self.glyphs:
            renderer.AddActor(actor)

    def remove_from(self, renderer: vtk.vtkRenderer):
        for actor in self.glyphs:
            renderer.RemoveActor(actor)

        self.glyphs.clear()

    def set_visible(self, visible: bool):
        self._visible = visible
        self._refresh()

    def adopt_display(self, other: CameraGlyphs):
        """Take on how another set was being shown, when replacing it.

        A plan that grows is drawn by a whole new set of frustums, built from
        scratch and so wearing the defaults. Anything the user had said about
        how they are drawn - solid or wireframe, on or off - belongs to the
        viewer rather than to the plan, and would otherwise be thrown away
        with the set that was told it. Colours are not carried: the route
        repaints them itself the moment the plan changes.
        """
        self._visible = other._visible
        self._active = other._active
        self.wireframe_enabled = other.wireframe_enabled
        self._refresh()

    def set_active(self, index: int | None):
        """Track which frustum the viewer is sitting inside."""
        self._active = index
        self._refresh()

    def set_selected(self, index: int | None):
        """Mark the camera the user has picked; None when nothing is picked."""
        self._selected = index
        self._refresh()

    def set_observer_colours(self, colours: dict[int, tuple[float, float, float]] | None):
        """Paint the observers of the picked target; None when no target is up."""
        self._observers = dict(colours or {})
        self._refresh()

    def set_route(self, selected: set[int] | None, shown: set[str] | None = None):
        """Paint the route: blue for in, dimmed for out.

        Pass None to give every frustum its own colours back, which is what
        happens the moment route planning stops.

        `shown` is the plan ids a loaded file named. Every camera in the scene
        whose id is not one of them is switched off rather than dimmed, so the
        scene holds that plan and nothing else. None, the usual case, draws
        every viewpoint the plan has.
        """
        self._route = None if selected is None else set(selected)
        self._shown = None if shown is None else set(shown)
        self._refresh()

    def set_new_cameras(self, ids: set[str] | None):
        """Place the given IDs in the set for the new camera IDs"""
        if ids is None:
            self.new_ids = set()  # Empty set
            return
        self.new_ids = set(ids)

    def show_only(self, ids: set[str] | None):
        """Switch off every camera the given plan ids do not name."""
        self._shown = None if ids is None else set(ids)
        self._refresh()

    def camera_id_of_actor(self, actor: vtk.vtkActor) -> int | None:
        return self.glyphs.get(actor)

    def actor_of_id(self, camera_id: int) -> vtk.vtkActor | None:
        for actor, i in self.glyphs.items():
            if i == camera_id:
                return actor
        return None

    @staticmethod
    def _build(polydata: vtk.vtkPolyData):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(2.0)

        return actor

    def _refresh(self):
        for actor, id in self.glyphs.items():
            # Every camera in the scene, one at a time: it is drawn only if
            # the glyphs are on at all, it is not the frustum you are sitting
            # inside (that one fills the view), and, when a plan has been
            # loaded, that plan names its id.
            actor.SetVisibility(
                self._visible
                and id != self._active
                and (self._shown is None or self.ids[id] in self._shown)
            )

            # Wireframe vs Surface mode
            if id == self._selected or id in self._observers:
                self.set_frustrum_representation(actor, "Observer")
            else:
                self.set_frustrum_representation(actor, "none")

            mapper = actor.GetMapper()
            colour = self._colour_of(id)

            if colour is None:
                # The glyph carries its own vertex colours; let them through.
                mapper.ScalarVisibilityOn()
                actor.GetProperty().SetColor(1.0, 1.0, 1.0)
                continue

            mapper.ScalarVisibilityOff()
            actor.GetProperty().SetColor(*colour)

    def _colour_of(self, id: int) -> tuple[float, float, float] | None:
        """What one frustum wears, strongest claim first, or None for its own colours.

        Every colour a glyph can wear is decided here, from state, and applied
        by a full _refresh. Nothing paints a glyph on its own: a colour that is
        set directly is a colour nothing knows how to take off again, which is
        how a camera used to keep the selection gold after the selection had
        moved on.
        """
        if id == self._selected:
            return self.COLOUR_ACTIVE

        if id in self._observers:
            return self._observers[id]

        # if self.ids[id] in self.new_ids: # check if string ID is in new set
        #     return self.COLOUR_NEW

        if self._route is not None:
            return ROUTE_SELECTED_COLOUR if id in self._route else ROUTE_UNSELECTED_COLOUR

        if self.ids[id] in self.new_ids:  # check if string ID is in new set
            return self.COLOUR_NEW

        return None

    def set_frustrum_representation(self, actor: vtk.vtkActor, mode: str):
        """Set a frustrum's representation to surface or wireframe, based on their 'mode'.
        If that actor is an observer -> surface/filled representation.
        Otherwise, if not an observer -> wireframe representation.

        The two representations carry their own opacity rather than sharing
        one. A faint wireframe is still a clear outline; a fill that faint is
        a smudge, so the solid frustums are drawn much more strongly. What a
        wireframe looks like is unchanged.
        """
        if mode == "Observer":
            actor.GetProperty().SetRepresentationToSurface()
            actor.GetProperty().SetOpacity(1.0)
        elif self.wireframe_enabled:
            actor.GetProperty().SetOpacity(GLYPH_WIREFRAME_OPACITY)
            actor.GetProperty().SetRepresentationToWireframe()
        else:
            actor.GetProperty().SetOpacity(GLYPH_SOLID_OPACITY)
            actor.GetProperty().SetRepresentationToSurface()
