// Browser side of the equation-in-the-loop panels. Metadata (equations, symbols, units, ranges, assumptions, sources)
// comes from adamas.loop.PANELS through data/site.json; this file holds only the arithmetic, which the node tests
// compare with Python golden values (web/tests/loop_golden.json). Every assumption id in the registry has a checker here:
// it returns { ok, note } when the lab state can test the assumption, or { assumed: true, note } when it cannot.
import { rabiP, ramseyP0 } from './sim/action.js';
import * as PH from './sim/photophys.js';
import * as UN from './sim/uncertainty.js';
import * as AD from './sim/addressing.js';
import * as CR from './sim/crystal.js';
import { odmrLines, GAMMA } from './sim/action.js';
import * as HT from './sim/heat.js';
import * as FT from './sim/fet.js';
import * as RS from './sim/resource.js';
import * as GB from './sim/gatebias.js';

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
      twolevel: () => ({ assumed: true, note: 'the drive is resonant with one line only' }),
    },
  },
  ramsey: {
    defaults: { de: 1, tau: 1, t2s: 2, Om: 5 },
    f: s => ramseyP0(s.tau, s.de, s.t2s),
    sub: s => `= ½[1 + cos(2π · ${num(n(s.de, 2))} MHz · ${num(n(s.tau, 2))} µs) · e<sup>−(${num(n(s.tau, 2))}/${num(n(s.t2s, 2))})²</sup>]<br>= ½[1 + ${n(Math.cos(2 * Math.PI * s.de * s.tau))} × ${n(Math.exp(-((s.tau / s.t2s) ** 2)))}]`,
    checks: {
      hard: s => ({ ok: 1 / (4 * (s.Om || 5)) < 0.1 * Math.max(s.tau, 1e-9), note: `π/2 pulse ${n(1000 / (4 * (s.Om || 5)), 0)} ns` }),
      gauss: () => ({ assumed: true, note: 'the lab draws static Gaussian detunings' }),
    },
  },
  echo: {
    defaults: { de: 1, eps: 0, t2s: 2, Om: 5 },
    f: s => 0.5 * (1 - Math.cos(2 * Math.PI * s.de * s.eps) * Math.exp(-((s.eps / s.t2s) ** 2))),
    sub: s => `= ½[1 − cos(2π · ${num(n(s.de, 2))} MHz · ${num(n(s.eps, 2))} µs) · e<sup>−(${num(n(s.eps, 2))}/${num(n(s.t2s, 2))})²</sup>]<br>${Math.abs(s.eps) < 1e-9 ? 'ε = 0: every static detuning cancels, whatever τ is' : `= ½[1 − ${n(Math.cos(2 * Math.PI * s.de * s.eps))} × ${n(Math.exp(-((s.eps / s.t2s) ** 2)))}]`}`,
    checks: {
      static: () => ({ assumed: true, note: 'T₂ decay (hundreds of µs) not included' }),
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
      zerofield: () => ({ assumed: true, note: 'no field, so ±1 are degenerate' }),
      perfectpi: () => ({ assumed: true, note: 'an imperfect π pulse lowers C further' }),
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
      uncomp: () => ({ assumed: true, note: 'any donor compensation raises R_on further' }),
      nofield: () => ({ assumed: true, note: 'Poole–Frenkel ionization ignored' }),
      sicceil: s => ({ ok: s.T <= 523, note: s.T > 523 ? 'above silicon carbide\'s package ceiling' : 'silicon carbide still allowed here' }),
    },
  },
  crosstalk: {
    defaults: { Om: 2, Dl: 30, t2s: 1 },
    f: s => AD.crosstalk(s.Om, s.Dl),
    sub: s => `= ${num(n(s.Om, 2))}² / (${num(n(s.Om, 2))}² + ${num(n(s.Dl, 2))}²) = ${n(s.Om ** 2, 3)} / ${n(s.Om ** 2 + s.Dl ** 2, 2)}<br>line width 2√ln2/(π · ${num(n(s.t2s, 1))} µs) = ${n(AD.linewidth(s.t2s), 3)} MHz; π pulse ${n(500 / s.Om, 0)} ns`,
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
      fit: () => ({ assumed: true, note: 'joins 7.7 MV/cm at 10⁴ to 1.5 MV/cm at 2×10⁷' }),
      range: s => ({ ok: s.D >= 1e4 && s.D <= 1e8, note: s.D < 1e4 ? 'held at 7.7 MV/cm below 10⁴' : s.D > 1e8 ? 'extrapolated, floored at 1 MV/cm' : 'inside the fitted range' }),
    },
  },
  odmr: {
    defaults: { B: 3, th: 40, D: 2870 },
    parts: s => { const bpar = s.B * Math.abs(Math.cos(s.th * Math.PI / 180)), bperp = s.B * Math.abs(Math.sin(s.th * Math.PI / 180));
      return { a: GAMMA * bpar, m: (GAMMA * bperp) ** 2 / (2 * s.D), sh: 3 * (GAMMA * bperp) ** 2 / (2 * s.D) }; },
    lines: s => { const { a, m, sh } = MODELS.odmr.parts(s), h = Math.hypot(a, m); return [s.D + sh - h, s.D + sh + h]; },
    f: s => { const [a, b] = MODELS.odmr.lines(s); return b - a; },
    sub: s => { const [lo, hi] = MODELS.odmr.lines(s), { a, m, sh } = MODELS.odmr.parts(s);
      return `γₑB cos θ = ${n(GAMMA, 2)} × ${num(n(s.B, 2))} × |cos ${num(n(s.th, 1))}°| = ${n(a, 2)} MHz; mixing term (γₑB sin θ)²/2D = ${n(m, 3)} MHz; common shift ${n(sh, 3)} MHz<br>f₋ = ${n(lo, 2)} MHz, f₊ = ${n(hi, 2)} MHz`; },
    checks: {
      weak: s => { const ex = odmrLines(s.B, s.th), [a, b] = MODELS.odmr.lines(s), e = Math.max(Math.abs(ex[0] - a), Math.abs(ex[1] - b)), es = Math.abs((ex[1] - ex[0]) - (b - a));
        return { ok: e < 0.5 && es < 0.5, note: `exact diagonalization: lines differ by ${n(e, 3)} MHz, splitting by ${n(es, 3)} MHz` }; },
      strainfree: () => ({ assumed: true, note: 'strain splits the lines at B = 0 by 2E' }),
    },
  },
  heat: {
    defaults: { k: 22, rc: 3.52 * 0.509, L: 0.2 },
    derive: s => ({ al: s.k / s.rc }),
    f: s => 1e3 * HT.slowestModeTime(s.k, s.rc, s.L),
    sub: s => `α = ${num(n(s.k, 2))} / ${num(n(s.rc, 2))} = ${n(s.k / s.rc, 2)} cm²/s<br>τ = 4 × ${num(n(s.L, 2))}² / (π² × ${n(s.k / s.rc, 2)}) = ${n(1e3 * HT.slowestModeTime(s.k, s.rc, s.L), 2)} ms; silicon at the same L: ${n(1e3 * HT.slowestModeTime(1.5, 2.33 * 0.705, s.L), 1)} ms`,
    checks: {
      constk: () => ({ assumed: true, note: 'κ falls as the die heats; not modelled' }),
      settled: s => { if (!(s.tlab >= 0)) return { assumed: true, note: 'no lab time yet' }; const r = s.tlab / MODELS.heat.f(s); return { ok: r >= 3, note: `lab time = ${n(r, 1)} τ` }; },
    },
  },
  ring: {
    defaults: { mu: 150, V: 10, ve: 1.5, vd: -2, r: 8, sim: NaN },
    est: s => FT.ringEstimate(s.mu, s.ve, s.vd, s.r, s.V),
    derive: s => { const e = MODELS.ring.est(s); return { N: 5, C: e.c * 1e15, IL: e.iLoad * 1e3, ID: e.iDrv * 1e3 }; },
    f: s => MODELS.ring.est(s).period * 1e9,
    sub: s => { const e = MODELS.ring.est(s);
      return `C = ${num(n(e.c * 1e15, 1))} fF, I<sub>L</sub> = ${num(n(e.iLoad * 1e3, 3))} mA, I<sub>D</sub> = ${num(n(e.iDrv * 1e3, 3))} mA<br>= 5 × (${n(e.tRise * 1e9, 2)} + ${n(e.tFall * 1e9, 3)}) ns: ${e.tRise > e.tFall ? 'charging through the load' : 'discharging through the driver'} sets the period`; },
    checks: {
      vsim: s => { if (!Number.isFinite(s.sim)) return { ok: false, note: 'the simulated ring does not oscillate here' };
        const r = MODELS.ring.f(s) / s.sim; return { ok: Math.abs(r - 1) <= 0.5, note: `estimate ÷ simulation = ${n(r, 2)}` }; },
      longch: () => ({ assumed: true, note: 'the lab uses 2 µm gates; velocity saturation is not modelled' }),
    },
  },
  logical: {
    defaults: { p: 0.06, d: 5, pth: 0.103, A: 0.1 },
    f: s => s.A * (s.p / s.pth) ** ((s.d + 1) / 2),
    sub: s => `= ${num(n(s.A, 2))} × (${num(n(s.p, 3))} / ${num(n(s.pth, 3))})<sup>${n((s.d + 1) / 2, 0)}</sup> = ${n(s.A, 2)} × ${n(s.p / s.pth, 3)}<sup>${n((s.d + 1) / 2, 0)}</sup><br>going from d = ${n(s.d, 0)} to ${n(s.d + 2, 0)} multiplies p<sub>L</sub> by ${n(s.p / s.pth, 3)}`,
    checks: {
      below: s => ({ ok: s.p < s.pth, note: s.p < s.pth ? 'bigger codes help' : 'above threshold: bigger codes make it worse' }),
      lowp: s => ({ ok: s.p <= 0.5 * s.pth, note: `p / p_th = ${n(s.p / s.pth, 2)}` }),
      codecap: () => ({ assumed: true, note: 'with noisy syndromes the threshold falls to about 2.9 % [wang2003], and near 1 % at circuit level [fowler2012]' }),
    },
  },
  budget: {
    defaults: { n: 1000, st: 1.07e9, d: 27, A: 0.03, lam: 2.14 },
    f: s => RS.failureProbability(s.n, s.st, s.d, s.A, s.lam),
    sub: s => `= ${num(sci(s.n))} × ${num(sci(s.st))} × ${num(n(s.d, 0))} × ${num(n(s.A, 3))} × ${num(n(s.lam, 2))}<sup>−${n((s.d + 1) / 2, 0)}</sup><br>one more step of distance (d + 2) divides it by Λ = ${n(s.lam, 2)}`,
    checks: {
      below: s => ({ ok: s.lam > 1, note: s.lam > 1 ? `Λ = ${n(s.lam, 2)}` : 'no distance helps' }),
      union: s => ({ ok: RS.failureProbability(s.n, s.st, s.d, s.A, s.lam) <= 0.1, note: 'needs P_fail ≪ 1' }),
      link: () => ({ assumed: true, note: 'see docs/STATUS.md' }),
    },
  },
  bias: {
    defaults: { eta: 100, h: 0.002 },
    f: s => GB.outputBias('cnot', s.eta, s.h)[1],
    sub: s => { const w = GB.outputDistribution('cnot', s.eta, s.h).perQubit[1], t = w.X + w.Y + w.Z;
      return `target leaves with P<sub>Z</sub> = ${n(w.Z / t, 4)}, P<sub>X</sub> = ${n(w.X / t, 4)}, P<sub>Y</sub> = ${n(w.Y / t, 4)} (of its error events)<br>short-Hadamard limit 1/(2 × ${num(n(s.eta, 1))} + 1) = ${n(1 / (2 * s.eta + 1), 4)}; a CZ alone would keep η = ${n(s.eta, 1)}`; },
    checks: {
      first: () => ({ assumed: true, note: 'two errors in one gate ignored' }),
      endseg: () => ({ assumed: true, note: 'X partway through the CZ would also spread' }),
      shorth: s => ({ ok: s.h <= 0.05, note: `η_out × (2η + 1) = ${n(GB.outputBias('cnot', s.eta, s.h)[1] * (2 * s.eta + 1), 2)}` }),
    },
  },
};
