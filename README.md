## Pico-mixer

![keypad](https://user-images.githubusercontent.com/480131/190699453-22a69127-dc96-4311-9798-fcf46ee1cf6d.png)

This project was born after thinking that I'd really like to have something like a [Launchpad](https://novationmusic.com/en/launch/launchpad-x) to control and mix sound ambiances while DMing a Dungeons and Dragons game.

What I wanted was a way to create an immersive atmosphere at the table, by being able to start, stop, pause and resume multiple individual soundtracks, adjust their volume, and flash pretty colors.

I used a [Pimoroni Keypad](https://shop.pimoroni.com/products/pico-rgb-keypad-base?variant=32369517166675), as well as a [Raspberry Pi Pico](https://learn.pimoroni.com/article/getting-started-with-pico), for a total budget of roughly 30 euro. The black casing was 3D-printed using the `rgb_keypad_-_bottom.stl` file from this [Thingiverse model](https://www.thingiverse.com/thing:4883873/files).


### Setup

The `code.py` script runs on a Raspberry Pi Pico, running [CircuitPython](https://circuitpython.org/), itself connected onto the [Pimoroni Keypad](https://shop.pimoroni.com/products/pico-rgb-keypad-base?variant=32369517166675). The first 12 keys control what audio tracks to play/stop, and the last 4 keys allow you to control the volume of individual tracks, as well as pause the whole stream.

<img width="100%" alt="Screen Shot 2022-09-17 at 15 20 23" src="https://user-images.githubusercontent.com/480131/190859070-7c1365d8-d062-462d-a73c-69e2f6cabcc1.png">

When a key (or a combination of Volume up/down + track key) is pressed, a JSON-formatted message is sent over USB. This message is read by the `mixer.py` script, a curses app displaying each individual track, associated with their volume bar.

<img width="100%" alt="Screen Shot 2022-09-17 at 15 15 47" src="https://user-images.githubusercontent.com/480131/190859066-77211be5-a692-450b-88c9-b99139f94216.png">

 
### Limitations

The `mixer.py` script currently uses [`pygame.mixer`](https://www.pygame.org/docs/ref/mixer.html) to play the individual track sound files over separate channels. While this works, the startup time can be excruciatingly slow, as each sound file must be fully loaded in memory before the app can start.

The python mixer code could possibly replaced by a web application relying on the following Web APIs:
- [`USB.getDevices()`](https://developer.mozilla.org/en-US/docs/Web/API/USB/getDevices) to read messages over USB (Chrome/Safari only)
- [`WebAudio`](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API) to stream/mix the different sound files.

### Local web application

I also implemented a slightly more complex web application that fixes the previously stated limitations. It is composed of 3 elements:

- the keypad CircuitPython code
- a webpage in charge of displaying the soundbars and active tracks as well as actually playing the audio tracks 
- a Flask webserver receiving the messages over USB and serving them to the webpage over a websocket, as well as serving the audio track files to the webpage

<img width="1116" alt="Screenshot 2022-09-18 at 16 59 36" src="https://user-images.githubusercontent.com/480131/190913656-5c0bb6a8-f8a9-460f-a5f7-cd65b29525fe.png">


As the browser is really good at streaming `<audio>` elements, the app can start immediately without having to load all audio files in memory.

<img width="100%" alt="Screenshot 2022-09-18 at 16 46 18" src="https://user-images.githubusercontent.com/480131/190913335-89fb520a-95c0-4723-bfc3-f301a472d06f.png">
