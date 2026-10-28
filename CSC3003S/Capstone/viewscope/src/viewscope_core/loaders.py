import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import trimesh

from viewscope_core import constants

PLAN_FRAME = "z-up-right-handed"
SCORE_KEYS = (
    "offsets",
    "camera_index",
    "weight",
    "f_rho",
    "f_theta",
    "sector_8",
    "sector_4",
    "best_8",
    "best_4",
    "diversity_8",
    "diversity_4",
    "score_8",
    "score_4",
    "meta",
)


def _fail(name, detail):
    raise ValueError(f"{name}: {detail}")


@dataclass(frozen=True)
class Plan:
    camera: dict
    ids: tuple
    positions: np.ndarray
    yaws_deg: np.ndarray
    pitches_deg: np.ndarray


@dataclass(frozen=True)
class Scores:
    offsets: np.ndarray
    camera_index: np.ndarray
    weight: np.ndarray
    f_rho: np.ndarray
    f_theta: np.ndarray
    sector_8: np.ndarray
    sector_4: np.ndarray
    best_8: np.ndarray
    best_4: np.ndarray
    diversity_8: np.ndarray
    diversity_4: np.ndarray
    score_8: np.ndarray
    score_4: np.ndarray
    meta: dict

    def observers(self, target_index):
        a = int(self.offsets[target_index])
        b = int(self.offsets[target_index + 1])
        window = slice(a, b)
        return {
            "camera_index": self.camera_index[window],
            "weight": self.weight[window],
            "f_rho": self.f_rho[window],
            "f_theta": self.f_theta[window],
            "sector_8": self.sector_8[window],
            "sector_4": self.sector_4[window],
            "best_8": self.best_8[window],
            "best_4": self.best_4[window],
        }


def load_scene(path):
    path = Path(path)
    if not path.exists():
        _fail("scene", f"{path} does not exist")
    mesh = trimesh.load(path, force="mesh", process=False)
    if not isinstance(mesh, trimesh.Trimesh) or len(mesh.faces) == 0:
        _fail("scene", f"{path} contains no triangle mesh")
    if not np.all(np.isfinite(mesh.vertices)):
        _fail("scene", "mesh vertices contain non finite values")
    if getattr(mesh.visual, "kind", None) not in ("texture", "vertex"):
        _fail("scene", "mesh carries no colour, expected a textured or vertex coloured OBJ")
    welded = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces, process=True)
    if not welded.is_watertight:
        print("scene: note: surface is not closed (a real scan), the inside test is best effort")
    return mesh


def load_targets(path):
    path = Path(path)
    if not path.exists():
        _fail("targets", f"{path} does not exist")
    with open(path, "rb") as fh:
        header = []
        while True:
            line = fh.readline()
            if not line:
                _fail("targets", "unterminated ply header")
            header.append(line.decode("ascii", "replace").strip())
            if header[-1] == "end_header":
                break
        if header[0] != "ply" or header[1] != "format binary_little_endian 1.0":
            _fail("targets", "expected a binary little endian ply file")
        count = 0
        properties = []
        for row in header:
            if row.startswith("element vertex "):
                count = int(row.split()[-1])
            elif row.startswith("element "):
                _fail("targets", f"unexpected element in header: {row}")
            elif row.startswith("property "):
                properties.append(row)
        expected = [f"property float {axis}" for axis in ("x", "y", "z", "nx", "ny", "nz")]
        if properties != expected:
            _fail("targets", f"expected properties {expected}, found {properties}")
        if count < 1:
            _fail("targets", "vertex count must be positive")
        raw = np.frombuffer(fh.read(count * 24), dtype="<f4")
    if raw.size != count * 6:
        _fail("targets", "file is truncated")
    data = raw.reshape(count, 6).astype(np.float64)
    if not np.all(np.isfinite(data)):
        _fail("targets", "targets contain non finite values")
    positions = data[:, :3]
    normals = data[:, 3:]
    lengths = np.linalg.norm(normals, axis=1)
    if np.any(np.abs(lengths - 1.0) > 1e-3):
        _fail("targets", "normals are not unit length")
    return positions, normals / lengths[:, None]


def load_plan(path):
    path = Path(path)
    if not path.exists():
        _fail("plan", f"{path} does not exist")
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        _fail("plan", f"invalid json: {error}")
    if raw.get("version") != 1:
        _fail("plan", "version must be 1")
    if raw.get("frame") != PLAN_FRAME:
        _fail("plan", f"frame must be {PLAN_FRAME}")
    if raw.get("units") != "metres":
        _fail("plan", "units must be metres")
    camera = raw.get("camera")
    if not isinstance(camera, dict):
        _fail("plan", "camera block is missing")
    width = camera.get("width")
    height = camera.get("height")
    yfov = camera.get("yfov_deg")
    if not (isinstance(width, int) and width > 0 and isinstance(height, int) and height > 0):
        _fail("plan", "camera width and height must be positive integers")
    if not (isinstance(yfov, (int, float)) and 10.0 < float(yfov) < 120.0):
        _fail("plan", "camera yfov_deg must lie in (10, 120)")
    viewpoints = raw.get("viewpoints")
    if not isinstance(viewpoints, list) or not viewpoints:
        _fail("plan", "viewpoints must be a non empty list")
    ids = []
    positions = np.zeros((len(viewpoints), 3), dtype=np.float64)
    yaws = np.zeros(len(viewpoints), dtype=np.float64)
    pitches = np.zeros(len(viewpoints), dtype=np.float64)
    for i, vp in enumerate(viewpoints):
        vid = vp.get("id")
        if not isinstance(vid, str) or not vid:
            _fail("plan", f"viewpoint {i} has no id")
        pos = vp.get("position")
        if not (isinstance(pos, list) and len(pos) == 3):
            _fail("plan", f"viewpoint {vid} position must be a list of three numbers")
        positions[i] = pos
        yaws[i] = vp.get("yaw_deg", np.nan)
        pitches[i] = vp.get("pitch_deg", np.nan)
        ids.append(vid)
    if len(set(ids)) != len(ids):
        _fail("plan", "viewpoint ids are not unique")
    if not np.all(np.isfinite(positions)) or not np.all(np.isfinite(yaws)):
        _fail("plan", "viewpoint poses contain non finite values")
    if not np.all(np.isfinite(pitches)) or np.any(np.abs(pitches) > 89.9):
        _fail("plan", "every pitch_deg must be finite and within (-89.9, 89.9)")
    return Plan(
        camera={"width": width, "height": height, "yfov_deg": float(yfov)},
        ids=tuple(ids),
        positions=positions,
        yaws_deg=yaws,
        pitches_deg=pitches,
    )


