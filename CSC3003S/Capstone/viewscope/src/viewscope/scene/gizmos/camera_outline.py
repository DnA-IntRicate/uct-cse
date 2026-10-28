from __future__ import annotations

import vtk


class CameraOutline:
    """The outline for a selected camera. Working with its position and not the camera itself."""

    def __init__(self):
        self.outline_actor = None

    def build(self, renderer: vtk.vtkRenderer, position: tuple[float, float, float]):
        """
        Spawn the outline at the position of the selected camera. This doesn't
        modify the camera glyph at all.
        """
        tempActor = vtk.vtkCubeSource()
        tempActor.SetCenter(position[0], position[1], position[2])
        tempActor.SetXLength(2)
        tempActor.SetYLength(2)
        tempActor.SetZLength(2)

        outlineFilter = vtk.vtkOutlineFilter()
        outlineFilter.SetInputConnection(tempActor.GetOutputPort())

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(outlineFilter.GetOutputPort())

        self.outline_actor = vtk.vtkActor()
        self.outline_actor.SetMapper(mapper)
        colors = vtk.vtkNamedColors()  # Need to create instance first, before getting color
        self.outline_actor.GetProperty().SetColor(colors.GetColor3d("Gold"))
        self.outline_actor.GetProperty().SetLineWidth(4.0)

        renderer.AddActor(self.outline_actor)

    def remove_from(self, renderer: vtk.vtkRenderer):
        if self.outline_actor is not None:
            renderer.RemoveActor(self.outline_actor)
            self.outline_actor = None
