"""Unit tests for src/viewscope/scene/still.py.

The renderer really is built: an offscreen GL context is exactly what this
class exists to manage, so mocking it away would leave nothing under test.
"""

import numpy as np
import pytest
import trimesh

import viewscope_core as vc
from viewscope.scene.still import StillRenderer

POSE = vc.camera_pose(np.array([0.0, 0.0, 12.0]), 0.0, -80.0)


@pytest.fixture
def mesh():
    return trimesh.creation.box(extents=(2.0, 2.0, 2.0))


@pytest.fixture
def still():
    renderer = StillRenderer()
    yield renderer
    renderer.close()


def test_a_shot_comes_back_as_pixels_of_the_size_asked_for(still, mesh):
    image = still.render(mesh, POSE, 64, 48, 53.13)

    assert image.shape == (48, 64, 3)
    assert image.dtype == np.uint8


def test_the_shot_is_of_the_model_rather_than_an_empty_frame(still, mesh):
    """Pointed at a box from above, something has to be lit."""
    image = still.render(mesh, POSE, 64, 48, 53.13)

    assert image.max() > 0


def test_a_second_shot_of_the_same_shape_reuses_the_renderer(still, mesh):
    """Building one costs a GL context, so the shape is what decides."""
    still.render(mesh, POSE, 64, 48, 53.13)
    renderer = still._renderer

    still.render(mesh, POSE, 64, 48, 53.13)

    assert still._renderer is renderer


def test_a_different_size_rebuilds_the_renderer(still, mesh):
    still.render(mesh, POSE, 64, 48, 53.13)
    renderer = still._renderer

    image = still.render(mesh, POSE, 32, 24, 53.13)

    assert still._renderer is not renderer
    assert image.shape == (24, 32, 3)


def test_a_different_lens_rebuilds_the_renderer(still, mesh):
    still.render(mesh, POSE, 64, 48, 53.13)
    renderer = still._renderer

    still.render(mesh, POSE, 64, 48, 40.0)

    assert still._renderer is not renderer


def test_a_different_mesh_rebuilds_the_renderer(still, mesh):
    still.render(mesh, POSE, 64, 48, 53.13)
    renderer = still._renderer

    still.render(trimesh.creation.box(extents=(4.0, 4.0, 4.0)), POSE, 64, 48, 53.13)

    assert still._renderer is not renderer


def test_the_size_is_taken_as_whole_pixels(still, mesh):
    """Callers pass widget sizes, which arrive as floats often enough."""
    image = still.render(mesh, POSE, 64.0, 48.0, 53.13)

    assert image.shape == (48, 64, 3)


def test_closing_gives_the_context_back_and_forgets_the_shape(still, mesh):
    still.render(mesh, POSE, 64, 48, 53.13)

    still.close()

    assert still._renderer is None
    assert still._mesh is None
    assert still._shape is None


def test_closing_a_renderer_that_was_never_built_is_harmless():
    StillRenderer().close()


def test_a_shot_after_closing_builds_a_fresh_renderer(still, mesh):
    still.render(mesh, POSE, 64, 48, 53.13)
    still.close()

    assert still.render(mesh, POSE, 64, 48, 53.13).shape == (48, 64, 3)
