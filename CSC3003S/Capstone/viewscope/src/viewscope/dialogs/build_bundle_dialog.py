"""Asking how a model should be turned into a bundle."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class BuildBundleDialog(QDialog):
    """The handful of things the builder cannot work out from the file itself.

    Scale and up axis above all: a model arrives in whatever units and frame
    its exporter used, and every distance the library scores with - the ideal
    ten metre standoff, the five metre safe distance - is in real metres.
    """

    def __init__(self, source: Path, parent=None):
        super().__init__(parent)
        self.source = Path(source)
        self.setWindowTitle("Build a project")
        self.setMinimumWidth(560)

        page = QVBoxLayout(self)
        page.setSpacing(14)

        heading = QLabel(f"<b>{self.source.name}</b><br>{self.source.parent}")
        page.addWidget(heading)

        form = QFormLayout()
        form.setSpacing(10)

        self.name = QLineEdit(self.source.stem)
        form.addRow("Project name", self.name)

        self.out_dir = QLineEdit(str(self.source.parent))
        browse = QPushButton("Browse...")
        browse.clicked.connect(self._choose_out_dir)
        folder_row = QHBoxLayout()
        folder_row.addWidget(self.out_dir, 1)
        folder_row.addWidget(browse)
        form.addRow("Write the bundle to", folder_row)

        self.length = QDoubleSpinBox()
        self.length.setRange(0.1, 10000.0)
        self.length.setDecimals(2)
        self.length.setValue(20.0)
        self.length.setSuffix(" m")
        form.addRow("Longest side measures", self.length)

        self.up = QComboBox()
        self.up.addItems(["y", "z"])
        form.addRow("Up axis of the model", self.up)

        self.targets = QSpinBox()
        self.targets.setRange(1000, 250000)
        self.targets.setSingleStep(5000)
        self.targets.setValue(60000)
        form.addRow("Surface targets", self.targets)

        self.viewpoints = QSpinBox()
        self.viewpoints.setRange(8, 600)
        self.viewpoints.setValue(120)
        form.addRow("Viewpoints to plan", self.viewpoints)

        page.addLayout(form)

        note = QLabel(
            "The six bundle files are written into that folder. Building renders "
            "every viewpoint, so it takes a few minutes."
        )
        note.setWordWrap(True)
        page.addWidget(note)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Build")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        page.addWidget(buttons)

    def _choose_out_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Write the bundle to", self.out_dir.text())
        if folder:
            self.out_dir.setText(folder)

    def settings(self) -> dict:
        """What the user chose, ready for viewscope.build_bundle."""
        return {
            "name": self.name.text().strip() or self.source.stem,
            "out_dir": Path(self.out_dir.text().strip()),
            "length": self.length.value(),
            "up": self.up.currentText(),
            "targets": self.targets.value(),
            "viewpoints": self.viewpoints.value(),
        }
