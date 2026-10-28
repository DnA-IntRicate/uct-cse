"""Unit tests for src/viewscope/panels/metrics_panel.py.

Read-only figures, so what is checked is the text that lands in each row.
"""

import numpy as np
import pytest
import trimesh

from viewscope.camera.structs import CameraInfo
from viewscope.panels.metrics_panel import MetricsPanel
from viewscope.scene.stats import FieldStats


@pytest.fixture
def panel(app, store):
    return MetricsPanel()


def text(panel, key):
    return panel.rows[key].text()


# -----------------------------------------------------------------------------
# The rows themselves
# -----------------------------------------------------------------------------


def test_every_row_the_sections_name_is_there(panel):
    expected = [key for _, keys in MetricsPanel.SECTIONS for key in keys]

    assert list(panel.rows) == expected


def test_the_rows_start_blank(panel):
    assert all(label.text() == "--" for label in panel.rows.values())


def test_the_figures_can_be_selected_so_they_can_be_copied(panel):
    from PySide6.QtCore import Qt

    flags = panel.rows["Diagonal"].textInteractionFlags()

    assert flags & Qt.TextInteractionFlag.TextSelectableByMouse


def test_setting_a_row_that_does_not_exist_is_harmless(panel):
    panel.set("Nonsense", 1)

    assert "Nonsense" not in panel.rows


def test_a_row_takes_whatever_it_is_handed(panel):
    panel.set("Targets", 12)

    assert text(panel, "Targets") == "12"


def test_clearing_puts_rows_back_to_blank(panel):
    panel.set("Yaw", "90.00")

    panel.clear(["Yaw"])

    assert text(panel, "Yaw") == "--"


# -----------------------------------------------------------------------------
# The bundle
# -----------------------------------------------------------------------------


def test_the_bundle_figures_come_off_the_loaded_scene(panel, store, make_scene):
    store.set_scene(make_scene())

    panel.show_bundle()

    assert text(panel, "Vertices") == "8"
    assert text(panel, "Triangles") == "12"
    assert text(panel, "Targets") == "2"
    assert text(panel, "Cameras") == "2"
    assert text(panel, "Diagonal") == f"{store.scene.diagonal:.2f}"


def test_large_counts_are_grouped_so_they_can_be_read(panel, store, make_scene):
    store.set_scene(make_scene(targets=np.zeros((1234, 3))))

    panel.show_bundle()

    assert text(panel, "Targets") == "1,234"


def test_with_no_scene_the_bundle_figures_are_zero(panel):
    panel.show_bundle()

    assert text(panel, "Vertices") == "0"
    assert text(panel, "Triangles") == "0"
    assert text(panel, "Diagonal") == "0.00"


def test_a_scene_whose_mesh_is_not_a_triangle_mesh_counts_no_geometry(panel, store, make_scene):
    """A point cloud bundle still has targets and cameras to report."""
    store.set_scene(make_scene(mesh=trimesh.PointCloud(np.zeros((5, 3)))))

    panel.show_bundle()

    assert text(panel, "Vertices") == "0"
    assert text(panel, "Triangles") == "0"
    assert text(panel, "Cameras") == "2"


def test_the_camera_count_follows_the_plan_without_being_asked(panel, store, make_scene):
    """Adding a camera has to show up here, and nothing calls show_bundle."""
    store.set_scene(make_scene())

    store.add_camera((1.0, 2.0, 3.0), 0.0, 0.0)

    assert text(panel, "Cameras") == "3"


# -----------------------------------------------------------------------------
# The scalar field
# -----------------------------------------------------------------------------


def test_the_field_figures_are_shown_to_four_places(panel):
    panel.show_field(FieldStats("score_8", 0.0, 0.5, 1.0))

    assert text(panel, "Field") == "score_8"
    assert text(panel, "Min") == "0.0000"
    assert text(panel, "Mean") == "0.5000"
    assert text(panel, "Max") == "1.0000"


def test_a_bundle_with_no_field_says_so_and_blanks_the_figures(panel):
    panel.show_field(FieldStats("score_8", 0.0, 0.5, 1.0))

    panel.show_field(None)

    assert text(panel, "Field") == "unavailable"
    assert text(panel, "Min") == "--"
    assert text(panel, "Max") == "--"


# -----------------------------------------------------------------------------
# The viewpoint
# -----------------------------------------------------------------------------


def test_the_viewpoint_is_numbered_from_one_for_the_reader(panel, store, make_scene):
    store.set_scene(make_scene())

    panel.show_camera(CameraInfo(0, np.array([1.5, -2.25, 3.0]), 90.0, -45.0))

    assert text(panel, "Camera") == "1 of 2"
    assert text(panel, "Position") == "1.50, -2.25, 3.00"
    assert text(panel, "Yaw") == "90.00"
    assert text(panel, "Pitch") == "-45.00"


def test_going_back_to_free_look_blanks_the_viewpoint(panel, store, make_scene):
    store.set_scene(make_scene())
    panel.show_camera(CameraInfo(0, np.zeros(3), 0.0, 0.0))

    panel.show_camera(None)

    assert text(panel, "Camera") == "--"
    assert text(panel, "Position") == "--"
