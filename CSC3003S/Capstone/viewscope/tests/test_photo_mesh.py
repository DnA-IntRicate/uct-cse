"""Unit tests for src/viewscope/scene/photo_mesh.py.

The importer is the point of this module, so it is really run: a small
textured OBJ is written to a temporary folder and read through
vtkOBJImporter, cache and all. The render window it hangs its actors on is
offscreen and never drawn.
"""

import pytest
import vtk
from PIL import Image

import viewscope.data.cache as cache
from viewscope.config import GEOMETRY_COLOUR, PHOTO_MESH_DIR
from viewscope.scene.photo_mesh import (
    PhotoMesh,
    PhotoMeshLoader,
    find_materials,
    find_photo_mesh,
)


@pytest.fixture
def model(tmp_path):
    """A two-material textured quad: the smallest thing the importer splits."""
    folder = tmp_path / "Mesh"
    folder.mkdir()

    (folder / "model.obj").write_text(
        "mtllib model.mtl\n"
        "v 0 0 0\nv 1 0 0\nv 0 1 0\nv 1 1 0\n"
        "vt 0 0\nvt 1 0\nvt 0 1\nvt 1 1\n"
        "usemtl mat_a\nf 1/1 2/2 3/3\n"
        "usemtl mat_b\nf 2/2 4/4 3/3\n"
    )
    (folder / "model.mtl").write_text(
        "newmtl mat_a\nKd 1 1 1\nmap_Kd tex_a.png\nnewmtl mat_b\nKd 1 0 0\nmap_Kd tex_b.png\n"
    )
    Image.new("RGB", (8, 8), (255, 0, 0)).save(folder / "tex_a.png")
    Image.new("RGB", (8, 8), (0, 255, 0)).save(folder / "tex_b.png")

    return folder / "model.obj"


@pytest.fixture
def loader(model):
    made = []

    def build(**kwargs):
        one = PhotoMeshLoader(model, **kwargs)
        made.append(one)
        return one

    yield build
    for one in made:
        one.finalize_window()


@pytest.fixture
def mesh(loader):
    return loader()._read()


# -----------------------------------------------------------------------------
# Finding the model and its materials
# -----------------------------------------------------------------------------


def test_a_bundle_that_ships_a_full_resolution_model_reports_it(model, tmp_path):
    assert find_photo_mesh(tmp_path) == model


def test_a_bundle_that_ships_none_reports_none(tmp_path):
    """Bundles are not required to carry one."""
    assert find_photo_mesh(tmp_path) is None


def test_no_bundle_at_all_reports_none():
    assert find_photo_mesh(None) is None


def test_a_mesh_folder_holding_no_model_reports_none(tmp_path):
    (tmp_path / PHOTO_MESH_DIR).mkdir()

    assert find_photo_mesh(tmp_path) is None


def test_the_first_of_several_models_is_the_one_taken(model, tmp_path):
    (model.parent / "another.obj").write_text("v 0 0 0\n")

    assert find_photo_mesh(tmp_path) == model.parent / "another.obj"


def test_the_material_beside_the_model_is_found_by_name(model):
    assert find_materials(model) == model.with_suffix(".mtl")


def test_a_material_under_another_name_is_found_in_the_folder(model):
    """The mtllib line is authoritative but sits past the last vertex."""
    model.with_suffix(".mtl").rename(model.parent / "textures.mtl")

    assert find_materials(model) == model.parent / "textures.mtl"


def test_a_model_with_no_material_at_all_reports_none(model):
    model.with_suffix(".mtl").unlink()

    assert find_materials(model) is None


# -----------------------------------------------------------------------------
# Reading the model
# -----------------------------------------------------------------------------


def test_the_model_comes_in_as_one_actor_per_material(mesh):
    assert len(mesh.actors) == 2
    assert mesh.cells == 2


def test_every_actor_comes_in_wearing_its_texture(mesh):
    assert all(actor.GetTexture() is not None for actor in mesh.actors)


def test_a_model_with_no_material_still_reads(model, loader):
    model.with_suffix(".mtl").unlink()

    mesh = loader()._read()

    assert mesh.cells == 2


