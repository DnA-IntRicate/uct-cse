"""
numpy / trimesh -> VTK utility conversions.

Pure functions only: no Qt, no actors, no application state. Everything here
can be exercised without a render window, which makes it the easy part of the
codebase to test.
"""

from __future__ import annotations

import numpy as np
import vtk
from vtkmodules.util import numpy_support as vtknp


def points(array):
    """Wrap an (n, 3) array as vtkPoints."""
    pts = vtk.vtkPoints()
    pts.SetData(vtknp.numpy_to_vtk(np.ascontiguousarray(array, dtype=np.float64), deep=True))

    return pts


def cells(indices, n_per_cell):
    """Wrap an (n, k) index array as a vtkCellArray."""
    idx = np.ascontiguousarray(indices, dtype=np.int64)
    padded = np.column_stack([np.full(len(idx), n_per_cell, dtype=np.int64), idx]).ravel()
    array = vtk.vtkCellArray()
    array.SetCells(len(idx), vtknp.numpy_to_vtkIdTypeArray(padded, deep=True))

    return array


def trimesh_to_polydata(mesh):
    """Convert a trimesh mesh, carrying vertex colours or UVs across."""
    poly = vtk.vtkPolyData()
    poly.SetPoints(points(mesh.vertices))
    poly.SetPolys(cells(mesh.faces, 3))

    kind = getattr(mesh.visual, "kind", None)
    if kind == "vertex":
        rgb = np.ascontiguousarray(mesh.visual.vertex_colors[:, :3], dtype=np.uint8)
        arr = vtknp.numpy_to_vtk(rgb, deep=True)
        arr.SetName("Colors")
        poly.GetPointData().SetScalars(arr)
    elif kind == "texture" and getattr(mesh.visual, "uv", None) is not None:
        uv = np.ascontiguousarray(mesh.visual.uv, dtype=np.float32)
        tc = vtknp.numpy_to_vtk(uv, deep=True)
        tc.SetName("TCoords")
        poly.GetPointData().SetTCoords(tc)

    return poly


def texture_from_mesh(mesh):
    """Build a vtkTexture from the mesh material, or None if it has no image."""
    image = getattr(getattr(mesh.visual, "material", None), "image", None)
    if image is None:
        return None

    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)[::-1]
    h, w, _ = rgb.shape
    img = vtk.vtkImageData()
    img.SetDimensions(w, h, 1)
    arr = vtknp.numpy_to_vtk(np.ascontiguousarray(rgb.reshape(-1, 3)), deep=True)
    img.GetPointData().SetScalars(arr)

    texture = vtk.vtkTexture()
    texture.SetInputData(img)
    texture.InterpolateOn()

    return texture


def cloud_polydata(positions):
    """Turn an (n, 3) array into renderable vertex cells."""
    poly = vtk.vtkPolyData()
    poly.SetPoints(points(positions))
    glyph = vtk.vtkVertexGlyphFilter()
    glyph.SetInputData(poly)
    glyph.Update()

    return glyph.GetOutput()


def glyph_polydata(vertices, faces, colours, edges):
    """Assemble one camera frustum glyph."""
    poly = vtk.vtkPolyData()
    poly.SetPoints(points(vertices))

    if faces is not None and len(faces):
        poly.SetPolys(cells(faces, 3))

    if edges is not None and len(edges):
        poly.SetLines(cells(edges, 2))

    if colours is not None and len(colours) == len(vertices):
        rgb = np.ascontiguousarray(np.asarray(colours)[:, :3], dtype=np.uint8)
        poly.GetPointData().SetScalars(vtknp.numpy_to_vtk(rgb, deep=True))

    return poly


def apply_pose(camera, pose, yfov_deg, distance):
    """
    Point a vtkCamera using a 4x4 camera-to-world pose.

    OpenGL convention: the camera looks down its own -Z with +Y up, so the
    rotation block's columns are the camera axes in world space.
    """
    pose = np.asarray(pose, dtype=np.float64)
    position = pose[:3, 3]
    forward = -pose[:3, 2]
    up = pose[:3, 1]

    camera.SetPosition(*position)
    camera.SetFocalPoint(*(position + forward * distance))
    camera.SetViewUp(*up)
    camera.UseHorizontalViewAngleOff()
    camera.SetViewAngle(yfov_deg)
    camera.SetClippingRange(0.1, max(100.0, 10.0 * distance))


def pose_from_camera(camera) -> np.ndarray:
    """
    The 4x4 camera-to-world pose a vtkCamera is currently holding.
    The inverse of apply_pose, in the same OpenGL convention, so a pose taken
    off the live camera frames the same shot when it is handed to a renderer
    that works in poses rather than in windows.
    """
    position = np.asarray(camera.GetPosition(), dtype=np.float64)
    focal = np.asarray(camera.GetFocalPoint(), dtype=np.float64)

    forward = focal - position
    forward = forward / np.linalg.norm(forward)

    # View up is a hint and need not be square to the view direction, which
    # is why the up axis is rebuilt from the right one rather than used as
    # given. Looking straight along it leaves nothing to cross with, so any
    # axis off the view direction will do to break the tie.
    up_hint = np.asarray(camera.GetViewUp(), dtype=np.float64)
    right = np.cross(forward, up_hint)
    if np.linalg.norm(right) < 1e-9:
        up_hint = np.array([1.0, 0.0, 0.0]) if abs(forward[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
        right = np.cross(forward, up_hint)

    right = right / np.linalg.norm(right)

    pose = np.eye(4, dtype=np.float64)
    pose[:3, 0] = right
    pose[:3, 1] = np.cross(right, forward)
    pose[:3, 2] = -forward
    pose[:3, 3] = position

    return pose
