function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));
}

function renderVideo(video) {
  const title = escapeHtml(video.title);
  const episode = escapeHtml(video.episode);
  const status = escapeHtml(video.status);
  const duration = escapeHtml(video.duration || '--:--');
  const summary = video.summary ? '<span>✦ Summary</span>' : '';
  const statusClass = video.status === 'AI Ready' ? 'ready' : 'processing';
  return `<article class="video-card"><a class="thumbnail thumb-${escapeHtml(video.thumbnail || 'cote')}" href="/video/${encodeURIComponent(video.id)}"><span class="play-overlay">▶</span><span class="duration">${duration}</span></a><div class="video-info"><div><h3>${title}</h3><p>${episode}</p></div><span class="status ${statusClass}">${status}</span></div><div class="video-meta"><span>⌁ ${Number(video.segments || 0).toLocaleString()} segments</span>${summary}</div></article>`;
}

async function loadDashboard() {
  const container = document.querySelector('#recentVideos');
  if (!container) return;
  const empty = document.querySelector('#dashboardEmpty');
  try {
    const response = await fetch('/api/dashboard');
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Dashboard data could not be loaded.');
    Object.entries(data.stats || {}).forEach(([key, value]) => {
      document.querySelector(`[data-stat="${key}"]`)?.replaceChildren(document.createTextNode(key === 'indexed_segments' ? Number(value).toLocaleString() : value));
    });
    container.querySelectorAll('[data-server-video]').forEach(video => video.remove());
    const videos = (data.videos || []).slice(0, 4);
    if (!videos.length) { empty?.classList.remove('hidden'); return; }
    empty?.remove();
    container.insertAdjacentHTML('afterbegin', videos.map(renderVideo).join(''));
  } catch (error) {
    if (typeof toast === 'function') toast(error.message, 'error');
  }
}

const librarySearch = document.querySelector('#librarySearch');
librarySearch?.addEventListener('input', () => {
  const query = librarySearch.value.toLowerCase().trim();
  let visible = 0;
  document.querySelectorAll('.library-item').forEach(card => {
    const show = card.dataset.title.includes(query);
    card.style.display = show ? '' : 'none';
    if (show) visible++;
  });
  document.querySelector('#emptyLibrary')?.classList.toggle('hidden', visible !== 0);
});

loadDashboard();
