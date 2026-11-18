"""Error-correction arithmetic mapped onto NV cells.

Surface code [kitaev2003], [dennis2002]; heuristic scaling per round per patch (a widely used rule of thumb,
e.g. [fowlergidney2018]; Fowler et al. give P_L ~ 0.03 (p / 0.57%)^d_e for their circuit model [fowler2012]):
    p_L ~ 0.1 (p / p_th)^((d + 1) / 2),  p_th ~ 1e-2; rotated layout, physical qubits per logical = 2 d^2 - 1 [litinski2019]
Three-qubit repetition code [shor1995], demonstrated in room-temperature diamond by [waldherr2014]:
    p_L = 3 p^2 - 2 p^3
The same three qubits in the Hadamard basis correct one phase flip instead, with the same p_L (a theorem; v0.50.0).
Nine-qubit code [shor1995]: three phase-flip blocks of three bit-flip qubits each, correcting one bit flip and one phase
flip. With independent bit flips (probability px) and phase flips (pz) on each qubit (v0.50.0, derived here and checked by
exhaustive decoding in `shor9_exhaustive`):
    a block fails on bit flips with q = 3 px^2 - 2 px^3; the code fails on bit flips when an odd number of blocks fail;
    a block's sign flips with s = probability of an odd number of phase flips among its 3 qubits; the code fails on
    phase flips when the majority vote of the 3 signs fails, 3 s^2 - 2 s^3.
Lower-overhead quantum low-density parity-check codes exist [bravyi2024] and need long-range links.
"""
from __future__ import annotations
import math


def surface_code_logical_error(p: float, d: int, p_th: float = 1e-2, prefactor: float = 0.1) -> float:
    return prefactor * (p / p_th) ** ((d + 1) / 2)


def surface_code_qubits(d: int) -> int:
    return 2 * d * d - 1


def distance_for_target(p: float, target: float, p_th: float = 1e-2) -> int | None:
    if p >= p_th:
        return None
    d = 3
    while surface_code_logical_error(p, d, p_th) > target * (1 + 1e-9):   # tolerance: 0.1*0.1**8 is 1.0000000000000005e-9 in floating point
        d += 2
        if d > 2001:
            return None
    return d


def repetition_logical_error(p: float) -> float:
    return 3 * p ** 2 - 2 * p ** 3


def nv_cells_needed(n_logical: int, p: float, target: float, qubits_per_cell: int = 4) -> dict | None:
    """qubits_per_cell: one electron plus nuclear memories ([bradley2019] controlled 10 at 4 K; 3 to 4 is realistic at 300 K)."""
    d = distance_for_target(p, target)
    if d is None:
        return None
    q = n_logical * surface_code_qubits(d)
    return {"distance": d, "physical_qubits": q, "nv_cells": math.ceil(q / qubits_per_cell)}


# ------------------------------------------------------------------------------------- phase flips and the nine-qubit code
def phase_flip_logical_error(p: float) -> float:
    """Three-qubit phase-flip code (the repetition code in the Hadamard basis): fails on two or more phase flips."""
    return repetition_logical_error(p)


def _odd3(p: float) -> float:
    """Probability of an odd number of events among three independent ones of probability p."""
    return 3 * p * (1 - p) ** 2 + p ** 3


def shor9_logical_error(px: float, pz: float) -> dict:
    """Nine-qubit code [shor1995] under independent bit flips (px) and phase flips (pz) on every qubit."""
    q = repetition_logical_error(px)                 # one block's majority vote fails
    fx = _odd3(q)                                    # odd number of failed blocks: a logical error (two cancel, a stabilizer)
    fz = repetition_logical_error(_odd3(pz))         # majority vote of the three block signs fails
    return {"bit": fx, "phase": fz, "total": 1 - (1 - fx) * (1 - fz)}


# Parity checks of the nine-qubit code as bit vectors over qubits 1..9 (qubit 1 is the highest bit).
_ZCHECKS = [0b110000000, 0b011000000, 0b000110000, 0b000011000, 0b000000110, 0b000000011]   # detect bit flips
_XCHECKS = [0b111111000, 0b000111111]                                                        # detect phase flips


