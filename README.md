# stick-stream

`stick-stream` is an ultra low-latency, virtual USB streaming system for Linux-based OSes. It is designed as an Linux-native, open-source alternative to [VirtualHere]([https://www.virtualhere.com/]) for gaming purposes.

`stick-stream` can be used to forward controller input from one machine (for example, a Raspberry Pi with USB gamepads attached) to another machine over the network and exposes those controllers as virtual Linux input devices via [**uinput**](https://www.kernel.org/doc/html/v4.12/input/uinput.html).

`stick-stream` is designed to work seamlessly with **Sunshine** and **Steam** for gaming. The original use case was to forward controller inputs from a Raspberry Pi in my living room to my gaming PC which resides in a different room.

## Features

- 🎮 Stream one or more gamepads over a local network.
- ⚡ Low-latency UDP-based transport. I play FPS games with `stick-stream` and do not notice any input lag.
- 🧠 Correctly handles analog sticks, triggers, D-pads, and all controller buttons.

## How It Works

`stick-stream` consists of two components:

1. **Broadcaster** – Runs on the machine with the physical controllers attached

   - Reads input events from `/dev/input/event*`
   - Serializes button and axis events
   - Sends them over the network

2. **Receiver** – Runs on the host machine (e.g. Sunshine server)

   - Receives events over UDP
   - Recreates controllers using `uinput`

From the perspective of games and applications, the streamed controller is indistinguishable from a locally connected USB gamepad.

## Requirements

### Sender

- Any Linux distro (tested on Debian)
- Python 3.9+
- `python-evdev`

### Receiver

- Any Linux distro (tested on Fedora 43)
- Python 3.9+
- `python-evdev`
- `python-uinput`

## Installation

### 1. Install system dependencies

```bash
sudo apt install python3-evdev
sudo modprobe uinput
```

Ensure uinput loads at boot:

```bash
echo uinput | sudo tee /etc/modules-load.d/uinput.conf
```

### 2. Install Python dependencies

```bash
pip install evdev uinput
```

> ⚠️ Note: `python-uinput` has multiple incompatible APIs across distros. `stick-stream` targets the tuple-based API commonly found on Debian/Ubuntu systems.

# FAQs

### Does this replace VirtualHere?

Short answer: **no**.

[VirtualHere]([https://www.virtualhere.com/]) supports anything that can be plugged into a USB port (like flash drives and Bluetooth dongles). `stick-stream` is really only designed to forward gamepad inputs.

My guess is that VirtualHere captures everything sent into the USB port and somehow replays them remotely to the connected VirtualHere clients. This is much different than `stick-stream` which only forwards controller input at the Linux input (evdev) level.

However, if you were only using VirtualHere to forward your gamepad inputs over the network, then `stick-stream` will accomplish these same goals.

### Does this work on non-Linux OSes?

No, not in it's current state. `stick-stream` relies heavily on some Linux-specific Kernel features and I have no plans to port it to other operating systems.
