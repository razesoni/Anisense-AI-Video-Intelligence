const player = document.querySelector("#videoElement");
const bigPlay = document.querySelector("#bigPlay");
const requestedTime = Number(new URLSearchParams(window.location.search).get("t"));
let pendingSeek = null;

function seekTo(seconds, announce = true, shouldPlay = false) {
  if (!player || !Number.isFinite(seconds) || seconds < 0) return;
  if (player.readyState < 1) {
    pendingSeek = { seconds, announce, shouldPlay };
    return;
  }
  const target = Math.min(seconds, Number.isFinite(player.duration) ? player.duration : seconds);
  player.currentTime = target;
  if (shouldPlay) player.play().catch(() => {});
  if (announce && typeof toast === "function") toast(`Jumped to ${formatTime(target)}`);
}

function formatTime(seconds) {
  const total = Math.max(0, Math.round(seconds));
  const minutes = Math.floor(total / 60);
  return `${String(minutes).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`;
}

player?.addEventListener("loadedmetadata", () => {
  if (pendingSeek) {
    const seek = pendingSeek;
    pendingSeek = null;
    seekTo(seek.seconds, seek.announce, seek.shouldPlay);
  }
  if (Number.isFinite(requestedTime) && requestedTime >= 0) seekTo(requestedTime, false);
});

bigPlay?.addEventListener("click", () => {
  bigPlay.textContent = "Ⅱ";
  bigPlay.classList.add("playing");
  toast("Video preview playing");
});

document.querySelectorAll("[data-time]").forEach(btn => btn.addEventListener("click", () => {
  document.querySelectorAll(".transcript-row").forEach(r => r.classList.remove("active"));
  btn.classList.add("active");
  const timestamp = (btn.dataset.time || btn.textContent.trim()).trim();
  const numericTimestamp = Number(timestamp);
  const parts = timestamp.split(":").map(Number);
  const seconds = Number.isFinite(numericTimestamp) ? numericTimestamp : parts.length === 3 ? parts[0] * 3600 + parts[1] * 60 + parts[2] : parts[0] * 60 + parts[1];
  seekTo(seconds, true, true);
}));

player?.addEventListener("error", () => {
  if (typeof toast === "function") toast("This video could not be loaded.", "error");
});
