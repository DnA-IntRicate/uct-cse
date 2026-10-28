"""
Turn a source OBJ into a ViewScope bundle the viewer can open.

    uv run viewscope-build data/SeaHawk/Seahawk.obj data/SeaHawk

The startup screen runs this too, as "Build from a model...", in a process of
its own: the renderer here and the viewer's both want an OpenGL context, and
the library asks for one live SceneRenderer per process.

It writes the six files the viewer expects - scene.obj, targets.ply, plan.json,
visibility.npz, scores.npz, flyable.npz - and every number in them comes out of
viewscope_core, the same library the shipped data/kiri bundle was built with.

Source models rarely arrive in the project's world frame, so the mesh is first
baked to vertex colours, turned +Z up, scaled to a real length in metres and
stood on the ground plane at z = 0.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path

import numpy as np
import trimesh
import trimesh.visual
from scipy.ndimage import distance_transform_edt
from trimesh.visual.color import uv_to_color

import viewscope_core as vc
from viewscope.config import PHOTO_MESH_DIR
from viewscope_core import constants

# The one camera every viewpoint uses, from the project brief.
CAMERA = {"width": 1368, "height": 912, "yfov_deg": 53.1301}

PLAN_FRAME = "z-up-right-handed"
GOLDEN_ANGLE = np.pi * (3.0 - np.sqrt(5.0))
MIN_ALTITUDE_M = 2.0
VOXEL_M = 0.2
ENVELOPE_GROWTH_M = 11.0


# -- Mesh ----------------------------------------------------------------


def load_coloured(obj_path: Path) -> trimesh.Trimesh:
    """
    Load an OBJ as a single vertex coloured mesh.

    The viewer draws scene.obj straight from its vertex colours, so per part
    textures and flat material colours are both baked down to one colour per
    vertex here.
    """
    with tempfile.TemporaryDirectory() as work:
        scene = trimesh.load(_with_local_textures(obj_path, Path(work)), process=False)
        geometries = list(scene.geometry.values()) if isinstance(scene, trimesh.Scene) else [scene]
        parts = [_coloured_part(part) for part in geometries if isinstance(part, trimesh.Trimesh)]

    mesh = trimesh.util.concatenate(parts)
    if not isinstance(mesh, trimesh.Trimesh) or len(mesh.faces) == 0:
        raise SystemExit(f"{obj_path} holds no triangle mesh")

    return mesh


def _with_local_textures(obj_path: Path, work: Path) -> Path:
    """
    Copy the OBJ and its material next to the textures, with paths rewritten.

    Exporters routinely write map_Kd as an absolute path from the machine that
    made the file. Those never resolve here, so every map_* line is pointed at
    whichever file of that name sits in the source tree.
    """
    images = {p.name.lower(): p for p in obj_path.parent.rglob("*") if p.is_file()}
    copy = work / obj_path.name
    shutil.copy(obj_path, copy)

    for material in obj_path.parent.glob("*.mtl"):
        text = material.read_text(errors="replace")

        def relocate(match):
            source = images.get(Path(match.group(2).replace("\\", "/")).name.lower())
            if source is None:
                return match.group(0)
            target = work / source.name
            if not target.exists():
                shutil.copy(source, target)
            return f"{match.group(1)}{source.name}"

        (work / material.name).write_text(re.sub(r"(map_\w+\s+)(\S.*)", relocate, text))

    return copy


def _coloured_part(part: trimesh.Trimesh) -> trimesh.Trimesh:
    """One geometry with its texture or material colour baked onto its vertices."""
    part = part.copy()
    material = getattr(part.visual, "material", None)
    image = getattr(material, "image", None)
    uv = getattr(part.visual, "uv", None)

    if image is not None and uv is not None:
        colours = np.asarray(uv_to_color(uv, image), dtype=np.uint8)
    else:
        base = np.asarray(getattr(material, "main_color", [180, 180, 180, 255]), dtype=np.uint8)
        colours = np.tile(base.reshape(1, -1), (len(part.vertices), 1))

    part.visual = trimesh.visual.ColorVisuals(part, vertex_colors=colours)
    return part


def compute_world_transform(vertices, length_m: float, up: str):
    """
    The scale and translation that puts these vertices into the app's
    frame: right handed, +Z up, metres, standing on z = 0, centred in X/Y.
    """
    vertices = _swap_up_axis(vertices, up)
    span = vertices.max(axis=0) - vertices.min(axis=0)
    scale = float(length_m) / float(span.max())

    scaled = vertices * scale
    low, high = scaled.min(axis=0), scaled.max(axis=0)
    translate = np.array(
        [-(low[0] + high[0]) / 2.0, -(low[1] + high[1]) / 2.0, -low[2]], dtype=np.float64
    )

    return scale, translate


def apply_world_transform(vertices, up: str, scale: float, translate):
    """
    Reapply a transform compute_world_transform derived, to another
    vertex array from the same source (e.g. the full-resolution geometry).
    """
    return _swap_up_axis(vertices, up) * scale + translate


def _swap_up_axis(vertices, up: str):
    if up == "y":
        # Model (x, y, z) with y up becomes world (z, x, y): a cyclic swap,
        # keeping the frame right handed.
        return vertices[:, [2, 0, 1]]

    return np.array(vertices, dtype=np.float64)


def to_world_frame(
    mesh: trimesh.Trimesh, length_m: float, up: str
) -> tuple[trimesh.Trimesh, tuple[float, np.ndarray]]:
    """Right handed, +Z up, metres, longest axis along +X, standing on z = 0."""
    scale, translate = compute_world_transform(mesh.vertices, length_m, up)
    mesh.vertices = apply_world_transform(mesh.vertices, up, scale, translate)

    return mesh, (scale, translate)


def export_full_resolution_mesh(
    source: Path, out_dir: Path, up: str, world_transform: tuple[float, np.ndarray]
):
    """
    A full-quality copy of the source model, reoriented and rescaled into
    the same frame as scene.obj - but with none of load_coloured's lossy
    steps applied: no baking to vertex colours, no concatenating parts into
    one mesh, no touching triangle count or texture resolution at all.
    """
    scale, translate = world_transform

    with tempfile.TemporaryDirectory() as work:
        loaded = trimesh.load(_with_local_textures(source, Path(work)), process=False)
        geometries = (
            dict(loaded.geometry) if isinstance(loaded, trimesh.Scene) else {"mesh": loaded}
        )

        for part in geometries.values():
            if not isinstance(part, trimesh.Trimesh):
                continue

            part.vertices = apply_world_transform(part.vertices, up, scale, translate)

        scene = trimesh.Scene(geometry=geometries)

        out_folder = out_dir / PHOTO_MESH_DIR
        out_folder.mkdir(parents=True, exist_ok=True)
        out_path = out_folder / source.name

        scene.export(str(out_path), file_type="obj")


# -- Targets ---------------------------------------------------------------


def sample_targets(mesh: trimesh.Trimesh, count: int, seed: int):
    """Surface targets with the outward unit normal of the face each sits on."""
    rng = np.random.default_rng(seed)
    points, faces = trimesh.sample.sample_surface(mesh, count, seed=int(rng.integers(1 << 31)))
    normals = np.asarray(mesh.face_normals[faces], dtype=np.float64)

    lengths = np.linalg.norm(normals, axis=1)
    usable = lengths > 1e-9  # degenerate faces carry no direction
    points, normals = points[usable], normals[usable] / lengths[usable, None]
    return np.asarray(points, dtype=np.float64), normals


def write_targets_ply(path: Path, positions, normals):
    """Binary little endian PLY, x y z nx ny nz as float32, the format load_targets reads."""
    header = (
        "ply\n"
        "format binary_little_endian 1.0\n"
        f"element vertex {len(positions)}\n"
        "property float x\nproperty float y\nproperty float z\n"
        "property float nx\nproperty float ny\nproperty float nz\n"
        "end_header\n"
    )
    body = np.hstack([positions, normals]).astype("<f4")
    with open(path, "wb") as fh:
        fh.write(header.encode("ascii"))
        fh.write(body.tobytes())


# -- the plan --------------------------------------------------------------


def build_plan(mesh, targets, count: int, seed: int):
    """Viewpoints spread over a dome around the model, each aimed at its centre.

    Candidates are spaced by the golden angle and spread evenly in sin(elevation)
    so the dome is covered without crowding its top, then anything the library
    calls an unsafe placement is dropped.
    """
    centre = mesh.bounds.mean(axis=0)
    reach = float(np.linalg.norm(mesh.bounds[1] - mesh.bounds[0]) / 2.0)
    radius = reach + constants.MU_RHO_M  # the library's ideal observation distance
    low, high = np.radians(8.0), np.radians(78.0)

    ids, positions, yaws, pitches, rejected = [], [], [], [], []
    for i in range(count):
        fraction = (i + 0.5) / count
        elevation = np.arcsin(np.sin(low) + fraction * (np.sin(high) - np.sin(low)))
        azimuth = i * GOLDEN_ANGLE
        position = centre + radius * np.array(
            [
                np.cos(elevation) * np.cos(azimuth),
                np.cos(elevation) * np.sin(azimuth),
                np.sin(elevation),
            ]
        )
        position = np.round(position, 4)

        placeable, reason = vc.check_placement(mesh, targets, position)
        if not placeable or position[2] < MIN_ALTITUDE_M:
            rejected.append(reason)
            continue

        yaw, pitch = vc.look_at_angles(position, centre)
        ids.append(f"vp{len(ids):03d}")
        positions.append(position)
        yaws.append(round(yaw, 4))
        pitches.append(round(pitch, 4))

    if not ids:
        raise SystemExit("no viewpoint survived the placement check")

    plan = {
        "version": 1,
        "frame": PLAN_FRAME,
        "units": "metres",
        "camera": dict(CAMERA),
        "viewpoints": [
            {"id": i, "position": [float(v) for v in p], "yaw_deg": y, "pitch_deg": t}
            for i, p, y, t in zip(ids, positions, yaws, pitches, strict=True)
        ],
    }
    return plan, rejected


# -- scores ----------------------------------------------------------------


def build_scores(targets, normals, plan, visible):
    """The CSR score table load_scores expects, ordered by target then camera.

    Every column is computed for all visible (target, camera) pairs at once, but
    through the same formulas as viewscope_core.scoring.
    """
    target_count = len(targets)

    # nonzero on (targets, cameras) walks row by row, which is the order the
    # file format asks for: ascending target, ascending camera within a target.
    pair_target, pair_camera = np.nonzero(visible.T)
    offset = plan.positions[pair_camera] - targets[pair_target]
    rho = np.linalg.norm(offset, axis=1)
    direction = offset / np.maximum(rho, 1e-12)[:, None]
    normal = normals[pair_target]
    theta = np.degrees(np.arccos(np.clip(np.einsum("ij,ij->i", direction, normal), -1.0, 1.0)))

    weight, f_rho, f_theta = vc.weight_factors(rho, theta)

    # The format requires every stored weight to be positive once it is float32,
    # so pairs whose weight underflows are left out of the table.
    keep = np.float32(weight) > 0
    pair_target, pair_camera = pair_target[keep], pair_camera[keep]
    offset, normal = offset[keep], normal[keep]
    weight = weight[keep].astype(np.float32)
    f_rho, f_theta = np.float32(f_rho[keep]), np.float32(f_theta[keep])

    counts = np.bincount(pair_target, minlength=target_count)
    offsets = np.concatenate([[0], np.cumsum(counts)]).astype(np.int64)

    sectors, bests, diversities, scores = {}, {}, {}, {}
    for size in (constants.DEFAULT_SECTOR_COUNT, constants.ALTERNATE_SECTOR_COUNT):
        sector = _sectors(offset, normal, size)
        best = _best_per_sector(pair_target, sector, weight, size)
        sectors[size] = sector
        bests[size] = best
        diversities[size] = _diversity(pair_target, sector, counts, size, target_count)
        totals = np.bincount(
            pair_target[best], weights=weight[best].astype(np.float64), minlength=target_count
        )
        scores[size] = np.float32(totals / size)

    meta = {
        "version": 1,
        "target_count": int(target_count),
        "camera_count": int(len(plan.ids)),
        "pair_count": int(len(weight)),
        "constants": {
            "MU_RHO_M": constants.MU_RHO_M,
            "SIGMA_RHO_M": constants.SIGMA_RHO_M,
            "MU_THETA_DEG": constants.MU_THETA_DEG,
            "SIGMA_THETA_DEG": constants.SIGMA_THETA_DEG,
        },
    }
    return {
        "offsets": offsets,
        "camera_index": pair_camera.astype(np.int32),
        "weight": weight,
        "f_rho": f_rho,
        "f_theta": f_theta,
        "sector_8": sectors[8].astype(np.int8),
        "sector_4": sectors[4].astype(np.int8),
        "best_8": bests[8],
        "best_4": bests[4],
        "diversity_8": diversities[8],
        "diversity_4": diversities[4],
        "score_8": scores[8],
        "score_4": scores[4],
        "meta": json.dumps(meta),
    }


def _sectors(offset, normal, size):
    """Which azimuth sector of the target's tangent plane each camera sits in."""
    # viewscope_core.scoring.tangent_basis, one target per row.
    axis = np.zeros_like(normal)
    axis[np.arange(len(normal)), np.argmin(np.abs(normal), axis=1)] = 1.0
    e1 = axis - np.einsum("ij,ij->i", axis, normal)[:, None] * normal
    e1 /= np.linalg.norm(e1, axis=1)[:, None]
    e2 = np.cross(normal, e1)

    azimuth = np.mod(
        np.arctan2(np.einsum("ij,ij->i", offset, e2), np.einsum("ij,ij->i", offset, e1)),
        2.0 * np.pi,
    )
    return np.minimum((azimuth * size / (2.0 * np.pi)).astype(np.int64), size - 1)


