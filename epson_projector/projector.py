"""Main of Epson projector module."""
import logging

import aiohttp

from .enums import PowerStatus, CMode

from .base_connection import BaseProjectorConnection
from .const import BUSY, TCP_PORT, HTTP_PORT, POWER
from .timeout import get_timeout

from .lock import Lock

_LOGGER = logging.getLogger(__name__)


class Projector:
    """
    Epson projector class.

    Control your projector with Python.
    """

    def __init__(
        self,
        connection: BaseProjectorConnection,
        timeout_scale=1.0,
    ):
        """
        Epson Projector controller.

        :param timeout_scale    Factor to multiply default timeouts by (for slow projectors)
        :param BaseProjectorConnection connection: Pre-initialized connection to use.

        """
        self._lock = Lock()
        self._type = type
        self._timeout_scale = timeout_scale
        self._power = None

        self._projector = connection

    @staticmethod
    def create_http(
        host: str,
        password: str | None = None,
        port: int = HTTP_PORT,
    ) -> "Projector":
        """
        Create an Epson Projector connected through HTTP.

        :param str host:             Hostname/IP/serial to the projector
        :param str | None password:  Optional password for HTTP
        :param int port:             HTTP port. Default 80.
        """
        from .projector_http import ProjectorHttp
        return Projector(connection=ProjectorHttp(
            host=host, password=password, port=port
        ))

    @staticmethod
    def create_escvpnet(
        host: str,
        password: str | None = None,
    ) -> "Projector":
        """
        Create an Epson Projector connected through ESC/VP.net.

        :param str host:             Hostname/IP/serial to the projector
        :param str | None password:  Optional password for ESC/VP.net connection
        """
        from .projector_tcp import ProjectorTcp
        connection = ProjectorTcp(host, TCP_PORT, password=password)
        return Projector(connection=connection)

    @staticmethod
    def create_serial(
        url: str,
    ) -> "Projector":
        """
        Create an Epson Projector connected through serial.

        :param str url:             Serialx supported URL for the projector
        """
        from .projector_serial import ProjectorSerial
        return Projector(connection=ProjectorSerial(url))

    def close(self):
        """Close connection."""
        if self._projector:
            self._projector.close()

    def set_timeout_scale(self, timeout_scale=1.0):
        """Set timeout scale for commands (to compensate for slow projectors)."""
        self._timeout_scale = timeout_scale

    async def get_serial_number(self):
        """Get serial number from device."""
        return await self._projector.get("SNO")
        # return await self._projector.get_serial_number()

    async def get_power(self):
        """Get Power info."""
        _LOGGER.debug("Getting POWER info")
        power = await self.get_property(command=POWER)
        if power:
            self._power = power
        return self._power

    async def get_property(self, command, timeout=None):
        """Get property state from device."""
        _LOGGER.debug("Getting property %s", command)
        timeout = timeout if timeout else get_timeout(command, self._timeout_scale)
        if self._lock.checkLock():
            return BUSY
        return await self._projector.get_property(command=command, timeout=timeout)

    async def send_command(self, command):
        """Send command to Epson."""
        _LOGGER.debug("Sending command to projector %s", command)
        if self._lock.checkLock():
            return False
        self._lock.setLock(command)
        return await self._projector.send_command(
            command, get_timeout(command, self._timeout_scale)
        )

    async def send_request(self, command):
        """Get property state from device."""
        _LOGGER.debug("Getting property %s", command)
        if self._lock.checkLock():
            return BUSY
        return await self._projector.send_request(params=command, timeout=10)


    # New API

    async def connect(self):
        """Establish connection."""
        await self._projector.connect()

    # Power

    async def pwr_on(self) -> None:
        """Turn on the projector."""
        await self._projector.set("PWR", "ON")

    async def pwr_off(self) -> None:
        """Turn off the projector."""
        await self._projector.set("PWR", "OFF")

    async def pwr_get(self) -> "PowerStatus":
        """Get power status."""
        response = await self._projector.get("PWR")
        return PowerStatus(response)



    # Serial number
    
    async def sno_get(self) -> str | None:
        """Get serial number."""
        return await self._projector.get("SNO")

    # Lamp
    
    async def lamp_get(self) -> int | None:
        """Get lamp hours."""
        response = await self._projector.get("LAMP")
        return int(response)

    # Volume

    async def vol_get(self) -> int | None:
        """Get volume level."""
        response = await self._projector.get("VOL")
        return int(response)

    async def vol_set(self, value: int) -> None:
        """Set volume level."""
        await self._projector.set("VOL", str(value))

    async def vol_inc(self) -> None:
        """Increase volume level."""
        await self._projector.set("VOL", "INC")

    async def vol_dec(self) -> None:
        """Decrease volume level."""
        await self._projector.set("VOL", "DEC")

    async def vol_init(self) -> None:
        """Initialize volume level."""
        await self._projector.set("VOL", "INIT")

    # CMODE: Color mode (dynamic, natural, cinema, etc.)

    async def cmode_get(self) -> CMode | None:
        """Get color mode."""
        response = await self._projector.get("CMODE")
        return CMode(response)
    
    async def cmode_set(self, value: CMode) -> None:
        """Set color mode."""
        await self._projector.set("CMODE", value.value)

    async def cmode_init(self) -> None:
        """Initialize color mode."""
        await self._projector.set("CMODE", "INIT")
