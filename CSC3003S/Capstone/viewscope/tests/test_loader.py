"""Unit tests for src/viewscope/data/loader.py.

`_read` is what the thread runs, and it is called directly here: starting a
QThread would leave the assertions racing it. Everything it reads is a real
bundle written to a temporary directory, so the parsing is real too.
"""

import numpy as np
import pytest

from viewscope.data.loader import STAGE_COUNT, SceneLoader


@pytest.fixture
def loader(bundle):
    return SceneLoader(bundle)


def watch(loader):
    """Collect every signal the loader emits."""
    seen = {"progress": [], "stage": [], "failed": [], "loaded": [], "files": []}
    loader.progress.connect(lambda message: seen["progress"].append(message))
    loader.stage.connect(lambda done, total: seen["stage"].append((done, total)))
    loader.failed.connect(lambda message: seen["failed"].append(message))
    loader.loaded.connect(lambda scene: seen["loaded"].append(scene))
    loader.filename_validation_failed.connect(
        lambda *args: seen["files"].append(args),
    )
    return seen


# -----------------------------------------------------------------------------
# Reading a whole bundle
# -----------------------------------------------------------------------------


def test_a_bundle_reads_into_a_scene(loader, bundle):
    scene = loader._read()

    assert len(scene.mesh.faces) == 12
    assert scene.targets.shape == (2, 3)
    assert scene.normals.shape == (2, 3)
    assert scene.plan.ids == ("vp000", "vp001")
    assert scene.data_dir == bundle


def test_the_scores_come_across_when_the_bundle_has_them(loader):
    scene = loader._read()

    assert scene.has_scores
    assert scene.scores_error is None


def test_the_visibility_matrix_comes_across(loader):
    scene = loader._read()

    assert scene.visibility is not None
    assert scene.visibility.shape == (2, 2)
    assert scene.visibility.dtype == bool


# -----------------------------------------------------------------------------
# Progress
# -----------------------------------------------------------------------------


def test_every_stage_is_announced_in_order(loader):
    seen = watch(loader)

    loader._read()

    assert len(seen["progress"]) == STAGE_COUNT
    assert seen["stage"] == [(n, STAGE_COUNT) for n in range(1, STAGE_COUNT + 1)]


def test_the_last_stage_is_the_viewers_own(loader):
    """The bar has to say something while VTK actors are built afterwards."""
    seen = watch(loader)

    loader._read()

    assert seen["progress"][-1] == "Preparing the viewer..."


def test_the_bar_never_runs_past_its_end(bundle):
    """_step is defensive about the count drifting out of step with the calls."""
    loader = SceneLoader(bundle)
    seen = watch(loader)

    for _ in range(STAGE_COUNT + 3):
        loader._step("...")

    assert seen["stage"][-1] == (STAGE_COUNT, STAGE_COUNT)


# -----------------------------------------------------------------------------
# run(), which is what the thread actually calls
# -----------------------------------------------------------------------------


def test_run_hands_the_scene_back(loader):
    seen = watch(loader)

    loader.run()

    assert len(seen["loaded"]) == 1
    assert seen["failed"] == []


def test_run_reports_the_failure_rather_than_raising(tmp_path):
    """The thread has nowhere to raise to, so everything comes back as a signal."""
    empty = tmp_path / "empty"
    empty.mkdir()
    loader = SceneLoader(empty)
    seen = watch(loader)

    loader.run()

    assert seen["loaded"] == []
    assert len(seen["failed"]) == 1


# -----------------------------------------------------------------------------
# Bundles that do not validate
# -----------------------------------------------------------------------------


def test_a_missing_file_is_reported_before_anything_is_read(bundle):
    (bundle / "flyable.npz").unlink()
    loader = SceneLoader(bundle)
    seen = watch(loader)

    loader._read()

    assert len(seen["files"]) == 1
    title, message, _ = seen["files"][0]
    assert title == "Unexpected Files found"
    assert "flyable.npz" in message


def test_a_plan_with_the_wrong_viewpoint_count_is_reported(bundle):
    """A shipped bundle is known to hold a certain number; this one does not."""
    loader = SceneLoader(bundle, expected_viewpoints=185)
    seen = watch(loader)

    loader._read()

    assert [args[0] for args in seen["files"]] == ["Validation Error: missing viewpoints"]
    assert "185" in seen["files"][0][1]


def test_a_plan_the_bundle_brought_itself_is_not_counted(bundle):
    """Projects the user builds bring their own plan, of whatever size."""
    seen = watch(SceneLoader(bundle))
    SceneLoader(bundle)._read()

    assert seen["files"] == []


def test_an_unreadable_scene_is_reported(bundle):
    """The dialog goes up, and the read then falls over.

    `_read` reports the bad file and carries on to use the mesh it never
    got, so what reaches `run` is an UnboundLocalError naming a local
    variable rather than anything about scene.obj. The dialog is what this
    pins down; the second failure is recorded here as it stands.
    """
    (bundle / "scene.obj").write_text("not an obj\n")
    loader = SceneLoader(bundle)
    seen = watch(loader)

    with pytest.raises(UnboundLocalError):
        loader._read()

    assert [args[0] for args in seen["files"]] == ["Invalid file"]
    assert "scene.obj" in seen["files"][0][1]


def test_unreadable_targets_are_reported(bundle):
    """As with the scene: the dialog goes up, then the read falls over."""
    (bundle / "targets.ply").write_bytes(b"not a ply\n")
    loader = SceneLoader(bundle)
    seen = watch(loader)

    with pytest.raises(UnboundLocalError):
        loader._read()

    assert [args[0] for args in seen["files"]] == ["Invalid file"]
    assert "target.ply" in seen["files"][0][1]


# -----------------------------------------------------------------------------
# The optional files
# -----------------------------------------------------------------------------


def test_a_bundle_with_unreadable_scores_still_loads_its_geometry(bundle):
    """Scores are optional: the viewer shows the model without them."""
    np.savez_compressed(bundle / "scores.npz", nothing=np.zeros(1))

    scene = SceneLoader(bundle)._read()

    assert scene.has_scores is False
    assert scene.scores_error is not None


def test_a_bundle_with_no_visibility_file_still_loads(bundle):
    (bundle / "visibility.npz").unlink()

    scene = SceneLoader(bundle)._read()

    assert scene.visibility is None


def test_an_unreadable_visibility_file_is_passed_over(bundle, capsys):
    bundle.joinpath("visibility.npz").write_bytes(b"not an npz")

    scene = SceneLoader(bundle)._read()

    assert scene.visibility is None
    assert "visibility unavailable" in capsys.readouterr().out


def test_a_visibility_matrix_of_the_wrong_shape_is_passed_over(bundle, capsys):
    """One column per target, or it describes a different bundle."""
    np.savez_compressed(bundle / "visibility.npz", visible=np.ones((2, 5), dtype=bool))

    scene = SceneLoader(bundle)._read()

    assert scene.visibility is None
    assert "cameras by targets" in capsys.readouterr().out


def test_a_visibility_matrix_that_is_not_boolean_is_passed_over(bundle):
    np.savez_compressed(bundle / "visibility.npz", visible=np.ones((2, 2), dtype=np.uint8))

    assert SceneLoader(bundle)._read().visibility is None
