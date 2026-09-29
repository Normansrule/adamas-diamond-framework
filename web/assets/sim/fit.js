// Curve fitting in the browser, mirroring adamas.fitting: a small Levenberg-Marquardt solver plus the experiment
// models (ODMR Lorentzians, Rabi, Ramsey, echo, Arrhenius, transistor square law, g2). Returns the iteration
// history so the Data Lab can animate convergence. Unit-tested with node against the Python fits.
const GAMMA = 28.025, KB = 8.617333262e-5;

function solve(A, b) {                         // Gaussian elimination with partial pivoting
  const n = b.length, M = A.map((r, i) => [...r, b[i]]);
  for (let c = 0; c < n; c++) { let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r; [M[c], M[p]] = [M[p], M[c]];
    const d = M[c][c] || 1e-300; for (let r = c + 1; r < n; r++) { const f = M[r][c] / d; for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; } }
  const x = new Array(n).fill(0); for (let r = n - 1; r >= 0; r--) { let s = M[r][n]; for (let k = r + 1; k < n; k++) s -= M[r][k] * x[k]; x[r] = s / (M[r][r] || 1e-300); } return x;
}
function invert(A) { const n = A.length; return A.map((_, i) => solve(A, A.map((__, j) => (i === j ? 1 : 0)))).map((col, i, cols) => cols.map(c => c[i])); }

export function lm(f, x, y, p0, { iters = 200, lower = null, upper = null } = {}) {
  let p = p0.slice(), lam = 1e-3, hist = [p.slice()];
  const clamp = q => q.map((v, i) => Math.min(upper ? upper[i] : Infinity, Math.max(lower ? lower[i] : -Infinity, v)));
  const res = q => x.map((xi, i) => y[i] - f(xi, q)), sse = r => r.reduce((s, v) => s + v * v, 0);
  let r = res(p), s = sse(r);
  const jac = q => { const J = x.map(() => new Array(q.length)); q.forEach((v, j) => { const h = 1e-6 * Math.max(1, Math.abs(v)), qp = q.slice(); qp[j] += h;
    x.forEach((xi, i) => { J[i][j] = (f(xi, qp) - f(xi, q)) / h; }); }); return J; };
  for (let it = 0; it < iters; it++) {
    const J = jac(p), n = p.length, JtJ = Array.from({ length: n }, (_, a) => Array.from({ length: n }, (_, b) => J.reduce((t, row) => t + row[a] * row[b], 0))), Jtr = Array.from({ length: n }, (_, a) => J.reduce((t, row, i) => t + row[a] * r[i], 0));
    const A = JtJ.map((row, a) => row.map((v, b) => (a === b ? v * (1 + lam) : v))), step = solve(A, Jtr), q = clamp(p.map((v, i) => v + step[i])), rq = res(q), sq = sse(rq);
    if (sq < s) { const done = (s - sq) / Math.max(s, 1e-300) < 1e-10; p = q; r = rq; s = sq; lam /= 3; hist.push(p.slice()); if (done) break; } else { lam *= 4; if (lam > 1e12) break; }
  }
  const J = jac(p), n = p.length, JtJ = Array.from({ length: n }, (_, a) => Array.from({ length: n }, (_, b) => J.reduce((t, row) => t + row[a] * row[b], 0)));
  const s2 = s / Math.max(1, x.length - n), C = invert(JtJ).map(row => row.map(v => v * s2));
  return { p, err: C.map((row, i) => Math.sqrt(Math.max(0, row[i]))), sse: s, hist };
}

const median = a => { const s = [...a].sort((u, v) => u - v); return s[Math.floor(s.length / 2)]; };
const std = a => { const m = a.reduce((s, v) => s + v, 0) / a.length; return Math.sqrt(a.reduce((s, v) => s + (v - m) ** 2, 0) / a.length); };
const noise2 = y => std(y.slice(2).map((v, i) => v - 2 * y[i + 1] + y[i])) / Math.sqrt(6);
export function lorentzSum(xx, q) { let v = q[0]; for (let k = 1; k + 2 < q.length + 1; k += 3) { const a = q[k], x0 = q[k + 1], w = q[k + 2]; v -= a * w * w / ((xx - x0) ** 2 + w * w); } return v; }

