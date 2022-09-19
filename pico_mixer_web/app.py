import time
import json
import glob

import serial.serialutil

from pathlib import Path
from serial import Serial
from serial.tools.list_ports import grep as list_ports

from flask import Flask, render_template
from flask_sock import Sock

sounds_dir = Path(__file__).parent.parent / "sounds"
app = Flask(
    "pico-mixer",
    static_url_path="/assets",
    static_folder=Path(__file__).parent / "assets",
)
sock = Sock(app)


def find_usb_device():
    if not (usb_ports := list(list_ports(r"^/dev/cu\.usbmodem.*$"))):
        return
    return Serial(usb_ports[0].device)


@app.get("/")
def index():
    track_files = sorted(glob.glob(f"{sounds_dir}/*"))[:12]
    tracks = {i: Path(track).name for i, track in enumerate(track_files)}
    return render_template("index.html.j2", tracks=tracks)


@sock.route("/key_events")
def stream_key_events(ws):
    connected = False
    while True:
        if not (usb_device := find_usb_device()):
            ws.send('{"state": "usb_disconnected"}')
            time.sleep(1)
            continue
        if not connected:
            ws.send('{"state": "usb_connected"}')
            connected = True
        try:
            line = usb_device.readline().strip()
            line = line.decode("utf-8")
            if not line.startswith("{"):
                continue
            try:
                json.loads(line)
            except ValueError:
                continue
            else:
                ws.send(line)
        except serial.serialutil.SerialException:
            ws.send('{"state": "usb_disconnected"}')
            connected = False
            time.sleep(1)


if __name__ == "__main__":
    app.run(port=8000)
