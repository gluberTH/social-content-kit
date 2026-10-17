(() => {
  'use strict';
  const cards = [...document.querySelectorAll('.card')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  const week = document.querySelector('#week');
  const search = document.querySelector('#search');
  const dialog = document.querySelector('#copy-dialog');
  const fallback = document.querySelector('#copy-fallback');
  const toast = document.querySelector('#toast');
  let platform = 'all', lastButton, timer;
  function filter() {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    cards.forEach(card => {
      card.hidden = !((platform === 'all' || card.dataset.platform === platform) && (week.value === 'all' || card.dataset.week === week.value) && (!query || card.dataset.search.includes(query)));
      if (!card.hidden) visible++;
    });
    document.querySelector('#result-count').textContent = `Showing ${visible} of ${cards.length} posts`;
    document.querySelector('#empty').hidden = visible !== 0;
    filters.forEach(button => {
      const active = button.dataset.filter === platform;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
  }
  function reset() { platform = 'all'; week.value = 'all'; search.value = ''; filter(); }
  filters.forEach(button => button.addEventListener('click', () => { platform = button.dataset.filter; filter(); }));
  week.addEventListener('change', filter);
  search.addEventListener('input', filter);
  document.querySelector('#reset').addEventListener('click', reset);
  document.querySelectorAll('[data-open-post]').forEach(link => link.addEventListener('click', () => {
    reset();
    const card = document.getElementById('post-' + link.dataset.openPost);
    if (card) { card.tabIndex = -1; requestAnimationFrame(() => card.focus({preventScroll: true})); }
  }));
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    const target = document.getElementById(button.dataset.copy);
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(target.value);
      clearTimeout(timer); toast.hidden = false; toast.textContent = 'Copied';
      timer = setTimeout(() => { toast.hidden = true; }, 2000);
    } catch (_) {
      lastButton = button; fallback.value = target.value;
      if (dialog.showModal) { dialog.showModal(); fallback.focus(); fallback.select(); }
      else { target.focus(); target.select(); }
    }
  }));
  document.querySelector('#close-dialog').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => lastButton?.focus());
})();
