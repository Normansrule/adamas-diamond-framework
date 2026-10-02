"""Native XZZX syndrome circuits with biased gate noise (project X-5): beyond the idle-noise emulation of adamas.circuit_qec.

The XZZX surface code is the CSS rotated surface code with a Hadamard applied to one checkerboard sublattice of data
qubits [bonillaataides2021]. Instead of emulating it through the noise model, this module rewrites the noiseless Stim
circuit gate by gate into a native XZZX circuit: on sublattice qubits, resets become RX, measurements become MX,
CX(ancilla -> data) becomes CZ, and CX(data -> ancilla) becomes XCX. Noise is then inserted identically into the CSS and
XZZX circuits, so hook errors (one ancilla fault spreading to two data qubits mid-sequence) appear naturally in both.

Noise model (a model of this repository): after every two-qubit gate, an independent biased Pauli channel on each of the two
qubits with total probability p and bias eta = p_Z / (p_X + p_Y) (eta = 0.5 is depolarizing); a flip before every
measurement and after every reset (p_meas, p_init); and during each ancilla readout, Z-only dephasing p_idle on every
data qubit (the nuclear-memory channel of chapter E6). Errors after ideal gates preserve the bias; for the NV dipolar
interaction, a diagonal ZZ coupling, dephasing commutes with the gate, which motivates the assumption [dolde2013]
[tuckett2018]. Decoding: PyMatching on the detector error model [higgott2022] (Y errors decomposed where possible).
"""
from __future__ import annotations
import numpy as np

try:
    import stim
    import pymatching
except ImportError:
    stim = None
    pymatching = None

TWO_QUBIT = {"CX", "CZ", "XCX"}
SWAP = {"R": "RX", "RX": "R", "M": "MX", "MX": "M"}      # a Hadamard swaps the Z and X bases


