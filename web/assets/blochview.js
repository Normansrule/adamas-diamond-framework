// A light, accessible Bloch-sphere view (SVG, no WebGL) for the scenes in sim/blochscenes.js (v0.53.0).
// Plays once when scrolled into view; with prefers-reduced-motion it never animates and shows its resting frame. A slider
// steps through every frame by hand, and a text line gives the arrow's numbers (announced when playback stops or the slider moves).
import { SCENES, TURN, describe } from './sim/blochscenes.js';
import * as B from './sim/bloch.js';

const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const PHI = -0.6, EPS = 0.32;                                    // view azimuth and elevation (radians)
function proj([x, y, z]) {                                       // orthographic: screen right, screen up, depth toward viewer
  const c = Math.cos(PHI), s = Math.sin(PHI), ce = Math.cos(EPS), se = Math.sin(EPS), d = x * c + y * s;
  return [y * c - x * s, z * ce - d * se, d * ce + z * se];
}
const still = () => typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const NV_POLES = ['|0⟩ mₛ = 0', '|1⟩ mₛ = −1'];
let uid = 0;

function sphereSVG(cx, cy, R, name, poles) {
  const pts = (f, n = 72) => [...Array(n + 1)].map((_, k) => f(2 * Math.PI * k / n));
  const path = (ps, front) => { let d = '', on = false;        // the front or back half of a great circle, as one or more runs
    for (const p of ps) { const q = proj(p), ok = front ? q[2] >= 0 : q[2] < 0;
      if (ok) d += `${on ? 'L' : 'M'}${(cx + R * q[0]).toFixed(1)} ${(cy - R * q[1]).toFixed(1)} `; on = ok; }
    return d.trim(); };
  const eq = pts(u => [Math.cos(u), Math.sin(u), 0]), mer = pts(u => [Math.cos(u), 0, Math.sin(u)]);
  let s = `<circle cx="${cx}" cy="${cy}" r="${R}" class="bs-ball"/>`;
  for (const ps of [eq, mer]) s += `<path d="${path(ps, false)}" class="bs-back"/><path d="${path(ps, true)}" class="bs-ring"/>`;
  const ax = (v, t, dx = 0, dy = 0) => { const q = proj(v.map(x => x * 1.18)); return `<line x1="${cx}" y1="${cy}" x2="${(cx + R * q[0]).toFixed(1)}" y2="${(cy - R * q[1]).toFixed(1)}" class="bs-axis"/><text x="${(cx + R * q[0] + dx).toFixed(1)}" y="${(cy - R * q[1] + dy).toFixed(1)}" class="bs-lab">${esc(t)}</text>`; };
  s += ax([1, 0, 0], 'x', -10, 12) + ax([0, 1, 0], 'y', 6, 4) + ax([0, 0, 1], poles[0], -34, -6) + ax([0, 0, -1], poles[1], -38, 16);
  if (name) s += `<text x="${cx}" y="${cy + R + 58}" class="bs-lab" text-anchor="middle">${esc(name)}</text>`;
  return s;
}

