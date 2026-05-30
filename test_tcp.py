#!/usr/bin/env python3

import argparse
import asyncio
import logging
import epson_projector as epson
from epson_projector.const import (POWER, PWR_OFF, VOLUME)
from epson_projector.projector import PowerStatus


async def main_tcp(args):
    """Run main with TCP session."""
    # projector = epson.Projector(host=args.host,
    #                             type='tcp')
    projector = epson.Projector.create_escvpnet(host=args.host, password="emulatorpassword")

    try:
        await projector.connect()
    except Exception as e:
        print(f"Error connecting to projector: {e}")
        return

    # data = await projector.get_power()
    data = await projector.pwr_get()
    print(data.name)
    print(f"POWER is {data == PowerStatus.NORMAL}")

    # data = await projector.vol_get()
    # print(f"VOLUME is {data}")

    # data2 = await projector.get_property(VOLUME)
    # print(data2)
    # print("VOL @", data2)
    dataa = await projector.get_serial_number()
    print("proj2", dataa)
    # await projector.send_command(PWR_OFF)
    projector.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(  # noqa: F821
        description="Example/test application for Epson Projector package through ESC/VP.net protocol."
    )

    parser.add_argument(
        "host",
        help="Hostname or IP address of the projector.",
    )
    parser.add_argument(
        "--loglevel",
        help="Set the logging level. Default is INFO.",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    asyncio.run(main_tcp(args))
