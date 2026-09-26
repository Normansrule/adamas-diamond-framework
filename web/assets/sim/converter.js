// Area-optimized hard-switched converter loss, mirroring adamas.converter [erickson2020] [baliga1989] [huang2004].
// Material data (specific on-resistance and output capacitance at 1 kV, and R_on(T)/R_on(300 K) tables) are exported by
// the Python package into data/site.json, so the browser uses the same physics; checked by tests/test_web.py.
export function scaled(m, bv) { return { rsp: m.rsp_1kv * (bv / 1000) ** 2, coss: m.coss_1kv * (1000 / bv) }; }

export function tFactor(m, tK) {
  const T = m.t_table.T, F = m.t_table.F;
  if (tK <= T[0]) return F[0]; if (tK >= T[T.length - 1]) return F[F.length - 1];
  const i = T.findIndex(x => x >= tK), f = (tK - T[i - 1]) / (T[i] - T[i - 1]); return F[i - 1] + f * (F[i] - F[i - 1]);
}

// returns { area (cm^2), pCond, pSw, pTotal } per switch
export function optimum(rspMohm, coss, v, i, f) {
  const r = rspMohm * 1e-3, k = 0.5 * coss * v * v * f, a = i * Math.sqrt(r / k);
  return { area: a, pCond: i * i * r / a, pSw: k * a, pTotal: 2 * i * v * Math.sqrt(f * r * coss / 2) };
}

export function switchLoss(m, { bv, v, i, f, tK = 300 }) {
  const s = scaled(m, bv); return optimum(s.rsp * tFactor(m, tK), s.coss, v, i, f);
}

export function efficiency(m, cfg, nSwitches = 6) { const p = switchLoss(m, cfg).pTotal * nSwitches, pout = cfg.v * cfg.i * 0.9; return pout / (pout + p); }
