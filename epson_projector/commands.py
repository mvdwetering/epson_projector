from __future__ import annotations

import abc

from enum import StrEnum
from typing import Callable, Generic, Protocol, TypeVar

from .base_connection import BaseProjectorConnection
from .enums import CMode, PowerStatus, Source

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
E = TypeVar("E", bound=StrEnum)

# Protocols for type checking of mixins.

class _SupportsOperatorMixin(Protocol):
    _connection: BaseProjectorConnection
    cmd: str

class _SupportsSetAndOrGetOperatorMixin(Protocol[T_co]):
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

class GetMixin:
    """Mixin that implements get() by calling _value_type on the raw response."""

    async def get(self: _SupportsSetAndOrGetOperatorMixin[T]) -> T | None:
        value = await self._connection.get(self.cmd)
        if value is not None:
            return self._value_type(value)
        return None

class SetEnumMixin:
    """Mixin for commands whose set value is an enum (passes value.value)."""
    async def set(self: _SupportsSetAndOrGetOperatorMixin[E], value: E) -> None:
        await self._connection.set(self.cmd, value.value)

class SetValueMixin:
    """Mixin for commands whose set value is passed through directly."""
    async def set(self: _SupportsSetAndOrGetOperatorMixin[T], value: T) -> None:
        await self._connection.set(self.cmd, str(value))

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

class CModeCommand(ProjectorCommand, GetMixin, SetEnumMixin):
    cmd = "CMODE"
    _value_type = CMode


class VolCommand(ProjectorCommand, GetMixin, SetValueMixin, IncMixin, DecMixin, InitMixin):
    cmd = "VOL"
    _value_type = int


# Avoid repeated long definitions
class IntRangeBaseCommand(abc.ABC, ProjectorCommand, GetMixin, SetValueMixin, IncMixin, DecMixin, InitMixin):
    _value_type = int
   
class BrightCommand(IntRangeBaseCommand):
    cmd = "BRIGHT"

class ContrastCommand(IntRangeBaseCommand):
    cmd = "CONTRAST"

class DensityCommand(IntRangeBaseCommand):
    cmd = "DENSITY"