function findDips(x, y) {
  const top = [...y].sort((a, b) => b - a).slice(0, Math.max(5, y.length >> 2)), base = median(top), dep = y.map(v => base - v), n = noise2(y), win = Math.max(1, Math.floor(x.length / 60));
  const sm = dep.map((_, i) => { let s = 0, c = 0; for (let k = i - (win >> 1); k <= i + (win >> 1); k++) if (k >= 0 && k < dep.length) { s += dep[k]; c++; } return s / c; });
  const thr = 4 * n / Math.sqrt(win), peaks = [];
  for (let i = 1; i < sm.length - 1; i++) {
    if (!(sm[i] >= sm[i - 1] && sm[i] > sm[i + 1])) continue;
    let lo = i, hi = i; while (lo > 0 && sm[lo - 1] <= sm[lo] + 1e-15) lo--; while (hi < sm.length - 1 && sm[hi + 1] <= sm[hi] + 1e-15) hi++;
    let l = i, mL = sm[i]; while (l > 0 && sm[l - 1] < sm[i] + 1e-15) { l--; mL = Math.min(mL, sm[l]); } let rr = i, mR = sm[i]; while (rr < sm.length - 1 && sm[rr + 1] < sm[i] + 1e-15) { rr++; mR = Math.min(mR, sm[rr]); }
    const prom = sm[i] - Math.max(mL, mR);
    if (prom > thr) peaks.push({ i, prom });
  }
  peaks.sort((a, b) => b.prom - a.prom); const chosen = []; for (const pk of peaks) if (chosen.every(c => Math.abs(c.i - pk.i) >= win)) chosen.push(pk);
  return { base, peaks: chosen.slice(0, 8).sort((a, b) => a.i - b.i), n };
}

