"""Space-time resource estimate for a room-temperature NV machine from circuit-level error rates (project X-2).

Chain of reasoning (each step a model of this repository unless cited):
1. Logical error per round per patch, p_L(d), is simulated at circuit level by adamas.circuit_qec for NV noise
   (link, readout, preparation, and idle-during-readout errors) and fitted to p_L(d) = A * Lambda^(-(d+1)/2), the
   standard below-threshold scaling of the surface code [fowler2012] [google2025].
2. A computation with n_L logical qubits and D logical time steps, each step lasting d rounds [litinski2019], succeeds
   with probability 1 - eps if n_L * D * d * p_L(d) <= eps. The smallest odd d satisfying this is the code distance.
3. Footprint: each logical qubit is a rotated patch of 2d^2 - 1 physical qubits; routing space and magic-state
   factories multiply this by an overhead factor (about 2 for compact lattice-surgery layouts [litinski2019]).
4. Cycle time of one syndrome round on NV hardware = ancilla preparation + four entangling gates + readout. The gate
   time comes from the dipolar coupling at the cell spacing [dolde2013] (chapter E5); readout from chapter E4.
The illustrative workloads below are order-of-magnitude, not the published algorithm counts.
"""
from __future__ import annotations
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parents[1] / "docs" / "data" / "resource_fit.json"
READOUT_US = [30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0]
T2_MEM_MS = [1000.0, 100.0]

WORKLOADS = {  # (logical qubits, logical time steps); illustrative scales
    "Chemistry demo (100 logical, 10⁶ steps)": (100, 1e6),
    "Materials simulation (1,000 logical, 10⁹ steps)": (1000, 1e9),
    "RSA-2048 scale (6,000 logical, 3×10⁹ steps)": (6000, 3e9),
}


def fit_lambda(ds, pls) -> tuple[float, float]:
    """Least-squares fit of log p_L = log A - ((d+1)/2) log Lambda. Returns (A, Lambda)."""
    x = np.array([(d + 1) / 2 for d in ds]); y = np.log(np.maximum(np.array(pls), 1e-12))
    slope, icpt = np.polyfit(x, y, 1)
    return float(math.exp(icpt)), float(math.exp(-slope))


def build_table(shots: int = 200000) -> dict:
    """Circuit-level p_L(d) for d = 3, 5, 7 on the readout-time x memory grid, and the fitted (A, Lambda)."""
    from . import circuit_qec as cq
    out = {"readout_us": READOUT_US, "t2_mem_ms": T2_MEM_MS, "d": [3, 5, 7], "shots": shots,
           "noise": {"p_link": 3e-3, "p_meas": 1e-2, "p_init": 2e-3}, "fits": {}}
    for t2 in T2_MEM_MS:
        rows = []
        for tr in READOUT_US:
            pls = [cq.nv_logical_error(d, tr, t2_mem_ms=t2, shots=shots, seed=11 + d) for d in (3, 5, 7)]
            A, lam = fit_lambda([3, 5, 7], pls)
            rows.append({"pL": pls, "A": A, "Lambda": lam})
        # physics: a slower readout can only hurt, so Lambda is non-increasing in readout time; remove sampling wiggles
        for k in range(1, len(rows)):
            if rows[k]["Lambda"] > rows[k - 1]["Lambda"]:
                rows[k]["Lambda"] = rows[k - 1]["Lambda"]
                rows[k]["A"] = max(rows[k]["A"], rows[k - 1]["A"])
        out["fits"][str(int(t2))] = rows
    return out


MODELS = {  # resource tables: (file stem, description)
    "standard": ("resource_fit", "standard code, depolarizing gate and idle noise (chapter E10)"),
    "css_biased": ("resource_fit_css_biased", "standard code, biased NV noise (gates at bias 100, dephasing idle)"),
    "xzzx_biased": ("resource_fit_xzzx_biased", "native XZZX code, biased NV noise (gates at bias 100, dephasing idle)"),
}


def build_biased_table(code: str, shots: int = 100000, eta: float = 100.0) -> dict:
    """Circuit-level fits with the native circuits of adamas.xzzx_native (worse of the two memory bases)."""
    from . import xzzx_native as X
    out = {"readout_us": READOUT_US, "t2_mem_ms": T2_MEM_MS, "d": [3, 5, 7], "shots": shots, "code": code, "eta": eta,
           "noise": {"p_link": 3e-3, "p_meas": 1e-2, "p_init": 2e-3, "idle": "Z only, 0.5(1 - exp(-t/T2))"}, "fits": {}}
    for t2 in T2_MEM_MS:
        rows = []
        for tr in READOUT_US:
            pid = 0.5 * (1 - math.exp(-tr / (t2 * 1e3)))
            pls = [X.worse_basis(d, 3e-3, eta, code, p_meas=1e-2, p_init=2e-3, p_idle=pid, shots=shots, seed=11 + d) for d in (3, 5, 7)]
            A, lam = fit_lambda([3, 5, 7], [max(p, 1e-7) for p in pls])
            rows.append({"pL": pls, "A": A, "Lambda": lam})
        for k in range(1, len(rows)):
            if rows[k]["Lambda"] > rows[k - 1]["Lambda"]:
                rows[k]["Lambda"] = rows[k - 1]["Lambda"]
        out["fits"][str(int(t2))] = rows
    return out


