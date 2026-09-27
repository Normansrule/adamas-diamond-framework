// Tiny looping previews for the lab cards (2-D canvas, cheap, pause when off-screen).
import { fitCanvas, colormap } from './site.js';
const DRAW = {
  rabi(g, w, h, t) { g.strokeStyle = '#9d7bff'; g.lineWidth = 2; g.beginPath();
    for (let x = 0; x < w; x++) { const y = h / 2 - (h * .35) * Math.cos((x / w) * 14 + t * 2) * Math.exp(-x / w * 1.2); x ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke(); },
  heat(g, w, h, t) { const r = 26 + 6 * Math.sin(t * 2);
    [[w * .25, '#8b98a5', 1.0], [w * .75, '#2de2e6', .25]].forEach(([cx, c, k]) => { const gr = g.createRadialGradient(cx, h * .35, 2, cx, h * .35, r * (1 + k));
      const [R, G, B] = colormap(k); gr.addColorStop(0, `rgba(${R},${G},${B},.95)`); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(cx - 80, 0, 160, h);
      g.fillStyle = c; g.font = '12px Inter'; g.fillText(k === 1 ? 'Si' : 'Diamond', cx - 18, h - 10); }); },
  lattice(g, w, h, t) { for (let i = 0; i < 60; i++) { const a = i * 2.39996 + t * .6, r = 6 + (i % 12) * 3.6, x = w / 2 + Math.cos(a) * r * 2.2, y = h / 2 + Math.sin(a) * r * .8;
      g.fillStyle = i === 7 ? '#ff5d6c' : '#6ff3ff'; g.globalAlpha = .4 + .6 * ((Math.sin(a) + 1) / 2); g.beginPath(); g.arc(x, y, i === 7 ? 4 : 2.4, 0, 7); g.fill(); } g.globalAlpha = 1; },
  cpu(g, w, h, t) { const v = Math.floor(t * 2) % 16; g.font = '600 13px JetBrains Mono';
    ['PC', 'ACC', 'OUT'].forEach((n, i) => { const val = (v + i * 5) % 16; g.fillStyle = '#8ea3b5'; g.fillText(n, 14, 28 + i * 28);
      for (let b = 0; b < 4; b++) { g.fillStyle = (val >> (3 - b)) & 1 ? '#2de2e6' : 'rgba(255,255,255,.08)'; g.fillRect(60 + b * 26, 16 + i * 28, 20, 16); } }); },
  qec(g, w, h, t) { const n = 5, s = Math.min(w, h * 2) / 12; const on = Math.floor(t * 1.5) % 9;
    for (let r = 0; r < n; r++) for (let c = 0; c < 2 * n; c++) { const lit = (r * 7 + c * 3 + on) % 11 === 0;
      g.fillStyle = lit ? '#ff5d6c' : 'rgba(111,243,255,.25)'; g.beginPath(); g.arc(20 + c * s * 1.1, 14 + r * s * .9, lit ? 5 : 3, 0, 7); g.fill(); } },
  fab(g, w, h, t) { const layers = ['#1b2b44', '#6ff3ff', '#ffc46b', '#9d7bff', '#2de2e6']; const k = (t * .7) % (layers.length + 1);
    layers.forEach((c, i) => { if (i < k) { g.fillStyle = c; g.globalAlpha = .85; const y = h - 18 - i * 16; g.fillRect(20 + i * 6, y, w - 40 - i * 12, 12); } }); g.globalAlpha = 1; },
  stack(g, w, h, t) { const cols = ['#8b98a5', '#ffc46b', '#9d7bff', '#2de2e6', '#ff5d8f'], e = (Math.sin(t) + 1) / 2;
    cols.forEach((c, i) => { const y = h - 20 - i * (8 + 10 * e); g.fillStyle = c; g.globalAlpha = .85; g.beginPath(); g.moveTo(w / 2 - 70, y); g.lineTo(w / 2, y + 10); g.lineTo(w / 2 + 70, y); g.lineTo(w / 2, y - 10); g.closePath(); g.fill(); }); g.globalAlpha = 1; },
  globe(g, w, h, t) { const cx = w / 2, cy = h / 2, R = h * .42; g.strokeStyle = 'rgba(111,243,255,.35)'; g.beginPath(); g.arc(cx, cy, R, 0, 7); g.stroke();
    for (let k = 0; k < 7; k++) { const lo = t * .5 + k * .9, x = cx + R * Math.sin(lo) * Math.cos(.4 * k - 1), y = cy - R * Math.sin(.4 * k - 1) * .9; if (Math.cos(lo) > 0) { g.fillStyle = ['#ffc46b', '#ff5d8f', '#2de2e6', '#9d7bff'][k % 4]; g.beginPath(); g.arc(x, y, 3.5, 0, 7); g.fill(); } } },
  ring(g, w, h, t) { ['#2de2e6', '#9d7bff', '#ff5d8f', '#ffc46b', '#48e5a3'].forEach((c, k) => { g.strokeStyle = c; g.lineWidth = 1.6; g.beginPath();
      for (let x = 0; x < w; x++) { const ph = (x / w) * 6 + t * 2 - k * 1.25, y = h / 2 + (h * .32) * Math.tanh(4 * Math.sin(ph)) * (k % 2 ? -1 : 1); x ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke(); }); },
  power(g, w, h, t) { const bars = [['Si', 1, '#8b98a5'], ['SiC', .38, '#e0a030'], ['GaN', .3, '#9d7bff'], ['C', .07, '#2de2e6']];
    bars.forEach(([n, v, c], k) => { const bw = (w - 60) * v * (0.85 + .15 * Math.sin(t * 2 + k)); g.fillStyle = c; g.fillRect(40, 12 + k * 24, bw, 16); g.fillStyle = '#8ea3b5'; g.font = '11px Inter'; g.fillText(n, 8, 24 + k * 24); }); },
  machine(g, w, h, t) { const n = 36, c = 18, ph = (t * .6) % 1; for (let k = 0; k < n; k++) { const i = k % c, j = Math.floor(k / c) + (k % 3 ? 0 : 0), lit = Math.abs(i / c - ph) < .08;
      for (let r = 0; r < 4; r++) { g.fillStyle = lit ? '#ff5d6c' : 'rgba(45,226,230,.55)'; g.fillRect(14 + i * ((w - 28) / c), 10 + r * 24, (w - 28) / c - 4, 20); } } },
  explorer(g, w, h, t) { g.strokeStyle = '#48e5a3'; g.lineWidth = 2; g.beginPath();
    for (let x = 0; x < w; x++) { const y = h - 10 - (h - 20) / (1 + Math.exp(-((x / w) * 10 - 5 - Math.sin(t) * 1.5))); x ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke(); },
};
export function minis() {
  document.querySelectorAll('canvas.mini').forEach(c => {
    let vis = false; new IntersectionObserver(e => vis = e[0].isIntersecting).observe(c);
    const f = t => { if (vis) { const { g, w, h } = fitCanvas(c, 110); g.clearRect(0, 0, w, h); DRAW[c.dataset.mini](g, w, h, t / 1000); } requestAnimationFrame(f); };
    requestAnimationFrame(f);
  });
}
