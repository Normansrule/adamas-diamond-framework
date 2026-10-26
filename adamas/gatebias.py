"""Why only a CZ gate keeps a noise bias on two-level qubits (chapter E6.1e, audit E9).

The XZZX code gains when qubits mostly suffer phase (Z) errors [bonillaataides2021]. A gate keeps that bias only if a Z
error that happens while the gate runs leaves the gate as a Z error. A CZ gate is diagonal, so it commutes with Z: the
bias survives. Two-level hardware usually builds a CNOT as a CZ between two Hadamards on the target. A Z error on the
target in the middle of that sequence is conjugated by the second Hadamard into an X error, and an X error before the
CZ spreads a Z onto the control. A CNOT that keeps the bias needs a continuous-symmetry trick that two-level systems
lack [guillaud2019] [puri2020]; careful two-level designs keep only a residual bias, about 5 [etxezarreta2025].

Model (a teaching model of this repository): the gate is a list of segments, each lasting a fraction of the gate time;
after each segment each qubit suffers an independent Pauli error with probability proportional to the segment's
duration, biased with eta = p_Z / (p_X + p_Y). Errors are propagated to the end of the gate by Clifford conjugation (the
symplectic rules below, checked against Stim's PauliString.after in the tests [gidney2021stim]). Output: the Pauli
distribution on each qubit to first order in p, and its bias eta_out = P(Z) / (P(X) + P(Y)) per qubit. Errors sit at
the end of each segment, so an X error partway through the CZ (which would also leave a Z on the other qubit) is not
counted: the spread fraction is a lower bound.
"""
from __future__ import annotations

PAULI = {(0, 0): "I", (1, 0): "X", (1, 1): "Y", (0, 1): "Z"}


def _conj(gate: str, qubits: tuple, x: list, z: list) -> None:
    """Conjugate the Pauli string (x, z bit lists) through one Clifford gate, in place (phases ignored)."""
    if gate == "H":
        (q,) = qubits; x[q], z[q] = z[q], x[q]
    elif gate == "CZ":
        a, b = qubits; z[a] ^= x[b]; z[b] ^= x[a]
    elif gate == "CX":
        c, t = qubits; x[t] ^= x[c]; z[c] ^= z[t]
    else:
        raise ValueError(gate)


def propagate(error: dict, after: list) -> dict:
    """Push a Pauli error {qubit: 'X'|'Y'|'Z'} through the gate list `after` [(name, qubits)]; return {qubit: Pauli}."""
    n = 2; x = [0] * n; z = [0] * n
    for q, p in error.items():
        x[q] = 1 if p in "XY" else 0; z[q] = 1 if p in "YZ" else 0
    for g, qs in after:
        _conj(g, qs, x, z)
    return {q: PAULI[(x[q], z[q])] for q in range(n)}


# Gate constructions: (segments [(gate, qubits, duration)]); qubit 0 is the control, 1 the target.
def construction(kind: str, h_frac: float = 0.002) -> list:
    """'cz': one CZ segment. 'cnot': H on the target, CZ, H on the target (how two-level hardware usually builds a CNOT).
    h_frac: duration of a Hadamard relative to the CZ (an NV microwave pi/2 pulse of tens of ns against a 25 us dipolar
    gate is about 0.002)."""
    if kind == "cz":
        return [("CZ", (0, 1), 1.0)]
    if kind == "cnot":
        return [("H", (1,), h_frac), ("CZ", (0, 1), 1.0), ("H", (1,), h_frac)]
    raise ValueError(kind)


def output_distribution(kind: str, eta: float, h_frac: float = 0.002) -> dict:
    """First-order output error distribution per qubit: {qubit: {'X': w, 'Y': w, 'Z': w}} normalized over error events,
    plus the spread fraction (events that leave errors on both qubits)."""
    seg = construction(kind, h_frac); tot = sum(d for *_, d in seg)
    pin = {"X": 1 / (2 * (eta + 1)), "Y": 1 / (2 * (eta + 1)), "Z": eta / (eta + 1)}
    out = {0: {"X": 0.0, "Y": 0.0, "Z": 0.0}, 1: {"X": 0.0, "Y": 0.0, "Z": 0.0}}; spread = 0.0; weight = 0.0
    for k, (_, _, dur) in enumerate(seg):
        rest = [(g, qs) for g, qs, _ in seg[k + 1:]]
        for q in (0, 1):
            for p, w in pin.items():
                ww = w * dur / tot; weight += ww
                res = propagate({q: p}, rest)
                hit = [r for r in res if res[r] != "I"]
                for r in hit:
                    out[r][res[r]] += ww
                if len(hit) == 2:
                    spread += ww
    return {"per_qubit": out, "spread": spread / weight, "weight": weight}


def output_bias(kind: str, eta: float, h_frac: float = 0.002) -> dict:
    """Bias eta_out = P(Z) / (P(X) + P(Y)) of the errors each qubit carries out of the gate."""
    d = output_distribution(kind, eta, h_frac)["per_qubit"]
    return {q: (d[q]["Z"] / (d[q]["X"] + d[q]["Y"]) if d[q]["X"] + d[q]["Y"] > 0 else float("inf")) for q in d}
