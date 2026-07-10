from __future__ import annotations

import abc

from enum import Enum
from typing import Callable, Generic, Protocol, TypeVar, cast, overload

from .base_connection import BaseProjectorConnection
from .enums import CMode, PowerStatus, Source

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



# Protocols for type checking of mixins.

class _SupportsOperatorMixin(Protocol):
    _connection: BaseProjectorConnection
    cmd: str

class _SupportsSetGetOperatorMixin(Protocol[T_co]):
    _connection: BaseProjectorConnection
    cmd: str

    @property
    def _value_type(self) -> Callable[[str], T_co]: ...

# Operator mixins

class IncMixin:
    async def inc(self: _SupportsOperatorMixin) -> None:
        await self._connection.set(self.cmd, "INC")

class DecMixin:
    async def dec(self: _SupportsOperatorMixin) -> None:
        await self._connection.set(self.cmd, "DEC")

class InitMixin:
    async def init(self: _SupportsOperatorMixin) -> None:
        await self._connection.set(self.cmd, "INIT")

class MaxMixin:
    async def max(self: _SupportsOperatorMixin) -> None:
        await self._connection.set(self.cmd, "MAX")

class MinMixin:
    async def min(self: _SupportsOperatorMixin) -> None:
        await self._connection.set(self.cmd, "MIN")

class GetMixin(Generic[T]):
    """Mixin that implements get() by calling _value_type on the raw response."""
    _value_type: Callable[[str], T]

    async def get(self: _SupportsSetGetOperatorMixin[T]) -> T | None:
        value = await self._connection.get(self.cmd)
        if value is not None:
            return self._value_type(value)
        return None

class SetEnumMixin:
    """Mixin for commands whose set value is an enum (passes value.value)."""
    async def set(self: _SupportsSetGetOperatorMixin[E], value: E) -> None:
        await self._connection.set(self.cmd, value.value)

class SetValueMixin:
    """Mixin for commands whose set value is passed through directly."""
    async def set(self: _SupportsSetGetOperatorMixin[T], value: T) -> None:
        await self._connection.set(self.cmd, value)

# Commands

class ProjectorCommand:
    cmd: str

    def __init__(self, connection: BaseProjectorConnection):
        self._connection = connection

# "manual" implementaitons

class PwrCommand(ProjectorCommand):
    cmd = "PWR"

    async def on(self) -> None:
        await self._connection.set(self.cmd, "ON")

    async def off(self) -> None:
        await self._connection.set(self.cmd, "OFF")

    async def get(self) -> PowerStatus | None:
        value = await self._connection.get(self.cmd) 
        if value is not None:
            return PowerStatus(value)
        return None

class SourceCommand(ProjectorCommand):
    cmd = "SOURCE"

    async def get(self) -> Source | None:
        value = await self._connection.get(self.cmd)
        if value is not None:
            return Source(value)
        return None

    async def set(self, source: Source) -> None:
        await self._connection.set(self.cmd, source.value)

# Mixin based implementations
# Less typing, more magic

class CModeCommand(ProjectorCommand, GetMixin[CMode], SetEnumMixin):
    cmd = "CMODE"
    _value_type = CMode


class VolCommand(ProjectorCommand, GetMixin[int], SetValueMixin, IncMixin, DecMixin, InitMixin):
    cmd = "VOL"
    _value_type = int


# Avoid repeated long definitions
class IntRangeBaseCommand(abc.ABC, ProjectorCommand, GetMixin[int], SetValueMixin, IncMixin, DecMixin, InitMixin):
    _value_type = int
   
class BrightCommand(IntRangeBaseCommand):
    cmd = "BRIGHT"

class ContrastCommand(IntRangeBaseCommand):
    cmd = "CONTRAST"

class DensityCommand(IntRangeBaseCommand):
    cmd = "DENSITY"
