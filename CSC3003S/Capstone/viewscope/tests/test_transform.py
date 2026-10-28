"""Unit tests for src/viewscope/scene/transform.py.

Pure conversions, so everything here is checked by reading the VTK object
back out and comparing it against the array that went in.
"""

import numpy as np
import pytest
import trimesh
import trimesh.visual
import vtk
from PIL import Image
from vtkmodules.util import numpy_support as vtknp

from viewscope.scene import transform

# A unit triangle, the smallest thing with a face.
VERTICES = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
FACES = np.array([[0, 1, 2]])


# -----------------------------------------------------------------------------
# points and cells
# -----------------------------------------------------------------------------


def test_points_carry_every_coordinate_across():
    pts = transform.points(VERTICES)

    assert pts.GetNumberOfPoints() == 3
    assert pts.GetPoint(1) == (1.0, 0.0, 0.0)


def test_points_accept_a_non_contiguous_array():
    """Callers slice columns off larger arrays; VTK needs one block of memory."""
    wide = np.zeros((3, 6))
    wide[:, 3:] = VERTICES

    pts = transform.points(wide[:, 3:])

    assert pts.GetPoint(2) == (0.0, 1.0, 0.0)


def test_points_of_an_empty_array_is_empty_rather_than_an_error():
    assert transform.points(np.zeros((0, 3))).GetNumberOfPoints() == 0


def test_cells_prefix_each_row_with_its_length():
    """The padded format VTK reads: n, then n indices, per cell."""
    array = transform.cells(FACES, 3)

    assert array.GetNumberOfCells() == 1
    ids = vtk.vtkIdList()
    array.GetCellAtId(0, ids)
    assert [ids.GetId(i) for i in range(ids.GetNumberOfIds())] == [0, 1, 2]


def test_cells_handles_two_point_lines_as_well_as_triangles():
    array = transform.cells(np.array([[0, 1], [1, 2]]), 2)

    assert array.GetNumberOfCells() == 2


# -----------------------------------------------------------------------------
# trimesh -> polydata
# -----------------------------------------------------------------------------


def test_a_mesh_becomes_polydata_with_its_points_and_faces():
    mesh = trimesh.Trimesh(vertices=VERTICES, faces=FACES, process=False)

    poly = transform.trimesh_to_polydata(mesh)

    assert poly.GetNumberOfPoints() == 3
    assert poly.GetNumberOfPolys() == 1


def test_vertex_colours_come_across_as_scalars_with_the_alpha_dropped():
    """VTK is handed RGB; trimesh stores RGBA."""
    mesh = trimesh.Trimesh(vertices=VERTICES, faces=FACES, process=False)
    mesh.visual = trimesh.visual.ColorVisuals(
        mesh, vertex_colors=np.array([[255, 0, 0, 255], [0, 255, 0, 255], [0, 0, 255, 255]])
    )

    poly = transform.trimesh_to_polydata(mesh)

    scalars = poly.GetPointData().GetScalars()
    assert scalars.GetName() == "Colors"
    assert scalars.GetNumberOfComponents() == 3
    assert vtknp.vtk_to_numpy(scalars)[0].tolist() == [255, 0, 0]


def test_texture_coordinates_come_across_when_the_mesh_is_textured():
    mesh = trimesh.Trimesh(vertices=VERTICES, faces=FACES, process=False)
    mesh.visual = trimesh.visual.TextureVisuals(
        uv=np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]),
        image=Image.new("RGB", (2, 2), (10, 20, 30)),
    )

    poly = transform.trimesh_to_polydata(mesh)

    tcoords = poly.GetPointData().GetTCoords()
    assert tcoords is not None
    assert tcoords.GetName() == "TCoords"
    assert tcoords.GetNumberOfTuples() == 3


def test_a_textured_mesh_with_no_uvs_gets_no_coordinates():
    """A texture that nothing is mapped to must not be half-applied."""
    mesh = trimesh.Trimesh(vertices=VERTICES, faces=FACES, process=False)
    mesh.visual = trimesh.visual.TextureVisuals(image=Image.new("RGB", (2, 2)))

    poly = transform.trimesh_to_polydata(mesh)

    assert poly.GetPointData().GetTCoords() is None


