"""Circuit-level surface-code memory for NV cells (project X-1b), using Stim [gidney2021stim] and PyMatching [higgott2022].

Why a second error-correction model: adamas.surface_sim treats noise phenomenologically. Real syndrome extraction is a
circuit of resets, CNOTs, and measurements, where one gate fault can spread to two qubits ("hook" errors), and where the
data qubits sit idle while the ancilla is read out. For NV hardware that idle time is the dominant new effect: electron
readout by repetitive nuclear-assisted measurement takes 0.1 to 10 ms [neumann2010science] [hopper2018], while the data
live in nuclear spins whose memory under illumination is of order a second with decoupling [maurer2012].

Circuit: Stim's rotated surface-code Z memory with d rounds [fowler2012] [gidney2021stim]. Noise mapping (a model of this
repository, first order):
    after every CNOT             two-qubit depolarizing, p_link   (one data qubit per cell: every CNOT crosses cells)
    before every measurement     bit flip, p_meas                 (readout error)
    after every reset            bit flip, p_init                 (ancilla preparation, e.g. wrong charge state [aslam2013])
    before every round, on data  depolarizing, p_idle = 3/4 * (1 - exp(-t_read / T2_mem))
The last line is the hardware-specific term: a slower readout directly raises the data error per round.
"""
from __future__ import annotations
import math
import numpy as np

try:
    import stim
    import pymatching
except ImportError:                       # optional:  pip install stim pymatching
    stim = None
    pymatching = None


def p_idle(t_read_us: float, t2_mem_ms: float) -> float:
    return 0.75 * (1.0 - math.exp(-t_read_us / (t2_mem_ms * 1e3)))


def circuit(d: int, rounds: int, p_link: float, p_meas: float, p_init: float = 0.0, p_data: float = 0.0):
    if stim is None:
        raise ImportError("circuit_qec needs Stim and PyMatching:  pip install stim pymatching")
    return stim.Circuit.generated("surface_code:rotated_memory_z", distance=d, rounds=rounds,
                                  after_clifford_depolarization=p_link, before_measure_flip_probability=p_meas,
                                  after_reset_flip_probability=p_init, before_round_data_depolarization=p_data)


def logical_error(d: int, p_link: float, p_meas: float, p_init: float = 0.0, p_data: float = 0.0,
                  rounds: int | None = None, shots: int = 20000, seed: int = 1) -> tuple[float, float]:
    """Returns (logical error per round, total logical error after `rounds` rounds)."""
    rounds = d if rounds is None else rounds
    c = circuit(d, rounds, p_link, p_meas, p_init, p_data)
    m = pymatching.Matching.from_detector_error_model(c.detector_error_model(decompose_errors=True))
    det, obs = c.compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    p_total = float(np.mean(m.decode_batch(det)[:, 0] != obs[:, 0]))
    p_round = 0.5 * (1.0 - max(1.0 - 2.0 * p_total, 1e-12) ** (1.0 / rounds))
    return p_round, p_total


def nv_logical_error(d: int, t_read_us: float, p_link: float = 3e-3, p_meas: float = 1e-2, p_init: float = 2e-3,
                     t2_mem_ms: float = 1000.0, **kw) -> float:
    return logical_error(d, p_link, p_meas, p_init, p_idle(t_read_us, t2_mem_ms), **kw)[0]


def max_readout_time_us(p_link: float = 3e-3, p_meas: float = 1e-2, p_init: float = 2e-3, t2_mem_ms: float = 1000.0,
                        d_small: int = 3, d_large: int = 7, shots: int = 20000) -> float:
    """Longest readout time for which the larger code still beats the smaller one (bisection in log time)."""
    lo, hi = 1.0, 1e6
    for _ in range(12):
        mid = math.sqrt(lo * hi)
        a = nv_logical_error(d_small, mid, p_link, p_meas, p_init, t2_mem_ms, shots=shots, seed=3)
        b = nv_logical_error(d_large, mid, p_link, p_meas, p_init, t2_mem_ms, shots=shots, seed=7)
        lo, hi = (mid, hi) if b < a else (lo, mid)
    return math.sqrt(lo * hi)
