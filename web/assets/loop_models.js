// Browser side of the equation-in-the-loop panels. Metadata (equations, symbols, units, ranges, assumptions, sources)
// comes from adamas.loop.PANELS through data/site.json; this file holds only the arithmetic, which the node tests
// compare with Python golden values (web/tests/loop_golden.json). Every assumption id in the registry has a checker here.
import { rabiP, ramseyP0 } from './sim/action.js';
import * as PH from './sim/photophys.js';
import * as UN from './sim/uncertainty.js';
import * as AD from './sim/addressing.js';
import * as CR from './sim/crystal.js';

const n = (x, d = 3) => (Number.isFinite(x) ? x.toFixed(d) : '∞');
const sci = x => { if (!Number.isFinite(x) || x === 0) return String(x); const e = Math.floor(Math.log10(Math.abs(x))), m = x / 10 ** e; return `${m.toFixed(2)}×10<sup>${e}</sup>`; };
const num = s => `<span class="n">${s}</span>`;

export const MODELS = {
  rabi: {
    defaults: { Om: 5, de: 0, t: 0.1, t2s: 2 },
    f: s => rabiP(s.t, s.Om, s.de),
    sub: s => { const w = Math.hypot(s.Om, s.de);
      return `= ${num(n(s.Om, 1))}² / (${num(n(s.Om, 1))}² + ${num(n(s.de, 2))}²) · sin²(π · ${num(n(w, 2))} MHz · ${num(n(s.t, 3))} µs)<br>= ${n((s.Om / w) ** 2)} · sin²(${n(Math.PI * w * s.t)} rad)`; },
    checks: {
      rwa: s => ({ ok: s.Om < 0.01 * 2870, note: `Ω/D = ${n(100 * s.Om / 2870, 2)} %` }),
      nodecay: s => ({ ok: !(s.t2s > 0) || s.t < 0.3 * s.t2s, note: s.t2s > 0 ? `t/T₂* = ${n(s.t / s.t2s, 2)}` : 'no dephasing set' }),
      twolevel: () => ({ ok: true, note: 'the drive is resonant with one line only' }),
    },
  },
  ramsey: {
    defaults: { de: 1, tau: 1, t2s: 2, Om: 5 },
    f: s => ramseyP0(s.tau, s.de, s.t2s),
    sub: s => `= ½[1 + cos(2π · ${num(n(s.de, 2))} MHz · ${num(n(s.tau, 2))} µs) · e<sup>−(${num(n(s.tau, 2))}/${num(n(s.t2s, 2))})²</sup>]<br>= ½[1 + ${n(Math.cos(2 * Math.PI * s.de * s.tau))} × ${n(Math.exp(-((s.tau / s.t2s) ** 2)))}]`,
    checks: {
      hard: s => ({ ok: 1 / (4 * (s.Om || 5)) < 0.1 * Math.max(s.tau, 1e-9), note: `π/2 pulse ${n(1000 / (4 * (s.Om || 5)), 0)} ns` }),
      gauss: () => ({ ok: true, note: 'the lab draws static Gaussian detunings' }),
    },
  },
  echo: {
    defaults: { de: 1, eps: 0, t2s: 2, Om: 5 },
    f: s => 0.5 * (1 - Math.cos(2 * Math.PI * s.de * s.eps) * Math.exp(-((s.eps / s.t2s) ** 2))),
    sub: s => `= ½[1 − cos(2π · ${num(n(s.de, 2))} MHz · ${num(n(s.eps, 2))} µs) · e<sup>−(${num(n(s.eps, 2))}/${num(n(s.t2s, 2))})²</sup>]<br>${Math.abs(s.eps) < 1e-9 ? 'ε = 0: every static detuning cancels, whatever τ is' : `= ½[1 − ${n(Math.cos(2 * Math.PI * s.de * s.eps))} × ${n(Math.exp(-((s.eps / s.t2s) ** 2)))}]`}`,
    checks: {
      static: () => ({ ok: true, note: 'T₂ decay (hundreds of µs) not included' }),
      hard: s => ({ ok: 1 / (2 * (s.Om || 5)) < 0.1, note: `π pulse ${n(500 / (s.Om || 5), 0)} ns` }),
    },
  },
  contrast: {
    defaults: { beta: 1, win: 0.3, tpol: 3 },
    derive: s => { const c = PH.counts(s.beta, s.win); return { ...c, P: PH.polarization(s.beta, s.tpol) }; },
    f: s => PH.measuredContrast(s.beta, s.win, s.tpol),
    sub: s => { const d = MODELS.contrast.derive(s);
      return `P = ${num(n(d.P))}, I₀ = ${num(n(d.i0, 2))}, I₁ = ${num(n(d.i1, 2))} photons per shot (rate model)<br>= 1 − (${n(d.P)} · ${n(d.i1, 2)} + ${n(1 - d.P)} · ${n(d.i0, 2)}) / (${n(d.P)} · ${n(d.i0, 2)} + ${n(1 - d.P)} · ${n(d.i1, 2)})`; },
    checks: {
      zerofield: () => ({ ok: true, note: 'no field, so ±1 are degenerate' }),
      perfectpi: () => ({ ok: true, note: 'an imperfect π pulse lowers C further' }),
      window: s => ({ ok: s.win <= 0.5, note: `window ${n(s.win * 1000, 0)} ns` }),
    },
    sweepSamples: 36,
  },
  hot_switch: {
    defaults: { T: 400, alpha: 2.8, bv: 1200 },
    derive: s => { const N = UN.driftDoping(5.7, 10, s.bv); return { N, fion: UN.ionizedFraction(5.7, 10, s.T, s.bv) }; },
    f: s => (s.T / 300) ** s.alpha / UN.ionizedFraction(5.7, 10, s.T, s.bv),
    sub: s => { const d = MODELS.hot_switch.derive(s);
      return `N = ${num(sci(d.N))} cm⁻³ (for ${s.bv} V), f<sub>ion</sub> = ${num(n(100 * d.fion, 2))} %<br>= (${num(n(s.T, 0))}/300)<sup>${n(s.alpha, 1)}</sup> / ${n(d.fion, 4)} = ${n((s.T / 300) ** s.alpha, 2)} / ${n(d.fion, 4)}`; },
    checks: {
      uncomp: () => ({ ok: true, note: 'any donor compensation raises R_on further' }),
      nofield: () => ({ ok: true, note: 'Poole–Frenkel ionization ignored' }),
      sicceil: s => ({ ok: s.T <= 523, note: s.T > 523 ? 'above silicon carbide\'s package ceiling' : 'silicon carbide still allowed here' }),
    },
  },
  crosstalk: {
    defaults: { Om: 2, Dl: 30, t2s: 1 },
    f: s => AD.crosstalk(s.Om, s.Dl),
    sub: s => `= ${num(n(s.Om, 2))}² / (${num(n(s.Om, 2))}² + ${num(n(s.Dl, 2))}²) = ${n(s.Om ** 2, 3)} / ${n(s.Om ** 2 + s.Dl ** 2, 2)}<br>line width 1/(π · ${num(n(s.t2s, 1))} µs) = ${n(AD.linewidth(s.t2s), 3)} MHz; π pulse ${n(500 / s.Om, 0)} ns`,
    checks: {
      resolved: s => ({ ok: s.Dl > AD.linewidth(s.t2s), note: `Δ / line width = ${n(s.Dl / AD.linewidth(s.t2s), 1)}` }),
      nohf: s => ({ ok: s.Dl > 3 * 2.147, note: s.Dl > 3 * 2.147 ? 'separation well above the triplet' : 'the ¹⁴N triplet blurs this separation' }),
    },
  },
  crystal: {
    defaults: { D: 2e7 },
    derive: s => ({ eps: CR.strain(s.D), t2: CR.t2star(s.D) }),
    f: s => CR.criticalField(s.D),
    sub: s => { const d = MODELS.crystal.derive(s);
      return `= 7.7 − 1.88 · log₁₀(${num(sci(s.D))} / 10⁴) = ${n(7.7 - 1.88 * Math.log10(Math.max(s.D, 1e4) / 1e4), 2)} → ${n(CR.criticalField(s.D), 2)} MV/cm<br>ε = ${num(sci(d.eps))}, T₂* ≤ ${num(n(d.t2, 3))} µs; figure of merit × ${n(CR.bfomRelative(s.D), 3)} of the 10 MV/cm value`; },
    checks: {
      fit: () => ({ ok: true, note: 'joins 7.7 MV/cm at 10⁴ to 1.5 MV/cm at 2×10⁷' }),
      range: s => ({ ok: s.D >= 1e4 && s.D <= 1e8, note: s.D < 1e4 ? 'held at 7.7 MV/cm below 10⁴' : s.D > 1e8 ? 'extrapolated, floored at 1 MV/cm' : 'inside the fitted range' }),
    },
  },
};