def _best_per_sector(pair_target, sector, weight, size):
    """Flag the heaviest camera in each occupied (target, sector), and only it."""
    key = pair_target * size + sector
    order = np.lexsort((weight, key))  # by sector, then weight within the sector
    ordered = key[order]

    leader = np.ones(len(order), dtype=bool)
    leader[:-1] = ordered[1:] != ordered[:-1]  # the last of each run is the heaviest

    best = np.zeros(len(order), dtype=bool)
    best[order[leader]] = True
    return best


def _diversity(pair_target, sector, counts, size, target_count):
    """How evenly a target's observers are spread around it, in [0, 1]."""
    per_sector = np.bincount(pair_target * size + sector, minlength=target_count * size)
    per_sector = per_sector.reshape(target_count, size).astype(np.float64)

    ideal = np.maximum(counts, 1)[:, None] / size
    spread = np.mean(np.minimum(per_sector, ideal) / ideal, axis=1)
    return np.float32(np.where(counts > 0, spread, 0.0))


# -- flyable volume --------------------------------------------------------


def build_flyable(mesh, targets, voxel=VOXEL_M):
    """The airspace a camera may occupy: clear of the structure and off the floor."""
    low = mesh.bounds[0] - ENVELOPE_GROWTH_M
    high = mesh.bounds[1] + ENVELOPE_GROWTH_M
    shape = np.maximum(np.ceil((high - low) / voxel).astype(np.int64), 1)

    index = np.floor((targets - low) / voxel).astype(np.int64)
    index = index[np.all((index >= 0) & (index < shape), axis=1)]
    occupied = np.zeros(shape, dtype=bool)
    occupied[index[:, 0], index[:, 1], index[:, 2]] = True

    clearance = distance_transform_edt(~occupied, sampling=(voxel, voxel, voxel))
    flyable = clearance >= constants.SAFE_DISTANCE_M

    altitude = low[2] + (np.arange(shape[2]) + 0.5) * voxel
    flyable &= (altitude >= mesh.bounds[0][2] + MIN_ALTITUDE_M)[None, None, :]

    meta = {
        "version": 1,
        "voxel_m": voxel,
        "origin": [float(v) for v in low],
        "shape": [int(v) for v in shape],
        "safe_distance_m": constants.SAFE_DISTANCE_M,
        "min_altitude_m": MIN_ALTITUDE_M,
        "envelope_growth_m": ENVELOPE_GROWTH_M,
        "flyable_voxels": int(flyable.sum()),
        "method": (
            "target-voxel occupancy, metric EDT clearance >= safe_distance, "
            "altitude floor z_min + min_altitude"
        ),
    }
    return {
        "bits": np.packbits(flyable.ravel()),
        "shape": shape.astype(np.int32),
        "origin": low.astype(np.float64),
        "voxel": np.float64(voxel),
        "meta": json.dumps(meta),
    }


