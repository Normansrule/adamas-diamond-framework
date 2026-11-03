// Quantum Device Library: the browser coupler model against Python (web/tests/qdl_golden.json, written by adamas build docs).
import { test } from 'node:test';
import assert from 'node:assert';
import { readFileSync } from 'node:fs';
import * as Q from '../assets/sim/qdl.js';
const G = JSON.parse(readFileSync(new URL('./qdl_golden.json', import.meta.url)));
const close = (a, b, rel = 1e-9) => Math.abs(a - b) <= rel * Math.abs(b);

test('dipolar coupling, gate time and coherence bound match adamas.coupling', () => {
  for (const [r, nu, t, f] of G.rows) {
    assert.ok(close(Q.couplingKHz(r, G.dipolar_mhz_nm3), nu), `nu at ${r} nm`);
    assert.ok(close(Q.gateTimeUs(r, G.dipolar_mhz_nm3), t), `t at ${r} nm`);
    assert.ok(close(Q.fidelityBound(r, G.t2_ms, G.dipolar_mhz_nm3), f), `F at ${r} nm`);
  }
});
test('largest spacing for a target fidelity matches adamas.qdl.r_max_nm', () => {
  assert.ok(close(Q.rMaxNm(0.99, G.t2_ms, G.dipolar_mhz_nm3), G.r_max_099));
  assert.ok(close(Q.rMaxNm(0.9, G.t2_ms, G.dipolar_mhz_nm3), G.r_max_09));
});
