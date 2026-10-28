"""
The full-resolution textured model and its loader.
"""

from __future__ import annotations

from pathlib import Path

import vtk
from PySide6.QtCore import QThread, Signal
from vtkmodules.vtkIOImport import vtkOBJImporter

import viewscope.data.cache as cache
from viewscope.config import GEOMETRY_COLOUR, PHOTO_MESH_DIR


def find_photo_mesh(data_dir) -> Path | None:
    """
    The full-resolution OBJ a bundle ships, or None when it ships none.
    Bundles are not required to carry one. Without it the camera view keeps
    the simplified mesh every other panel draws, which is the picture it has
    always shown.
    """
    if data_dir is None:
        return None

    folder = Path(data_dir) / PHOTO_MESH_DIR
    if not folder.is_dir():
        return None

    meshes = sorted(folder.glob("*.obj"))
    return meshes[0] if meshes else None


def find_materials(mesh_path: Path) -> Path | None:
    """
    The .mtl beside a model, by name where it matches and by folder where not.
    The name in the OBJ's own `mtllib` line would be authoritative, but it is
    written after the last vertex: on a model this size, finding it means
    reading the better part of a gigabyte to learn something the folder
    already says.
    """
    named = mesh_path.with_suffix(".mtl")
    if named.exists():
        return named

    materials = sorted(mesh_path.parent.glob("*.mtl"))
    return materials[0] if materials else None


class PhotoMesh:
    """
    The imported model, wearing the same face as MeshView.
    One actor per material, because the texture arrives as a set of tiles and
    an actor carries one texture at a time.
    """

    def __init__(self, actors: list[vtk.vtkActor]):
        self.actors = actors

        # What each actor was imported wearing, so geometry mode can put the
        # textures back afterwards.
        self._textures = [(actor, actor.GetTexture()) for actor in self.actors]

    @property
    def cells(self) -> int:
        """How many triangles came in, for the status line."""
        return sum(actor.GetMapper().GetInput().GetNumberOfCells() for actor in self.actors)

    def add_to(self, renderer: vtk.vtkRenderer):
        for actor in self.actors:
            renderer.AddActor(actor)

    def remove_from(self, renderer: vtk.vtkRenderer):
        for actor in self.actors:
            renderer.RemoveActor(actor)

    def set_visible(self, visible: bool):
        for actor in self.actors:
            actor.SetVisibility(visible)

    def clone(self) -> PhotoMesh:
        """
        A second set of actors over the same triangles and the same images.
        Two renderers cannot share one set of actors: hiding the mesh in one
        panel would hide it in the other, and each render window uploads to
        its own GL context regardless. What is worth sharing is what was
        expensive to produce - the parsed geometry and the decoded textures -
        and both are held here by reference rather than copied.
        """
        actors = []
        for src_actor, texture in self._textures:
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(src_actor.GetMapper().GetInput())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

            if texture is not None:
                shared = vtk.vtkTexture()
                shared.SetInputData(texture.GetInput())
                shared.SetInterpolate(texture.GetInterpolate())
                shared.SetMipmap(texture.GetMipmap())
                shared.SetRepeat(texture.GetRepeat())
                shared.SetEdgeClamp(texture.GetEdgeClamp())
                shared.SetMaximumAnisotropicFiltering(texture.GetMaximumAnisotropicFiltering())
                actor.SetTexture(shared)

            actors.append(actor)

        return PhotoMesh(actors)

    def show_textured(self):
        """
        The model as it was photographed, with no shading of ours on top.
        These textures are the survey photographs themselves: the light in
        them was real light, already in the picture. Lighting them a second
        time is what blew the panel out, and there is nothing to recover
        once a texel has been driven past white. Ambient alone, at full
        strength, hands each one to the screen as it was captured.
        """
        for actor, texture in self._textures:
            if texture is not None:
                actor.SetTexture(texture)

            prop = actor.GetProperty()
            actor.GetMapper().ScalarVisibilityOn()
            prop.SetRepresentationToSurface()
            prop.SetAmbient(1.0)
            prop.SetAmbientColor(1.0, 1.0, 1.0)
            prop.SetDiffuse(0.0)
            prop.SetSpecular(0.0)
            prop.EdgeVisibilityOff()

    def show_geometry(self):
        """
        The shape on its own, textures off.
        No wireframe over it, unlike the simplified mesh: seven million
        triangles of edge are a solid block of colour and cost a second a
        frame to draw.
        """
        for actor in self.actors:
            prop = actor.GetProperty()
            # actor.SetTexture(vtk.vtkTexture())
            actor.GetMapper().ScalarVisibilityOff()
            prop.SetRepresentationToSurface()

            # Lit the usual way here, unlike the textured mode: with the
            # photographs off there is no baked light left, and shading is
            # the only thing giving the shape any relief.
            prop.SetAmbient(0.0)
            prop.SetDiffuse(1.0)
            prop.SetSpecular(0.0)
            prop.SetColor(*GEOMETRY_COLOUR)
            prop.EdgeVisibilityOff()


