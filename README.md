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

This is due to the fact that `pygame` can handle sound 2 different ways:
- it can stream large sound files as background music via `mixer.music` (which is what we want!), but it can only play one track at a time(<sigh>)
- it can play multiple sound files on different channels via `pygame.mixer.{Sound,Channel}`, but it has to fully load these sound files into memory. It's usually ok because these sounds files are very small, as it's mostly for quick sound effects.

 We're trying to shoehorn both `mixer.Sound` and `mixer.music` together, which has sadly proven to not work, as pygame implement streaming from an audio file directly in the `mixer.music` class, without exposing it as a standalone utility.


### Local web application

One way I found to circumvent the previously stated [limitations](#limitations) was to implement a slightly more complex web application composed of 3 elements:

- the keypad CircuitPython code
- a webpage in charge of displaying the soundbars and active tracks as well as actually controlling the audio tracks
- a Flask webserver receiving the keypad messages over USB and serving them to the webpage over a websocket, as well as serving the static audio files to the webpage

<img width="100%" alt="Screenshot 2022-09-18 at 17 06 35" src="https://user-images.githubusercontent.com/480131/190913995-a27c2385-ea1d-491a-8cc8-84a14d738a49.png">


As the browser is really good at streaming `<audio>` elements, the app can start immediately without having to load all audio files in memory.

<img width="100%" alt="Screenshot 2022-09-21 at 20 25 38" src="https://user-images.githubusercontent.com/480131/191582090-3d54a629-ce9f-4f26-9178-f8311c55de6d.png">

### Colors

The key colors were generated from [iwanthue](https://medialab.github.io/iwanthue/) and are stored in the `COLORS` list, in `pico/code.py`. Any changes to the colors will be reflected in the web UI, as they are [advertised](https://github.com/brouberol/pico-mixer/blob/2c5acb191eb22d45affdfcc4eb21ec853d690a0e/pico/code.py#L57-L60) to the web-server at [propagated](https://github.com/brouberol/pico-mixer/blob/2c5acb191eb22d45affdfcc4eb21ec853d690a0e/pico_mixer_web/assets/js/script.js#L70-L71) to the UI when the keypad starts.


### Getting started on macOS and Linux

(This guide assumes that CircuitPython has been installed on the pico. If that is not the case, follow these [instructions](https://learn.adafruit.com/welcome-to-circuitpython) first.)


Open a terminal app, then run the following commands:

```console
$ cd ~/Downloads
$ curl -L https://github.com/brouberol/pico-mixer/archive/refs/heads/main.zip -o main.zip
$ unzip main.zip
$ cd pico-mixer-main
$ python3 -m pip install --user poetry
$ make install
```

Plug the keypad, and run:

```console
$ make pico-sync
```

The keypad should light up. Unplug it.

Now, copy all the sounds files you would like to play (12 max) under the `sounds` folder, and replace each example `title` attribute under the `config.json` file with the name of a sound file you copied under `sounds`. Feel free to add a couple of descriptive tags under the `tags` attribute. Save the `config.json` file.

Run the following command to start the webserver:

```console
$ make webmixer
```

At that point, the webserver will start and the webpage will open. Plug the keypad in. You are now ready.

### Getting started on Windows

(This guide assumes that CircuitPython has been installed on the pico. If that is not the case, follow these [instructions](https://learn.adafruit.com/welcome-to-circuitpython) first.)

Before being able to execute this application on your Windows machine, you will need to install the Python programming language. To do this, go to the [Windows download page](https://www.python.org/downloads/windows/), click on the "Latest Python 3 Release" link, and follow the installation instructions.

Now that Python is installed, click on the green `Code` button at the top of this page, and then on `Download zip`. This will download the project as a zip file in your `Downloads` folder. Unzip it by right-clicking on the archive, and click on "Extract here".

Open the `pico-mixer-main` folder, and its subfolder, until you can see a `README.md` file. Open the `pico` folder. Plug the keypad to your computer using the USB cable. A file explorer window should open. Copy all the files in the current `pico` folder to the `CIRCUITPY` USB volume. At that point, the keypad should light up. Unplug it. Go back to the parent folder.

Now, click on the address bar of your file explorer, type `cmd` and then press the Enter key. You should see a terminal, opened in the folder you were in.

Type in the following commands to install all the project dependencies (don't type the `C:\...>` part, it's just there to mimick what you see in the terminal).

```console
C:\Users\you\Downloads\pico-mixer-main\pico-mixer-main>python.exe -m venv .venv
C:\Users\you\Downloads\pico-mixer-main\pico-mixer-main>.venv\Scripts\python.exe -m pip install -r requirements.txt
```

You only have to run these commands once. At that point, all the dependencies have been installed.

Now, copy all the sounds files you would like to play (12 max) under the `sounds` folder, and open the `config.json` file with a text editor, such as Notepad. Replace each example `title` attribute with the name of a sound file you copied under `sounds` and, feel free to add a couple of descriptive tags under the `tags` attribute. Save the `config.json` file.

We can now execute the web server!

```console
C:\Users\you\Downloads\pico-mixer-main\pico-mixer-main>cd pico_mixer_web
C:\Users\you\Downloads\pico-mixer-main\pico-mixer-main>..\.venv\Scripts\python.exe app.py
```

Finally, open your internet browser, and type the following address, then the Enter key: `http://localhost:8000`. Plug the keypad in. At that point, you should see as many bars as you have sound files (12 max), with colors, and you should see the 🔌 ✅ emoji, indicating that the keypad is plugged and recognized.

Press a key, and low and behold, a sound should play. If that is not the case, check out the output of the command you ran in the terminal. If you see some lines with `404 -`, this means that you made a typo in the `title` attribute of that track, in the `config.json` file, and that it does not match the filename of the actual sound file. Fix the typo and try again.
