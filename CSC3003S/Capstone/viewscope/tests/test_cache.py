# Unit tests for src/viewscope/data/cache.py

import vtk

import viewscope.data.cache as cache


def polydata() -> vtk.vtkPolyData:
    sphere = vtk.vtkSphereSource()
    sphere.Update()
    return sphere.GetOutput()


def image(dim: int = 8) -> vtk.vtkImageData:
    data = vtk.vtkImageData()
    data.SetDimensions(dim, dim, 1)
    data.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 3)
    return data


def source(tmp_path, body: str = "v 0 0 0\n"):
    """An OBJ and its MTL on disk, so the fingerprint has real files to read."""
    obj = tmp_path / "model.obj"
    obj.write_text(body)
    mtl = tmp_path / "model.mtl"
    mtl.write_text("newmtl material_0\n")
    return obj, mtl


def test_a_written_set_reads_back_with_its_textures(tmp_path):
    """The round trip the fast path depends on: geometry and texture both survive."""
    obj, mtl = source(tmp_path)
    cache.write_cache(obj, mtl, [(polydata(), image()), (polydata(), image())])

    cached = cache.cached_actors(obj, mtl)
    assert cached is not None and len(cached) == 2

    actors = cache.read_geometry_cache(cached)
    assert len(actors) == 2
    assert all(actor.GetTexture() is not None for actor in actors)
    assert all(actor.GetMapper().GetInput().GetNumberOfCells() for actor in actors)


def test_the_two_variants_do_not_collide_on_disk(tmp_path):
    """
    A capped set must never answer a full-resolution read. They share a
    fingerprint - it is the same OBJ - and are told apart by variant alone.
    """
    obj, mtl = source(tmp_path)
    cache.write_cache(obj, mtl, [(polydata(), image(8))], cache.VARIANT_CAPPED)

    assert cache.cached_actors(obj, mtl, cache.VARIANT_CAPPED) is not None
    assert cache.cached_actors(obj, mtl, cache.VARIANT_FULL) is None

    cache.write_cache(obj, mtl, [(polydata(), image(16))], cache.VARIANT_FULL)

    capped = cache.cached_actors(obj, mtl, cache.VARIANT_CAPPED)
    full = cache.cached_actors(obj, mtl, cache.VARIANT_FULL)
    assert capped is not None and full is not None
    assert capped[0].geometry_path != full[0].geometry_path

    dims = [
        max(cache.read_geometry_cache(entry)[0].GetTexture().GetInput().GetDimensions()[:2])
        for entry in (capped, full)
    ]
    assert dims == [8, 16]


def test_a_stale_set_is_not_a_hit(tmp_path):
    """Rewriting the OBJ changes the fingerprint, so the old set is passed over."""
    obj, mtl = source(tmp_path)
    cache.write_cache(obj, mtl, [(polydata(), image())])
    assert cache.cached_actors(obj, mtl) is not None

    obj.write_text("v 1 1 1\nv 2 2 2\n")
    assert cache.cached_actors(obj, mtl) is None


def test_the_read_reports_progress_per_actor(tmp_path):
    """
    Without this the bar sits at 5% for the whole read - seconds on the capped
    set, and four times that on the full-resolution one - and reads as a hang.
    """
    obj, mtl = source(tmp_path)
    cache.write_cache(obj, mtl, [(polydata(), image()) for _ in range(3)])

    cached = cache.cached_actors(obj, mtl)
    assert cached is not None

    seen = []
    cache.read_geometry_cache(cached, lambda done, total: seen.append((done, total)))
    assert seen == [(1, 3), (2, 3), (3, 3)]


def test_the_read_still_works_without_a_progress_callback(tmp_path):
    """The callback is optional; nothing in cache.py may require one."""
    obj, mtl = source(tmp_path)
    cache.write_cache(obj, mtl, [(polydata(), image())])

    cached = cache.cached_actors(obj, mtl)
    assert cached is not None
    assert len(cache.read_geometry_cache(cached)) == 1


# -----------------------------------------------------------------------------
# The fingerprint
# -----------------------------------------------------------------------------


def test_a_source_with_no_material_still_fingerprints(tmp_path):
    """Not every OBJ has an MTL beside it."""
    obj = tmp_path / "model.obj"
    obj.write_text("v 0 0 0\n")

    cache.write_cache(obj, None, [(polydata(), image())])

    assert cache.cached_actors(obj, None) is not None


