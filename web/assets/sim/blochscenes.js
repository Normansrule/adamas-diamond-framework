// Bloch-sphere scenes shared by the Device Library, the Fab Journey and the Entanglement Lab (v0.53.0). Pure module, no DOM;
// every frame comes from bloch.js, the browser twin of adamas.bloch (checked against Python by web/tests/bloch.test.mjs).
// A frame is { r: [x, y, z], spins?: [[x, y, z], ...], pair?: [rA, rB], label: text }. North pole |0> = m_s = 0 (bright),
// south pole |1> = m_s = -1 [doherty2013]. Rates, pulse lengths and detunings below are illustrative unless a source is named.
import * as B from './bloch.js';

const R = v => v.map(x => Math.abs(x) < 1e-12 ? 0 : x);
const f2 = x => (Math.abs(x) < 0.005 ? 0 : x).toFixed(2);
export const describe = (r, down = 'P(mₛ = −1)') => `x ${f2(r[0])}, y ${f2(r[1])}, z ${f2(r[2])}; length ${f2(Math.hypot(...r))}; ${down} ${f2(B.pMinus1(r))}`;

function pulseFrames(r0, p, tUs, n, label) {
  return B.trajectory(r0, tUs, n, p).slice(1).map((r, k) => ({ r: R(r), label: label((k + 1) * tUs / n) }));
}
function ensembleFrames(p, seq, per, names) {     // B.run gives mean and spins per frame
  let i = 0; const steps = seq.flatMap((s, j) => Array(per).fill(names[j]));
  return B.run(p, seq, per).map(f => ({ r: R(f.m), spins: f.spins, label: i === 0 ? (i++, 'start: |0⟩') : steps[i++ - 1] }));
}

export const TURN = { X: 'π about x', Y: 'π about y', Z: 'π about z', H: 'π about (x + z)/√2', S: 'π/2 about z', T: 'π/4 about z' };

