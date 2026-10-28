"""The 3D viewport: a render window plus the views drawn into it."""

from __future__ import annotations

from contextlib import contextmanager
from typing import cast

import numpy as np
import vtk
from PySide6.QtCore import QElapsedTimer, QPoint, QPointF, Qt, QTimer, Signal
from PySide6.QtGui import QCursor, QMouseEvent, QWheelEvent
from vtkmodules.qt.QVTKRenderWindowInteractor import (
    QVTKRenderWindowInteractor,
)
from vtkmodules.vtkInteractionWidgets import (
    vtkCameraOrientationRepresentation,
    vtkCameraOrientationWidget,
)

import viewscope.qt  # noqa: F401
import viewscope_core as vc
from viewscope.camera import CameraInfo
from viewscope.config import (
    BACKGROUND,
    MODE_ALL,
    MODE_GEOMETRY,
    MODE_TARGETS,
    MODE_TEXTURED,
    PICK_DRAG_SLOP_PX,
    PICK_TARGET_RADIUS_PX,
    YFOV_DEG,
    OverlayOptions,
)
from viewscope.data import SCENE_STORE, SceneData
from viewscope.scene import (
    CameraMode,
    FieldStats,
    FlightPathLine,
    MeshView,
    PhotoMesh,
    SceneCameraController,
    StillRenderer,
    TargetCloudView,
    TargetOverlay,
    TargetReport,
    UnobservedTargets,
    observer_colour,
    transform,
    weight_lut,
)
from viewscope.scene.gizmos import (
    CameraGlyphs,
    CameraModeGizmo,
    CameraOutline,
    FloorGrid,
    TranslationGizmo,
)


