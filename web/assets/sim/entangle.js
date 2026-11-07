// Entanglement Lab, the browser twin of adamas.entangle (checked against web/tests/entangle_golden.json, which Python
// computes with full density matrices). Closed forms for a Werner pair v |Phi+><Phi+| + (1 - v) I/4 measured along
// angles in the X-Z plane: P(Alice k, Bob l) = (1 + (-1)^(k+l) v cos(a - b)) / 4, so Bob's own odds are 1/2 whatever
// Alice does (no-communication theorem [ghirardi1980]). Teleportation [bennett1993] with the two bits: (1 + v)/2;
// without them: 1/2. CHSH [clauser1969]: S = 2 sqrt(2) v at the optimal angles, local bound 2, quantum bound 2 sqrt(2)
// [cirelson1980].
export const C_M_S = 299792458;
export const LOCAL_BOUND = 2;
export const TSIRELSON = 2 * Math.SQRT2;
export const MEASURE_PREPARE = 2 / 3;      // no entanglement: measure in Z, phone the result, re-prepare (average over inputs)

export function joint(v, a, b) {
  const c = v * Math.cos(a - b);
  return [[(1 + c) / 4, (1 - c) / 4], [(1 - c) / 4, (1 + c) / 4]];
}
export function bobP0(v, a, b) { const P = joint(v, a, b); return P[0][0] + P[1][0]; }          // always 1/2
export function correlator(v, a, b) { return v * Math.cos(a - b); }
export function chsh(v, a = 0, a2 = Math.PI / 2, b = Math.PI / 4, b2 = -Math.PI / 4) {
  return correlator(v, a, b) + correlator(v, a, b2) + correlator(v, a2, b) - correlator(v, a2, b2);
}
export function teleportFidelity(v, withBits) { return withBits ? (1 + v) / 2 : 0.5; }
export function lightMs(km) { return km * 1e3 / C_M_S * 1e3; }
export const wernerThreshold = () => LOCAL_BOUND / TSIRELSON;

// One round of the lab's signaling attempt: sample (Alice's outcome, Bob's outcome) from joint(v, a, b).
export function sample(v, a, b, rnd = Math.random) {
  const P = joint(v, a, b), u = rnd();
  if (u < P[0][0]) return [0, 0];
  if (u < P[0][0] + P[0][1]) return [0, 1];
  if (u < P[0][0] + P[0][1] + P[1][0]) return [1, 0];
  return [1, 1];
}
