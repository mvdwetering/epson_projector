"""Python library to control Epson projector."""

from epson_projector.error import ProjectorError, ProjectorUnavailableError

from epson_projector.projector import Projector
from epson_projector.enums import KeyCodes

from epson_projector.version import __version__

__all__ = [
    "Projector",
    "KeyCodes",
    "ProjectorError",
    "ProjectorUnavailableError",
]