"""
TargetPanel

The breakdown of the target picked in the 3D view: every camera that can see
it with its weight and the two factors behind that weight, and the sector
decomposition those cameras fall into.

Like the other panels it reports intent through signals and takes state
through `show_*`. It touches neither VTK nor the scene.
"""

from __future__ import annotations

import contextlib

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from viewscope.config import (
    SECTOR_COUNTS,
    TARGET_COLOUR_MODES,
    OverlayOptions,
)
from viewscope.panels import SectorBarChart
from viewscope.scene import TargetReport

HINT = "Click a target in the 3D view to break it down."


class TargetPanel(QWidget):
    """One picked target: its weights, and how its observers spread around it."""

    #: The sector count to decompose by changed, so the report must be rebuilt.
    sector_count_changed = Signal(int)
    #: Anything that only changes how the overlay is drawn.
    overlay_changed = Signal()
    #: A row of the observers table was chosen; jump to that camera.
    camera_picked = Signal(int)
    #: Drop the selection entirely.
    cleared = Signal()

    SUMMARY_KEYS = ("Target", "Position", "Normal", "Score", "Diversity", "Observers", "Sectors")

    def __init__(self):
        super().__init__()

        self._report: TargetReport | None = None
        self._suppress = False

        body = QWidget()
        layout = QVBoxLayout(body)

        self.hint = QLabel(HINT)
        self.hint.setWordWrap(True)
        layout.addWidget(self.hint)

        layout.addWidget(self._build_controls())
        layout.addWidget(self._build_summary())

        layout.addWidget(QLabel("Sectors"))
        self.sector_bar_chart = SectorBarChart()  # Show Barchart first
        layout.addWidget(self.sector_bar_chart)
        self.sector_table = self._build_table(["Sector", "Cameras", "Best weight", "Best camera"])
        layout.addWidget(self.sector_table)

        layout.addWidget(QLabel("Observers"))
        self.observer_table = self._build_table(
            ["Camera", "Sector", "Weight", "Distance", "Angle", "Limited by", "Best"]
        )
        self.observer_table.itemSelectionChanged.connect(self._on_observer_selected)
        layout.addWidget(self.observer_table)

        self.sector_bar_chart = SectorBarChart()  # Show Barchart first
        layout.addWidget(self.sector_bar_chart)

        self.clear_button = QPushButton("Clear selection")
        self.clear_button.clicked.connect(self.cleared)
        layout.addWidget(self.clear_button)

        scroller = QScrollArea()
        scroller.setWidgetResizable(True)
        scroller.setWidget(body)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroller)

        self.show_target(None)

    # -- construction --------------------------------------------------

    def _build_controls(self) -> QGroupBox:
        box = QGroupBox("Decomposition")
        form = QFormLayout(box)

        self.sectors = QComboBox()
        self.sectors.addItems([str(count) for count in SECTOR_COUNTS])
        self.sectors.setToolTip("How many equal wedges the compass around the normal is cut into")
        self.sectors.currentTextChanged.connect(
            lambda text: self.sector_count_changed.emit(int(text))
        )
        form.addRow("Sectors", self.sectors)

        self.colour_by = QComboBox()
        self.colour_by.addItems(TARGET_COLOUR_MODES)
        self.colour_by.setToolTip(
            "Colour the observer rays, and the cameras they run to, by weight or by sector"
        )
        self.colour_by.currentTextChanged.connect(lambda _text: self.overlay_changed.emit())
        form.addRow("Colour by", self.colour_by)

        self.rays = QCheckBox("Show observer rays")
        self.rays.setChecked(True)
        self.rays.toggled.connect(lambda _on: self.overlay_changed.emit())
        form.addRow(self.rays)

        return box

    def _build_summary(self) -> QGroupBox:
        box = QGroupBox("Target")
        form = QFormLayout(box)

        self.rows = {}
        for key in self.SUMMARY_KEYS:
            label = QLabel("--")
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            form.addRow(key, label)
            self.rows[key] = label

        self.source = QLabel("")
        self.source.setWordWrap(True)
        form.addRow(self.source)

        return box

    @staticmethod
    def _build_table(headers: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.setMinimumHeight(140)

        return table

    # -- state ---------------------------------------------------------

    @property
    def sector_count(self) -> int:
        return int(self.sectors.currentText())

    def options(self) -> OverlayOptions:
        """How the viewport should draw the current selection."""
        return OverlayOptions(
            rays=self.rays.isChecked(),
            colour_by=self.colour_by.currentText(),
        )

    def show_target(self, report: TargetReport | None):
        """Fill the panel in for one target, or empty it out when given None."""
        self._report = report

        with contextlib.suppress(Exception):
            self.sector_bar_chart.update_chart(report)

        self.hint.setText(HINT if report is None else f"Target {report.index}")
        self.clear_button.setEnabled(report is not None)

        if report is None:
            for label in self.rows.values():
                label.setText("--")
            self.source.setText("")
            self._fill(self.sector_table, [])
            self._fill(self.observer_table, [])
            return

        self._show_summary(report)
        self._fill(
            self.sector_table,
            [
                [
                    str(sector.index),
                    str(sector.observers),
                    f"{sector.best_weight:.3f}" if sector.occupied else "--",
                    "--" if sector.best_camera is None else str(sector.best_camera + 1),
                ]
                for sector in report.sectors
            ],
        )
        self._fill(
            self.observer_table,
            [
                [
                    str(observer.camera_index + 1),
                    str(observer.sector),
                    f"{observer.weight:.3f}",
                    f"{observer.f_rho:.3f}",
                    f"{observer.f_theta:.3f}",
                    observer.limited_by,
                    "yes" if observer.best else "",
                ]
                for observer in report.observers
            ],
        )

    def selected_camera_row(self) -> int | None:
        """Which observer row is highlighted, as a plan index."""
        if self._report is None:
            return None

        rows = self.observer_table.selectionModel().selectedRows()
        if not rows:
            return None

        return self._report.observers[rows[0].row()].camera_index

    def select_camera(self, index: int | None):
        """Highlight the row for one camera, without re-emitting."""
        self._suppress = True
        try:
            if self._report is None or index is None:
                self.observer_table.clearSelection()
                return

            for row, observer in enumerate(self._report.observers):
                if observer.camera_index == index:
                    self.observer_table.selectRow(row)
                    return

            self.observer_table.clearSelection()
        finally:
            self._suppress = False

    # -- internals -----------------------------------------------------

    def _show_summary(self, report: TargetReport):
        position, normal = report.position, report.normal
        self.rows["Target"].setText(f"{report.index}")
        self.rows["Position"].setText(f"{position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f}")
        self.rows["Normal"].setText(f"{normal[0]:.2f}, {normal[1]:.2f}, {normal[2]:.2f}")
        self.rows["Score"].setText(f"{report.score:.4f}")
        self.rows["Diversity"].setText(f"{report.diversity:.4f}")
        self.rows["Observers"].setText(f"{len(report.observers)}")
        self.rows["Sectors"].setText(f"{report.occupied_sectors} of {report.sector_count} occupied")

        notes = []
        if report.live:
            notes.append("Recomputed for the edited plan, not read from the bundle.")
        if report.assumed_visibility:
            notes.append("Some cameras had no visibility data and were assumed to see this target.")
        self.source.setText(" ".join(notes))

    def _fill(self, table: QTableWidget, rows: list[list[str]]):
        self._suppress = True
        try:
            table.clearSelection()
            table.setRowCount(len(rows))
            for r, values in enumerate(rows):
                for c, text in enumerate(values):
                    table.setItem(r, c, QTableWidgetItem(text))
        finally:
            self._suppress = False

    def _on_observer_selected(self):
        if self._suppress:
            return

        index = self.selected_camera_row()
        if index is not None:
            self.camera_picked.emit(index)
