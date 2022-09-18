const ws = new WebSocket("ws://localhost:8000/key_events");
const tracksPlaying = {};

ws.addEventListener('message', event => {
  const keyEvent = JSON.parse(event.data);

  if (keyEvent.state === "pause") {
    Object.values(tracksPlaying).forEach(audioElement => {
      audioElement.pause();
    });
  } else if (keyEvent.state === "unpause") {
    Object.values(tracksPlaying).forEach(audioElement => {
      audioElement.play();
    });
  }

  const audioElement = document.getElementById(`track_${keyEvent.key}`);
  if (audioElement === null) {
    return;
  }
  switch (keyEvent.state) {
    case "on":
      tracksPlaying[keyEvent.key] = audioElement;
      audioElement.play();
      break;
    case "off":
      audioElement.pause();
      audioElement.currentTime = 0;
      delete tracksPlaying[keyEvent.key];
      break;
    case "vol_up":
      if (audioElement.volume <= 0.9) {
        audioElement.volume += 0.1;
      };
      break;
    case "vol_down":
      if (audioElement.volume > 0) {
        audioElement.volume -= 0.1;
      };
      break;
  }
});