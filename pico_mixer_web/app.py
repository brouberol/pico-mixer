from gettext import find
import time
import json
from pathlib import Path

import serial.serialutil

from serial import Serial
from serial.tools.list_ports import grep as list_ports

from flask import Flask, render_template
from flask_sock import Sock

track_config_path = Path(__file__).parent / ".." / "config.json"
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
    with open(track_config_path) as track_config:
        return render_template("index.html.j2", tracks=json.load(track_config))


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
