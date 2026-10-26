// Scene renderers for the Equations in Action page. Each scene draws an animated picture of the mechanism (frame), the
// curve the experiment should measure (plot), and the equation with the slider values plugged in (plug). Physics comes
// from ./sim/action.js, which is tested against the Python package. Colors follow the site palette.
import * as A from './sim/action.js';
import { colormap } from './site.js';

export const C = { teal: '#2de2e6', cyan: '#6ff3ff', violet: '#9d7bff', pink: '#ff5d8f', gold: '#ffc46b', green: '#48e5a3', red: '#ff5d6c', ink: '#e8f1f8', mute: '#8ea3b5', line: 'rgba(148,190,220,.16)', orange: '#ff9a3c' };
const TAU = Math.PI * 2;

// ---------------------------------------------------------------- formatting and drawing helpers
const SUP = { '-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' };
export function num(x, s = 3) {
  if (!isFinite(x)) return '∞';
  if (x === 0) return '0';
  const a = Math.abs(x);
  if (a >= 1e5 || a < 1e-3) { const e = Math.floor(Math.log10(a)), m = x / 10 ** e; return `${(+m.toPrecision(s)).toString()} × 10${String(e).split('').map(c => SUP[c]).join('')}`; }
  const v = +x.toPrecision(s); return Math.abs(v) >= 1000 ? Math.round(v).toLocaleString('en-US') : String(v);
}
const b = (s, cls = '') => `<b class="pv ${cls}">${s}</b>`;   // plugged value
function txt(g, s, x, y, { c = C.mute, size = 12, align = 'left', weight = 400, base = 'alphabetic', font = 'Inter' } = {}) {
  g.fillStyle = c; g.font = `${weight} ${size}px ${font}, system-ui, sans-serif`; g.textAlign = align; g.textBaseline = base; g.fillText(s, x, y);
}
function glow(g, x, y, r, color, a = 1) {
  const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, color); gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.globalAlpha = a; g.fillStyle = gr; g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill(); g.globalAlpha = 1;
}
function dot(g, x, y, r, c) { g.fillStyle = c; g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill(); }
function line(g, pts, c, w = 2, dash = null) { if (pts.length < 2) return; g.strokeStyle = c; g.lineWidth = w; g.setLineDash(dash || []); g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.stroke(); g.setLineDash([]); }
function arrow(g, x0, y0, x1, y1, c, w = 2, head = 9) {
  line(g, [[x0, y0], [x1, y1]], c, w); const a = Math.atan2(y1 - y0, x1 - x0);
  g.fillStyle = c; g.beginPath(); g.moveTo(x1, y1); g.lineTo(x1 - head * Math.cos(a - .4), y1 - head * Math.sin(a - .4)); g.lineTo(x1 - head * Math.cos(a + .4), y1 - head * Math.sin(a + .4)); g.closePath(); g.fill();
}
function wavy(g, x0, y0, x1, y1, c, phase = 0, amp = 4, k = 0.35, w = 1.8) {
  const L = Math.hypot(x1 - x0, y1 - y0), ux = (x1 - x0) / L, uy = (y1 - y0) / L, pts = [];
  for (let s = 0; s <= L; s += 2) { const o = amp * Math.sin(k * s - phase); pts.push([x0 + ux * s - uy * o, y0 + uy * s + ux * o]); }
  line(g, pts, c, w);
}
function roundRect(g, x, y, w, h, r, fill, stroke) {
  g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath();
  if (fill) { g.fillStyle = fill; g.fill(); } if (stroke) { g.strokeStyle = stroke; g.lineWidth = 1.2; g.stroke(); }
}
function gem(g, cx, cy, s, glowColor, glowAmt) {        // a cut diamond with a fluorescence halo
  if (glowAmt > 0) glow(g, cx, cy, s * (1.6 + glowAmt), glowColor, 0.25 + 0.6 * glowAmt);
  const P = [[-1, -.35], [-.55, -.8], [.55, -.8], [1, -.35], [0, 1]].map(([x, y]) => [cx + x * s, cy + y * s]);
  g.fillStyle = 'rgba(111,243,255,.18)'; g.strokeStyle = C.cyan; g.lineWidth = 1.4; g.beginPath(); P.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); g.fill(); g.stroke();
  line(g, [P[0], P[3]], 'rgba(111,243,255,.6)', 1); line(g, [[cx - .3 * s, cy - .35 * s], P[4], [cx + .3 * s, cy - .35 * s]], 'rgba(111,243,255,.45)', 1);
  line(g, [P[1], [cx - .3 * s, cy - .35 * s], [cx, cy - .8 * s], [cx + .3 * s, cy - .35 * s], P[2]], 'rgba(111,243,255,.45)', 1);
}
const lerp = (a, b, t) => a + (b - a) * t;
const tri = (t, period) => { const x = (t / period) % 1; return x < .5 ? 2 * x : 2 - 2 * x; };

// a small plotting kit: axes with linear or log scales, grid, ticks, labels
function nice(lo, hi, n = 5) { const raw = (hi - lo) / n, p = 10 ** Math.floor(Math.log10(raw)), m = raw / p, step = (m < 1.5 ? 1 : m < 3.5 ? 2 : m < 7.5 ? 5 : 10) * p; const t = []; for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9 * step; v += step) t.push(+v.toPrecision(12)); return t; }
export function axes(g, w, h, o) {
  const L = o.left ?? 62, R = 14, T = 14, B = 42, pw = w - L - R, ph = h - T - B;
  const fx = o.logx ? Math.log10 : x => x, fy = o.logy ? Math.log10 : y => y, [x0, x1] = o.x.map(fx), [y0, y1] = o.y.map(fy);
  const X = x => L + (fx(x) - x0) / (x1 - x0) * pw, Y = y => T + ph - (fy(y) - y0) / (y1 - y0) * ph;
  const ticks = (lo, hi, log) => { if (!log) return nice(lo, hi); const n = hi - lo, st = n > 16 ? 5 : n > 7 ? 2 : 1, out = []; for (let e = Math.ceil(lo); e <= Math.floor(hi); e++) if (e % st === 0) out.push(10 ** e); return out; };
  g.strokeStyle = C.line; g.lineWidth = 1;
  for (const v of ticks(x0, x1, o.logx)) { g.beginPath(); g.moveTo(X(v), T); g.lineTo(X(v), T + ph); g.stroke(); txt(g, o.xfmt ? o.xfmt(v) : num(v, 3), X(v), T + ph + 15, { align: 'center', size: 11 }); }
  for (const v of ticks(y0, y1, o.logy)) { g.beginPath(); g.moveTo(L, Y(v)); g.lineTo(L + pw, Y(v)); g.stroke(); txt(g, o.yfmt ? o.yfmt(v) : num(v, 3), L - 6, Y(v) + 4, { align: 'right', size: 11 }); }
  g.strokeStyle = 'rgba(148,190,220,.4)'; g.strokeRect(L, T, pw, ph);
  txt(g, o.xlabel || '', L + pw / 2, h - 6, { align: 'center', size: 12, c: '#b7c8d6' });
  g.save(); g.translate(13, T + ph / 2); g.rotate(-Math.PI / 2); txt(g, o.ylabel || '', 0, 0, { align: 'center', size: 12, c: '#b7c8d6' }); g.restore();
  return { X, Y, L, T, pw, ph, clip() { g.save(); g.beginPath(); g.rect(L, T, pw, ph); g.clip(); }, unclip() { g.restore(); } };
}
function curve(g, ax, xs, f, c, w = 2.2, dash) { line(g, xs.map(x => [ax.X(x), ax.Y(f(x))]).filter(p => isFinite(p[1])), c, w, dash); }
function marker(g, x, y, c = C.red, label) { glow(g, x, y, 16, c, .5); dot(g, x, y, 5.5, c); g.strokeStyle = '#fff'; g.lineWidth = 1.5; g.beginPath(); g.arc(x, y, 5.5, 0, TAU); g.stroke(); if (label) txt(g, label, x + 10, y - 9, { c: C.ink, size: 12, weight: 600 }); }
function legend(g, x, y, items) { items.forEach(([lab, c, dash], i) => { line(g, [[x, y + i * 17], [x + 20, y + i * 17]], c, 2.5, dash); txt(g, lab, x + 26, y + i * 17 + 4, { size: 11.5, c: '#c9d6e2' }); }); }
const range = (a, b, n = 200, log = false) => [...Array(n)].map((_, i) => log ? 10 ** lerp(Math.log10(a), Math.log10(b), i / (n - 1)) : lerp(a, b, i / (n - 1)));
const dataOf = (ctx, id) => ctx.experiments?.[id]?.result;

// Bloch-sphere projection: physics z is up; yaw spins slowly
function bloch(g, cx, cy, R, yaw) {
  const pitch = 0.38, P = v => { const x = v[0] * Math.cos(yaw) - v[1] * Math.sin(yaw), y = v[0] * Math.sin(yaw) + v[1] * Math.cos(yaw); return [cx + R * x, cy - R * (v[2] * Math.cos(pitch) - y * Math.sin(pitch)), y * Math.cos(pitch) + v[2] * Math.sin(pitch)]; };
  glow(g, cx, cy, R * 1.25, 'rgba(45,226,230,.10)', 1);
  g.strokeStyle = 'rgba(111,243,255,.35)'; g.lineWidth = 1; g.beginPath(); g.arc(cx, cy, R, 0, TAU); g.stroke();
  for (const ring of [0, 1]) { const pts = range(0, TAU, 80).map(a => P(ring ? [Math.cos(a), 0, Math.sin(a)] : [Math.cos(a), Math.sin(a), 0])); line(g, pts.map(p => [p[0], p[1]]), 'rgba(111,243,255,.22)', 1); }
  for (const [v, lab] of [[[0, 0, 1.18], '|0⟩ bright'], [[0, 0, -1.18], '|−1⟩ dim'], [[1.2, 0, 0], 'x'], [[0, 1.2, 0], 'y']]) { const p = P(v); txt(g, lab, p[0], p[1], { align: 'center', size: 11.5, c: lab.startsWith('|') ? C.ink : C.mute, base: 'middle' }); }
  line(g, [P([0, 0, -1]), P([0, 0, 1])].map(p => [p[0], p[1]]), 'rgba(148,190,220,.3)', 1, [3, 4]);
  return P;
}

