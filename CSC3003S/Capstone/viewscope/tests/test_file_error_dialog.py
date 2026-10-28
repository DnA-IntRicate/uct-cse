"""Unit tests for src/viewscope/dialogs/file_error_dialog.py.

The dialog shuts the application down, so nothing here is allowed to let
that run: the quit and the folder-opening are both intercepted.
"""

import pytest
from PySide6.QtCore import Qt

from viewscope import config
from viewscope.dialogs import file_error_dialog
from viewscope.dialogs.file_error_dialog import FileErrorDialog


@pytest.fixture
def dialog(app):
    return FileErrorDialog("Missing files", "scores.npz is not there", "Put it back")


# -----------------------------------------------------------------------------
# What it says
# -----------------------------------------------------------------------------


def test_the_dialog_shows_the_error_and_what_to_do_about_it(dialog):
    assert dialog.windowTitle() == "Missing files"
    assert dialog.message.text() == "scores.npz is not there"
    assert dialog.action.text() == "Put it back"


def test_the_dialog_cannot_be_dismissed_out_of_hand(dialog):
    """No close button: the bundle is unusable, so it has to be dealt with."""
    assert dialog.windowFlags() & Qt.WindowType.CustomizeWindowHint
    assert dialog.windowModality() == Qt.WindowModality.ApplicationModal


def test_the_dialog_offers_both_ways_out(dialog):
    assert dialog.open_folder_button.text() == "Open the Data folder"
    assert dialog.exit_button.text() == "Exit Application"


# -----------------------------------------------------------------------------
# Opening the data folder
# -----------------------------------------------------------------------------


def test_on_a_mac_the_folder_is_opened_with_open(dialog, monkeypatch):
    calls = []
    monkeypatch.setattr(file_error_dialog.sys, "platform", "darwin")
    monkeypatch.setattr(file_error_dialog.subprocess, "run", lambda args: calls.append(args))

    dialog.open_folder_button.click()

    assert calls == [["open", config.DATA_DIR]]


def test_on_linux_the_folder_is_opened_with_xdg_open(dialog, monkeypatch):
    calls = []
    monkeypatch.setattr(file_error_dialog.sys, "platform", "linux")
    monkeypatch.setattr(file_error_dialog.subprocess, "run", lambda args: calls.append(args))

    dialog.open_folder_location()

    assert calls == [["xdg-open", config.DATA_DIR]]


def test_on_windows_the_folder_is_opened_through_the_shell(dialog, monkeypatch):
    calls = []
    monkeypatch.setattr(file_error_dialog.sys, "platform", "win32")
    # startfile only exists on Windows, so it is put there rather than patched.
    monkeypatch.setattr(file_error_dialog.os, "startfile", calls.append, raising=False)

    dialog.open_folder_location()

    assert calls == [config.DATA_DIR]


# -----------------------------------------------------------------------------
# Exiting
# -----------------------------------------------------------------------------


def test_exiting_closes_the_dialog_before_shutting_down(dialog, monkeypatch):
    """sys.exit upsets the VTK renderer, so the quit is deferred instead."""
    deferred = []
    monkeypatch.setattr(
        file_error_dialog.QTimer,
        "singleShot",
        lambda delay, slot: deferred.append((delay, slot)),
    )

    dialog.exit_button.click()

    assert dialog.result() == FileErrorDialog.DialogCode.Rejected.value
    assert len(deferred) == 1
    assert deferred[0][0] == 50
