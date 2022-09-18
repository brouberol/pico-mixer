from gettext import find
import time
import json
from pathlib import Path

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
    usb_ports = list(list_ports(r"^/dev/cu\.usbmodem.*$"))
    if not usb_ports:
        print("No USB-plugged keypad was found")
        return
    return Serial(usb_ports[0].device)


@app.get("/")
def index():
    with open(track_config_path) as track_config:
        return render_template("index.html.j2", tracks=json.load(track_config))


@sock.route("/key_events")
def stream_key_events(ws):
    while not (usb_device := find_usb_device()):
        time.sleep(1)
    while True:
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


if __name__ == "__main__":
    app.run(port=8000)
