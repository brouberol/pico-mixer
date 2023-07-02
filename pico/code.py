import math
import time

import usb_cdc
from pimoroni_rgbkeypad import RGBKeypad

# Generated via https://medialab.github.io/iwanthue/
COLORS = [
    [229, 133, 154],
    [236, 123, 70],
    [213, 165, 120],
    [213, 172, 61],
    [208, 226, 69],
    [213, 225, 154],
    [143, 185, 73],
    [108, 218, 71],
    [139, 175, 125],
    [101, 216, 128],
    [103, 217, 173],
    [85, 179, 178],
    [120, 223, 235],
    [120, 166, 224],
    [201, 157, 216],
    [220, 110, 223],
]
VOLUME_DOWN_KEY_INDEX = 12
VOLUME_UP_KEY_INDEX = 13
PAUSE_KEY_INDEX = 14
PAUSE_ALL_KEY_INDEX = 15
ACTIVATED_KEY_BRIGHTNESS = 0.6
DEACTIVATED_KEY_BRIGHTNESS = 0.2
BRIGHTNESS_FLUCTUATION_CYCLE_MS = 3000

activated_keys = {}
keys_being_pressed = {}
keys_paused = set()
paused_all = False


class KeyState:
    init = "init"
    pause = "pause"
    pause_all = "pause_all"
    start = "start"
    stop = "stop"
    unpause = "unpause"
    unpause_all = "unpause_all"
    vol_down = "vol_down"
    vol_up = "vol_up"


def fluctuating_brightness(t, cycle):
    """Cyclic function representing the brightness fluctuation of a key over time

    See https://s.42l.fr/FsKw74vh

    """
    brightness = abs(math.cos(math.pi * t / cycle))
    return clamp(value=brightness, min_value=0.05, max_value=0.90)


def clamp(value, min_value, max_value):
    """Clamp a value between 2 boundary values"""
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    return value


def send_key_state(key, state):
    """Send a JSON-encoded message reflecting the state of the given argument key"""
    send_message('{"key": "%s", "state": "%s"}\n' % (str(key), state))


def send_message(message):
    """Send the arugment message over the USB port"""
    print(message)


def initialize_keys(keypad):
    """Light up each keys with their associated color"""
    for i, key in enumerate(keypad.keys):
        key.color = COLORS[i]
        key.brightness = DEACTIVATED_KEY_BRIGHTNESS


def advertise_keys_colors():
    """Send an init message over USB with the color of each key"""
    while not usb_cdc.console.connected:
        time.sleep(0.1)
    send_message('{"state": "%s", "colors": %s}\n' % (KeyState.init, str(COLORS[:12])))


def handle_keypress_combination(keys_pressed):
    """Handle key combination to allow volume up/down, key pause/unpause, etc"""
    if len([pressed for pressed in keys_pressed if pressed]) != 2:
        return

    associated_keys_index = [
        i
        for (i, pressed) in enumerate(keys_pressed)
        if pressed
        if i < VOLUME_DOWN_KEY_INDEX
    ]
    if len(associated_keys_index) != 1:
        return

    associated_key_index = associated_keys_index[0]
    if not keys_being_pressed.get(associated_key_index):
        keys_being_pressed[associated_key_index] = True

        if keys_pressed[VOLUME_DOWN_KEY_INDEX] is True:
            state = KeyState.vol_down
        elif keys_pressed[VOLUME_UP_KEY_INDEX] is True:
            state = KeyState.vol_up
        else:
            # pause / unpause
            if associated_key_index not in keys_paused:
                keys_paused.add(associated_key_index)
                state = KeyState.pause
            else:
                keys_paused.remove(associated_key_index)
                state = KeyState.unpause

        send_key_state(key=associated_key_index, state=state)


def main():
    global paused_all
    start_time = time.monotonic()
    keypad = RGBKeypad()

    initialize_keys(keypad)
    advertise_keys_colors()

    while True:
        # This is faster than iterating over all the keys everytime
        # BUT while the operator presses on the key, the key will be
        # marked as pressed multiple times. We need to keep track of
        # the keys that are _being_ pressed and only light them up once,
        # to avoid a flicker effect
        keys_pressed = keypad.get_keys_pressed()
        handle_keypress_combination(keys_pressed)

        for key_index, key_pressed in enumerate(keys_pressed):
            # De-register a key that was being pressed if their state indicates
            # that they are not being pressed.
            if not key_pressed:
                if key_index in keys_being_pressed:
                    keys_being_pressed.pop(key_index)

                # When a key was activated, make its brightness fluctuate,
                # except if the pause button is activated itself. In that case,
                # only make the pause button fluctuate and deactivate all other
                # activated keys, while keeping their activated state, to make it
                # easy to restore
                if (
                    PAUSE_ALL_KEY_INDEX in activated_keys
                    and key_index != PAUSE_ALL_KEY_INDEX
                ):
                    key = keypad.keys[key_index]
                    key.brightness = DEACTIVATED_KEY_BRIGHTNESS
                elif key_index in activated_keys:
                    elapsed_ms = (time.monotonic() - start_time) * 1000
                    key = keypad.keys[key_index]
                    key.brightness = fluctuating_brightness(
                        elapsed_ms, cycle=BRIGHTNESS_FLUCTUATION_CYCLE_MS
                    )
                continue

            if key_index in (
                # The compose keys
                VOLUME_DOWN_KEY_INDEX,
                VOLUME_UP_KEY_INDEX,
                PAUSE_KEY_INDEX,
            ):
                continue

            # Don't modify a key that is still being pressed, to avoid making it flicker
            if key_index in keys_being_pressed:
                continue

            # When a key was pressed, send the associated keyboard event from the
            # keypad to the computed it is connected to
            key = keypad.keys[key_index]
            keys_being_pressed[key_index] = True

            # Toggle the key activation state after it was pressed
            if key_index in activated_keys:
                activated_keys.pop(key_index)
                key.brightness = DEACTIVATED_KEY_BRIGHTNESS
                state = KeyState.stop
            else:
                activated_keys[key_index] = True
                key.brightness = ACTIVATED_KEY_BRIGHTNESS
                state = KeyState.start

            if key_index == PAUSE_ALL_KEY_INDEX:
                if paused_all:
                    state = KeyState.unpause_all
                else:
                    state = KeyState.pause_all
                paused_all = not paused_all

            send_key_state(key=key_index, state=state)


if __name__ == "__main__":
    main()
