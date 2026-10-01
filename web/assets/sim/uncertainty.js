// Live uncertainty analysis for the Confidence page, mirroring adamas.uncertainty: Latin-hypercube Monte Carlo and
// one-at-a-time tornado swings. Power: SiC/diamond loss ratio = sqrt(mu_D Ec_D^2 / (mu_S Ec_S^2)) at the area optimum
// (permittivity and blocking voltage cancel). Quantum: runtime from the circuit-level resource model (resource.js).
import { estimate } from './resource.js';

export const powerRatio = p => Math.sqrt(p['Diamond hole mobility'] * p['Diamond critical field'] ** 2 / (p['SiC electron mobility'] * p['SiC critical field'] ** 2));
export const quantumYears = (p, table, job = [6000, 3e9]) => {
  const e = estimate(table, { nLogical: job[0], steps: job[1], tReadUs: p['Readout time'], t2MemMs: p['Nuclear memory T₂'], gateUs: p['Two-qubit gate time'],
    prepUs: p['Ancilla preparation'], overhead: p['Layout overhead'] });
  return e ? e.runtimeHours / 8766 : Infinity;
};

export function rng(seed = 11) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

export function lhs(params, n, r = rng()) {        // params: {name: [base, lo, hi, scale, ...]}
  const out = Array.from({ length: n }, () => ({}));
  for (const [k, [base, lo, hi, scale]] of Object.entries(params)) {
    const perm = [...Array(n).keys()]; for (let i = n - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [perm[i], perm[j]] = [perm[j], perm[i]]; }
    for (let i = 0; i < n; i++) { const u = (perm[i] + r()) / n;
      out[i][k] = scale === 'choice' ? (u < 0.5 ? lo : hi) : scale === 'log' ? Math.exp(Math.log(lo) + u * (Math.log(hi) - Math.log(lo))) : lo + u * (hi - lo); }
  }
  return out;
}

export const baseline = params => Object.fromEntries(Object.entries(params).map(([k, v]) => [k, v[0]]));

export function tornado(params, f) {
  const b = baseline(params), y0 = f(b);
  return Object.entries(params).map(([k, [, lo, hi]]) => { const yl = f({ ...b, [k]: lo }), yh = f({ ...b, [k]: hi }); return { name: k, lo, hi, yl, yh, swing: Math.abs(yh - yl), y0 }; })
    .sort((a, c) => c.swing - a.swing);
}

export function percentile(sorted, q) { const i = (sorted.length - 1) * q, a = Math.floor(i), b = Math.ceil(i); return sorted[a] + (sorted[b] - sorted[a]) * (i - a); }
