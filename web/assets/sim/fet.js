// Square-law hydrogen-terminated diamond p-FET, enhancement/depletion inverter, and ring oscillator. Mirrors
// adamas.logic.Fet [sze2006] (magnitude convention: rails are negative in the lab) and the inverter style of [liu2017].
// Unit-tested with node against the Python package and the ngspice ring oscillator.
const EPS0 = 8.8541878128e-14;                    // F/cm

export function fet({ mu = 150, toxNm = 30, epsOx = 9, w = 100, l = 2, vth = 1 } = {}) {
  const cox = epsOx * EPS0 / (toxNm * 1e-7), k = mu * cox * w / l;
  return { mu, toxNm, epsOx, w, l, vth, cox, k, cgate: cox * w * l * 1e-8,
    current(vgs, vds) { const vov = vgs - vth; if (vov <= 0 || vds <= 0) return 0; return vds < vov ? k * (vov * vds - vds * vds / 2) : k * vov * vov / 2; } };
}

// Output voltage of the E/D inverter for input vin: solve I_drv(vin, vo) = I_load(0, vdd - vo) by bisection.
export function inverterOut(drv, load, vin, vdd) {
  let lo = 0, hi = vdd;
  for (let i = 0; i < 60; i++) { const vo = (lo + hi) / 2; (drv.current(vin, vo) > load.current(0, vdd - vo)) ? hi = vo : lo = vo; }
  return (lo + hi) / 2;
}
export function vtc(drv, load, vdd, n = 201) { const vin = [...Array(n)].map((_, i) => vdd * i / (n - 1)); return { vin, vout: vin.map(v => inverterOut(drv, load, v, vdd)) }; }

export function noiseMargins(vin, vout) {        // unity-gain points
  const g = vout.map((v, i) => i ? (v - vout[i - 1]) / (vin[i] - vin[i - 1]) : 0);
  let il = g.findIndex(x => x < -1), ih = g.length - 1 - [...g].reverse().findIndex(x => x < -1);
  if (il < 1) return { nml: 0, nmh: 0 };
  const vil = vin[il], vih = vin[ih], voh = vout[0], vol = vout[vout.length - 1];
  return { nml: vil - vol, nmh: voh - vih, vil, vih, voh, vol };
}

// N-stage ring: C dVk/dt = I_load(0, vdd - Vk) - I_drv(V(k-1), Vk). Returns node waveforms and the period.
export function ring(drv, load, { vdd = 10, stages = 5, cWire = 20e-15, tEnd = 200e-9, dt = 2e-11 } = {}) {
  const C = drv.cgate + cWire, v = [...Array(stages)].map((_, k) => k % 2 ? vdd : 0), t = [], wave = [...Array(stages)].map(() => []);
  const rises = [];
  for (let s = 0, time = 0; time < tEnd; s++, time += dt) {
    const dv = v.map((vk, k) => (load.current(0, vdd - vk) - drv.current(v[(k + stages - 1) % stages], vk)) / C * dt);
    const before = v[0]; for (let k = 0; k < stages; k++) v[k] = Math.min(vdd, Math.max(0, v[k] + dv[k]));
    if (before < vdd / 2 && v[0] >= vdd / 2) rises.push(time);
    if (s % 20 === 0) { t.push(time); v.forEach((x, k) => wave[k].push(x)); }
  }
  const periods = rises.slice(1).map((x, i) => x - rises[i]);
  return { t, wave, period: periods.length > 2 ? periods.slice(2).reduce((a, b) => a + b) / (periods.length - 2) : NaN, C };
}
