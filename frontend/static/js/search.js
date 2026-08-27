/**
 * AniSense AI - Semantic Search Controller
 * Connects frontend UI to /api/search API endpoint.
 */

document.addEventListener("DOMContentLoaded", () => {
  const searchForm = document.querySelector("#searchForm");
  const input = document.querySelector("#searchInput");
  const resultsContainer = document.querySelector("#results");
  const loadingIndicator = document.querySelector("#searchLoading");
  const resultCount = document.querySelector("#resultCount");
  const resultTitle = document.querySelector("#resultTitle");
  const timelineTicks = document.querySelector(".timeline");

  let currentScope = "both";

  // Filter button handlers
  document.querySelectorAll(".filter").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentScope = btn.dataset.scope || "both";
      if (input && input.value.trim()) {
        performSearch(input.value.trim());
      }
    });
  });

  // Render timeline markers for video timestamp results
  function renderTimelineMarkers(items) {
    if (!timelineTicks) return;
    const existingMarkers = timelineTicks.querySelectorAll(".marker");
    existingMarkers.forEach((m) => m.remove());

    const maxDuration = 1800; // 30 minutes reference for timeline visualization

    items.forEach((item, index) => {
      if (item.source === "transcript" && item.start_seconds > 0) {
        const percent = Math.min(95, Math.max(5, (item.start_seconds / maxDuration) * 100));
        const markerBtn = document.createElement("button");
        markerBtn.className = `marker m${(index % 3) + 1}`;
        markerBtn.style.left = `${percent.toFixed(1)}%`;
        markerBtn.textContent = item.timestamp_label.split(" - ")[0] || item.timestamp_label;
        markerBtn.title = `${item.video_title} (${item.timestamp_label})`;

        markerBtn.addEventListener("click", () => {
          window.location.href = item.watch_url;
        });

        timelineTicks.appendChild(markerBtn);
      }
    });
  }

  // Render search hit result cards
  function renderResults(items, queryText) {
    if (!resultsContainer) return;

    const displayItems = (items || []).slice(0, 4);

    if (!displayItems || displayItems.length === 0) {
      resultsContainer.innerHTML = `
        <div class="empty-search-state" style="text-align: center; padding: 40px 20px; color: var(--text-muted, #94a3b8);">
          <div style="font-size: 2.5rem; margin-bottom: 12px;">⌕</div>
          <h3 style="font-size: 1.25rem; color: var(--text-main, #f8fafc); margin-bottom: 8px;">No matching moments found</h3>
          <p>Try refining your search terms or selecting "All Content" filter.</p>
        </div>
      `;
      if (resultCount) resultCount.textContent = "0 relevant moments";
      if (resultTitle) resultTitle.textContent = `Search results for "${queryText}"`;
      renderTimelineMarkers([]);
      return;
    }

    if (resultTitle) resultTitle.textContent = `Results for "${queryText}"`;
    if (resultCount) resultCount.textContent = `${displayItems.length} relevant moment${displayItems.length === 1 ? "" : "s"}`;

    resultsContainer.innerHTML = displayItems
      .map(
        (r, i) => {
          const watchUrl = r.watch_url || `/video/${encodeURIComponent(r.video_id)}?t=${encodeURIComponent(r.start_seconds || 0)}`;
          const videoUrl = `/video/${encodeURIComponent(r.video_id)}`;
          return `
      <article class="result-card">
        <div class="result-top">
          <span class="result-index">0${i + 1}</span>
          <div>
            <h3>${r.video_title} — ${r.episode}</h3>
            <span class="result-time">▶ ${r.timestamp_label}</span>
            <span class="pill soft" style="margin-left: 8px; font-size: 0.75rem;">${r.source === "summary" ? "Episode Summary" : "Transcript Moment"}</span>
          </div>
          <div class="match">
            <strong>${r.semantic_match_percent}%</strong>
            <span>Semantic Match</span>
            <i><b style="width:${r.semantic_match_percent}%"></b></i>
          </div>
        </div>
        <p>${r.source === "summary" ? "Summary snippet:" : "Transcript snippet:"}</p>
        <blockquote style="line-height: 1.6;">${r.matched_text}</blockquote>
        <div class="result-actions">
          <a class="btn primary small" href="${watchUrl}">▶ Watch Moment</a>
          <a class="btn ghost small" href="${videoUrl}">Open Video</a>
        </div>
      </article>
    `;
        }
      )
      .join("");

    renderTimelineMarkers(displayItems);
  }

  // Execute API Search
  async function performSearch(queryText) {
    if (!queryText) return;

    if (resultsContainer) resultsContainer.classList.add("hidden");
    if (loadingIndicator) loadingIndicator.classList.remove("hidden");

    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: queryText,
          top_k: 4,
          scope: currentScope,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || "Search execution failed.");
      }

      renderResults(data.results, data.query || queryText);
    } catch (error) {
      console.error("Search error:", error);
      if (typeof toast === "function") {
        toast(error.message || "Search service is unavailable.", "error");
      }
      if (resultsContainer) {
        resultsContainer.innerHTML = `
          <div class="search-error" style="padding: 24px; text-align: center; color: #ef4444;">
            <p><strong>Search Error:</strong> ${error.message || "Unable to reach search service."}</p>
          </div>
        `;
      }
    } finally {
      if (loadingIndicator) loadingIndicator.classList.add("hidden");
      if (resultsContainer) resultsContainer.classList.remove("hidden");
    }
  }

  // Handle search form submission
  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const val = input ? input.value.trim() : "";
      if (!val) {
        if (typeof toast === "function") toast("Please enter a search query.", "error");
        return;
      }
      // Update URL query string without reloading page
      const newUrl = `${window.location.pathname}?q=${encodeURIComponent(val)}`;
      window.history.pushState({ path: newUrl }, "", newUrl);

      performSearch(val);
    });
  }

  // Auto-search if 'q' parameter is present in URL
  const urlParams = new URLSearchParams(window.location.search);
  const initialQuery = urlParams.get("q");
  if (initialQuery && initialQuery.trim()) {
    if (input) input.value = initialQuery.trim();
    performSearch(initialQuery.trim());
  }
});
