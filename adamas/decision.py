"""What to measure next: variance-based sensitivity, value of information, and the code decision.

The tornado diagram of adamas.uncertainty moves one input at a time. This module answers the decision questions behind it:

1. Which unknown explains the spread? First-order and total Sobol indices [sobol2001], estimated with the Saltelli/Jansen
   pick-freeze scheme [jansen1999] on Latin-hypercube samples [saltelli2002]. The first-order index S_i is exactly the fraction of the
   output variance that would disappear, on average, if input i were known perfectly: its expected value of information
   when the cost of being wrong is the squared error.
2. Which measurement buys that reduction most cheaply? Each input is mapped to the ADAMAS experiment (or desk study) that
   pins it down, with that experiment's cost; ranking S_i per dollar gives a measurement roadmap.
3. Does the unknown change a decision? The gate-noise bias of NV two-qubit gates is unmeasured. Choosing the standard or
   the XZZX code under that uncertainty is a decision problem; the expected value of perfect information (EVPI) on the
   bias [howard1966] is the most a bias measurement could be worth for that choice.

Costs are geometric means of the experiment price ranges in adamas.experiments; "desk study" costs are nominal
(about a week of an engineer's time). The prior over the bias is uniform over the three simulated values, an assumption.
"""
from __future__ import annotations
import functools
import math

import numpy as np

from . import uncertainty as U

DESK = 1000.0      # nominal cost of a literature or simulation study (US$)
RESOLUTION = 0.02  # Sobol estimates below this are within the estimator's seed-to-seed scatter at n = 16,000

# input -> (how it is pinned down, experiment id or None for a desk study, what is measured)
MEASURE = {
    "Diamond critical field": ("C2", "breakdown of sacrificial devices from a traveler run"),
    "Diamond hole mobility": ("B3", "Hall and four-point measurement on doped single-crystal diamond"),
    "Diamond permittivity": (None, "literature review (well known)"),
    "SiC critical field": (None, "literature review of commercial 4H-SiC"),
    "SiC electron mobility": (None, "literature review of commercial 4H-SiC"),
    "Readout time": ("C1", "single-shot readout on a single NV by photon counting or photocurrent"),
    "Nuclear memory T₂": ("C1", "nuclear-spin echo while the electron is read out"),
    "Two-qubit gate time": ("D1", "dipolar coupling of implanted pairs"),
    "Ancilla preparation": ("C1", "charge-state verified initialization time"),
    "Layout overhead": (None, "architecture simulation (routing and lattice surgery)"),
}


def experiment_cost(eid: str | None) -> float:
    if eid is None:
        return DESK
    from .experiments import EXPERIMENTS
    lo, hi = next(e["cost"] for e in EXPERIMENTS if e["id"] == eid)
    return math.sqrt(max(lo, 1.0) * hi)


def _model(study: str):
    space, fn, label = U.STUDIES[study]
    if study == "quantum":
        from . import resource
        tab = resource.table()
        return space, (lambda p: math.log10(max(fn(p, tab), 1e-6))), "log10 " + label
    return space, fn, label


def sobol(study: str, n: int = 16000, seed: int = 21) -> list[dict]:
    """First-order (Jansen) and total (Jansen) Sobol indices for every input of an uncertainty study (cached)."""
    return [dict(r) for r in _sobol(study, n, seed)]


@functools.lru_cache(maxsize=16)
def _sobol(study: str, n: int, seed: int) -> tuple:
    space, f, _ = _model(study)
    names = list(space)
    A, B = U.sample(space, n, seed), U.sample(space, n, seed + 1)
    fA = np.array([f(p) for p in A]); fB = np.array([f(p) for p in B])
    var = np.var(np.concatenate([fA, fB]))
    out = []
    for k in names:
        fAB = np.array([f({**a, k: b[k]}) for a, b in zip(A, B)])     # A with column k taken from B
        s1 = (var - 0.5 * np.mean((fB - fAB) ** 2)) / var
        st = 0.5 * np.mean((fA - fAB) ** 2) / var
        out.append({"name": k, "S1": float(max(0.0, s1)), "ST": float(st)})
    out.sort(key=lambda r: r["S1"], reverse=True)
    return tuple(out)


