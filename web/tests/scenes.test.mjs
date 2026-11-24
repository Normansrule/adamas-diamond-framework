// Bloch-sphere scenes (web/assets/sim/blochscenes.js): physical sanity of every frame and the key end states.
import { test } from 'node:test';
import assert from 'node:assert';
import { readFileSync } from 'node:fs';
import * as B from '../assets/sim/bloch.js';
import { SCENES, DEVICE_SCENE, DEVICE_EXTRA, STEP_SCENE } from '../assets/sim/blochscenes.js';
const G = JSON.parse(readFileSync(new URL('./bloch_golden.json', import.meta.url)));
const D = { t1_us: G.t1_us, t2_us: G.t2_us, thermal_z: G.thermal_z, reset_z: G.reset_z };
const len = r => Math.hypot(...r);

test('every frame of every scene stays inside the Bloch ball and has a label', () => {
  for (const [k, f] of Object.entries(SCENES)) { const s = f(D);
    assert.ok(s.frames.length > 10 && s.caption && s.title && s.status === 'simulated', k);
    for (const fr of s.frames) { assert.ok(len(fr.r) <= 1 + 1e-9, `${k} ${fr.r}`); assert.ok(fr.label, k); for (const v of fr.spins || []) assert.ok(len(v) <= 1 + 1e-9); } }
});
test('Rabi: 100 ns at 5 MHz is a pi pulse, and the resting frame shows it', () => { const s = SCENES.rabi(D); assert.ok(Math.abs(s.frames[s.rest].r[2] + 1) < 1e-9); });
test('ODMR: the arrow reaches the bottom only on resonance', () => {
  const f = SCENES.odmr(D).frames, mid = f[30], edge = f[0];
  assert.ok(Math.abs(B.pMinus1(mid.r) - 1) < 1e-9); assert.ok(B.pMinus1(edge.r) < 0.1);
});
test('Echo refocuses what Ramsey loses', () => {
  const f = SCENES.echo(D).frames;     // 5 steps x 30 frames: after the first wait (frame 60) and after the second (frame 120)
  assert.ok(len(f[120].r) > len(f[60].r) + 0.2, `${len(f[60].r)} -> ${len(f[120].r)}`);
});
test('Relaxation: the equator arrow shrinks (T2), the |1> arrow climbs to the center (T1); reset ends at the photophysics value', () => {
  const f = SCENES.relax(D).frames, k = f.findIndex((x, j) => j > 0 && x.newTrail);
  assert.ok(k > 0 && len(f[k - 1].r) < 0.06 && f[k].r[2] === -1 && len(f.at(-1).r) < 0.1 && f.at(-1).r[2] > -0.06);
  assert.ok(Math.abs(SCENES.reset(D).frames.at(-1).r[2] - G.reset_z) < 1e-12);
});
test('Gates: |0> -> H S T X matches the gate images', () => {
  let r = [0, 0, 1]; for (const g of ['H', 'S', 'T', 'X']) r = B.applyGate(r, g);
  SCENES.gates(D).frames.at(-1).r.forEach((x, i) => assert.ok(Math.abs(x - r[i]) < 1e-9));
});
test('Entanglement: a Bell pair leaves each arrow at the center', () => {
  const f = SCENES.entangle(D).frames; assert.ok(len(f[0].r) > 0.999 && len(f.at(-1).r) < 1e-9);
});
test('every mapped device and step names a scene that exists', () => {
  for (const v of [...Object.values(DEVICE_SCENE), ...Object.values(DEVICE_EXTRA), ...Object.values(STEP_SCENE)]) assert.ok(SCENES[v], v);
});
test('Composite scene: BB1 ends much closer to |1> than the plain pulse', () => {
  const f = SCENES.composite(D).frames, k = f.findIndex((x, j) => j > 0 && x.newTrail);
  assert.ok(f[k - 1].r[2] > -0.97 && f.at(-1).r[2] < -0.995, `${f[k - 1].r[2]} ${f.at(-1).r[2]}`);
});
