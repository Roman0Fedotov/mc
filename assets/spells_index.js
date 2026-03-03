(function () {
  // только верхнеуровневые строки таблицы (без вложенной таблицы occurrences)
  const rows = Array.from(document.querySelectorAll("#sp-table > tbody > tr"))
    .filter(r => r.hasAttribute("data-letter"));

  const countEl = document.getElementById("sp-count");
  const alphaRoot = document.getElementById("sp-alpha-filter");
  const perSel = document.getElementById("sp-per-page");
  const pagerEls = Array.from(document.querySelectorAll('[data-role="sp-pager"]'));

  if (!rows.length || !countEl || !alphaRoot || !perSel || pagerEls.length === 0) return;

  const allowedPer = new Set([20, 50, 100]);
  const allowedLetters = new Set(["ALL", "OTHER", ..."ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("")]);

  const state = { letter: "ALL", per: 20, page: 1 };

  function readStateFromUrl() {
    const p = new URLSearchParams(window.location.search);
    const per = parseInt(p.get("per") || "", 10);
    const page = parseInt(p.get("page") || "", 10);
    const letter = (p.get("letter") || "ALL").toUpperCase().trim();

    state.per = allowedPer.has(per) ? per : 20;
    state.page = Number.isFinite(page) && page > 0 ? page : 1;
    state.letter = allowedLetters.has(letter) ? letter : "ALL";

    perSel.value = String(state.per);
  }

  function buildHref(page) {
    const p = new URLSearchParams(window.location.search);
    p.set("per", String(state.per));
    p.set("page", String(page));
    p.set("letter", state.letter);
    return window.location.pathname + "?" + p.toString();
  }

  function writeStateToUrl() {
    const p = new URLSearchParams();
    p.set("per", String(state.per));
    p.set("page", String(state.page));
    p.set("letter", state.letter);
    history.replaceState(null, "", window.location.pathname + "?" + p.toString());
  }

  function rowsForLetter(letter) {
    if (letter === "ALL") return rows;
    return rows.filter(r => (r.getAttribute("data-letter") || "OTHER") === letter);
  }

  function addPagerItem(container, label, page, opts) {
    const a = document.createElement("a");
    a.textContent = label;
    a.href = buildHref(page);
    a.setAttribute("data-page", String(page));
    if (opts?.active) a.classList.add("active");
    if (opts?.disabled) a.classList.add("disabled");
    container.appendChild(a);
  }

  function addEllipsis(container) {
    const span = document.createElement("span");
    span.className = "ellipsis";
    span.textContent = "…";
    container.appendChild(span);
  }

  function renderPager(total) {
    const pages = Math.max(1, Math.ceil(total / state.per));
    const cur = Math.min(Math.max(1, state.page), pages);

    for (const container of pagerEls) {
      container.innerHTML = "";

      if (pages <= 1) {
        container.style.display = "none";
        continue;
      }
      container.style.display = "";

      addPagerItem(container, "Prev", Math.max(1, cur - 1), { disabled: cur === 1 });

      const wanted = new Set([1, pages]);
      for (let i = cur - 2; i <= cur + 2; i++) {
        if (i >= 1 && i <= pages) wanted.add(i);
      }
      const nums = Array.from(wanted).sort((a, b) => a - b);

      let last = 0;
      for (const n of nums) {
        if (last && n - last > 1) addEllipsis(container);
        addPagerItem(container, String(n), n, { active: n === cur });
        last = n;
      }

      addPagerItem(container, "Next", Math.min(pages, cur + 1), { disabled: cur === pages });
    }
  }

  function apply() {
    const filtered = rowsForLetter(state.letter);
    const total = filtered.length;

    const pages = Math.max(1, Math.ceil(total / state.per));
    state.page = Math.min(Math.max(1, state.page), pages);

    rows.forEach(r => (r.style.display = "none"));

    const start = (state.page - 1) * state.per;
    const end = start + state.per;
    filtered.slice(start, end).forEach(r => (r.style.display = ""));

    const noun = (total === 1) ? "spell title" : "spell titles";
    countEl.textContent = total + " " + noun + (state.letter === "ALL" ? "" : (" (" + state.letter + ")"));

    renderPager(total);
    writeStateToUrl();
  }

  alphaRoot.addEventListener("click", (e) => {
    const a = e.target.closest("a[data-letter]");
    if (!a) return;
    e.preventDefault();
    state.letter = (a.getAttribute("data-letter") || "ALL").toUpperCase();
    state.page = 1;
    apply();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  perSel.addEventListener("change", () => {
    const v = parseInt(perSel.value, 10);
    state.per = allowedPer.has(v) ? v : 20;
    state.page = 1;
    apply();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  for (const container of pagerEls) {
    container.addEventListener("click", (e) => {
      const a = e.target.closest("a[data-page]");
      if (!a || a.classList.contains("disabled") || a.classList.contains("active")) return;
      e.preventDefault();

      const p = parseInt(a.getAttribute("data-page") || "", 10);
      if (!Number.isFinite(p)) return;

      state.page = p;
      apply();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  window.addEventListener("popstate", () => {
    readStateFromUrl();
    apply();
  });

  readStateFromUrl();
  apply();
})();