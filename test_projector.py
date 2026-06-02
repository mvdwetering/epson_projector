#!/usr/bin/env python3

"""Test and example of usage of Epson module."""
import argparse
from getpass import getpass
import epson_projector as epson

import asyncio
import logging

from epson_projector.enums import PowerStatus
from epson_projector.error import ProjectorUnauthorizedError

_LOGGER = logging.getLogger(__name__)

def _create_projector_from_args(args, password):
    """Create a projector instance based on the command line arguments."""
    if args.type == "http":
        print(f"Creating HTTP projector with host {args.host_or_serial_url} and port {args.port}")
        return epson.Projector.create_http(
            host=args.host_or_serial_url,
            password=password,
            port=args.port,
        )
    elif args.type == "escvpnet":
        return epson.Projector.create_escvpnet(
            host=args.host_or_serial_url,
            password=password,
            port=args.port,
        )
    elif args.type == "serial":
        return epson.Projector.create_serial(
            url=args.host_or_serial_url,
        )
    else:
        raise ValueError(f"Unsupported connection type: {args.type}")

async def main(args):
    password = None
    projector = None

    try_again = True
    while try_again:
        try_again = False
        try:
            projector = _create_projector_from_args(args, password)
            await projector.connect()
        except ProjectorUnauthorizedError:
            password = getpass("Password: ")
            try_again = True
        except Exception as e:  
            print(f"Error connecting to projector: {e}")
            return
        
    assert projector is not None, "Projector should be initialized at this point"

    data = await projector.sno_get()
    print(data)
    data = await projector.pwr_get()
    print(data.name)
    data = await projector.lamp_get()
    print(data)

    counter = 0
    while True:
        print(f"Loop {counter}")
        counter += 1

        try:
            data = await projector.pwr_get()
            print(data.name)
            print(f"POWER is {data == PowerStatus.NORMAL}")
            data = await projector.source_get()
            print(f"Source is {data.name} '{data.value}'")
            data = await projector.lamp_get()
            print(f"LAMP is {data} hours")
        except Exception as e:
            print(f"Exception: {e}")
        await asyncio.sleep(1)

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