def test_a_model_that_imports_no_geometry_is_refused(tmp_path, loader):
    empty = tmp_path / "Mesh" / "empty.obj"
    empty.write_text("v 0 0 0\n")

    with pytest.raises(ValueError, match="imported no geometry"):
        PhotoMeshLoader(empty)._read()


def test_the_read_reports_its_progress(model, loader):
    one = loader()
    seen = []
    one.progress.connect(lambda message, pct: seen.append((message, pct)))

    one._read()

    assert seen[0][1] == 0
    assert seen[-1][1] == 100
    assert [pct for _, pct in seen] == sorted(pct for _, pct in seen)


def test_run_hands_the_mesh_back(loader):
    one = loader()
    got, failed = [], []
    one.loaded.connect(got.append)
    one.failed.connect(failed.append)

    one.run()

    assert len(got) == 1 and failed == []


def test_run_reports_the_failure_rather_than_raising(tmp_path):
    """The thread has nowhere to raise to."""
    one = PhotoMeshLoader(tmp_path / "nothing.obj")
    got, failed = [], []
    one.loaded.connect(got.append)
    one.failed.connect(failed.append)

    one.run()

    assert got == [] and len(failed) == 1
    one.finalize_window()


# -----------------------------------------------------------------------------
# Texture size
# -----------------------------------------------------------------------------


def test_a_texture_over_the_cap_is_shrunk(model, loader, monkeypatch):
    """Full size textures would cost more RAM than the panel is worth."""
    monkeypatch.setattr(PhotoMeshLoader, "MAX_TEXTURE_DIM", 4)

    mesh = loader()._read()

    for actor in mesh.actors:
        assert max(actor.GetTexture().GetInput().GetDimensions()[:2]) == 4


def test_a_texture_already_under_the_cap_is_left_alone(mesh):
    for actor in mesh.actors:
        assert max(actor.GetTexture().GetInput().GetDimensions()[:2]) == 8


def test_the_full_resolution_read_leaves_the_textures_at_their_own_size(model, loader, monkeypatch):
    monkeypatch.setattr(PhotoMeshLoader, "MAX_TEXTURE_DIM", 4)

    mesh = loader(full_resolution=True)._read()

    for actor in mesh.actors:
        assert max(actor.GetTexture().GetInput().GetDimensions()[:2]) == 8


# -----------------------------------------------------------------------------
# The cache
# -----------------------------------------------------------------------------


def test_the_two_reads_are_cached_apart(model, loader):
    capped = loader()
    full = loader(full_resolution=True)

    assert capped._variant == cache.VARIANT_CAPPED
    assert full._variant == cache.VARIANT_FULL


def test_a_second_read_comes_off_the_cache(model, loader):
    loader()._read()

    one = loader()
    seen = []
    one.progress.connect(lambda message, pct: seen.append(message))
    mesh = one._read()

    assert "Loaded from cache" in seen
    assert "Parsing model geometry..." not in seen
    assert mesh.cells == 2


def test_a_cached_read_keeps_the_textures(model, loader):
    loader()._read()

    mesh = loader()._read()

    assert all(actor.GetTexture() is not None for actor in mesh.actors)


def test_a_capped_cache_does_not_answer_a_full_resolution_read(model, loader):
    """It holds the downscaled pixels the full read was opened to avoid."""
    loader()._read()

    one = loader(full_resolution=True)
    seen = []
    one.progress.connect(lambda message, pct: seen.append(message))
    one._read()

    assert "Parsing model geometry..." in seen


def test_the_cached_read_reports_its_progress(model, loader):
    loader()._read()

    one = loader()
    seen = []
    one.progress.connect(lambda message, pct: seen.append((message, pct)))
    one._read()

    reading = [pct for message, pct in seen if message.startswith("Reading cache (")]
    assert reading and min(reading) >= 5 and max(reading) <= 100


# -----------------------------------------------------------------------------
# Actors the importer leaves behind
# -----------------------------------------------------------------------------


def test_a_material_that_is_declared_but_never_used_is_dropped(model, loader):
    """It still arrives as an actor, holding no triangles."""
    text = model.with_suffix(".mtl").read_text()
    model.with_suffix(".mtl").write_text(text + "newmtl unused\nKd 0 0 1\n")

    assert len(loader()._read().actors) == 2


