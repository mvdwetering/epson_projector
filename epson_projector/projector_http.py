"""HTTP connection of Epson projector module."""
import json
import json
import logging

import aiohttp
import asyncio

from epson_projector.escvpnet.escvp21_communication import EscVp21CommandError

from .const import (
    ACCEPT_ENCODING,
    ACCEPT_HEADER,
    BUSY,
    EPSON_KEY_COMMANDS,
    DIRECT_SEND,
    HTTP_OK,
    SNO,
    STATE_UNAVAILABLE,
    POWER,
    EPSON_CODES,
    TCP_SERIAL_PORT,
    SERIAL_BYTE,
    JSON_QUERY,
)
from .error import ProjectorConnectionError, ProjectorUnauthorizedError, ProjectorUnavailableError
from .timeout import get_timeout
from .base_connection import BaseProjectorConnection

_LOGGER = logging.getLogger(__name__)


class ProjectorHttp(BaseProjectorConnection):
    """
    Epson projector class.

    Control your projector with Python.
    """

    def __init__(self, host:str, password: str | None = None, port:int=80):
        """
        Epson Projector controller.

        :param str host:        IP address or hostname of Projector
        :param str | None password:  Optional password for HTTP
        :param int port:        Port to connect to. Default 80.
        """
        self._host = host
        self._password = password
        self._base_url = f"http://{self._host}:{port}/cgi-bin/"
        self._json_query_url = self._base_url + JSON_QUERY
        self._direct_send_url = self._base_url + DIRECT_SEND
        self._headers = {
            "Accept-Encoding": ACCEPT_ENCODING,
            "Accept": ACCEPT_HEADER,
            "Referer": f"http://{self._host}:{port}/cgi-bin/webconf",
        }
        self._serial_number = None
        self._websession = None
        self._lock = asyncio.Lock()

    def close(self):
        if self._websession and not self._websession.closed:
            asyncio.create_task(self._websession.close())

    async def get_property(self, command, timeout):
        """Get property state from device."""
        response = await self.send_request(
            timeout=timeout, params=EPSON_KEY_COMMANDS[command], type=JSON_QUERY
        )
        if not response:
            return False
        try:
            if response == STATE_UNAVAILABLE:
                return STATE_UNAVAILABLE
            return response["projector"]["feature"]["reply"]
        except KeyError:
            return BUSY

    async def send_command(self, command, timeout):
        """Send command to Epson."""
        response = await self.send_request(
            timeout=timeout, params=EPSON_KEY_COMMANDS[command], type=DIRECT_SEND
        )
        return response

    async def send_request(self, params, timeout, type=JSON_QUERY):
        """Send request to Epson."""
        try:
            async with asyncio.timeout(timeout):
                url = "{url}{type}".format(url=self._base_url, type=type)
                _LOGGER.debug("Sending request: %s", params)
                async with self._websession.get(
                    url=url, params=params, headers=self._headers
                ) as response:
                    _LOGGER.debug("Received response, status: %s", response.status)
                    if response.status != HTTP_OK:
                        _LOGGER.warning("Error message %d from Epson.", response.status)
                        return False
                    if type == JSON_QUERY:
                        return await response.json()
                    return response
        except (
            aiohttp.ClientError,
            aiohttp.ClientConnectionError,
            TimeoutError,
            asyncio.exceptions.TimeoutError,
        ):
            raise ProjectorUnavailableError(STATE_UNAVAILABLE)

    async def get_serial_number(self):
        """Request for serial number to Epson."""

        # First attempt to get serial number through get_property
        # This command also works when the projector is in standby
        if not self._serial_number:
            try:
                response = await self.get_property(SNO, get_timeout(SNO))
            except ProjectorUnavailableError:
                response = False
            else:
                if response and response != BUSY and response != STATE_UNAVAILABLE:
                    self._serial_number = response

        # Otherwise fallback to the same method as used for TCP request for serial number
        if not self._serial_number:
            try:
                async with asyncio.timeout(10):
                    power_on = await self.get_property(POWER, get_timeout(POWER))
                    if power_on == EPSON_CODES[POWER]:
                        reader, writer = await asyncio.open_connection(
                            host=self._host,
                            port=TCP_SERIAL_PORT,
                        )
                        _LOGGER.debug("Asking for serial number.")
                        writer.write(SERIAL_BYTE)
                        await writer.drain()
                        response = await reader.read(32)
                        self._serial_number = response[24:].decode()
                        writer.close()
                    else:
                        _LOGGER.error("Is projector turned on?")
            except ProjectorUnavailableError:
                _LOGGER.error("Projector unavailable. Is projector connected and turned on?")
            except asyncio.TimeoutError:
                _LOGGER.error(
                    "Timeout error receiving SERIAL of projector. Is projector turned on?"
                )

        return self._serial_number

    # NEW API

    async def connect(self):
        """Establish connection. This will make a connection to the projector and make sure it can transmit data."""
        middlewares = []
        if self._password:
            digest_auth = aiohttp.DigestAuthMiddleware(
                login="EPSONWEB", password=self._password
            )
            middlewares.append(digest_auth)

        websession = aiohttp.ClientSession(middlewares=middlewares, raise_for_status=True)
        self._websession = websession

        await self.null()


    async def _send_request(self, url, params, timeout) -> str:
        try:
            async with self._lock:
                async with asyncio.timeout(timeout):
                    _LOGGER.debug("Send: GET '%s' %s", url, params)
                    start_time = asyncio.get_event_loop().time()
                    async with self._websession.get(
                        url=url, params=params, headers=self._headers
                    ) as response:
                        if response.status != HTTP_OK:
                            _LOGGER.warning("Error message with status %d from Epson.", response.status)
                            response.raise_for_status()
                        # Need to consume the response body here because we are in a context manager
                        # and it will be out of scope when doing it later
                        response_text = await response.text()
                        end_time = asyncio.get_event_loop().time()
                        _LOGGER.debug("Recv (%d): %s (%.3f ms)", response.status, response_text.strip(), (end_time - start_time) * 1000)

                        return response_text
        except aiohttp.ClientResponseError as e:
            _LOGGER.debug("ClientResponseError: %s", e)
            if e.status == 401:
                raise ProjectorUnauthorizedError("Unauthorized") from e
            raise ProjectorConnectionError() from e
        except (
            aiohttp.ClientError,
            aiohttp.ClientConnectionError,
            TimeoutError,
            asyncio.exceptions.TimeoutError,
        ) as e:
            _LOGGER.debug("Error: %s", e)
            raise ProjectorConnectionError() from e

    async def get(self, command) -> str:
        """Get property state from device."""
        response = await self._send_request(url=self._json_query_url, params={"jsoncallback": command + "?"}, timeout=10)
        response = json.loads(response)

        feature = response["projector"]["feature"]
        if not feature["error"]:
            # Reply contains just the value, e.g. "01", not "PWR=01"
            return feature["reply"]

        raise EscVp21CommandError(
            f"Command '{command}' failed with response: {response}"
        )


    async def set(self, command, value) -> None:
        """Set property state on device."""
        await self._send_request(url=self._direct_send_url, params=f"{command}={value}", timeout=10)

    async def null(self) -> None:
        """Set property state on device."""
        await self._send_request(url=self._direct_send_url, params="", timeout=10)

