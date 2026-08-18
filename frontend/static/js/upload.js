const fileInput = document.querySelector("#videoFile");
const browseBtn = document.querySelector("#browseBtn");
const uploadZone = document.querySelector(".upload-zone");
const preview = document.querySelector("#filePreview");
const form = document.querySelector("#uploadForm");

browseBtn?.addEventListener("click", () => fileInput.click());

function showFile(file) {
  if (!file) return;
  const size = (file.size / (1024 * 1024)).toFixed(1);
  preview.classList.remove("hidden");
  preview.innerHTML = `<div class="file-icon">▣</div><div><strong>${file.name}</strong><span>${size} MB · ${file.type || "video file"}</span></div><button type="button" id="removeFile">×</button>`;
  document.querySelector("#removeFile").onclick = () => {
    fileInput.value = "";
    preview.classList.add("hidden");
    preview.innerHTML = "";
  };
}
fileInput?.addEventListener("change", e => showFile(e.target.files[0]));

["dragenter","dragover"].forEach(type => uploadZone?.addEventListener(type, e => {
  e.preventDefault(); uploadZone.classList.add("dragging");
}));
["dragleave","drop"].forEach(type => uploadZone?.addEventListener(type, e => {
  e.preventDefault(); uploadZone.classList.remove("dragging");
}));
uploadZone?.addEventListener("drop", e => {
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("video/")) {
    const dt = new DataTransfer(); dt.items.add(file); fileInput.files = dt.files; showFile(file);
  } else toast("Please choose a supported video file.", "error");
});

form?.addEventListener("submit", async e => {
  e.preventDefault();
  const file = fileInput.files[0];
  if (!file) return toast("Choose a video before processing.", "error");
  if (file.size > 2 * 1024 * 1024 * 1024) return toast("Maximum file size is 2 GB.", "error");
  const button = form.querySelector(".upload-submit");
  button.disabled = true;
  button.textContent = "Uploading…";
  const data = new FormData(form);
  try {
    const res = await fetch("/api/upload", {method:"POST", body:data});
    const json = await res.json();
    if (!json.success) throw new Error(json.message);
    button.textContent = "Processing started ✓";
    toast("Video uploaded successfully");
    setTimeout(() => {
      document.querySelectorAll(".pipeline-step").forEach((step, i) => {
        if (i < 2) { step.classList.add("done"); step.querySelector(".step-state").textContent = "Completed"; }
      });
    }, 500);
  } catch (err) {
    toast(err.message || "Unable to process video", "error");
    button.disabled = false; button.textContent = "Process Video →";
  }
});
