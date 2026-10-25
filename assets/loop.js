/* Figure 2: scroll-driven control loop, a port of the Schema Harness Figure 3 mechanics.
   Scrolling the step cards drives the stage: outer loop → rollout ledger → zoom into one search
   → recorded Pen trace → failed submission → frozen held-out test. No results are simulated;
   the trace lines restate the recorded run documented in docs/pen-case-study.json. */
(() => {
  "use strict";
  const root = document.querySelector("[data-loop]");
  if (!root) return;
  const R = (name) => root.querySelector(`[data-ref="${name}"]`);
  const cl = (v) => Math.max(0, Math.min(1, v));
  const ss = (v) => { v = cl(v); return v * v * (3 - 2 * v); };
  const css = getComputedStyle(document.documentElement);
  const C = {
    green: css.getPropertyValue("--green").trim() || "#276451",
    rust: css.getPropertyValue("--rust").trim() || "#be5d39",
    ink: css.getPropertyValue("--ink").trim() || "#242620",
    soft: css.getPropertyValue("--green-soft").trim() || "#e4eadf",
  };
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");

  function keyState(el, on, mark) {
    if (!el) return;
    el.querySelectorAll("[data-br]").forEach((b) => { b.style.borderColor = on ? C.green : (mark ? "#8fb5a5" : "#b9b8ac"); });
    const t = el.querySelector("[data-t]");
    if (t) t.style.color = (on || mark) ? C.green : "#9a9a90";
    el.style.background = on ? C.soft : "transparent";
  }
  function arrowState(el, on, warn) {
    if (!el) return;
    el.setAttribute("stroke", on ? (warn ? C.rust : C.ink) : (warn ? "#e3b7a5" : "#c4c3b8"));
    el.setAttribute("stroke-width", on ? "1.8" : "1.5");
  }

  const outer = [0, 1, 2, 3].map((i) => R(`ok${i}`));
  const inner = [0, 1, 2, 3].map((i) => R(`ik${i}`));
  const outerArrows = [0, 1, 2, 3].map((i) => R(`oa${i}`));
  const innerArrows = [0, 1, 2, 3].map((i) => R(`ia${i}`));
  const steps = [...root.querySelectorAll(".lp-step")];
  const trace = [0, 1, 2, 3, 4].map((i) => R(`tr${i}`));
  const article = document.getElementById("article");
  let pz = 0, raf = null;

  function traceIdx(prog, active) {
    if (active === 3) return Math.min(2, Math.floor(prog[3] * 3.6));
    if (active === 4) return 3;
    return 4;
  }

  function update() {
    raf = null;
    const scroll = R("scroll"), stick = R("stick"), wrap = R("fit"), stage = R("stage");
    const vw = document.documentElement.clientWidth, vh = window.innerHeight;
    // Break out of the article column to the full viewport width, as the original figure does.
    const left = article ? article.getBoundingClientRect().left : 0;
    scroll.style.marginLeft = `${-left}px`;
    scroll.style.width = `${vw}px`;
    const w = stick.clientWidth;
    const wide = w > 1240;
    stick.style.justifyContent = wide ? "flex-end" : "center";
    const padR = wide ? Math.max(20, (w - 1500) / 2) : 12;
    stick.style.paddingRight = `${padR}px`;
    const avail = wide ? w - padR - 450 : w - 24;
    const fit = Math.min(avail / 1040, (vh - 80) / 620, 1);
    wrap.style.width = `${1040 * fit}px`;
    stage.style.transform = `scale(${fit})`;
    R("steps").style.marginLeft = wide ? `${Math.max(14, (vw - 1500) / 2 + 20)}px` : "";

    const rs = steps.map((s) => s.getBoundingClientRect());
    const yc = vh * 0.5;
    let active = 0;
    rs.forEach((r, i) => { if (r.top < yc) active = i; });
    const prog = rs.map((r) => cl((vh - r.top) / (vh * 0.9 + r.height)));
    R("edges").style.opacity = String(active === 0 ? 0 : (active === 1 ? ss(cl(prog[1] * 1.6)) : 1));
    const ti = active >= 3 ? traceIdx(prog, active) : -1;
    let stageOn;
    if (active === 0) stageOn = Math.floor(prog[0] * 11.999) % 4;
    else if (active <= 2) stageOn = 1;
    else stageOn = [0, 0, 1, 2, 3][ti];
    outer.forEach((el, i) => keyState(el, i === stageOn, false));
    outerArrows.forEach((el, i) => arrowState(el, active === 0 && i === (stageOn + 3) % 4, false));

    const cells = R("cells").children;
    const n = active === 0 ? 3 : (active === 1 ? 3 + Math.round(prog[1] * 11) : cells.length);
    [...cells].forEach((c, i) => {
      const on = i < n, last = i === n - 1;
      c.style.background = on ? (last ? C.green : C.ink) : "#efeee6";
      c.style.borderColor = on ? (last ? C.green : C.ink) : "#deddd2";
    });

    const zin = ss(cl((vh * 0.85 - rs[2].top) / (vh * 0.5)));
    const zout = ss(cl((vh * 0.85 - rs[3].top) / (vh * 0.5)));
    pz = zin * (1 - zout);
    const cam = R("cam");
    cam.style.transformOrigin = "397px 106px";
    cam.style.transform = `scale(${1 + pz * 1.9})`;
    cam.style.opacity = String(1 - ss(cl((pz - 0.18) / 0.34)));
    const pin = R("pin");
    const po = ss(cl((pz - 0.52) / 0.33));
    pin.style.opacity = String(po);
    pin.style.visibility = po > 0.01 ? "visible" : "hidden";
    pin.style.transform = `scale(${0.55 + 0.45 * pz})`;
    const lp = (a, b) => `${(a + (b - a) * pz).toFixed(1)}px`;
    const zb = R("zb"), zt = R("zt"), on = pz > 0.02;
    zb.style.left = lp(282, 50); zb.style.top = "44px";
    zb.style.width = lp(230, 940); zb.style.height = lp(124, 96 + (pin.offsetHeight || 360));
    zb.style.opacity = on ? "1" : "0";
    outer[1].querySelectorAll("[data-br], [data-t]").forEach((el) => { el.style.opacity = on ? "0" : "1"; });
    zt.style.left = lp(357, 520); zt.style.top = "64px";
    zt.style.fontSize = `${(26 + 3 * pz).toFixed(1)}px`;
    zt.style.opacity = on ? "1" : "0";

    const wrapH = ((active >= 2 || pz > 0.03) ? 620 : 340) * fit;
    wrap.style.height = `${wrapH}px`;
    const rr = scroll.getBoundingClientRect();
    const cm = Math.max(12, (vh - wrapH) / 2);
    const en = ss(cl(1 - rr.top / (vh * 0.6)));
    const ex = ss(cl((rr.bottom - vh) / (vh * 0.5)));
    const endMt = Math.max(12, vh - wrapH - 16);
    let mt = 12 + (cm - 12) * en;
    mt = mt * ex + endMt * (1 - ex) * en;
    wrap.style.marginTop = `${mt.toFixed(1)}px`;
    document.body.classList.toggle("lp-in-view", rr.top < vh * 0.5 && rr.bottom > vh * 0.5);

    const showTrace = active >= 3;
    const ptr = R("ptr");
    ptr.style.opacity = showTrace ? "1" : "0";
    ptr.style.transform = showTrace ? "translateY(0)" : "translateY(14px)";
    R("sup").style.opacity = active === 4 ? "1" : (active >= 3 ? "0.22" : "0");
    arrowState(R("supPath"), active === 4, true);
    const held = R("held");
    held.style.opacity = active === 5 ? "1" : "0.35";
    held.style.borderColor = active === 5 ? C.green : C.ink;
    held.style.background = active === 5 ? C.soft : "";
    R("imgEnd").style.opacity = ti === 4 ? "1" : "0";
    trace.forEach((el, i) => { el.style.color = i === ti ? C.ink : (i < ti ? "#8a8b82" : "#cfcec4"); });
  }

  const kick = () => { if (!raf) raf = requestAnimationFrame(update); };
  window.addEventListener("scroll", kick, { passive: true });
  window.addEventListener("resize", kick);

  // While zoomed in, pulse the inner loop: propose → evaluate → analyze → (refine → evaluate →) commit.
  let t = 0, last = performance.now();
  const seq = [[0, -1], [1, 0], [2, 2], [0, 1], [1, 0], [2, 2], [3, 3]];
  function pulse(now) {
    const dt = Math.min(0.05, (now - last) / 1000); last = now;
    if (pz > 0.5 && !reduced.matches) {
      t += dt;
      const [k, a] = seq[Math.floor(t / 0.85) % seq.length];
      inner.forEach((el, i) => keyState(el, i === k, i === 3));
      innerArrows.forEach((el, i) => arrowState(el, i === a, i === 1));
    } else if (t) {
      t = 0;
      inner.forEach((el, i) => keyState(el, false, i === 3));
      innerArrows.forEach((el, i) => arrowState(el, false, i === 1));
    }
    requestAnimationFrame(pulse);
  }

  root.classList.add("lp-ready");
  inner.forEach((el, i) => keyState(el, false, i === 3));
  kick();
  requestAnimationFrame(pulse);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(kick);
})();
