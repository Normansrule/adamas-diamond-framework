"""Native XZZX syndrome circuits with biased gate noise (project X-5): beyond the idle-noise emulation of adamas.circuit_qec.

The XZZX surface code is the CSS rotated surface code with a Hadamard applied to one checkerboard sublattice of data
qubits [bonillaataides2021]. Instead of emulating it through the noise model, this module rewrites the noiseless Stim
circuit gate by gate into a native XZZX circuit: on sublattice qubits, resets become RX, measurements become MX,
CX(ancilla -> data) becomes CZ, and CX(data -> ancilla) becomes XCX. Noise is then inserted identically into the CSS and
XZZX circuits, so hook errors (one ancilla fault spreading to two data qubits mid-sequence) appear naturally in both.

Gate set (two-level qubits). A bias-preserving CNOT is impossible for two-level qubits [guillaud2019] [puri2020]: a Z
error partway through a CNOT can leave the target with an X or Y error. Bias-preserving CZ gates are possible, because CZ is diagonal and commutes
with dephasing; for the NV dipolar interaction, a diagonal ZZ coupling, this is the native gate [dolde2013]
[etxezarreta2025]. So every ancilla that copies a Z-type data component is run in the X frame (prepared with RX, read
with MX) and talks to its data qubits through CZ, and every X-type component uses a CNOT: half the two-qubit gates are
CZ in both codes. This is the hybrid biased-depolarizing model of [etxezarreta2025]; `cz_native=False` restores the
older circuit (CX, and CZ / XCX on the XZZX sublattice only).

Noise model (a model of this repository): after every two-qubit gate, an independent biased Pauli channel on each of the
two qubits with total probability p and bias eta = p_Z / (p_X + p_Y) (eta = 0.5 is depolarizing). CZ gates keep the full
bias eta; CNOT-type gates (CX, XCX) keep at most the residual bias ETA_CNOT = 5 reported for two-level qubits
[etxezarreta2025]. `eta_cnot=None` gives every gate the full bias, the bias-preserving upper bound of
[bonillaataides2021] [tuckett2018] that earlier versions reported. A flip before every measurement and after every reset
(p_meas, p_init); and during each ancilla readout, Z-only dephasing p_idle on every data qubit (the nuclear-memory
channel of chapter E6). Decoding: PyMatching on the detector error model [higgott2022] (Y errors decomposed where
possible).
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
ETA_CNOT = 5.0          # residual bias of a CNOT on two-level qubits [etxezarreta2025]
SWAP = {"R": "RX", "RX": "R", "M": "MX", "MX": "M", "MR": "MRX", "MRX": "MR"}      # a Hadamard swaps the Z and X bases


def _sublattice(c, data):
    coords = c.get_final_qubit_coordinates()
    return {q for q in data if ((int(coords[q][0]) // 2) + (int(coords[q][1]) // 2)) % 2 == 1}


def _data_qubits(c):
    coords = c.get_final_qubit_coordinates()
    return {q for q, (x, y) in coords.items() if int(x) % 2 == 1 and int(y) % 2 == 1}


def native_circuit(d: int, rounds: int, code: str = "xzzx", basis: str = "z", cz_native: bool = True):
    """Noiseless rotated-memory circuit, rewritten to native XZZX if code == 'xzzx', then (cz_native) to the CZ-native
    gate set: Z-type ancillas move to the X frame so that their gates become CZ."""
    if stim is None:
        raise ImportError("needs Stim and PyMatching:  pip install stim pymatching")
    base = stim.Circuit.generated(f"surface_code:rotated_memory_{basis}", distance=d, rounds=rounds).flattened()
    data = _data_qubits(base)
    if code == "css":
        out = base
    else:
        B = _sublattice(base, data); out = stim.Circuit()
        for ins in base:
            name, t, args = ins.name, [x.value for x in ins.targets_copy() if x.is_qubit_target], ins.gate_args_copy()
            if name in SWAP and any(q in B for q in t):
                for q in t:                      # one by one, so the measurement-record order (rec[-k]) is unchanged
                    out.append(SWAP[name] if q in B else name, [q], args)
            elif name == "CX":
                for a, b in zip(t[0::2], t[1::2]):
                    if b in B:                   # ancilla controls a sublattice data qubit
                        out.append("CZ", [a, b])
                    elif a in B:                 # sublattice data qubit controls an ancilla
                        out.append("XCX", [a, b])
                    else:
                        out.append("CX", [a, b])
            else:
                out.append(ins)
    return _cz_frame(out, data) if cz_native else out


def _cz_frame(c, data):
    """Run every Z-frame ancilla (one without Hadamards) in the X frame: R/MR/M -> RX/MRX/MX, CX(data -> ancilla) -> CZ
    and XCX(data, ancilla) -> CX(ancilla -> data). Conjugating one qubit by H leaves the ideal measurement record unchanged."""
    hads = {x.value for ins in c if ins.name == "H" for x in ins.targets_copy()}
    anc = {x.value for ins in c if ins.name in ("MR", "MRX") for x in ins.targets_copy()} - data - hads
    out = stim.Circuit()
    for ins in c:
        name, t, args = ins.name, [x.value for x in ins.targets_copy() if x.is_qubit_target], ins.gate_args_copy()
        if name in SWAP and any(q in anc for q in t):
            for q in t:
                out.append(SWAP[name] if q in anc else name, [q], args)
        elif name in ("CX", "XCX") and any(q in anc for q in t):
            for a, b in zip(t[0::2], t[1::2]):
                if name == "CX" and b in anc:
                    out.append("CZ", [b, a])
                elif name == "XCX" and (a in anc or b in anc):
                    q, dq = (a, b) if a in anc else (b, a)
                    out.append("CX", [q, dq])
                else:
                    out.append(name, [a, b])
        else:
            out.append(ins)
    return out


def noisy(c, p: float, eta: float, p_meas: float, p_init: float, p_idle: float, eta_cnot: float | None = ETA_CNOT):
    """Insert the biased noise model into a noiseless circuit (same rules for CSS and XZZX). CZ keeps bias eta; CX and
    XCX keep min(eta, eta_cnot) (eta_cnot=None: every gate keeps eta, the bias-preserving upper bound)."""
    def chan(e):
        return [p / (2 * (e + 1)), p / (2 * (e + 1)), p * e / (e + 1)]
    full = chan(eta); cnot = full if eta_cnot is None else chan(min(eta, eta_cnot))
    data = _data_qubits(c); out = stim.Circuit(); wait = False
    for ins in c:
        name = ins.name; t = [x.value for x in ins.targets_copy() if x.is_qubit_target]
        if name in ("M", "MR") and p_meas > 0:
            out.append("X_ERROR", t, p_meas)
        if name in ("MX", "MRX") and p_meas > 0:
            out.append("Z_ERROR", t, p_meas)
        if wait and name not in ("MR", "MRX"):      # first instruction after a readout layer: dephase the data first
            out.append("Z_ERROR", sorted(data), p_idle); wait = False
        out.append(ins)
        if name in TWO_QUBIT and p > 0:
            out.append("PAULI_CHANNEL_1", t, full if name == "CZ" else cnot)
        if name in ("R", "MR") and p_init > 0:
            out.append("X_ERROR", t, p_init)
        if name in ("RX", "MRX") and p_init > 0:
            out.append("Z_ERROR", t, p_init)
        if name in ("MR", "MRX") and p_idle > 0:     # data qubits wait in memory while the ancillas are read out:
            wait = True                               # once per readout layer, which may span several instructions
    if wait:
        out.append("Z_ERROR", sorted(data), p_idle)
    return out


def logical_error(d: int, p: float, eta: float, code: str = "xzzx", basis: str = "z", p_meas: float | None = None,
                  p_init: float = 0.0, p_idle: float = 0.0, rounds: int | None = None, shots: int = 20000, seed: int = 1,
                  eta_cnot: float | None = ETA_CNOT, cz_native: bool = True) -> float:
    """Logical error per round. Defaults: CZ-native gate set, residual CNOT bias ETA_CNOT (see the module docstring)."""
    rounds = d if rounds is None else rounds
    c = noisy(native_circuit(d, rounds, code, basis, cz_native), p, eta, p if p_meas is None else p_meas, p_init, p_idle, eta_cnot)
    dem = c.detector_error_model(decompose_errors=True, ignore_decomposition_failures=True)
    m = pymatching.Matching.from_detector_error_model(dem)
    det, obs = c.compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    pt = float(np.mean(m.decode_batch(det)[:, 0] != obs[:, 0]))
    return 0.5 * (1.0 - max(1.0 - 2.0 * pt, 1e-12) ** (1.0 / rounds))


def worse_basis(d, p, eta, code, **kw) -> float:
    """A memory must protect both logical bases; report the worse of the two."""
    return max(logical_error(d, p, eta, code, "z", **kw), logical_error(d, p, eta, code, "x", **kw))


def threshold(eta: float, code: str, ds=(3, 5), ps=None, shots: int = 20000, **kw) -> float:
    """Crossing of the worse-basis logical error curves for two distances (log-linear interpolation)."""
    ps = np.geomspace(2e-3, 3e-2, 9) if ps is None else ps
    a = np.array([worse_basis(ds[0], p, eta, code, shots=shots, **kw) for p in ps]); b = np.array([worse_basis(ds[1], p, eta, code, shots=shots, **kw) for p in ps])
    r = np.log(np.maximum(b, 1e-9)) - np.log(np.maximum(a, 1e-9))
    for i in range(len(ps) - 1):
        if r[i] < 0 <= r[i + 1]:
            f = -r[i] / (r[i + 1] - r[i]); return float(np.exp(np.log(ps[i]) + f * (np.log(ps[i + 1]) - np.log(ps[i]))))
    return float("nan")


def study(shots: int = 20000) -> dict:
    """Data for Figure 50: thresholds versus bias (residual CNOT bias, and the bias-preserving upper bound), logical error
    versus p at strong bias, and the NV readout scenario."""
    import math
    etas = [0.5, 1, 3, 10, 30, 100, 1000]
    out = {"etas": etas, "eta_cnot": ETA_CNOT, "thr": {c: [threshold(e, c, shots=shots) for e in etas] for c in ("css", "xzzx")}}
    wide = np.geomspace(2e-3, 8e-2, 12)              # bias-preserving CNOTs (impossible for two-level qubits): upper bound
    out["thr_upper"] = {"xzzx": [threshold(e, "xzzx", ps=wide, shots=shots, eta_cnot=None) for e in etas]}
    ps = list(np.geomspace(1.5e-3, 2.5e-2, 8))
    out["ps"] = ps
    out["curves"] = {c: {d: [worse_basis(d, p, 100, c, shots=shots) for p in ps] for d in (3, 5, 7)} for c in ("css", "xzzx")}
    tr = [100, 300, 1000, 3000, 10000, 30000, 100000]
    pid = [0.5 * (1 - math.exp(-t / 1e6)) for t in tr]                 # pure dephasing during readout, 1 s nuclear T2
    out["t_read_us"] = tr
    out["nv"] = {c: {d: [worse_basis(d, 3e-3, 100, c, p_meas=1e-2, p_init=2e-3, p_idle=q, shots=shots) for q in pid] for d in (3, 5, 7)} for c in ("css", "xzzx")}
    return out


def cached_study(path=None, shots: int = 12000) -> dict:
    """Study data from docs/data/xzzx_native.json (about three minutes to regenerate with  make xzzx)."""
    import json
    from pathlib import Path
    p = Path(path) if path else Path(__file__).resolve().parents[1] / "docs" / "data" / "xzzx_native.json"
    if p.exists():
        d = json.loads(p.read_text())
        for k in ("curves", "nv"):
            d[k] = {c: {int(dd): v for dd, v in byd.items()} for c, byd in d[k].items()}
        return d
    d = study(shots); p.write_text(json.dumps(d)); return d
