// Bloch-sphere twin (web/assets/sim/bloch.js) against adamas.bloch (web/tests/bloch_golden.json, written by
// adamas.bloch.write_golden via `adamas build docs`).
import { test } from 'node:test';
import assert from 'node:assert';
import { readFileSync } from 'node:fs';
import * as B from '../assets/sim/bloch.js';
const G = JSON.parse(readFileSync(new URL('./bloch_golden.json', import.meta.url)));
const close = (a, b, tol = 1e-9) => Math.abs(a - b) <= tol;
const key = p => ({ rabiMHz: p.rabi_mhz ?? 0, detuningMHz: p.detuning_mhz ?? 0, phase: p.phase ?? 0, t1Us: p.t1_us ?? Infinity, t2Us: p.t2_us ?? Infinity, zEq: p.z_eq ?? 0, pumpPerUs: p.pump_per_us ?? 0, zPump: p.z_pump ?? 1 });

test('Bloch equations: exact solution matches Python', () => {
  for (const c of G.evolve) { const r = B.evolve(c.r0, c.t, key(c.p)); r.forEach((x, i) => assert.ok(close(x, c.r[i]), `${JSON.stringify(c.p)} ${i}: ${x} vs ${c.r[i]}`)); }
});
test('trajectory steps land on the exact solution', () => {
  const c = G.evolve[3], tr = B.trajectory(c.r0, c.t, 50, key(c.p));
  tr.at(-1).forEach((x, i) => assert.ok(close(x, c.r[i], 1e-8)));
});
test('gates: axes, angles and images match the matrices', () => {
  for (const [g, v] of Object.entries(G.gates)) {
    assert.ok(close(B.GATES[g].angle, v.angle), `${g} angle`); B.GATES[g].axis.forEach((x, i) => assert.ok(close(x, v.axis[i]), `${g} axis`));
    const ins = [[0, 0, 1], [1, 0, 0], [0, 1, 0], [0.2, -0.3, 0.5]];
    ins.forEach((r, k) => B.applyGate(r, g).forEach((x, i) => assert.ok(close(x, v.images[k][i]), `${g} image ${k}`)));
  }
});
test('entanglement shrinks the arrow: reduced Bloch vector and concurrence', () => {
  for (const [t, r, c] of G.entangled) {
    B.reducedBloch(t).forEach((x, i) => assert.ok(close(x, r[i]), `t=${t}`)); assert.ok(close(B.concurrence(t), c), `C t=${t}`);
    const rr = B.reducedBloch(t); assert.ok(close(rr[2] ** 2 + B.concurrence(t) ** 2, 1));
  }
});
test('projection noise and the pump rate match Python', () => { assert.equal(B.PUMP_PER_US, G.pump_per_us); for (const [p, n, sd] of G.noise) assert.ok(close(B.projectionNoise(p, n), sd)); });
test('ensemble with T2: the echo decays as exp(-tau/T2), the light pumps to zPump', () => {
  for (const tau of [1, 3, 8]) {
    const p = { rabiMHz: 2000, detuningMHz: 0, t2starUs: 0, t1Us: Infinity, t2Us: 4, n: 1 };   // near-instant pulses
    assert.ok(close(B.sweep(p, 'echo', [tau])[0], (1 - Math.exp(-tau / 4)) / 2, 2e-4), `tau=${tau}`);
  }
  const p = { rabiMHz: 5, t2starUs: 0, t1Us: 6000, t2Us: 1800, n: 3, pumpPerUs: 0.5, zPump: G.reset_z };
  const f = B.run(p, [{ op: 'x', angle: Math.PI }, { op: 'light', t: 40 }], 10);
  assert.ok(Math.abs(f.at(-1).m[2] - G.reset_z) < 1e-3, `${f.at(-1).m[2]}`);
});
test('ideal gates in a sequence: H then S from |0> ends on +y', () => {
  const f = B.run({ rabiMHz: 5, t2starUs: 0, t1Us: 0, n: 2 }, [{ op: 'gate', name: 'H' }, { op: 'gate', name: 'S' }], 8);
  [0, 1, 0].forEach((x, i) => assert.ok(close(f.at(-1).m[i], x, 1e-12))); assert.equal(f.at(-1).time, 0);
});
test('shots: the fraction stays within 5 projection-noise widths', () => {
  const n = 4000, k = B.shots(0.3, n); assert.ok(Math.abs(k / n - 0.3) < 5 * B.projectionNoise(0.3, n));
});