class Viewport(QVTKRenderWindowInteractor):
    """
    Renders a bundle and exposes display state as plain method calls.

    Emits `camera_changed` with a CameraInfo, or None for the overview, so
    panels can follow along without reaching into the renderer.
    """

    # Swallow residual noise from the cursor warp during manipulation
    _WARP_ECHO_EPSILON: float = 2.0  # px
    _ZOOM_NOTCH_SENSITIVITY: float = 20
    _CAMERA_MODE_TRANSITION_DURATION_MS: float = 500.0

    camera_changed = Signal(CameraInfo)
    camera_picked = Signal(int)

    # A camera has been placed by clicking: where it stands, and the point
    # on the model it was aimed at.
    camera_placed = Signal(object, object)
    # How far placing a camera has got: 0 asks for the standpoint, 1 for
    # what it looks at, and -1 means placing has finished or been dropped.
    placing_changed = Signal(int)

    # A surface target was clicked, by its row in the target cloud.
    target_picked = Signal(int)

    # A click landed on nothing, so whatever was picked should be let go.
    target_cleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(*BACKGROUND)
        self.GetRenderWindow().AddRenderer(self.renderer)

        self._interactor = self.GetRenderWindow().GetInteractor()
        self._interactor.SetInteractorStyle(vtk.vtkInteractorStyleUser())

        # self._mouse_picker = vtk.vtkPropPicker()
        self._mouse_picker = vtk.vtkCellPicker()
        # self._mouse_picker.SetTolerance(0.0)
        self._mouse_picker.PickFromListOn()

        # Targets are picked off the surface they sit on, so a click never
        # reaches a target on the far side of the model. With the mesh hidden
        # there is nothing to hide behind, and the cloud is picked directly.
        self._surface_picker = vtk.vtkCellPicker()
        self._surface_picker.PickFromListOn()
        self._point_picker = vtk.vtkPointPicker()
        self._point_picker.PickFromListOn()

        self.mesh = None
        self.cloud = None
        self.glyphs = None
        self.camera = None

        self._targets = None
        self._overlay = TargetOverlay()
        self._still = StillRenderer()

        # The bundle's own mesh, kept when the full-resolution model takes
        # its place on screen. `mesh` is whichever is being drawn.
        self._simple_mesh = None
        self._photo_mesh = None

        # The same table the overlay's rays and scalar bar read, so a camera
        # glyph and the ray out to it land on one colour.
        self._weight_lut = weight_lut()
        self._mode = MODE_ALL

        self._camera_mode = CameraMode.LOOK_AT
        self._render_mode = MODE_ALL
        self._mouse_locked = False
        self._mouse_lock_global_pos = QPoint()
        self._mouse_virtual_local_pos = QPointF()

        # Where the gesture started, and how far it has travelled since. A
        # left click that never travels is a pick; one that does is the user
        # swinging the view around, and picks nothing.
        self._press_position = QPointF()
        self._picked_glyph = False
        self._drag_px = 0.0

        self.selected_outline = CameraOutline()
        self.selected_camera_pos = (0, 0, 0)

        # Nesting depth of held(): while it is above nought, render() only
        # notes that a draw is owed.
        self._held = 0

        # Where a camera being placed by clicking will stand, once the
        # first click has said. None while nothing is being placed.
        self._placing = False
        self._standpoint = None

        self.flight_path = FlightPathLine()
        self.unobserved = UnobservedTargets()
        # While the targets nothing can see are flagged, they are the only
        # ones drawn, so the cloud they were picked out of comes off.
        self._flagging_unobserved = False

        # Camera Orientation Widget configuration
        self.orientation_widget = vtkCameraOrientationWidget()
        self.orientation_widget.SetParentRenderer(self.renderer)
        self.orientation_widget.AddObserver(
            vtk.vtkCommand.InteractionEvent, self._on_camera_moved_external
        )
        self.orientation_widget.AddObserver(
            vtk.vtkCommand.EndInteractionEvent, self._on_camera_moved_external
        )

        # Representation - the widget that's drawn in render window
        representation = cast(
            vtkCameraOrientationRepresentation,
            self.orientation_widget.GetRepresentation(),
        )
        representation.AnchorToUpperLeft()

        self.set_camera_orientation_visible(True)

        self.translation_gizmo = TranslationGizmo(self.renderer)

        # CameraMode gizmo configuration
        self.camera_mode_gizmo = CameraModeGizmo(self)
        self.camera_mode_gizmo.mode_changed.connect(self.set_scene_camera_mode)
        self.camera_mode_gizmo.raise_()

        # Animates the LOOK_AT camera into place after leaving TRACKBALL mode,
        # rather than snapping to stale orbit state on the next interaction.
        self._mode_transition_timer = QTimer(self)
        self._mode_transition_timer.setInterval(16)  # Assuming ~60fps
        self._mode_transition_timer.timeout.connect(self._on_camera_mode_transition_tick)
        self._mode_transition_elapsed = QElapsedTimer()
        self._mode_transition_start = None

        self._finalized = False  # See shutdown()

        # FloorGrid configuration. set_scene moves it onto the ground of
        # whichever bundle is loaded, so this is only where it starts.
        self.grid_origin_point = (0.0, 0.0, 0.0)
        self.floor_grid = FloorGrid(self.renderer, 100, self.grid_origin_point)

    # -- Lifecycle -----------------------------------------------------

    def start(self):
        """Call once the window is on screen."""
        self._interactor.Initialize()

    def shutdown(self):
        """
        Release the GL context explicitly; skipping this crashes on macOS.

        Runs at most once: closing the window and later destroying it would
        otherwise finalize the same render window twice, which frees the same
        pointer twice.
        """
        if self._finalized:
            return

        self._finalized = True
        self._still.close()
        self.Finalize()

    def render(self):
        if self._held:
            return

        self.GetRenderWindow().Render()

    @contextmanager
    def held(self):
        """Draw once at the end of a change, rather than after every part of it.

        Each thing the viewport is told draws the scene again, which is right
        for one change and wasteful for a dozen. Route planning makes a dozen
        on every click - the glyph colours, the flight path, the flagged
        targets, the heat map, the occlusion - and a draw of this scene costs
        more than all of them put together.
        """
        self._held += 1
        try:
            yield
        finally:
            self._held -= 1
            if not self._held:
                self.render()

    # -- Scene ---------------------------------------------------------

    def set_scene(self, data: SceneData):
        self.mesh = MeshView(data.mesh)
        self._simple_mesh = self.mesh
        self._photo_mesh = None

        self.cloud = TargetCloudView(data.targets, data.scores)

        for view in (self.mesh, self.cloud):
            view.add_to(self.renderer)

        self._rebuild_glyphs(data.plan)
        if self.glyphs:
            self.glyphs.set_new_cameras(SCENE_STORE.new_camera_ids)

        self._targets = np.asarray(data.targets, dtype=np.float64)
        self._surface_picker.AddPickList(self.mesh.actor)
        self._point_picker.AddPickList(self.cloud.actor)
        self._mouse_picker.AddPickList(self.mesh.actor)

        # NOTE(Adam): This is already done in _rebuild_glyphs(), so lets not do it again
        # for glyph_actor in self.glyphs.actors:
        #     self._mouse_picker.AddPickList(glyph_actor)

        self.grid_origin_point = self._ground_centre(data)
        self.floor_grid.move_to(self.grid_origin_point)

        self.camera = SceneCameraController(self.renderer, YFOV_DEG)
        self.renderer.ResetCamera()
        self.camera.save_overview()
        self.set_render_mode(self._render_mode)

    @staticmethod
    def _ground_centre(data: SceneData) -> tuple:
        """The middle of the scene's footprint, at its lowest point."""
        low, high = data.mesh.bounds
        return (float((low[0] + high[0]) / 2), float((low[1] + high[1]) / 2), float(low[2]))

    @property
    def has_scene(self) -> bool:
        return self.mesh is not None

    # -- Display state -------------------------------------------------

    def set_render_mode(self, mode: str):
        if self._render_mode == mode:
            return

        if not self.has_scene:
            return

        self._render_mode = mode
        self._apply_render_mode()

    def _apply_render_mode(self):
        """
        Dress whichever mesh is on screen in the current mode.
        Separate from set_render_mode because the mode outlives the mesh: the
        full-resolution model arrives seconds after the scene does, and has to
        come up wearing what the simplified one was wearing.
        """
        mode = self._render_mode

        if self.mesh is not None:
            self.mesh.set_visible(self._mesh_visible)

            if mode == MODE_GEOMETRY:
                self.mesh.show_geometry()
            elif self._mesh_visible:
                self.mesh.show_textured()

        self._apply_cloud_visibility()

        self.render()

    def _apply_cloud_visibility(self):
        """Show the targets the mode and the flagging between them call for.

        Two things have a say. The render mode decides whether targets are
        drawn at all - a mode showing only the mesh draws neither the cloud
        nor the flags, which would otherwise be points hanging in front of it
        with nothing to belong to. Flagging then decides which of them: the
        ones nothing can see, or all of them.
        """
        if self.cloud is None:
            return

        showing_targets = self._render_mode in (MODE_TARGETS, MODE_ALL)

        self.cloud.set_visible(showing_targets and not self._flagging_unobserved)
        self.unobserved.set_visible(showing_targets)

    @property
    def _mesh_visible(self) -> bool:
        """
        Whether the current mode draws the mesh at all.

        The surface ray reads this rather than an actor: with the mesh
        switched off there is nothing for a click to land on, and the cloud
        is picked directly, which is the behaviour whichever mesh is loaded.
        """
        return self._render_mode in (MODE_TEXTURED, MODE_GEOMETRY, MODE_ALL)

    def set_photo_mesh(self, photo: PhotoMesh):
        """
        Draw the full-resolution textured model in place of the simplified one.
        Only what is drawn changes. Targets are still picked against the
        simplified geometry, the cloud and the glyphs are untouched, and the
        camera does not move: the two meshes are in the same frame.
        """
        if not self.has_scene:
            return

        if self.mesh is not None:
            self.mesh.remove_from(self.renderer)

        self._photo_mesh = photo
        self.mesh = photo
        photo.add_to(self.renderer)
        self._apply_render_mode()

    def set_scalar_field(self, field: str) -> FieldStats | None:
        """Returns FieldStats, or None when the bundle has no scores."""
        if not self.has_scene:
            return None

        stats = None
        if self.cloud is not None:
            stats = self.cloud.set_field(field)

        self.render()
        return stats

    def set_scalar_values(self, field: str, values, value_range) -> FieldStats | None:
        """Colour the cloud by values worked out here, on a scale held fixed."""
        if not self.has_scene or self.cloud is None:
            return None

        stats = self.cloud.set_values(field, values, value_range)
        self.render()

        return stats

    def set_point_size(self, size: int):
        if self.has_scene and self.cloud is not None:
            self.cloud.set_point_size(size)
            # The flags sit on the cloud, so they grow with it.
            self.unobserved.set_point_size(size)
            self.render()

    # -- placing a camera by clicking ----------------------------------

    @property
    def placing(self) -> bool:
        """Whether clicks are being read as placing a camera rather than picking."""
        return self._placing

    def begin_placement(self):
        """Take the next two clicks on the model as a camera and what it faces."""
        if not self.has_scene:
            return

        self._placing = True
        self._standpoint = None
        self.placing_changed.emit(0)

    def cancel_placement(self):
        """Give the clicks back to picking, placing nothing."""
        if not self._placing:
            return

        self._placing = False
        self._standpoint = None
        self.placing_changed.emit(-1)

    def _place_click(self, position: QPointF) -> bool:
        """One click of a placement. Returns whether it landed on the model.

        The first says where the camera stands, the second what it looks at.
        A click that misses the model is not a point in space - a ray through
        empty air has no depth to it - so it counts for nothing and the step
        is asked for again.
        """
        landed = self._surface_under(position)
        if landed is None:
            return False

        point, normal = landed

        if self._standpoint is None:
            # Out along the surface it was clicked on, so the camera stands
            # off the model rather than buried in it, at the distance the
            # scoring likes best.
            self._standpoint = point + normal * vc.constants.MU_RHO_M
            self.placing_changed.emit(1)

            return True

        standpoint, self._standpoint = self._standpoint, None
        self._placing = False
        self.placing_changed.emit(-1)
        self.camera_placed.emit(standpoint, point)

        return True

    def _surface_under(self, position: QPointF):
        """Where on the model a click landed, and which way the model faces there."""
        x, y = self._display_position(position)
        self._surface_picker.Pick(x, y, 0, self.renderer)
        if self._surface_picker.GetActor() is None:
            return None

        point = np.asarray(self._surface_picker.GetPickPosition(), dtype=np.float64)
        normal = np.asarray(self._surface_picker.GetPickNormal(), dtype=np.float64)

        length = float(np.linalg.norm(normal))
        if not np.isfinite(length) or length < 1e-9:
            # A degenerate face has no outward direction to stand off along,
            # so the camera goes straight up instead of nowhere at all.
            normal = np.array([0.0, 0.0, 1.0])
        else:
            normal = normal / length

        return point, normal

    def show_unobserved(self, targets):
        """Draw these targets - the ones nothing can see - and only these.

        The rest of the cloud comes off while they are up. Picking a handful
        of points out of sixty thousand by colour alone is hard however they
        are coloured, and what is being looked for is where the gaps are:
        with everything else gone, what is left on screen is the answer.
        """
        if not self.has_scene:
            return

        self._flagging_unobserved = True
        self.unobserved.show(self.renderer, targets)
        self._apply_cloud_visibility()
        self.render()

    def clear_unobserved(self):
        """Take the flags off and give the rest of the targets back."""
        self._flagging_unobserved = False
        self.unobserved.remove_from(self.renderer)
        self._apply_cloud_visibility()
        self.render()

    def set_glyphs_visible(self, visible: bool):
        if self.has_scene and self.glyphs is not None:
            self.glyphs.set_visible(visible)
            self.render()

    def set_occlusion_mask(self, mask):
        """Paint the targets one camera can see; None restores the field colours."""
        if self.has_scene and self.cloud is not None:
            self.cloud.set_occlusion(mask)
            self.render()

    def set_route_selection(self, selected: set[int] | None):
        """Paint the route on the camera glyphs; None gives their colours back."""
        if self.has_scene and self.glyphs is not None:
            self.glyphs.set_route(selected)
            self.render()

    def show_flight_path(self, positions):
        """Draw the red line through these viewpoints, in this order."""
        if not self.has_scene:
            return

        self.flight_path.show(self.renderer, positions)
        self.render()

    def clear_flight_path(self):
        """Take the flight path off the scene."""
        self.flight_path.remove_from(self.renderer)
        self.render()

    # -- Target inspection ---------------------------------------------

    def show_target_overlay(
        self,
        report: TargetReport,
        camera_positions,
        diagonal: float,
        options: OverlayOptions,
    ):
        """Draw the picked target's sector rose and the rays out to its observers."""
        if not self.has_scene:
            return

        self._overlay.show(self.renderer, report, camera_positions, diagonal, options)
        self._colour_observers(report, options.colour_by)
        self.render()

    def clear_target_overlay(self):
        """Take the target overlay down, leaving the rest of the scene alone."""
        # INVARIANT: The glyphs cannot be uninitialized at this stage!
        assert self.glyphs is not None

        self._overlay.clear()
        self.glyphs.set_observer_colours(None)
        self.render()

    def set_grid_visible(self, visible: bool):
        """Show/Hide the floor grid."""
        # self.grid_visible = visible
        if self.has_scene and self.floor_grid is not None:
            # TODO(Azaam): Enable the segment, when resuming Grid optimization
            # if self.grid_visible:
            #     self.floor_grid.remove_from(self.renderer)
            #     self.floor_grid = FloorGrid(
            #         self.renderer, 100, self.grid_origin_point, self.grid_scale
            #     )
            # else:
            #     self.floor_grid.set_visible(visible)
            self.floor_grid.set_visible(visible)
            self.render()

    # -- Camera --------------------------------------------------------

    def show_overview(self):
        if self.has_scene and self.camera is not None:
            self._moved(self.camera.show_overview())

    def on_camera_changed(self, info: CameraInfo | None):
        """Update the highlighted camera. Change its colour to Gold, build outline around it."""
        # INVARIANT: The glyphs should not be uninitialized at this stage!
        assert self.glyphs is not None

        self.glyphs.set_selected(None if info is None else info.index)
        self.selected_outline.remove_from(self.renderer)

        if info is not None:
            self.set_selected_camera_position(info)

            if self.selected_camera_pos != (0, 0, 0):
                self.selected_outline.build(self.renderer, self.selected_camera_pos)

                actor = self.glyphs.actor_of_id(info.index)
                if actor is not None:
                    self.translation_gizmo.attach(
                        actor,
                        heading_deg=info.yaw,
                        on_move=lambda pos, idx=info.index: SCENE_STORE.move_camera(
                            idx, tuple(pos.tolist())
                        ),
                    )
        else:
            self.translation_gizmo.detach()

        self.render()

    def on_plan_changed(self):
        """Rebuild the camera glyphs for the current plan."""
        if SCENE_STORE.scene is None:
            return

        # NOTE(Adam): The only renderer objects that need to be fully rebuilt
        #             when the plan changes are the camera glyphs. The mesh and
        #             cloud are unaffected by the plan.
        self._rebuild_glyphs(SCENE_STORE.scene.plan)
        if self.glyphs:
            self.glyphs.set_new_cameras(SCENE_STORE.new_camera_ids)

        self.render()

    def _rebuild_glyphs(self, plan: vc.Plan):
        """
        Put one frustum per viewpoint in the scene, and only one.

        The old actors come off the renderer first. Both the scene load and a
        plan change come through here, and they overlap: the store announces
        the plan before set_scene runs, so a set of glyphs is already in the
        renderer by the time the scene arrives. Left there, that set is drawn
        for the life of the window while every route colour and every
        visibility switch lands on the set that replaced it.
        """
        previous = self.glyphs
        if previous is not None:
            for glyph_actor in previous.actors:
                self._mouse_picker.DeletePickList(glyph_actor)

            previous.remove_from(self.renderer)

        self.glyphs = CameraGlyphs(plan)
        if previous is not None:
            # A new set starts on the defaults, which would quietly undo the
            # display panel every time a camera was added.
            self.glyphs.adopt_display(previous)

        self.glyphs.add_to(self.renderer)

        for glyph_actor in self.glyphs.actors:
            self._mouse_picker.AddPickList(glyph_actor)

    def set_selected_camera_position(self, info: CameraInfo | None):
        if info is not None:
            self.selected_camera_pos = (
                float(info.position[0]),
                float(info.position[1]),
                float(info.position[2]),
            )

    def set_camera_orientation_visible(self, visible: bool):
        if visible:
            self.orientation_widget.On()
        else:
            self.orientation_widget.Off()

        self.render()

    def toggle_camera_orientation_visible(self):
        current_visibility = self.orientation_widget.GetEnabled()
        self.set_camera_orientation_visible(not current_visibility)

    def set_scene_camera_mode(self, mode: CameraMode):
        # INVARIANT: Camera cannot be null!
        assert self.camera is not None

        if mode == self._camera_mode:
            return

        prev_mode = self._camera_mode
        self._camera_mode = mode

        if self._camera_mode is CameraMode.TRACKBALL:
            self._cancel_camera_mode_transition()
            self._interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        else:
            self._interactor.SetInteractorStyle(vtk.vtkInteractorStyleUser())
            if prev_mode is CameraMode.TRACKBALL:
                self._begin_camera_mode_transition()

        self.camera_mode_gizmo.set_current_mode(mode)
        self.render()

    def render_still(self, width: int | None = None, height: int | None = None):
        """
        A pyrender image of the shot the viewport is holding.
        The same pose the window is drawing, rendered offscreen by pyrender
        and handed back as pixels: height x width x 3 uint8, or None when
        there is no scene to shoot. Sized to the window unless asked
        otherwise, so what comes back is what is on screen.
        """
        scene = SCENE_STORE.scene
        if scene is None or scene.mesh is None:
            return None

        if width is None or height is None:
            width, height = self.GetRenderWindow().GetSize()

        # Off the live camera rather than the plan: free-look is a shot too,
        # and the view angle is the one the user is looking through.
        camera = self.renderer.GetActiveCamera()
        pose = transform.pose_from_camera(camera)

        return self._still.render(scene.mesh, pose, width, height, camera.GetViewAngle())

    def _moved(self, info: CameraInfo | None):
        if self.glyphs is not None:
            self.glyphs.set_active(None if info is None else info.index)

        self.camera_changed.emit(info)
        self.render()

    def _begin_camera_mode_transition(self):
        """
        Animate from wherever trackball left the camera into the nearest
        pose the look-at model can represent (same position/pivot, roll
        discarded), instead of snapping there on the next orbit/pan/dolly.
        """
        # INVARIANT: Camera cannot be null!
        assert self.camera is not None

        self._mode_transition_start = self.camera.begin_transition_to_orbit()
        self._mode_transition_elapsed.restart()
        self._mode_transition_timer.start()

    def _cancel_camera_mode_transition(self):
        if self._mode_transition_timer.isActive():
            self._mode_transition_timer.stop()
            self._mode_transition_start = None

    def _on_camera_moved_external(self, obj=None, event=None):
        """
        Resync SceneCameraController after something outside it (the
        orientation widget, a planned-viewpoint jump, etc.) moves the VTK
        camera directly.
        """
        # INVARIANT: Camera cannot be null!
        assert self.camera is not None

        self.camera.sync_from_camera()
        self.render()

    def _on_camera_mode_transition_tick(self):
        """Lerp the transition animation."""
        # INVARIANT: Camera cannot be null!
        assert self.camera is not None

        if self._mode_transition_start is None:
            self._mode_transition_timer.stop()
            return

        t = self._mode_transition_elapsed.elapsed() / self._CAMERA_MODE_TRANSITION_DURATION_MS
        if t >= 1.0:
            self.camera.finish_transition()
            self._mode_transition_timer.stop()
            self._mode_transition_start = None
        else:
            self.camera.apply_transition(self._mode_transition_start, self._smoothstep(t))

        self.render()

    @staticmethod
    def _smoothstep(t: float) -> float:
        return t * t * (3.0 - 2.0 * t)

    # -- Mouse --------------------------------------------------------

    def mousePressEvent(self, ev: QMouseEvent):
        """
        Lock mouse on Right Click, Left Click & Middle Click, and handle mouse-picking dispatch.
        """
        # Where the gesture started, and how far it has travelled since. A
        # left click that never travels is a pick; one that does is the user
        # swinging the view around, and picks nothing.
        self._press_position = ev.position()
        self._drag_px = 0.0
        self._picked_glyph = False

        if ev.button() == Qt.MouseButton.LeftButton:
            x, y = self._display_position(ev.position())
            if self.translation_gizmo.try_start_drag(x, y):
                super().mousePressEvent(ev)
                return
            if self._pick_camera_glyph(ev):
                self._picked_glyph = True
                super().mousePressEvent(ev)
                return

        # if (ev.button() in (...) and not self._mouse_locked):
        #     self._mouse_lock_enter(ev)
        # super().mousePressEvent(ev)

        # NOTE(Adam): Early-return here handles camera-click vs viewport manip on left-click
        if (
            ev.button() == Qt.MouseButton.LeftButton
            and not self._placing
            and self._pick_camera_glyph(ev)
        ):
            self._picked_glyph = True
            super().mousePressEvent(ev)
            return

        if (
            ev.button()
            in (Qt.MouseButton.RightButton, Qt.MouseButton.LeftButton, Qt.MouseButton.MiddleButton)
            and not self._mouse_locked
        ):
            self._mouse_lock_enter(ev)

        super().mousePressEvent(ev)

    def mouseReleaseEvent(self, ev: QMouseEvent):
        """Unlock the mouse when all tracked mouse buttons have been released."""

        if self.translation_gizmo.active:
            self.translation_gizmo.end_drag()
            return
        #         super().mouseReleaseEvent(ev)
        super().mouseReleaseEvent(ev)

        if self._mouse_locked and not (
            ev.buttons()
            & (Qt.MouseButton.LeftButton | Qt.MouseButton.RightButton | Qt.MouseButton.MiddleButton)
        ):
            self._mouse_lock_exit()

        if (
            ev.button() == Qt.MouseButton.LeftButton
            and not self._picked_glyph
            and self._drag_px <= PICK_DRAG_SLOP_PX
        ):
            # Placing a camera takes the clicks that would otherwise pick a
            # target. Dragging still swings the view, so the model can be
            # turned around between the two clicks.
            if self._placing:
                self._place_click(self._press_position)
            else:
                self._pick_target(self._press_position)

    def mouseMoveEvent(self, ev: QMouseEvent):
        """
        Handle mouse movements during viewport manipulation when the mouse is locked.

        When the mouse is locked during active interaction (e.g., panning or rotating),
        this method intercepts the OS move event to accumulate virtual positional deltas
        and forwards synthetic events to VTK's interactor style. The physical OS cursor
        is reset back to its initial anchor position to allow infinite range-of-motion
        without running off-screen.
        """
        if self.translation_gizmo.active:
            x, y = self._display_position(ev.position())
            self.translation_gizmo.drag(x, y)
            self.render()
            return
        if not self._mouse_locked:
            super().mouseMoveEvent(ev)
            return

        anchor = QPointF(self._mouse_lock_global_pos)
        current_global = ev.globalPosition()
        delta = current_global - anchor

        # Swallow the warp's own echo (and any sub-pixel OS noise) without
        # discarding a whole event; real motion merged into a compressed
        # event still gets through, so nothing gets batched/skipped.
        if (abs(delta.x()) <= self._WARP_ECHO_EPSILON) and (
            abs(delta.y()) <= self._WARP_ECHO_EPSILON
        ):
            return

        # How far the gesture has travelled, past the warp echo: what tells a
        # click meant as a pick from one meant to swing the view around.
        self._drag_px += abs(delta.x()) + abs(delta.y())

        # Accumulate relative delta onto virtual local position
        self._mouse_virtual_local_pos += delta

        # Synthesize event with accumulated position so VTK trackball moves smoothly
        fake_ev = QMouseEvent(
            ev.type(),
            self._mouse_virtual_local_pos,
            ev.globalPosition(),
            ev.button(),
            ev.buttons(),
            ev.modifiers(),
        )

        QCursor.setPos(self._mouse_lock_global_pos)
        super().mouseMoveEvent(fake_ev)

        if self.camera is not None and self._camera_mode is CameraMode.LOOK_AT:
            if ev.buttons() & Qt.MouseButton.LeftButton:
                self.camera.orbit(delta.x(), delta.y())
            elif ev.buttons() & Qt.MouseButton.MiddleButton:
                self.camera.pan(delta.x(), delta.y())
            elif ev.buttons() & Qt.MouseButton.RightButton:
                self.camera.dolly(-delta.y())

            self.render()

    def wheelEvent(self, ev: QWheelEvent):
        if not self.has_scene or self.camera is None or self._camera_mode is not CameraMode.LOOK_AT:
            super().wheelEvent(ev)
            return

        # angleDelta().y() is in eighths of a degree; 120 == one notch on most mouses.
        scroll_notches = ev.angleDelta().y() / 120.0
        self.camera.dolly(scroll_notches * self._ZOOM_NOTCH_SENSITIVITY)
        self.render()

        ev.accept()

    def _mouse_lock_enter(self, ev: QMouseEvent):
        # INVARIANT: Camera cannot be null!
        assert self.camera is not None

        if self._mode_transition_timer.isActive():
            self.camera.finish_transition()
            self._cancel_camera_mode_transition()

        self._mouse_locked = True
        self._mouse_lock_global_pos = ev.globalPosition().toPoint()

        # Virtual position starts at real initial position and grows infinitely.
        # This position is kept as a float to avoid rounding jitter.
        self._mouse_virtual_local_pos = ev.position()
        self.HideCursor()

    def _mouse_lock_exit(self):
        self._mouse_locked = False

        # Restore cursor visibility and position
        self.ShowCursor()
        QCursor.setPos(self._mouse_lock_global_pos)

    def _pick_camera_glyph(self, ev: QMouseEvent) -> bool:
        """
        Selects the camera from the camera glyph hovered by the mouse cursor.
        Returns True if a camera was under the mouse and selected, False otherwise.
        """
        if self.glyphs is None:
            return False

        x, y = self._display_position(ev.position())
        self._mouse_picker.Pick(x, y, 0, self.renderer)

        actor = self._mouse_picker.GetActor()
        if actor is None:
            return False

        # NOTE(Adam): With the scene mesh added to the pick list,
        #       this will correctly return None when clicking on the mesh,
        #       therefore blocking glyph selections through the mesh.
        camera_id = self.glyphs.camera_id_of_actor(actor)
        if camera_id is None:
            return False

        print(f"Selected camera: {camera_id}")
        self.camera_picked.emit(camera_id)

        return True

    def _display_position(self, position: QPointF) -> tuple[int, int]:
        """A Qt widget position as the render window's own pixel coordinates."""
        # NOTE(Adam): Qt uses the top-left origin.
        #             VTK uses OpenGL coordinates - bottom-left origin.
        dpr = self.devicePixelRatioF()  # Handle window DPI scaling
        x = int(position.x() * dpr)
        y = self.GetRenderWindow().GetSize()[1] - int(position.y() * dpr) - 1

        return x, y

    def _pick_target(self, position: QPointF) -> bool:
        """
        Select the surface target under the cursor.

        Emits `target_picked` with its row in the cloud, or `target_cleared`
        when the click landed on nothing. Returns whether a target was found.
        """
        index = self._target_under(position)

        if index is None:
            self.target_cleared.emit()
            return False

        self.target_picked.emit(index)

        return True

    def _target_under(self, position: QPointF) -> int | None:
        if self._targets is None or not len(self._targets):
            return None

        x, y = self._display_position(position)

        # The mesh goes first, so a click only ever reaches what it can see.
        self._surface_picker.Pick(x, y, 0, self.renderer)
        if self._surface_picker.GetActor() is not None:
            return self._within_reach(
                self._nearest_target(self._surface_picker.GetPickPosition()), x, y
            )

        # No mesh under the cursor: either it is hidden, or the click missed
        # the model. Either way the cloud is all that is left to hit.
        self._point_picker.Pick(x, y, 0, self.renderer)
        if self._point_picker.GetActor() is None:
            return None

        point_id = int(self._point_picker.GetPointId())
        if 0 <= point_id < len(self._targets):
            return self._within_reach(point_id, x, y)

        return self._within_reach(self._nearest_target(self._point_picker.GetPickPosition()), x, y)

    def _nearest_target(self, world_position) -> int:
        """The target closest to a point on the surface."""
        # INVARIANT: Targets cannot be uninitialized at this stage!
        assert self._targets is not None

        offsets = self._targets - np.asarray(world_position, dtype=np.float64)
        return int(np.argmin(np.einsum("ij,ij->i", offsets, offsets)))

    def _within_reach(self, index: int, x: int, y: int) -> int | None:
        """
        The target, unless the click landed too far away to have meant it.

        Picking off the surface hands back whichever target is nearest the
        point that was hit, and on bare mesh the nearest one can be metres
        off. Held to a radius around the cursor, a click on nothing stays
        nothing, and the selection is let go instead of jumping.
        """
        # INVARIANT: Targets cannot be uninitialized at this stage!
        assert self._targets is not None

        target_x, target_y = self._display_of_world(self._targets[index])
        reach = PICK_TARGET_RADIUS_PX * self.devicePixelRatioF()

        if float(np.hypot(target_x - x, target_y - y)) > reach:
            return None

        return index

    def _display_of_world(self, world_position) -> tuple[float, float]:
        """A point in the scene as the render window's own pixel coordinates."""
        self.renderer.SetWorldPoint(
            float(world_position[0]), float(world_position[1]), float(world_position[2]), 1.0
        )
        self.renderer.WorldToDisplay()
        display_x, display_y, _ = self.renderer.GetDisplayPoint()

        return display_x, display_y

    def _colour_observers(self, report: TargetReport, colour_by: str):
        """Give every camera that sees the target the colour of its own ray.

        The ray says which camera made a sector strong; wearing the same
        colour, the frustum out in the scene says where that camera is
        without the eye having to follow the line back.
        """
        # INVARIANT: The glyphs cannot be uninitialized at this stage!
        assert self.glyphs is not None

        top_camera = None if report.top_observer is None else report.top_observer.camera_index
        self.glyphs.set_observer_colours(
            {
                observer.camera_index: observer_colour(
                    observer, colour_by, self._weight_lut, top_camera
                )
                for observer in report.observers
            }
        )

    def toggle_glyph_wireframe(self, enabled: bool):
        """Toggle between the solid and wireframe representation for CameraGlyph.
        Render scene as soon as bool updates."""
        # INVARIANT: The glyphs cannot be uninitialized at this stage!
        assert self.glyphs is not None

        self.glyphs.wireframe_enabled = enabled
        self.glyphs._refresh()
        self.render()

    # -- Window events ---------------------------------------------------

    def resizeEvent(self, ev):
        super().resizeEvent(ev)

        margin = 12
        self.camera_mode_gizmo.adjustSize()

        x = self.width() - self.camera_mode_gizmo.width() - margin
        y = margin

        self.camera_mode_gizmo.move(x, y)
        self.camera_mode_gizmo.raise_()
