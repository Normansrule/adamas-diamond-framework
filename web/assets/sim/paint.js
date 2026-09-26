// "Paint with heat": one grid, left half silicon, right half diamond, same cells and time step for both, so what you
// see is the difference in thermal diffusivity alpha = kappa / (rho c): 0.91 versus 12.3 cm^2/s [glassbrenner1964] [wei1993].
// Explicit scheme, edges held at ambient. Pure module; unit-tested with node.
export const ALPHA = { Si: 1.5 / (2.33 * 0.705), Diamond: 22 / (3.52 * 0.509) };

export function create(nx = 120, ny = 60) {
  const a = new Float32Array(nx * ny);
  for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) a[j * nx + i] = i < nx / 2 ? ALPHA.Si : ALPHA.Diamond;
  const amax = ALPHA.Diamond;
  return { nx, ny, T: new Float32Array(nx * ny), N: new Float32Array(nx * ny), a, f: a.map(v => 0.24 * v / amax) };  // f = alpha dt / dx^2 <= 0.24
}

export function deposit(g, x, y, amount = 1, radius = 3) {   // x, y in cells
  for (let j = Math.max(1, y - radius); j <= Math.min(g.ny - 2, y + radius); j++)
    for (let i = Math.max(1, x - radius); i <= Math.min(g.nx - 2, x + radius); i++) {
      const d2 = (i - x) ** 2 + (j - y) ** 2; if (d2 <= radius * radius) g.T[j * g.nx + i] += amount * Math.exp(-d2 / (radius * radius));
    }
}

export function step(g, n = 1) {
  const { nx, ny, f } = g;
  for (let s = 0; s < n; s++) {
    const T = g.T, N = g.N;
    for (let j = 1; j < ny - 1; j++) for (let i = 1; i < nx - 1; i++) {
      const k = j * nx + i;                                   // conservative flux form with harmonic-mean interfaces
      const fx1 = 2 * f[k] * f[k + 1] / (f[k] + f[k + 1]), fx0 = 2 * f[k] * f[k - 1] / (f[k] + f[k - 1]);
      N[k] = T[k] + fx1 * (T[k + 1] - T[k]) - fx0 * (T[k] - T[k - 1]) + f[k] * (T[k + nx] + T[k - nx] - 2 * T[k]);
    }
    g.T = N; g.N = T;
  }
  return g;
}

export function spread(g, half) {                             // second moment of the heat in one half: how far it has moved
  let m = 0, s = 0, sx = 0, sy = 0; const x0 = half === 'Si' ? 1 : g.nx / 2, x1 = half === 'Si' ? g.nx / 2 : g.nx - 1;
  for (let j = 1; j < g.ny - 1; j++) for (let i = x0; i < x1; i++) { const v = g.T[j * g.nx + i]; m += v; sx += v * i; sy += v * j; }
  const cx = sx / m, cy = sy / m;
  for (let j = 1; j < g.ny - 1; j++) for (let i = x0; i < x1; i++) { const v = g.T[j * g.nx + i]; s += v * ((i - cx) ** 2 + (j - cy) ** 2); }
  return s / m;
}
