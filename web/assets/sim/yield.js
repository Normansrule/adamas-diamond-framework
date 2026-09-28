// Dies per wafer and yield, mirroring adamas.wafer [murphy1964] [stapper1983]; plus a Monte Carlo that drops point
// defects on a wafer and marks every die hit as bad, which is exactly the Poisson model.
export const diesPerWafer = (dMm, aMm2) => Math.max(0, Math.floor(Math.PI * (dMm / 2) ** 2 / aMm2 - Math.PI * dMm / Math.sqrt(2 * aMm2)));
export const poisson = (aMm2, d0) => Math.exp(-aMm2 * 1e-2 * d0);
export const murphy = (aMm2, d0) => { const x = aMm2 * 1e-2 * d0; return x === 0 ? 1 : ((1 - Math.exp(-x)) / x) ** 2; };

export function layout(dMm, sideMm, edgeMm = 3) {       // die grid: squares fully inside the usable radius
  const r = dMm / 2 - edgeMm, n = Math.ceil(dMm / sideMm), dies = [];
  for (let i = -n; i < n; i++) for (let j = -n; j < n; j++) {
    const x = i * sideMm, y = j * sideMm, far = Math.max(Math.hypot(x, y), Math.hypot(x + sideMm, y), Math.hypot(x, y + sideMm), Math.hypot(x + sideMm, y + sideMm));
    if (far <= r) dies.push({ x, y, bad: false });
  }
  return { r, side: sideMm, dies };
}

export function drop(L, count, rng = Math.random) {     // uniform defects in the usable disk; returns their positions
  const pts = [];
  for (let k = 0; k < count; k++) { const rr = L.r * Math.sqrt(rng()), a = 2 * Math.PI * rng(), x = rr * Math.cos(a), y = rr * Math.sin(a); pts.push([x, y]);
    const i = Math.floor(x / L.side), j = Math.floor(y / L.side); const d = L.dies.find(q => Math.abs(q.x - i * L.side) < 1e-9 && Math.abs(q.y - j * L.side) < 1e-9); if (d) d.bad = true; }
  return pts;
}