export const SCENES = {
  rabi: () => {
    const p = { rabiMHz: 5 };
    return { title: 'Rabi: the drive turns the arrow', status: 'simulated',
      frames: [{ r: [0, 0, 1], label: 'start: |0⟩, bright' }, ...pulseFrames([0, 0, 1], p, 0.2, 60, t => `resonant drive, ${(t * 1000).toFixed(0)} ns: turned ${(t * 2 * 5).toFixed(2)} π`)],
      rest: 30, caption: 'A resonant microwave pulse turns the arrow about x at the Rabi frequency (5 MHz here, illustrative): a π pulse in 100 ns moves |0⟩ to |1⟩, and the red glow dims by up to about 30 % [gruber1997]. Bloch equations [bloch1946] [rabi1937] [jelezko2004a].' };
  },
  odmr: () => {
    const Om = 1, frames = [];
    for (let k = 0; k <= 60; k++) { const de = -4 + 8 * k / 60, r = R(B.evolve([0, 0, 1], 1 / (2 * Om), { rabiMHz: Om, detuningMHz: de }));
      frames.push({ r, label: `detuning ${de.toFixed(2)} MHz: P(mₛ = −1) after one π-long pulse ${f2(B.pMinus1(r))}` }); }
    return { title: 'Finding the dip: only on resonance does the arrow reach the bottom', status: 'simulated', trailOnly: true, frames,
      caption: 'Sweeping the microwave frequency: each dot is where one π-long pulse leaves the arrow at that detuning. Off resonance the turning axis tilts toward z, so the arrow never reaches |1⟩ and the glow barely dims; at the dip (zero detuning) it turns all the way. This is the pulsed picture; in continuous-wave ODMR (optically detected magnetic resonance) laser and microwave act at once, so the dip is much shallower (0.5 to 3 % in step A1.5). Rabi frequency 1 MHz, illustrative [rabi1937].' };
  },
  ramsey: () => {
    const p = { rabiMHz: 5, detuningMHz: 0.5, t2starUs: 1.2, t1Us: 0, n: 24 };
    return { title: 'Ramsey: free precession measures a field', status: 'simulated',
      frames: ensembleFrames(p, B.SEQUENCES.ramsey(1.5), 30, ['π/2 pulse', 'free precession at the detuning; spins fan out (T₂*)', 'π/2 pulse: the phase becomes a population']),
      caption: 'A π/2 pulse lays the arrow on the equator; during free time it turns at the detuning, which a magnetic field, a temperature or a rotation shifts. A second π/2 pulse turns that angle into brightness. Each faint arrow is one spin of an ensemble with its own detuning, so the mean shrinks with T₂* (1.2 µs, illustrative) [ramsey1950].' };
  },
  echo: () => {
    const p = { rabiMHz: 5, detuningMHz: 0.5, t2starUs: 0.8, t1Us: 0, n: 24 };
    return { title: 'Spin echo: a π pulse refocuses the fan', status: 'simulated',
      frames: ensembleFrames(p, B.SEQUENCES.echo(2), 30, ['π/2 pulse', 'spins fan out', 'π pulse flips the fan', 'spins fan back in', 'π/2 pulse']),
      caption: 'The π pulse in the middle flips the fan so the fast spins now trail; after the same time they all meet again and the lost length comes back. Static spread is undone; only noise that changes during the sequence (T₂) is not [hahn1950].' };
  },
  gates: () => {
    let r = [0, 0, 1]; const frames = [{ r, label: 'start: |0⟩' }];
    for (const g of ['H', 'S', 'T', 'X']) {
      for (let k = 1; k <= 24; k++) frames.push({ r: R(B.applyGate(r, g, k / 24)), label: `${g} gate: a turn of ${TURN[g]}` });
      r = frames.at(-1).r;
    }
    return { title: 'Gates are turns of the arrow', status: 'simulated', interactive: 'gates', frames,
      caption: 'Every single-qubit gate is, up to a global phase, a rotation of the arrow about some axis [nielsen2010]. On a nitrogen-vacancy (NV) spin, X and Y are microwave pulses of the right phase, and Z, S and T are free precession or a phase shift of later pulses.' };
  },
  relax: d => {
    const t1Us = d.t1_us, t2Us = d.t2_us, zEq = d.thermal_z, p = { detuningMHz: 0.001, t1Us, t2Us, zEq }, q = { t1Us, t2Us, zEq };
    const a = pulseFrames([1, 0, 0], p, 3 * t2Us, 180, t => `${(t / 1000).toFixed(2)} ms on the equator: length ${f2(Math.hypot(...B.evolve([1, 0, 0], t, p)))}`);
    const b = pulseFrames([0, 0, -1], q, 3 * t1Us, 90, t => `${(t / 1000).toFixed(1)} ms from |1⟩: z ${f2(B.evolve([0, 0, -1], t, q)[2])}`);
    return { title: 'Relaxation: T₂ shrinks the arrow, T₁ brings it to the center', status: 'simulated',
      frames: [{ r: [1, 0, 0], label: 'start: on the equator after a π/2 pulse about y', newTrail: true }, ...a, { r: [0, 0, -1], label: 'next: start at |1⟩ (mₛ = −1)', newTrail: true }, ...b],
      caption: `Room-temperature NV (nitrogen-vacancy) spin: Hahn-echo T₂ = ${t2Us / 1000} ms [balasubramanian2009] shrinks an arrow on the equator, then T₁ = ${t1Us / 1000} ms [jarmola2012] brings an arrow from |1⟩ to the center. The decay shown is echo-limited, as if each spin's static detuning were refocused; an arrow precessing freely decays faster, with T₂*. The slow 1 kHz turn (illustrative) only makes the shrinking visible. In the dark the arrow ends at the center, not the top: at 300 K the thermal z is only ${zEq.toExponential(1)} (adamas.bloch.thermal_z). Bloch equations [bloch1946]; time compressed.` };
  },
  reset: d => {
    const z = d.reset_z, frames = [];
    for (let k = 0; k <= 40; k++) frames.push({ r: [0, 0, z * k / 40], label: k ? `green light on: polarizing, z ${f2(z * k / 40)}` : 'start: unpolarized, at the center' });
    return { title: 'Optical reset: green light pumps the arrow up', status: 'simulated', frames,
      caption: `Green light cycles the NV through its excited state; the decay through the singlet favors mₛ = 0, so the arrow grows toward |0⟩ [doherty2013]. End point z = ${z.toFixed(2)} from adamas.photophysics (simulated; mₛ = ±1 taken as equally populated); the timing of the growth is schematic.` };
  },
  readout: d => {
    const z = d.reset_z, frames = [{ r: [0, 0, z], label: 'after reset' }, ...pulseFrames([0, 0, z], { rabiMHz: 5 }, 0.05, 30, () => 'π/2 pulse')];
    const r = frames.at(-1).r, p1 = B.pMinus1(r);
    frames.push({ r, label: `measure: mₛ = 0 with probability ${f2(1 - p1)}, mₛ = −1 with ${f2(p1)}`, outcomes: [[0, 0, 1], [0, 0, -1]] });
    return { title: 'Readout: the arrow is projected to a pole', status: 'simulated', frames,
      caption: 'A measurement does not read the arrow; it sends it to |0⟩ with probability (1 + z)/2 or to |1⟩ otherwise. Optically, mₛ = −1 glows about 30 % dimmer [gruber1997], so one shot rarely tells them apart at room temperature and the result is averaged or read through a nuclear spin [doherty2013].' };
  },
  entangle: () => {
    const frames = [];
    for (let k = 0; k <= 40; k++) { const t = (Math.PI / 4) * k / 40, r = B.reducedBloch(t);
      frames.push({ r, pair: [r, r], label: `cos θ |00⟩ + sin θ |11⟩ with θ = ${(t / Math.PI).toFixed(3)} π: each arrow ${f2(r[2])} long, concurrence ${f2(B.concurrence(t))}` }); }
    return { title: 'Entanglement shrinks each qubit\'s own arrow', status: 'simulated', interactive: 'theta', frames, poles: ['|0⟩', '|1⟩'],
      caption: 'Two qubits entangled as cos θ |00⟩ + sin θ |11⟩. Seen alone, each qubit is a shorter arrow, length cos 2θ, while the pair\'s concurrence is sin 2θ [wootters1998]: |r|² + C² = 1. A Bell pair puts both arrows at the center. The information is in the correlations, not in either qubit.' };
  },
};

