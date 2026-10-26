// Planar surface code (bit-flip sector) on the same graph as adamas/surface_sim.py [dennis2002] [fowler2012]:
// checks on a d x (d-1) grid, data qubits on edges, logical error = chain joining the left and right boundaries.
// The decoder here is greedy nearest-pair matching (fast and visual); the Python package uses exact matching [higgott2022].
export function layout(d) {
  const rows = d, cols = d - 1, edges = [];
  for (let r = 0; r < rows; r++) for (let c = 0; c <= cols; c++)
    edges.push({ kind: 'h', r, c, a: c > 0 ? [r, c - 1] : null, b: c < cols ? [r, c] : null, logical: c === 0 });
  for (let r = 0; r < rows - 1; r++) for (let c = 0; c < cols; c++)
    edges.push({ kind: 'v', r, c, a: [r, c], b: [r + 1, c], logical: false });
  return { d, rows, cols, edges };
}

export function syndrome(L, flips) {
  const s = new Uint8Array(L.rows * L.cols);
  L.edges.forEach((e, i) => { if (!flips[i]) return; for (const p of [e.a, e.b]) if (p) s[p[0] * L.cols + p[1]] ^= 1; });
  return s;
}

function pathEdges(L, from, to) {     // Manhattan path between two checks, or to the nearer side boundary if to === null
  const idx = new Map(L.edges.map((e, i) => [`${e.kind}${e.r},${e.c}`, i])), out = [];
  let [r, c] = from;
  if (to === null) {
    if (c + 1 <= L.cols - c) { for (let k = c; k >= 0; k--) out.push(idx.get(`h${r},${k}`)); }
    else { for (let k = c + 1; k <= L.cols; k++) out.push(idx.get(`h${r},${k}`)); }
    return out;
  }
  const [r2, c2] = to;
  while (c !== c2) { const k = c < c2 ? c + 1 : c; out.push(idx.get(`h${r},${k}`)); c += c < c2 ? 1 : -1; }
  while (r !== r2) { const k = r < r2 ? r : r - 1; out.push(idx.get(`v${k},${c}`)); r += r < r2 ? 1 : -1; }
  return out;
}

export function decode(L, s) {
  const defects = []; for (let r = 0; r < L.rows; r++) for (let c = 0; c < L.cols; c++) if (s[r * L.cols + c]) defects.push([r, c]);
  const bdist = p => Math.min(p[1] + 1, L.cols - p[1]), corr = new Uint8Array(L.edges.length), pairs = [];
  const live = defects.slice();
  while (live.length) {
    let best = null;
    for (let i = 0; i < live.length; i++) {
      const bd = bdist(live[i]); if (!best || bd < best.w) best = { w: bd, i, j: -1 };
      for (let j = i + 1; j < live.length; j++) {
        const w = Math.abs(live[i][0] - live[j][0]) + Math.abs(live[i][1] - live[j][1]);
        if (w < best.w) best = { w, i, j };
      }
    }
    const a = live[best.i], b = best.j >= 0 ? live[best.j] : null;
    for (const e of pathEdges(L, a, b)) corr[e] ^= 1;
    pairs.push([a, b]);
    live.splice(Math.max(best.i, best.j), 1); if (best.j >= 0) live.splice(Math.min(best.i, best.j), 1);
  }
  return { corr, pairs };
}

export function logicalFlip(L, flips, corr) {
  let p = 0; L.edges.forEach((e, i) => { if (e.logical) p ^= (flips[i] ^ corr[i]); }); return p;
}

// Fit p_L = A (p / p_th)^((d+1)/2) to threshold-experiment data by weighted least squares in log space:
// log p_L - k log p = log A - k log p_th, k = (d+1)/2, each point weighted by its binomial precision N p_L / (1 - p_L).
// Only points below the current p_th estimate are used (the leading-order regime), iterating the cut; zero counts carry
// no log and are skipped, which biases A slightly upward at the smallest p (stated in the lab).
export function fitScaling(ps, ds, res, trials = 600, iters = 4) {
  let pth = Infinity, out = null;
  for (let it = 0; it < iters; it++) {
    let s11 = 0, s12 = 0, s22 = 0, b1 = 0, b2 = 0, n = 0;
    for (const d of ds) { const k = (d + 1) / 2; ps.forEach((p, i) => { const v = res[d][i]; if (!(v > 0 && v < 0.5) || p >= pth) return;
      const w = trials * v / (1 - v), y = Math.log(v) - k * Math.log(p); s11 += w; s12 -= w * k; s22 += w * k * k; b1 += w * y; b2 -= w * k * y; n++; }); }
    const det = s11 * s22 - s12 * s12; if (n < 3 || Math.abs(det) < 1e-12) return out;
    const a = (b1 * s22 - s12 * b2) / det, c = (s11 * b2 - s12 * b1) / det;
    out = { A: Math.exp(a), pth: Math.exp(c), n };
    if (Math.exp(c) === pth) break; pth = Math.exp(c);
  }
  return out;
}
