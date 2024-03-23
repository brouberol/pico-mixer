import json
import sys
import time
import os
from pathlib import Path

import click
import serial.serialutil
from flask import Flask, render_template
from flask_sock import Sock
from serial import Serial
from serial.tools.list_ports import grep as list_ports

# From https://devicehunt.com/view/type/usb/vendor/239A
ADAFRUIT_HARDWARE_VENDOR_ID = "239A"

assets_dir = Path(__file__).parent / "assets"
sounds_dir = assets_dir / "sounds"

track_config_path = os.environ.get(
    'PICO_MIXER_CONFIG',
    Path(__file__).parent / ".." / "config.json"
)
app = Flask(
    "pico-mixer",
    static_url_path="/assets",
    static_folder=assets_dir,
)
sock = Sock(app)

if not sounds_dir.exists():
    click.echo(
        click.style(
            f"The {sounds_dir} folder does not exist. Creating it on the fly.",
            fg="yellow",
        )
    )
    sounds_dir.mkdir(exist_ok=True)

elif not (sounds_dir.is_dir() or sounds_dir.is_symlink()):
    click.echo(
        click.style(
            f"{sounds_dir} should be a directory and not a file. Delete it and restart the app.",
            fg="red",
        )
    )
    sys.exit(1)
elif not list(sounds_dir.iterdir()):
    click.echo(
        click.style(
            f"{sounds_dir} is empty. No sounds will be played. Put sounds file under it and "
            "update the config.json file to reflect the file names",
            fg="yellow",
        )
    )


def find_usb_device():
    if not (usb_ports := list(list_ports(r".*"))):
        return
    for port in usb_ports:
        if ADAFRUIT_HARDWARE_VENDOR_ID in port.hwid:
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
