// Bloch-sphere twin (web/assets/sim/bloch.js) against adamas.bloch (web/tests/bloch_golden.json, written by
// adamas.bloch.write_golden via `adamas build docs`).
import { test } from 'node:test';
import assert from 'node:assert';
import { readFileSync } from 'node:fs';
import * as B from '../assets/sim/bloch.js';
const G = JSON.parse(readFileSync(new URL('./bloch_golden.json', import.meta.url)));
const close = (a, b, tol = 1e-9) => Math.abs(a - b) <= tol;
const key = p => ({ rabiMHz: p.rabi_mhz ?? 0, detuningMHz: p.detuning_mhz ?? 0, phase: p.phase ?? 0, t1Us: p.t1_us ?? Infinity, t2Us: p.t2_us ?? Infinity, zEq: p.z_eq ?? 0 });

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
