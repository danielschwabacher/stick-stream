#!/usr/bin/env python3
# RUN THIS FROM THE COMPUTER RUNNING SUNSHINE/STEAM

import socket
import struct
import click
import uinput
from evdev import ecodes
from pprint import pprint

PACK_FMT = "!BHHi"

devices = {}
axis_state = {}


def get_device(cid):
    if cid not in devices:
        print(f"[+] Creating virtual controller {cid}")

        capabilities = [
            # Buttons
            (ecodes.EV_KEY, ecodes.BTN_SOUTH),
            (ecodes.EV_KEY, ecodes.BTN_EAST),
            (ecodes.EV_KEY, ecodes.BTN_NORTH),
            (ecodes.EV_KEY, ecodes.BTN_WEST),
            (ecodes.EV_KEY, ecodes.BTN_TL),
            (ecodes.EV_KEY, ecodes.BTN_TR),
            (ecodes.EV_KEY, ecodes.BTN_SELECT),
            (ecodes.EV_KEY, ecodes.BTN_START),
            (ecodes.EV_KEY, ecodes.BTN_THUMBL),
            (ecodes.EV_KEY, ecodes.BTN_THUMBR),
            # Left stick
            (ecodes.EV_ABS, ecodes.ABS_X, -32768, 32767, 16, 128),
            (ecodes.EV_ABS, ecodes.ABS_Y, -32768, 32767, 16, 128),
            # Right stick
            (ecodes.EV_ABS, ecodes.ABS_RX, -32768, 32767, 16, 128),
            (ecodes.EV_ABS, ecodes.ABS_RY, -32768, 32767, 16, 128),
            # Triggers
            (ecodes.EV_ABS, ecodes.ABS_Z, 0, 255, 0, 0),
            (ecodes.EV_ABS, ecodes.ABS_RZ, 0, 255, 0, 0),
            # D-pad
            (ecodes.EV_ABS, ecodes.ABS_HAT0X, -1, 1, 0, 0),
            (ecodes.EV_ABS, ecodes.ABS_HAT0Y, -1, 1, 0, 0),
        ]

        devices[cid] = uinput.Device(
            capabilities,
            name=f"stick-stream gamepad {cid}",
        )

        axis_state[cid] = {}

    return devices[cid]


def log(event_type, controller_name, controller_id, code, value):
    print(
        f"Received {event_type} event from controller: {controller_name} controller_id={controller_id} code={code} value={value}"
    )


@click.command()
@click.option("--port", default=9999, show_default=True, help="UDP port to listen on")
@click.option("--debug", is_flag=True, flag_value=True, help="Enable debug logging")
def receive(port, debug):
    """Receive controller input and expose virtual gamepads."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", port))
    if debug:
        click.echo("[*] Debug logging enabled")

    click.echo(f"[*] Listening for controllers on UDP {port}")

    while True:
        data, _ = sock.recvfrom(64)
        cid, etype, code, value = struct.unpack(PACK_FMT, data)
        dev = get_device(cid)

        if etype == ecodes.EV_KEY:
            if debug:
                log("KEY", {devices[cid]._Device__name}, cid, code, value)
            dev.emit((ecodes.EV_KEY, code), value)
        elif etype == ecodes.EV_ABS:
            if debug:
                log("ABS", {devices[cid]._Device__name}, cid, code, value)
            axis_state[cid][code] = value

            for axis, val in axis_state[cid].items():
                dev.emit((ecodes.EV_ABS, axis), val, syn=False)
            dev.syn()
