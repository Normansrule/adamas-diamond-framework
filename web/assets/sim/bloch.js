// Two-level NV spin (ms = 0, ms = -1) as an ensemble of Bloch vectors. Pure module, no DOM; unit-tested with node.
// Driven rotation about (Omega, 0, delta) in the rotating frame [rabi1937] [jelezko2004a]; free precession at the detuning;
// T2* from a Gaussian spread of static detunings, refocused by a pi pulse [hahn1950]; T1 and T2 by the exact Bloch equations
// (v0.54.0; before, T1 relaxed toward ms = 0), and green light pumping toward ms = 0.
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
  for (let i = 0; i < (p.n || 64); i++) spins.push({ v: [0, 0, 1], d: (p.detuningMHz || 0) + sigma * gaussian(rng), a: 1 });
  if (p.ampSpread > 0) { const r2 = mulberry32(8); for (const s of spins) s.a = 1 + p.ampSpread * gaussian(r2); }   // drive strength varies spin to spin (v0.55.0)
  return spins;
}

// v0.54.0: when T1, T2 or green light is set, every spin follows the exact Bloch equations (evolve, below) with its own
// detuning, so relaxation goes to the thermal z (about 0 at room temperature) in the dark and to zPump under light.
const relaxing = p => (p.t1Us > 0 && Number.isFinite(p.t1Us)) || (p.t2Us > 0 && Number.isFinite(p.t2Us));
const bp = (p, s, extra) => ({ detuningMHz: s.d, t1Us: p.t1Us > 0 ? p.t1Us : Infinity, t2Us: p.t2Us > 0 ? p.t2Us : Infinity, zEq: p.zEq || 0, ...extra });

export function pulse(spins, p, axisName, angle) {  // angle in radians; duration angle / (2 pi Omega)
  // axisName: 'x', 'y', or a drive phase in radians (composite pulses). The length is set by the nominal Omega; a spin whose
  // drive is a times stronger turns a times as far (amplitude error).
  const om = p.rabiMHz, t = Math.abs(angle) / (2 * Math.PI * om), phi = typeof axisName === 'number' ? axisName : axisName === 'y' ? Math.PI / 2 : 0;
  const ph = phi + (angle < 0 ? Math.PI : 0);         // a negative angle is the same pulse with its phase shifted by pi
  if (relaxing(p)) { for (const s of spins) s.v = evolve(s.v, t, bp(p, s, { rabiMHz: om * (s.a ?? 1), phase: ph })); return t; }
  for (const s of spins) {
    const oa = om * (s.a ?? 1), w = Math.hypot(oa, s.d), ax = [oa * Math.cos(ph) / w, oa * Math.sin(ph) / w, s.d / w];
    s.v = rotate(s.v, ax, 2 * Math.PI * w * t);
  }
  return t;
}

export function wait(spins, p, tUs, light = false) {
  if (relaxing(p) || light) { for (const s of spins) s.v = evolve(s.v, tUs, bp(p, s, light ? { pumpPerUs: p.pumpPerUs || PUMP_PER_US, zPump: p.zPump ?? 1 } : {})); return tUs; }
  for (const s of spins) s.v = rotate(s.v, [0, 0, 1], 2 * Math.PI * s.d * tUs);
  return tUs;
}
export const PUMP_PER_US = 0.5;      // illustrative optical pumping rate (per microsecond) for the green-light op

