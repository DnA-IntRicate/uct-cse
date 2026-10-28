from typing import TYPE_CHECKING

from .structs import CameraInfo

if TYPE_CHECKING:
    from .controller import CameraController

__all__ = ["CameraController", "CameraInfo"]


def __getattr__(name: str):
    """Load the controller on demand.

    ``viewscope.data.store`` needs ``CameraInfo`` from this package, and the
    controller needs the store, so importing the controller here eagerly would
    close that loop while ``viewscope.data`` is still half built.
    """
    if name == "CameraController":
        from .controller import CameraController

        return CameraController
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
