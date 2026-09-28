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


_SENTINEL = 0.0123457    # marks the idle-noise instructions so they can be swapped for a biased channel


def circuit(d: int, rounds: int, p_link: float, p_meas: float, p_init: float = 0.0, p_data: float = 0.0,
            basis: str = "z", idle: str = "depolarize"):
    """Rotated surface-code memory. basis 'z' or 'x' selects which logical observable is protected in the experiment;
    idle 'depolarize' (X, Y, Z equally likely) or 'dephase' (Z only, the dominant nuclear-spin error under
    illumination, a biased channel [tuckett2018] [bonillaataides2021]) sets the data-qubit idle error per round."""
    if stim is None:
        raise ImportError("circuit_qec needs Stim and PyMatching:  pip install stim pymatching")
    c = stim.Circuit.generated(f"surface_code:rotated_memory_{basis}", distance=d, rounds=rounds,
                               after_clifford_depolarization=float(p_link), before_measure_flip_probability=float(p_meas),
                               after_reset_flip_probability=float(p_init), before_round_data_depolarization=_SENTINEL if p_data > 0 else 0.0)
    p_data = float(p_data)          # numpy 2 prints np.float64(...) in repr, which Stim cannot parse
    if p_data > 0:
        if idle == "xzzx_dephase":
            # XZZX code = this CSS code with a Hadamard on one checkerboard sublattice of data qubits [bonillaataides2021].
            # A physical Z error on a Hadamard-conjugated qubit acts as an X error in the CSS frame, so Z-only idle noise
            # on the XZZX code equals Z noise on sublattice A plus X noise on sublattice B here (gate noise is symmetric).
            coords = c.get_final_qubit_coordinates()
            data = next(ins.targets_copy() for ins in c.flattened() if ins.name == "DEPOLARIZE1" and abs(ins.gate_args_copy()[0] - _SENTINEL) < 1e-12)
            a = [t.value for t in data if ((int(coords[t.value][0]) // 2) + (int(coords[t.value][1]) // 2)) % 2 == 0]
            b = [t.value for t in data if t.value not in a]
            new = f"Z_ERROR({p_data!r}) " + " ".join(map(str, a)) + f"\nX_ERROR({p_data!r}) " + " ".join(map(str, b))
            text = "\n".join(new if l.strip().startswith(f"DEPOLARIZE1({_SENTINEL})") else l for l in str(c).splitlines())
            c = stim.Circuit(text)
        else:
            new = f"Z_ERROR({p_data!r})" if idle == "dephase" else f"DEPOLARIZE1({p_data!r})"
            c = stim.Circuit(str(c).replace(f"DEPOLARIZE1({_SENTINEL})", new))
    return c


def logical_error(d: int, p_link: float, p_meas: float, p_init: float = 0.0, p_data: float = 0.0,
                  rounds: int | None = None, shots: int = 20000, seed: int = 1, basis: str = "z", idle: str = "depolarize") -> tuple[float, float]:
    """Returns (logical error per round, total logical error after `rounds` rounds)."""
    rounds = d if rounds is None else rounds
    c = circuit(d, rounds, p_link, p_meas, p_init, p_data, basis, idle)
    m = pymatching.Matching.from_detector_error_model(c.detector_error_model(decompose_errors=True))
    det, obs = c.compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    p_total = float(np.mean(m.decode_batch(det)[:, 0] != obs[:, 0]))
    p_round = 0.5 * (1.0 - max(1.0 - 2.0 * p_total, 1e-12) ** (1.0 / rounds))
    return p_round, p_total


def nv_logical_error(d: int, t_read_us: float, p_link: float = 3e-3, p_meas: float = 1e-2, p_init: float = 2e-3,
                     t2_mem_ms: float = 1000.0, **kw) -> float:
    return logical_error(d, p_link, p_meas, p_init, p_idle(t_read_us, t2_mem_ms), **kw)[0]


def biased_idle_error(d: int, t_read_us: float, basis: str, idle: str, t2_mem_ms: float = 1000.0, p_link: float = 3e-3,
                      p_meas: float = 1e-2, p_init: float = 2e-3, **kw) -> float:
    """Logical error per round when the idle channel is depolarizing or pure dephasing, in the Z or X memory basis.
    For dephasing, p = (1 - exp(-t/T2)) / 2 is the Z-flip probability; for depolarizing the 3/4 form above is used,
    so both channels have the same total coherence loss."""
    p = 0.5 * (1.0 - math.exp(-t_read_us / (t2_mem_ms * 1e3))) if idle in ("dephase", "xzzx_dephase") else p_idle(t_read_us, t2_mem_ms)
    return logical_error(d, p_link, p_meas, p_init, p, basis=basis, idle=idle, **kw)[0]


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