def test_a_mesh_with_no_visual_kind_carries_neither_colours_nor_coordinates():
    class Bare:
        visual = None
        vertices = VERTICES
        faces = FACES

    poly = transform.trimesh_to_polydata(Bare())

    assert poly.GetPointData().GetScalars() is None
    assert poly.GetPointData().GetTCoords() is None


# -----------------------------------------------------------------------------
# Textures
# -----------------------------------------------------------------------------


def test_a_material_image_becomes_an_interpolated_texture():
    mesh = trimesh.Trimesh(vertices=VERTICES, faces=FACES, process=False)
    mesh.visual = trimesh.visual.TextureVisuals(image=Image.new("RGB", (4, 2), (10, 20, 30)))

    texture = transform.texture_from_mesh(mesh)

    assert texture is not None
    assert texture.GetInterpolate() == 1
    assert texture.GetInput().GetDimensions() == (4, 2, 1)


def test_the_texture_is_flipped_so_it_lands_the_right_way_up():
    """Images run top row first; VTK's origin is at the bottom."""
    pixels = np.zeros((2, 1, 3), dtype=np.uint8)
    pixels[0] = [255, 0, 0]  # top row red
    mesh = trimesh.Trimesh(vertices=VERTICES, faces=FACES, process=False)
    mesh.visual = trimesh.visual.TextureVisuals(image=Image.fromarray(pixels))

    texture = transform.texture_from_mesh(mesh)
    assert texture is not None

    stored = vtknp.vtk_to_numpy(texture.GetInput().GetPointData().GetScalars())
    assert stored[0].tolist() == [0, 0, 0]  # bottom row first
    assert stored[-1].tolist() == [255, 0, 0]


def test_a_mesh_with_no_image_has_no_texture():
    mesh = trimesh.Trimesh(vertices=VERTICES, faces=FACES, process=False)

    assert transform.texture_from_mesh(mesh) is None


# -----------------------------------------------------------------------------
# Point clouds and glyphs
# -----------------------------------------------------------------------------


def test_a_cloud_gets_one_vertex_cell_per_point():
    poly = transform.cloud_polydata(np.random.default_rng(0).normal(size=(5, 3)))

    assert poly.GetNumberOfPoints() == 5
    assert poly.GetNumberOfVerts() == 5


def test_a_glyph_carries_faces_edges_and_colours():
    colours = np.array([[255, 0, 0, 255], [0, 255, 0, 255], [0, 0, 255, 255]])

    poly = transform.glyph_polydata(VERTICES, FACES, colours, np.array([[0, 1], [1, 2]]))

    assert poly.GetNumberOfPolys() == 1
    assert poly.GetNumberOfLines() == 2
    assert poly.GetPointData().GetScalars().GetNumberOfTuples() == 3


def test_a_glyph_of_lines_alone_has_no_faces():
    poly = transform.glyph_polydata(VERTICES, None, None, np.array([[0, 1]]))

    assert poly.GetNumberOfPolys() == 0
    assert poly.GetNumberOfLines() == 1
    assert poly.GetPointData().GetScalars() is None


def test_a_glyph_of_faces_alone_has_no_lines():
    poly = transform.glyph_polydata(VERTICES, FACES, None, None)

    assert poly.GetNumberOfPolys() == 1
    assert poly.GetNumberOfLines() == 0


def test_empty_face_and_edge_arrays_are_the_same_as_none():
    poly = transform.glyph_polydata(VERTICES, np.zeros((0, 3)), None, np.zeros((0, 2)))

    assert poly.GetNumberOfPolys() == 0
    assert poly.GetNumberOfLines() == 0


def test_colours_that_do_not_match_the_vertices_are_ignored():
    """A mismatched array would colour the wrong points, so it is dropped."""
    poly = transform.glyph_polydata(VERTICES, FACES, np.array([[255, 0, 0, 255]]), None)

    assert poly.GetPointData().GetScalars() is None


# -----------------------------------------------------------------------------
# Poses
# -----------------------------------------------------------------------------


