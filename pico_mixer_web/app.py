import time
import json

import serial.serialutil

from pathlib import Path
from serial import Serial
from serial.tools.list_ports import grep as list_ports

from flask import Flask, render_template
from flask_sock import Sock

# From https://devicehunt.com/view/type/usb/vendor/239A
ADAFRUIT_HARDWARE_VENDOR_ID = "239A"

track_config_path = Path(__file__).parent / ".." / "config.json"
app = Flask(
    "pico-mixer",
    static_url_path="/assets",
    static_folder=Path(__file__).parent / "assets",
)
sock = Sock(app)


def find_usb_device():
    if not (usb_ports := list(list_ports(r".*"))):
        return
    for port in usb_ports:
        if port.hwid.startswith(ADAFRUIT_HARDWARE_VENDOR_ID):
            return Serial(port.device)


@app.get("/")
def index():
    with open(track_config_path) as track_config:
        tracks = json.load(track_config)
        tracks = sorted(tracks, key=lambda track: (track["tags"][0], track["title"]))
        return render_template("index.html.j2", tracks=tracks)


@sock.route("/key_events")
def stream_key_events(ws):
    connected, usb_device = False, None
    while True:
        if not connected:
            if not (usb_device := find_usb_device()):
                ws.send('{"state": "usb_disconnected"}')
                time.sleep(1)
                continue
            else:
                ws.send('{"state": "usb_connected"}')
                connected = True
        elif usb_device is not None:
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
