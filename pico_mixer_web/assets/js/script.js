const ws = new WebSocket("ws://localhost:8000/key_events");
const tracksPlaying = {};
const volumeIncrement = 0.05;

function pauseAllPlayingTracks() {
  Object.entries(tracksPlaying).forEach(([key, audioElement]) => {
    audioElement.pause();
    const trackProgressBar = document.getElementById(`progress_track_${key}`);
    trackProgressBar.classList.add("bg-warning");
  });
}

function unpauseAllPlayingTracks() {
  Object.entries(tracksPlaying).forEach(([key, audioElement]) => {
    audioElement.play();
    const trackProgressBar = document.getElementById(`progress_track_${key}`);
    trackProgressBar.classList.remove("bg-warning");
  });
}

function colorizeTracksKbdElements(colors) {
  for (i=0; i<colors.length; i++) {
    const color = colors[i];
    const trackColoredElements = document.getElementsByClassName(`track_${i}`);
    for (const element of trackColoredElements) {
      element.style.backgroundColor = `rgb(${color[0]}, ${color[1]}, ${color[2]}`;
    };
  }
}

function startTrack(trackKey, trackAudioElement, trackProgressBar) {
  tracksPlaying[trackKey] = trackAudioElement;
  trackProgressBar.classList.remove("non-playing");
  trackProgressBar.textContent = "100%";
  trackProgressBar.style.backgroundColor = document.getElementsByClassName(`track_${trackKey}`)[0].style.backgroundColor;
  trackAudioElement.play();
}

function stopTrack(trackKey, trackaudioElement, trackProgressBar) {
  trackProgressBar.classList.add("non-playing");
  trackaudioElement.pause();
  trackaudioElement.currentTime = 0;
  trackaudioElement.volume = 1;
  trackProgressBar.style.width = '100%';
  trackProgressBar.style.backgroundColor = null;
  trackProgressBar.textContent = "";
  delete tracksPlaying[trackKey];
}

function increaseTrackVolume(trackAudioElement, trackProgressBar) {
  if (trackAudioElement.volume + volumeIncrement <= 1) {
    trackAudioElement.volume += volumeIncrement;
    trackProgressBar.style["width"] = trackAudioElement.volume * 100 + "%";
    trackProgressBar.textContent = trackProgressBar.style["width"];
  };
}

function decreaseTrackVolume(trackAudioElement, trackProgressBar) {
  if (trackAudioElement.volume - volumeIncrement > 0) {
    trackAudioElement.volume -= volumeIncrement;
    trackProgressBar.style["width"] = trackAudioElement.volume * 100 + "%";
    trackProgressBar.textContent = trackProgressBar.style["width"];
  };
}

ws.addEventListener('message', event => {
  const keyEvent = JSON.parse(event.data);
  const usbStatus = document.getElementById("usb_status");

  if (keyEvent.state === "usb_disconnected") {
    usbStatus.textContent = "🔌 🚫";
  } else if (keyEvent.state === "usb_connected") {
    usbStatus.textContent = "🔌 ✅";
  } else if (keyEvent.state === "init") {
    colorizeTracksKbdElements(keyEvent.colors);
  } else if (keyEvent.state === "pause") {
    pauseAllPlayingTracks();
  } else if (keyEvent.state === "unpause") {
    unpauseAllPlayingTracks();
  } else {

    const trackProgressBar = document.getElementById(`progress_track_${keyEvent.key}`);
    const audioElement = document.getElementById(`audio_track_${keyEvent.key}`);

    if (audioElement === null) {
      return;
    }

    switch (keyEvent.state) {
      case "on":
        startTrack(keyEvent.key, audioElement, trackProgressBar);
        break;
      case "off":
        stopTrack(keyEvent.key, audioElement, trackProgressBar);
        break;
      case "vol_up":
        increaseTrackVolume(audioElement, trackProgressBar);
        break;
      case "vol_down":
        decreaseTrackVolume(audioElement, trackProgressBar);
        break;
    }
  }

});