# TODO(Adam): Ideally, this class should be moved to viewscope.data.loader.
class PhotoMeshLoader(QThread):
    """
    Reads the full-resolution model off the interface thread.
    vtkOBJImporter is what makes this worth doing at all: it reads the
    gigabyte OBJ, its materials and its textures in a handful of seconds,
    where the trimesh path the planning library uses takes minutes.
    """

    MAX_TEXTURE_DIM: int = 4096

    loaded = Signal(object)
    failed = Signal(str)
    progress = Signal(str, int)

    def __init__(self, path: Path, parent=None, *, full_resolution: bool = False):
        """
        full_resolution reads the model exactly as it was shipped: textures at
        their own size rather than capped at MAX_TEXTURE_DIM. It is cached like
        any other read, but under its own variant: the two hold different
        pixels for the same OBJ, and a capped set handed to this path would
        quietly give it the downscaled textures it was opened to avoid.
        """
        super().__init__(parent)
        self.path = Path(path)
        self.full_resolution = full_resolution

        # Built here on the interface thread, and only filled by run(). The
        # importer wants a render window to hang its actors on, and a render
        # window is not a thing to construct off the main thread; this one is
        # offscreen and never drawn either way.
        self._renderer = vtk.vtkRenderer()
        self._window = vtk.vtkRenderWindow()
        self._window.SetOffScreenRendering(1)
        self._window.AddRenderer(self._renderer)

    @property
    def _variant(self) -> str:
        """Which cached set this read belongs to."""
        return cache.VARIANT_FULL if self.full_resolution else cache.VARIANT_CAPPED

    def run(self):
        try:
            self.loaded.emit(self._read())
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")

    def finalize_window(self):
        """Release the offscreen GL context. Must be called from the main thread!"""
        self._window.Finalize()

    def _read(self) -> PhotoMesh:
        materials = find_materials(self.path)

        # A previous load already paid the ASCII-parse cost once; skip
        # vtkOBJImporter entirely and read the cached geometry back in,
        # reapplying whatever textures the importer would have assigned.
        self.progress.emit("Checking cache...", 0)
        cached_mesh = self._try_read_cache(materials)
        if cached_mesh is not None:
            self.progress.emit("Loaded from cache", 100)
            return cached_mesh

        self.progress.emit("Parsing model geometry...", 1)

        importer = vtkOBJImporter()
        importer.SetFileName(str(self.path))
        importer.SetRenderWindow(self._window)

        if materials is not None:
            importer.SetFileNameMTL(str(materials))
            importer.SetTexturePath(str(self.path.parent))

        # NOTE(Adam): Ok so this is insanely flipping slow... Nice
        #             (Its an OBJ file)
        importer.Update()

        actors = self._imported_actors()
        if not actors:
            raise ValueError(f"{self.path.name} imported no geometry!")

        self.progress.emit(f"Decoding {len(actors)} textures...", 40)

        cached_textures: list[tuple[vtk.vtkPolyData, vtk.vtkImageData | None]] = []
        for i, actor in enumerate(actors):
            image_to_cache: vtk.vtkImageData | None = None

            actor.GetMapper().Update()
            texture = actor.GetTexture()

            if texture is not None:
                texture.Update()
                texture.InterpolateOn()

                # NOTE(Adam): We limit the max resolution of loaded textures here
                #             to avoid exorbitant RAM usage and to reduce GPU load.
                image = texture.GetInput()
                if image is not None and not self.full_resolution:
                    max_dim = max(image.GetDimensions()[:2])
                    if max_dim > self.MAX_TEXTURE_DIM:
                        scale = self.MAX_TEXTURE_DIM / max_dim

                        resize = vtk.vtkImageResize()
                        resize.SetInputData(image)
                        resize.SetOutputDimensions(
                            int(image.GetDimensions()[0] * scale),
                            int(image.GetDimensions()[1] * scale),
                            1,
                        )
                        resize.Update()

                        resized = resize.GetOutput()
                        texture.SetInputData(resized)

                # Whatever the texture ended up wearing is what the cache has to
                # hand back. Reading it off the texture here rather than only
                # inside the resize branch is what keeps a texture already under
                # the cap - and every texture on the full-resolution path - from
                # being cached as no texture at all.
                image_to_cache = texture.GetInput()

            cached_textures.append((actor.GetMapper().GetInput(), image_to_cache))
            self._renderer.RemoveActor(actor)

            # Reflects how many textures have been processed so far.
            done = i + 1
            pct = 40 + int(60 * done / len(actors))
            self.progress.emit(f"Decoding textures ({done}/{len(actors)})...", pct)

        # Pay the price of the slow ASCII parse forward: every load of this exact OBJ/MTL
        # after this one, read the same way, skips vtkOBJImporter entirely.
        cache.write_cache(self.path, materials, cached_textures, self._variant)
        return PhotoMesh(actors)

    def _try_read_cache(self, materials: Path | None = None) -> PhotoMesh | None:
        """
        A PhotoMesh rebuilt from a previous slow parse of this exact OBJ read
        this same way, or None if there's no valid cache.
        """
        cached = cache.cached_actors(self.path, materials, self._variant)
        if cached is None:
            return None

        self.progress.emit("Reading cache...", 5)

        def report(done: int, total: int):
            # Spans the same 5-100 the importer's own pass reports over, so the
            # bar moves at a steady rate whichever way the model arrives.
            self.progress.emit(f"Reading cache ({done}/{total})...", 5 + int(95 * done / total))

        actors = cache.read_geometry_cache(cached, report)
        return PhotoMesh(actors)

    def _imported_actors(self) -> list[vtk.vtkActor]:
        """
        Every actor the importer made, minus the empty ones.
        A material the model declares but never uses still arrives as an
        actor, holding no triangles.
        """
        collection = self._renderer.GetActors()
        collection.InitTraversal()

        actors = []
        for _ in range(collection.GetNumberOfItems()):
            actor = collection.GetNextActor()
            mapper = actor.GetMapper()
            if mapper is None:
                continue

            mapper.Update()
            if mapper.GetInput().GetNumberOfCells():
                actors.append(actor)

        return actors