// Which scene each Device Library device shows (devices with no single-spin picture show none). The relaxation scene
// uses electron-spin times, so it goes with the electron-spin qubit cell; QDL-01 shows it as a second scene.
export const DEVICE_EXTRA = { 'QDL-01': 'relax' };
export const DEVICE_SCENE = { 'QDL-01': 'gates', 'QDL-03': 'entangle', 'QDL-04': 'entangle', 'QDL-05': 'readout', 'QDL-06': 'reset',
  'QDL-08': 'rabi', 'QDL-10': 'entangle', 'QDL-11': 'entangle', 'QDL-12': 'ramsey', 'QDL-13': 'entangle', 'QDL-14': 'entangle', 'QDL-15': 'entangle',
  'QDL-16': 'entangle', 'QDL-17': 'ramsey', 'QDL-18': 'echo', 'QDL-19': 'ramsey', 'QDL-20': 'ramsey', 'QDL-21': 'ramsey',
  'QDL-24': 'ramsey', 'QDL-27': 'rabi' };
// What a scene shows on a device or step where it needs one more sentence.
export const DEVICE_NOTE = { 'QDL-10': 'Shown for the entangled states the chain passes along; the bus itself transfers states.',
  'QDL-11': 'Remote NV entanglement is demonstrated only at cryogenic temperature; the scene shows the mathematics, not a room-temperature result.',
  'QDL-13': 'Proposed at room temperature; the scene shows the mathematics of the heralded pair, not a result.' };
export const STEP_NOTE = { 'S18': 'This step measures the coupling (by double electron-electron resonance); the scene shows the entanglement that coupling would enable (proposed).' };
// Which scene each Fab Journey step shows.
export const STEP_SCENE = { 'A1.5': 'odmr', 'B1.1': 'reset', 'B1.2': 'odmr', 'B1.3': 'rabi', 'B1.4': 'ramsey', 'B1.5': 'echo', 'S18': 'entangle' };
