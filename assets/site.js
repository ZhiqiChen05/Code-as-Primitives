(() => {
  'use strict';
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const progress = document.querySelector('.reading-progress');
  let scheduled = false;
  const updateProgress = () => {
    const height = document.documentElement.scrollHeight - window.innerHeight;
    if (progress) progress.style.transform = `scaleX(${height > 0 ? Math.min(1, Math.max(0, window.scrollY / height)) : 0})`;
    scheduled = false;
  };
  window.addEventListener('scroll', () => {
    if (!scheduled) { scheduled = true; requestAnimationFrame(updateProgress); }
  }, { passive: true });
  window.addEventListener('resize', updateProgress);
  updateProgress();

  document.querySelectorAll('[data-tab-group]').forEach(group => {
    const tabs = [...group.querySelectorAll(':scope > [role="tablist"] > [role="tab"]')];
    function activate(tab, focus = false) {
      tabs.forEach(item => {
        const selected = item === tab;
        item.setAttribute('aria-selected', String(selected));
        item.tabIndex = selected ? 0 : -1;
        const panel = document.getElementById(item.getAttribute('aria-controls'));
        if (!panel) return;
        panel.hidden = !selected;
        if (!selected) panel.querySelectorAll('video').forEach(video => video.pause());
      });
      if (focus) tab.focus();
    }
    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => activate(tab));
      tab.addEventListener('keydown', event => {
        let next;
        if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
        if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
        if (event.key === 'Home') next = 0;
        if (event.key === 'End') next = tabs.length - 1;
        if (next !== undefined) { event.preventDefault(); activate(tabs[next], true); }
      });
    });
    if (tabs.length) activate(tabs.find(tab => tab.getAttribute('aria-selected') === 'true') || tabs[0]);
  });

  const reelVideos = [...document.querySelectorAll('.reel video')];
  const reelButton = document.getElementById('reel-toggle');
  let playReel = !reducedMotion.matches;
  const visibleReels = new Set();
  const syncReel = () => {
    reelVideos.forEach(video => {
      if (playReel && visibleReels.has(video) && !document.hidden) video.play().catch(() => {});
      else video.pause();
    });
    if (reelButton) {
      reelButton.textContent = playReel ? 'Pause previews Ⅱ' : 'Play previews ▷';
      reelButton.setAttribute('aria-pressed', String(playReel));
    }
  };
  if ('IntersectionObserver' in window) {
    const mediaObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) visibleReels.add(entry.target);
        else visibleReels.delete(entry.target);
      });
      syncReel();
    }, { threshold: 0.15 });
    reelVideos.forEach(video => mediaObserver.observe(video));
    const sections = [...document.querySelectorAll('.article-section[id]')];
    const links = [...document.querySelectorAll('.contents a[href^="#"]')];
    const sectionObserver = new IntersectionObserver(entries => {
      const active = entries.filter(entry => entry.isIntersecting).sort((a,b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (!active) return;
      links.forEach(link => {
        if (link.hash === `#${active.target.id}`) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }, { rootMargin: '-8% 0px -65% 0px', threshold: 0 });
    sections.forEach(section => sectionObserver.observe(section));
  }
  if (reelButton) reelButton.addEventListener('click', () => { playReel = !playReel; syncReel(); });
  reducedMotion.addEventListener('change', event => { if (event.matches) { playReel = false; syncReel(); } });
  document.addEventListener('visibilitychange', syncReel);
  syncReel();

  document.querySelectorAll('[data-copy-target]').forEach(button => {
    button.addEventListener('click', async () => {
      const target = document.getElementById(button.dataset.copyTarget);
      if (!target) return;
      try {
        await navigator.clipboard.writeText(target.textContent);
        button.textContent = 'Copied';
      } catch (_) {
        const range = document.createRange();
        range.selectNodeContents(target);
        const selection = window.getSelection();
        selection.removeAllRanges(); selection.addRange(range);
        button.textContent = 'Select + copy';
      }
      window.setTimeout(() => { button.textContent = 'Copy'; }, 2200);
    });
  });
})();
