// Space-time resource estimate, mirroring adamas.resource (project X-2): circuit-level fits p_L(d) = A * Lambda^(-(d+1)/2)
// from Stim simulations of NV noise [gidney2021stim], lattice-surgery bookkeeping [litinski2019] [fowler2012].
// The fit table is exported by the Python package into data/site.json; tests/test_web.py checks agreement.
export function interpFit(t, tReadUs, t2MemMs) {
  const rows = t.fits[String(Math.round(t2MemMs))], xs = t.readout_us.map(Math.log);
  const x = Math.log(Math.min(Math.max(tReadUs, t.readout_us[0]), t.readout_us[t.readout_us.length - 1]));
  let i = xs.findIndex(v => v >= x); if (i <= 0) i = 1; const f = (x - xs[i - 1]) / (xs[i] - xs[i - 1]);
  const logA = Math.log(rows[i - 1].A) + f * (Math.log(rows[i].A) - Math.log(rows[i - 1].A)), lam = rows[i - 1].Lambda + f * (rows[i].Lambda - rows[i - 1].Lambda);
  return { A: Math.exp(logA), lam };
}

export function estimate(t, { nLogical, steps, tReadUs = 1000, t2MemMs = 1000, eps = 0.01, gateUs = 25, prepUs = 5, overhead = 2, qubitsPerCell = 4, pitchUm = 1, fill = 0.6 }) {
  const { A, lam } = interpFit(t, tReadUs, t2MemMs);
  if (lam <= 1) return null;
  let d = 3; while (d < 199 && nLogical * steps * d * A * lam ** (-(d + 1) / 2) > eps) d += 2;
  if (d >= 199) return null;
  const phys = nLogical * (2 * d * d - 1) * overhead, cells = phys / qubitsPerCell, cycle = prepUs + 4 * gateUs + tReadUs;
  return { distance: d, physical: phys, cells, dieSideMm: Math.sqrt(cells * pitchUm ** 2 / fill) * 1e-3, cycleUs: cycle, runtimeHours: steps * d * cycle * 1e-6 / 3600, lam };
}

export function superconducting(nLogical, steps, { eps = 0.01, lam = 2.14, A = 0.03, cycleUs = 1.1, overhead = 2 } = {}) {
  let d = 3; while (nLogical * steps * d * A * lam ** (-(d + 1) / 2) > eps) d += 2;
  return { distance: d, physical: nLogical * (2 * d * d - 1) * overhead, runtimeHours: steps * d * cycleUs * 1e-6 / 3600 };
}

export function human(hours) {
  if (!Number.isFinite(hours)) return '–';
  if (hours < 1 / 60) return `${(hours * 3600).toFixed(1)} s`; if (hours < 1) return `${(hours * 60).toFixed(1)} min`;
  if (hours < 48) return `${hours.toFixed(1)} h`; if (hours < 24 * 365 * 2) return `${(hours / 24).toFixed(0)} days`; return `${(hours / 24 / 365).toFixed(1)} years`;
}
