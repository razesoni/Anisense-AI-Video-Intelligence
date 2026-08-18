const searchForm = document.querySelector("#searchForm");
const input = document.querySelector("#searchInput");
const results = document.querySelector("#results");
const loading = document.querySelector("#searchLoading");
const count = document.querySelector("#resultCount");

function renderResults(items) {
  results.innerHTML = items.map((r, i) => `
    <article class="result-card">
      <div class="result-top"><span class="result-index">0${i+1}</span><div><h3>${r.video}</h3><span class="result-time">▶ ${r.time}</span></div>
      <div class="match"><strong>${r.match}%</strong><span>Semantic Match</span><i><b style="width:${r.match}%"></b></i></div></div>
      <p>Transcript snippet:</p><blockquote>${r.snippet}</blockquote>
      <div class="result-actions"><a class="btn primary small" href="/video/1">▶ Watch Moment</a><button class="btn ghost small">View Transcript</button><a class="btn ghost small" href="/video/1">Open Video</a></div>
    </article>`).join("");
  count.textContent = `${items.length} relevant moments`;
}
searchForm?.addEventListener("submit", async e => {
  e.preventDefault();
  const query = input.value.trim();
  if (!query) return toast("Describe the moment you want to find.", "error");
  results.classList.add("hidden"); loading.classList.remove("hidden");
  try {
    await new Promise(r => setTimeout(r, 850));
    const res = await fetch("/api/search", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({query})});
    const data = await res.json();
    renderResults(data.results);
    toast("Search completed");
  } catch {
    toast("Search service is unavailable.", "error");
  } finally {
    loading.classList.add("hidden"); results.classList.remove("hidden");
  }
});
document.querySelectorAll(".filter").forEach(btn => btn.addEventListener("click", () => {
  document.querySelectorAll(".filter").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
}));
document.querySelectorAll(".marker").forEach(m => m.addEventListener("click", () => toast(`Opening video at ${m.textContent}`)));
