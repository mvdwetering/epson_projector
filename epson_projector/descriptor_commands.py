"""
This module contains the descriptor classes for projector commands. 

These descriptors are used to define command attributes in the Projector class
on a class level.

There is no difference in usage from the non-descriptor approach. 
It is only in the definition that there is a difference. 

See below for both approaches.

class Projector:

    # Descriptor based
    power = ProjectorCommandDescriptor(PwrCommand)

    def __init__( ... params ... ):
        # More code

        # Non-descriptor based
        self.power = PwrCommand(self._projector)
"""

from __future__ import annotations

from enum import Enum
from typing import Generic, Protocol, TypeVar, cast, overload

from .commands import ProjectorCommand

from .base_connection import BaseProjectorConnection

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
E = TypeVar("E", bound=Enum)
T_Command = TypeVar("T_Command", bound="ProjectorCommand")

# Use protocol to avoid cyclic import of Projector class
# Maybe need to restructure the code if PoC works out
class _Projector(Protocol):
    _projector: BaseProjectorConnection

# Hmmm, this ended up looking way more complicated than initially envisioned
# Not sure if I like this. The more manual approach is a lot easier to understand, but more typing.
class ProjectorCommandDescriptor(Generic[T_Command]):
    def __init__(self, command_cls: type[T_Command]):
        self._command_cls = command_cls
        self._attr_name: str | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        # Cache per Projector instance so repeated access reuses the same command object.
        self._attr_name = f"__command_{name}"

    @overload
    def __get__(
        self, instance: None, objtype: type | None = None
    ) -> ProjectorCommandDescriptor[T_Command]: ...

    @overload
    def __get__(
        self, instance: _Projector, objtype: type | None = None
    ) -> T_Command: ...

    def __get__(
        self, instance: _Projector | None, objtype: type | None = None
    ) -> T_Command | ProjectorCommandDescriptor[T_Command]:
        if instance is None:
            return self

        if self._attr_name is not None and self._attr_name in instance.__dict__:
            return cast(T_Command, instance.__dict__[self._attr_name])

        command = self._command_cls(instance._projector)
        if self._attr_name is not None:
            instance.__dict__[self._attr_name] = command
        return command

    def __set__(self, instance: _Projector, value: object) -> None:
        msg = "Can not set this attribute"
        raise AttributeError(msg)
