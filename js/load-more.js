document.addEventListener('DOMContentLoaded', () => {
  const grids = document.querySelectorAll('.grid-3');
  const BATCH_SIZE = 18;
  grids.forEach(grid => {
    const cards = Array.from(grid.querySelectorAll('.post-card'));
    if (cards.length <= BATCH_SIZE) return;
    let visibleCount = BATCH_SIZE;
    cards.forEach((card, index) => {
      if (index >= visibleCount) card.hidden = true;
    });
    const wrapper = document.createElement('div');
    wrapper.className = 'load-more-wrapper';
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'load-more-btn';
    button.textContent = 'Load More';
    wrapper.appendChild(button);
    grid.insertAdjacentElement('afterend', wrapper);
    button.addEventListener('click', () => {
      const nextCount = Math.min(visibleCount + BATCH_SIZE, cards.length);
      for (let i = visibleCount; i < nextCount; i++) {
        cards[i].hidden = false;
      }
      visibleCount = nextCount;
      if (visibleCount >= cards.length) {
        wrapper.remove();
      }
    });
  });
});