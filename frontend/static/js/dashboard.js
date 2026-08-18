const librarySearch = document.querySelector("#librarySearch");
librarySearch?.addEventListener("input", () => {
  const query = librarySearch.value.toLowerCase().trim();
  let visible = 0;
  document.querySelectorAll(".library-item").forEach(card => {
    const show = card.dataset.title.includes(query);
    card.style.display = show ? "" : "none";
    if (show) visible++;
  });
  document.querySelector("#emptyLibrary")?.classList.toggle("hidden", visible !== 0);
});