def test_a_material_that_is_not_there_is_left_out_of_the_fingerprint(tmp_path):
    """A path may be named without the file existing; that must not raise."""
    obj = tmp_path / "model.obj"
    obj.write_text("v 0 0 0\n")
    missing = tmp_path / "gone.mtl"

    cache.write_cache(obj, missing, [(polydata(), image())])

    assert cache.cached_actors(obj, missing) is not None


def test_changing_the_material_makes_the_old_set_stale(tmp_path):
    obj, mtl = source(tmp_path)
    cache.write_cache(obj, mtl, [(polydata(), image())])

    mtl.write_text("newmtl material_0\nKd 1 0 0\n")

    assert cache.cached_actors(obj, mtl) is None


# -----------------------------------------------------------------------------
# Where a loaded texture came from
# -----------------------------------------------------------------------------


def test_a_texture_read_from_a_file_reports_that_file(tmp_path):
    png = tmp_path / "skin.png"
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(png))
    writer.SetInputData(image())
    writer.Write()

    reader = vtk.vtkPNGReader()
    reader.SetFileName(str(png))
    texture = vtk.vtkTexture()
    texture.SetInputConnection(reader.GetOutputPort())

    assert cache.texture_source_path(texture) == png


def test_no_texture_has_no_source():
    assert cache.texture_source_path(None) is None


def test_a_texture_built_in_memory_has_no_source():
    """SetInputData leaves no reader behind to ask."""
    texture = vtk.vtkTexture()
    texture.SetInputData(image())

    assert cache.texture_source_path(texture) is None


def test_a_reader_that_has_no_file_name_yet_has_no_source():
    reader = vtk.vtkPNGReader()
    texture = vtk.vtkTexture()
    texture.SetInputConnection(reader.GetOutputPort())

    assert cache.texture_source_path(texture) is None


# -----------------------------------------------------------------------------
# Caches that are not hits
# -----------------------------------------------------------------------------


def test_a_source_that_has_never_been_cached_is_not_a_hit(tmp_path):
    obj, mtl = source(tmp_path)

    assert cache.cached_actors(obj, mtl) is None


def test_a_manifest_that_will_not_parse_is_not_a_hit(tmp_path):
    """A half-written file from an interrupted run reads as absent."""
    obj, mtl = source(tmp_path)
    cache.write_cache(obj, mtl, [(polydata(), image())])

    manifest = next((tmp_path / ".viewscope_cache").glob("*.json"))
    manifest.write_text("{ not json")

    assert cache.cached_actors(obj, mtl) is None


def test_a_set_missing_one_of_its_geometry_files_is_not_a_hit(tmp_path):
    """Partial is worse than absent: it would load half a model."""
    obj, mtl = source(tmp_path)
    cache.write_cache(obj, mtl, [(polydata(), image()), (polydata(), image())])

    next((tmp_path / ".viewscope_cache").glob("*.1.vtp")).unlink()

    assert cache.cached_actors(obj, mtl) is None


# -----------------------------------------------------------------------------
# Actors with no texture
# -----------------------------------------------------------------------------


def test_an_actor_with_no_texture_is_cached_without_one(tmp_path):
    obj, mtl = source(tmp_path)

    cache.write_cache(obj, mtl, [(polydata(), None)])

    cached = cache.cached_actors(obj, mtl)
    assert cached is not None
    assert cached[0].texture_path is None


def test_an_untextured_actor_reads_back_bare(tmp_path):
    obj, mtl = source(tmp_path)
    cache.write_cache(obj, mtl, [(polydata(), None)])

    cached = cache.cached_actors(obj, mtl)
    assert cached is not None

    actors = cache.read_geometry_cache(cached)
    assert actors[0].GetTexture() is None
    assert actors[0].GetMapper().GetInput().GetNumberOfCells()


def test_an_actor_whose_texture_file_has_gone_reads_back_bare(tmp_path):
    """The geometry is still good, so the set is still worth loading."""
    obj, mtl = source(tmp_path)
    cache.write_cache(obj, mtl, [(polydata(), image())])
    cached = cache.cached_actors(obj, mtl)
    assert cached is not None

    texture_path = cached[0].texture_path
    assert texture_path is not None
    texture_path.unlink()

    assert cache.read_geometry_cache(cached)[0].GetTexture() is None
