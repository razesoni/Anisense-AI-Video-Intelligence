function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));
}

function renderStats(stats) {
  Object.entries(stats || {}).forEach(([key, value]) => {
    const element = document.querySelector(`[data-stat="${key}"]`);
    if (element) element.textContent = key === 'indexed_segments' ? Number(value).toLocaleString() : value;
  });
}

function renderTrend(videos) {
  const chart = document.querySelector('#processingTrendChart');
  if (!chart) return;
  if (!videos.length) {
    chart.innerHTML = '<div class="chart-empty"><b>No processing data yet</b><small>Upload a video to start building your library trend.</small></div>';
    return;
  }
  const maxSegments = Math.max(...videos.map(video => Number(video.segments || 0)), 1);
  const bars = videos.map(video => {
    const height = Math.max(8, Math.round((Number(video.segments || 0) / maxSegments) * 100));
    return `<div class="trend-item" title="${escapeHtml(video.title)}: ${Number(video.segments || 0).toLocaleString()} segments"><span class="trend-bar" style="height:${height}%"></span><small>${escapeHtml(video.episode || video.title)}</small></div>`;
  }).join('');
  chart.innerHTML = `<span class="chart-grid"></span><div class="trend-bars">${bars}</div><div class="trend-axis"><span>0 segments</span><span>${maxSegments.toLocaleString()} max</span></div>`;
}

function renderStatus(videos) {
  const container = document.querySelector('#statusBreakdown');
  if (!container) return;
  const counts = videos.reduce((result, video) => {
    const status = video.status === 'AI Ready' ? 'ready' : video.status === 'Processing' ? 'processing' : 'other';
    result[status] += 1;
    return result;
  }, { ready: 0, processing: 0, other: 0 });
  const total = videos.length || 1;
  const readyEnd = counts.ready / total * 100;
  const processingEnd = readyEnd + counts.processing / total * 100;
  container.querySelector('.status-ring').style.background = `radial-gradient(circle, var(--bg-secondary) 51%, transparent 52%), conic-gradient(#79c8a0 0 ${readyEnd}%, #8d57d8 ${readyEnd}% ${processingEnd}%, #5b526f ${processingEnd}% 100%)`;
  container.querySelector('.status-ring span').textContent = `${videos.length} video${videos.length === 1 ? '' : 's'}`;
  container.querySelector('.ready-count').textContent = counts.ready;
  container.querySelector('.processing-count').textContent = counts.processing;
  container.querySelector('.other-count').textContent = counts.other;
}

function renderActivity(videos) {
  const container = document.querySelector('#recentActivity');
  if (!container) return;
  if (!videos.length) {
    container.innerHTML = '<div><b>No processing events yet</b><small>Upload a video to see ingestion, summary, and indexing activity here.</small></div>';
    return;
  }
  container.classList.add('activity-list');
  container.innerHTML = videos.slice(-4).reverse().map(video => {
    const status = video.status === 'AI Ready' ? 'Ready' : escapeHtml(video.status || 'Indexed');
    return `<div class="activity-row"><span class="activity-dot ${video.status === 'AI Ready' ? 'ready' : 'processing'}"></span><div><b>${escapeHtml(video.title)} · ${escapeHtml(video.episode)}</b><small>${status} · ${Number(video.segments || 0).toLocaleString()} indexed segments</small></div></div>`;
  }).join('');
}

document.addEventListener('DOMContentLoaded', async () => {
  try {
    const response = await fetch('/api/dashboard');
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Analytics data could not be loaded.');
    const videos = Array.isArray(data.videos) ? data.videos : [];
    renderStats(data.stats);
    renderTrend(videos);
    renderStatus(videos);
    renderActivity(videos);
  } catch (error) {
    document.querySelectorAll('[data-stat]').forEach(element => { element.textContent = '--'; });
    if (typeof toast === 'function') toast(error.message, 'error');
  }
});
