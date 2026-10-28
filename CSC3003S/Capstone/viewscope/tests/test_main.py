# Unit tests for src/viewscope/main.py

import os

# Must be set before Qt picks a platform plugin, so these run without a display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from types import SimpleNamespace  # noqa: E402
from unittest.mock import MagicMock  # noqa: E402

import pytest  # noqa: E402

from viewscope import config  # noqa: E402
from viewscope import main as main_module  # noqa: E402
from viewscope.main import main  # noqa: E402


@pytest.fixture
def qt(monkeypatch):
    """Stand-ins for Qt, so main() never opens a window or blocks in exec()."""
    app = MagicMock()
    app.platformName.return_value = "cocoa"
    app.exec.return_value = 0

    page = MagicMock()

    monkeypatch.setattr(main_module, "QApplication", MagicMock(return_value=app))
    monkeypatch.setattr(main_module, "StartupWindow", MagicMock(return_value=page))

    return SimpleNamespace(app=app, page=page)


def test_main_returns_the_exit_code_qt_hands_back(qt):
    qt.app.exec.return_value = 3

    assert main() == 3


def test_main_names_the_application_before_reading_settings(qt):
    main()

    qt.app.setOrganizationName.assert_called_once_with(config.ORG_NAME)
    qt.app.setApplicationName.assert_called_once_with(config.APP_NAME)


def test_main_shows_the_startup_page(qt):
    main()

    qt.page.show.assert_called_once()
    qt.page.activateWindow.assert_called_once()


def test_linux_gets_a_headless_opengl_platform(qt, monkeypatch):
    monkeypatch.setattr(main_module.platform, "system", lambda: "Linux")
    monkeypatch.delenv("PYOPENGL_PLATFORM", raising=False)

    main()

    assert os.environ["PYOPENGL_PLATFORM"] == "egl"


def test_wayland_falls_back_to_x11(qt, monkeypatch):
    qt.app.platformName.return_value = "wayland"
    monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)

    main()

    assert os.environ["QT_QPA_PLATFORM"] == "xcb"
