// Telling two NV centers apart inside one laser spot, mirroring adamas.addressing (checked against
// web/tests/loop_golden.json). Airy focus [born1999]; exact spin-1 lines per NV axis (action.js) [dolde2013];
// gradient shift gamma_e G dx [grinolds2011]; off-resonant crosstalk Omega^2 / (Omega^2 + Delta^2) [rabi1937].
import { odmrLines, GAMMA, NV_AXES } from './action.js';

export { NV_AXES };
// Bessel J1 by its power series (fine for the |v| < 15 used here) and the Airy intensity [2 J1(v) / v]^2
export function besselJ1(x) { let term = x / 2, sum = term; for (let k = 1; k < 60; k++) { term *= -(x * x / 4) / (k * (k + 1)); sum += term; if (Math.abs(term) < 1e-17) break; } return sum; }
export function airy(rNm, lambdaNm = 532, na = 0.95) { const v = Math.max(1e-12, 2 * Math.PI * na * rNm / lambdaNm); return (2 * besselJ1(v) / v) ** 2; }
export function spotFwhm(lambdaNm = 532, na = 0.95) {
  let lo = 0, hi = lambdaNm / na;
  for (let i = 0; i < 80; i++) { const mid = (lo + hi) / 2; if (airy(mid, lambdaNm, na) > 0.5) lo = mid; else hi = mid; }
  return 2 * (lo + hi) / 2;
}
export function fieldVector(bMt, thDeg, phDeg) { const t = thDeg * Math.PI / 180, p = phDeg * Math.PI / 180; return [bMt * Math.sin(t) * Math.cos(p), bMt * Math.sin(t) * Math.sin(p), bMt * Math.cos(t)]; }
export function linesOnAxis(bMt, thDeg, phDeg, axis) {
  const B = fieldVector(bMt, thDeg, phDeg), n = Math.hypot(...axis), a = axis.map(x => x / n);
  const par = B[0] * a[0] + B[1] * a[1] + B[2] * a[2], perp = Math.hypot(B[0] - par * a[0], B[1] - par * a[1], B[2] - par * a[2]);
  const b = Math.hypot(par, perp); if (b < 1e-15) return odmrLines(0, 0);
  return odmrLines(b, Math.atan2(perp, par) * 180 / Math.PI);
}
export function spectralSeparation(bMt, thDeg, phDeg, axisA = NV_AXES[0], axisB = NV_AXES[1]) {
  const la = linesOnAxis(bMt, thDeg, phDeg, axisA), lb = linesOnAxis(bMt, thDeg, phDeg, axisB);
  return Math.min(...la.flatMap(x => lb.map(y => Math.abs(x - y))));
}
export const gradientShift = (gGPerNm, dxNm) => GAMMA * gGPerNm * 0.1 * dxNm;          // 1 G = 0.1 mT
export const crosstalk = (rabi, det) => rabi * rabi / (rabi * rabi + det * det);
export const linewidth = t2sUs => 1 / (Math.PI * t2sUs);
export const maxRabi = (det, eps = 0.01) => det * Math.sqrt(eps / (1 - eps));
export function verdict(sep, t2s, rabi, eps = 0.01) {
  const lw = linewidth(t2s), xt = crosstalk(rabi, sep);
  return { linewidth: lw, crosstalk: xt, resolved: sep > lw, selective: sep > lw && xt <= eps, piNs: 500 / rabi, maxRabi: maxRabi(sep, eps) };
}
// Rabi probability of a spin detuned by `det` under a drive `rabi`, after time t (used to animate both spins)
export const rabiP = (t, rabi, det) => { const w = Math.hypot(rabi, det); return w ? (rabi / w) ** 2 * Math.sin(Math.PI * w * t) ** 2 : 0; };
