"""
Shared test setup.

Qt must be told to use the offscreen platform before anything imports it, so
the suite runs the same on a developer's machine as on a headless runner.
"""

import os

# Must be set before Qt picks a platform plugin, so these run without a display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np  # noqa: E402
import pytest  # noqa: E402
import trimesh  # noqa: E402
import trimesh.visual  # noqa: E402

import viewscope_core as vc  # noqa: E402
from viewscope.data.scene import SceneData  # noqa: E402
from viewscope.data.store import SCENE_STORE  # noqa: E402


@pytest.fixture(scope="session")
def app():
    """The one QApplication the whole session shares; Qt allows no second."""
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def make_scene():
    """Build a small bundle: a box, targets on it, and a plan around it."""

    def build(positions=((0.0, 0.0, 12.0), (12.0, 0.0, 6.0)), targets=None, **fields):
        positions = np.asarray(positions, dtype=float).reshape(-1, 3)
        targets = (
            np.asarray(targets, dtype=float)
            if targets is not None
            else np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 1.0]])
        )

        plan = vc.Plan(
            camera={"width": 64, "height": 48, "yfov_deg": 53.13},
            ids=tuple(f"vp{i:03d}" for i in range(len(positions))),
            positions=positions,
            yaws_deg=np.zeros(len(positions)),
            pitches_deg=np.full(len(positions), -45.0),
        )

        return SceneData(
            mesh=fields.pop("mesh", None) or trimesh.creation.box(extents=(2.0, 2.0, 2.0)),
            targets=targets,
            normals=np.tile([0.0, 0.0, 1.0], (len(targets), 1)),
            plan=plan,
            **fields,
        )

    return build


@pytest.fixture
def store():
    """The global scene store, emptied before and after so tests stay apart."""
    SCENE_STORE.clear()
    yield SCENE_STORE
    SCENE_STORE.clear()


@pytest.fixture(autouse=True)
def _keep_the_opengl_platform_put():
    """Undo any change a test makes to PYOPENGL_PLATFORM.

    `main()` sets it as a side effect, and monkeypatch cannot put back a
    variable that was never there to begin with. Left set to "egl" it breaks
    every offscreen render for the rest of the session on a machine with no
    EGL, which is every mac.
    """
    before = os.environ.get("PYOPENGL_PLATFORM")
    yield
    if before is None:
        os.environ.pop("PYOPENGL_PLATFORM", None)
    else:
        os.environ["PYOPENGL_PLATFORM"] = before


def _write_bundle(out):
    """The six files a bundle is, small enough to build in a test.

    Two targets on a box and two viewpoints above it, with a dense
    observation table: every pair is an observation, so the score columns
    have something in them without the numbers mattering.
    """
    import json

    from viewscope_core import constants

    out.mkdir(parents=True, exist_ok=True)

    mesh = trimesh.creation.box(extents=(2.0, 2.0, 2.0))
    mesh.visual = trimesh.visual.ColorVisuals(
        mesh, vertex_colors=np.tile([200, 180, 160, 255], (len(mesh.vertices), 1))
    )
    mesh.export(out / "scene.obj", include_color=True)

    targets = np.array([[0.0, 0.0, 1.0], [0.5, 0.0, 1.0]])
    normals = np.tile([0.0, 0.0, 1.0], (2, 1))
    header = (
        "ply\nformat binary_little_endian 1.0\n"
        f"element vertex {len(targets)}\n"
        "property float x\nproperty float y\nproperty float z\n"
        "property float nx\nproperty float ny\nproperty float nz\nend_header\n"
    )
    body = np.hstack([targets, normals]).astype("<f4")
    (out / "targets.ply").write_bytes(header.encode("ascii") + body.tobytes())

    positions = np.array([[0.0, 0.0, 11.0], [6.0, 0.0, 9.0]])
    (out / "plan.json").write_text(
        json.dumps(
            {
                "version": 1,
                "frame": "z-up-right-handed",
                "units": "metres",
                "camera": {"width": 64, "height": 48, "yfov_deg": 53.1301},
                "viewpoints": [
                    {
                        "id": f"vp{i:03d}",
                        "position": [float(v) for v in position],
                        "yaw_deg": yaw,
                        "pitch_deg": pitch,
                    }
                    for i, (position, yaw, pitch) in enumerate(
                        zip(positions, [0.0, 180.0], [-80.0, -50.0], strict=True)
                    )
                ],
            },
            indent=1,
        )
    )

    pair_target = np.repeat(np.arange(2), 2)
    pair_camera = np.tile(np.arange(2), 2)
    offset = positions[pair_camera] - targets[pair_target]
    rho = np.linalg.norm(offset, axis=1)
    direction = offset / rho[:, None]
    theta = np.degrees(
        np.arccos(np.clip(np.einsum("ij,ij->i", direction, normals[pair_target]), -1.0, 1.0))
    )
    weight, f_rho, f_theta = vc.weight_factors(rho, theta)

    sectors, bests, scores, diversities = {}, {}, {}, {}
    for size in (8, 4):
        sectors[size] = np.concatenate(
            [
                vc.sector_indices(
                    targets[t], normals[t], positions[pair_camera[pair_target == t]], size
                )
                for t in range(2)
            ]
        ).astype(np.int8)

        best = np.zeros(len(weight), dtype=bool)
        for t in range(2):
            rows = np.flatnonzero(pair_target == t)
            for sector in np.unique(sectors[size][rows]):
                wedge = rows[sectors[size][rows] == sector]
                best[wedge[np.argmax(weight[wedge])]] = True
        bests[size] = best

        scores[size] = np.asarray(
            [weight[(pair_target == t) & best].sum() / size for t in range(2)], dtype=np.float32
        )
        spread = []
        for t in range(2):
            rows = np.flatnonzero(pair_target == t)
            per_sector = np.bincount(sectors[size][rows], minlength=size).astype(float)
            ideal = max(len(rows), 1) / size
            spread.append(np.mean(np.minimum(per_sector, ideal) / ideal))
        diversities[size] = np.asarray(spread, dtype=np.float32)

    np.savez_compressed(
        out / "scores.npz",
        offsets=np.array([0, 2, 4], dtype=np.int64),
        camera_index=pair_camera.astype(np.int32),
        weight=weight.astype(np.float32),
        f_rho=np.float32(f_rho),
        f_theta=np.float32(f_theta),
        sector_8=sectors[8],
        sector_4=sectors[4],
        best_8=bests[8],
        best_4=bests[4],
        diversity_8=diversities[8],
        diversity_4=diversities[4],
        score_8=scores[8],
        score_4=scores[4],
        meta=json.dumps(
            {
                "version": 1,
                "target_count": 2,
                "camera_count": 2,
                "pair_count": int(len(weight)),
                "constants": {
                    key: getattr(constants, key)
                    for key in ("MU_RHO_M", "SIGMA_RHO_M", "MU_THETA_DEG", "SIGMA_THETA_DEG")
                },
            }
        ),
    )

    np.savez_compressed(
        out / "visibility.npz",
        visible=np.ones((2, 2), dtype=bool),
        meta=json.dumps({"version": 1}),
    )
    np.savez_compressed(
        out / "flyable.npz",
        bits=np.packbits(np.ones(8, dtype=bool)),
        shape=np.array([2, 2, 2], dtype=np.int32),
        origin=np.zeros(3),
        voxel=np.float64(1.0),
        meta=json.dumps({"version": 1}),
    )

    return out


@pytest.fixture
def bundle(tmp_path):
    """A complete, valid bundle directory the loader can read end to end."""
    return _write_bundle(tmp_path / "bundle")
