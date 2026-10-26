// Physics for the Equations in Action page. Pure functions, no DOM. Each mirrors a function of the Python package and is
// checked against it by web/tests/sim.test.mjs using web/tests/action_golden.json (written by adamas.action.write_golden).
export const H = 6.62607015e-34, KB = 1.380649e-23, KB_EV = 8.617333262e-5, Q = 1.602176634e-19, M0 = 9.1093837015e-31;
export const EPS0_F_CM = 8.8541878128e-14, MU_B = 9.2740100783e-24, G_E = 2.0028;
export const GAMMA = G_E * MU_B / H * 1e-9;           // MHz per mT, 28.03 [doherty2013]
export const D_MHZ = 2870;                            // zero-field splitting at 300 K [doherty2013]
export const DIPOLAR = 52.066006;                        // MHz nm^3, mu0 gamma^2 hbar / (4 pi) / (2 pi) [neumann2010natphys]
export const NV_AXES = [[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]].map(a => a.map(x => x / Math.sqrt(3)));
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));

// ---- 1. ODMR: exact spin-1 eigenvalues of D Sz^2 + gamma B.S with B in the x-z plane (adamas.nv) ----
export function eigSym3(m) {                          // closed-form eigenvalues of a real symmetric 3x3, ascending
  const [[a, b, c], [, d, e], [, , f]] = m, p1 = b * b + c * c + e * e, q = (a + d + f) / 3;
  if (p1 < 1e-18) return [a, d, f].sort((x, y) => x - y);
  const p2 = (a - q) ** 2 + (d - q) ** 2 + (f - q) ** 2 + 2 * p1, p = Math.sqrt(p2 / 6);
  const B = [[a - q, b, c], [b, d - q, e], [c, e, f - q]].map(r => r.map(x => x / p));
  const det = B[0][0] * (B[1][1] * B[2][2] - B[1][2] * B[2][1]) - B[0][1] * (B[1][0] * B[2][2] - B[1][2] * B[2][0]) + B[0][2] * (B[1][0] * B[2][1] - B[1][1] * B[2][0]);
  const phi = Math.acos(clamp(det / 2, -1, 1)) / 3, e1 = q + 2 * p * Math.cos(phi), e3 = q + 2 * p * Math.cos(phi + 2 * Math.PI / 3);
  return [e3, 3 * q - e1 - e3, e1].sort((x, y) => x - y);
}
export function odmrLines(bMt, thetaDeg) {           // the two transitions out of the lowest level, MHz
  const th = thetaDeg * Math.PI / 180, bz = GAMMA * bMt * Math.cos(th), bx = GAMMA * bMt * Math.sin(th) / Math.SQRT2;
  const ev = eigSym3([[D_MHZ + bz, bx, 0], [bx, 0, bx], [0, bx, D_MHZ - bz]]);
  return [ev[1] - ev[0], ev[2] - ev[0]];
}
export const lorentzDips = (f, lines, fwhm, c) => 1 - lines.reduce((s, l) => s + c * (fwhm / 2) ** 2 / ((f - l) ** 2 + (fwhm / 2) ** 2), 0);

// ---- 2. dipole field on the axis of a small magnet ----
export const dipoleMt = (mAm2, rCm) => 1e-7 * 2 * mAm2 / (rCm / 100) ** 3 * 1e3;
export const splitMHz = bMt => 2 * GAMMA * bMt;

// ---- 3. heat spreaders (adamas.experiments expected 'heat_spreaders') ----
export const SPREADERS = { Diamond: { k: 20, rc: 3.52 * 0.509 }, Copper: { k: 4.0, rc: 8.96 * 0.385 }, Aluminium: { k: 2.37, rc: 2.70 * 0.897 }, Silicon: { k: 1.5, rc: 2.33 * 0.705 } };
export const rth = k => 1 / (4 * k * 0.1) + 3.0 + 1.5;            // K/W: spreading (1 mm radius) + paste + sink [carslaw1959]
export const tauHeat = k => 12 + 30 / k;                          // s
export const heatRise = (P, k, t) => P * rth(k) * (1 - Math.exp(-t / tauHeat(k)));
export function plate(n = 40) { return { n, T: new Float32Array(n * n) }; }
export function plateStep(g, alpha, power, dtS, hCm = 0.025) {     // explicit diffusion on a 1 cm plate, cold edges, heater at center
  const n = g.n, T = g.T, sub = Math.max(1, Math.ceil(dtS * alpha / (0.2 * hCm * hCm))), dt = dtS / sub, r = alpha * dt / (hCm * hCm), c = n >> 1;
  const N = new Float32Array(n * n);
  for (let s = 0; s < sub; s++) {
    for (let i = 1; i < n - 1; i++) for (let j = 1; j < n - 1; j++) { const k = i * n + j; N[k] = T[k] + r * (T[k - 1] + T[k + 1] + T[k - n] + T[k + n] - 4 * T[k]); }
    for (let i = c - 1; i <= c; i++) for (let j = c - 1; j <= c; j++) N[i * n + j] += power * dt;
    T.set(N);
  }
  return g;
}

