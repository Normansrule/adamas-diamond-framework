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
  echo: tau => [{ op: 'x', angle: Math.PI / 2 }, { op: 'wait', t: tau / 2 }, { op: 'x', angle: Math.PI }, { op: 'wait', t: tau / 2 }, { op: 'x', angle: Math.PI / 2 }],
};

export function sweep(p, kind, taus) {             // final P(ms=-1) versus tau for a sequence family
  return taus.map(tau => {
    const spins = makeEnsemble(p);
    for (const st of SEQUENCES[kind](tau)) st.op === 'wait' ? wait(spins, p, st.t) : pulse(spins, p, st.op, st.angle);
    return P_MINUS1(spins);
  });
}
