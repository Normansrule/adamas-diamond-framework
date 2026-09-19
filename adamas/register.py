"""A two-qubit NV register: electron spin plus one nuclear spin, the unit cell of [yao2012].

The electron (ms = 0 and ms = -1) is the fast "bus" qubit; the nuclear spin (nitrogen or carbon-13) is
the long-lived memory ([dutt2007], [neumann2008], [maurer2012]). A microwave pi pulse that is resonant
only when the nucleus is "up" implements a controlled-NOT ([jelezko2004b]). Choosing the Rabi frequency
Omega = A / sqrt(3) makes the unwanted, detuned branch complete a full 2 pi rotation, so it returns to
its start (a standard selective-pulse trick; high-fidelity versions in [rong2015], [xie2023]).

Rotating-frame Hamiltonian (MHz): H = delta(n) |1><1|_e + (Omega / 2) sigma_x,e, with delta = 0 or A.
"""
from __future__ import annotations
import numpy as np

SIGX = np.array([[0, 1], [1, 0]], dtype=complex)
P1 = np.array([[0, 0], [0, 1]], dtype=complex)
I2 = np.eye(2, dtype=complex)


def _u(h_mhz: np.ndarray, t_us: float) -> np.ndarray:
    w, v = np.linalg.eigh(h_mhz)
    return v @ np.diag(np.exp(-2j * np.pi * w * t_us)) @ v.conj().T


def selective_pi_pulse(a_mhz: float, rabi_mhz: float | None = None) -> tuple[np.ndarray, float]:
    """Unitary on (electron x nucleus) and its duration in microseconds."""
    omega = a_mhz / np.sqrt(3) if rabi_mhz is None else rabi_mhz
    t = 1 / (2 * omega)
    h_up = omega / 2 * SIGX                      # nucleus up: resonant
    h_dn = a_mhz * P1 + omega / 2 * SIGX         # nucleus down: detuned by the hyperfine coupling
    up, dn = np.diag([1, 0]).astype(complex), np.diag([0, 1]).astype(complex)
    return np.kron(_u(h_up, t), up) + np.kron(_u(h_dn, t), dn), t


def bell_fidelity(a_mhz: float = 2.16, rabi_mhz: float | None = None, t2star_us: float = 100.0) -> float:
    """Fidelity of the electron-nuclear Bell pair made by one selective pulse.

    Start: electron in ms = 0, nucleus in an equal superposition. Electron dephasing during the pulse is
    applied as a Gaussian factor exp(-(t/T2*)^2) on electron coherences [degen2017].
    """
    u, t = selective_pi_pulse(a_mhz, rabi_mhz)
    psi0 = np.kron(np.array([1, 0], dtype=complex), np.array([1, 1], dtype=complex) / np.sqrt(2))
    psi = u @ psi0
    rho = np.outer(psi, psi.conj())
    damp = np.exp(-(t / t2star_us) ** 2)
    mask = np.ones((4, 4))
    for i in range(4):
        for j in range(4):
            if (i // 2) != (j // 2):
                mask[i, j] = damp
    rho = rho * mask
    # target: (|1,up> + e^{i phi} |0,down>)/sqrt 2, maximized over the known local phase phi
    a, b = 2, 1
    return float(np.real(rho[a, a] + rho[b, b]) / 2 + abs(rho[a, b]))