export function mountBloch(host, sceneName, data, note = '') {
  let sc;
  try { sc = SCENES[sceneName](data || {}); } catch (e) {        // e.g. a stale site data file without the bloch block
    host.innerHTML = '<p class="note">This Bloch-sphere scene needs data the page did not load; rebuild the site.</p>'; return null;
  }
  const id = `bs${++uid}`, pair = !!sc.frames[0].pair, W = pair ? 460 : 260, H = pair ? 300 : 270, R = 96;
  const centers = pair ? [[115, 128], [345, 128]] : [[130, 128]], poles = sc.poles || NV_POLES;
  const rest = f => Math.min(f.length - 1, sc.rest ?? f.length - 1);
  host.innerHTML = `<figure class="bloch" aria-labelledby="${id}t">
    <figcaption id="${id}t"><b>${esc(sc.title)}</b> <span class="st simulated">${esc(sc.status)}</span></figcaption>
    <svg viewBox="0 0 ${W} ${H}" style="max-width:${pair ? 460 : 340}px" role="img" aria-labelledby="${id}t ${id}r">${centers.map((c, i) => sphereSVG(c[0], c[1], R, pair ? `qubit ${'AB'[i]} on its own` : '', poles)).join('')}<g data-dyn></g></svg>
    <p class="bs-step" data-step></p><p class="bs-read" id="${id}r" data-read></p><p class="sr-only" aria-live="polite" data-live></p>
    <div class="bs-ctl">${sc.interactive === 'gates' ? Object.keys(TURN).map(g => `<button type="button" class="btn small" data-gate="${g}" aria-label="${g} gate: ${esc(TURN[g])}">${g}</button>`).join('') + '<button type="button" class="btn small" data-gate="reset" aria-label="Reset to state 0">|0⟩</button>'
      : `<button type="button" class="btn small" data-play>Play</button>`}
      <label class="bs-scrub">${sc.interactive === 'theta' ? 'θ' : 'Step'} <input type="range" min="0" max="${sc.frames.length - 1}" value="${rest(sc.frames)}" data-scrub aria-label="${sc.interactive === 'theta' ? 'Entangling angle theta' : 'Step through the scene'}"></label></div>
    <p class="note">${esc(sc.caption)}${note ? ' ' + esc(note) : ''}</p></figure>`;
  const $ = s => host.querySelector(s), dyn = $('[data-dyn]'), scrub = $('[data-scrub]');
  let frames = sc.frames, i = rest(frames), timer = 0, playing = false;

  function arrow(cx, cy, r, cls) { const q = proj(r), x = cx + R * q[0], y = cy - R * q[1], L = Math.hypot(x - cx, y - cy);
    const head = L > 6 ? (() => { const ux = (x - cx) / L, uy = (y - cy) / L; return `<path d="M${x.toFixed(1)} ${y.toFixed(1)} L${(x - 9 * ux - 4.5 * uy).toFixed(1)} ${(y - 9 * uy + 4.5 * ux).toFixed(1)} L${(x - 9 * ux + 4.5 * uy).toFixed(1)} ${(y - 9 * uy - 4.5 * ux).toFixed(1)}z" class="${cls}h"/>`; })() : '';
    return `<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" class="${cls}"/>${head}<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${L > 6 ? 2.6 : 4}" class="${cls}h"/>`; }
  function draw(announce) {
    const f = frames[i]; let s = '', from = 0;
    for (let k = i; k >= 0; k--) if (frames[k].newTrail) { from = k; break; }
    centers.forEach(([cx, cy], k) => {
      const tips = frames.slice(from, i + 1).map(fr => proj(pair ? fr.pair[k] : fr.r)).map(q => [(cx + R * q[0]).toFixed(1), (cy - R * q[1]).toFixed(1)]);
      if (sc.trailOnly) s += tips.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="2" class="bs-dot"/>`).join('');    // separate runs, not a path in time
      else if (tips.length > 1) s += `<polyline points="${tips.map(t => t.join(',')).join(' ')}" class="bs-trail"/>`;
      for (const v of f.spins || []) s += arrow(cx, cy, v, 'bs-spin');
      for (const o of f.outcomes || []) s += arrow(cx, cy, o, 'bs-ghost');
      s += arrow(cx, cy, pair ? f.pair[k] : f.r, 'bs-arrow');
    });
    dyn.innerHTML = s; $('[data-step]').textContent = f.label; scrub.value = String(i); scrub.setAttribute('aria-valuetext', f.label);
    const txt = (pair ? 'Each qubit: ' : 'Arrow: ') + describe(f.r, sc.poles ? 'P(|1⟩)' : undefined) + (f.spins ? ` (mean of ${f.spins.length} spins)` : '');
    $('[data-read]').textContent = txt;
    if (announce) $('[data-live]').textContent = `${f.label}. ${txt}`;
  }
  function stop(announce) { const was = playing; playing = false; clearTimeout(timer); const b = $('[data-play]'); if (b) b.textContent = 'Play'; if (was && announce) draw(true); }
  function play(from = 0) {
    if (still()) { i = frames.length - 1; draw(true); return; }
    stop(false); playing = true; i = from; const b = $('[data-play]'); if (b) b.textContent = 'Pause';
    const tick = () => { if (!host.isConnected || !playing) return; draw(false); if (i < frames.length - 1) { i++; timer = setTimeout(tick, 33); } else stop(true); };
    tick();
  }
  scrub.oninput = () => { stop(false); i = +scrub.value; draw(true); };
  const pb = $('[data-play]'); if (pb) pb.onclick = () => playing ? stop(true) : play(i >= frames.length - 1 ? 0 : i);
  host.querySelectorAll('[data-gate]').forEach(b => b.onclick = () => {
    stop(false); const g = b.dataset.gate, r0 = frames.at(-1).r;           // the completed state, never a half-turned arrow
    if (g === 'reset') frames = [{ r: [0, 0, 1], label: 'reset to |0⟩' }];
    else frames = [{ r: r0, label: `before ${g}` }, ...[...Array(24)].map((_, k) => ({ r: B.applyGate(r0, g, (k + 1) / 24), label: `${g} gate: a turn of ${TURN[g]}` }))];
    scrub.max = String(frames.length - 1); play(0);
  });
  draw(false);
  if (!still() && sc.interactive !== 'theta' && typeof IntersectionObserver === 'function') {
    const io = new IntersectionObserver(es => { if (!host.isConnected) { io.disconnect(); return; }
      if (es.some(e => e.isIntersecting)) { io.disconnect(); play(0); } }, { threshold: 0.4 });
    io.observe(host);
  }
  return { play, stop };
}
