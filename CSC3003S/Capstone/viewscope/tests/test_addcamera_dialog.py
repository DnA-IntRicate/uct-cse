"""Unit tests for src/viewscope/dialogs/add_camera_dialog.py."""

import pytest

from viewscope.dialogs.add_camera_dialog import AddCameraDialog


@pytest.fixture
def dialog(app):
    return AddCameraDialog()


def test_a_dialog_with_nothing_given_opens_at_the_origin(dialog):
    assert dialog.values() == (0.0, 0.0, 0.0, 0.0, 0.0)


def test_a_dialog_opens_on_the_pose_it_is_given(app):
    dialog = AddCameraDialog(position=(1.5, -2.25, 3.0), yaw=90.0, pitch=-45.0)

    assert dialog.values() == (1.5, -2.25, 3.0, 90.0, -45.0)


def test_a_position_with_no_angles_still_opens(app):
    """Placing in the view gives a point but no direction."""
    dialog = AddCameraDialog(position=(4.0, 5.0, 6.0))

    assert dialog.values() == (4.0, 5.0, 6.0, 0.0, 0.0)


def test_angles_with_no_position_still_open(app):
    dialog = AddCameraDialog(yaw=30.0, pitch=-10.0)

    assert dialog.values() == (0.0, 0.0, 0.0, 30.0, -10.0)


def test_the_dialog_is_titled_whatever_it_is_told(app):
    assert AddCameraDialog(title="Edit Camera").windowTitle() == "Edit Camera"
    assert AddCameraDialog().windowTitle() == "Add Camera"


def test_the_pitch_cannot_be_taken_past_vertical(dialog):
    """Beyond straight up or down the camera roll is undefined."""
    assert (dialog.pitch_widget.minimum(), dialog.pitch_widget.maximum()) == (-90.0, 90.0)


def test_the_yaw_goes_all_the_way_round_either_way(dialog):
    assert (dialog.yaw_widget.minimum(), dialog.yaw_widget.maximum()) == (-360.0, 360.0)


def test_a_position_can_be_far_from_the_origin(dialog):
    """A survey keeps its own coordinates, which are not small numbers."""
    dialog.position_widgets[0].setValue(500_000.0)

    assert dialog.values()[0] == 500_000.0


def test_positions_are_kept_to_the_centimetre_and_angles_to_a_tenth(dialog):
    assert dialog.position_widgets[0].decimals() == 2
    assert dialog.yaw_widget.decimals() == 1


def test_ok_accepts_the_dialog(dialog):
    dialog.ok_button.click()

    assert dialog.result() == AddCameraDialog.DialogCode.Accepted.value


def test_cancel_rejects_the_dialog(dialog):
    dialog.cancel_button.click()

    assert dialog.result() == AddCameraDialog.DialogCode.Rejected.value


def test_reset_puts_every_field_back_to_zero(app):
    dialog = AddCameraDialog(position=(1.0, 2.0, 3.0), yaw=45.0, pitch=-30.0)

    dialog.reset_button.click()

    assert dialog.values() == (0.0, 0.0, 0.0, 0.0, 0.0)


def test_the_reset_button_is_the_only_one_that_resets(app):
    """_on_button_clicked is dispatched by identity, not by label."""
    dialog = AddCameraDialog(position=(1.0, 2.0, 3.0))

    dialog._on_button_clicked(dialog.ok_button)
    assert dialog.values()[:3] == (1.0, 2.0, 3.0)

    dialog._on_button_clicked(dialog.reset_button)
    assert dialog.values()[:3] == (0.0, 0.0, 0.0)
