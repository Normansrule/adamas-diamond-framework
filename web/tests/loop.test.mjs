// Equation-in-the-loop models and the v0.28 simulations against their Python twins (web/tests/loop_golden.json,
// written by adamas.loop.write_golden).
import { test } from 'node:test';
import assert from 'node:assert';
import { readFileSync } from 'node:fs';
import * as AD from '../assets/sim/addressing.js';
import * as GB from '../assets/sim/gatebias.js';
import * as CR from '../assets/sim/crystal.js';
import * as PH from '../assets/sim/photophys.js';
import * as UN from '../assets/sim/uncertainty.js';
import * as ACT from '../assets/sim/action.js';
import * as B from '../assets/sim/bloch.js';
import { MODELS } from '../assets/loop_models.js';
const G = JSON.parse(readFileSync(new URL('./loop_golden.json', import.meta.url)));
const close = (a, b, rel = 1e-6, abs = 1e-12) => Math.abs(a - b) <= Math.max(abs, rel * Math.abs(b));

test('qubit equations match adamas.nv (Rabi, Ramsey, mistimed echo)', () => {
  for (const [om, de, t, v] of G.rabi) assert.ok(close(ACT.rabiP(t, om, de), v), `rabi ${om} ${de} ${t}`);
  for (const [de, tau, t2s, v] of G.ramsey) assert.ok(close(ACT.ramseyP0(tau, de, t2s), v), `ramsey ${de} ${tau}`);
  for (const [de, e, t2s, v] of G.echo) assert.ok(close(MODELS.echo.f({ de, eps: e, t2s }), v), `echo ${de} ${e} ${t2s}`);
});
test('the ensemble echo on the Bloch sphere follows the mistimed-echo equation', () => {
  const p = { rabiMHz: 400, detuningMHz: 1.0, t2starUs: 1.0, t1Us: 0, n: 4000 };
  for (const e of [0, 0.4, -0.8]) {
    const ens = B.sweep(p, 'echo', [4], e)[0], eq = MODELS.echo.f({ de: 1.0, eps: e, t2s: 1.0 });
    assert.ok(Math.abs(ens - eq) < 0.04, `echo offset ${e}: ensemble ${ens} vs equation ${eq}`);
  }
});
test('photophysics: polarization and measured contrast match the Python rate model', () => {
  for (const [b, t, v] of G.polarization) assert.ok(close(PH.polarization(b, t), v, 2e-4), `P ${b} ${t}: ${PH.polarization(b, t)} vs ${v}`);
  for (const [b, w, t, v] of G.contrast) assert.ok(close(PH.measuredContrast(b, w, t), v, 3e-3), `C ${b} ${w} ${t}: ${PH.measuredContrast(b, w, t)} vs ${v}`);
});
test('hot switch: ionized fraction and R_on(T) factor match adamas.converter', () => {
  for (const [bv, t, f, fac] of G.hot) {
    assert.ok(close(UN.ionizedFraction(5.7, 10, t, bv), f, 1e-6), `f_ion ${bv} ${t}`);
    assert.ok(close(UN.ronFactorDiamond(t, bv), fac, 1e-6), `factor ${bv} ${t}`);
  }
});
test('crystal quality: E_c(D), strain, T2* and killer survival match', () => {
  for (const [D, ec, eps, t2, surv] of G.crystal) {
    assert.ok(close(CR.criticalField(D), ec)); assert.ok(close(CR.strain(D), eps)); assert.ok(close(CR.t2star(D), t2)); assert.ok(close(CR.killerSurvival(25, D, 1e-3), surv, 1e-6, 1e-300));
  }
});
test('addressing: Airy spot, lines per NV axis, gradient shift and crosstalk match adamas.addressing', () => {
  for (const [lam, na, v] of G.spot) assert.ok(close(AD.spotFwhm(lam, na), v, 1e-6), `spot ${lam} ${na}`);
  for (const [b, th, ph, k, [lo, hi]] of G.lines) { const [a, c] = AD.linesOnAxis(b, th, ph, AD.NV_AXES[k]); assert.ok(close(a, lo, 1e-9, 1e-6) && close(c, hi, 1e-9, 1e-6), `lines ${b} ${th} ${ph} ${k}: ${a},${c} vs ${lo},${hi}`); }
  for (const [g, dx, v] of G.gradient) assert.ok(close(AD.gradientShift(g, dx), v));
  for (const [om, dl, v] of G.crosstalk) assert.ok(close(AD.crosstalk(om, dl), v));
  assert.ok(AD.spectralSeparation(5, 0, 0) < 1e-6, 'a field along [001] gives every axis the same lines');
  assert.ok(AD.spectralSeparation(5, 54.7356, 45) > 50, 'a field along one axis separates it from the others');
});
test('gate bias: Pauli propagation and output distributions match adamas.gatebias (Stim-checked)', () => {
  for (const [q, p, res] of G.propagate) assert.deepEqual(GB.propagate({ [q]: p }, [['CZ', [0, 1]], ['H', [1]]]), { 0: res[0] ?? res['0'], 1: res[1] ?? res['1'] });
  for (const [k, eta, h, dist, spread] of G.bias) {
    const o = GB.outputDistribution(k, eta, h);
    for (const q of ['0', '1']) for (const P of 'XYZ') assert.ok(close(o.perQubit[q][P], dist[q][P], 1e-9, 1e-15), `${k} ${eta} ${h} q${q} ${P}`);
    assert.ok(close(o.spread, spread, 1e-9, 1e-15));
  }
  const cz = GB.outputBias('cz', 100), cx = GB.outputBias('cnot', 100);
  assert.ok(Math.abs(cz[0] - 100) < 1e-9 && Math.abs(cz[1] - 100) < 1e-9, 'CZ keeps the bias on both qubits');
  assert.ok(cx[1] < 0.02, 'the H-CZ-H CNOT turns the target\'s phase errors into bit flips');
});
test('every equation panel in the Python registry has a JavaScript model and a checker for each assumption', () => {
  const site = JSON.parse(readFileSync(new URL('./loop_registry.json', import.meta.url)));
  for (const [id, p] of Object.entries(site)) {
    assert.ok(MODELS[id], `no JS model for panel ${id}`);
    for (const a of p.assumptions) assert.ok(MODELS[id].checks && MODELS[id].checks[a.id], `panel ${id}: no checker for assumption ${a.id}`);
    for (const k of Object.keys(p.vars)) assert.ok(k in MODELS[id].defaults || p.vars[k].derived, `panel ${id}: no default for ${k}`);
  }
});
