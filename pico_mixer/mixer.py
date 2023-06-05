"""This code is DEPRECATED and is only left to illustrate why relying in on pygame was a dead-end.

See https://blog.balthazar-rouberol.com/my-diy-dungeons-and-dragons-ambiance-mixer for details.

"""
import contextlib

with contextlib.redirect_stdout(None):
    import pygame

    pygame.init()

import json
import sys
import curses
import time
import threading

from pygame import mixer
from serial import Serial
from serial.tools.list_ports import grep as list_ports


WINDOW_SIZE_X = 0
WINDOW_SIZE_Y = 0
BARS_START_X = 3
BARS_START_Y = 0

config = json.load(open("config.json"))
tracks = {}


class Track:
    def __init__(self, key, filename, sound, volume, display_char="#"):
        self.key = key
        self.filename = filename
        self.sound = sound
        self.display_char = display_char
        self.sound.set_volume(volume / 100)

    @property
    def channel(self):
        return mixer.Channel(int(self.key))

    @property
    def volume(self):
        return int(self.sound.get_volume() * 100)

    @volume.setter
    def volume(self, new_volume):
        self.sound.set_volume(new_volume / 100)

    @property
    def playing(self):
        return self.channel.get_busy()

    def change_volume(self, by):
        volume = self.volume
        volume += by
        if volume < 0:
            volume = 0
        elif volume > 100:
            volume = 100
        self.volume = volume

    def render(self):
        bar = f"{self.display_char * self.volume}".ljust(100, " ")
        return f"[{self.key}] - {self.filename}\n{BARS_START_X * ' '}{bar}"

    def play(self):
        self.channel.play(self.sound, loops=-1)

    def stop(self):
        self.channel.stop()


def update_sound_bars(stdscr):
    while True:
        time.sleep(0.2)
        for i in config:
            try:
                sound_bar = tracks[i]
            except KeyError:
                continue
            else:
                sound_bar_start_x = BARS_START_X
                sound_bar_start_y = BARS_START_Y + (int(i) * 3)
                addstr_args = () if not sound_bar.playing else (curses.A_BOLD,)
                # We need to clear the sound bar to redraw it after a potential sound change
                stdscr.addstr(
                    sound_bar_start_y,
                    sound_bar_start_x,
                    sound_bar.render(),
                    *addstr_args,
                )
                stdscr.refresh()


def process_message(message):
    key_name, state = message["key"], message["state"]

    if state == "pause":
        pygame.mixer.pause()
    elif state == "unpause":
        pygame.mixer.unpause()
    elif key_name in config:
        track = tracks[key_name]
        if state == "on":
            track.play()
        elif state == "off":
            track.stop()
        elif state in ("vol_up", "vol_down"):
            track.change_volume(by=10 if state == "vol_up" else -10)


def init_window(stdscr):
    global WINDOW_SIZE_X, WINDOW_SIZE_Y, BARS_START_X, BARS_START_Y
    WINDOW_SIZE_Y, WINDOW_SIZE_X = stdscr.getmaxyx()
    BARS_START_Y = int(WINDOW_SIZE_Y * 0.03)
    stdscr.clear()


def load_sounds(stdscr):
    for i, sound_path in config.items():
        tracks[i] = Track(
            key=i, filename=sound_path, sound=mixer.Sound(sound_path), volume=100
        )
        stdscr.refresh()


def main(stdscr):
    init_window(stdscr)
    mixer.set_num_channels(len(config.keys()))

    threading.Thread(target=update_sound_bars, args=(stdscr,), daemon=True).start()
    load_sounds(stdscr)

    usb_ports = list(list_ports(r"^/dev/cu\.usbmodem.*$"))
    if not usb_ports:
        print("No USB-plugged keypad was found")
        sys.exit(1)

    usb_device = Serial(usb_ports[0].device)
    while True:
        line = usb_device.readline().strip()
        line = line.decode("utf-8")
        if not line.startswith("{"):
            continue
        try:
            message = json.loads(line)
        except ValueError:
            continue
        else:
            process_message(message)


if __name__ == "__main__":
    curses.wrapper(main)
