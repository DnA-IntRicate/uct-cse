"""
PlanRoutePanel

Choosing which of the planned viewpoints actually get flown. "Plan route"
puts every camera in and turns them blue in the 3D view; clicking a camera
there takes it out again, or puts it back. "Load route" starts from a route
saved earlier, or from another plan's json, instead of from the whole plan,
and hides every viewpoint that file did not name.
Two charts answer the questions the whole exercise is about: how many targets
the cameras still in the route can see between them, and whether those cameras
stand all around the model or bunched on one side of it. Below them,
"Plan flight path" draws the order the route would be flown in.

Like the other panels it reports intent through signals and takes state
through `show_*`. It touches neither VTK nor the scene.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from viewscope.data import FlightPath, RouteStatus

from .route_charts import CoverageBar, SectorBars

IDLE_HINT = "Plan a route to choose which viewpoints get flown."
PLANNING_HINT = "Click a camera in the 3D view to take it out of the route, or put it back."

PATH_IDLE = "Plan flight path"
PATH_SHOWN = "Hide flight path"


class PlanRoutePanel(QWidget):
    """The route: which cameras are in it, and what they see between them."""

    #: Start planning, with every camera in the route.
    plan_requested = Signal()
    #: Stop planning, saving the route out or dropping it.
    stop_requested = Signal()
    #: Plan a route from the viewpoints named by a json file the user picks.
    load_requested = Signal()
    select_all_requested = Signal()
    clear_requested = Signal()
    #: Show the flight path through the route, or take it off the scene.
    path_requested = Signal(bool)
    #: Write the route, its charts and its flight path out as a document.
    report_requested = Signal()

    def __init__(self):
        super().__init__()

        # Everything goes inside a scroller, the way the target panel does it.
        # Two charts, a group box and seven buttons come to some eight hundred
        # pixels, and a dock that cannot be made shorter than its contents
        # makes the whole window taller than the screen: the viewport is left
        # a narrow strip, and the model is no longer where the middle of the
        # screen is. Scrolled, the panel asks for no height of its own.
        body = QWidget()
        layout = QVBoxLayout(body)

        self.hint = QLabel(IDLE_HINT)
        self.hint.setWordWrap(True)
        layout.addWidget(self.hint)

        start = QHBoxLayout()
        self.plan_button = QPushButton("Plan route")
        self.plan_button.setToolTip("Put every viewpoint in the route and start choosing")
        self.plan_button.clicked.connect(self.plan_requested)
        start.addWidget(self.plan_button)

        self.load_button = QPushButton("Load route...")
        self.load_button.setToolTip(
            "Plan from a route or plan json, rather than from the viewpoints on show"
        )
        self.load_button.clicked.connect(self.load_requested)
        start.addWidget(self.load_button)
        layout.addLayout(start)

        layout.addWidget(self._build_summary())

        buttons = QHBoxLayout()
        self.select_all_button = QPushButton("Select all")
        self.select_all_button.clicked.connect(self.select_all_requested)
        buttons.addWidget(self.select_all_button)

        self.clear_button = QPushButton("Unselect all")
        self.clear_button.setToolTip("Take every camera out of the route")
        self.clear_button.clicked.connect(self.clear_requested)
        buttons.addWidget(self.clear_button)
        layout.addLayout(buttons)

        self.coverage_bar = CoverageBar()
        layout.addWidget(self.coverage_bar)

        self.sector_bars = SectorBars()
        layout.addWidget(self.sector_bars)

        layout.addWidget(self._build_path())

        self.stop_button = QPushButton("Stop planning")
        self.stop_button.setToolTip(
            "Stop choosing, saving the route to a JSON file or leaving it unsaved"
        )
        self.stop_button.clicked.connect(self.stop_requested)
        layout.addWidget(self.stop_button)

        self.note = QLabel("")
        self.note.setWordWrap(True)
        layout.addWidget(self.note)

        scroller = QScrollArea()
        scroller.setWidgetResizable(True)
        scroller.setWidget(body)
        # The dock draws its own edge; a second one inside it is a box in a box.
        scroller.setFrameShape(QFrame.Shape.NoFrame)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroller)

        self.show_route(None)

    # -- construction --------------------------------------------------

    def _build_path(self) -> QGroupBox:
        box = QGroupBox("Flight path")
        form = QVBoxLayout(box)

        self.path_button = QPushButton(PATH_IDLE)
        self.path_button.setCheckable(True)
        self.path_button.setToolTip(
            "Join the viewpoints of the route into the shortest flight path "
            "found, and draw it from frustum to frustum"
        )
        self.path_button.toggled.connect(self._on_path_toggled)
        form.addWidget(self.path_button)

        self.path_note = QLabel("--")
        self.path_note.setWordWrap(True)
        form.addWidget(self.path_note)

        self.report_button = QPushButton("Generate report")
        self.report_button.setToolTip(
            "Write the route out as a PDF: both charts, the path by viewpoint and by "
            "co-ordinate, how far it runs, how hard it turns and what it would cost to fly"
        )
        self.report_button.clicked.connect(self.report_requested)
        form.addWidget(self.report_button)

        self.report_note = QLabel("")
        self.report_note.setWordWrap(True)
        form.addWidget(self.report_note)

        return box

    def _build_summary(self) -> QGroupBox:
        box = QGroupBox("Route")
        form = QVBoxLayout(box)

        self.cameras = QLabel("--")
        self.coverage = QLabel("--")
        for label in (self.cameras, self.coverage):
            label.setWordWrap(True)
            form.addWidget(label)

        return box

    # -- state ---------------------------------------------------------

    def show_route(self, status: RouteStatus | None):
        """Fill the panel in, or empty it out when there is no scene."""
        planning = status is not None and status.planning

        self.hint.setText(PLANNING_HINT if planning else IDLE_HINT)
        self.plan_button.setEnabled(status is not None and not planning)
        # Loading is a way into planning and a way to start the route over
        # from a file, so it stays live either side of the switch.
        self.load_button.setEnabled(status is not None)
        for button in (self.select_all_button, self.clear_button, self.stop_button):
            button.setEnabled(planning)

        # The path can be drawn through a plan as readily as through a route,
        # so it needs a scene and nothing more. The report is a document about
        # that same path, so it asks for no more than the path does.
        self.path_button.setEnabled(status is not None)
        self.report_button.setEnabled(status is not None)
        if status is None and self.path_button.isChecked():
            self.path_button.setChecked(False)

        self.coverage_bar.update_chart(status)
        self.sector_bars.update_chart(status)

        if status is None:
            self.cameras.setText("--")
            self.coverage.setText("--")
            # A report written of another bundle's route is not this one's.
            self.report_note.setText("")
            return

        self.cameras.setText(f"Cameras: {len(status.selected)} of {status.camera_count} selected")
        self.coverage.setText(
            f"Targets observed: {status.observed:,} of {status.targets:,} ({status.coverage:.1%})"
        )

    def show_path(self, path: FlightPath | None):
        """Say how far the planned path runs, and how it keeps off the model."""
        if path is None:
            self.path_note.setText("--")
            return

        stops = len(path.order)
        lines = [f"{path.length:,.0f} m through {stops} viewpoint{'' if stops == 1 else 's'}"]

        if path.avoidances:
            went = []
            if path.detours:
                went.append(f"{path.detours} round")
            if path.climbs:
                went.append(f"{path.climbs} over")
            lines.append(f"Keeping off the model: {', '.join(went)}.")

        # Said plainly, because it is the one thing the path promises.
        if path.clear:
            lines.append("Nothing flies through the model.")
        elif path.checked:
            lines.append(
                f"{path.crossings} hop{'' if path.crossings == 1 else 's'} cross the model: "
                "no way round or over was found."
            )
        else:
            lines.append("The model was not measured, so nothing was kept off it.")

        self.path_note.setText(" ".join(lines))

    def show_saved(self, path):
        """Say where the route went, or clear the line when given None."""
        self.note.setText("" if path is None else f"Saved to {path}")

    def show_report(self, path):
        """Say where the report went, or clear the line when given None."""
        self.report_note.setText("" if path is None else f"Report written to {path}")

    def show_loaded(self, path, added: int = 0, unscored: int = 0):
        """Say which file the route came from, and what it brought with it."""
        appended = ""
        if added:
            appended = f", adding {added} viewpoint{'' if added == 1 else 's'} to the plan"

        lines = [
            f"Loaded from {path}{appended}. Its viewpoints are the route; "
            "the rest of the plan is still on screen, out of it."
        ]

        # The route is flown and saved all the same; it is the colouring that
        # cannot speak for a viewpoint nothing was ever measured from.
        if unscored:
            lines.append(
                f"The bundle scored the plan it shipped, so the heat map counts nothing "
                f"for {unscored} of them."
            )

        self.note.setText(" ".join(lines))

    # -- internals -----------------------------------------------------

    def _on_path_toggled(self, shown: bool):
        self.path_button.setText(PATH_SHOWN if shown else PATH_IDLE)
        if not shown:
            self.path_note.setText("--")

        self.path_requested.emit(shown)
