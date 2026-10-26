// Live uncertainty analysis for the Confidence page, mirroring adamas.uncertainty: Latin-hypercube Monte Carlo and
// one-at-a-time tornado swings. Power: SiC/diamond loss ratio = sqrt(R_SiC C_SiC / (R_D C_D)) at the area optimum, with
// R C proportional to (T/300)^alpha / (mu Ec^2), and the bulk boron-doped diamond drift divided by its ionized fraction
// (adamas.converter.ron_temperature_factor, audit G6). Quantum: runtime from the circuit-level resource model (resource.js).
import { estimate } from './resource.js';
import { freeCarriers, EPS0_F_CM, Q } from './action.js';

export const ALPHA = { sic: 2.4, diamond: 2.8 };                        // lattice-mobility exponents, adamas.converter
export const BORON_EA = 0.37, BV = 1200;                                  // eV [collins1971]; design blocking voltage, V
export const driftDoping = (epsR, ecMV, bv = BV) => EPS0_F_CM * epsR * (ecMV * 1e6) ** 2 / (2 * Q * bv);
export const ionizedFraction = (epsR, ecMV, tK = 300, bv = BV) => { const n = driftDoping(epsR, ecMV, bv); return freeCarriers(BORON_EA, n, tK) / n; };
export const ronFactorDiamond = (tK, bv = BV, alpha = ALPHA.diamond, epsR = 5.7, ecMV = 10) => (tK / 300) ** alpha / ionizedFraction(epsR, ecMV, tK, bv);
export const powerRatioAt = (p, tK) => {
  const dia = p['Diamond hole mobility'] * p['Diamond critical field'] ** 2 * ionizedFraction(p['Diamond permittivity'], p['Diamond critical field'], tK) / (tK / 300) ** ALPHA.diamond;
  const sic = p['SiC electron mobility'] * p['SiC critical field'] ** 2 / (tK / 300) ** ALPHA.sic;
  return Math.sqrt(dia / sic);
};
export const powerRatio = p => powerRatioAt(p, 300);          // one argument, so .map(powerRatio) is safe
export const powerRatioHot = p => powerRatioAt(p, 523);
export const RSA_STEPS = 8 * 3.6e9 / 27;                                  // calibrated to [gidney2021]: d = 27, 1 us cycle, 8 h
export const quantumYears = (p, table, job = [6000, RSA_STEPS]) => {
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
