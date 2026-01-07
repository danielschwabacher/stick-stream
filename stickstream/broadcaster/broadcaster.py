#!/usr/bin/env python3
# RUN THIS FROM THE SERVER WHICH HAS CONTROLLERS PLUGGED INTO IT
import socket
import struct
import click
from evdev import InputDevice, list_devices, ecodes

# Packet format:
# controller_id (B), type (H), code (H), value (i)
PACK_FMT = "!BHHi"


def find_gamepads():
    click.echo("[*] Searching for gamepads...")
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


@click.command()
@click.option("--host", help="Receiver IP address")
@click.option("--port", default=9999, show_default=True, help="Receiver UDP port")
def broadcast(host, port):
    """Broadcast local controller input over the network."""
    if not host:
        raise click.BadParameter(
            "You must specify the IP address of the receiver.",
            param_hint=["--host"],
        )

    gamepads = find_gamepads()
    if not gamepads:
        raise click.ClickException("No compatible controllers found on this computer.")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (host, port)

    click.echo(f"[*] Broadcasting {len(gamepads)} controllers to IP address {host}...")

    for i, dev in enumerate(gamepads):
        click.echo(f"  [{i}] {dev.path} ({dev.name})")

    for dev in gamepads:
        dev.grab()

    try:
        while True:
            for cid, dev in enumerate(gamepads):
                try:
                    for event in dev.read():
                        if event.type in (ecodes.EV_KEY, ecodes.EV_ABS):
                            pkt = struct.pack(
                                PACK_FMT,
                                cid,
                                event.type,
                                event.code,
                                event.value,
                            )
                            try:
                                sock.sendto(pkt, addr)
                            except BlockingIOError:
                                # Ignore transient send failures for UDP
                                pass
                except BlockingIOError:
                    # Ignore transient send failures for UDP
                    pass
    finally:
        for dev in gamepads:
            dev.ungrab()


"""
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
"""
