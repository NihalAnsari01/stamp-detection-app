let pollingInterval = null;

function showError(message) {
  console.error("❌", message); // Just log errors now
}

function pollDetections() {
  // No need to fetch or display detections anymore
  // You can keep this function empty or remove it entirely
}

function startVideo() {
  const video = document.getElementById("videoFeed");
  try {
    video.src = "/video_feed";
    video.style.display = "block";

    if (!pollingInterval) {
      // Optional: start polling in future again
      pollingInterval = setInterval(pollDetections, 3000);
    }
  } catch (err) {
    console.error("Video error:", err);
    showError("Camera stream could not be started.");
  }
}

function stopVideo() {
  const video = document.getElementById("videoFeed");
  video.src = "";
  video.style.display = "none";

  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }

  fetch("/stop_video")
    .then(() => {
      console.log("Camera stopped successfully.");
    })
    .catch(err => {
      console.error("Error stopping camera:", err);
      showError("Could not stop camera on server.");
    });
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("startBtn").addEventListener("click", startVideo);
  document.getElementById("stopBtn").addEventListener("click", stopVideo);
});
