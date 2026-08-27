document.addEventListener('DOMContentLoaded', async () => {
  try {
    const response = await fetch('/api/dashboard');
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Analytics data could not be loaded.');
    Object.entries(data.stats || {}).forEach(([key, value]) => {
      const element = document.querySelector(`[data-stat="${key}"]`);
      if (element) element.textContent = key === 'indexed_segments' ? Number(value).toLocaleString() : value;
    });
  } catch (error) {
    document.querySelectorAll('[data-stat]').forEach(element => { element.textContent = '--'; });
    if (typeof toast === 'function') toast(error.message, 'error');
  }
});
