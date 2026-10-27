(() => {
  'use strict';
  const gallery = document.getElementById('task-gallery');
  if (!gallery) return;
  const rowsEl = gallery.querySelector('.gallery-rows');
  const filterEl = gallery.querySelector('.gallery-filter');
  const statEl = gallery.querySelector('.gallery-stat');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const GROUPS = ['Adroit', 'Primitive', 'Functional', 'Articulation', 'Bimanual', 'Multi-goal'];
  const ARMS = [['model_driven', 'Agentic', 'var(--green)'], ['cem', 'CEM', 'var(--rust)']];
  const RESETS = '#8db3a3';
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
  const num = v => (Number.isInteger(v) ? v.toLocaleString('en-US') : v.toFixed(1));
  let data = null;
  let selected = 'All';

  function chart(t) {
    const x0 = 74, x1 = 172, h = 11, pitch = 16;
    const rows = [];
    const block = (title, y0, value, scale, label) => {
      rows.push(`<text x="0" y="${y0}" class="gc-head">${title}</text>`);
      ARMS.forEach(([key, name, color], i) => {
        const y = y0 + 7 + i * pitch;
        rows.push(`<text x="0" y="${y + 9.5}" class="gc-arm">${name}</text>`);
        const arm = t[key];
        const w = v => (x1 - x0) * Math.min(v, scale) / scale;
        const v = value(arm);
        if (key === 'model_driven' && label === 'rollouts') {
          rows.push(`<rect x="${x0}" y="${y}" width="${w(arm.search_rollouts).toFixed(1)}" height="${h}" fill="${color}"/>`);
          rows.push(`<rect x="${(x0 + w(arm.search_rollouts)).toFixed(1)}" y="${y}" width="${(w(v) - w(arm.search_rollouts)).toFixed(1)}" height="${h}" fill="${RESETS}"/>`);
        } else {
          rows.push(`<rect x="${x0}" y="${y}" width="${w(v).toFixed(1)}" height="${h}" fill="${color}"/>`);
        }
        const text = label === 'rollouts' ? num(v) : `${+v.toFixed(1)}%`;
        rows.push(`<text x="210" y="${y + 9.5}" class="gc-val" text-anchor="end">${text}</text>`);
      });
    };
    block('HELD-OUT SUCCESS', 10, a => a.heldout_percent, 100, 'heldout');
    const scale = Math.max(1, ...ARMS.map(([k]) => t[k].total_rollouts));
    block('TOTAL ROLLOUTS', 62, a => a.total_rollouts, scale, 'rollouts');
    return `<svg viewBox="0 0 210 102" class="gc-chart" aria-hidden="true">${rows.join('')}</svg>`;
  }

  function card(t) {
    const label = `${t.benchmark} ${t.task}`;
    const failed = t.video_outcome === 'failure';
    // The renders carry a burned-in caption band (task, campaign, seed); the crop classes frame it out.
    const media = t.video
      ? `<video class="${t.benchmark === 'Adroit' ? 'gc-crop-square' : 'gc-crop-wide'}" muted loop playsinline preload="none" aria-label="${esc(label)}: Agentic search held-out ${failed ? 'failure, the policy times out' : 'success'} replay"><source src="${esc(t.video)}" type="video/mp4"></video>`
      : `<div class="gc-empty">${t.model_driven.accepted ? 'No replay recorded' : 'No accepted Agentic policy'}</div>`;
    const summary = `${label}. Held-out success: Agentic search ${t.model_driven.heldout_percent}%, CEM search ${t.cem.heldout_percent}%. ` +
      `Total rollouts: Agentic search ${t.model_driven.total_rollouts}, CEM search ${t.cem.total_rollouts}.`;
    return `<article class="gallery-card${failed ? ' is-failed' : ''}" aria-label="${esc(summary)}"><div class="gc-media">${media}` +
      `<span class="gc-badge">${esc(t.benchmark === 'Adroit' ? 'ADROIT' : t.group.toUpperCase())}</span>` +
      (failed ? '<span class="gc-failed">FAILED · not accepted</span>' : '') + '</div>' +
      `<div class="gc-name">${esc(t.task)}</div>${chart(t)}</article>`;
  }

  const mean = (ts, key) => ts.reduce((s, t) => s + t[key].heldout_percent, 0) / ts.length;
  const successText = value => {
    const label = `${value.toFixed(1)}%`;
    return value >= 90 ? `<strong class="result-number result-number--support">${label}</strong>` : label;
  };

  function render() {
    const groups = selected === 'All' ? GROUPS : [selected];
    rowsEl.innerHTML = groups.map(g => {
      const ts = data.tasks.filter(t => t.group === g);
      return `<div class="gallery-group"><div class="gallery-group-head"><span>${esc(g)}</span>` +
        `<span>${ts.length} task${ts.length > 1 ? 's' : ''} · held-out: Agentic ${successText(mean(ts, 'model_driven'))} · CEM ${successText(mean(ts, 'cem'))}</span></div>` +
        `<div class="gallery-track" tabindex="0" aria-label="${esc(g)} tasks, scroll sideways"><div class="gallery-strip">${ts.map(card).join('')}</div></div></div>`;
    }).join('');
    const ts = data.tasks.filter(t => groups.includes(t.group));
    statEl.innerHTML = `Mean held-out · Agentic ${successText(mean(ts, 'model_driven'))} · CEM ${successText(mean(ts, 'cem'))}`;
    filterEl.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.group === selected)));
    rowsEl.querySelectorAll('.gallery-track').forEach(dragScroll);
    watchVideos();
  }

  function dragScroll(el) {
    let drag = null;
    el.addEventListener('dragstart', e => e.preventDefault());
    el.addEventListener('pointerdown', e => {
      if (e.pointerType !== 'mouse') return;
      drag = { x: e.clientX, s: el.scrollLeft };
      el.setPointerCapture(e.pointerId);
      el.classList.add('dragging');
    });
    el.addEventListener('pointermove', e => { if (drag) el.scrollLeft = drag.s - (e.clientX - drag.x); });
    const up = () => { drag = null; el.classList.remove('dragging'); };
    el.addEventListener('pointerup', up);
    el.addEventListener('pointercancel', up);
  }

  let observer = null;
  function watchVideos() {
    if (observer) observer.disconnect();
    const videos = [...rowsEl.querySelectorAll('video')];
    if (reducedMotion.matches || !('IntersectionObserver' in window)) {
      videos.forEach(v => { v.controls = true; v.preload = 'metadata'; });
      return;
    }
    observer = new IntersectionObserver(entries => entries.forEach(({ target, isIntersecting }) => {
      if (isIntersecting && !document.hidden) target.play().catch(() => {});
      else target.pause();
    }), { threshold: 0.4 });
    videos.forEach(v => observer.observe(v));
  }
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) rowsEl.querySelectorAll('video').forEach(v => v.pause());
    else watchVideos();
  });

  fetch('assets/data/search-results-by-task.json').then(r => r.json()).then(json => {
    data = json;
    filterEl.innerHTML = ['All', ...GROUPS].map(g => `<button type="button" class="tab-button" data-group="${esc(g)}">${esc(g)}</button>`).join('');
    filterEl.addEventListener('click', e => {
      const b = e.target.closest('button');
      if (b) { selected = b.dataset.group; render(); }
    });
    render();
  }).catch(() => {
    rowsEl.innerHTML = '<p class="small-note">The task gallery could not load. All per-task numbers are in the <a href="assets/data/search-results-by-task.json">data file</a>.</p>';
  });
})();
