// NV resonance lines and the diamond lattice: pure functions shared by the 3-D labs. Unit-tested with node.
import { GAMMA } from './action.js';
export const D_MHZ = 2870, GAMMA_MHZ_PER_MT = GAMMA;                            // 28.03 MHz/mT, g = 2.0028 [doherty2013]
export const NV_AXES = [[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]].map(a => a.map(x => x / Math.sqrt(3)));

export function lines(B) {           // B in mT (vector); two lines per orientation, second-order perpendicular shift included
  const b2 = B[0] ** 2 + B[1] ** 2 + B[2] ** 2, out = [];
  NV_AXES.forEach((a, k) => {
    const bp = a[0] * B[0] + a[1] * B[1] + a[2] * B[2], bt2 = Math.max(b2 - bp * bp, 0), shift = 3 * GAMMA_MHZ_PER_MT ** 2 * bt2 / (2 * D_MHZ);
    const half = Math.hypot(GAMMA_MHZ_PER_MT * bp, GAMMA_MHZ_PER_MT ** 2 * bt2 / (2 * D_MHZ));     // +/-1 mixing near 90 degrees (adamas.nv.lines_perturbative_mhz)
    out.push({ axis: k, f: D_MHZ + shift - half }, { axis: k, f: D_MHZ + shift + half });
  });
  return out;
}

export function spectrum(B, freqs, widthMHz = 1.5, contrast = 0.02) {
  const ls = lines(B);
  return freqs.map(f => 1 - ls.reduce((s, l) => s + contrast * widthMHz ** 2 / ((f - l.f) ** 2 + widthMHz ** 2), 0));
}

export function diamondLattice(cells = 2, a = 3.567) {   // conventional cubic cell, 8 atoms [sze2006] [wort2008]
  const basis = [[0, 0, 0], [0, .5, .5], [.5, 0, .5], [.5, .5, 0], [.25, .25, .25], [.25, .75, .75], [.75, .25, .75], [.75, .75, .25]];
  const atoms = [];
  for (let x = 0; x < cells; x++) for (let y = 0; y < cells; y++) for (let z = 0; z < cells; z++)
    for (const b of basis) atoms.push([(x + b[0]) * a, (y + b[1]) * a, (z + b[2]) * a]);
  const bond = a * Math.sqrt(3) / 4, bonds = [];
  for (let i = 0; i < atoms.length; i++) for (let j = i + 1; j < atoms.length; j++) {
    const d = Math.hypot(atoms[i][0] - atoms[j][0], atoms[i][1] - atoms[j][1], atoms[i][2] - atoms[j][2]);
    if (Math.abs(d - bond) < 0.05 * a) bonds.push([i, j]);
  }
  return { atoms, bonds, bond, a };
}

// Lines of one NV to second order in the field, theta = angle between B and the NV axis (mirrors adamas.nv.lines_perturbative_mhz)
export function linesPerturbative(bMt, thDeg, d = D_MHZ) {
  const bpar = bMt * Math.abs(Math.cos(thDeg * Math.PI / 180)), bperp = bMt * Math.abs(Math.sin(thDeg * Math.PI / 180));
  const sh = 3 * (GAMMA_MHZ_PER_MT * bperp) ** 2 / (2 * d), half = Math.hypot(GAMMA_MHZ_PER_MT * bpar, (GAMMA_MHZ_PER_MT * bperp) ** 2 / (2 * d));
  return [d + sh - half, d + sh + half];
}
