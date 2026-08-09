from __future__ import annotations

import abc

import asyncio
from enum import StrEnum
import time
from typing import Callable, Protocol, TypeVar

from .base_connection import BaseProjectorConnection
from .enums import CMode, Illuminance, ImgProc, PowerStatus, Source

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
        # HTTP and ESC/VP.net stop responding when immediately executing commands 
        # after off command returned with : These protocols return fast/immediately after sending OFF
        # Serial is fine with it, but takes about 4 seconds to return/complete. 
        await self._connection.set(self.cmd, "OFF", min_duration=10)

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

# Other commands not used in HA, but that are mentioned in the const file

class ImgProcCommand(ProjectorCommand, GetMixin, SetEnumMixin, InitMixin):
    cmd = "IMGPROC"
    _value_type = ImgProc

class IlluminanceCommand(ProjectorCommand, GetMixin, SetEnumMixin, InitMixin):
    cmd = "ILLUMINANCE"
    _value_type = Illuminance


# What names to use for lens position commands?
# Manual uses terms: Load, Save, Erase, Reset is unclear what it means and there is Rename but dont see command for that
# Command names are: POPLP, PUSHLP, ERASELP
# Excel descriptions are: Call of lensposition, Registration of lensposition, Deletion of lensposition

class LensPositionLoadCommand(ProjectorCommand):
    cmd = "POPLP"

    async def set(self, slot: int) -> None:
        if slot < 1 or slot > 10:
            raise ValueError("Lens position slot must be between 1 and 10")
        return await self._connection.set(self.cmd, format(slot, "X"))

# class LensPositionSaveCommand(ProjectorCommand):
class SaveLensPositionCommand(LensPositionLoadCommand):
    cmd = "PUSHLP"

# The other lensposition commands are no in the const, but lets
# see how it would look like if they were there.
class LensPositionEraseCommand(ProjectorCommand):
    cmd = "ERASELP"

    # Need to allow for 0 to 10, as 0 is used to delete all positions
    # Maybe it could be its own command to avoid accidents? (implemented)
    # But it does not follow the pattern of 1 command class per ESC/VP21 command
    # Is that a problem?
    async def set(self, slot: int) -> None:
        if slot < 0 or slot > 10:
            raise ValueError("Lens position slot must be between 1 and 10")
        return await self._connection.set(self.cmd, format(slot, "X"))

class LensPositionEraseAllCommand(ProjectorCommand):
    cmd = "ERASELP"

    # Slot 0 is all
    async def set(self) -> None:
        return await self._connection.set(self.cmd, "00")

# Could also make it fancier by having a LensPosititionCommand with "subcommands"
# But doing it like this results in a bit weird usage by having to call set on them.
#
# await projector.lens_position.save.set(1)
# await projector.lens_position.load.set(1)
# await projector.lens_position.erase.set(1)
# await projector.lens_position.erase_all.set()
class LensPositionGroupCommand():
    def __init__(self, connection: BaseProjectorConnection):
        self.load = LensPositionLoadCommand(connection)
        self.save = SaveLensPositionCommand(connection)
        self.erase = LensPositionEraseCommand(connection)
        self.erase_all = LensPositionEraseAllCommand(connection)

# Alternatively, could make it like this
# Which I think looks nicer/makes more sense, 
# but it is not following the normal ESC/VP21 command pattern with set/get
#
# await projector.lens_position.save(1)
# await projector.lens_position.load(2)
# await projector.lens_position.erase(3)
# await projector.lens_position.erase_all()
class LensPositionCommandAlt(ProjectorCommand):

    async def save(self, slot: int) -> None:
        if slot < 1 or slot > 10:
            raise ValueError("Lens position slot must be between 1 and 10")
        return await self._connection.set("PUSHLP", format(slot, "X"))

    async def load(self, slot: int) -> None:
        if slot < 1 or slot > 10:
            raise ValueError("Lens position slot must be between 1 and 10")
        return await self._connection.set("POPLP", format(slot, "X"))

    async def erase(self, slot: int) -> None:
        if slot < 1 or slot > 10:
            raise ValueError("Lens position slot must be between 1 and 10")
        return await self._connection.set("ERASELP", format(slot, "X"))

    async def erase_all(self) -> None:
        return await self._connection.set("ERASELP", "00")


# Memory commands are similar to lens position commands, but with a type parameter for the memory type

class LoadMemoryCommand(ProjectorCommand):
    cmd = "POPMEM"

    # There is no known projector that uses another memory type than 02
    # this is based on the info in the Excel sheet which contained 300 models that support POPMEM command
    # So lets just hardcode it to keep the API simple.
    async def set(self, slot: int) -> None:
        if slot < 1 or slot > 10:
            raise ValueError("Memory slot must be between 1 and 10")
        return await self._connection.set(self.cmd, f"02 {format(slot, 'X')}")