// ---- 4-6. Rabi, Ramsey, echo (adamas.nv.rabi, ramsey, hahn_echo) ----
export function rabiP(t, om, de = 0) { const w = Math.hypot(om, de); return w ? (om / w) ** 2 * Math.sin(Math.PI * w * t) ** 2 : 0; }
export const ramseyP0 = (tau, de, t2s, p = 2) => 0.5 * (1 + Math.cos(2 * Math.PI * de * tau) * Math.exp(-((tau / t2s) ** p)));
export const echoC = (tau, t2, p = 3) => Math.exp(-((tau / t2) ** p));
export function rotate(v, ax, ang) {                  // Rodrigues rotation of vector v about unit-normalized axis ax
  const n = Math.hypot(...ax) || 1, k = ax.map(x => x / n), c = Math.cos(ang), s = Math.sin(ang), d = k[0] * v[0] + k[1] * v[1] + k[2] * v[2];
  const x = [k[1] * v[2] - k[2] * v[1], k[2] * v[0] - k[0] * v[2], k[0] * v[1] - k[1] * v[0]];
  return v.map((vi, i) => vi * c + x[i] * s + k[i] * d * (1 - c));
}
export function rabiVector(t, om, de) {               // Bloch vector after a pulse of length t (us) from |0> = +z
  return rotate([0, 0, 1], [om, 0, de], 2 * Math.PI * Math.hypot(om, de) * t);
}
export function gaussianDetunings(n, de, t2s, rng = mulberry(7)) {   // quasi-static spread, sigma = sqrt(2) / (2 pi T2*)
  const sig = Math.SQRT2 / (2 * Math.PI * t2s), out = [];
  for (let i = 0; i < n; i++) { const u = (i + 0.5) / n; out.push(de + sig * Math.SQRT2 * erfinv(2 * u - 1)); }
  return out.sort(() => rng() - 0.5);
}
export function erfinv(x) { const a = 0.147, l = Math.log(1 - x * x), t = 2 / (Math.PI * a) + l / 2; return Math.sign(x) * Math.sqrt(Math.sqrt(t * t - l / a) - t); }
export function mulberry(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

// ---- 7. vector magnetometry ----
export function bVector(b, thDeg, phDeg) { const t = thDeg * Math.PI / 180, p = phDeg * Math.PI / 180; return [b * Math.sin(t) * Math.cos(p), b * Math.sin(t) * Math.sin(p), b * Math.cos(t)]; }
export const projections = B => NV_AXES.map(n => Math.abs(n[0] * B[0] + n[1] * B[1] + n[2] * B[2]));
export const splittings = B => projections(B).map(x => 2 * GAMMA * x);
export const magnitudeFromSplittings = s => Math.sqrt(0.75 * s.reduce((a, x) => a + (x / (2 * GAMMA)) ** 2, 0));

// ---- 8. incomplete ionization (adamas.doping.free_carriers_cm3) ----
export const dosCm3 = (mDos, T) => 2 * (2 * Math.PI * mDos * M0 * KB * T / H ** 2) ** 1.5 * 1e-6;
export function freeCarriers(ea, na, T, nd = 0, g = 4, mDos = 0.9) {
  const k = dosCm3(mDos, T) / g * Math.exp(-ea / (KB_EV * T)), b = nd + k, c = -k * (na - nd);
  return Math.max(0, (-b + Math.sqrt(b * b - 4 * c)) / 2);
}
export const holeMobility = T => 1500 * (T / 300) ** -2.2;        // lattice-limited, as in the B3 expected data
export const resistivity = (p, T) => 1 / (Q * Math.max(p, 1e-30) * holeMobility(T));

// ---- 9. photon antibunching ----
export const g2 = (tau, rho, tau1) => 1 - rho * rho * Math.exp(-Math.abs(tau) / tau1);

// ---- 10. square-law diamond p-FET (adamas.logic.Fet) ----
export function fetK(mu, toxNm = 30, epsOx = 9, w = 100, l = 2) { return mu * epsOx * EPS0_F_CM / (toxNm * 1e-7) * w / l; }
export function fetI(vgs, vds, mu, vth = 1.5) { const k = fetK(mu), v = vgs - vth; if (v <= 0 || vds <= 0) return 0; return vds < v ? k * (v * vds - vds * vds / 2) : k * v * v / 2; }

// ---- 11. dipolar two-qubit gate budget (adamas.gate_budget.GateBudget, single quantum, echo, theta = 90 deg) ----
export const couplingKHz = r => DIPOLAR * 1e3 / r ** 3;
export const gateTimeUs = r => 1e3 / (2 * couplingKHz(r));
export function bellFidelity(r, t2, q) { const w = Math.exp(-((gateTimeUs(r) / t2) ** 3)), fc = (1 + w) ** 2 / 4; return q * q * fc + (1 - q * q) / 4; }

// ---- 12. wafer yield (adamas.wafer) ----
export const diesPerWafer = (d, a) => Math.max(0, Math.floor(Math.PI * (d / 2) ** 2 / a - Math.PI * d / Math.sqrt(2 * a)));
export const poissonY = (a, d0) => Math.exp(-a * 1e-2 * d0);
export const murphyY = (a, d0) => { const x = a * 1e-2 * d0; return x === 0 ? 1 : (-Math.expm1(-x) / x) ** 2; };   // expm1 keeps precision at tiny A·D0
export const goodDies = (d, a, d0) => diesPerWafer(d, a) * murphyY(a, d0);

// ---- 13. unipolar power-device limit (adamas.power.ron_sp_mohm_cm2) ----
export function ronSp(m, vb) { const ec = m.ec_mv_cm * 1e6; return 4 * vb * vb / (m.eps_r * EPS0_F_CM * m.mu * ec ** 3) * 1e3; }  // mOhm cm^2
export const driftUm = (m, vb) => 2 * vb / (m.ec_mv_cm * 1e6) * 1e4;

// ---- 14. surface code (adamas.qec) ----
export const logicalError = (p, d, pth = 1e-2) => 0.1 * (p / pth) ** ((d + 1) / 2);
export const surfaceQubits = d => 2 * d * d - 1;
