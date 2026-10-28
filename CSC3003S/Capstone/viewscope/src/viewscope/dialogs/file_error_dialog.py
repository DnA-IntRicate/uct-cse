import os
import subprocess
import sys

from PySide6.QtCore import QCoreApplication, Qt, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from viewscope import config


class FileErrorDialog(QDialog):
    """The Dialog that shows up when there's an error while validating a file.
    For now, it's only being used to validate plan.json.'"""

    def __init__(self, error_title, error_message, action_message, parent=None):
        super().__init__(parent)

        self.setWindowFlags(  # Removed the close button from Modal
            Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint
        )

        self.setWindowTitle(error_title)
        self.setMinimumWidth(500)
        self.setMinimumHeight(200)
        self.setWindowModality(
            Qt.WindowModality.ApplicationModal
        )  # Enforce modal standard, make it stay on top.

        layout = QVBoxLayout(self)

        # Error message
        self.message = QLabel(error_message)
        layout.addWidget(self.message)

        # Actionable message
        self.action = QLabel(action_message)
        layout.addWidget(self.action)

        self.setLayout(layout)

        # Buttons
        self.open_folder_button = QPushButton("Open the Data folder")
        self.open_folder_button.clicked.connect(self.open_folder_location)

        self.exit_button = QPushButton("Exit Application")
        self.exit_button.clicked.connect(self.on_exit)

        layout.addWidget(self.open_folder_button)
        layout.addWidget(self.exit_button)

        self.selected_file = None

    def open_folder_location(self):
        """Open the folder location of the data directory, to help users navigate their files,
        and see which files are missing or incorrect."""
        folder_path = config.DATA_DIR

        # Cross-platform folder opening
        if sys.platform == "win32":
            os.startfile(folder_path)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", folder_path])
        else:  # Linux, Unix, etc.
            subprocess.run(["xdg-open", folder_path])

    def on_exit(self):
        """Perform a clean application shutdown, using QTCore"""
        # using sys.exit(0) presents issues with VTK Renderer.
        self.reject()  # Close Dialog
        QTimer.singleShot(50, QCoreApplication.quit)  # Delay shutdown until after dialog is closed.
