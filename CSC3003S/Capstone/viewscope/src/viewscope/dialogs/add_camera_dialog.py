from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class AddCameraDialog(QDialog):
    """Dialog for creating a new camera viewpoint."""

    def __init__(
        self,
        position: tuple[float, float, float] | None = None,
        yaw: float | None = None,
        pitch: float | None = None,
        title: str = "Add Camera",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)

        # Position [x, y, z]
        if position is None:
            position = (0.0, 0.0, 0.0)

        self.position_widgets = [
            QDoubleSpinBox(
                decimals=2, minimum=-1_000_000.0, maximum=1_000_000.0, value=position[0]
            ),
            QDoubleSpinBox(
                decimals=2, minimum=-1_000_000.0, maximum=1_000_000.0, value=position[1]
            ),
            QDoubleSpinBox(
                decimals=2, minimum=-1_000_000.0, maximum=1_000_000.0, value=position[2]
            ),
        ]

        # Rotation
        if yaw is None:
            yaw = 0.0
        if pitch is None:
            pitch = 0.0

        self.yaw_widget = QDoubleSpinBox(decimals=1, minimum=-360.0, maximum=360.0, value=yaw)
        self.pitch_widget = QDoubleSpinBox(decimals=1, minimum=-90.0, maximum=90.0, value=pitch)

        self.form = QFormLayout()
        self.form.addRow("X:", self.position_widgets[0])
        self.form.addRow("Y:", self.position_widgets[1])
        self.form.addRow("Z:", self.position_widgets[2])
        self.form.addRow("Yaw:", self.yaw_widget)
        self.form.addRow("Pitch:", self.pitch_widget)

        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.reset_button = QPushButton("Reset")

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.reset_button.clicked.connect(self._reset)

        buttons = QHBoxLayout()
        buttons.addWidget(self.ok_button)
        buttons.addWidget(self.cancel_button)
        buttons.addWidget(self.reset_button)

        layout = QVBoxLayout(self)
        layout.addLayout(self.form)
        layout.addLayout(buttons)

    def values(self) -> tuple[float, float, float, float, float]:
        return (
            self.position_widgets[0].value(),
            self.position_widgets[1].value(),
            self.position_widgets[2].value(),
            self.yaw_widget.value(),
            self.pitch_widget.value(),
        )

    def _on_button_clicked(self, button: QPushButton):
        if button == self.reset_button:
            self._reset()

    def _reset(self):
        for widget in self.position_widgets:
            widget.setValue(0.0)

        self.yaw_widget.setValue(0.0)
        self.pitch_widget.setValue(0.0)
