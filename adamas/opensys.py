"""Open-quantum-system models for NV qubits: a Lindblad two-qubit gate, a nuclear-spin bath, and
dynamical-decoupling filter functions.

1. Lindblad master equation [lindblad1976], [gorini1976] (same formalism as QuTiP [johansson2012]):
       d rho / dt = -i [H, rho] + sum_k ( c_k rho c_k^dag - 1/2 { c_k^dag c_k, rho } )
   Two NV electron-spin qubits with dipolar interaction H = 2 pi nu_dd |11><11| [dolde2013]; pure dephasing
   c = sqrt(1 / (2 T2)) sigma_z on each spin and symmetric relaxation at 1 / (2 T1) each way [jarmola2012].
2. Carbon-13 bath, quasi-static secular approximation [maze2008prb], [dobrovitski2008], [zhao2012]:
       sigma^2 = 1/4 sum_k A_zz,k^2,   coherence = exp(-(t / T2*)^2),   T2* = sqrt(2) / (2 pi sigma)
   A full treatment needs the cluster-correlation expansion [yang2008]; that is proposed experiment S-3.
3. Decoupling [hahn1950], [carr1954], [meiboom1958], [viola1999] against Ornstein-Uhlenbeck noise of strength b and
   correlation time tau_c [delange2010]:  chi(t) = 1/2 int int y(t1) y(t2) b^2 exp(-|t1 - t2| / tau_c),
   with y = +/-1 the switching function [cywinski2008]. For a slow bath T2 grows as N^(2/3) [delange2010], [bargill2013].
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import expm
from .constants import MU0, HBAR, GAMMA_E_HZ_PER_T, GAMMA_13C_HZ_PER_T
from .coupling import dipolar_coupling_khz

SZ = np.diag([1.0, -1.0]).astype(complex)
SM = np.array([[0, 1], [0, 0]], dtype=complex)
I2 = np.eye(2, dtype=complex)


def liouvillian(h: np.ndarray, c_ops: list[np.ndarray]) -> np.ndarray:
    """Column-stacking convention: vec(A rho B) = (B^T kron A) vec(rho)."""
    n = h.shape[0]
    eye = np.eye(n, dtype=complex)
    l = -1j * (np.kron(eye, h) - np.kron(h.T, eye))
    for c in c_ops:
        cdc = c.conj().T @ c
        l += np.kron(c.conj(), c) - 0.5 * np.kron(eye, cdc) - 0.5 * np.kron(cdc.T, eye)
    return l


def cz_gate_fidelity(r_nm: float, t2_ms: float = 1.8, t1_ms: float = 6.0) -> float:
    """State fidelity of |++> -> CZ|++> for two NVs r_nm apart, with Markovian T2 and T1 on both spins."""
    nu = float(dipolar_coupling_khz(r_nm)) * 1e-3                 # MHz
    t_gate = 1.0 / (2 * nu)                                        # microseconds
    h = np.zeros((4, 4), dtype=complex)
    h[3, 3] = 2 * np.pi * nu
    g_phi, g_1 = 1.0 / (t2_ms * 1e3), 1.0 / (t1_ms * 1e3)
    g_phi = max(g_phi - g_1 / 2, 0.0)                              # 1/T2 = 1/(2 T1) + 1/T_phi
    c_ops = []
    for op in (lambda a: np.kron(a, I2), lambda a: np.kron(I2, a)):
        c_ops += [np.sqrt(g_phi / 2) * op(SZ), np.sqrt(g_1 / 2) * op(SM), np.sqrt(g_1 / 2) * op(SM.conj().T)]
    plus = np.ones(4, dtype=complex) / 2
    rho0 = np.outer(plus, plus.conj())
    rho_t = (expm(liouvillian(h, c_ops) * t_gate) @ rho0.reshape(-1, order="F")).reshape(4, 4, order="F")
    target = np.diag([1, 1, 1, -1]) @ plus
    return float(np.real(target.conj() @ rho_t @ target))


# ---- carbon-13 bath ----
A_NM = 0.3567
E_13C_KHZ_NM3 = MU0 / (4 * np.pi) * (2 * np.pi * GAMMA_E_HZ_PER_T) * (2 * np.pi * GAMMA_13C_HZ_PER_T) * HBAR \
    / (2 * np.pi) * 1e27 * 1e-3                                    # about 19.8 kHz nm^3


def _lattice(radius_nm: float) -> np.ndarray:
    n = int(np.ceil(radius_nm / A_NM)) + 1
    g = np.arange(-n, n + 1)
    cells = np.stack(np.meshgrid(g, g, g, indexing="ij"), -1).reshape(-1, 3)
    basis = np.array([[0, 0, 0], [0, .5, .5], [.5, 0, .5], [.5, .5, 0]])
    basis = np.vstack([basis, basis + 0.25])
    pts = (cells[:, None, :] + basis[None, :, :]).reshape(-1, 3) * A_NM
    r = np.linalg.norm(pts, axis=1)
    return pts[(r > 0.2) & (r <= radius_nm)]


def t2star_us_c13(concentration: float = 0.011, radius_nm: float = 4.0, samples: int = 200,
                  strong_cut_khz: float = 200.0, seed: int = 7) -> np.ndarray:
    """T2* (microseconds) for `samples` random carbon-13 configurations. Nuclei coupled more strongly than
    strong_cut_khz give resolved lines, not dephasing, and are excluded (a simplification of this repository)."""
    rng = np.random.default_rng(seed)
    pts = _lattice(radius_nm)
    r = np.linalg.norm(pts, axis=1)
    cos = pts @ (np.ones(3) / np.sqrt(3)) / r
    a_zz = E_13C_KHZ_NM3 * (1 - 3 * cos ** 2) / r ** 3            # kHz
    a_zz = np.where(np.abs(a_zz) > strong_cut_khz, 0.0, a_zz)
    out = np.empty(samples)
    for i in range(samples):
        occ = rng.random(len(pts)) < concentration
        sigma_khz = 0.5 * np.sqrt(np.sum(a_zz[occ] ** 2))
        out[i] = np.inf if sigma_khz == 0 else np.sqrt(2) / (2 * np.pi * sigma_khz) * 1e3
    return out


# ---- dynamical decoupling ----
def cpmg_coherence(t_us, n_pulses: int, b_per_us: float = 3.6, tau_c_us: float = 25.0, grid: int = 1200) -> np.ndarray:
    """Coherence after total time t under n equally spaced pi pulses (n = 0 free decay, n = 1 Hahn echo).
    Default bath parameters are those measured in [delange2010]."""
    t_us = np.atleast_1d(np.asarray(t_us, dtype=float))
    out = np.empty_like(t_us)
    u = (np.arange(grid) + 0.5) / grid
    y = np.ones(grid)
    for j in range(1, n_pulses + 1):
        y[u > (j - 0.5) / n_pulses] *= -1
    for i, t in enumerate(t_us):
        tt = u * t
        c = b_per_us ** 2 * np.exp(-np.abs(tt[:, None] - tt[None, :]) / tau_c_us)
        out[i] = np.exp(-0.5 * (y @ c @ y) * (t / grid) ** 2)
    return out


def t2_under_cpmg_us(n_pulses: int, **kw) -> float:
    t = np.logspace(-1, 3, 160)
    w = cpmg_coherence(t, n_pulses, **kw)
    return float(np.interp(np.exp(-1), w[::-1], t[::-1]))
