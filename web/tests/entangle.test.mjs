// Entanglement Lab closed forms against adamas.entangle density-matrix values (web/tests/entangle_golden.json,
// written by adamas.entangle.write_golden via `adamas build docs`).
import { test } from 'node:test';
import assert from 'node:assert';
import { readFileSync } from 'node:fs';
import * as EN from '../assets/sim/entangle.js';
const G = JSON.parse(readFileSync(new URL('./entangle_golden.json', import.meta.url)));
const close = (a, b, rel = 1e-9, abs = 1e-12) => Math.abs(a - b) <= Math.max(abs, rel * Math.abs(b));

test('joint probabilities and Bob\'s marginal match the density-matrix calculation', () => {
  for (const [v, a, b, P] of G.joint) {
    const J = EN.joint(v, a, b);
    for (const k of [0, 1]) for (const l of [0, 1]) assert.ok(close(J[k][l], P[k][l]), `v=${v} a=${a} b=${b} ${k}${l}`);
    assert.ok(close(EN.bobP0(v, a, b), 0.5), 'Bob sees 50/50 whatever Alice does');
  }
});
test('teleportation fidelity with and without the two classical bits', () => {
  for (const [v, w, wo] of G.teleport) { assert.ok(close(EN.teleportFidelity(v, true), w), `with bits v=${v}`); assert.ok(close(EN.teleportFidelity(v, false), wo), `without v=${v}`); }
});
test('CHSH value, bounds, and light time', () => {
  for (const [v, s] of G.chsh) assert.ok(close(EN.chsh(v), s), `chsh v=${v}`);
  assert.ok(close(EN.wernerThreshold(), 1 / Math.SQRT2));
  for (const [km, ms] of G.light_ms) assert.ok(close(EN.lightMs(km), ms), `light ${km} km`);
});
test('sampled rounds: Bob\'s outcome frequency does not depend on Alice\'s setting', () => {
  let s = 12345; const rnd = () => { s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };   // mulberry32
  const n = 40000, f = a => { let z = 0; for (let i = 0; i < n; i++) z += EN.sample(1, a, 0, rnd)[1] === 0; return z / n; };
  for (const a of [0, Math.PI / 2]) assert.ok(Math.abs(f(a) - 0.5) < 4 * Math.sqrt(0.25 / n), `a=${a}`);
});
