"""Unit tests for src/viewscope/scene/gizmos/camera_mode.py."""

import pytest

from viewscope.scene.camera import CameraMode
from viewscope.scene.gizmos.camera_mode import CameraModeGizmo


@pytest.fixture
def gizmo(app):
    return CameraModeGizmo()


def heard(gizmo):
    seen = []
    gizmo.mode_changed.connect(seen.append)
    return seen


def test_the_gizmo_offers_both_camera_modes(gizmo):
    assert set(gizmo._buttons) == {CameraMode.TRACKBALL, CameraMode.LOOK_AT}


def test_the_gizmo_opens_on_look_at(gizmo):
    assert gizmo._buttons[CameraMode.LOOK_AT].isChecked()
    assert not gizmo._buttons[CameraMode.TRACKBALL].isChecked()


def test_the_frame_is_pinned_to_what_the_buttons_need(gizmo):
    """A stylesheet-skewed sizeHint must never squeeze the buttons together."""
    chrome = 2 * (gizmo.FRAME_PADDING + gizmo.FRAME_BORDER)
    expected = chrome + gizmo.BUTTON_HEIGHT * 2 + gizmo.BUTTON_GAP

    assert gizmo.height() == expected
    assert gizmo.minimumHeight() == gizmo.maximumHeight() == expected


def test_the_buttons_are_all_the_height_the_frame_was_sized_for(gizmo):
    assert all(button.height() == gizmo.BUTTON_HEIGHT for button in gizmo._buttons.values())


def test_the_buttons_stay_pressed_to_show_the_mode(gizmo):
    assert all(button.isCheckable() for button in gizmo._buttons.values())


# -----------------------------------------------------------------------------
# Choosing a mode
# -----------------------------------------------------------------------------


def test_choosing_a_mode_presses_it_and_lets_the_other_up(gizmo):
    gizmo.set_mode(CameraMode.TRACKBALL)

    assert gizmo._buttons[CameraMode.TRACKBALL].isChecked()
    assert not gizmo._buttons[CameraMode.LOOK_AT].isChecked()


def test_choosing_a_mode_announces_it(gizmo):
    seen = heard(gizmo)

    gizmo.set_mode(CameraMode.TRACKBALL)

    assert seen == [CameraMode.TRACKBALL]


def test_clicking_a_button_chooses_its_mode(gizmo):
    seen = heard(gizmo)

    gizmo._buttons[CameraMode.TRACKBALL].click()

    assert seen == [CameraMode.TRACKBALL]
    assert gizmo._buttons[CameraMode.TRACKBALL].isChecked()


def test_a_mode_the_gizmo_does_not_offer_is_ignored(gizmo):
    seen = heard(gizmo)

    gizmo.set_mode("not a mode")

    assert seen == []
    assert gizmo._buttons[CameraMode.LOOK_AT].isChecked()


# -----------------------------------------------------------------------------
# Following the viewport rather than driving it
# -----------------------------------------------------------------------------


def test_the_gizmo_can_be_told_the_mode_without_announcing_it(gizmo):
    """The viewport changes mode by other means too; this only catches up."""
    seen = heard(gizmo)

    gizmo.set_current_mode(CameraMode.TRACKBALL)

    assert gizmo._buttons[CameraMode.TRACKBALL].isChecked()
    assert seen == []


def test_being_told_an_unknown_mode_leaves_every_button_up(gizmo):
    gizmo.set_current_mode("not a mode")

    assert not any(button.isChecked() for button in gizmo._buttons.values())
