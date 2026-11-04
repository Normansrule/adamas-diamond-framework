// Quantum Device Library: the live coupler panel's arithmetic, the browser twin of adamas.coupling and adamas.qdl.r_max_nm.
// nu = DIP / r^3 (perpendicular orientation), t = 1 / (2 nu), coherence-limited bound F = (1 + exp(-t / T2)) / 2.
// Assumptions: echo-limited, no control errors, perfect charge state: an upper bound. Tested against
// web/tests/qdl_golden.json (written by adamas build docs) to relative 1e-9.
export const couplingKHz = (r, dip) => dip * 1e3 / r ** 3;
export const gateTimeUs = (r, dip) => 1e3 / (2 * couplingKHz(r, dip));
export const fidelityBound = (r, t2ms, dip) => 0.5 * (1 + Math.exp(-gateTimeUs(r, dip) / (t2ms * 1e3)));
export function rMaxNm(F, t2ms, dip) {
  const tUs = -Math.log(2 * F - 1) * t2ms * 1e3, nu = 1e3 / (2 * tUs);
  return Math.cbrt(dip * 1e3 / nu);
}
