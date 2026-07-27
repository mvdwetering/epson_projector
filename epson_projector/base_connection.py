"""Base class for Epson projector connections (HTTP, Serial, TCP)."""
import abc
import logging
from typing import final

_LOGGER = logging.getLogger(__name__)
class BaseProjectorConnection(abc.ABC):
    """
    Abstract base class for Epson projector connections.
    """

    @abc.abstractmethod
    async def get_property(self, command, timeout):
        """Get property state from device."""
        pass

    @abc.abstractmethod
    async def send_command(self, command, timeout):
        """Send command to Epson."""
        pass

    @abc.abstractmethod
    async def send_request(self, *args, **kwargs):
        """Send request to Epson."""
        pass

    @abc.abstractmethod
    async def get_serial_number(self):
        """Get serial number from device."""
        pass

    @abc.abstractmethod
    def close(self):
        """Close the connection."""
        pass

    # Proposed API, alternative to send_command, send_request, and get_property

    @final
    async def send_escvp21(self, command:str) -> str:
        """
        Send ESC/VP21 command to Epson and return the response. Just transmission, no interpretation.
        Will lock the connection for the duration of the command, so it is safe to call from multiple tasks.

        :param str command: Plain ESC/VP21 command to send (without any \r or :) e.g. "PWR?" or "SOURCE 30"
        :return: Response from the projector as a string (without trailing \r or :)
        """

        if not hasattr(self, '_send_escvp21_lock'):
            import asyncio
            self._send_escvp21_lock = asyncio.Lock()

        _LOGGER.debug(f"Before lock: {command}")  # noqa: SLF001
        async with self._send_escvp21_lock:
            _LOGGER.debug(f"In lock: {command}")  # noqa: SLF001
            return await self._send_escvp21_impl(command)
        _LOGGER.debug(f"After lock: {command}")  # noqa: SLF001

    @abc.abstractmethod
    async def _send_escvp21_impl(self, command:str) -> str:
        """
        Send ESC/VP21 command implementation for specific transports
        """
        pass

    # A "medium level" API
    #
    # Not sure I like it yet.
    # There are get and set commands with multiple parameters, how would those work?
    # You might as well build the string yourself at that point and send it with send_escvp21.
    # The get does have the nice convenience of removing the "COMMAND=" prefix if it was there
    # It might reduce the number of errors when implementing commands and have consistent logging.

    @final
    async def get(self, command: str) -> str | None:
        """
        Get property value. The "COMMAND=" prefix is removed if it was there.
        Returns None if the projector returned "ERR" for the command.
        """

        response = await self.send_escvp21(f"{command}?")

        _LOGGER.debug(f"get({command}) response: {response}")  # noqa: SLF001

        prefix = f"{command}="
        if response.startswith(prefix):
            response = response[len(prefix):]

        if response == "ERR":
            return None

        return response

    @final
    async def set(self, command:str, value:str) -> None:
        """Set property value."""
        await self.send_escvp21(f"{command} {value}")
