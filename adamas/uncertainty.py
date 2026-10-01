"""How sure are the headline numbers? Uncertainty and sensitivity analysis (a systems-engineering view of ADAMAS).

Two headline results are propagated through their models with every uncertain input drawn from a documented range:

1. Power: the loss ratio silicon carbide / diamond for the 800 V, 300 A, 20 kHz traction inverter (chapter E9). Material
   constants are not settled: diamond's critical field is quoted from about 5 to 10 MV/cm and its hole mobility from
   about 1,000 to 3,800 cm^2/(V s) depending on crystal quality and doping [isberg2002] [wort2008] [donato2020]; silicon
   carbide's field and mobility have narrower spreads [kimoto2014].
2. Quantum: the runtime of the RSA-2048-scale job on a room-temperature NV machine (chapter E10.5b), with readout time,
   nuclear-memory lifetime, gate time, preparation time, and layout overhead uncertain [hopper2018] [maurer2012]
   [dolde2013] [litinski2019].

Methods: Latin-hypercube sampling (uniform or log-uniform per parameter) for the output distribution with P10, P50, P90,
and one-at-a-time low/high swings around the baseline for a tornado diagram, the standard first look in decision
analysis. Ranges are this repository's judgment from the cited spreads, stated in the tables below.
"""
from __future__ import annotations
import math
from dataclasses import replace

import numpy as np

# name: (baseline, low, high, scale, unit, source)
POWER = {
    "Diamond critical field": (10.0, 5.0, 10.0, "lin", "MV/cm", "[wort2008] [donato2020]"),
    "Diamond hole mobility": (3800.0, 1000.0, 3800.0, "log", "cm²/V·s", "[isberg2002] [wort2008]"),
    "Diamond permittivity": (5.7, 5.6, 5.8, "lin", "", "[sze2006]"),
    "SiC critical field": (3.0, 2.5, 3.5, "lin", "MV/cm", "[kimoto2014]"),
    "SiC electron mobility": (950.0, 700.0, 1000.0, "lin", "cm²/V·s", "[kimoto2014]"),
}
QUANTUM = {
    "Readout time": (1000.0, 100.0, 3000.0, "log", "µs", "[hopper2018] [neumann2010science]"),
    "Nuclear memory T₂": (1000.0, 100.0, 1000.0, "choice", "ms", "[maurer2012]"),
    "Two-qubit gate time": (25.0, 5.0, 50.0, "log", "µs", "[dolde2013]"),
    "Ancilla preparation": (5.0, 2.0, 10.0, "lin", "µs", "[aslam2013]"),
    "Layout overhead": (2.0, 1.5, 3.0, "lin", "×", "[litinski2019]"),
}


def power_ratio(p: dict) -> float:
    """Loss(SiC) / Loss(diamond) at the area optimum; the 2·I·V·sqrt(f/2) prefactor cancels, leaving sqrt(R·C) ratios."""
    from . import converter, materials, power
    d = replace(materials.MATERIALS["Diamond"], ec_mv_cm=p["Diamond critical field"], mu_p=p["Diamond hole mobility"], eps_r=p["Diamond permittivity"])
    s = replace(materials.MATERIALS["4H-SiC"], ec_mv_cm=p["SiC critical field"], mu_n=p["SiC electron mobility"])
    rc = lambda m, car: power.ron_sp_mohm_cm2(m, 1200.0, car) * converter.coss_sp_f_cm2(m, 1200.0)  # noqa: E731
    return math.sqrt(rc(s, "n") / rc(d, "p"))


def quantum_runtime_years(p: dict, table=None) -> float:
    from . import resource
    n, st = resource.WORKLOADS["RSA-2048 scale (6,000 logical, 3×10⁹ steps)"]
    e = resource.estimate(n, st, p["Readout time"], p["Nuclear memory T₂"], gate_us=p["Two-qubit gate time"], prep_us=p["Ancilla preparation"],
                          overhead=p["Layout overhead"], t=table or resource.table())
    return float("inf") if e is None else e.runtime_hours / 8766


STUDIES = {"power": (POWER, power_ratio, "SiC loss ÷ diamond loss (EV inverter)"),
           "quantum": (QUANTUM, quantum_runtime_years, "RSA-2048-scale runtime (years)")}


def baseline(space: dict) -> dict:
    return {k: v[0] for k, v in space.items()}


def sample(space: dict, n: int, seed: int = 11) -> list[dict]:
    """Latin-hypercube samples: one draw per stratum for each parameter, strata shuffled independently."""
    rng = np.random.default_rng(seed); out = [dict() for _ in range(n)]
    for k, (base, lo, hi, scale, *_rest) in space.items():
        u = (rng.permutation(n) + rng.random(n)) / n
        if scale == "choice":
            vals = np.where(u < 0.5, lo, hi)
        elif scale == "log":
            vals = np.exp(np.log(lo) + u * (np.log(hi) - np.log(lo)))
        else:
            vals = lo + u * (hi - lo)
        for i in range(n):
            out[i][k] = float(vals[i])
    return out


def monte_carlo(study: str, n: int = 2000, seed: int = 11) -> dict:
    space, fn, label = STUDIES[study]
    kw = {}
    if study == "quantum":
        from . import resource
        tab = resource.table(); f = lambda p: fn(p, tab)  # noqa: E731
    else:
        f = fn
    ys = np.array([f(p) for p in sample(space, n, seed)])
    finite = ys[np.isfinite(ys)]
    return {"label": label, "values": ys.tolist(), "p10": float(np.percentile(finite, 10)), "p50": float(np.percentile(finite, 50)),
            "p90": float(np.percentile(finite, 90)), "baseline": float(f(baseline(space))), "fraction_failed": float(1 - finite.size / ys.size)}


def tornado(study: str) -> list[dict]:
    """One-at-a-time swings: each parameter set to its low and high value with the others at baseline."""
    space, fn, label = STUDIES[study]
    if study == "quantum":
        from . import resource
        tab = resource.table(); f = lambda p: fn(p, tab)  # noqa: E731
    else:
        f = fn
    base = baseline(space); y0 = f(base); rows = []
    for k, (b, lo, hi, *_rest) in space.items():
        ylo, yhi = f({**base, k: lo}), f({**base, k: hi})
        rows.append({"name": k, "low": lo, "high": hi, "y_low": ylo, "y_high": yhi, "swing": abs(yhi - ylo)})
    rows.sort(key=lambda r: r["swing"], reverse=True)
    return [{"baseline": y0, **r} for r in rows]


def to_json() -> dict:
    """Parameter spaces for the browser Uncertainty Lab (the lab re-runs the Monte Carlo live)."""
    return {s: {"label": STUDIES[s][2], "params": {k: list(v) for k, v in STUDIES[s][0].items()}} for s in STUDIES}