def roadmap(n: int = 16000) -> list[dict]:
    """Every uncertain input ranked by variance removed per dollar of the measurement that pins it down."""
    rows = []
    for study in ("power", "quantum"):
        for r in sobol(study, n):
            eid, what = MEASURE[r["name"]]
            cost = experiment_cost(eid)
            resolved = r["S1"] >= RESOLUTION
            rows.append({**r, "study": study, "experiment": eid or "desk study", "what": what, "cost_usd": cost, "resolved": resolved,
                         "S1_per_10k": 1e4 * r["S1"] / cost if resolved else 0.0})
    rows.sort(key=lambda r: r["S1_per_10k"], reverse=True)
    return rows


# ---------------------------------------------------------------- the code decision under unknown gate-noise bias
JOB = "RSA-2048 scale (6,000 logical, 3×10⁹ steps)"


def payoff(t_read_us: float = 1000.0, t2_mem_ms: float = 1000.0) -> dict:
    """Physical qubits (millions) and runtime (years) for each code at each simulated bias, native circuits."""
    from . import resource as R
    n, st = R.WORKLOADS[JOB]
    out = {}
    for code in ("css", "xzzx"):
        for eta in R.BIAS_GRID:
            e = R.estimate(n, st, t_read_us, t2_mem_ms, t=R.table_eta(code, eta))
            out[(code, eta)] = (float("inf"), float("inf"), None) if e is None else (e.physical_qubits / 1e6, e.runtime_hours / 8766, e.distance)
    return out


def code_decision(prior: dict | None = None, t_read_us: float = 1000.0, metric: int = 0) -> dict:
    """Expected cost of each code under the prior on the bias, the regret table, and the EVPI on the bias.
    metric 0 = millions of physical qubits, 1 = runtime in years (both lower is better)."""
    from . import resource as R
    prior = prior or {eta: 1 / len(R.BIAS_GRID) for eta in R.BIAS_GRID}
    P = payoff(t_read_us)
    exp = {c: sum(prior[e] * P[(c, e)][metric] for e in prior) for c in ("css", "xzzx")}
    best_now = min(exp, key=exp.get)
    with_info = sum(prior[e] * min(P[("css", e)][metric], P[("xzzx", e)][metric]) for e in prior)
    regret = {(c, e): P[(c, e)][metric] - min(P[("css", e)][metric], P[("xzzx", e)][metric]) for c in ("css", "xzzx") for e in prior}
    dominates = all(P[("xzzx", e)][metric] <= P[("css", e)][metric] for e in prior)
    return {"prior": prior, "expected": exp, "choice": best_now, "evpi": exp[best_now] - with_info, "regret": regret,
            "xzzx_dominates": dominates, "payoff": P}


def to_json() -> dict:
    from . import resource as R
    d = code_decision(); dy = code_decision(metric=1)
    return {"roadmap": roadmap(),
            "decision": {"etas": list(R.BIAS_GRID),
                         "qubits_m": {c: [d["payoff"][(c, e)][0] for e in R.BIAS_GRID] for c in ("css", "xzzx")},
                         "years": {c: [d["payoff"][(c, e)][1] for e in R.BIAS_GRID] for c in ("css", "xzzx")},
                         "distance": {c: [d["payoff"][(c, e)][2] for e in R.BIAS_GRID] for c in ("css", "xzzx")},
                         "expected_qubits_m": d["expected"], "evpi_qubits_m": d["evpi"], "evpi_years": dy["evpi"],
                         "choice": d["choice"], "xzzx_dominates": d["xzzx_dominates"] and dy["xzzx_dominates"]}}
