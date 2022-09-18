const ws = new WebSocket("ws://localhost:8000/key_events");
const tracksPlaying = {};

function pauseAllPlayingTracks() {
  Object.entries(tracksPlaying).forEach(([key, audioElement]) => {
    audioElement.pause();
    const trackProgressBar = document.getElementById(`progress_track_${key}`);
    trackProgressBar.classList.remove("bg-success");
    trackProgressBar.classList.add("bg-warning");
  });
}

function unpauseAllPlayingTracks() {
  Object.entries(tracksPlaying).forEach(([key, audioElement]) => {
    audioElement.play();
    const trackProgressBar = document.getElementById(`progress_track_${key}`);
    trackProgressBar.classList.remove("bg-warning");
    trackProgressBar.classList.add("bg-success");
  });
}

function startTrack(trackKey, trackAudioElement, trackProgressBar) {
  tracksPlaying[trackKey] = trackAudioElement;
  trackProgressBar.classList.remove("bg-secondary");
  trackProgressBar.classList.add("bg-success");
  trackProgressBar.textContent = "100%";
  trackAudioElement.play();
}

function stopTrack(trackKey, trackaudioElement, trackProgressBar) {
  trackProgressBar.classList.remove("bg-success");
  trackProgressBar.classList.add("bg-secondary");
  trackaudioElement.pause();
  trackaudioElement.currentTime = 0;
  trackaudioElement.volume = 1;
  trackProgressBar.style["width"] = '100%';
  trackProgressBar.textContent = "";
  delete tracksPlaying[trackKey];
}

function increaseTrackVolume(trackAudioElement, trackProgressBar) {
  if (trackAudioElement.volume + 0.1 <= 1) {
    trackAudioElement.volume += 0.1;
    trackProgressBar.style["width"] = trackAudioElement.volume * 100 + "%";
    trackProgressBar.textContent = trackProgressBar.style["width"];
  };
}

function decreaseTrackVolume(trackAudioElement, trackProgressBar) {
  if (trackAudioElement.volume - 0.1 > 0) {
    trackAudioElement.volume -= 0.1;
    trackProgressBar.style["width"] = trackAudioElement.volume * 100 + "%";
    trackProgressBar.textContent = trackProgressBar.style["width"];
  };
}

ws.addEventListener('message', event => {
  const keyEvent = JSON.parse(event.data);
  const usbStatus = document.getElementById("usb_status");

  if (keyEvent.state === "usb_disconnected") {
    usbStatus.textContent = "🚫";
  } else if (keyEvent.state === "usb_connected") {
    usbStatus.textContent = "✅";
  } else if (keyEvent.state === "pause") {
    pauseAllPlayingTracks();
  } else if (keyEvent.state === "unpause") {
    unpauseAllPlayingTracks();
  } else {

    const trackProgressBar = document.getElementById(`progress_track_${keyEvent.key}`);
    const audioElement = document.getElementById(`track_${keyEvent.key}`);
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