def table_for(model: str = "standard", refresh: bool = False) -> dict:
    if model == "standard":
        return table(refresh)
    path = DATA.parent / f"{MODELS[model][0]}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    t = build_biased_table("xzzx" if model.startswith("xzzx") else "css"); path.write_text(json.dumps(t)); return t


BIAS_GRID = (0.5, 10.0, 100.0)      # gate-noise bias values with stored native-circuit tables (0.5 = depolarizing)


def table_eta(code: str, eta: float, refresh: bool = False) -> dict:
    """Native-circuit resource table for code 'css' or 'xzzx' at gate-noise bias eta (dephasing idle in all cases).
    Bias 100 reuses the css_biased / xzzx_biased tables; other values are cached as resource_fit_<code>_eta<eta>.json."""
    if float(eta) == 100.0:
        return table_for(f"{code}_biased", refresh)
    path = DATA.parent / f"resource_fit_{code}_eta{eta:g}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    t = build_biased_table(code, eta=eta); path.write_text(json.dumps(t)); return t


def table(refresh: bool = False) -> dict:
    if DATA.exists() and not refresh:
        return json.loads(DATA.read_text())
    t = build_table(); DATA.parent.mkdir(parents=True, exist_ok=True); DATA.write_text(json.dumps(t)); return t


def interp_fit(t: dict, t_read_us: float, t2_mem_ms: float) -> tuple[float, float]:
    rows = t["fits"][str(int(t2_mem_ms))]
    x = np.log(t["readout_us"]); xi = math.log(min(max(t_read_us, t["readout_us"][0]), t["readout_us"][-1]))
    logA = np.interp(xi, x, [math.log(r["A"]) for r in rows]); lam = np.interp(xi, x, [r["Lambda"] for r in rows])
    return float(math.exp(logA)), float(lam)


@dataclass(frozen=True)
class Estimate:
    distance: int
    physical_qubits: float
    cells: float
    die_side_mm: float
    cycle_us: float
    runtime_hours: float
    lam: float


def estimate(n_logical: float, steps: float, t_read_us: float = 1000.0, t2_mem_ms: float = 1000.0, eps: float = 0.01,
             gate_us: float = 25.0, prep_us: float = 5.0, overhead: float = 2.0, qubits_per_cell: int = 4,
             pitch_um: float = 1.0, fill: float = 0.6, t: dict | None = None, model: str = "standard") -> Estimate | None:
    t = t or table_for(model)
    A, lam = interp_fit(t, t_read_us, t2_mem_ms)
    if lam <= 1.0:
        return None                                   # above threshold: no distance helps
    d = 3
    while d < 199 and n_logical * steps * d * A * lam ** (-(d + 1) / 2) > eps:
        d += 2
    if d >= 199:
        return None
    phys = n_logical * (2 * d * d - 1) * overhead
    cells = phys / qubits_per_cell
    cycle = prep_us + 4 * gate_us + t_read_us
    return Estimate(d, phys, cells, math.sqrt(cells * pitch_um ** 2 / fill) * 1e-3, cycle, steps * d * cycle * 1e-6 / 3600, lam)


def superconducting_reference(n_logical: float, steps: float, eps: float = 0.01, lam: float = 2.14, A: float = 0.03,
                              cycle_us: float = 1.1, overhead: float = 2.0) -> Estimate:
    """Same bookkeeping with the measured below-threshold factor Lambda = 2.14 and a 1.1 us cycle [google2025].
    Note the asymmetry: this Lambda is measured on hardware, while the NV Lambda assumes a 0.3% link error that has not
    been demonstrated (the best room-temperature NV-NV entangling fidelity is 0.82 [dolde2014])."""
    d = 3
    while n_logical * steps * d * A * lam ** (-(d + 1) / 2) > eps:
        d += 2
    phys = n_logical * (2 * d * d - 1) * overhead
    return Estimate(d, phys, phys, float("nan"), cycle_us, steps * d * cycle_us * 1e-6 / 3600, lam)
