// Why only a CZ gate keeps a noise bias, mirroring adamas.gatebias (checked against web/tests/loop_golden.json and,
// in Python, against Stim's PauliString.after [gidney2021stim]). Qubit 0 is the control, 1 the target.
const PAULI = { '0,0': 'I', '1,0': 'X', '1,1': 'Y', '0,1': 'Z' };
export function conj(gate, qs, x, z) {
  if (gate === 'H') { const [q] = qs; [x[q], z[q]] = [z[q], x[q]]; }
  else if (gate === 'CZ') { const [a, b] = qs; z[a] ^= x[b]; z[b] ^= x[a]; }
  else if (gate === 'CX') { const [c, t] = qs; x[t] ^= x[c]; z[c] ^= z[t]; }
  else throw new Error(gate);
}
export function propagate(error, after) {          // error {q: 'X'|'Y'|'Z'}, after [[gate, qubits]] -> {0: P, 1: P}
  const x = [0, 0], z = [0, 0];
  for (const [q, p] of Object.entries(error)) { x[q] = 'XY'.includes(p) ? 1 : 0; z[q] = 'YZ'.includes(p) ? 1 : 0; }
  for (const [g, qs] of after) conj(g, qs, x, z);
  return { 0: PAULI[`${x[0]},${z[0]}`], 1: PAULI[`${x[1]},${z[1]}`] };
}
export function construction(kind, hFrac = 0.002) {
  if (kind === 'cz') return [['CZ', [0, 1], 1]];
  if (kind === 'cnot') return [['H', [1], hFrac], ['CZ', [0, 1], 1], ['H', [1], hFrac]];
  throw new Error(kind);
}
export function outputDistribution(kind, eta, hFrac = 0.002) {
  const seg = construction(kind, hFrac), tot = seg.reduce((s, x) => s + x[2], 0);
  const pin = { X: 1 / (2 * (eta + 1)), Y: 1 / (2 * (eta + 1)), Z: eta / (eta + 1) };
  const out = { 0: { X: 0, Y: 0, Z: 0 }, 1: { X: 0, Y: 0, Z: 0 } }; let spread = 0, weight = 0; const events = [];
  seg.forEach(([, , dur], k) => {
    const rest = seg.slice(k + 1).map(([g, qs]) => [g, qs]);
    for (const q of [0, 1]) for (const [p, w] of Object.entries(pin)) {
      const ww = w * dur / tot; weight += ww;
      const res = propagate({ [q]: p }, rest), hit = [0, 1].filter(r => res[r] !== 'I');
      hit.forEach(r => { out[r][res[r]] += ww; }); if (hit.length === 2) spread += ww;
      events.push({ segment: k, qubit: q, pauli: p, weight: ww, result: res });
    }
  });
  return { perQubit: out, spread: spread / weight, weight, events };
}
export function outputBias(kind, eta, hFrac = 0.002) {
  const d = outputDistribution(kind, eta, hFrac).perQubit, b = q => (d[q].X + d[q].Y > 0 ? d[q].Z / (d[q].X + d[q].Y) : Infinity);
  return { 0: b(0), 1: b(1) };
}
