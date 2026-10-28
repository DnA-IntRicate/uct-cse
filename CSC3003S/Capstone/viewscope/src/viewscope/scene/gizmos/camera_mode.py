from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout

from viewscope.scene import CameraMode


class CameraModeGizmo(QFrame):
    """Small floating control for switching camera interaction modes."""

    mode_changed = Signal(CameraMode)

    # The frame is sized from these rather than from sizeHint(). main.py sets
    # an application-wide stylesheet, which switches Qt to QStyleSheetStyle,
    # and under it the layout's QWidgetItems report each button 12px shorter
    # than the button's own sizeHint(). The frame's hint comes out ~22px short,
    # Viewport.resizeEvent's adjustSize() shrinks it to that, and the layout
    # then crams both buttons into less room than they need - they overlap.
    BUTTON_HEIGHT = 24
    BUTTON_GAP = 6
    FRAME_PADDING = 8
    FRAME_BORDER = 1  # Matches the 1px border in the stylesheet below.

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("CameraModeGizmo")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._buttons: dict[CameraMode, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.FRAME_PADDING, self.FRAME_PADDING, self.FRAME_PADDING, self.FRAME_PADDING
        )

        # Spacing is an explicit spacer item, not layout spacing: with the
        # item hints under-reported, the layout drops its own spacing when it
        # is short on room and leaves the buttons edge to edge.
        layout.setSpacing(0)

        self._add_mode(
            layout,
            CameraMode.TRACKBALL,
            "🖱",
            "Trackball Camera",
        )

        layout.addSpacing(self.BUTTON_GAP)

        self._add_mode(
            layout,
            CameraMode.LOOK_AT,
            "✦",
            "Look-At Camera",
        )

        self.setStyleSheet("""
            #CameraModeGizmo {
                background: rgba(25, 25, 28, 220);
                border: 1px solid rgba(255, 255, 255, 35);
                border-radius: 7px;
            }

            QPushButton {
                background: transparent;
                color: rgba(255, 255, 255, 180);
                border: none;
                border-radius: 5px;
                padding: 5px 9px;
                text-align: left;
                font-size: 11px;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 20);
                color: white;
            }

            QPushButton:checked {
                background: rgba(80, 140, 255, 100);
                color: white;
            }
        """)

        self._apply_fixed_size()
        self.set_mode(CameraMode.LOOK_AT)

    def _apply_fixed_size(self):
        """
        Pin the frame to what the buttons actually need, so a stylesheet-skewed
        sizeHint can never squeeze them. See the note on BUTTON_HEIGHT.
        """
        count = len(self._buttons)
        chrome = 2 * (self.FRAME_PADDING + self.FRAME_BORDER)

        widest = max(button.sizeHint().width() for button in self._buttons.values())
        height = self.BUTTON_HEIGHT * count + self.BUTTON_GAP * (count - 1)

        self.setFixedSize(chrome + widest, chrome + height)

    def _add_mode(self, layout: QVBoxLayout, mode: CameraMode, icon: str, text: str):
        button = QPushButton(f"{icon}  {text}", self)
        button.setCheckable(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFixedHeight(self.BUTTON_HEIGHT)

        button.clicked.connect(lambda checked=False, m=mode: self.set_mode(m))

        self._buttons[mode] = button
        layout.addWidget(button)

    def set_mode(self, mode: CameraMode):
        if mode not in self._buttons:
            return

        for button_mode, button in self._buttons.items():
            button.setChecked(button_mode == mode)

        self.mode_changed.emit(mode)

    def set_current_mode(self, mode: CameraMode):
        """Update the visual state without emitting mode_changed."""
        for button_mode, button in self._buttons.items():
            button.setChecked(button_mode == mode)
