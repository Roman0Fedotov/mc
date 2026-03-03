(function () {
  const root = document.getElementById("alpha-filter");
  const countEl = document.getElementById("ms-count");

  // только строки верхней таблицы (без вложенностей)
  const rows = Array.from(document.querySelectorAll("#ms-table > tbody > tr"))
    .filter(r => r.hasAttribute("data-letter"));

  if (!root || !countEl || rows.length === 0) return;

  function apply(letter) {
    let visible = 0;

    rows.forEach(r => {
      const L = (r.getAttribute("data-letter") || "#");
      const show = (letter === "ALL") ? true : (L === letter);
      r.style.display = show ? "" : "none";
      if (show) visible++;
    });

    const noun = (visible === 1) ? "manuscript" : "manuscripts";
    countEl.textContent = visible + " " + noun + (letter === "ALL" ? "" : (" (" + letter + ")"));
  }

  root.addEventListener("click", (e) => {
    const a = e.target.closest("a[data-letter]");
    if (!a) return;
    e.preventDefault();
    apply((a.getAttribute("data-letter") || "ALL").toUpperCase());
  });

  apply("ALL");
})();