def test_an_actor_with_no_mapper_is_passed_over(loader):
    one = loader()
    one._renderer.AddActor(vtk.vtkActor())

    assert one._imported_actors() == []


# -----------------------------------------------------------------------------
# Showing the model
# -----------------------------------------------------------------------------


def test_the_model_goes_on_and_comes_off_the_renderer(mesh):
    renderer = vtk.vtkRenderer()

    mesh.add_to(renderer)
    assert renderer.GetActors().GetNumberOfItems() == 2

    mesh.remove_from(renderer)
    assert renderer.GetActors().GetNumberOfItems() == 0


def test_the_model_can_be_hidden_and_shown(mesh):
    mesh.set_visible(False)
    assert all(actor.GetVisibility() == 0 for actor in mesh.actors)

    mesh.set_visible(True)
    assert all(actor.GetVisibility() == 1 for actor in mesh.actors)


def test_the_textured_view_is_ambient_only(mesh):
    """The photographs already hold real light; lighting them again blows them out."""
    mesh.show_textured()

    for actor in mesh.actors:
        prop = actor.GetProperty()
        assert prop.GetAmbient() == pytest.approx(1.0)
        assert prop.GetDiffuse() == pytest.approx(0.0)
        assert prop.GetSpecular() == pytest.approx(0.0)
        assert actor.GetTexture() is not None


def test_the_geometry_view_turns_the_photographs_off_and_lights_it_normally(mesh):
    mesh.show_geometry()

    for actor in mesh.actors:
        prop = actor.GetProperty()
        assert prop.GetAmbient() == pytest.approx(0.0)
        assert prop.GetDiffuse() == pytest.approx(1.0)
        assert prop.GetColor() == pytest.approx(GEOMETRY_COLOUR, abs=1 / 255)
        assert actor.GetMapper().GetScalarVisibility() == 0


def test_the_geometry_view_draws_no_wireframe(mesh):
    """Seven million triangles of edge is a solid block of colour."""
    mesh.show_geometry()

    assert all(actor.GetProperty().GetEdgeVisibility() == 0 for actor in mesh.actors)


def test_going_back_to_textured_puts_the_photographs_back(mesh):
    mesh.show_geometry()

    mesh.show_textured()

    assert all(actor.GetTexture() is not None for actor in mesh.actors)


def test_an_untextured_model_still_switches_between_the_two_views():
    bare = PhotoMesh([_actor_with_geometry()])

    bare.show_textured()
    assert bare.actors[0].GetTexture() is None

    bare.show_geometry()
    assert bare.actors[0].GetProperty().GetDiffuse() == pytest.approx(1.0)


# -----------------------------------------------------------------------------
# Cloning for a second panel
# -----------------------------------------------------------------------------


def test_a_clone_is_a_second_set_of_actors_over_the_same_triangles(mesh):
    """Two renderers cannot share one set: hiding it in one would hide both."""
    clone = mesh.clone()

    assert len(clone.actors) == len(mesh.actors)
    assert all(a is not b for a, b in zip(clone.actors, mesh.actors, strict=True))
    assert clone.cells == mesh.cells


def test_a_clone_shares_the_geometry_rather_than_copying_it(mesh):
    clone = mesh.clone()

    for original, copy in zip(mesh.actors, clone.actors, strict=True):
        assert copy.GetMapper().GetInput() is original.GetMapper().GetInput()


def test_a_clone_shares_the_decoded_images(mesh):
    clone = mesh.clone()

    for original, copy in zip(mesh.actors, clone.actors, strict=True):
        assert copy.GetTexture() is not original.GetTexture()
        assert copy.GetTexture().GetInput() is original.GetTexture().GetInput()


def test_hiding_a_clone_leaves_the_original_showing(mesh):
    clone = mesh.clone()

    clone.set_visible(False)

    assert all(actor.GetVisibility() == 1 for actor in mesh.actors)


def test_an_untextured_model_clones_without_a_texture():
    bare = PhotoMesh([_actor_with_geometry()])

    clone = bare.clone()

    assert clone.actors[0].GetTexture() is None


def _actor_with_geometry() -> vtk.vtkActor:
    source = vtk.vtkSphereSource()
    source.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(source.GetOutput())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor
