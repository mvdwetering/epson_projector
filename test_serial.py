#!/usr/bin/env python3

import argparse
import asyncio
import epson_projector as epson
from epson_projector.const import (POWER, PWR_ON, PWR_OFF)
import logging

async def main_serial(args):
    """Run main with serial connection."""
    # projector = epson.Projector(host=args.serial_url,
    #                             type='serial',
    #                             timeout_scale=2.0)
    # data = await projector.get_power()
    # print(data)
    # cmd = None
    # if data == '01':
    #     cmd = PWR_OFF
    # elif data == '00':
    #     cmd = PWR_ON
    # if cmd:
    #     data2 = await projector.send_command(cmd)
    #     print(data2)

    # serialno = await projector.get_serial_number()
    # print("Projector serial number:", serialno)
    # projector.close()

    projector = epson.Projector.create_serial(
        url=args.serial_url,
    )

    try:
        await projector.connect()
    except Exception as e:
        print(f"Error connecting to projector: {e}")
        return

    # data = await projector.get_property(POWER)
    # print(data)
    # data = await projector.get_serial_number()
    # print(data)
    data = await projector.pwr_get()
    print(data.name)
    data = await projector.sno_get()
    print(data)
    data = await projector.lamp_get()
    print(data)

    projector.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Example/test application for Epson Projector package through serial connection."
    )

    parser.add_argument(
        "serial_url",
        help="Can be a devicename like /dev/ttyUSB0 or COM3 for real serial port or use socket://<ip-or-host>:<port> for connections to tcp-to-serial solutions.",
    )
    parser.add_argument(
        "--loglevel",
        help="Set the logging level. Default is INFO.",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    asyncio.run(main_serial(args))
