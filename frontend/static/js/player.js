const player = document.querySelector("#videoPlayer");
const bigPlay = document.querySelector("#bigPlay");
bigPlay?.addEventListener("click", () => {
  bigPlay.textContent = "Ⅱ";
  bigPlay.classList.add("playing");
  toast("Video preview playing");
});
document.querySelectorAll("[data-time]").forEach(btn => btn.addEventListener("click", () => {
  document.querySelectorAll(".transcript-row").forEach(r => r.classList.remove("active"));
  btn.classList.add("active");
  toast(`Jumped to ${btn.dataset.time || btn.textContent.trim()}`);
}));
