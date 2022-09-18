const ws = new WebSocket("ws://localhost:8000/key_events");
const tracksPlaying = {};

ws.addEventListener('message', event => {
  const keyEvent = JSON.parse(event.data);

  if (keyEvent.state === "pause") {
    Object.entries(tracksPlaying).forEach(([key, audioElement]) => {
      audioElement.pause();
      const trackProgressBar = document.getElementById(`progress_track_${key}`);
      trackProgressBar.classList.remove("bg-success");
      trackProgressBar.classList.add("bg-warning");
    });
  } else if (keyEvent.state === "unpause") {
    Object.entries(tracksPlaying).forEach(([key, audioElement]) => {
      audioElement.play();
      const trackProgressBar = document.getElementById(`progress_track_${key}`);
      trackProgressBar.classList.remove("bg-warning");
      trackProgressBar.classList.add("bg-success");
    });
  }

  const trackProgressBar = document.getElementById(`progress_track_${keyEvent.key}`);
  const audioElement = document.getElementById(`track_${keyEvent.key}`);
  if (audioElement === null) {
    return;
  }
  switch (keyEvent.state) {
    case "on":
      tracksPlaying[keyEvent.key] = audioElement;
      trackProgressBar.classList.remove("bg-secondary");
      trackProgressBar.classList.add("bg-success");
      trackProgressBar.textContent = "100%";
      audioElement.play();
      break;
    case "off":
      trackProgressBar.classList.remove("bg-success");
      trackProgressBar.classList.add("bg-secondary");
      audioElement.pause();
      audioElement.currentTime = 0;
      audioElement.volume = 1;
      trackProgressBar.style["width"] = '100%';
      trackProgressBar.textContent = "";
      delete tracksPlaying[keyEvent.key];
      break;
    case "vol_up":
      if (audioElement.volume + 0.1 <= 1) {
        audioElement.volume += 0.1;
        trackProgressBar.style["width"] = audioElement.volume * 100 + "%";
        trackProgressBar.textContent = trackProgressBar.style["width"];
      };
      break;
    case "vol_down":
      if (audioElement.volume - 0.1 > 0) {
        audioElement.volume -= 0.1;
        trackProgressBar.style["width"] = audioElement.volume * 100 + "%";
        trackProgressBar.textContent = trackProgressBar.style["width"];
      };
      break;
  }
});