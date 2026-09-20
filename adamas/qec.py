"""Error-correction arithmetic mapped onto NV cells.

Surface code [kitaev2003], [dennis2002], [fowler2012]:
    p_L ~ 0.1 (p / p_th)^((d + 1) / 2),  p_th ~ 1e-2,  physical qubits per logical qubit = 2 d^2 - 1
Three-qubit repetition code [shor1995], demonstrated in room-temperature diamond by [waldherr2014]:
    p_L = 3 p^2 - 2 p^3
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
    while surface_code_logical_error(p, d, p_th) > target:
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
