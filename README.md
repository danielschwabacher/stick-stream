# stick-stream

**stick-stream** is an ultra low-latency, LAN-based gamepad streaming system for Linux. It forwards controller input from one machine (for example, a Raspberry Pi with USB gamepads attached) to another machine over the network and exposes those controllers as virtual Linux input devices via **uinput**.

stick-stream is designed to work seamlessly with **Sunshine** and **Steam** for gaming. The original use case was to forward controller inputs from a Raspberry Pi in my living room to my gaming PC in another room in the house over a LAN connection.

## Features

- 🎮 Stream one or more gamepads over a local network
- ⚡ Low-latency UDP-based transport
- 🧠 Correctly handles analog sticks, triggers, D-pads, and all controller buttons
- 🖥 Appears as a real game controller to applications

## How It Works

stick-stream consists of two components:

1. **Broadcaster** – Runs on the machine with the physical controllers attached

   - Reads input events from `/dev/input/event*`
   - Serializes button and axis events
   - Sends them over the network

2. **Receiver** – Runs on the host machine (e.g. Sunshine server)

   - Receives events over UDP
   - Recreates controllers using `uinput`

From the perspective of games and applications, the streamed controller is indistinguishable from a locally connected USB gamepad.

---

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
- Kernel support for `uinput`

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

> ⚠️ Note: `python-uinput` has multiple incompatible APIs across distros. stick-stream targets the tuple-based API commonly found on Debian/Ubuntu systems.
