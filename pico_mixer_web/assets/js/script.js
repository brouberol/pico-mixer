const ws = new WebSocket("ws://localhost:8000/key_events");
const tracksPlaying = {};
const volumeIncrement = 0.05;


function roundTo2Digits(num) {
  return Math.round(num * 100) / 100;
}

function pauseTrack(audioElement, trackProgressBar) {
  if (!(audioElement.paused && trackProgressBar.classList.contains("non-playing"))) {
    audioElement.pause();
    trackProgressBar.classList.add("paused");
  }
}

function unPauseTrack(audioElement, trackProgressBar) {
  if (audioElement.paused && trackProgressBar.classList.contains("paused")) {
    audioElement.play();
    trackProgressBar.classList.remove("paused");
  }
}

function pauseAllPlayingTracks() {
  Object.entries(tracksPlaying).forEach(([key, audioElement]) => {
    const trackProgressBar = document.getElementById(`progress_track_${key}`);
    pauseTrack(audioElement, trackProgressBar);
  });
}

function unpauseAllPlayingTracks() {
  Object.entries(tracksPlaying).forEach(([key, audioElement]) => {
    const trackProgressBar = document.getElementById(`progress_track_${key}`);
    unPauseTrack(audioElement, trackProgressBar)
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
  trackProgressBar.classList.remove("paused");
  trackProgressBar.textContent = "100%";
  trackProgressBar.style.backgroundColor = document.getElementsByClassName(`track_${trackKey}`)[0].style.backgroundColor;
  trackAudioElement.play();
}

function stopTrack(trackKey, trackaudioElement, trackProgressBar) {
  trackProgressBar.classList.add("non-playing");
  trackProgressBar.classList.remove("paused");
  trackaudioElement.pause();
  trackaudioElement.currentTime = 0;
  trackaudioElement.volume = 1;
  trackProgressBar.style.width = '100%';
  trackProgressBar.style.backgroundColor = null;
  trackProgressBar.textContent = "";
  delete tracksPlaying[trackKey];
}

function increaseTrackVolume(trackAudioElement, trackProgressBar) {
  if (roundTo2Digits(trackAudioElement.volume + volumeIncrement <= 1)) {
    trackAudioElement.volume = roundTo2Digits(trackAudioElement.volume + volumeIncrement);
    trackProgressBar.style["width"] = trackAudioElement.volume * 100 + "%";
    trackProgressBar.textContent = trackProgressBar.style["width"];
  };
}

function decreaseTrackVolume(trackAudioElement, trackProgressBar) {
  if (roundTo2Digits(trackAudioElement.volume - volumeIncrement) >= 0) {
    trackAudioElement.volume = roundTo2Digits(trackAudioElement.volume - volumeIncrement);
    trackProgressBar.style["width"] = trackAudioElement.volume * 100 + "%";
    trackProgressBar.textContent = trackProgressBar.style["width"];
  };
}

function alertAboutTrackNotFound(trackNode) {
  warningNode = document.createElement("span");
  warningNode.className = 'track-warning';
  warningNode.textContent = "⚠ not found!️";
  trackNode.appendChild(warningNode);
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
  } else if (keyEvent.state === "pause_all") {
    pauseAllPlayingTracks();
  } else if (keyEvent.state === "unpause_all") {
    unpauseAllPlayingTracks();
  } else {

    const trackProgressBar = document.getElementById(`progress_track_${keyEvent.key}`);
    const audioElement = document.getElementById(`audio_track_${keyEvent.key}`);

    if (audioElement === null) {
      return;
    }

    switch (keyEvent.state) {
      case "start":
        startTrack(keyEvent.key, audioElement, trackProgressBar);
        break;
      case "stop":
        stopTrack(keyEvent.key, audioElement, trackProgressBar);
        break;
      case "vol_up":
        increaseTrackVolume(audioElement, trackProgressBar);
        break;
      case "vol_down":
        decreaseTrackVolume(audioElement, trackProgressBar);
        break;
      case "pause":
        pauseTrack(audioElement, trackProgressBar);
        break;
      case "unpause":
        unPauseTrack(audioElement, trackProgressBar);
        break;
    }
  }

});


async function probeAudioTrack(audioNode) {
  await fetch(audioNode.src, { "method": "HEAD" }).then((response) => {
    if (response.status != 200) {
      alertAboutTrackNotFound(audioNode.parentNode);
    }
  })
}

window.addEventListener('load', function () {
  audioNodes = document.getElementsByTagName('audio')
  for (let i = 0; i < audioNodes.length; i++) {
    audioNode = document.getElementById(`audio_track_${i}`);
    probeAudioTrack(audioNode);
  }
})