export const MODELS = {
  odmr(x, y) {
    const { base, peaks } = findDips(x, y), step = Math.abs(x[1] - x[0]);
    if (!peaks.length) throw new Error('no resonance dip found above the noise');
    let p0 = [base]; peaks.forEach(pk => p0.push(base - y[pk.i], x[pk.i], 3 * step + 1));
    let r = lm(lorentzSum, x, y, p0, { iters: 300 });
    const keep = peaks.map((_, k) => k).filter(k => Math.abs(r.p[3 + 3 * k]) > 0.5 * step && r.p[1 + 3 * k] > 2.5 * r.err[1 + 3 * k]);
    if (keep.length && keep.length < peaks.length) { p0 = [r.p[0]]; keep.forEach(k => p0.push(r.p[1 + 3 * k], r.p[2 + 3 * k], r.p[3 + 3 * k])); const h = r.hist; r = lm(lorentzSum, x, y, p0, { iters: 300 }); r.hist = h.concat(r.hist); }
    const n = (r.p.length - 1) / 3, names = ['baseline']; for (let k = 1; k <= n; k++) names.push(`depth${k}`, `center${k}`, `hwhm${k}`);
    const centers = []; for (let k = 0; k < n; k++) centers.push(r.p[2 + 3 * k]); centers.sort((a, b) => a - b);
    const notes = [`${n} resonance line(s) found`];
    if (n === 1) notes.push(`single line at ${centers[0].toFixed(2)} MHz (zero-field splitting D ≈ 2870 MHz)`);
    else notes.push(`outermost lines ${(centers[n - 1] - centers[0]).toFixed(2)} MHz apart → |B∥| ≥ ${((centers[n - 1] - centers[0]) / (2 * GAMMA)).toFixed(3)} mT along the most aligned NV axis`);
    return { f: lorentzSum, ...r, names, notes };
  },
  rabi(x, y) {
    const f = (t, q) => q[3] + q[0] * (1 - Math.cos(2 * Math.PI * q[1] * t) * Math.exp(-t / q[2]));
    const r = lm(f, x, y, [(Math.max(...y) - Math.min(...y)) / 2, guessFreq(x, y), Math.max(...x), Math.min(...y)]);
    return { f, ...r, names: ['amplitude', 'rabi_MHz', 'decay_us', 'offset'], notes: [`π pulse = ${(500 / r.p[1]).toFixed(1)} ns, π/2 pulse = ${(250 / r.p[1]).toFixed(1)} ns`] };
  },
  ramsey(x, y) {
    const f = (t, q) => q[3] + q[0] * (1 - Math.cos(2 * Math.PI * q[1] * t) * Math.exp(-((t / q[2]) ** 2)));
    const r = lm(f, x, y, [(Math.max(...y) - Math.min(...y)) / 2, guessFreq(x, y), Math.max(...x) / 4, Math.min(...y)]);
    return { f, ...r, names: ['amplitude', 'detuning_MHz', 'T2star_us', 'offset'], notes: [`T₂* = ${Math.abs(r.p[2]).toPrecision(3)} µs`] };
  },
  echo(x, y) {
    const f = (t, q) => q[3] + q[0] * Math.exp(-((t / q[1]) ** q[2]));
    const r = lm(f, x, y, [Math.max(...y) - Math.min(...y), Math.max(...x) / 2, 1.5, Math.min(...y)], { lower: [0, 1e-9, 0.5, -Infinity], upper: [Infinity, Infinity, 4, Infinity] });
    return { f, ...r, names: ['amplitude', 'T2_us', 'stretch_n', 'offset'], notes: [`T₂ = ${r.p[1].toPrecision(3)} µs, stretch exponent ${r.p[2].toFixed(2)}`] };
  },
  arrhenius(x, y) {        // x = 1000/T, y = resistance; fit ln(R T^-0.7) on the coldest third
    const idx = x.map((v, i) => i).sort((a, b) => x[b] - x[a]).slice(0, Math.max(5, Math.floor(x.length / 3)));
    const xs = idx.map(i => x[i]), ys = idx.map(i => Math.log(y[i] * (1000 / x[i]) ** -0.7));
    const r = lm((u, q) => q[0] * u + q[1], xs, ys, [1, 0]), f = (u, q) => Math.exp(q[0] * u + q[1]) * (1000 / u) ** 0.7;
    return { f, ...r, names: ['slope_K', 'intercept'], notes: [`activation energy ${(r.p[0] * 1000 * KB).toFixed(3)} ± ${(r.err[0] * 1000 * KB).toFixed(3)} eV (corrected)`], ea: r.p[0] * 1000 * KB, xfit: xs };
  },
  iv(x, y) {
    const f = (v, q) => (v < q[1] ? q[0] * (q[1] * v - v * v / 2) : q[0] * q[1] * q[1] / 2);
    const r = lm(f, x, y, [2 * Math.max(...y) / (Math.max(...x) / 2) ** 2, Math.max(...x) / 2]);
    return { f, ...r, names: ['k_mA_per_V2', 'overdrive_V'], notes: [`gain factor k = ${r.p[0].toPrecision(3)} mA/V², saturation onset ${r.p[1].toPrecision(3)} V`] };
  },
  g2(x, y) {
    const f = (t, q) => q[2] * (1 - (1 - q[0]) * Math.exp(-Math.abs(t) / q[1]));
    const r = lm(f, x, y, [0.3, 10, 1]);
    return { f, ...r, names: ['g2_zero', 'tau_ns', 'norm'], notes: [`g⁽²⁾(0) = ${r.p[0].toFixed(3)} → ${r.p[0] < 0.5 ? 'a single quantum emitter' : 'more than one emitter'}`] };
  },
};

function guessFreq(x, y) {        // brute-force DFT peak
  const n = x.length, T = x[n - 1] - x[0], m = y.reduce((s, v) => s + v, 0) / n; let best = 0, bf = 1 / T;
  for (let k = 1; k < n / 2; k++) { const fk = k / T; let re = 0, im = 0; for (let i = 0; i < n; i++) { const a = 2 * Math.PI * fk * (x[i] - x[0]); re += (y[i] - m) * Math.cos(a); im += (y[i] - m) * Math.sin(a); } const p = re * re + im * im; if (p > best) { best = p; bf = fk; } }
  return bf;
}

export function parseCSV(text) {
  const x = [], y = [];
  for (const line of text.split(/\r?\n/)) { const parts = line.split(/[,;\t ]+/).map(Number); if (parts.length >= 2 && Number.isFinite(parts[0]) && Number.isFinite(parts[1])) { x.push(parts[0]); y.push(parts[1]); } }
  if (x.length < 5) throw new Error('need at least five numeric rows with two columns');
  return { x, y };
}

export function fit(kind, x, y) { return MODELS[kind](x, y); }
