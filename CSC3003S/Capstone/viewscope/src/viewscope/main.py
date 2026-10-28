"""
ViewScope desktop viewer: entry point.

uv run viewscope
"""

from __future__ import annotations

import os
import platform
import sys

from PySide6.QtWidgets import QApplication

from viewscope import config
from viewscope.startup import StartupWindow


def main() -> int:
    # Required for running headless on Linux
    if platform.system() == "Linux":
        os.environ.setdefault("PYOPENGL_PLATFORM", "egl")

    app = QApplication(sys.argv)
    app.setOrganizationName(config.ORG_NAME)
    app.setApplicationName(config.APP_NAME)

    # Set on the application rather than on a window: a tooltip is a top-level
    # window of its own and never inherits the stylesheet of whatever it is
    # describing.
    app.setStyleSheet(config.TOOLTIP_STYLE)

    # Wayland doesn't allow clients to warp the global cursor for
    # security reasons - which is done by the viewport.
    # To work around this, we force the application into X11 compatibility mode
    if app.platformName() == "wayland":
        os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
        print(
            "[Warning]: Viewscope is not fully-compatible with Wayland. "
            "Switching to X11 compatibility mode..."
        )

    # The startup screen opens the viewer itself, once a project is loaded.
    startup = StartupWindow()
    startup.show()
    startup.raise_()
    startup.activateWindow()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
