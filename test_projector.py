#!/usr/bin/env python3

"""Test and example of usage of Epson module."""
import argparse
from getpass import getpass

import aiohttp
import epson_projector as epson

import asyncio
import logging

from epson_projector.error import UnauthorizedError

_LOGGER = logging.getLogger(__name__)

def _create_projector_from_args(args, password):
    """Create a projector instance based on the command line arguments."""
    websession = None
    if args.type == "http":
        print(f"Creating HTTP projector with host {args.host_or_serial_url} and port {args.port}")
        conn_type = "http"

        middlewares = []
        if password:
            _LOGGER.info("Using password for authentication")
            digest_auth = aiohttp.DigestAuthMiddleware(
                login="EPSONWEB", password=password
            )
            middlewares.append(digest_auth)

        websession = aiohttp.ClientSession(middlewares=middlewares)
    elif args.type == "escvpnet":
        conn_type = "tcp"
    elif args.type == "serial":
        conn_type = "serial"
    else:
        raise ValueError(f"Unsupported connection type: {args.type}")
    
    projector = epson.Projector(
        host=args.host_or_serial_url,
        websession=websession,
        type=conn_type,
        tcp_password=password,
    )

    # Hack the port overrride for now
    if args.port:
        if conn_type == "http":
            projector._projector._http_url = projector._projector._http_url.replace(  # noqa: SLF001 # pyright: ignore[reportAttributeAccessIssue]
                ":80/", f":{args.port}/"
            )
            print(f"HTTP URL overridden to {projector._projector._http_url}") # noqa: SLF001 # pyright: ignore[reportAttributeAccessIssue]
        elif conn_type == "tcp":
            projector._projector._port = args.port # pyright: ignore[reportAttributeAccessIssue]  # noqa: SLF001

    return projector


async def main(args):
    password = None
    projector = None

    try_again = True
    while try_again:
        try_again = False
        try:
            projector = _create_projector_from_args(args, password)
            # Send a command to verify connection and authentication
            await projector.get_power()
        except UnauthorizedError:
            password = getpass("Password: ")
            try_again = True
        except Exception as e:  
            print(f"Error connecting to projector: {e}")
            return
        
    assert projector is not None, "Projector should be initialized at this point"

    # This fails for LS11000 because does not support the additional command to get the serial number
    #data = await projector.get_serial_number()
    data = await projector.get_serial_number_alt()
    print(data)

    # await projector.contrast.set(50)
    # await projector.volume.set(20)
    data = await projector.colormode.get()
    print(data.value, data.name)

    # There is a Unclosed client session error because not awaiting the close
    # This is already fixed in the PR that adds the improved constructors, so ignore for now
    projector.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Example/test application for Epson Projector package."
    )

    parser.add_argument(
        "type",
        help="Type of the projector connection.",
        choices=["http", "escvpnet", "serial"],
    )
    parser.add_argument(
        "host_or_serial_url",
        help="Hostname/IP address or serial port url of the projector.",
    )
    parser.add_argument(
        "--port",
        help="Override the default port of the selected connection type.",
        type=int,
    )
    parser.add_argument(
        "--loglevel",
        help="Set the logging level. Default is INFO.",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    asyncio.run(main(args))
