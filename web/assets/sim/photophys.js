// NV optical cycle, mirroring adamas.photophysics: seven-level model lumped to five levels, rates from [tetienne2012].
// Levels: 0 g0, 1 g±1, 2 e0, 3 e±1, 4 singlet. Deterministic rate equations for curves, and a stochastic
// quantum-jump trajectory (Gillespie) for the animation of one NV center. Unit-tested with node against the Python.
export const K = { r: 65.9, e0s: 11.0, e1s: 91.8, sg0: 4.87, sg1: 2.04 };   // 1/us

export function rates(beta) {   // list of [from, to, rate, kind]
  return [[0, 2, beta * K.r, 'pump'], [1, 3, beta * K.r, 'pump'], [2, 0, K.r, 'photon'], [3, 1, K.r, 'photon'],
    [2, 4, K.e0s, 'isc'], [3, 4, K.e1s, 'isc'], [4, 0, K.sg0, 'relax'], [4, 1, K.sg1, 'relax']];
}

export function evolve(beta, start, tEnd, dt = 1e-4) {      // returns { t, photonRate, pops }
  const R = rates(beta), p = [0, 0, 0, 0, 0]; p[start === '0' ? 0 : 1] = 1;
  const t = [], photon = [], pops = []; let every = Math.max(1, Math.round(tEnd / dt / 400));
  for (let s = 0, time = 0; time <= tEnd + 1e-12; s++, time += dt) {
    if (s % every === 0) { t.push(time); photon.push(K.r * (p[2] + p[3])); pops.push(p.slice()); }
    // RK2 (midpoint) step
    const d = q => { const o = [0, 0, 0, 0, 0]; for (const [a, b, k] of R) { o[a] -= k * q[a]; o[b] += k * q[a]; } return o; };
    const k1 = d(p), mid = p.map((v, i) => v + k1[i] * dt / 2), k2 = d(mid); for (let i = 0; i < 5; i++) p[i] += k2[i] * dt;
  }
  return { t, photonRate: photon, pops };
}

export function contrast(beta = 1, windowUs = 0.3) {
  const a = evolve(beta, '0', windowUs), b = evolve(beta, '1', windowUs), I = x => x.photonRate.reduce((s, v, i) => i ? s + (v + x.photonRate[i - 1]) / 2 * (x.t[i] - x.t[i - 1]) : 0, 0);
  return 1 - I(b) / I(a);
}

export function trajectory(beta, start, tEnd, rng = Math.random) {   // list of jumps [{t, from, to, kind}]
  const R = rates(beta), out = []; let s = start === '0' ? 0 : 1, t = 0;
  while (t < tEnd) {
    const out_ = R.filter(r => r[0] === s), tot = out_.reduce((a, r) => a + r[2], 0);
    t += -Math.log(1 - rng()) / tot; if (t > tEnd) break;
    let u = rng() * tot, pick = out_[0]; for (const r of out_) { if ((u -= r[2]) <= 0) { pick = r; break; } }
    out.push({ t, from: s, to: pick[1], kind: pick[3] }); s = pick[1];
  }
  return out;
}
