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
test('composite pulses: plain and BB1 images match Python', () => {
  for (const c of G.composite) {
    assert.ok(close(B.bb1Phase(c.theta), c.bb1_phase));
    B.sequenceImage([0, 0, 1], [{ angle: c.theta, phase: 0 }], c.e, c.f).forEach((x, i) => assert.ok(close(x, c.plain[i]), `plain ${i}`));
    B.sequenceImage([0, 0, 1], B.bb1Sequence(c.theta), c.e, c.f).forEach((x, i) => assert.ok(close(x, c.bb1[i]), `bb1 ${i}`));
  }
});
test('the lab pulse() path (per-spin drive and detuning, with and without the Bloch-equation solver) matches sequenceImage', () => {
  for (const relax of [{}, { t1Us: 1e9, t2Us: 1e9 }]) for (const th of [Math.PI / 2, Math.PI]) {
    const spins = [{ v: [0, 0, 1], d: 0.5, a: 1.1 }], p = { rabiMHz: 5, ...relax };
    for (const st of B.bb1Sequence(th)) B.pulse(spins, p, st.phase, st.angle);
    const want = B.sequenceImage([0, 0, 1], B.bb1Sequence(th), 0.1, 0.1);
    spins[0].v.forEach((x, i) => assert.ok(Math.abs(x - want[i]) < 1e-6, `${JSON.stringify(relax)} θ=${th} ${i}: ${x} vs ${want[i]}`));
  }
});
test('ensemble with a drive spread: BB1 brings the mean much closer to |1> than a plain pi pulse', () => {
  const p = { rabiMHz: 5, t2starUs: 0, t1Us: 0, n: 60, ampSpread: 0.15 };
  const plain = B.run(p, [{ op: 'x', angle: Math.PI }], 4).at(-1).m[2], bb1 = B.run(p, B.bb1Sequence(Math.PI), 4).at(-1).m[2];
  assert.ok(plain > -0.97 && bb1 < -0.995, `${plain} ${bb1}`);
  const same = B.run({ ...p, ampSpread: 0 }, [{ op: 'x', angle: Math.PI }], 4).at(-1).m[2]; assert.ok(close(same, -1, 1e-9));
});
