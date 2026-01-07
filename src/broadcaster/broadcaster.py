#!/usr/bin/env python3
# RUN THIS FROM THE SERVER WHICH HAS CONTROLLERS PLUGGED INTO IT

import asyncio
import socket
import struct
from evdev import InputDevice, list_devices, ecodes

SERVER_IP = "10.1.10.12"  # CHANGE ME
SERVER_PORT = 9999

# Packet format:
# controller_id (B), type (H), code (H), value (i)
PACK_FMT = "!BHHi"


def find_gamepads():
    devices = []
    for path in list_devices():
        dev = InputDevice(path)
        if ecodes.EV_KEY in dev.capabilities():
            if any(
                k in dev.capabilities()[ecodes.EV_KEY]
                for k in (ecodes.BTN_A, ecodes.BTN_SOUTH)
            ):
                devices.append(dev)
    return devices


async def stream_device(dev, controller_id, sock):
    print(f"[+] Streaming {dev.name} as controller {controller_id}")
    dev.grab()

    async for event in dev.async_read_loop():
        if event.type in (ecodes.EV_KEY, ecodes.EV_ABS):
            packet = struct.pack(
                PACK_FMT, controller_id, event.type, event.code, event.value
            )
            sock.send(packet)


async def main():
    gamepads = find_gamepads()
    if not gamepads:
        print("No gamepads found")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((SERVER_IP, SERVER_PORT))

    tasks = []
    print(f"Total gamepads: {len(gamepads)}")
    for i, dev in enumerate(gamepads):
        tasks.append(asyncio.create_task(stream_device(dev, i, sock)))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