// ---------------------------------------------------------------- scenes
export const SCENES = {
  odmr: {
    frame(g, w, h, t, S, st) {
      const L = A.odmrLines(S.B, S.theta), span = Math.max(160, A.GAMMA * S.B * 1.25 + 4 * S.width), f0 = A.D_MHZ - span, f1 = A.D_MHZ + span;
      const fs = lerp(f0, f1, tri(t, 7)), I = A.lorentzDips(fs, L, S.width, 1), dip = 1 - I;
      // left: green pump, diamond, red glow that dims on resonance
      const gx = w * 0.2, gy = h * 0.42;
      for (let k = 0; k < 3; k++) wavy(g, 14, gy - 22 + k * 22, gx - 40, gy - 6 + k * 6, C.green, t * 12 + k, 4, .3);
      txt(g, '532 nm pump', 16, gy - 40, { c: C.green, size: 11.5 });
      gem(g, gx, gy, 34, 'rgba(255,70,70,.9)', 0.85 - 0.7 * Math.min(1, dip));
      txt(g, `red glow ${(100 * (1 - S.contrast / 100 * dip)).toFixed(1)}%`, gx, gy + 64, { align: 'center', c: '#ff8b8b', size: 12.5, weight: 600 });
      wavy(g, gx - 30, h - 34, gx + 30, h - 34, C.orange, t * 9, 5, .5, 2);
      txt(g, `microwave ${fs.toFixed(0)} MHz`, gx, h - 14, { align: 'center', c: C.orange, size: 12, weight: 600 });
      // right: energy levels; the excited pair is zoomed (the 2870 MHz gap is drawn broken)
      const x0 = w * 0.45, x1 = w * 0.95, y0 = h * 0.80, yc = h * 0.36, k = (h * 0.22) / (A.GAMMA * 10 + 10);
      const ym = yc - (L[0] - A.D_MHZ) * k, yp = yc - (L[1] - A.D_MHZ) * k;
      line(g, [[x0, y0], [x1, y0]], C.ink, 3); txt(g, 'mₛ = 0  (bright)', x1, y0 + 18, { align: 'right', c: C.ink, size: 12.5 });
      line(g, [[x0 + 4, (y0 + yc) / 2 + 26], [x0 + 16, (y0 + yc) / 2 + 20], [x0 + 4, (y0 + yc) / 2 + 14], [x0 + 16, (y0 + yc) / 2 + 8]], C.mute, 1.4);
      txt(g, 'gap D = 2870 MHz, not to scale', x0 + 22, (y0 + yc) / 2 + 20, { size: 11 });
      line(g, [[x0, yc], [x0 + 70, yc]], 'rgba(148,190,220,.6)', 2, [4, 4]); txt(g, 'B = 0', x0, yc - 8, { size: 11 });
      line(g, [[x0 + 70, yc], [x0 + 130, ym]], 'rgba(45,226,230,.45)', 1.2, [2, 3]); line(g, [[x0 + 70, yc], [x0 + 130, yp]], 'rgba(157,123,255,.45)', 1.2, [2, 3]);
      line(g, [[x0 + 130, ym], [x1, ym]], C.teal, 3); txt(g, 'mₛ = −1', x1, ym + 16, { align: 'right', c: C.teal, size: 12.5 });
      line(g, [[x0 + 130, yp], [x1, yp]], C.violet, 3); txt(g, 'mₛ = +1', x1, yp - 8, { align: 'right', c: C.violet, size: 12.5 });
      [[L[0], ym, C.teal, 0.55], [L[1], yp, C.violet, 0.75]].forEach(([f, y, c, fx]) => {
        const on = Math.exp(-(((fs - f) / (S.width * 0.8)) ** 2)), x = lerp(x0 + 130, x1, fx);
        arrow(g, x, y0 - 2, x, y + 5, on > .3 ? c : 'rgba(148,190,220,.35)', on > .3 ? 3 : 1.5, 9);
        if (on > .3) { glow(g, x, (y0 + y) / 2, 26, c, on * .7); txt(g, 'spin flip!', x + 8, (y0 + y) / 2 + 22, { c, size: 12, weight: 700 }); }
        txt(g, `${f.toFixed(1)} MHz`, x + 8, (y0 + y) / 2, { c, size: 11.5, weight: 600 });
      });
      // the sweep, drawn live along the bottom
      const sx = f => lerp(x0, x1, (f - f0) / (f1 - f0));
      const pts = []; for (let f = f0; f <= fs; f += (f1 - f0) / 220) pts.push([sx(f), h - 14 - 24 * A.lorentzDips(f, L, S.width, 1)]);
      line(g, pts, '#ff8b8b', 1.8); dot(g, sx(fs), h - 14 - 24 * I, 4, C.orange);
      st.hud = `sweeping ${fs.toFixed(0)} MHz · dips at ${L.map(x => x.toFixed(1)).join(' and ')} MHz`;
    },
    plot(g, w, h, S) {
      const L = A.odmrLines(S.B, S.theta), span = Math.max(160, A.GAMMA * 10 + 20), fs = range(A.D_MHZ - span, A.D_MHZ + span, 500), c = S.contrast / 100;
      const ax = axes(g, w, h, { x: [fs[0], fs[fs.length - 1]], y: [1 - 1.25 * c, 1 + 0.15 * c], xlabel: 'Microwave frequency (MHz)', ylabel: 'Red fluorescence (normalized)', yfmt: v => v.toFixed(3) });
      ax.clip(); curve(g, ax, fs, f => A.lorentzDips(f, [A.D_MHZ], S.width, c), 'rgba(148,190,220,.45)', 1.5, [5, 4]);
      curve(g, ax, fs, f => A.lorentzDips(f, L, S.width, c), C.red, 2.6); ax.unclip();
      L.forEach((f, i) => marker(g, ax.X(f), ax.Y(A.lorentzDips(f, L, S.width, c)), i ? C.violet : C.teal, i ? 'f₊' : 'f₋'));
      legend(g, ax.L + 12, ax.T + 14, [['with field B', C.red], ['zero field', 'rgba(148,190,220,.6)', [5, 4]]]);
    },
    plug(S) {
      const L = A.odmrLines(S.B, S.theta), bp = S.B * Math.cos(S.theta * Math.PI / 180), first = [A.D_MHZ - A.GAMMA * bp, A.D_MHZ + A.GAMMA * bp];
      return `B<sub>∥</sub> = ${b(num(S.B))} mT × cos ${b(S.theta + '°')} = ${b(num(bp))} mT<br>f<sub>±</sub> = 2870 ± 28.03 × ${num(bp)} = ${b(first[0].toFixed(1))} and ${b(first[1].toFixed(1))} MHz` +
        (S.theta > 0 && S.B > 0 ? `<br><small>exact diagonalization (adds the transverse-field shift): ${L[0].toFixed(1)} and ${L[1].toFixed(1)} MHz</small>` : '') +
        `<br>splitting Δf = ${b(num(L[1] - L[0]) + ' MHz', 'big')}`;
    },
  },

  dipole: {
    frame(g, w, h, t, S, st) {
      const y = h * 0.5, xd = w * 0.12, px = (w * 0.78) / 12, xm = xd + S.r * px, Bmt = A.dipoleMt(S.m, S.r), split = A.splitMHz(Bmt);
      // rail with centimetre ticks
      line(g, [[xd, y + 34], [w - 20, y + 34]], '#caa36a', 6);
      for (let c = 0; c <= 12; c++) { line(g, [[xd + c * px, y + 31], [xd + c * px, y + (c % 2 ? 37 : 42)]], '#3b2e1a', 1.4); if (!(c % 2)) txt(g, `${c} cm`, xd + c * px, y + 56, { align: 'center', size: 11 }); }
      // field lines of a dipole pointing toward the diamond (-x), drawn around the magnet, flowing
      g.save(); g.lineDashOffset = -t * 30;
      for (const k of [0.9, 1.6, 2.6, 4.2, 7]) for (const sgn of [1, -1]) {
        const pts = range(0.05, Math.PI - 0.05, 90).map(th => { const r = k * Math.sin(th) ** 2 * px; return [xm - r * Math.cos(th), y - sgn * r * Math.sin(th)]; });
        line(g, pts, `rgba(157,123,255,${0.55 - k * 0.05})`, 1.3, [6, 6]);
      }
      g.restore();
      roundRect(g, xm - 16, y - 12, 32, 24, 5, '#b9c3cf', '#fff'); g.fillStyle = C.red; g.fillRect(xm - 16, y - 12, 16, 24); txt(g, 'N', xm - 8, y + 4, { c: '#fff', align: 'center', weight: 700 }); txt(g, 'S', xm + 8, y + 4, { c: '#1d2330', align: 'center', weight: 700 });
      gem(g, xd, y, 18, 'rgba(255,70,70,.9)', 0.6);
      // inset: the two lines move apart as B grows
      const ix = w * 0.12, iy = 30, iw = w * 0.36, sc = iw / 2 / A.splitMHz(A.dipoleMt(3, 2)) * 1.6;
      roundRect(g, ix - 10, iy - 8, iw + 20, 64, 10, 'rgba(5,7,13,.55)', C.line);
      line(g, [[ix, iy + 40], [ix + iw, iy + 40]], 'rgba(148,190,220,.4)', 1);
      for (const s of [-1, 1]) { const x = ix + iw / 2 + s * Math.min(iw / 2 - 4, split / 2 * sc); line(g, [[x, iy + 40], [x, iy + 6]], s < 0 ? C.teal : C.violet, 3); }
      txt(g, `Δf = ${num(split)} MHz`, ix + iw / 2, iy + 54, { align: 'center', c: C.ink, size: 12, weight: 600 });
      txt(g, `B = ${num(Bmt)} mT at the diamond`, w - 20, h - 16, { align: 'right', c: C.ink, size: 13, weight: 600 });
      st.hud = `magnet ${S.r.toFixed(1)} cm away · halve the distance → 8× the field`;
    },
    plot(g, w, h, S, st, ctx) {
      const rs = range(2, 12, 120), ax = axes(g, w, h, { x: [2, 12], y: [1, 3000], logx: true, logy: true, xlabel: 'Magnet distance r (cm, log scale)', ylabel: 'Splitting Δf (MHz, log scale)', xfmt: v => num(v) });
      ax.clip(); curve(g, ax, rs, r => A.splitMHz(A.dipoleMt(S.m, r)), C.violet, 2.6);
      const d = dataOf(ctx, 'A2'); if (d) d.x.forEach((x, i) => dot(g, ax.X(x), ax.Y(d.series.measured[i]), 4, C.gold));
      ax.unclip();
      marker(g, ax.X(S.r), ax.Y(A.splitMHz(A.dipoleMt(S.m, S.r))), C.red, `${num(A.splitMHz(A.dipoleMt(S.m, S.r)))} MHz`);
      txt(g, 'slope −3', ax.X(6), ax.Y(A.splitMHz(A.dipoleMt(S.m, 6))) - 16, { c: C.violet, size: 12, weight: 600 });
      legend(g, ax.L + ax.pw - 230, ax.T + 14, [['on-axis equation, your m', C.violet], ['A2 data (m = 1.2, outer pair ×0.85)', C.gold, [1, 3]]]);
    },
    plug(S) { const B = A.dipoleMt(S.m, S.r); return `B = 10⁻⁷ × 2 × ${b(num(S.m))} / (${b(num(S.r / 100))} m)³ = ${b(num(B) + ' mT')}<br>Δf = 2 × 28.03 × ${num(B)} = ${b(num(A.splitMHz(B)) + ' MHz', 'big')}`; },
  },

  heat: {
    init(st) { st.plates = Object.keys(A.SPREADERS).map(k => ({ k, g: A.plate(32) })); st.age = 0; st.scale = 1e-9; },
    frame(g, w, h, t, S, st, dt) {
      if (!st.plates || st.age > 3.2 || st.P !== S.P) { this.init(st); st.P = S.P; }
      st.age += dt;
      const cw = Math.min((w - 60) / 4, h - 90), img = st.img || (st.img = typeof document !== 'undefined' ? document.createElement('canvas') : null);
      st.plates.forEach((p, i) => {
        const M = A.SPREADERS[p.k], alpha = M.k / M.rc; A.plateStep(p.g, alpha, 4000 * S.P / M.rc, 0.0015);
        let mx = 0; for (const v of p.g.T) mx = Math.max(mx, v); if (p.k === 'Silicon') st.scale = Math.max(st.scale, mx);
        const x = 20 + i * (cw + 13), y = Math.max(50, (h - cw) / 2 + 4), sel = M.k === S.kappa;
        if (img) { img.width = img.height = p.g.n; const c2 = img.getContext('2d'), id = c2.createImageData(p.g.n, p.g.n);
          for (let k = 0; k < p.g.T.length; k++) { const [r, gg, bb] = colormap(Math.sqrt(p.g.T[k] / st.scale)); id.data[4 * k] = r; id.data[4 * k + 1] = gg; id.data[4 * k + 2] = bb; id.data[4 * k + 3] = 255; }
          c2.putImageData(id, 0, 0); g.imageSmoothingEnabled = true; g.drawImage(img, x, y, cw, cw); }
        roundRect(g, x, y, cw, cw, 6, null, sel ? C.teal : C.line); if (sel) { g.lineWidth = 3; g.strokeStyle = C.teal; g.strokeRect(x - 2, y - 2, cw + 4, cw + 4); }
        txt(g, p.k, x + cw / 2, y - 22, { align: 'center', c: sel ? C.ink : C.mute, size: 13.5, weight: 700 });
        txt(g, `κ = ${M.k} W/(cm·K)`, x + cw / 2, y - 7, { align: 'center', size: 11 });
        txt(g, `hot spot ${(100 * mx / st.scale).toFixed(0)}%`, x + cw / 2, y + cw + 18, { align: 'center', c: sel ? C.gold : C.mute, size: 12, weight: 600 });
      });
      txt(g, 'slow motion: the first few milliseconds of spreading, same heater on every plate (edges held at sink temperature)', 20, h - 10, { size: 11 });
      st.hud = `ΔT after ${S.t.toFixed(0)} s on ${Object.keys(A.SPREADERS).find(k => A.SPREADERS[k].k === S.kappa)}: ${A.heatRise(S.P, S.kappa, S.t).toFixed(2)} K`;
    },
    plot(g, w, h, S, st, ctx) {
      const ts = range(0, 180, 181), ax = axes(g, w, h, { x: [0, 180], y: [0, 3 * 5.2], xlabel: 'Time (s)', ylabel: 'Heater temperature rise (K)' });
      const col = { Diamond: C.cyan, Copper: C.orange, Aluminium: '#b7c8d6', Silicon: C.violet };
      const d = dataOf(ctx, 'A3'); ax.clip();
      if (d && Math.abs(S.P - 1.5) < 0.05) Object.entries(d.series).forEach(([k, ys]) => ys.forEach((y, i) => i % 6 === 0 && dot(g, ax.X(d.x[i]), ax.Y(y), 2.2, 'rgba(255,196,107,.7)')));
      Object.entries(A.SPREADERS).forEach(([k, M]) => curve(g, ax, ts, t => A.heatRise(S.P, M.k, t), col[k], M.k === S.kappa ? 3.2 : 1.6));
      ax.unclip(); marker(g, ax.X(S.t), ax.Y(A.heatRise(S.P, S.kappa, S.t)), C.red, `${A.heatRise(S.P, S.kappa, S.t).toFixed(2)} K`);
      legend(g, ax.L + ax.pw - 150, ax.T + 14, Object.keys(col).map(k => [k, col[k]]).concat(Math.abs(S.P - 1.5) < 0.05 ? [['A3 data (1.5 W)', C.gold, [1, 3]]] : []));
    },
    plug(S) { const R = A.rth(S.kappa); return `R<sub>th</sub> = 1/(4 × ${b(S.kappa)} × 0.1) + 3.0 + 1.5 = ${b(R.toFixed(2) + ' K/W')}<br>ΔT = ${b(S.P)} W × ${R.toFixed(2)} × (1 − e<sup>−${b(S.t.toFixed(0))}/${A.tauHeat(S.kappa).toFixed(1)}</sup>) = ${b(A.heatRise(S.P, S.kappa, S.t).toFixed(2) + ' K', 'big')}<br><small>steady state ${(S.P * R).toFixed(2)} K; silicon would reach ${(S.P * A.rth(1.5)).toFixed(2)} K</small>`; },
  },

  rabi: {
    frame(g, w, h, t, S, st) {
      const R = Math.min(h * 0.34, w * 0.22), cx = w * 0.3, cy = h * 0.5, P = bloch(g, cx, cy, R, 0.6 + t * 0.15);
      const ax = P([S.Om / Math.hypot(S.Om, S.de), 0, S.de / Math.hypot(S.Om, S.de)]); line(g, [[2 * cx - ax[0], 2 * cy - ax[1]], [ax[0], ax[1]]], 'rgba(255,154,60,.7)', 1.5, [5, 4]);
      txt(g, 'rotation axis (Ω, 0, δ)', ax[0] + 6, ax[1] - 6, { c: C.orange, size: 11 });
      const trail = range(0, S.tau, 90).map(x => P(A.rabiVector(x, S.Om, S.de))); line(g, trail.map(p => [p[0], p[1]]), 'rgba(255,93,143,.75)', 2);
      const v = A.rabiVector(S.tau, S.Om, S.de), p = P(v); arrow(g, cx, cy, p[0], p[1], C.red, 3.2, 12); glow(g, p[0], p[1], 16, C.red, .6);
      // pulse sequence and glow meter
      const x0 = w * 0.58, x1 = w - 24, yy = h * 0.3, tl = (x1 - x0), sc = tl / 4.5;
      txt(g, 'pulse sequence', x0, yy - 34, { c: C.ink, size: 12.5, weight: 600 });
      roundRect(g, x0, yy - 20, 3 * sc * 0.5, 18, 4, 'rgba(72,229,163,.8)'); txt(g, 'laser: initialize', x0 + 4, yy + 14, { size: 11, c: C.green });
      const mw0 = x0 + 1.5 * sc + 8, mww = Math.max(3, S.tau * sc * 2.2); roundRect(g, mw0, yy - 20, mww, 18, 4, 'rgba(255,154,60,.9)'); txt(g, `microwave τ = ${(S.tau * 1000).toFixed(0)} ns`, mw0, yy + 30, { size: 11, c: C.orange });
      roundRect(g, mw0 + mww + 8, yy - 20, 0.3 * sc, 18, 4, 'rgba(72,229,163,.8)'); txt(g, 'read', mw0 + mww + 8, yy + 14, { size: 11, c: C.green });
      const Pm = (1 - v[2]) / 2, F = 1 - 0.3 * Pm;
      txt(g, 'red glow at readout', x0, h * 0.6, { c: C.ink, size: 12.5, weight: 600 }); roundRect(g, x0, h * 0.6 + 10, tl, 16, 8, 'rgba(255,255,255,.06)');
      roundRect(g, x0, h * 0.6 + 10, tl * F, 16, 8, '#ff6b6b'); txt(g, `${(100 * F).toFixed(1)}% (P₋₁ = ${Pm.toFixed(3)})`, x0, h * 0.6 + 44, { c: '#ff8b8b', size: 12.5, weight: 600 });
      const tpi = 1 / (2 * Math.hypot(S.Om, S.de)); txt(g, `π pulse: ${(tpi * 1000).toFixed(0)} ns`, x0, h * 0.82, { c: C.mute, size: 12 });
      st.hud = `drag the pulse length or press Play · the arrow is the spin, the trail is its path during the pulse`;
    },
    plot(g, w, h, S, st, ctx) {
      const ts = range(0, 1, 400), ax = axes(g, w, h, { x: [0, 1], y: [0, 1.05], xlabel: 'Pulse length τ (µs)', ylabel: 'P(mₛ = −1)' });
      const d = dataOf(ctx, 'B1'); ax.clip();
      if (d) { const [x, y] = d.panels['Rabi (µs)']; x.forEach((xi, i) => dot(g, ax.X(xi), ax.Y(y[i] / 0.1), 2.4, 'rgba(255,196,107,.75)')); }
      curve(g, ax, ts, t => A.rabiP(t, S.Om, S.de), C.teal, 2.6); ax.unclip();
      marker(g, ax.X(S.tau), ax.Y(A.rabiP(S.tau, S.Om, S.de)), C.red);
      legend(g, ax.L + ax.pw - 210, ax.T + 14, [['equation, your Ω and δ', C.teal], ['B1 data (Ω = 5 MHz, with decay)', C.gold, [1, 3]]]);
    },
    plug(S) { const W = Math.hypot(S.Om, S.de); return `Ω<sub>eff</sub> = √(${b(num(S.Om))}² + ${b(num(S.de))}²) = ${b(num(W) + ' MHz')}<br>P<sub>−1</sub> = ${(S.Om ** 2 / W ** 2).toFixed(3)} × sin²(π × ${num(W)} × ${b(num(S.tau))}) = ${b(A.rabiP(S.tau, S.Om, S.de).toFixed(3), 'big')}<br><small>π pulse = 1/(2Ω<sub>eff</sub>) = ${(1000 / (2 * W)).toFixed(0)} ns</small>`; },
  },

  ramsey: {
    frame(g, w, h, t, S, st) {
      if (!st.ds || st.key !== `${S.de}|${S.t2s}`) { st.ds = A.gaussianDetunings(48, S.de, S.t2s); st.key = `${S.de}|${S.t2s}`; }
      const R = Math.min(h * 0.38, w * 0.2), cx = w * 0.27, cy = h * 0.5;
      g.strokeStyle = 'rgba(111,243,255,.35)'; g.lineWidth = 1; g.beginPath(); g.arc(cx, cy, R, 0, TAU); g.stroke();
      line(g, [[cx - R - 8, cy], [cx + R + 8, cy]], C.line, 1); line(g, [[cx, cy - R - 8], [cx, cy + R + 8]], C.line, 1);
      txt(g, 'equator of the Bloch sphere, seen from above (rotating frame)', cx, cy + R + 26, { align: 'center', size: 11 });
      let mx = 0, my = 0;
      st.ds.forEach(d => { const ph = TAU * d * S.tau, x = Math.cos(ph), y = Math.sin(ph); mx += x / st.ds.length; my += y / st.ds.length; line(g, [[cx, cy], [cx + R * x, cy - R * y]], 'rgba(157,123,255,.4)', 1.2); dot(g, cx + R * x, cy - R * y, 2.6, C.violet); });
      arrow(g, cx, cy, cx + R * mx, cy - R * my, C.red, 3.4, 12);
      const x0 = w * 0.56, x1 = w - 24, yy = h * 0.32, sc = (x1 - x0 - 60) / 3;
      txt(g, 'pulse sequence', x0, yy - 34, { c: C.ink, size: 12.5, weight: 600 });
      roundRect(g, x0, yy - 20, 22, 18, 4, 'rgba(255,154,60,.9)'); txt(g, 'π/2', x0 + 11, yy + 14, { align: 'center', size: 11, c: C.orange });
      line(g, [[x0 + 26, yy - 11], [x0 + 30 + S.tau * sc, yy - 11]], C.mute, 1.5, [3, 3]); txt(g, `wait τ = ${S.tau.toFixed(2)} µs`, x0 + 30, yy + 14, { size: 11 });
      roundRect(g, x0 + 34 + S.tau * sc, yy - 20, 22, 18, 4, 'rgba(255,154,60,.9)'); txt(g, 'π/2', x0 + 45 + S.tau * sc, yy - 26, { align: 'center', size: 11, c: C.orange });
      const env = Math.exp(-((S.tau / S.t2s) ** 2));
      txt(g, `coherence left (length of the red arrow)`, x0, h * 0.6, { c: C.ink, size: 12.5, weight: 600 }); roundRect(g, x0, h * 0.6 + 10, x1 - x0, 16, 8, 'rgba(255,255,255,.06)');
      roundRect(g, x0, h * 0.6 + 10, (x1 - x0) * Math.hypot(mx, my), 16, 8, C.red); txt(g, `${Math.hypot(mx, my).toFixed(2)} measured from the drawn spins · ${env.toFixed(2)} from e^(−(τ/T₂*)²)`, x0, h * 0.6 + 44, { size: 12, c: '#ff8b8b' });
      st.hud = `48 spins, each with its own static detuning · they fan out and the average shrinks`;
    },
    plot(g, w, h, S, st, ctx) {
      const ts = range(0, 3, 500), ax = axes(g, w, h, { x: [0, 3], y: [0, 1.05], xlabel: 'Free evolution τ (µs)', ylabel: 'P(mₛ = 0)' });
      const d = dataOf(ctx, 'B1'); ax.clip();
      if (d) { const [x, y] = d.panels['Ramsey (µs)']; x.forEach((xi, i) => dot(g, ax.X(xi), ax.Y(1 - y[i] / 0.1), 2.4, 'rgba(255,196,107,.75)')); }
      curve(g, ax, ts, t => 0.5 * (1 + Math.exp(-((t / S.t2s) ** 2))), 'rgba(148,190,220,.6)', 1.4, [5, 4]); curve(g, ax, ts, t => 0.5 * (1 - Math.exp(-((t / S.t2s) ** 2))), 'rgba(148,190,220,.6)', 1.4, [5, 4]);
      curve(g, ax, ts, t => A.ramseyP0(t, S.de, S.t2s), C.violet, 2.4); ax.unclip();
      marker(g, ax.X(S.tau), ax.Y(A.ramseyP0(S.tau, S.de, S.t2s)), C.red);
      legend(g, ax.L + ax.pw - 240, ax.T + 14, [['fringes, your δ and T₂*', C.violet], ['envelope e^(−(τ/T₂*)²)', 'rgba(148,190,220,.7)', [5, 4]], ['B1 data (δ = 3 MHz, T₂* = 0.6 µs)', C.gold, [1, 3]]]);
    },
    plug(S) { const e = Math.exp(-((S.tau / S.t2s) ** 2)); return `cos(2π × ${b(num(S.de))} × ${b(num(S.tau))}) = ${Math.cos(TAU * S.de * S.tau).toFixed(3)}, envelope e<sup>−(${num(S.tau)}/${b(num(S.t2s))})²</sup> = ${e.toFixed(3)}<br>P<sub>0</sub> = ½(1 + ${Math.cos(TAU * S.de * S.tau).toFixed(3)} × ${e.toFixed(3)}) = ${b(A.ramseyP0(S.tau, S.de, S.t2s).toFixed(3), 'big')}`; },
  },

  echo: {
    frame(g, w, h, t, S, st) {
      if (!st.ds) { st.ds = A.gaussianDetunings(48, 0, 0.25); st.nz = A.gaussianDetunings(48, 0, 1).map(x => x * 4.4); }
      const loop = 5, s = (t % loop) / loop, half = s < 0.5, C0 = A.echoC(S.tau, S.t2, S.p), sig = Math.sqrt(Math.max(0, -2 * Math.log(Math.max(C0, 1e-9))));
      const R = Math.min(h * 0.38, w * 0.2), cx = w * 0.27, cy = h * 0.5;
      g.strokeStyle = 'rgba(111,243,255,.35)'; g.lineWidth = 1; g.beginPath(); g.arc(cx, cy, R, 0, TAU); g.stroke();
      line(g, [[cx - R - 8, cy], [cx + R + 8, cy]], C.line, 1); line(g, [[cx, cy - R - 8], [cx, cy + R + 8]], C.line, 1);
      let mx = 0, my = 0;
      st.ds.forEach((d, i) => {
        const acc = half ? s : 1 - s, ph = TAU * d * acc * 2 * 3 + st.nz[i] * sig * s;   // static part reverses after the pi pulse, slow noise keeps adding
        const x = Math.cos(ph), y = Math.sin(ph); mx += x / st.ds.length; my += y / st.ds.length;
        line(g, [[cx, cy], [cx + R * x, cy - R * y]], 'rgba(72,229,163,.35)', 1.2); dot(g, cx + R * x, cy - R * y, 2.6, C.green);
      });
      arrow(g, cx, cy, cx + R * mx, cy - R * my, C.red, 3.4, 12);
      if (Math.abs(s - 0.5) < 0.03) { glow(g, cx, cy, R * 1.2, C.orange, .45); txt(g, 'π pulse: every spin flips', cx, cy - R - 16, { align: 'center', c: C.orange, size: 13, weight: 700 }); }
      const x0 = w * 0.56, x1 = w - 24, yy = h * 0.32, mid = (x0 + x1) / 2;
      txt(g, 'pulse sequence', x0, yy - 34, { c: C.ink, size: 12.5, weight: 600 });
      roundRect(g, x0, yy - 20, 20, 18, 4, 'rgba(255,154,60,.9)'); roundRect(g, mid - 14, yy - 20, 28, 18, 4, 'rgba(255,154,60,.95)'); roundRect(g, x1 - 20, yy - 20, 20, 18, 4, 'rgba(255,154,60,.9)');
      txt(g, 'π/2', x0 + 10, yy + 14, { align: 'center', size: 11, c: C.orange }); txt(g, 'π', mid, yy + 14, { align: 'center', size: 11, c: C.orange }); txt(g, 'π/2', x1 - 10, yy + 14, { align: 'center', size: 11, c: C.orange });
      line(g, [[x0 + 22, yy - 11], [mid - 16, yy - 11]], C.mute, 1.5, [3, 3]); line(g, [[mid + 16, yy - 11], [x1 - 22, yy - 11]], C.mute, 1.5, [3, 3]);
      dot(g, lerp(x0 + 10, x1 - 10, s), yy - 30, 4, C.red);
      txt(g, `τ/2 = ${(S.tau / 2).toFixed(0)} µs`, (x0 + mid) / 2, yy + 30, { align: 'center', size: 11 }); txt(g, `τ/2`, (mid + x1) / 2, yy + 30, { align: 'center', size: 11 });
      txt(g, 'echo contrast at the end', x0, h * 0.62, { c: C.ink, size: 12.5, weight: 600 }); roundRect(g, x0, h * 0.62 + 10, x1 - x0, 16, 8, 'rgba(255,255,255,.06)');
      roundRect(g, x0, h * 0.62 + 10, (x1 - x0) * C0, 16, 8, C.red); txt(g, `C = ${C0.toFixed(3)}`, x0, h * 0.62 + 44, { size: 12.5, c: '#ff8b8b', weight: 600 });
      st.hud = half ? 'first half: static fields fan the spins out' : 'second half: the π pulse makes the same fields bring them back';
    },
    plot(g, w, h, S, st, ctx) {
      const ts = range(0, 2000, 400), ax = axes(g, w, h, { x: [0, 2000], y: [0, 1.05], xlabel: 'Total free time τ (µs)', ylabel: 'Echo contrast C' });
      const d = dataOf(ctx, 'B1'); ax.clip();
      if (d) { const [x, y] = d.panels['Echo (µs)']; x.forEach((xi, i) => dot(g, ax.X(xi), ax.Y(y[i] / 0.1), 2.6, 'rgba(255,196,107,.8)')); }
      curve(g, ax, ts, t => Math.exp(-((t / S.t2) ** 2)), 'rgba(148,190,220,.4)', 1.2, [3, 4]);
      curve(g, ax, ts, t => A.echoC(t, S.t2, S.p), C.green, 2.6); ax.unclip(); marker(g, ax.X(S.tau), ax.Y(A.echoC(S.tau, S.t2, S.p)), C.red);
      legend(g, ax.L + ax.pw - 230, ax.T + 14, [['echo, your T₂ and p', C.green], ['p = 2 for comparison', 'rgba(148,190,220,.6)', [3, 4]], ['B1 data (T₂ = 300 µs, p = 1.5)', C.gold, [1, 3]]]);
    },
    plug(S) { return `C = e<sup>−(${b(num(S.tau))}/${b(num(S.t2))})<sup>${b(num(S.p))}</sup></sup> = e<sup>−${((S.tau / S.t2) ** S.p).toFixed(3)}</sup> = ${b(A.echoC(S.tau, S.t2, S.p).toFixed(3), 'big')}<br><small>coherence falls to 1/e at τ = T₂ = ${num(S.t2)} µs, about ${num(S.t2 / 2)}× longer than a typical T₂* of 0.5 µs</small>`; },
  },

  vector: {
    frame(g, w, h, t, S, st) {
      const cx = w * 0.32, cy = h * 0.52, R = Math.min(h, w * 0.6) * 0.3, yaw = 0.5 + t * 0.25, pitch = 0.42;
      const P = v => { const x = v[0] * Math.cos(yaw) - v[1] * Math.sin(yaw), y = v[0] * Math.sin(yaw) + v[1] * Math.cos(yaw); return [cx + R * x, cy - R * (v[2] * Math.cos(pitch) - y * Math.sin(pitch))]; };
      const cube = [-1, 1].flatMap(x => [-1, 1].flatMap(y => [-1, 1].map(z => [x, y, z].map(c => c / Math.sqrt(3)))));
      cube.forEach((a, i) => cube.forEach((c, j) => { if (j > i && a.filter((v, k) => v !== c[k]).length === 1) line(g, [P(a), P(c)], 'rgba(148,190,220,.22)', 1); }));
      const cols = [C.teal, C.violet, C.pink, C.gold], Bv = A.bVector(S.B, S.theta, S.phi), pr = A.NV_AXES.map(n => n[0] * Bv[0] + n[1] * Bv[1] + n[2] * Bv[2]);
      A.NV_AXES.forEach((n, i) => { line(g, [P(n.map(x => -x * 1.25)), P(n.map(x => x * 1.25))], cols[i] + '88', 1.4, [4, 3]); const e = P(n.map(x => x * 1.32)); txt(g, `NV ${i + 1}`, e[0], e[1], { c: cols[i], size: 11.5, weight: 600, align: 'center' }); });
      const bs = 1 / 5;
      A.NV_AXES.forEach((n, i) => { const tip = P(n.map(x => x * pr[i] * bs)); line(g, [P([0, 0, 0]), tip], cols[i], 4.5); dot(g, tip[0], tip[1], 4, cols[i]); });
      const bt = P(Bv.map(x => x * bs)); arrow(g, cx, cy, bt[0], bt[1], C.ink, 3, 12); txt(g, 'B', bt[0] + 8, bt[1] - 6, { c: C.ink, size: 15, weight: 700 });
      const x0 = w * 0.62; txt(g, 'what each NV orientation measures', x0, 40, { c: C.ink, size: 12.5, weight: 600 });
      A.splittings(Bv).forEach((s, i) => { const y = 62 + i * 46, wmax = w - x0 - 40; roundRect(g, x0, y, wmax, 14, 7, 'rgba(255,255,255,.05)'); roundRect(g, x0, y, wmax * s / (2 * A.GAMMA * 5), 14, 7, cols[i]); txt(g, `Δf${'₁₂₃₄'[i]} = ${s.toFixed(1)} MHz`, x0, y + 28, { size: 11.5, c: cols[i] }); });
      txt(g, `recovered |B| = ${A.magnitudeFromSplittings(A.splittings(Bv)).toFixed(3)} mT`, x0, h - 22, { c: C.ink, size: 13, weight: 700 });
      st.hud = 'colored bars on each axis: the projection of B that orientation feels';
    },
    plot(g, w, h, S) {
      const Bv = A.bVector(S.B, S.theta, S.phi), L = A.NV_AXES.flatMap((n, i) => { const sh = A.splittings(Bv)[i] / 2; return [[A.D_MHZ - sh, i], [A.D_MHZ + sh, i]]; });
      const span = 2 * A.GAMMA * 5 * 0.6 + 30, fs = range(A.D_MHZ - span, A.D_MHZ + span, 600), cols = [C.teal, C.violet, C.pink, C.gold];
      const ax = axes(g, w, h, { x: [fs[0], fs[fs.length - 1]], y: [0.88, 1.01], xlabel: 'Microwave frequency (MHz): eight lines from four orientations (first order)', ylabel: 'Fluorescence', yfmt: v => v.toFixed(2) });
      ax.clip(); curve(g, ax, fs, f => 1 - L.reduce((s, [l]) => s + 0.012 * 9 / ((f - l) ** 2 + 9), 0), C.red, 2.2);
      L.forEach(([l, i]) => line(g, [[ax.X(l), ax.Y(1.005)], [ax.X(l), ax.Y(0.975)]], cols[i], 3)); ax.unclip();
      legend(g, ax.L + 12, ax.T + 14, cols.map((c, i) => [`NV ${i + 1}`, c]));
    },
    plug(S) { const s = A.splittings(A.bVector(S.B, S.theta, S.phi)); return `Δf<sub>i</sub> = ${s.map(x => b(x.toFixed(1))).join(', ')} MHz<br>|B| = √(¾ Σ (Δf<sub>i</sub>/56.06)²) = ${b(A.magnitudeFromSplittings(s).toFixed(3) + ' mT', 'big')} <small>(set: ${num(S.B)} mT)</small>`; },
  },

  arrhenius: {
    frame(g, w, h, t, S, st) {
      const p = A.freeCarriers(S.Ea, S.Na, S.T, S.Nd), ion = (p + S.Nd) / S.Na, x0 = 30, x1 = w * 0.62, yv = h * 0.78, sc = (h * 0.5) / 0.65, ya = yv - S.Ea * sc;
      g.fillStyle = 'rgba(157,123,255,.18)'; g.fillRect(x0, yv, x1 - x0, h - yv - 18); line(g, [[x0, yv], [x1, yv]], C.violet, 2.5); txt(g, 'valence band', x0 + 6, h - 24, { c: C.violet, size: 12 });
      g.fillStyle = 'rgba(45,226,230,.10)'; g.fillRect(x0, 14, x1 - x0, 26); line(g, [[x0, 40], [x1, 40]], C.teal, 2); txt(g, 'conduction band, 5.47 eV up (not to scale)', x0 + 6, 32, { c: C.teal, size: 11.5 });
      line(g, [[x0 + 8, 46], [x0 + 18, 52], [x0 + 8, 58]], C.mute, 1.4);
      line(g, [[x0, ya], [x1, ya]], C.gold, 1.6, [6, 4]); txt(g, `boron level, E_A = ${S.Ea.toFixed(2)} eV`, x1 + 8, ya + 4, { c: C.gold, size: 12, weight: 600 });
      arrow(g, x0 + 30, yv, x0 + 30, ya + 3, C.gold, 1.4, 7);
      const N = 36, nIon = Math.round(Math.min(1, ion) * N), jig = (S.T / 800) * 3;
      for (let i = 0; i < N; i++) { const x = lerp(x0 + 60, x1 - 20, i / (N - 1)), y = ya + jig * Math.sin(t * 9 + i * 1.7); if (i * 7 % N < nIon) { dot(g, x, y, 4.2, C.cyan); } else { g.strokeStyle = C.gold; g.lineWidth = 1.4; g.beginPath(); g.arc(x, y, 4.2, 0, TAU); g.stroke(); } }
      const nh = Math.round(Math.min(1, p / S.Na) * N * 1.0);
      for (let i = 0; i < nh; i++) { const x = x0 + ((i * 53 + t * (20 + S.T / 10)) % (x1 - x0)), y = yv + 16 + (i * 13 % Math.max(10, h - yv - 44)); glow(g, x, y, 9, 'rgba(255,93,143,.6)', .9); g.strokeStyle = C.pink; g.lineWidth = 1.5; g.beginPath(); g.arc(x, y, 4.5, 0, TAU); g.stroke(); }
      const tx = w * 0.82, th = h * 0.62; roundRect(g, tx - 9, 40, 18, th, 9, 'rgba(255,255,255,.06)', C.line); const fill = (S.T - 250) / 550;
      roundRect(g, tx - 6, 40 + th * (1 - fill), 12, th * fill, 6, C.red); glow(g, tx, 52 + th, 16, C.red, .9); dot(g, tx, 50 + th, 10, C.red);
      txt(g, `${S.T.toFixed(0)} K`, tx, 30, { align: 'center', c: C.ink, size: 13, weight: 700 }); txt(g, `${(S.T - 273.15).toFixed(0)} °C`, tx, h - 8, { align: 'center', size: 11.5 });
      txt(g, '● filled boron (gave up a hole)   ○ neutral boron   ◌ free hole', x0, 66, { size: 11, c: C.mute });
      st.hud = `${(100 * p / S.Na).toPrecision(2)}% of boron atoms have released a free hole at ${S.T.toFixed(0)} K`;
    },
    plot(g, w, h, S, st, ctx) {
      const Ts = range(250, 800, 160), ax = axes(g, w, h, { x: [1000 / 800, 1000 / 250], y: [1e-3, 1e9], logy: true, xlabel: '1000 / T (1/K): hotter to the left', ylabel: 'Resistivity ρ (Ω·cm, log)' });
      const d = dataOf(ctx, 'B3'); ax.clip();
      if (d) d.x.forEach((x, i) => dot(g, ax.X(x), ax.Y(d.series['resistivity (Ω·cm)'][i]), 3, 'rgba(255,196,107,.85)'));
      line(g, Ts.map(T => [ax.X(1000 / T), ax.Y(A.resistivity(A.freeCarriers(0.045, S.Na, T, S.Nd), T))]), 'rgba(148,190,220,.6)', 1.6, [5, 4]);
      line(g, Ts.map(T => [ax.X(1000 / T), ax.Y(A.resistivity(A.freeCarriers(S.Ea, S.Na, T, S.Nd), T))]), C.pink, 2.6); ax.unclip();
      const r = A.resistivity(A.freeCarriers(S.Ea, S.Na, S.T, S.Nd), S.T); marker(g, ax.X(1000 / S.T), ax.Y(r), C.red, `${num(r)} Ω·cm`);
      legend(g, ax.L + 12, ax.T + 14, [['your E_A and doping', C.pink], ['silicon-like dopant (0.045 eV)', 'rgba(148,190,220,.7)', [5, 4]], ['B3 data (0.37 eV, 3×10¹⁷)', C.gold, [1, 3]]]);
    },
    plug(S) { const p = A.freeCarriers(S.Ea, S.Na, S.T, S.Nd), r = A.resistivity(p, S.T); return `N<sub>A</sub> = ${b(num(S.Na))}, N<sub>D</sub> = ${b(num(S.Nd))} cm⁻³, T = ${b(S.T.toFixed(0) + ' K')}, e<sup>−E<sub>A</sub>/kT</sup> = ${num(Math.exp(-S.Ea / (A.KB_EV * S.T)))}<br>p = ${b(num(p) + ' cm⁻³')} (${(100 * p / S.Na).toPrecision(2)}% of boron), μ = ${num(A.holeMobility(S.T))} cm²/V·s<br>ρ = 1/(q p μ) = ${b(num(r) + ' Ω·cm', 'big')}`; },
  },

  g2: {
    init(st) { st.hist = new Float64Array(81); st.na = 0; st.nb = 0; st.T = 0; st.rng = A.mulberry(11); st.vis = []; st.next = 0; },
    frame(g, w, h, t, S, st, dt) {
      if (!st.hist || st.key !== `${S.rho}|${S.tau1}`) { this.init(st); st.key = `${S.rho}|${S.tau1}`; }
      // fast background simulation (ns): renewal emitter with two exponential stages (rates sum to 1/tau1) plus Poisson background
      const r = st.rng, k = 1 / (2 * S.tau1), sig = 1 / (4 * S.tau1), bg = sig * (1 - S.rho) / S.rho, eta = 1;
      let te = st.T, tb = st.T, A1 = [], B1 = [];
      const Tend = st.T + 60000 * S.tau1 / 12;
      while (te < Tend) { te += -Math.log(1 - r()) / k - Math.log(1 - r()) / k; if (r() < eta) (r() < .5 ? A1 : B1).push(te); }
      while (bg > 0 && tb < Tend) { tb += -Math.log(1 - r()) / bg; if (r() < eta) (r() < .5 ? A1 : B1).push(tb); }
      A1.sort((a, b) => a - b); B1.sort((a, b) => a - b);
      let j0 = 0; for (const ta of A1) { while (j0 < B1.length && B1[j0] < ta - 80.5) j0++; for (let j = j0; j < B1.length && B1[j] <= ta + 80.5; j++) { const bin = Math.round((B1[j] - ta) / 2) + 40; if (bin >= 0 && bin <= 80) st.hist[bin] += 1; } }
      st.na += A1.length; st.nb += B1.length; st.T = Tend;
      // slow visible photons
      const ex = w * 0.12, ey = h * 0.55, bx = w * 0.45, dA = [bx, h * 0.14], dB = [w * 0.8, ey];
      st.next -= dt; if (st.next <= 0) { st.vis.push({ s: 0, bg: Math.random() > S.rho, up: Math.random() < .5 }); st.next = 0.25 + Math.random() * 0.35; }
      glow(g, ex, ey, 34, 'rgba(255,70,70,.8)', .7); dot(g, ex, ey, 7, '#ff9a9a'); txt(g, 'single NV', ex, ey + 46, { align: 'center', c: C.ink, size: 12, weight: 600 });
      line(g, [[bx - 22, ey + 22], [bx + 22, ey - 22]], C.cyan, 4); txt(g, '50:50 beam splitter', bx + 26, ey + 30, { size: 11 });
      for (const [p, lab] of [[dA, 'detector A'], [dB, 'detector B']]) { roundRect(g, p[0] - 22, p[1] - 16, 44, 32, 6, '#2a3446', C.line); txt(g, lab, p[0], p[1] + 32, { align: 'center', size: 11.5 }); }
      st.vis = st.vis.filter(v => v.s < 1.02); st.vis.forEach(v => {
        v.s += dt * 0.9; const c = v.bg ? '#9aa6b2' : '#ff6b6b';
        let x, y; if (v.s < 0.5) { x = lerp(ex, bx, v.s / 0.5); y = ey; } else { const tgt = v.up ? dA : dB, q = (v.s - .5) / .5; x = lerp(bx, tgt[0], q); y = lerp(ey, tgt[1], q); }
        glow(g, x, y, 10, c, .8); dot(g, x, y, 3.2, c); if (v.s >= 1) { const p = v.up ? dA : dB; glow(g, p[0], p[1], 40, c, .9); }
      });
      txt(g, 'red: photons from the NV · grey: background light', w * 0.55, h - 14, { size: 11 });
      const norm = 2 * st.na * st.nb / Math.max(1, st.T) || 1, g0 = st.hist[40] / norm;
      st.g0 = g0; st.norm = norm; st.hud = `${(st.na + st.nb).toLocaleString('en-US')} detected photons simulated · measured g⁽²⁾(0) ≈ ${g0.toFixed(2)} (formula ${(1 - S.rho ** 2).toFixed(2)})`;
    },
    plot(g, w, h, S, st, ctx) {
      const ax = axes(g, w, h, { x: [-80, 80], y: [0, 1.5], xlabel: 'Delay between detector A and B clicks, τ (ns)', ylabel: 'g⁽²⁾(τ)' });
      const d = dataOf(ctx, 'C1'); ax.clip();
      if (d) { const [x, y] = d.panels.g2; x.forEach((xi, i) => i % 2 === 0 && dot(g, ax.X(xi), ax.Y(y[i]), 2, 'rgba(255,196,107,.55)')); }
      if (st.hist && st.norm) { const bw = ax.pw / 81; for (let i = 0; i < 81; i++) { const v = st.hist[i] / st.norm, x = ax.X((i - 40) * 2); g.fillStyle = 'rgba(157,123,255,.55)'; g.fillRect(x - bw / 2 + .5, ax.Y(v), bw - 1, ax.Y(0) - ax.Y(v)); } }
      curve(g, ax, range(-80, 80, 321), tt => A.g2(tt, S.rho, S.tau1), C.teal, 2.6);
      line(g, [[ax.X(-80), ax.Y(0.5)], [ax.X(80), ax.Y(0.5)]], C.red, 1.2, [6, 4]); ax.unclip(); txt(g, 'single-emitter limit 0.5', ax.X(-78), ax.Y(0.5) - 6, { c: C.red, size: 11 });
      legend(g, ax.L + ax.pw - 220, ax.T + 14, [['equation', C.teal], ['live simulated histogram', 'rgba(157,123,255,.9)'], ['C1 data (ρ² = 0.8)', C.gold, [1, 3]]]);
    },
    plug(S, st) { return `g<sup>(2)</sup>(0) = 1 − ${b(num(S.rho))}² = ${b((1 - S.rho ** 2).toFixed(3), 'big')} ${1 - S.rho ** 2 < 0.5 ? '<span class="ok">below 0.5: one emitter</span>' : '<span class="no">above 0.5: could be two or more</span>'}<br><small>recovery time ${b(num(S.tau1) + ' ns')}; background-limited contrast needs ρ > 0.71${st && st.g0 ? `; simulated so far: ${st.g0.toFixed(2)}` : ''}</small>`; },
  },

  fet: {
    frame(g, w, h, t, S, st, dt) {
      const vov = S.vgs - 1.5, I = A.fetI(S.vgs, S.vds, S.mu), sat = vov > 0 && S.vds >= vov, vd = Math.min(S.vds, Math.max(vov, 0));
      const x0 = w * 0.16, x1 = w * 0.84, ys = h * 0.5;
      g.fillStyle = 'rgba(111,243,255,.08)'; g.fillRect(20, ys, w - 40, h - ys - 20); txt(g, 'single-crystal diamond', 30, h - 28, { c: C.cyan, size: 12 });
      for (let x = 30; x < w - 30; x += 18) txt(g, 'H', x, ys - 3, { size: 9, c: 'rgba(232,241,248,.45)' });
      roundRect(g, 20, ys - 30, x0 - 14, 30, 4, '#c9a24a', '#e8c76c'); roundRect(g, x1 - 6, ys - 30, w - 20 - x1 + 6, 30, 4, '#c9a24a', '#e8c76c');
      txt(g, 'source', (20 + x0) / 2, ys - 38, { align: 'center', size: 12, c: C.gold }); txt(g, `drain −${S.vds.toFixed(1)} V`, (x1 + w - 20) / 2, ys - 38, { align: 'center', size: 12, c: C.gold });
      g.fillStyle = 'rgba(157,123,255,.35)'; g.fillRect(x0 + 4, ys - 26, x1 - x0 - 8, 22); txt(g, 'Al₂O₃ 30 nm', x0 + 10, ys - 10, { size: 11, c: '#cbbcff' });
      roundRect(g, x0 + 4, ys - 64, x1 - x0 - 8, 34, 5, '#8b98a5', '#cfd8e2'); txt(g, `gate −${S.vgs.toFixed(1)} V`, (x0 + x1) / 2, ys - 42, { align: 'center', c: '#0b1220', size: 13, weight: 700 });
      // gradual channel: local charge q(x) ∝ vov − V(x); V(x) from (vov V − V²/2) = (x/L)(vov vd − vd²/2)
      const Vx = s => { const tot = vov * vd - vd * vd / 2; const c = s * tot; const disc = vov * vov - 2 * c; return vov - Math.sqrt(Math.max(0, disc)); };
      const qx = s => Math.max(0, vov - Vx(s)) / Math.max(vov, 1e-6);
      if (vov > 0) {
        const n = 220; for (let i = 0; i < n; i++) { const s = i / n, th = 3 + 9 * qx(s); g.fillStyle = `rgba(255,93,143,${0.15 + 0.5 * qx(s)})`; g.fillRect(lerp(x0, x1, s), ys + 1, (x1 - x0) / n + 1, th); }
        st.ph = ((st.ph || 0) + dt * I / Math.max(1e-6, A.fetK(S.mu)) * 0.02) % 1;
        const cum = range(0, 1, 101).map(qx); let tot = 0; const C1 = cum.map(v => (tot += v)); const at = u => { const k = C1.findIndex(v => v >= u * tot); return Math.max(0, k) / 100; };
        for (let i = 0; i < 46; i++) { const s = at(((i / 46) + st.ph) % 1), x = lerp(x0, x1, s); dot(g, x, ys + 6 + (i % 3) * 2.5, 2.6, C.pink); }
        if (sat) { glow(g, x1 - 6, ys + 6, 22, C.gold, .7); txt(g, 'pinch-off', x1 - 10, ys + 34, { align: 'right', c: C.gold, size: 12, weight: 700 }); }
      } else txt(g, 'gate below threshold: no hole channel', (x0 + x1) / 2, ys + 24, { align: 'center', c: C.mute, size: 12.5 });
      txt(g, 'two-dimensional hole gas', (x0 + x1) / 2, ys + 50, { align: 'center', c: C.pink, size: 12 });
      txt(g, `I_D = ${(I * 1e3).toFixed(2)} mA · ${vov <= 0 ? 'off' : sat ? 'saturation' : 'linear'}`, w - 24, h - 28, { align: 'right', c: C.ink, size: 13.5, weight: 700 });
      st.hud = 'pink: holes in the channel · thinner channel near the drain as V_DS grows';
    },
    plot(g, w, h, S) {
      const vs = range(0, 20, 200), ax = axes(g, w, h, { x: [0, 20], y: [0, A.fetI(10, 20, 300) * 1e3 * 0.42], xlabel: '|V_DS| (V)', ylabel: '|I_D| (mA), W = 100 µm, L = 2 µm' });
      ax.clip(); for (const v of [3, 5, 7, 9]) curve(g, ax, vs, x => A.fetI(v, x, S.mu) * 1e3, 'rgba(148,190,220,.45)', 1.3);
      curve(g, ax, range(0, 8.5, 80), x => A.fetI(x + 1.5, x, S.mu) * 1e3, 'rgba(255,196,107,.7)', 1.4, [5, 4]);
      curve(g, ax, vs, x => A.fetI(S.vgs, x, S.mu) * 1e3, C.pink, 2.8); ax.unclip();
      marker(g, ax.X(S.vds), ax.Y(A.fetI(S.vgs, S.vds, S.mu) * 1e3), C.red, `${(A.fetI(S.vgs, S.vds, S.mu) * 1e3).toFixed(2)} mA`);
      legend(g, ax.L + 12, ax.T + 14, [[`|V_GS| = ${S.vgs.toFixed(1)} V`, C.pink], ['|V_GS| = 3, 5, 7, 9 V', 'rgba(148,190,220,.7)'], ['saturation edge V_DS = V_GS − V_th', C.gold, [5, 4]]]);
    },
    plug(S) { const k = A.fetK(S.mu), vov = S.vgs - 1.5, sat = S.vds >= vov; return `k = ${b(num(S.mu))} × 2.66×10⁻⁷ F/cm² × 100/2 = ${b(num(k * 1e6) + ' µA/V²')}<br>${vov <= 0 ? 'V<sub>GS</sub> below threshold: I<sub>D</sub> = 0' : sat ? `saturation: I<sub>D</sub> = k/2 × (${b(num(S.vgs))} − 1.5)² = ${b((A.fetI(S.vgs, S.vds, S.mu) * 1e3).toFixed(3) + ' mA', 'big')}` : `linear: I<sub>D</sub> = k[(${num(vov)}) × ${b(num(S.vds))} − ½ × ${num(S.vds)}²] = ${b((A.fetI(S.vgs, S.vds, S.mu) * 1e3).toFixed(3) + ' mA', 'big')}`}`; },
  },

  gate: {
    frame(g, w, h, t, S, st, dt) {
      const nu = A.couplingKHz(S.r), tg = A.gateTimeUs(S.r), wco = Math.exp(-((tg / S.t2) ** 3)), cx = w * 0.42, cy = h * 0.48, sep = lerp(60, w * 0.6, (S.r - 8) / 32);
      for (let x = 24; x < w - 20; x += 22) for (let y = 30; y < h - 30; y += 19) dot(g, x + ((y / 19) % 2) * 11, y, 1.3, 'rgba(111,243,255,.18)');
      st.cs = st.cs || [1, 1]; st.tc = (st.tc || 0) + dt; if (st.tc > 0.7) { st.tc = 0; st.cs = [Math.random() < S.q, Math.random() < S.q]; }
      const pa = [cx - sep / 2, cy], pb = [cx + sep / 2, cy];
      g.save(); g.lineDashOffset = -t * 20; for (const k of [0.25, 0.45, 0.7]) { g.strokeStyle = `rgba(157,123,255,${0.55 - k * 0.4})`; g.lineWidth = 1.5; g.setLineDash([5, 5]); g.beginPath(); g.ellipse(cx, cy, sep / 2, sep * k, 0, Math.PI, TAU); g.stroke(); g.beginPath(); g.ellipse(cx, cy, sep / 2, sep * k, 0, 0, Math.PI); g.stroke(); } g.setLineDash([]); g.restore();
      [pa, pb].forEach((p, i) => { const on = st.cs[i]; glow(g, p[0], p[1], 34, on ? 'rgba(255,70,70,.9)' : 'rgba(150,160,170,.5)', on ? .8 : .4); dot(g, p[0], p[1], 9, on ? '#ff8080' : '#7f8a96');
        txt(g, on ? 'NV⁻ ready' : 'NV⁰ dark!', p[0], p[1] + 44, { align: 'center', c: on ? '#ff9a9a' : C.mute, size: 12.5, weight: 700 }); });
      line(g, [[pa[0], cy + 64], [pb[0], cy + 64]], C.ink, 1.2); line(g, [[pa[0], cy + 58], [pa[0], cy + 70]], C.ink, 1.2); line(g, [[pb[0], cy + 58], [pb[0], cy + 70]], C.ink, 1.2);
      txt(g, `r = ${S.r.toFixed(1)} nm`, cx, cy + 84, { align: 'center', c: C.ink, size: 12.5, weight: 600 });
      const dx = w - 92, dy = 74, ph = ((t * 0.5) % 1); g.strokeStyle = C.line; g.lineWidth = 6; g.beginPath(); g.arc(dx, dy, 42, 0, TAU); g.stroke();
      g.strokeStyle = C.violet; g.beginPath(); g.arc(dx, dy, 42, -Math.PI / 2, -Math.PI / 2 + TAU * ph); g.stroke();
      txt(g, 'gate phase', dx, dy - 2, { align: 'center', size: 11 }); txt(g, `t_g = ${num(tg)} µs`, dx, dy + 14, { align: 'center', c: C.ink, size: 12, weight: 600 });
      txt(g, `coupling ν = ${num(nu)} kHz`, 24, 28, { c: C.violet, size: 13, weight: 700 });
      txt(g, `coherence left after the gate: ${(100 * wco).toFixed(1)}%`, 24, h - 18, { c: C.green, size: 12.5, weight: 600 });
      st.hud = `each NV is redrawn every 0.7 s: in the right charge state with probability q = ${S.q.toFixed(2)}`;
    },
    plot(g, w, h, S) {
      const qs = range(0.5, 1, 100), ax = axes(g, w, h, { x: [0.5, 1], y: [0, 1], xlabel: 'Charge-state preparation probability q', ylabel: 'Bell-state fidelity F' });
      ax.clip(); curve(g, ax, qs, q => A.bellFidelity(S.r, 1e9, q), 'rgba(148,190,220,.6)', 1.4, [5, 4]);
      curve(g, ax, qs, q => A.bellFidelity(S.r, S.t2, q), C.violet, 2.8);
      for (const [f, lab] of [[0.67, 'measured 2013: 0.67'], [0.82, 'optimal control 2014: 0.82']]) { line(g, [[ax.X(0.5), ax.Y(f)], [ax.X(1), ax.Y(f)]], 'rgba(255,196,107,.6)', 1.2, [2, 4]); txt(g, lab, ax.X(0.51), ax.Y(f) - 5, { c: C.gold, size: 11 }); }
      line(g, [[ax.X(0.5), ax.Y(0.5)], [ax.X(1), ax.Y(0.5)]], 'rgba(255,93,108,.5)', 1, [6, 4]); txt(g, 'entanglement needs F > 0.5', ax.X(0.51), ax.Y(0.5) + 14, { c: C.red, size: 11 }); ax.unclip();
      marker(g, ax.X(S.q), ax.Y(A.bellFidelity(S.r, S.t2, S.q)), C.red, A.bellFidelity(S.r, S.t2, S.q).toFixed(3));
      legend(g, ax.L + ax.pw - 210, ax.T + ax.ph - 40, [['your r and T₂', C.violet], ['perfect coherence', 'rgba(148,190,220,.7)', [5, 4]]]);
    },
    plug(S) { const nu = A.couplingKHz(S.r), tg = A.gateTimeUs(S.r), wco = Math.exp(-((tg / S.t2) ** 3)), fc = (1 + wco) ** 2 / 4; return `ν = 52.07 / ${b(num(S.r))}³ MHz = ${b(num(nu) + ' kHz')}, t<sub>g</sub> = ${b(num(tg) + ' µs')}, e<sup>−(t<sub>g</sub>/${b(num(S.t2))})³</sup> = ${wco.toFixed(4)}<br>F = ${b(S.q.toFixed(2))}² × ${fc.toFixed(4)} + (1 − ${S.q.toFixed(2)}²)/4 = ${b(A.bellFidelity(S.r, S.t2, S.q).toFixed(3), 'big')}<br><small>the q² term caps the fidelity: at perfect coherence it is ${A.bellFidelity(S.r, 1e9, S.q).toFixed(3)}</small>`; },
  },

  yield: {
    frame(g, w, h, t, S, st, dt) {
      const side = Math.sqrt(S.A), key = `${S.A}|${S.d}|${S.D0}`;
      if (!st.L || st.key !== key || st.age > 6) { st.L = layoutDies(S.d, side); st.key = key; st.age = 0; st.pts = []; st.rng = A.mulberry(st.seed = (st.seed || 1) + 1); st.target = Math.round(S.D0 * Math.PI * (st.L.r / 10) ** 2); }
      st.age += dt; const R = Math.min(h * 0.44, w * 0.27), cx = w * 0.3, cy = h * 0.5, sc = R / (S.d / 2);
      const want = Math.min(st.target, Math.round(st.target * Math.min(1, st.age / 3.5)));
      while (st.pts.length < want) { const rr = st.L.r * Math.sqrt(st.rng()), a = TAU * st.rng(), x = rr * Math.cos(a), y = rr * Math.sin(a); st.pts.push([x, y, st.age]); const die = st.L.dies.find(q => x >= q.x && x < q.x + side && y >= q.y && y < q.y + side); if (die) die.bad = true; }
      glow(g, cx, cy, R * 1.15, 'rgba(111,243,255,.10)', 1); g.fillStyle = 'rgba(111,243,255,.10)'; g.strokeStyle = C.cyan; g.lineWidth = 1.5; g.beginPath(); g.arc(cx, cy, R, 0, TAU); g.fill(); g.stroke();
      st.L.dies.forEach(q => { g.fillStyle = q.bad ? 'rgba(255,93,108,.75)' : 'rgba(72,229,163,.55)'; g.fillRect(cx + q.x * sc + .6, cy + q.y * sc + .6, side * sc - 1.2, side * sc - 1.2); });
      st.pts.forEach(([x, y, born]) => { const age = st.age - born; glow(g, cx + x * sc, cy + y * sc, 9 * Math.max(.3, 1 - age), '#fff', Math.max(.3, 1 - age)); dot(g, cx + x * sc, cy + y * sc, 1.8, '#fff'); });
      const good = st.L.dies.filter(q => !q.bad).length, tot = st.L.dies.length, x0 = w * 0.64;
      txt(g, 'this wafer', x0, 46, { c: C.ink, size: 13, weight: 700 }); txt(g, `${good} good of ${tot} dies (${(100 * good / Math.max(1, tot)).toFixed(0)}%)`, x0, 70, { c: C.green, size: 13.5, weight: 600 });
      txt(g, `${st.pts.length} killer defects landed`, x0, 92, { size: 12.5 });
      txt(g, 'the equations (average wafer)', x0, 130, { c: C.ink, size: 13, weight: 700 });
      txt(g, `Poisson ${(100 * A.poissonY(S.A, S.D0)).toFixed(0)}% · Murphy ${(100 * A.murphyY(S.A, S.D0)).toFixed(0)}%`, x0, 154, { size: 12.5 });
      txt(g, `${num(A.goodDies(S.d, S.A, S.D0))} good dies expected`, x0, 176, { c: C.green, size: 13.5, weight: 600 });
      st.hud = 'white sparks: defects falling on the wafer · red: dies they ruined · a new wafer every 6 s';
    },
    plot(g, w, h, S) {
      const ds = range(0.1, 20, 160, true), top = Math.max(10, A.diesPerWafer(S.d, S.A) * 1.1), ax = axes(g, w, h, { x: [0.1, 20], y: [0, top], logx: true, xlabel: 'Killer defect density D₀ (per cm², log)', ylabel: 'Good dies per wafer' });
      ax.clip(); curve(g, ax, ds, d0 => A.diesPerWafer(S.d, S.A) * A.poissonY(S.A, d0), C.teal, 2, [5, 4]); curve(g, ax, ds, d0 => A.goodDies(S.d, S.A, d0), C.green, 2.8);
      line(g, [[ax.X(0.1), ax.Y(A.diesPerWafer(S.d, S.A))], [ax.X(20), ax.Y(A.diesPerWafer(S.d, S.A))]], 'rgba(148,190,220,.5)', 1, [2, 4]); ax.unclip();
      marker(g, ax.X(S.D0), ax.Y(A.goodDies(S.d, S.A, S.D0)), C.red, `${num(A.goodDies(S.d, S.A, S.D0))}`);
      legend(g, ax.L + ax.pw - 200, ax.T + 14, [['Murphy (clustered defects)', C.green], ['Poisson (random defects)', C.teal, [5, 4]], [`gross dies N = ${A.diesPerWafer(S.d, S.A)}`, 'rgba(148,190,220,.7)', [2, 4]]]);
    },
    plug(S) { const x = S.A * 1e-2 * S.D0; return `A·D₀ = ${b(num(S.A))} mm² × ${b(num(S.D0))} /cm² = ${num(x)}<br>N = π(${b(S.d)}/2)²/${num(S.A)} − π${S.d}/√(2 × ${num(S.A)}) = ${b(A.diesPerWafer(S.d, S.A))}, Y<sub>Murphy</sub> = ${A.murphyY(S.A, S.D0).toFixed(3)}<br>good dies = ${b(num(A.goodDies(S.d, S.A, S.D0)), 'big')} per wafer`; },
  },

  bfom: {
    frame(g, w, h, t, S, st, dt, ctx) {
      const M = ctx.materials, keys = ['Si', '4H-SiC', 'GaN', 'Ga2O3', 'Diamond'], wmax = A.driftUm(M.Si, S.VB), cw = (w - 80) / keys.length, top = 50, bot = h - 60;
      keys.forEach((k, i) => {
        const m = M[k], W = A.driftUm(m, S.VB), hh = Math.max(3, (bot - top) * Math.sqrt(W / wmax)), x = 40 + i * cw + cw * 0.18, ww = cw * 0.64, sel = k === S.mat;
        roundRect(g, x, bot - hh, ww, hh, 6, sel ? 'rgba(45,226,230,.35)' : 'rgba(148,190,220,.14)', sel ? C.teal : C.line);
        const r = A.ronSp(m, S.VB), rate = 1 / Math.sqrt(r); for (let j = 0; j < 8; j++) { const yy = bot - hh + ((j / 8 + t * rate * 0.4) % 1) * hh; dot(g, x + ww * ((j * 37 % 8) + .5) / 8, yy, 2, sel ? C.cyan : 'rgba(232,241,248,.5)'); }
        roundRect(g, x - 4, bot, ww + 8, 8, 3, '#c9a24a'); roundRect(g, x - 4, bot - hh - 8, ww + 8, 8, 3, '#c9a24a');
        txt(g, m.name.split(' (')[0], x + ww / 2, bot + 26, { align: 'center', c: sel ? C.ink : C.mute, size: 12, weight: sel ? 700 : 500 });
        txt(g, `${num(W)} µm`, x + ww / 2, bot - hh - 16, { align: 'center', c: sel ? C.cyan : C.mute, size: 11.5, weight: 600 });
        txt(g, `${num(r)} mΩ·cm²`, x + ww / 2, bot + 42, { align: 'center', c: sel ? C.gold : C.mute, size: 11 });
      });
      txt(g, `drift layer needed to block ${num(S.VB)} V (height ∝ √thickness so all fit) · dots: on-state current, faster = lower resistance`, 40, 26, { size: 11.5 });
      st.hud = `${M[S.mat].name.split(' (')[0]}: ${num(A.driftUm(M[S.mat], S.VB))} µm thick, ${num(A.ronSp(M.Si, S.VB) / A.ronSp(M[S.mat], S.VB))}× lower resistance than silicon`;
    },
    plot(g, w, h, S, st, ctx) {
      const M = ctx.materials, vs = range(100, 10000, 100, true), cols = { Si: '#b7c8d6', '4H-SiC': C.violet, GaN: C.green, Ga2O3: C.gold, Diamond: C.cyan };
      const ax = axes(g, w, h, { x: [100, 10000], y: [1e-4, 1e4], logx: true, logy: true, xlabel: 'Breakdown voltage V_B (V, log)', ylabel: 'R_on,sp (mΩ·cm², log)' });
      ax.clip(); Object.keys(cols).forEach(k => curve(g, ax, vs, v => A.ronSp(M[k], v), cols[k], k === S.mat ? 3.2 : 1.6));
      const meas = ctx.power?.['Diamond (measured 2022 device)']; if (meas) { glow(g, ax.X(1000), ax.Y(meas.rsp_1kv), 12, C.red, .6); dot(g, ax.X(1000), ax.Y(meas.rsp_1kv), 4.5, C.red); txt(g, 'measured diamond device, scaled to 1 kV', ax.X(1000) + 8, ax.Y(meas.rsp_1kv) - 8, { c: C.red, size: 11 }); }
      ax.unclip(); marker(g, ax.X(S.VB), ax.Y(A.ronSp(M[S.mat], S.VB)), C.red);
      legend(g, ax.L + 12, ax.T + 14, Object.keys(cols).map(k => [M[k].name.split(' (')[0], cols[k]]));
    },
    plug(S, st, ctx) { const m = ctx.materials[S.mat], r = A.ronSp(m, S.VB); return `${m.name}: ε<sub>r</sub> = ${m.eps_r}, μ = ${num(m.mu)} cm²/V·s (${m.carrier}), E<sub>c</sub> = ${m.ec_mv_cm} MV/cm<br>R<sub>on,sp</sub> = 4 × ${b(num(S.VB))}² / (ε μ E<sub>c</sub>³) = ${b(num(r) + ' mΩ·cm²', 'big')}, W = ${b(num(A.driftUm(m, S.VB)) + ' µm')}<br><small>BFOM relative to silicon: ${num(A.ronSp(ctx.materials.Si, 1000) / A.ronSp(m, 1000))}×</small>`; },
  },

  surface: {
    frame(g, w, h, t, S, st, dt) {
      const d = S.d, size = Math.min(h - 60, w * 0.46), cell = size / d, x0 = 24, y0 = (h - size) / 2;
      st.err = st.err && st.err.length === d * d ? st.err : new Float32Array(d * d); st.acc = (st.acc || 0) + dt;
      const visRate = Math.min(0.5, S.p * 40);
      if (st.acc > 0.12) { st.acc = 0; for (let i = 0; i < d * d; i++) { st.err[i] = Math.max(0, st.err[i] - 0.25); if (Math.random() < visRate) st.err[i] = 1; } }
      for (let i = 0; i < d - 1; i++) for (let j = 0; j < d - 1; j++) {
        const x = x0 + (j + 0.5) * cell, y = y0 + (i + 0.5) * cell, s = st.err[i * d + j] + st.err[i * d + j + 1] + st.err[(i + 1) * d + j] + st.err[(i + 1) * d + j + 1];
        g.fillStyle = (i + j) % 2 ? 'rgba(157,123,255,.16)' : 'rgba(45,226,230,.12)'; g.fillRect(x, y, cell, cell);
        if (s % 2 > 0.5 && s > 0.6) { g.fillStyle = 'rgba(255,196,107,.45)'; g.fillRect(x, y, cell, cell); }
      }
      for (let i = 0; i < d; i++) for (let j = 0; j < d; j++) { const e = st.err[i * d + j], x = x0 + (j + 0.5) * cell, y = y0 + (i + 0.5) * cell; if (e > 0) glow(g, x, y, cell * 0.9, C.red, e); dot(g, x, y, Math.max(1.6, cell * 0.16), e > 0 ? C.red : C.ink); }
      const xr = x0 + size + 26; txt(g, `distance-${d} surface code`, xr, 50, { c: C.ink, size: 14, weight: 700 }); txt(g, `${A.surfaceQubits(d)} physical qubits`, xr, 74, { size: 12.5 }); txt(g, 'per logical qubit', xr, 92, { size: 12.5 });
      txt(g, 'red: a physical error', xr, 120, { size: 12, c: C.red }); txt(g, 'gold: checks that light up', xr, 138, { size: 12, c: C.gold }); txt(g, `errors shown ${Math.round(visRate / S.p)}× more often than p`, xr, 156, { size: 11 });
      const pl = A.logicalError(S.p, d); txt(g, `p_L = ${num(pl)} per round`, xr, 194, { c: S.p < 1e-2 ? C.green : C.red, size: 14, weight: 700 });
      txt(g, S.p < 1e-2 ? `d + 2 → ${num(1e-2 / S.p)}× safer` : 'above threshold: bigger is worse', xr, 216, { size: 12.5, c: S.p < 1e-2 ? C.green : C.red });
      st.hud = 'each dot is a data qubit; the shaded squares are the parity checks between them';
    },
    plot(g, w, h, S) {
      const ps = range(1e-4, 2e-2, 120, true), ax = axes(g, w, h, { x: [1e-4, 2e-2], y: [1e-25, 1], logx: true, logy: true, xlabel: 'Physical error rate p (log)', ylabel: 'Logical error p_L (log)' });
      ax.clip(); for (let d = 3; d <= 25; d += 2) curve(g, ax, ps, p => A.logicalError(p, d), d === S.d ? C.teal : `rgba(148,190,220,${0.15 + 0.4 * (1 - d / 25)})`, d === S.d ? 3 : 1.2);
      line(g, [[ax.X(1e-2), ax.Y(1e-25)], [ax.X(1e-2), ax.Y(1)]], C.red, 1.4, [6, 4]); ax.unclip(); txt(g, 'threshold', ax.X(1e-2) - 6, ax.T + 30, { align: 'right', c: C.red, size: 11.5 });
      marker(g, ax.X(S.p), ax.Y(A.logicalError(S.p, S.d)), C.red, `d = ${S.d}`);
      legend(g, ax.L + 12, ax.T + ax.ph - 30, [[`your distance d = ${S.d}`, C.teal], ['d = 3, 5, …, 25', 'rgba(148,190,220,.6)']]);
    },
    plug(S) { const pl = A.logicalError(S.p, S.d); let dn = 3; while (dn < 101 && A.logicalError(S.p, dn) > 1e-12) dn += 2; return `p<sub>L</sub> = 0.1 × (${b(num(S.p))}/0.01)<sup>(${b(S.d)} + 1)/2</sup> = ${b(num(pl), 'big')}, n = 2 × ${S.d}² − 1 = ${b(A.surfaceQubits(S.d))}<br><small>${S.p < 1e-2 ? `for 10⁻¹² per round you need d = ${dn < 101 ? dn : '> 100'} (${dn < 101 ? A.surfaceQubits(dn).toLocaleString('en-US') : 'too many'} qubits)` : 'above threshold no distance helps'}</small>`; },
  },
};

function layoutDies(dMm, sideMm, edgeMm = 3) {           // die grid fully inside the usable radius (adamas.wafer geometry)
  const r = dMm / 2 - edgeMm, n = Math.ceil(dMm / sideMm), dies = [];
  for (let i = -n; i < n; i++) for (let j = -n; j < n; j++) { const x = i * sideMm, y = j * sideMm, far = Math.max(Math.hypot(x, y), Math.hypot(x + sideMm, y), Math.hypot(x, y + sideMm), Math.hypot(x + sideMm, y + sideMm)); if (far <= r) dies.push({ x, y, bad: false }); }
  return { r, dies };
}
