document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('uploadForm');
  const fileInput = document.getElementById('videoFile');
  const browseBtn = document.getElementById('browseBtn');
  const titleInput = document.getElementById('animeTitle');
  const seasonInput = document.getElementById('animeSeason');
  const episodeInput = document.getElementById('animeEpisode');
  const previewText = document.getElementById('targetFilenamePreview');
  const progress = document.getElementById('uploadProgress');
  const progressText = document.getElementById('uploadProgressText');
  const submitButton = form.querySelector('.upload-submit');
  const pipelineSteps = document.querySelectorAll('.pipeline-step');

  browseBtn.addEventListener('click', () => fileInput.click());

  // Function to compute and show canonical filename preview
  function updatePreview() {
    const rawTitle = titleInput.value.trim();
    const season = seasonInput.value || '1';
    const episode = String(episodeInput.value || '1').padStart(2, '0');

    if (rawTitle && fileInput.files[0]) {
      const ext = fileInput.files[0].name.split('.').pop();
      const cleanTitle = rawTitle.replace(/[\s_]+/g, '-').replace(/[^a-zA-Z0-9\-]/g, '');
      const formatted = `${cleanTitle}_S${season}_Ep-${episode}.${ext}`;
      previewText.textContent = `Canonical Output: ${formatted}`;
    } else {
      previewText.textContent = '';
    }
  }

  titleInput.addEventListener('input', updatePreview);
  seasonInput.addEventListener('input', updatePreview);
  episodeInput.addEventListener('input', updatePreview);
  fileInput.addEventListener('change', updatePreview);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!fileInput.files[0]) {
      alert('Please select a video file.');
      return;
    }

    const formData = new FormData(form);
    submitButton.disabled = true;
    progress.classList.remove('hidden');
    progressText.textContent = 'Uploading video and preparing ingestion...';

    try {
      const response = await fetch('/api/v1/ingestion/upload', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      if (response.ok) {
        await pollIngestion(data.job_id);
      } else {
        alert(data.detail || data.message || 'Upload failed.');
        resetUploadState();
      }
    } catch (err) {
      alert(`Upload error: ${err.message}`);
      resetUploadState();
    }
  });

  async function pollIngestion(jobId) {
    const poll = async () => {
      const response = await fetch(`/api/v1/ingestion/status/${jobId}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Could not read ingestion status.');
      updatePipeline(data);
      if (data.status === 'completed') {
        progressText.textContent = 'Ingestion complete. Opening dashboard...';
        window.location.href = `/video/${encodeURIComponent(data.result.video_id)}`;
        return;
      }
      if (data.status === 'failed') throw new Error(data.message || 'Ingestion failed.');
      setTimeout(poll, 1000);
    };
    await poll();
  }

  function updatePipeline(data) {
    const stageNames = ['validation', 'audio', 'transcription', 'cleaning', 'indexing', 'summarization'];
    const labels = {
      validation: 'Validation', audio: 'Audio extraction', transcription: 'Transcription',
      cleaning: 'Transcript cleaning', summarization: 'Summarization', indexing: 'Semantic indexing'
    };
    pipelineSteps.forEach((step, index) => {
      const state = data.stages[stageNames[index]] || 'pending';
      step.classList.remove('pending', 'active', 'done', 'error');
      step.classList.add(state);
      step.querySelector('.step-state').textContent = state === 'active' ? 'Working' : state[0].toUpperCase() + state.slice(1);
    });
    progressText.textContent = data.current_stage ? `${labels[data.current_stage]} in progress...` : data.message;
  }

  function resetUploadState() {
    submitButton.disabled = false;
    progress.classList.add('hidden');
  }
});