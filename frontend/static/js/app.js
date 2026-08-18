const qs = (s, root=document) => root.querySelector(s);
const qsa = (s, root=document) => [...root.querySelectorAll(s)];

function toast(message, type="success") {
  const stack = qs("#toastStack");
  if (!stack) return;
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.innerHTML = `<span>${type === "success" ? "✓" : "!"}</span><div>${message}</div>`;
  stack.appendChild(el);
  setTimeout(() => el.classList.add("show"), 20);
  setTimeout(() => { el.classList.remove("show"); setTimeout(() => el.remove(), 250); }, 3200);
}

const globalSearch = qs("#globalSearch");
function openSearch() {
  if (!globalSearch) return;
  globalSearch.classList.add("open");
  globalSearch.setAttribute("aria-hidden", "false");
  setTimeout(() => qs(".global-search-form input", globalSearch)?.focus(), 100);
}
function closeSearch() {
  globalSearch?.classList.remove("open");
  globalSearch?.setAttribute("aria-hidden", "true");
}
qsa("[data-open-search]").forEach(b => b.addEventListener("click", openSearch));
qsa("[data-close-search]").forEach(b => b.addEventListener("click", closeSearch));
globalSearch?.addEventListener("click", e => { if (e.target === globalSearch) closeSearch(); });
document.addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); openSearch(); }
  if (e.key === "Escape") closeSearch();
});

const sidebar = qs("#sidebar");
qs("#menuToggle")?.addEventListener("click", () => sidebar?.classList.toggle("open"));

qsa(".suggestions button").forEach(b => b.addEventListener("click", () => {
  const input = qs(".global-search-form input");
  if (input) input.value = b.textContent;
  qs(".global-search-form")?.requestSubmit();
}));

qsa(".btn, .nav-link, .quick-card, .video-card").forEach(el => {
  el.addEventListener("click", () => el.classList.add("clicked"));
});


// Anime atmosphere theme toggle with local persistence.
const themeToggle = qs("#themeToggle");
const savedTheme = localStorage.getItem("anisense-theme");

if (savedTheme === "dark") {
  document.body.classList.add("anime-dark");
  if (themeToggle) themeToggle.textContent = "☀";
}

themeToggle?.addEventListener("click", () => {
  const dark = document.body.classList.toggle("anime-dark");
  localStorage.setItem("anisense-theme", dark ? "dark" : "light");
  themeToggle.textContent = dark ? "☀" : "☾";
  toast(dark ? "Dreamy night theme enabled" : "Soft daylight theme enabled");
});
