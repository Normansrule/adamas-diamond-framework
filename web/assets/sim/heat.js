// 2-D heat conduction in a die cross-section (explicit finite differences). Pure module; unit-tested with node.
// dT/dt = alpha * laplacian(T) + q / (rho c), alpha = kappa / (rho c). Bottom edge held at the heat-sink temperature;
// other edges insulated. Material data: kappa [sze2006] [kimoto2014] [mishra2008] [wei1993]; rho and c textbook values.
export const MATERIALS = {
  Si:      { name: 'Silicon',         kappa: 1.5,  rho: 2.33, c: 0.705, color: '#8b98a5' },
  SiC:     { name: 'Silicon carbide', kappa: 4.9,  rho: 3.21, c: 0.69,  color: '#e0a030' },
  GaN:     { name: 'Gallium nitride', kappa: 2.3,  rho: 6.15, c: 0.49,  color: '#9d7bff' },
  Diamond: { name: 'Diamond',         kappa: 22.0, rho: 3.52, c: 0.509, color: '#2de2e6' },
};

export function create(key, n = 48, sizeCm = 0.2) {
  const m = MATERIALS[key], dx = sizeCm / n, alpha = m.kappa / (m.rho * m.c);
  return { key, n, dx, alpha, rc: m.rho * m.c, kappa: m.kappa, T: new Float64Array(n * n), time: 0, dtMax: 0.2 * dx * dx / alpha };
}

// q: volumetric source (W/cm^3) applied in a small block at the top center (the switching transistor)
export function sourceMask(n) { const s = new Uint8Array(n * n), w = Math.max(2, n >> 3);
  for (let j = 0; j < 3; j++) for (let i = (n >> 1) - (w >> 1); i < (n >> 1) + (w >> 1); i++) s[j * n + i] = 1; return s; }

export function step(sim, q, dt, mask = sourceMask(sim.n)) {
  const { n, dx, alpha, rc } = sim; let T = sim.T, left = dt;
  const N = new Float64Array(n * n);
  while (left > 0) {
    const h = Math.min(left, sim.dtMax), f = alpha * h / (dx * dx);
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
      const k = j * n + i;
      if (j === n - 1) { N[k] = 0; continue; }                         // heat sink row
      const up = j > 0 ? T[k - n] : T[k], dn = T[k + n], lf = i > 0 ? T[k - 1] : T[k], rt = i < n - 1 ? T[k + 1] : T[k];
      N[k] = T[k] + f * (up + dn + lf + rt - 4 * T[k]) + (mask[k] ? q * h / rc : 0);
    }
    T.set(N); left -= h; sim.time += h;
  }
  return sim;
}

export function steady(sim, q, iters = 6000) {        // Gauss-Seidel on kappa * laplacian(T) = -q
  const { n, dx, kappa } = sim, T = sim.T, mask = sourceMask(n), s = q * dx * dx / kappa;
  for (let it = 0; it < iters; it++) for (let j = 0; j < n - 1; j++) for (let i = 0; i < n; i++) {
    const k = j * n + i, up = j > 0 ? T[k - n] : T[k], dn = T[k + n], lf = i > 0 ? T[k - 1] : T[k], rt = i < n - 1 ? T[k + 1] : T[k];
    let nb = 4, sum = up + dn + lf + rt;
    if (j === 0) { nb--; sum -= up; } if (i === 0) { nb--; sum -= lf; } if (i === n - 1) { nb--; sum -= rt; }
    T[k] = (sum + (mask[k] ? s : 0)) / nb;
  }
  return sim;
}

export const maxT = sim => sim.T.reduce((a, b) => Math.max(a, b), 0);
