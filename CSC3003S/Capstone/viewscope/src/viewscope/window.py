"""
The application shell: docks, actions, and the wiring between them.

This class deliberately holds no scene state. It routes panel signals into the
viewport and viewport signals back into the panels.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image
from PySide6.QtCore import QByteArray, QSettings, Qt, Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QStatusBar,
)

import viewscope_core as vc
from viewscope.camera import CameraInfo
from viewscope.camera_viewport import CameraViewport
from viewscope.config import APP_NAME, DATA_DIR, MODES, ORG_NAME, ROUTE_FILENAME
from viewscope.data import (
    SCENE_STORE,
    Obstacle,
    RoutePlan,
    SceneData,
    SceneLoader,
    load_route,
    plan_path,
)
from viewscope.dialogs import FileErrorDialog
from viewscope.panels import (
    DisplayPanel,
    MetricsPanel,
    PlanRoutePanel,
    TargetPanel,
    ViewpointsPanel,
)
from viewscope.route_report import write_report
from viewscope.scene import (
    PhotoMesh,
    PhotoMeshLoader,
    SubsetScores,
    TargetReport,
    TargetReports,
    TargetVisibility,
    find_photo_mesh,
)
from viewscope.viewport import Viewport


class MainWindow(QMainWindow):
    # Asked for the project list back. The startup screen is what answers it.
    back_requested = Signal()

    # The scene loader's own loaded signal has already fired by the time
    # the photo-mesh load starts, so we need to manually track these.
    photo_mesh_progress = Signal(str, int)  # (message, percent 0-100)
    photo_mesh_finished = Signal(bool)  # Whether a model was actually loaded

    def __init__(
        self,
        data_dir: Path = DATA_DIR,
        *,
        expected_viewpoints: int | None = None,
        defer_load: bool = False,
        load_photo_mesh: bool = True,
        full_resolution_mesh: bool = False,
    ):
        """
        Build the shell and, unless the load is deferred, start reading the bundle.

        expected_viewpoints is the plan size a shipped bundle is known to hold,
        checked while loading. Pass defer_load=True to leave the loader idle:
        the startup screen uses that to connect to its signals before the first
        one is emitted, then calls self.loader.start() itself.

        Pass load_photo_mesh=False to stay on the simplified mesh: the
        full-resolution model is the bulk of a bundle's memory, and the startup
        screen offers it as a choice for machines that cannot hold it.

        Pass full_resolution_mesh=True to read that model as it was shipped,
        with its textures at their own size and the disk cache untouched. It
        costs a good deal more memory, and every load pays the slow parse.
        """
        super().__init__()
        self.setWindowTitle("ViewScope")
        self.resize(1500, 950)

        self.viewport = Viewport(self)
        self.setCentralWidget(self.viewport)  # Set the cental widget vtk

        self.visibility = None  # TargetVisibility, once a scene is loaded
        self.reports = None  # TargetReports, likewise
        self.route = RoutePlan()

        # Whether the flight path is drawn. It follows the route while it is
        # up, so it is recomputed on every change rather than only on the
        # click that switched it on.
        self.flight_path_on = False

        # The model as space the path has to stay out of. Built on the first
        # path asked for and kept for the life of the scene.
        self.obstacle = None

        # Whether the targets nothing can see are flagged, and what the whole
        # plan can see between it - which is what "nothing" means outside
        # route planning. Counted once and kept, because it only moves when
        # the plan does.
        self.unobserved_on = False
        self.plan_mask = None

        # Rescores the targets for the cameras in the route, so the heat map
        # answers what the route covers rather than what the plan does. None
        # until a scene with a score table arrives.
        self.subset_scores = None

        # What the whole route can see, while planning is on. Recounted on
        # every route change, because both the coverage line and the
        # occlusion colouring read it.
        self.route_mask = None

        self.selected_camera = None
        self.selected_target: TargetReport | None = None
        self.occlusion_on = False

        # Reads the full-resolution model, once, for every panel that draws it.
        self.photo_loader = None
        self.load_photo_mesh = load_photo_mesh
        self.full_resolution_mesh = full_resolution_mesh

        self.camera_viewport = CameraViewport(self)
        self.display_panel = DisplayPanel()
        self.metrics_panel = MetricsPanel()
        self.viewpoints_panel = ViewpointsPanel()
        self.target_panel = TargetPanel()
        self.plan_route_panel = PlanRoutePanel()
        self.camera_viewport = CameraViewport(self)

        self.docks = {}
        self._add_dock("Viewpoints", self.viewpoints_panel, Qt.DockWidgetArea.LeftDockWidgetArea)
        self._add_dock("Target", self.target_panel, Qt.DockWidgetArea.LeftDockWidgetArea)
        self._add_dock("Plan Route", self.plan_route_panel, Qt.DockWidgetArea.LeftDockWidgetArea)
        self._add_dock("Display", self.display_panel, Qt.DockWidgetArea.RightDockWidgetArea)
        self._add_dock("Camera View", self.camera_viewport, Qt.DockWidgetArea.RightDockWidgetArea)
        self._add_dock("Metrics", self.metrics_panel, Qt.DockWidgetArea.RightDockWidgetArea)

        self._connect()
        self._build_actions()

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Loading...")

        # Snapshot the docks and toolbar as __init__ arranged them, before a
        # saved session overwrites them. This is what "Reset Layout" restores.
        self._default_state = self.saveState()
        self._restore_layout()

        # Load the scene
        self.loader = SceneLoader(data_dir, self, expected_viewpoints)
        self.loader.progress.connect(self.statusBar().showMessage)
        self.loader.loaded.connect(self._on_scene_loaded)
        self.loader.failed.connect(self._on_failed)
        self.loader.plan_validation_failed.connect(self.show_error_dialog)
        self.loader.filename_validation_failed.connect(self.show_error_dialog)

        if not defer_load:
            self.loader.start()

    def start(self):
        """Hand control to the VTK interactor, once the window is visible."""
        self.viewport.start()
        self.camera_viewport.start()

    # -- Construction --------------------------------------------------

    def _add_dock(self, title, widget, area):
        dock = QDockWidget(title, self)
        dock.setObjectName(f"dock_{title}")  # Required for saveState
        dock.setWidget(widget)
        dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.addDockWidget(area, dock)
        self.docks[title] = dock
        return dock

    def _connect(self):
        self.display_panel.mode_changed.connect(self.viewport.set_render_mode)
        self.display_panel.point_size_changed.connect(self.viewport.set_point_size)
        self.display_panel.field_changed.connect(self._on_field_changed)
        self.display_panel.field_changed.connect(self._on_field_changed)
        self.display_panel.occlusion_toggled.connect(self._on_occlusion_toggled)
        self.display_panel.grid_toggled.connect(self.viewport.set_grid_visible)
        self.display_panel.glyphs_toggled.connect(self.viewport.set_glyphs_visible)
        self.display_panel.glyph_wireframe_toggled.connect(self.viewport.toggle_glyph_wireframe)
        self.display_panel.unobserved_toggled.connect(self._on_unobserved_toggled)

        # This updates the camera in FPV viewport
        # TODO(Adam): In future, I would prefer if camera_picked
        #             returned a CameraInfo and was wired into self._on_camera_changed.
        self.viewpoints_panel.place_requested.connect(self.viewport.begin_placement)
        self.viewport.placing_changed.connect(self._on_placing_changed)
        self.viewport.camera_placed.connect(self._on_camera_placed)
        self.viewpoints_panel.camera_picked.connect(self.camera_viewport.show_camera)
        self.viewport.camera_picked.connect(self.camera_viewport.show_camera)
        self.viewport.camera_picked.connect(self.viewpoints_panel.select_row)

        # Picking a target in the 3D view fills the target panel in; the
        # panel's own controls only ever change what is drawn for it.
        self.viewport.target_picked.connect(self._on_target_picked)
        self.viewport.target_cleared.connect(self.clear_target)
        self.target_panel.sector_count_changed.connect(self._on_sector_count_changed)
        self.target_panel.overlay_changed.connect(self._refresh_target_overlay)
        self.target_panel.cleared.connect(self.clear_target)
        self.target_panel.camera_picked.connect(self.camera_viewport.show_camera)
        self.target_panel.camera_picked.connect(self.viewpoints_panel.select_row)

        # While planning is on, clicking a camera in the 3D view takes it out
        # of the route or puts it back.
        self.viewport.camera_picked.connect(self._on_route_camera_picked)
        self.plan_route_panel.plan_requested.connect(self.start_route_planning)
        self.plan_route_panel.stop_requested.connect(self.stop_route_planning)
        self.plan_route_panel.load_requested.connect(self.load_route_file)
        self.plan_route_panel.select_all_requested.connect(self._on_route_select_all)
        self.plan_route_panel.clear_requested.connect(self._on_route_clear)
        self.plan_route_panel.path_requested.connect(self._on_flight_path_toggled)
        self.plan_route_panel.report_requested.connect(self.generate_route_report)

        SCENE_STORE.plan_changed.connect(self._on_plan_changed)
        self.camera_viewport.camera_changed.connect(self._on_camera_changed)
        SCENE_STORE.camera_moved.connect(self.camera_viewport.on_camera_moved)

    def _build_actions(self):
        project_bar = self.addToolBar("Project")
        project_bar.setObjectName("toolbar_project")

        self.act_back = QAction("\u2190 Projects", self)
        self.act_back.setShortcut(QKeySequence("Ctrl+Shift+P"))
        self.act_back.setToolTip("Close this bundle and pick another (Ctrl+Shift+P)")
        self.act_back.triggered.connect(self.back_requested)
        project_bar.addAction(self.act_back)
        self.addAction(self.act_back)  # keeps the shortcut alive when VTK has focus

        project_menu = self.menuBar().addMenu("&Project")
        project_menu.addAction(self.act_back)

        toolbar = self.addToolBar("Cameras")
        toolbar.setObjectName("toolbar_cameras")

        self.act_prev = QAction("Previous", self)
        self.act_prev.setShortcuts([QKeySequence("P"), QKeySequence(Qt.Key.Key_Left)])

        # self.act_prev.triggered.connect(self.viewport.prev_camera)

        self.act_next = QAction("Next", self)
        self.act_next.setShortcuts([QKeySequence("N"), QKeySequence(Qt.Key.Key_Right)])

        # self.act_next.triggered.connect(self.viewport.next_camera)

        self.act_overview = QAction("Overview", self)
        self.act_overview.setShortcut(QKeySequence("O"))
        self.act_overview.triggered.connect(self.viewport.show_overview)

        self.act_clear_target = QAction("Clear Target", self)
        self.act_clear_target.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        self.act_clear_target.setToolTip(
            "Let go of the picked target, or stop placing a camera (Esc)"
        )
        self.act_clear_target.triggered.connect(self.clear_target)
        self.act_clear_target.setEnabled(False)

        self.act_still = QAction("Render Still", self)
        self.act_still.setShortcut(QKeySequence("Ctrl+R"))
        self.act_still.setToolTip("Save the camera view as a high-resolution image (Ctrl+R)")
        self.act_still.triggered.connect(self.render_still)

        self.toggle_orientation = QAction("Toggle Orientation", self, checkable=True)
        self.toggle_orientation.triggered.connect(self.viewport.toggle_camera_orientation_visible)
        self.toggle_orientation.setChecked(True)

        camera_actions = (
            self.act_prev,
            self.act_next,
            self.act_overview,
            self.act_clear_target,
            self.act_still,
            self.act_clear_target,
            self.toggle_orientation,
        )
        for act in camera_actions:
            toolbar.addAction(act)
            self.addAction(act)  # Keeps shortcuts alive when VTK has focus

        view_menu = self.menuBar().addMenu("&View")
        for dock in self.docks.values():
            view_menu.addAction(dock.toggleViewAction())

        view_menu.addSeparator()
        self.act_reset_layout = QAction("Reset Layout", self)
        self.act_reset_layout.triggered.connect(self.reset_layout)
        view_menu.addAction(self.act_reset_layout)

        camera_menu = self.menuBar().addMenu("&Camera")
        for act in camera_actions:
            camera_menu.addAction(act)

        # Number keys mirror the display combo box.
        for i, mode in enumerate(MODES, start=1):
            act = QAction(mode, self)
            act.setShortcut(QKeySequence(str(i)))
            act.triggered.connect(
                lambda _checked=False, m=mode: self.display_panel.mode.setCurrentText(m)
            )
            self.addAction(act)

        # -- camera ---

        self.act_prev.triggered.connect(self.camera_viewport.prev_camera)
        self.act_next.triggered.connect(self.camera_viewport.next_camera)
        self.act_overview.triggered.connect(self.camera_viewport.show_overview)

    # -- callbacks -----------------------------------------------------

    def _on_failed(self, message):
        self.statusBar().showMessage("Load failed")
        QMessageBox.critical(self, "ViewScope", f"Could not load the bundle.\n\n{message}")

    def _on_scene_loaded(self, scene: SceneData):
        SCENE_STORE.set_scene(scene)
        self.visibility = TargetVisibility(scene)
        self.reports = TargetReports(scene, self.visibility)
        # A new model is a new shape to fly around, and a new plan is a new
        # answer to what nothing can see.
        self.obstacle = None
        self.plan_mask = None
        # Another bundle's route.json is not this bundle's to overwrite.
        self.route.forget_file()
        self.subset_scores = (
            None
            if scene.scores is None
            else SubsetScores(scene.scores, len(scene.targets), len(scene.plan.ids))
        )

        self.viewport.set_scene(scene)
        self.camera_viewport.set_scene(scene)
        self.metrics_panel.show_bundle()

        if scene.has_scores:
            self._on_field_changed(self.display_panel.field.currentText())
        else:
            self.display_panel.disable_fields()
            self.metrics_panel.show_field(None)
            if scene.scores_error:
                print(f"scores unavailable: {scene.scores_error}")

        self._refresh_route()

        self.viewport.show_overview()
        self.camera_viewport.show_overview()
        self.statusBar().showMessage("Ready", 3000)

        if scene.data_dir is not None:
            self._load_photo_mesh(scene.data_dir)

    # -- placing a camera by clicking ----------------------------------

    def _on_placing_changed(self, step: int):
        """Say what the next click will do, or that there is nothing to click for."""
        # Escape is what stops it, and it shares the action that lets go of a
        # picked target, so that action has to be live while placing.
        self.act_clear_target.setEnabled(step >= 0 or self.selected_target is not None)

        if step == 0:
            self.statusBar().showMessage(
                "Placing a camera: click the model where it should stand. Escape to stop."
            )
        elif step == 1:
            self.statusBar().showMessage("Now click what it should look at. Escape to stop.")
        else:
            self.statusBar().clearMessage()

    def _on_camera_placed(self, standpoint, target):
        """Add the camera the user has just clicked out."""
        try:
            yaw, pitch = vc.look_at_angles(standpoint, target)
        except ValueError:
            # The two clicks landed on the same spot, so there is no direction
            # to face. Nothing is added and the user is told why.
            self.statusBar().showMessage(
                "Those two clicks are the same point, so there is nothing to face", 5000
            )
            return

        x, y, z = (float(v) for v in standpoint)
        SCENE_STORE.add_camera((x, y, z), yaw, pitch)

        position = f"{x:.1f}, {y:.1f}, {z:.1f}"
        self.statusBar().showMessage(
            f"Camera placed at {position}, facing {yaw:.0f} deg yaw, {pitch:.0f} deg pitch",
            6000,
        )

    def _on_field_changed(self, field):
        self.metrics_panel.show_field(self._paint_field(field))

    def _paint_field(self, field: str):
        """Colour the targets by one field, for the route or for the plan.

        While a route is being planned the heat map is worked out from the
        cameras in it, on the plan's own scale: an empty route leaves every
        target at the cold end, and each camera put back warms what it sees.
        Outside planning, and for anything the rescorer cannot answer, the
        column the bundle shipped is used as it always was.
        """
        if not self._rescoring(field):
            return self.viewport.set_scalar_field(field)

        assert self.subset_scores is not None  # _rescoring is the only route here

        return self.viewport.set_scalar_values(
            field,
            self.subset_scores.values(field, self.route.selected),
            self.subset_scores.full_range(field),
        )

    def _unscored(self, rows) -> int:
        """How many of these viewpoints the bundle's score table cannot credit."""
        if self.subset_scores is None:
            return 0

        return len(self.subset_scores.unscored(rows))

    def _rescoring(self, field: str) -> bool:
        """Whether the heat map should follow the route rather than the plan."""
        return (
            self.route.planning and self.subset_scores is not None and SubsetScores.handles(field)
        )

    def _refresh_heatmap(self):
        """Repaint the targets, for when the route or the plan moves under them."""
        if SCENE_STORE.scene is None or not self.display_panel.field.isEnabled():
            return

        self._on_field_changed(self.display_panel.field.currentText())

    def _on_camera_changed(self, info: CameraInfo | None):
        if SCENE_STORE.scene is None:
            return

        self.metrics_panel.show_camera(info)
        self.viewport.on_camera_changed(info)

        self.selected_camera = info
        if info is not None:
            self.viewpoints_panel.select_row(info.index)
        self.target_panel.select_camera(None if info is None else info.index)

        camera_count = SCENE_STORE.camera_count
        self.statusBar().showMessage(
            "Overview" if info is None else f"Camera {info.index + 1} of {camera_count}"
        )

        self._apply_occlusion()

    def _on_plan_changed(self, info: CameraInfo | None):
        if SCENE_STORE.scene is None:
            return

        self.viewport.on_plan_changed()

        # A new camera changes who observes what, so every cached report and
        # the overlay drawn from one are out of date.
        if self.reports is not None:
            self.reports.forget()
        self._rebuild_target()

        # A camera added to the plan can see things nothing could see before,
        # so what the whole plan covers has to be counted again.
        self.plan_mask = None

        # The score table describes the plan the bundle shipped, and this is
        # no longer that plan: the new camera has no rows to score by. That
        # is a reason to credit it nothing, which the rescorer already does
        # for any row past the table, and not a reason to throw the rescorer
        # away: dropping it would put the heat map back on the shipped
        # columns, where it answers what the whole plan covers no matter what
        # is in the route, and the route would stop colouring anything at all.
        if self.subset_scores is not None and self.route.planning:
            self.statusBar().showMessage(
                "The heat map counts nothing for a viewpoint the bundle never scored", 6000
            )

        # on_plan_changed built fresh glyphs, which know nothing of the route.
        self.route.forget_beyond(SCENE_STORE.camera_count)
        self._refresh_route()

        self.selected_camera = info
        if info is not None:
            self.viewpoints_panel.select_row(info.index)

        camera_count = SCENE_STORE.camera_count
        self.statusBar().showMessage(
            "Overview" if info is None else f"Camera {info.index + 1} of {camera_count}"
        )

    # -- The full-resolution model -------------------------------------

    def render_still(self):
        """
        Save the camera view as an image, at far more pixels than it is shown.
        The shot is the one in the Camera View dock -- same viewpoint, same
        model, same display mode -- drawn again in tiles at around
        `STILL_WIDTH` across, so the exported photograph carries the detail
        the dock has no room for.
        """
        if SCENE_STORE.scene is None:
            return

        suggested = Path(self.loader.data_dir) / "still.png"
        path, _ = QFileDialog.getSaveFileName(
            self, "Render Still", str(suggested), "PNG image (*.png)"
        )
        if not path:
            return

        self.statusBar().showMessage("Rendering...")
        try:
            colour = self.camera_viewport.render_still()
            if colour is None:
                self.statusBar().showMessage("Nothing to render")
                return

            Image.fromarray(colour).save(path)
        except Exception as exc:
            self.statusBar().showMessage("Render failed")
            QMessageBox.critical(self, "ViewScope", f"Could not render the still.\n\n{exc}")
            return

        height, width = colour.shape[:2]
        self.statusBar().showMessage(f"Rendered {Path(path).name} at {width}x{height}", 5000)

    def _load_photo_mesh(self, data_dir: Path):
        """
        Start reading the full-resolution model, if the bundle ships one.
        Read here rather than in either viewport, because both of them draw
        it: a gigabyte of triangles and eight textures are worth parsing once
        and handing round.
        """
        # Don't run the loader if it's already running
        if self.photo_loader is not None and self.photo_loader.isRunning():
            return

        if not self.load_photo_mesh:
            self.photo_mesh_finished.emit(False)
            return

        path = find_photo_mesh(data_dir)
        if path is None:
            self.photo_mesh_finished.emit(False)
            return

        self._stop_photo_loader()

        self.photo_loader = PhotoMeshLoader(path, self, full_resolution=self.full_resolution_mesh)
        self.photo_loader.loaded.connect(self._on_photo_mesh)
        self.photo_loader.failed.connect(self._on_photo_mesh_failed)
        self.photo_loader.progress.connect(self.photo_mesh_progress)

        self.statusBar().showMessage(f"Reading {path.name}...")
        self.photo_loader.start()

    def _on_photo_mesh(self, photo: PhotoMesh):
        """
        Put the model on screen in both viewports.
        Each gets its own actors over the same triangles and images: two
        renderers cannot share one set, and hiding the mesh in one panel
        would otherwise hide it in the other.
        """
        self.camera_viewport.set_photo_mesh(photo)
        self.viewport.set_photo_mesh(photo.clone())

        self.statusBar().showMessage(
            f"Full-resolution model ready ({photo.cells:,} triangles).", 5000
        )

        if self.photo_loader is not None:
            self.photo_loader.finalize_window()

        self.photo_mesh_finished.emit(True)

    def _on_photo_mesh_failed(self, message: str):
        """Fail loudly and leave both viewports on the simplified mesh."""
        print(f"photo mesh unavailable: {message}")
        self.statusBar().showMessage("Full-resolution model unavailable!", 5000)

        if self.photo_loader is not None:
            self.photo_loader.finalize_window()

        self.photo_mesh_finished.emit(False)

    def _stop_photo_loader(self):
        """
        Let go of a read still in flight, so nothing lands in a dead window.
        Blocks until the thread actually finishes.
        """
        loader = self.photo_loader
        self.photo_loader = None

        if loader is None:
            return

        loader.blockSignals(True)
        if loader.isRunning():
            loader.wait()

    # -- Target Inspection ---------------------------------------------

    def _on_target_picked(self, index: int):
        """Break down the target just clicked in the 3D view."""
        report = None if self.reports is None else self.reports.report(index, self.sector_count)

        if report is None:
            self.clear_target()
            return

        self.selected_target = report
        self.act_clear_target.setEnabled(True)
        self.target_panel.show_target(report)
        self.target_panel.select_camera(
            None if self.selected_camera is None else self.selected_camera.index
        )
        self._refresh_target_overlay()

        self.statusBar().showMessage(
            f"Target {report.index}: {len(report.observers)} observers across "
            f"{report.occupied_sectors} of {report.sector_count} sectors",
            6000,
        )

    def _on_sector_count_changed(self, _count: int):
        """The same target, cut into a different number of wedges."""
        self._rebuild_target()

    def clear_target(self):
        """Let go of whatever Escape should let go of.

        Placing a camera first, because that is the thing with a click owed
        on it: stopping halfway through would otherwise need the mouse.
        """
        if self.viewport.placing:
            self.viewport.cancel_placement()
            self.statusBar().showMessage("Placing stopped; no camera was added", 4000)
            return

        if self.selected_target is None:
            return

        self.selected_target = None
        self.act_clear_target.setEnabled(False)
        self.target_panel.show_target(None)
        self.viewport.clear_target_overlay()

    def _rebuild_target(self):
        """Re-read the selected target, for when the plan or the sectors move."""
        if self.selected_target is not None:
            self._on_target_picked(self.selected_target.index)

    def _refresh_target_overlay(self):
        """Redraw the overlay from the panel's current options."""
        if self.selected_target is None or SCENE_STORE.scene is None:
            self.viewport.clear_target_overlay()
            return

        self.viewport.show_target_overlay(
            self.selected_target,
            SCENE_STORE.scene.plan.positions,
            SCENE_STORE.scene.diagonal,
            self.target_panel.options(),
        )

    @property
    def sector_count(self) -> int:
        return self.target_panel.sector_count

    # -- Route Planning ------------------------------------------------

    def start_route_planning(self):
        """Put every viewpoint in the route and start choosing between them."""
        if SCENE_STORE.scene is None:
            return

        self.route.start(SCENE_STORE.camera_count)
        self.plan_route_panel.show_saved(None)
        self._refresh_route()
        self.statusBar().showMessage(
            "Planning a route: click a camera to take it out, or put it back", 6000
        )

    def load_route_file(self):
        """Plan the route named by a json file, instead of the plan on show.

        The file is read as a plan: a route saved earlier, or the plan.json of
        another bundle. Viewpoints it names that the current plan already has
        are matched by id and left where they are; the rest are appended, so a
        route planned against a different plan still arrives whole.
        """
        if SCENE_STORE.scene is None:
            return

        path = self._ask_loaded_route_path()
        if path is None:
            return

        try:
            entries = load_route(path)
        except ValueError as exc:
            QMessageBox.warning(self, "ViewScope", f"Could not load that route.\n\n{exc}")
            return

        rows, added = SCENE_STORE.ensure_cameras(
            [(entry.id, entry.position, entry.yaw_deg, entry.pitch_deg) for entry in entries]
        )

        # The file names the route, not the scene: the viewpoints it lists go
        # into the route and the rest of the plan stays where it is, out of
        # the route and on screen. A viewpoint you cannot see is one you
        # cannot click back in.
        self.route.select(rows)
        self.route.resume()
        # Saving this route again writes back to the file it came out of,
        # rather than starting the naming over at route.json.
        self.route.came_from(path)
        self._refresh_route()
        self.plan_route_panel.show_loaded(path, added, self._unscored(rows))
        self.statusBar().showMessage(f"Planning the {len(rows)} viewpoints of {path.name}", 6000)

    def stop_route_planning(self):
        """Leave planning, with or without writing the route out first.

        Stopping asks which of the two it is to be. Saving leaves planning
        once the route is written; exiting leaves it and keeps nothing.
        Backing out of either dialog keeps planning on.
        """
        scene = SCENE_STORE.scene
        if scene is None or not self.route.planning:
            return

        save = self._ask_stop_choice()
        if save is None:
            self.statusBar().showMessage("Still planning", 4000)
            return

        if not save:
            self.route.stop()
            self._refresh_route()
            self.plan_route_panel.show_saved(None)
            self.statusBar().showMessage("Left planning: the route was not saved", 6000)
            return

        path = self._ask_route_path()
        if path is None:
            self.statusBar().showMessage("Still planning: nothing was saved", 4000)
            return

        observed = 0 if self.route_mask is None else int(self.route_mask.sum())
        try:
            written = self.route.save(path, scene.plan, observed, len(scene.targets))
        except OSError as exc:
            QMessageBox.critical(self, "ViewScope", f"Could not save the route.\n\n{exc}")
            return

        self.route.stop()
        self._refresh_route()
        self.plan_route_panel.show_saved(written)
        self.statusBar().showMessage(f"Route saved to {written}", 6000)

    def _ask_stop_choice(self):
        """True to save the route, False to drop it, None to keep planning."""
        ask = QMessageBox(self)
        ask.setWindowTitle("ViewScope")
        ask.setIcon(QMessageBox.Icon.NoIcon)
        ask.setText("Stop planning the route?")
        count = len(self.route)
        lines = [f"The route has {count} viewpoint{'' if count == 1 else 's'}."]
        if self.route.path is None:
            lines.append("Exit leaves planning without saving it.")
        else:
            # Named, because this is the press that overwrites it.
            lines.append(f"Saving writes back to {self.route.path.name}.")
            lines.append("Exit leaves planning and that file as it is.")

        ask.setInformativeText(" ".join(lines))

        save = ask.addButton("Save route", QMessageBox.ButtonRole.AcceptRole)
        leave = ask.addButton("Exit", QMessageBox.ButtonRole.DestructiveRole)
        ask.setDefaultButton(save)
        ask.exec()

        clicked = ask.clickedButton()
        if clicked is save:
            return True
        if clicked is leave:
            return False

        return None

    def _ask_route_path(self):
        """Where to write the route, or None if the user changed their mind.

        Opens on the file the route belongs to -- the one it was loaded from,
        or the one it was last saved to -- so a route read out of a file goes
        back into it by pressing return. Anything else is a save-as, which is
        the dialog's own business.
        """
        suggested = self.route.path or Path(self.loader.data_dir) / ROUTE_FILENAME
        chosen, _filter = QFileDialog.getSaveFileName(
            self, "Save route", str(suggested), "JSON (*.json)"
        )

        return Path(chosen) if chosen else None

    def _ask_loaded_route_path(self):
        """Which route to read, or None if the user changed their mind."""
        start = Path(self.loader.data_dir) / ROUTE_FILENAME
        chosen, _filter = QFileDialog.getOpenFileName(
            self, "Load route", str(start), "JSON (*.json)"
        )

        return Path(chosen) if chosen else None

    def _on_route_camera_picked(self, index: int):
        if not self.route.planning:
            return

        inside = self.route.toggle(index)
        self._refresh_route()

        plan = SCENE_STORE.scene.plan if SCENE_STORE.scene is not None else None
        name = plan.ids[index] if plan is not None and index < len(plan.ids) else f"#{index + 1}"
        self.statusBar().showMessage(
            f"{name} {'added to' if inside else 'taken out of'} the route", 4000
        )

    def _on_route_select_all(self):
        """Put the whole plan in the route."""
        self.route.select_all(SCENE_STORE.camera_count)
        self._refresh_route()

    def _on_route_clear(self):
        self.route.clear()
        self._refresh_route()

    # -- targets nothing can see ---------------------------------------

    def _on_unobserved_toggled(self, flagged: bool):
        self.unobserved_on = flagged
        self._refresh_unobserved()

    def _observed_mask(self):
        """What can be seen, and by what, or None when nothing can say.

        While a route is being planned the question is what the route covers,
        so that taking a camera out shows the gap it leaves. Outside planning
        it is the whole plan: the targets flagged are then the ones the
        survey never covers, however it is flown.
        """
        if self.route.planning:
            return self.route_mask

        if self.plan_mask is None and self.visibility is not None:
            try:
                self.plan_mask = self.visibility.union_mask(range(SCENE_STORE.camera_count))
            except Exception as exc:
                self.statusBar().showMessage(f"Coverage unavailable: {exc}", 5000)
                return None

        return self.plan_mask

    def _refresh_unobserved(self):
        """Re-flag the targets nothing can see, after anything that moves them."""
        scene = SCENE_STORE.scene
        if not self.unobserved_on or scene is None:
            self.viewport.clear_unobserved()
            return

        observed = self._observed_mask()
        # Nothing to go on means nothing is known to be covered, so every
        # target is flagged. That is the honest answer, not a blank screen.
        missed = (
            np.ones(len(scene.targets), dtype=bool) if observed is None else ~np.asarray(observed)
        )

        self.viewport.show_unobserved(scene.targets[missed])
        self.statusBar().showMessage(
            f"{int(missed.sum()):,} of {missed.size:,} targets have no observer"
            f"{' in the route' if self.route.planning else ' in the plan'}",
            5000,
        )

    # -- flight path ---------------------------------------------------

    def _on_flight_path_toggled(self, shown: bool):
        self.flight_path_on = shown
        self._refresh_flight_path()

    def _flight_path_rows(self) -> tuple[int, ...]:
        """Which viewpoints the path runs through.

        The route, once there is one worth flying. Before that - a scene just
        opened, or every camera taken out again - the whole plan, so the
        button says something the moment it is pressed rather than drawing
        nothing and looking broken.
        """
        selected = self.route.selected
        if len(selected) >= 2:
            return selected

        return tuple(range(SCENE_STORE.camera_count))

    def _obstacle(self) -> Obstacle | None:
        """The model as space to stay out of, built once and kept.

        Voxelising costs a fraction of a second, which is worth paying to
        keep a path off the building but not worth paying on a load nobody
        asked a path of, so it waits until the first one is wanted.
        """
        scene = SCENE_STORE.scene
        if scene is None:
            return None

        if self.obstacle is None:
            self.statusBar().showMessage("Measuring the model to fly around it...")
            try:
                self.obstacle = Obstacle.from_mesh(scene.mesh)
            except Exception as exc:
                # Better a path that is only short than no path at all, but
                # the user has to be told it is not being kept off the model.
                self.statusBar().showMessage(f"Cannot fly around the model: {exc}", 8000)
                return None

        return self.obstacle

    def _plan_flight_path(self):
        """The path through the route as it stands, or None without a scene.

        Planned rather than remembered: the route moves on every click, and
        the path is cheap enough to find again that keeping one would only be
        a second answer to go stale.
        """
        scene = SCENE_STORE.scene
        if scene is None:
            return None

        rows = self._flight_path_rows()

        return plan_path(scene.plan.positions[list(rows)], self._obstacle()), rows

    def _refresh_flight_path(self):
        """Replan and redraw the path, after anything that could move it."""
        if not self.flight_path_on or SCENE_STORE.scene is None:
            self.viewport.clear_flight_path()
            self.plan_route_panel.show_path(None)
            return

        path, _rows = self._plan_flight_path()

        self.viewport.show_flight_path(path.points)
        self.plan_route_panel.show_path(path)

    def generate_route_report(self):
        """Write the route, its charts and its flight path out as a document.

        The path is planned for the report whether or not it is on screen:
        the report is about the flight, and asking the user to switch a line
        on first would only be a way of getting an empty document.
        """
        scene = SCENE_STORE.scene
        if scene is None:
            return

        if not len(self.route) and not SCENE_STORE.camera_count:
            self.statusBar().showMessage("Nothing to report on", 4000)
            return

        path = self._ask_report_path()
        if path is None:
            return

        self.statusBar().showMessage("Writing the report...")
        try:
            planned, rows = self._plan_flight_path()
            # The route is what the report is about; with nothing in it the
            # path falls back to the whole plan, and the report follows it
            # rather than describing a route that is not there.
            status = self._report_status(self.route.selected or rows, scene)

            written = write_report(
                path,
                name=self._route_name(),
                bundle=Path(self.loader.data_dir).name,
                status=status,
                path=planned,
                ids=scene.plan.ids,
                positions=scene.plan.positions,
            )
        except Exception as exc:
            self.statusBar().showMessage("Report failed")
            QMessageBox.critical(self, "ViewScope", f"Could not write the report.\n\n{exc}")
            return

        self.plan_route_panel.show_report(written)
        self.statusBar().showMessage(f"Report written to {written}", 6000)

    def _report_status(self, rows, scene):
        """What the report describes, counted for these viewpoints.

        The coverage the panel is showing is only kept while planning is on,
        and a report is worth as much after it as during it, so anything that
        is not to hand is counted again here.
        """
        described = RoutePlan()
        described.select(rows)

        observed = 0
        if self.route_mask is not None and tuple(rows) == self.route.selected:
            observed = int(self.route_mask.sum())
        elif self.visibility is not None:
            observed = int(self.visibility.union_mask(rows).sum())

        return described.status(scene.plan, observed, len(scene.targets), scene.centre)

    def _route_name(self) -> str:
        """What to call this route in the report."""
        if self.route.path is not None:
            return self.route.path.stem

        return "Unsaved route" if self.route.planning else "The whole plan"

    def _ask_report_path(self):
        """Where to write the report, or None if the user changed their mind."""
        stem = self.route.path.stem if self.route.path is not None else "route"
        suggested = Path(self.loader.data_dir) / f"{stem}_report.pdf"
        chosen, _filter = QFileDialog.getSaveFileName(
            self, "Generate report", str(suggested), "PDF (*.pdf)"
        )

        return Path(chosen) if chosen else None

    def _route_coverage(self):
        """The targets the route can see between them, or None when it sees none."""
        if self.visibility is None or not len(self.route):
            return None

        try:
            return self.visibility.union_mask(self.route.selected)
        except Exception as exc:
            self.statusBar().showMessage(f"Coverage unavailable: {exc}", 5000)
            return None

    def _refresh_route(self):
        """Repaint the glyphs and recount the coverage, after any route change."""
        scene = SCENE_STORE.scene
        if scene is None:
            self.plan_route_panel.show_route(None)
            return

        self.route_mask = self._route_coverage() if self.route.planning else None
        observed = 0 if self.route_mask is None else int(self.route_mask.sum())

        selected = set(self.route.selected)

        # Every part of this repaints the scene, and a repaint costs more
        # than all of them together, so the whole route change is drawn once.
        with self.viewport.held():
            # The route colours are only worn while planning; outside it
            # every frustum goes back to its own.
            self.viewport.set_route_selection(selected if self.route.planning else None)
            # Sectors are read about the model, not about the world origin:
            # a bundle carrying a larger survey's coordinates would otherwise
            # show its whole route standing in one sector.
            self.plan_route_panel.show_route(
                self.route.status(scene.plan, observed, len(scene.targets), scene.centre)
            )
            self._refresh_flight_path()
            self._refresh_unobserved()
            self._refresh_heatmap()

            # Occlusion follows the route while planning, so every camera in
            # it paints at once rather than only the one last clicked.
            self._apply_occlusion()

    # -- occlusion -----------------------------------------------------

    def _on_occlusion_toggled(self, enabled: bool):
        self.occlusion_on = enabled
        self._apply_occlusion()

        # Occlusion owns the target colours while it is on and gives them
        # back as the bundle shipped them, which is not what the route was
        # showing. Repaint, so leaving occlusion returns what you left.
        if not enabled:
            self._refresh_heatmap()

    def _apply_occlusion(self):
        """
        Push a visibility mask into the viewport.

        While a route is being planned that is everything the route sees
        between them, so taking a camera out shows what goes dark with it.
        Otherwise it is the one selected viewpoint.
        """
        mask = None
        planning = self.route.planning

        if self.occlusion_on:
            if planning:
                mask = self.route_mask
                if mask is None:
                    self.statusBar().showMessage("Put a camera in the route to see its cover", 4000)
            elif self.selected_camera is None:
                self.statusBar().showMessage("Pick a viewpoint to see what it can view", 4000)
            elif self.visibility is not None:
                try:
                    mask = self.visibility.mask_for(self.selected_camera.index)
                except Exception as exc:
                    self.statusBar().showMessage(f"Visibility failed: {exc}", 5000)

        self.viewport.set_occlusion_mask(mask)

        if mask is not None:
            seen = int(mask.sum())
            subject = (
                f"the {len(self.route)} cameras in the route" if planning else "this viewpoint"
            )
            self.statusBar().showMessage(
                f"{seen} of {mask.size} targets visible to {subject}", 5000
            )

    # -- layout persistence --------------------------------------------

    def reset_layout(self):
        """Put every dock and the toolbar back where the application starts them."""
        self.restoreState(self._default_state)
        self.statusBar().showMessage("Layout reset", 3000)

    def _restore_layout(self):
        settings = QSettings(ORG_NAME, APP_NAME)
        geometry = settings.value("geometry")
        state = settings.value("state")
        if isinstance(geometry, QByteArray):
            self.restoreGeometry(geometry)
        if isinstance(state, QByteArray):
            self.restoreState(state)

    def _save_layout(self):
        settings = QSettings(ORG_NAME, APP_NAME)
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("state", self.saveState())

    def closeEvent(self, event):
        # Safe to run twice: closing the window and later destroying it both
        # come through here, and the things being released do not take it twice.
        self._save_layout()
        if self.visibility is not None:
            self.visibility.close()
            self.visibility = None

        if self.loader.isRunning():
            self.loader.wait(2000)

        self._stop_photo_loader()
        self.viewport.shutdown()
        self.camera_viewport.shutdown()
        super().closeEvent(event)

    # -- Dialog Window -- #
    def show_error_dialog(self, error_title, error_message, action_message):
        self.statusBar().showMessage("Plan validation failed")

        dialog = FileErrorDialog(
            error_title=error_title, error_message=error_message, action_message=action_message
        )
        dialog.exec()  # Use exec() instead of show() for modal dialog