# -- driver ----------------------------------------------------------------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="" if __doc__ is None else __doc__.splitlines()[1])
    parser.add_argument("source", type=Path, help="the OBJ to convert")
    parser.add_argument("out_dir", type=Path, help="bundle directory to write")
    parser.add_argument(
        "--length", type=float, default=20.0, help="real length of the longest axis, in metres"
    )
    parser.add_argument("--up", choices=("y", "z"), default="y", help="up axis of the source")
    parser.add_argument("--targets", type=int, default=60000, help="surface targets to sample")
    parser.add_argument("--viewpoints", type=int, default=120, help="viewpoints to plan")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args(argv)

    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    print(f"[1/6] reading {args.source}")
    mesh, world_transform = to_world_frame(load_coloured(args.source), args.length, args.up)
    print(f"      {len(mesh.faces)} faces, extents {mesh.extents.round(2)} m")
    mesh.export(out / "scene.obj", include_color=True)

    print("      writing full-resolution mesh for the camera view...")
    export_full_resolution_mesh(args.source, out, args.up, world_transform)

    print(f"[2/6] sampling {args.targets} targets")
    targets, normals = sample_targets(mesh, args.targets, args.seed)
    write_targets_ply(out / "targets.ply", targets, normals)

    print(f"[3/6] planning {args.viewpoints} viewpoints")
    plan_json, rejected = build_plan(mesh, targets, args.viewpoints, args.seed)
    (out / "plan.json").write_text(json.dumps(plan_json, indent=1))
    print(f"      kept {len(plan_json['viewpoints'])}, rejected {len(rejected)}")

    plan = vc.load_plan(out / "plan.json")

    print("[4/6] rendering visibility")
    renderer = vc.SceneRenderer(mesh, CAMERA["width"], CAMERA["height"], CAMERA["yfov_deg"])
    try:
        visible = vc.compute_visibility(renderer, targets, normals, plan)
    finally:
        renderer.close()
    np.savez_compressed(
        out / "visibility.npz",
        visible=visible,
        meta=json.dumps(
            {
                "version": 1,
                "cameras": int(visible.shape[0]),
                "targets": int(visible.shape[1]),
                "camera": dict(CAMERA),
                "znear_m": constants.ZNEAR_M,
                "depth_tolerance_abs_m": constants.DEPTH_TOLERANCE_ABS_M,
                "depth_tolerance_rel": constants.DEPTH_TOLERANCE_REL,
            }
        ),
    )
    seen = visible.any(axis=0).mean()
    print(f"      {visible.sum()} visible pairs, {seen:.1%} of targets seen by someone")

    print("[5/6] scoring")
    np.savez_compressed(out / "scores.npz", **build_scores(targets, normals, plan, visible))

    print("[6/6] mapping the flyable volume")
    np.savez_compressed(out / "flyable.npz", **build_flyable(mesh, targets))

    print(f"\nwrote {out}:")
    for path in sorted(out.iterdir()):
        print(f"  {path.name:16s} {path.stat().st_size / 1e6:8.2f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