def _sublattice(c, data):
    coords = c.get_final_qubit_coordinates()
    return {q for q in data if ((int(coords[q][0]) // 2) + (int(coords[q][1]) // 2)) % 2 == 1}


def _data_qubits(c):
    coords = c.get_final_qubit_coordinates()
    return {q for q, (x, y) in coords.items() if int(x) % 2 == 1 and int(y) % 2 == 1}


def native_circuit(d: int, rounds: int, code: str = "xzzx", basis: str = "z"):
    """Noiseless rotated-memory circuit, rewritten to native XZZX if code == 'xzzx'."""
    if stim is None:
        raise ImportError("needs Stim and PyMatching:  pip install stim pymatching")
    base = stim.Circuit.generated(f"surface_code:rotated_memory_{basis}", distance=d, rounds=rounds)
    if code == "css":
        return base.flattened()
    data = _data_qubits(base); B = _sublattice(base, data)
    out = stim.Circuit()
    for ins in base.flattened():
        name, t, args = ins.name, [x.value for x in ins.targets_copy() if x.is_qubit_target], ins.gate_args_copy()
        if name in SWAP and any(q in B for q in t):
            for q in t:                          # one by one, so the measurement-record order (rec[-k]) is unchanged
                out.append(SWAP[name] if q in B else name, [q], args)
        elif name == "CX":
            for a, b in zip(t[0::2], t[1::2]):
                if b in B:                       # ancilla controls a sublattice data qubit
                    out.append("CZ", [a, b])
                elif a in B:                     # sublattice data qubit controls an ancilla
                    out.append("XCX", [a, b])
                else:
                    out.append("CX", [a, b])
        else:
            out.append(ins)
    return out


def noisy(c, p: float, eta: float, p_meas: float, p_init: float, p_idle: float):
    """Insert the biased noise model into a noiseless circuit (same rules for CSS and XZZX)."""
    pz = p * eta / (eta + 1); pxy = p / (2 * (eta + 1))
    data = _data_qubits(c); out = stim.Circuit()
    for ins in c:
        name = ins.name; t = [x.value for x in ins.targets_copy() if x.is_qubit_target]
        if name in ("M", "MR") and p_meas > 0:
            out.append("X_ERROR", t, p_meas)
        if name == "MX" and p_meas > 0:
            out.append("Z_ERROR", t, p_meas)
        out.append(ins)
        if name in TWO_QUBIT and p > 0:
            out.append("PAULI_CHANNEL_1", t, [pxy, pxy, pz])
        if name in ("R", "MR") and p_init > 0:
            out.append("X_ERROR", t, p_init)
        if name == "RX" and p_init > 0:
            out.append("Z_ERROR", t, p_init)
        if name == "MR" and p_idle > 0:              # data qubits wait in memory while the ancillas are read out
            out.append("Z_ERROR", sorted(data), p_idle)
    return out


def logical_error(d: int, p: float, eta: float, code: str = "xzzx", basis: str = "z", p_meas: float | None = None,
                  p_init: float = 0.0, p_idle: float = 0.0, rounds: int | None = None, shots: int = 20000, seed: int = 1) -> float:
    """Logical error per round."""
    rounds = d if rounds is None else rounds
    c = noisy(native_circuit(d, rounds, code, basis), p, eta, p if p_meas is None else p_meas, p_init, p_idle)
    dem = c.detector_error_model(decompose_errors=True, ignore_decomposition_failures=True)
    m = pymatching.Matching.from_detector_error_model(dem)
    det, obs = c.compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    pt = float(np.mean(m.decode_batch(det)[:, 0] != obs[:, 0]))
    return 0.5 * (1.0 - max(1.0 - 2.0 * pt, 1e-12) ** (1.0 / rounds))


def worse_basis(d, p, eta, code, **kw) -> float:
    """A memory must protect both logical bases; report the worse of the two."""
    return max(logical_error(d, p, eta, code, "z", **kw), logical_error(d, p, eta, code, "x", **kw))


def threshold(eta: float, code: str, ds=(3, 5), ps=None, shots: int = 20000) -> float:
    """Crossing of the worse-basis logical error curves for two distances (log-linear interpolation)."""
    ps = np.geomspace(2e-3, 3e-2, 9) if ps is None else ps
    a = np.array([worse_basis(ds[0], p, eta, code, shots=shots) for p in ps]); b = np.array([worse_basis(ds[1], p, eta, code, shots=shots) for p in ps])
    r = np.log(np.maximum(b, 1e-9)) - np.log(np.maximum(a, 1e-9))
    for i in range(len(ps) - 1):
        if r[i] < 0 <= r[i + 1]:
            f = -r[i] / (r[i + 1] - r[i]); return float(np.exp(np.log(ps[i]) + f * (np.log(ps[i + 1]) - np.log(ps[i]))))
    return float("nan")


def study(shots: int = 20000) -> dict:
    """Data for Figure 50: thresholds versus bias, logical error versus p at strong bias, and the NV readout scenario."""
    import math
    etas = [0.5, 1, 3, 10, 30, 100, 1000]
    out = {"etas": etas, "thr": {c: [threshold(e, c, shots=shots) for e in etas] for c in ("css", "xzzx")}}
    ps = list(np.geomspace(1.5e-3, 2.5e-2, 8))
    out["ps"] = ps
    out["curves"] = {c: {d: [worse_basis(d, p, 100, c, shots=shots) for p in ps] for d in (3, 5, 7)} for c in ("css", "xzzx")}
    tr = [100, 300, 1000, 3000, 10000, 30000, 100000]
    pid = [0.5 * (1 - math.exp(-t / 1e6)) for t in tr]                 # pure dephasing during readout, 1 s nuclear T2
    out["t_read_us"] = tr
    out["nv"] = {c: {d: [worse_basis(d, 3e-3, 100, c, p_meas=1e-2, p_init=2e-3, p_idle=q, shots=shots) for q in pid] for d in (3, 5, 7)} for c in ("css", "xzzx")}
    return out


def cached_study(path=None, shots: int = 12000) -> dict:
    """Study data from docs/data/xzzx_native.json (about a minute to regenerate with  make xzzx)."""
    import json
    from pathlib import Path
    p = Path(path) if path else Path(__file__).resolve().parents[1] / "docs" / "data" / "xzzx_native.json"
    if p.exists():
        d = json.loads(p.read_text())
        for k in ("curves", "nv"):
            d[k] = {c: {int(dd): v for dd, v in byd.items()} for c, byd in d[k].items()}
        return d
    d = study(shots); p.write_text(json.dumps(d)); return d
