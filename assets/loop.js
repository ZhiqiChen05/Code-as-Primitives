/* Figure 3: scroll-driven learning loop with accessible, synchronized Pen artifacts.
   The diagram is decorative; videos, code and the recorded evidence are ordinary HTML.
   Smaller viewports use the same sequence with explicit step controls. */
(() => {
  "use strict";
  const root = document.querySelector("[data-loop]");
  if (!root) return;
  const R = name => root.querySelector(`[data-ref="${name}"]`);
  const clamp = v => Math.max(0, Math.min(1, v));
  const smooth = v => { v = clamp(v); return v * v * (3 - 2 * v); };
  const css = getComputedStyle(document.documentElement);
  const C = {
    green: css.getPropertyValue("--green").trim() || "#276451",
    rust: css.getPropertyValue("--rust").trim() || "#be5d39",
    ink: css.getPropertyValue("--ink").trim() || "#242620",
    soft: css.getPropertyValue("--green-soft").trim() || "#e4eadf",
  };
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");
  const compact = matchMedia("(max-width: 1240px), (max-height: 739px)");
  const outer = [0, 1, 2, 3].map(i => R(`ok${i}`));
  const inner = [0, 1, 2, 3].map(i => R(`ik${i}`));
  const outerArrows = [0, 1, 2, 3].map(i => R(`oa${i}`));
  const innerArrows = [0, 1, 2, 3].map(i => R(`ia${i}`));
  const steps = [...root.querySelectorAll(".lp-step")];
  const panels = [...root.querySelectorAll("[data-pen-evidence]")];
  const evidence = R("evidence"), scene = R("scene"), article = document.getElementById("article");
  const back = root.querySelector('[data-loop-action="back"]');
  const next = root.querySelector('[data-loop-action="next"]');
  let active = 0, rendered = -1, frame = null, pulseFrame = null, pz = 0;
  let inView = false, pulseTime = 0, lastPulse = 0, wasCompact = compact.matches;

  function keyState(el, on, mark = false) {
    el.querySelectorAll("[data-br]").forEach(b => { b.style.borderColor = on ? C.green : (mark ? "#8fb5a5" : "#b9b8ac"); });
    el.querySelector("[data-t]").style.color = on || mark ? C.green : "#9a9a90";
    el.style.background = on ? C.soft : "transparent";
  }
  function arrowState(el, on, warn = false) {
    el.setAttribute("stroke", on ? (warn ? C.rust : C.ink) : (warn ? "#e3b7a5" : "#c4c3b8"));
    el.setAttribute("stroke-width", on ? "1.8" : "1.5");
  }
  function pauseVideos() { evidence.querySelectorAll("video").forEach(video => video.pause()); }
  function renderStep() {
    if (rendered === active) return;
    pauseVideos();
    const focusedPanel = panels.find(panel => panel.contains(document.activeElement));
    if (focusedPanel && Number(focusedPanel.dataset.penEvidence) !== active - 3) next.focus({preventScroll:true});
    evidence.hidden = active < 3;
    panels.forEach((panel, i) => { panel.hidden = i !== active - 3; });
    steps.forEach((step, i) => step.classList.toggle("is-active", i === active));
    R("counter").textContent = `${String(active + 1).padStart(2, "0")} / ${String(steps.length).padStart(2, "0")}`;
    R("step-name").textContent = steps[active].dataset.title;
    back.setAttribute("aria-disabled", String(active === 0));
    next.setAttribute("aria-disabled", String(active === steps.length - 1));
    R("compact-note").innerHTML = active < 3 ? steps[active].innerHTML : "";
    R("compact-note").hidden = active >= 3;
    R("mini-search").hidden = active !== 2;
    root.dataset.step = String(active);
    scene.scrollTop = 0;
    rendered = active;
  }

  function update() {
    frame = null;
    const isCompact = compact.matches;
    root.classList.toggle("lp-compact", isCompact);
    const scroll = R("scroll"), stick = R("stick"), wrap = R("fit");
    const vw = document.documentElement.clientWidth, vh = innerHeight;
    const left = article ? article.getBoundingClientRect().left : 0;
    scroll.style.marginLeft = isCompact ? "" : `${-left}px`;
    scroll.style.width = isCompact ? "" : `${vw}px`;
    const padR = Math.max(20, (vw - 1500) / 2);
    stick.style.paddingRight = isCompact ? "" : `${padR}px`;
    const width = Math.min(1040, vw - padR - 450);
    scene.style.width = isCompact ? "" : `${width}px`;
    const fit = Math.min(scene.clientWidth / 1040, (vh - 80) / 620, 1);
    wrap.style.width = isCompact ? "" : `${1040 * fit}px`;
    R("stage").style.transform = `scale(${fit})`;
    R("steps").style.marginLeft = isCompact ? "" : `${Math.max(14, (vw - 1500) / 2 + 20)}px`;

    const rects = steps.map(step => step.getBoundingClientRect());
    const bounds = scroll.getBoundingClientRect();
    inView = bounds.top < vh && bounds.bottom > 0;
    if (!isCompact && isCompact === wasCompact) {
      let candidate = 0;
      rects.forEach((rect, i) => { if (rect.top < vh * .5) candidate = i; });
      // Do not replace a video or an expanded artifact while a reader is using its controls.
      if (!evidence.contains(document.activeElement)) active = candidate;
    }
    if (!isCompact && wasCompact) {
      // Keep the selected step when resizing from the manual layout into the scroll layout.
      if (inView) scrollTo({top: scrollY + rects[active].top + rects[active].height / 2 - vh / 2, behavior:"instant"});
    }
    wasCompact = isCompact;
    renderStep();
    if (!inView || document.hidden) pauseVideos();
    document.body.classList.toggle("lp-in-view", !isCompact && bounds.top < vh * .5 && bounds.bottom > vh * .5);

    const progress = rects.map(rect => clamp((vh - rect.top) / (vh * .9 + rect.height)));
    let stageOn = active === 0 ? Math.floor(progress[0] * 11.999) % 4 : active <= 2 ? 1 : [0, 0, 1, 2, 3][active - 3];
    if (isCompact && active === 0) stageOn = 0;
    outer.forEach((el, i) => keyState(el, i === stageOn));
    root.querySelectorAll("[data-mini]").forEach(el => el.classList.toggle("is-active", Number(el.dataset.mini) === stageOn));
    R("mini-held").classList.toggle("is-active", active === 7);
    outerArrows.forEach((el, i) => arrowState(el, active === 0 && i === (stageOn + 3) % 4));
    R("edges").style.opacity = String(active === 0 ? .35 : 1);
    const cells = [...R("cells").children];
    const count = active === 0 ? 3 : active === 1 ? 3 + Math.round(progress[1] * 11) : cells.length;
    cells.forEach((cell, i) => {
      cell.style.background = i < count ? (i === count - 1 ? C.green : C.ink) : "#efeee6";
      cell.style.borderColor = i < count ? C.ink : "#deddd2";
    });

    const zin = smooth((vh * .85 - rects[2].top) / (vh * .5));
    const zout = smooth((vh * .85 - rects[3].top) / (vh * .5));
    pz = isCompact || active >= 3 ? 0 : reduced.matches ? (active === 2 ? 1 : 0) : zin * (1 - zout);
    const cam = R("cam");
    cam.style.transformOrigin = "397px 106px";
    cam.style.transform = `scale(${1 + pz * 1.9})`;
    cam.style.opacity = String(1 - smooth((pz - .18) / .34));
    const pin = R("pin"), opacity = smooth((pz - .52) / .33);
    pin.style.opacity = String(opacity);
    pin.style.visibility = opacity > .01 ? "visible" : "hidden";
    pin.style.transform = `scale(${.55 + .45 * pz})`;
    const lerp = (a, b) => `${a + (b - a) * pz}px`;
    const zoom = R("zb"), title = R("zt"), zooming = pz > .02;
    zoom.style.left = lerp(282, 50); zoom.style.top = "44px";
    zoom.style.width = lerp(230, 940); zoom.style.height = lerp(124, 96 + (pin.offsetHeight || 360));
    zoom.style.opacity = zooming ? "1" : "0";
    outer[1].querySelectorAll("[data-br], [data-t]").forEach(el => { el.style.opacity = zooming ? "0" : "1"; });
    title.style.left = lerp(357, 520); title.style.top = "64px";
    title.style.fontSize = `${26 + 3 * pz}px`; title.style.opacity = zooming ? "1" : "0";
    wrap.style.height = `${(active === 2 || pz > .03 ? 620 : 340) * fit}px`;
    R("sup").style.opacity = active === 6 ? "1" : active >= 3 ? ".22" : "0";
    arrowState(R("supPath"), active === 6, true);
    R("held").style.opacity = active === 7 ? "1" : ".35";
    R("held").style.borderColor = active === 7 ? C.green : C.ink;
    R("held").style.background = active === 7 ? C.soft : "";
    scene.style.marginTop = isCompact ? "" : `${Math.max(16, (vh - Math.min(scene.scrollHeight, vh - 32)) / 2)}px`;
    syncPulse();
  }

  const kick = () => { if (frame === null) frame = requestAnimationFrame(update); };
  const sequence = [[0, -1], [1, 0], [2, 2], [0, 1], [1, 0], [2, 2], [3, 3]];
  function pulse(now) {
    pulseFrame = null;
    pulseTime += Math.min(.05, (now - lastPulse) / 1000); lastPulse = now;
    const [key, arrow] = sequence[Math.floor(pulseTime / .85) % sequence.length];
    inner.forEach((el, i) => keyState(el, i === key, i === 3));
    innerArrows.forEach((el, i) => arrowState(el, i === arrow, i === 1));
    syncPulse();
  }
  function syncPulse() {
    if (pz > .5 && inView && !reduced.matches && !document.hidden) {
      if (pulseFrame === null) { lastPulse = performance.now(); pulseFrame = requestAnimationFrame(pulse); }
    } else {
      if (pulseFrame !== null) cancelAnimationFrame(pulseFrame);
      pulseFrame = null; pulseTime = 0;
      inner.forEach((el, i) => keyState(el, false, i === 3));
      innerArrows.forEach((el, i) => arrowState(el, false, i === 1));
    }
  }
  function goTo(index) {
    active = Math.max(0, Math.min(steps.length - 1, index));
    renderStep();
    if (compact.matches) {
      // Keep navigation visible after stepping from a taller artifact, without jumping if already visible.
      const nav = root.querySelector(".lp-navigation").getBoundingClientRect();
      if (nav.top < 0 || nav.bottom > innerHeight) root.scrollIntoView({block:"start", behavior:"instant"});
    } else {
      const rect = steps[active].getBoundingClientRect();
      scrollTo({top:scrollY + rect.top + rect.height / 2 - innerHeight / 2, behavior:"instant"});
    }
    kick();
  }
  root.querySelector(".lp-navigation").addEventListener("click", event => {
    const button = event.target.closest("[data-loop-action]");
    if (!button || button.getAttribute("aria-disabled") === "true") return;
    goTo(active + (button.dataset.loopAction === "next" ? 1 : -1));
  });
  root.querySelector(".lp-navigation").addEventListener("keydown", event => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    const target = {ArrowLeft:active - 1, ArrowRight:active + 1, Home:0, End:steps.length - 1}[event.key];
    if (target !== undefined) { event.preventDefault(); goTo(target); }
  });
  evidence.addEventListener("toggle", kick, true);
  evidence.addEventListener("focusout", kick);
  document.addEventListener("visibilitychange", kick);
  window.addEventListener("scroll", kick, {passive:true});
  window.addEventListener("resize", kick);
  reduced.addEventListener("change", kick);
  compact.addEventListener("change", kick);
  if ("ResizeObserver" in window) new ResizeObserver(kick).observe(evidence);
  const followAnchor = () => { if (location.hash === "#pen-walkthrough") goTo(3); };
  window.addEventListener("hashchange", followAnchor);
  document.querySelectorAll('a[href="#pen-walkthrough"]').forEach(link => link.addEventListener("click", event => {
    event.preventDefault(); history.pushState(null, "", "#pen-walkthrough"); goTo(3);
    if (compact.matches) root.scrollIntoView({block:"start", behavior:"instant"});
  }));
  let printDetails = [];
  window.addEventListener("beforeprint", () => {
    printDetails = [...evidence.querySelectorAll("details:not([open])")];
    printDetails.forEach(details => { details.open = true; });
  });
  window.addEventListener("afterprint", () => {
    printDetails.forEach(details => { details.open = false; });
    printDetails = []; kick();
  });
  root.classList.add("lp-ready");
  update();
  if (location.hash === "#pen-walkthrough") requestAnimationFrame(followAnchor);
  if (document.fonts?.ready) document.fonts.ready.then(kick);
})();
