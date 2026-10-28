"""
Qt/VTK compatibility initialization.

This is a small bootstrap module that imports vtkmodules.qt
and sets some of qt's configuration.

VTK must be told which Qt binding to use before importing any VTK module
that initializes Qt integration.
"""

import vtkmodules.qt

vtkmodules.qt.PyQtImpl = "PySide6"
