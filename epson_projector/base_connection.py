"""Base class for Epson projector connections (HTTP, Serial, TCP)."""
import abc

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

    @abc.abstractmethod
    async def send_escvp21(self, command:str) -> str:
        """
        Send ESC/VP21 command to Epson and return the response. Just transmission, no interpretation.

        :param str command: Plain ESC/VP21 command to send (without any \r or :) e.g. "PWR?" or "SOURCE 30"
        :return: Response from the projector as a string (without trailing \r or :)
        """
        pass
