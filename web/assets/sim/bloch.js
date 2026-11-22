// Two-level NV spin (ms = 0, ms = -1) as an ensemble of Bloch vectors. Pure module, no DOM; unit-tested with node.
// Driven rotation about (Omega, 0, delta) in the rotating frame [rabi1937] [jelezko2004a]; free precession at the detuning;
// T2* from a Gaussian spread of static detunings, refocused by a pi pulse [hahn1950]; T1 relaxation toward ms = 0.
// Fluorescence: ms = 0 bright, ms = -1 about 30% dimmer [gruber1997] [doherty2013].

export function rotate(v, axis, angle) {            // Rodrigues rotation of vector v about unit axis
  const [x, y, z] = v, [a, b, c] = axis, cs = Math.cos(angle), sn = Math.sin(angle), d = a * x + b * y + c * z;
  return [x * cs + (b * z - c * y) * sn + a * d * (1 - cs),
          y * cs + (c * x - a * z) * sn + b * d * (1 - cs),
          z * cs + (a * y - b * x) * sn + c * d * (1 - cs)];
}

function gaussian(rng) { let u = 0, v = 0; while (u === 0) u = rng(); while (v === 0) v = rng(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
export function mulberry32(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

// params: { rabiMHz, detuningMHz, t2starUs, t1Us, n }
export function makeEnsemble(p) {
  const rng = mulberry32(7), sigma = p.t2starUs > 0 ? Math.SQRT2 / (2 * Math.PI * p.t2starUs) : 0;   // MHz, exp(-(t/T2*)^2)
  const spins = [];
  for (let i = 0; i < (p.n || 64); i++) spins.push({ v: [0, 0, 1], d: (p.detuningMHz || 0) + sigma * gaussian(rng) });
  return spins;
}

export function pulse(spins, p, axisName, angle) {  // angle in radians; duration angle / (2 pi Omega)
  const om = p.rabiMHz, t = Math.abs(angle) / (2 * Math.PI * om), phi = axisName === 'y' ? Math.PI / 2 : 0;
  for (const s of spins) {
    const w = Math.hypot(om, s.d), ax = [om * Math.cos(phi) / w, om * Math.sin(phi) / w, s.d / w];
    s.v = rotate(s.v, ax, Math.sign(angle) * 2 * Math.PI * w * t);
  }
  relax(spins, p, t);
  return t;
}

export function wait(spins, p, tUs) {
  for (const s of spins) s.v = rotate(s.v, [0, 0, 1], 2 * Math.PI * s.d * tUs);
  relax(spins, p, tUs);
  return tUs;
}

function relax(spins, p, t) {
  if (!p.t1Us || p.t1Us <= 0) return;
  const k = Math.exp(-t / p.t1Us);
  for (const s of spins) s.v = [s.v[0] * k, s.v[1] * k, 1 - (1 - s.v[2]) * k];
}

export function mean(spins) {
  const m = [0, 0, 0]; for (const s of spins) { m[0] += s.v[0]; m[1] += s.v[1]; m[2] += s.v[2]; }
  return m.map(x => x / spins.length);
}

export const P_MINUS1 = spins => (1 - mean(spins)[2]) / 2;                   // probability of ms = -1
export const fluorescence = (spins, contrast = 0.3) => 1 - contrast * P_MINUS1(spins);

// Run a sequence [{op:'x'|'y', angle}, {op:'wait', t}] and return per-step snapshots for animation.
export function run(p, seq, framesPerStep = 24) {
  const spins = makeEnsemble(p), frames = [];
  let time = 0;
  frames.push({ time, m: mean(spins), spins: spins.map(s => s.v.slice()) });
  for (const step of seq) {
    for (let k = 0; k < framesPerStep; k++) {
      if (step.op === 'wait') time += wait(spins, p, step.t / framesPerStep);
      else time += pulse(spins, p, step.op, step.angle / framesPerStep);
      frames.push({ time, m: mean(spins), spins: spins.map(s => s.v.slice()) });
    }
  }
  return frames;
}

export const SEQUENCES = {
  rabi: tau => [{ op: 'x', angle: tau }],
  ramsey: tau => [{ op: 'x', angle: Math.PI / 2 }, { op: 'wait', t: tau }, { op: 'x', angle: Math.PI / 2 }],
  // eps = tau2 - tau1: a mistimed pi pulse (0 for a centred echo); the result follows adamas.nv.echo_mistimed
  echo: (tau, eps = 0) => [{ op: 'x', angle: Math.PI / 2 }, { op: 'wait', t: Math.max(0, tau / 2 - eps / 2) }, { op: 'x', angle: Math.PI }, { op: 'wait', t: Math.max(0, tau / 2 + eps / 2) }, { op: 'x', angle: Math.PI / 2 }],
};

export function sweep(p, kind, taus, eps = 0) {    // final P(ms=-1) versus tau for a sequence family
  return taus.map(tau => {
    const spins = makeEnsemble(p);
    for (const st of SEQUENCES[kind](tau, Math.max(-tau, Math.min(tau, eps)))) st.op === 'wait' ? wait(spins, p, st.t) : pulse(spins, p, st.op, st.angle);
    return P_MINUS1(spins);
  });
}

// ---- v0.53.0: the twin of adamas.bloch (checked against web/tests/bloch_golden.json) ----
// Bloch equations [bloch1946]: dr/dt = 2 pi W x r - (x/T2, y/T2, (z - zEq)/T1), W = (Om cos phi, Om sin phi, delta), solved
// exactly with the matrix exponential of the 4 x 4 affine generator (scaling and squaring of a Taylor series).
const rate = t => (t > 0 && Number.isFinite(t)) ? 1 / t : 0;
export function generator({ rabiMHz = 0, detuningMHz = 0, phase = 0, t1Us = Infinity, t2Us = Infinity, zEq = 0 } = {}) {
  const w = [rabiMHz * Math.cos(phase), rabiMHz * Math.sin(phase), detuningMHz].map(x => 2 * Math.PI * x), g1 = rate(t1Us), g2 = rate(t2Us);
  return [[-g2, -w[2], w[1], 0], [w[2], -g2, -w[0], 0], [-w[1], w[0], -g1, g1 * zEq], [0, 0, 0, 0]];
}
const mm = (A, B) => A.map((r, i) => B[0].map((_, j) => r.reduce((s, a, k) => s + a * B[k][j], 0)));
export function expm4(A) {
  const nrm = Math.max(...A.map(r => r.reduce((s, x) => s + Math.abs(x), 0)));
  const sq = Math.max(0, Math.ceil(Math.log2(nrm / 0.25)) + 1), sc = 1 / 2 ** sq, B = A.map(r => r.map(x => x * sc));
  let E = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], T = E;
  for (let k = 1; k <= 20; k++) { T = mm(T, B).map(r => r.map(x => x / k)); E = E.map((r, i) => r.map((x, j) => x + T[i][j])); }
  for (let k = 0; k < sq; k++) E = mm(E, E);
  return E;
}
export function evolve(r0, tUs, p) {
  const E = expm4(generator(p).map(r => r.map(x => x * tUs))), v = [...r0, 1];
  return [0, 1, 2].map(i => E[i].reduce((s, a, k) => s + a * v[k], 0));
}
export function trajectory(r0, tUs, steps, p) {
  const E = expm4(generator(p).map(r => r.map(x => x * tUs / steps))), out = [r0.slice()];
  let v = [...r0, 1];
  for (let s = 0; s < steps; s++) { v = [0, 1, 2, 3].map(i => E[i].reduce((a, e, k) => a + e * v[k], 0)); out.push(v.slice(0, 3)); }
  return out;
}
// Gates are rotations [nielsen2010]: axis and angle of each single-qubit gate, up to a global phase.
const H2 = Math.SQRT1_2;
export const GATES = { X: { axis: [1, 0, 0], angle: Math.PI }, Y: { axis: [0, 1, 0], angle: Math.PI }, Z: { axis: [0, 0, 1], angle: Math.PI },
  H: { axis: [H2, 0, H2], angle: Math.PI }, S: { axis: [0, 0, 1], angle: Math.PI / 2 }, T: { axis: [0, 0, 1], angle: Math.PI / 4 } };
export const applyGate = (r, name, frac = 1) => rotate(r, GATES[name].axis, GATES[name].angle * frac);
// One qubit of cos t |00> + sin t |11>: r = (0, 0, cos 2t); concurrence |sin 2t| [wootters1998]; |r|^2 + C^2 = 1.
export const reducedBloch = t => [0, 0, Math.cos(2 * t)];
export const concurrence = t => Math.abs(Math.sin(2 * t));
export const purity = r => (1 + r[0] * r[0] + r[1] * r[1] + r[2] * r[2]) / 2;
export const pMinus1 = r => (1 - r[2]) / 2;
