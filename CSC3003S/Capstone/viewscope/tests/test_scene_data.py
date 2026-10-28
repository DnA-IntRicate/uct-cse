"""Unit tests for src/viewscope/data/scene.py."""

import numpy as np
import pytest
import trimesh

import viewscope_core as vc
from viewscope.data.scene import SceneData


def scene(mesh=None, scores=None) -> SceneData:
    mesh = mesh if mesh is not None else trimesh.creation.box(extents=(4.0, 2.0, 6.0))
    return SceneData(
        mesh=mesh,
        targets=np.zeros((1, 3)),
        normals=np.array([[0.0, 0.0, 1.0]]),
        plan=vc.Plan(
            camera={"width": 8, "height": 8, "yfov_deg": 53.13},
            ids=("vp000",),
            positions=np.array([[0.0, 0.0, 5.0]]),
            yaws_deg=np.array([0.0]),
            pitches_deg=np.array([0.0]),
        ),
        scores=scores,
    )


def test_a_bundle_without_a_score_table_says_so():
    """The panels branch on this rather than catching an attribute error."""
    assert scene().has_scores is False


def test_a_bundle_with_a_score_table_says_so():
    assert scene(scores=object()).has_scores is True


def test_the_diagonal_spans_the_bounding_box_corner_to_corner():
    box = trimesh.creation.box(extents=(3.0, 4.0, 12.0))

    assert scene(box).diagonal == pytest.approx(13.0)


def test_the_centre_is_the_middle_of_the_box_not_the_origin():
    """A model cut out of a larger survey keeps that survey's coordinates."""
    box = trimesh.creation.box(extents=(2.0, 2.0, 2.0))
    box.apply_translation([10.0, -4.0, 3.0])

    assert scene(box).centre == pytest.approx([10.0, -4.0, 3.0])