def _check_best(name, offsets, sectors, best, weight, sector_count, pair_targets):
    key = pair_targets * sector_count + sectors.astype(np.int64)
    occupied = np.bincount(key, minlength=0)
    flagged = np.bincount(key[best], minlength=occupied.size)
    if not np.array_equal(flagged > 0, occupied > 0) or np.any(flagged > 1):
        _fail("scores", f"{name} must flag exactly one camera per occupied sector")
    top = np.zeros(occupied.size, dtype=np.float64)
    np.maximum.at(top, key, weight)
    if not np.allclose(weight[best], top[key[best]], rtol=0, atol=1e-6):
        _fail("scores", f"{name} does not always flag the highest weight in its sector")


def load_scores(path, target_count, camera_count):
    path = Path(path)
    if not path.exists():
        _fail("scores", f"{path} does not exist")
    with np.load(path, allow_pickle=False) as bundle:
        missing = [k for k in SCORE_KEYS if k not in bundle.files]
        if missing:
            _fail("scores", f"missing arrays: {missing}")
        arrays = {k: bundle[k] for k in SCORE_KEYS}
    meta = json.loads(str(arrays.pop("meta")))
    if meta.get("version") != 1:
        _fail("scores", "meta version must be 1")
    if meta.get("target_count") != int(target_count):
        _fail("scores", "meta target_count does not match the loaded targets")
    if meta.get("camera_count") != int(camera_count):
        _fail("scores", "meta camera_count does not match the loaded plan")
    stored = meta.get("constants", {})
    for key in ("MU_RHO_M", "SIGMA_RHO_M", "MU_THETA_DEG", "SIGMA_THETA_DEG"):
        if stored.get(key) != getattr(constants, key):
            _fail("scores", f"constant {key} in the file disagrees with the library")
    offsets = arrays["offsets"]
    if offsets.dtype != np.int64 or offsets.shape != (target_count + 1,):
        _fail("scores", "offsets must be int64 of length target_count plus one")
    if offsets[0] != 0 or np.any(np.diff(offsets) < 0):
        _fail("scores", "offsets must start at zero and never decrease")
    pair_count = int(offsets[-1])
    for key, dtype in (
        ("camera_index", np.int32),
        ("weight", np.float32),
        ("f_rho", np.float32),
        ("f_theta", np.float32),
        ("sector_8", np.int8),
        ("sector_4", np.int8),
        ("best_8", np.bool_),
        ("best_4", np.bool_),
    ):
        if arrays[key].dtype != dtype or arrays[key].shape != (pair_count,):
            _fail("scores", f"{key} must be {dtype.__name__} of length {pair_count}")
    for key in ("diversity_8", "diversity_4", "score_8", "score_4"):
        if arrays[key].dtype != np.float32 or arrays[key].shape != (target_count,):
            _fail("scores", f"{key} must be float32 of length {target_count}")
        if np.any(arrays[key] < 0) or np.any(arrays[key] > 1):
            _fail("scores", f"{key} must lie in [0, 1]")
    cams = arrays["camera_index"]
    if pair_count and (cams.min() < 0 or cams.max() >= camera_count):
        _fail("scores", "camera_index out of range")
    w = arrays["weight"].astype(np.float64)
    if np.any(w <= 0) or np.any(w > 1):
        _fail("scores", "weights must lie in (0, 1]")
    product = arrays["f_rho"].astype(np.float64) * arrays["f_theta"].astype(np.float64)
    if not np.allclose(w, product, rtol=1e-4, atol=1e-6):
        _fail("scores", "weight must equal f_rho times f_theta")
    if np.any(arrays["sector_8"] < 0) or np.any(arrays["sector_8"] > 7):
        _fail("scores", "sector_8 out of range")
    if np.any(arrays["sector_4"] < 0) or np.any(arrays["sector_4"] > 3):
        _fail("scores", "sector_4 out of range")
    pair_targets = np.repeat(np.arange(target_count, dtype=np.int64), np.diff(offsets))
    boundaries = np.flatnonzero(np.diff(pair_targets) == 0)
    if boundaries.size and np.any(np.diff(cams.astype(np.int64))[boundaries] <= 0):
        _fail("scores", "camera_index must be strictly increasing within each target")
    if pair_count:
        _check_best("best_8", offsets, arrays["sector_8"], arrays["best_8"], w, 8, pair_targets)
        _check_best("best_4", offsets, arrays["sector_4"], arrays["best_4"], w, 4, pair_targets)
    return Scores(meta=meta, **arrays)


def load_reference(path):
    path = Path(path)
    if not path.exists():
        _fail("reference", f"{path} does not exist")
    raw = json.loads(path.read_text())
    for key in ("dataset", "agreement_min", "totals", "spot_checks"):
        if key not in raw:
            _fail("reference", f"missing key {key}")
    return raw
