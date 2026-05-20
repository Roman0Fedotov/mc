(function () {
  const currentSearch = window.location.search || "";
  const currentHash = window.location.hash || "";

  document.querySelectorAll("[data-lang-switch]").forEach(link => {
    link.addEventListener("click", function (e) {
      const lang = this.getAttribute("data-lang-switch");
      if (!lang) return;

      localStorage.setItem("preferred_lang", lang);

      const href = this.getAttribute("href");
      if (!href) return;

      e.preventDefault();
      window.location.href = href + currentSearch + currentHash;
    });
  });

  const htmlLang = document.documentElement.getAttribute("lang");
  if (htmlLang === "ru" || htmlLang === "en") {
    localStorage.setItem("preferred_lang", htmlLang);
  }
})();