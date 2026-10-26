// Build-program phase P1 in the browser: one simulated thermometer run of the A1 kit, mirroring
// adamas.build_program.p1_thermometer (A1 noise model of adamas.experiments; fits with fit.js, the Data Lab's
// mirror of adamas.fitting). The random numbers differ from Python's, so the tests compare statistics, not draws.
import { MODELS } from './fit.js';
import { mulberry32 } from './bloch.js';

export const A1 = { contrast: 0.012, fwhm: 6.0, noise: 0.0012, d300: 2870, dddt: -74.2e-3, dddtSigma: 0.7e-3 };   // MHz, MHz/K [acosta2010]
export function gauss(rng) { let u = 0; while (!u) u = rng(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * rng()); }

// Zero-field ensemble spectrum: eight lines (four axes, two transitions) on top of each other, total depth 2 x contrast
export function spectrum(f, dMHz, rng, p = A1) {
  const hw = p.fwhm / 2;
  return f.map(x => 1 - 2 * p.contrast * hw * hw / ((x - dMHz) ** 2 + hw * hw) + p.noise * gauss(rng));
}

export function thermometerRun(seed, temps = [20, 27.5, 35, 42.5, 50], p = A1) {   // inside the 280-330 K of [acosta2010]
  const rng = mulberry32(seed), f = []; for (let x = 2840; x <= 2900 + 1e-9; x += 0.25) f.push(x);
  const T = temps.map(t => t + 273.15), c = [], e = [];
  for (const t of T) {
    const r = MODELS.odmr(f, spectrum(f, p.d300 + p.dddt * (t - 300), rng, p));
    const k = r.p.length === 4 ? 0 : r.p.slice(1).reduce((best, _, i, a) => (i % 3 === 0 && a[i] > a[best] ? i : best), 0);   // deepest line
    c.push(r.p[2 + k]); e.push(r.err[2 + k]);
  }
  const w = e.map(x => 1 / (x * x)), tm = T.reduce((s, t) => s + t, 0) / T.length;
  const S0 = w.reduce((s, v) => s + v, 0), S1 = w.reduce((s, v, i) => s + v * (T[i] - tm), 0), S2 = w.reduce((s, v, i) => s + v * (T[i] - tm) ** 2, 0);
  const Sy = w.reduce((s, v, i) => s + v * c[i], 0), Sxy = w.reduce((s, v, i) => s + v * (T[i] - tm) * c[i], 0), det = S0 * S2 - S1 * S1;
  const slope = (S0 * Sxy - S1 * Sy) / det, slopeErr = Math.sqrt(S0 / det), tol = 2 * Math.hypot(slopeErr, p.dddtSigma);
  return { slope: slope * 1e3, slopeErr: slopeErr * 1e3, tol: tol * 1e3, pass: Math.abs(slope - p.dddt) <= tol, centers: c, errs: e, temps };
}
