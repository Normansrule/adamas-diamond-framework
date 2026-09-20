"""Monte Carlo surface-code memory with three separate error rates (expert-track project X-1).

Code: planar surface code of distance d, decoding bit-flip (X) errors; phase-flip errors behave identically by
symmetry [dennis2002], [fowler2012]. Checks sit on a d x (d - 1) grid, data qubits are the d^2 + (d - 1)^2 edges,
and a logical error is a chain that joins the left boundary to the right boundary.

Noise: phenomenological [dennis2002], [wang2003]. Every round each data qubit flips with probability p_d and each
syndrome bit is misread with probability p_m; `rounds` noisy rounds are followed by one perfect round. For
p_d = p_m the threshold under matching is about 2.9 to 3.0 percent [wang2003], which the test suite reproduces.

Decoder: minimum-weight perfect matching [edmonds1965] on the space-time graph, through PyMatching [higgott2022],
with edge weights ln((1 - p)/p).

Mapping NV hardware onto the two phenomenological rates (first order; a model of this repository):
    each round a data qubit idles or is gated inside its cell (p_intra) and takes part in 4 two-qubit gates with
    ancillas; when data and ancilla sit in different NV cells those gates use the inter-cell link (p_link).
    Of the 15 two-qubit Pauli errors, 8 put a bit-flip component on a given qubit, so
        p_d = p_intra + 4 (8/15) f_link p_link          p_m = p_meas + 4 (8/15) f_link p_link
    where f_link is the fraction of syndrome gates that cross cells (1 = one qubit per cell, 0 = whole patch in
    one cell). Hook errors and correlated faults need a circuit-level model: that is follow-up project X-1b.
"""
from __future__ import annotations
import numpy as np
from scipy import sparse

try:
    import pymatching
except ImportError:                      # optional dependency:  pip install pymatching
    pymatching = None

BITFLIP_FRACTION = 8 / 15


def effective_rates(p_intra: float, p_link: float, p_meas: float, f_link: float = 1.0) -> tuple[float, float]:
    extra = 4 * BITFLIP_FRACTION * f_link * p_link
    return min(p_intra + extra, 0.5), min(p_meas + extra, 0.5)


def build_graph(d: int, rounds: int, p_d: float, p_m: float):
    """Returns (matching, check_matrix [nodes x edges], edge_probabilities, logical_mask)."""
    if pymatching is None:
        raise ImportError("surface_sim needs PyMatching:  pip install pymatching")
    rows, cols, layers = d, d - 1, rounds + 1
    node = lambda t, r, c: (t * rows + r) * cols + c                       # noqa: E731
    n_nodes = layers * rows * cols
    us, vs, ps, logical = [], [], [], []                                   # v = -1 means boundary
    for t in range(layers):
        for r in range(rows):
            for c in range(cols + 1):                                      # d horizontal edges per row
                left = node(t, r, c - 1) if c > 0 else -1
                right = node(t, r, c) if c < cols else -1
                u, v = (left, right) if left >= 0 else (right, -1)
                us.append(u); vs.append(v); ps.append(p_d); logical.append(c == 0)
        for r in range(rows - 1):                                          # (d - 1)^2 vertical edges
            for c in range(cols):
                us.append(node(t, r, c)); vs.append(node(t, r + 1, c)); ps.append(p_d); logical.append(False)
    for t in range(layers - 1):                                            # measurement errors: time-like edges
        for r in range(rows):
            for c in range(cols):
                us.append(node(t, r, c)); vs.append(node(t + 1, r, c)); ps.append(p_m); logical.append(False)
    ps = np.clip(np.array(ps), 1e-12, 0.5 - 1e-12)
    m = pymatching.Matching()
    for u, v, p, lg in zip(us, vs, ps, logical):
        w = float(np.log((1 - p) / p))
        if v < 0:
            m.add_boundary_edge(u, fault_ids={0} if lg else set(), weight=w)
        else:
            m.add_edge(u, v, fault_ids={0} if lg else set(), weight=w)
    e = len(us)
    idx = np.arange(e)
    us_a, vs_a = np.array(us), np.array(vs)
    keep = vs_a >= 0
    h = sparse.csr_matrix((np.ones(e + keep.sum(), dtype=np.uint8),
                           (np.concatenate([us_a, vs_a[keep]]), np.concatenate([idx, idx[keep]]))), shape=(n_nodes, e))
    return m, h, ps, np.array(logical)


def logical_error_rate(d: int, p_d: float, p_m: float, shots: int = 4000, rounds: int | None = None,
                       seed: int = 1) -> tuple[float, float]:
    """Probability that a d-round memory experiment ends in a logical bit flip, and its one-sigma uncertainty."""
    rounds = d if rounds is None else rounds
    m, h, ps, logical = build_graph(d, rounds, p_d, p_m)
    rng = np.random.default_rng(seed)
    fails = 0
    for start in range(0, shots, 2000):                                    # chunks keep memory small
        n = min(2000, shots - start)
        errs = (rng.random((n, len(ps))) < ps).astype(np.uint8)
        syndromes = (h @ errs.T).T % 2
        predicted = m.decode_batch(syndromes.astype(np.uint8))[:, 0]
        actual = errs[:, logical].sum(axis=1) % 2
        fails += int(np.sum(predicted != actual))
    p = fails / shots
    return p, float(np.sqrt(max(p * (1 - p), 1.0 / shots) / shots))


def nv_logical_error(d: int, p_intra: float, p_link: float, p_meas: float, f_link: float = 1.0, **kw) -> tuple[float, float]:
    return logical_error_rate(d, *effective_rates(p_intra, p_link, p_meas, f_link), **kw)


def threshold_estimate(d_small: int = 5, d_large: int = 9, lo: float = 0.015, hi: float = 0.045, shots: int = 6000,
                       steps: int = 7) -> float:
    """Crossing point of two distances for p_d = p_m, by bisection on the sign of the difference."""
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        a, _ = logical_error_rate(d_small, mid, mid, shots, seed=11)
        b, _ = logical_error_rate(d_large, mid, mid, shots, seed=12)
        if b < a:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