// An ideal gate (no duration, no error): a turn of every spin by `frac` of the gate's rotation [nielsen2010].
export function gate(spins, name, frac = 1) { for (const s of spins) s.v = applyGate(s.v, name, frac); return 0; }

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
      if (step.op === 'wait' || step.op === 'light') time += wait(spins, p, step.t / framesPerStep, step.op === 'light');
      else if (step.op === 'gate') time += gate(spins, step.name, 1 / framesPerStep);
      else time += pulse(spins, p, step.op === 'p' ? step.phase : step.op, step.angle / framesPerStep);
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
export function generator({ rabiMHz = 0, detuningMHz = 0, phase = 0, t1Us = Infinity, t2Us = Infinity, zEq = 0, pumpPerUs = 0, zPump = 1 } = {}) {
  const w = [rabiMHz * Math.cos(phase), rabiMHz * Math.sin(phase), detuningMHz].map(x => 2 * Math.PI * x), g1 = rate(t1Us), g2 = rate(t2Us), gp = Math.max(0, pumpPerUs);
  return [[-g2 - gp, -w[2], w[1], 0], [w[2], -g2 - gp, -w[0], 0], [-w[1], w[0], -g1 - gp, g1 * zEq + gp * zPump], [0, 0, 0, 0]];
}
function mul4(a, b) {                                // 4 x 4 product on flat arrays (row major)
  const c = new Float64Array(16);
  for (let i = 0; i < 4; i++) for (let k = 0; k < 4; k++) { const x = a[4 * i + k]; if (x) for (let j = 0; j < 4; j++) c[4 * i + j] += x * b[4 * k + j]; }
  return c;
}
function expmFlat(a) {                                // scaling and squaring of a Taylor series
  let nrm = 0; for (let i = 0; i < 4; i++) nrm = Math.max(nrm, Math.abs(a[4 * i]) + Math.abs(a[4 * i + 1]) + Math.abs(a[4 * i + 2]) + Math.abs(a[4 * i + 3]));
  const sq = Math.max(0, Math.ceil(Math.log2(nrm / 0.25)) + 1), sc = 1 / 2 ** sq, b = a.map(x => x * sc);
  let e = new Float64Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]), t = e.slice();
  for (let k = 1; k <= 12; k++) { t = mul4(t, b); for (let i = 0; i < 16; i++) { t[i] /= k; e[i] += t[i]; } }
  for (let k = 0; k < sq; k++) e = mul4(e, e);
  return e;
}
const CACHE = new Map();
export function expm4(A) { const e = expmFlat(Float64Array.from(A.flat())); return [0, 1, 2, 3].map(i => Array.from(e.subarray(4 * i, 4 * i + 4))); }
export function evolve(r0, tUs, p) {
  const { rabiMHz = 0 } = p || {};
  if (!rabiMHz) {                                     // no drive: exact closed form (free precession, decay, relaxation)
    const { detuningMHz = 0, t1Us = Infinity, t2Us = Infinity, zEq = 0, pumpPerUs = 0, zPump = 1 } = p || {};
    const g1 = rate(t1Us) + Math.max(0, pumpPerUs), g2 = rate(t2Us) + Math.max(0, pumpPerUs), zInf = g1 ? (rate(t1Us) * zEq + Math.max(0, pumpPerUs) * zPump) / g1 : 0;
    const a = 2 * Math.PI * detuningMHz * tUs, c = Math.cos(a), s = Math.sin(a), k2 = Math.exp(-g2 * tUs), k1 = Math.exp(-g1 * tUs);
    return [(r0[0] * c - r0[1] * s) * k2, (r0[0] * s + r0[1] * c) * k2, g1 ? zInf + (r0[2] - zInf) * k1 : r0[2]];
  }
  const key = `${rabiMHz}|${p.detuningMHz}|${p.phase}|${p.t1Us}|${p.t2Us}|${p.zEq}|${p.pumpPerUs}|${p.zPump}|${tUs}`;
  let e = CACHE.get(key);                             // ensembles reuse the same pulse on the same detunings: compute once
  if (!e) { if (CACHE.size > 50000) CACHE.clear(); e = expmFlat(Float64Array.from(generator(p).flat().map(x => x * tUs))); CACHE.set(key, e); }
  const v = [r0[0], r0[1], r0[2], 1];
  return [0, 1, 2].map(i => e[4 * i] * v[0] + e[4 * i + 1] * v[1] + e[4 * i + 2] * v[2] + e[4 * i + 3]);
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
// Ideal projective shots: how many of n land on m_s = -1, and the projection noise sqrt(p (1 - p) / n) [itano1993].
export function shots(p1, n, rng = mulberry32(11)) { let k = 0; for (let i = 0; i < n; i++) k += rng() < p1; return k; }
export const projectionNoise = (p1, n) => Math.sqrt(Math.max(0, p1 * (1 - p1)) / n);

// ---- v0.55.0: composite pulses. BB1 [wimperis1994]: theta, then pi, 2 pi, pi at phases phi1, 3 phi1, phi1, phi1 = arccos(-theta / 4 pi).
export const bb1Phase = theta => Math.acos(-theta / (4 * Math.PI));
export function bb1Sequence(theta, phase = 0) { const p1 = bb1Phase(theta);
  return [{ op: 'p', angle: theta, phase }, { op: 'p', angle: Math.PI, phase: phase + p1 }, { op: 'p', angle: 2 * Math.PI, phase: phase + 3 * p1 }, { op: 'p', angle: Math.PI, phase: phase + p1 }]; }
// One spin's Bloch vector after a sequence, with amplitude error e and detuning ratio f = delta / Omega (twin of adamas.bloch).
export function sequenceImage(r, seq, e = 0, f = 0) {
  for (const st of seq) { const ax = [(1 + e) * Math.cos(st.phase), (1 + e) * Math.sin(st.phase), f], n = Math.hypot(...ax);
    r = rotate(r, ax.map(x => x / n), st.angle * n); }
  return r;
}
