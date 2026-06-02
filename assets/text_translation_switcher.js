(function () {
  document.querySelectorAll('[data-translation-switcher]').forEach(block => {
    const initial = block.getAttribute('data-active-translation') || document.documentElement.lang || 'ru';

    function apply(lang) {
      const safeLang = (lang === 'en') ? 'en' : 'ru';
      block.setAttribute('data-active-translation', safeLang);

      block.querySelectorAll('[data-translation-target]').forEach(button => {
        const active = button.getAttribute('data-translation-target') === safeLang;
        button.classList.toggle('active', active);
        button.setAttribute('aria-pressed', active ? 'true' : 'false');
      });
    }

    block.addEventListener('click', event => {
      const button = event.target.closest('[data-translation-target]');
      if (!button || !block.contains(button)) return;

      apply(button.getAttribute('data-translation-target'));
    });

    apply(initial);
  });
})();