def pose_looking_along_x() -> np.ndarray:
    """Standing at the origin looking down +X, with +Z up."""
    pose = np.eye(4)
    pose[:3, 0] = [0.0, -1.0, 0.0]  # right
    pose[:3, 1] = [0.0, 0.0, 1.0]  # up
    pose[:3, 2] = [-1.0, 0.0, 0.0]  # back, so forward is +X
    return pose


def test_a_pose_points_the_camera_where_it_says():
    camera = vtk.vtkCamera()

    transform.apply_pose(camera, pose_looking_along_x(), 53.13, 10.0)

    assert camera.GetPosition() == pytest.approx([0.0, 0.0, 0.0])
    assert camera.GetFocalPoint() == pytest.approx([10.0, 0.0, 0.0])
    assert camera.GetViewUp() == pytest.approx([0.0, 0.0, 1.0])


def test_the_field_of_view_is_set_vertically():
    """Horizontal would crop the frame differently from the renderer's."""
    camera = vtk.vtkCamera()

    transform.apply_pose(camera, pose_looking_along_x(), 53.13, 10.0)

    assert camera.GetUseHorizontalViewAngle() == 0
    assert camera.GetViewAngle() == pytest.approx(53.13)


def test_the_far_plane_grows_with_the_distance_but_never_shrinks_past_a_floor():
    near = vtk.vtkCamera()
    far = vtk.vtkCamera()

    transform.apply_pose(near, pose_looking_along_x(), 53.13, 1.0)
    transform.apply_pose(far, pose_looking_along_x(), 53.13, 50.0)

    assert near.GetClippingRange() == pytest.approx([0.1, 100.0])
    assert far.GetClippingRange() == pytest.approx([0.1, 500.0])


def test_a_pose_taken_off_a_camera_frames_the_same_shot():
    """The round trip apply_pose -> pose_from_camera must be the identity."""
    camera = vtk.vtkCamera()
    original = pose_looking_along_x()
    transform.apply_pose(camera, original, 53.13, 10.0)

    assert transform.pose_from_camera(camera) == pytest.approx(original, abs=1e-9)


def test_the_pose_is_a_right_handed_frame_whatever_the_up_hint_was():
    """View up is a hint and need not be square to the view direction."""
    camera = vtk.vtkCamera()
    camera.SetPosition(1.0, 2.0, 3.0)
    camera.SetFocalPoint(4.0, 2.0, 3.0)
    camera.SetViewUp(0.3, 0.0, 1.0)  # leaning, not square

    pose = transform.pose_from_camera(camera)

    rotation = pose[:3, :3]
    assert rotation.T @ rotation == pytest.approx(np.eye(3), abs=1e-9)
    assert np.linalg.det(rotation) == pytest.approx(1.0)
    assert pose[:3, 3] == pytest.approx([1.0, 2.0, 3.0])


def test_looking_straight_up_still_gives_a_usable_frame():
    """The up hint is parallel to the view, so there is nothing to cross with."""
    camera = vtk.vtkCamera()
    camera.SetPosition(0.0, 0.0, 0.0)
    camera.SetFocalPoint(0.0, 0.0, 5.0)
    camera.SetViewUp(0.0, 0.0, 1.0)

    pose = transform.pose_from_camera(camera)

    rotation = pose[:3, :3]
    assert rotation.T @ rotation == pytest.approx(np.eye(3), abs=1e-9)
    assert pose[:3, 2] == pytest.approx([0.0, 0.0, -1.0])


def test_looking_straight_along_x_picks_the_other_tie_breaker():
    """The fallback axis must itself be off the view direction."""
    camera = vtk.vtkCamera()
    camera.SetPosition(0.0, 0.0, 0.0)
    camera.SetFocalPoint(5.0, 0.0, 0.0)
    camera.SetViewUp(1.0, 0.0, 0.0)

    pose = transform.pose_from_camera(camera)

    rotation = pose[:3, :3]
    assert rotation.T @ rotation == pytest.approx(np.eye(3), abs=1e-9)
    assert pose[:3, 2] == pytest.approx([-1.0, 0.0, 0.0])