def _span(vecs):
    out = {0}
    for v in vecs:
        out |= {x ^ v for x in out}
    return out


def _syndrome(e: int, checks) -> tuple:
    return tuple(bin(e & c).count("1") & 1 for c in checks)


def _fail_prob(p: float, checks, stabilizers) -> float:
    """Exact failure probability of a minimum-weight lookup decoder for one error type, by enumerating all 2^9 patterns."""
    best = {}
    for e in sorted(range(512), key=lambda x: bin(x).count("1")):     # lightest pattern first for each syndrome
        best.setdefault(_syndrome(e, checks), e)
    stab = _span(stabilizers)
    fail = 0.0
    for e in range(512):
        w = bin(e).count("1")
        if (e ^ best[_syndrome(e, checks)]) not in stab:
            fail += p ** w * (1 - p) ** (9 - w)
    return fail


def shor9_exhaustive(px: float, pz: float) -> dict:
    """The same failure probabilities as `shor9_logical_error`, from exhaustive minimum-weight decoding (a check of the formula)."""
    fx = _fail_prob(px, _ZCHECKS, _XCHECKS)          # residual bit-flip pattern is harmless if it is an X-type stabilizer
    fz = _fail_prob(pz, _XCHECKS, _ZCHECKS)
    return {"bit": fx, "phase": fz, "total": 1 - (1 - fx) * (1 - fz)}


def shor9_break_even(tol: float = 1e-12) -> float:
    """Flip probability p (bit and phase flips both p, independent) below which the nine-qubit code fails less often than one
    unencoded qubit, 1 - (1 - p)^2. Found by bisection on (0, 0.25); above it the code is worse until both reach 3/4 at p = 1/2."""
    g = lambda p: shor9_logical_error(p, p)["total"] - (1 - (1 - p) ** 2)   # noqa: E731
    lo, hi = 1e-6, 0.25
    if g(lo) >= 0 or g(hi) <= 0:
        raise ValueError("no break-even point in (0, 0.25)")
    while hi - lo > tol:
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if g(mid) < 0 else (lo, mid)
    return (lo + hi) / 2


def repetition_both(p: float) -> float:
    """Three-qubit bit-flip code under independent bit and phase flips of probability p: it corrects one bit flip, but any odd
    number of phase flips is a logical phase error (a single Z on any qubit acts on the encoded state)."""
    return 1 - (1 - repetition_logical_error(p)) * (1 - _odd3(p))


def figure(out="docs/img"):
    """Figure 64: logical failure of no code, the three-qubit code and the nine-qubit code [shor1995] when every qubit suffers
    independent bit and phase flips of probability p (simulated: exact formulas)."""
    from pathlib import Path
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    ps = np.logspace(-3, np.log10(0.5), 200)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.loglog(ps, [1 - (1 - p) ** 2 for p in ps], color="#555555", lw=2.4, label="one unencoded qubit: 1 − (1 − p)²")
    ax.loglog(ps, [repetition_both(p) for p in ps], color="#d1495b", lw=2.4, label="three-qubit bit-flip code: corrects bit flips only, worse than no code here")
    ax.loglog(ps, [shor9_logical_error(p, p)["total"] for p in ps], color="#00798c", lw=2.4, label="nine-qubit code [shor1995]: corrects one bit flip and one phase flip")
    b = shor9_break_even()
    ax.axvline(b, color="#00798c", ls=":", lw=1.4)
    ax.annotate(f"break-even p = {b:.3f}", (b, 2e-5), xytext=(6, 0), textcoords="offset points", color="#00798c")
    ax.set_xlabel("Probability p of a bit flip, and separately of a phase flip, on each qubit")
    ax.set_ylabel("Probability of a logical error (bit, phase or both)")
    ax.set_ylim(1e-5, 1)
    ax.set_title("Error correction against both error types (simulated: exact formulas)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=1, frameon=False)
    fig.tight_layout()
    p = out / "fig64_qec_codes.png"; fig.savefig(p, dpi=150); plt.close(fig)
    return p
