#!/usr/bin/env python3

import asyncio
import argparse
import epson_projector as epson
from epson_projector.const import POWER, PWR_ON, PWR_OFF
import logging

_LOGGER = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
_LOGGER.addHandler(console_handler)
_LOGGER.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG)


async def main_serial(args):
    """Run main with serial connection."""
    await run(args)


async def run(args):
    projector = epson.Projector(host=args.host, type="serial", timeout_scale=2.0)

    data = await projector.get_power()
    print(data)
    cmd = None
    if data == '01':
        cmd = PWR_OFF
    elif data == '00':
        cmd = PWR_ON
    if cmd:
        data2 = await projector.send_command(cmd)
        print(data2)

    serialno = await projector.get_serial_number()
    print("Projector serial number:", serialno)

    projector.close()


parser = argparse.ArgumentParser(
    description="Test application for serial EPSON projectors."
)
parser.add_argument(
    "host",
    help="Serial port name like '/dev/ttyUSB0' or PySerial URL handler like 'socket://192.168.178.42:12345'",
)
args = parser.parse_args()

loop = asyncio.get_event_loop()
loop.run_until_complete(main_serial(args))
loop.close()
