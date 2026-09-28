"""NV optical cycle: why mₛ = 0 is bright. Seven-level rate model with the rates measured by [tetienne2012]
(see also [manson2006] [robledo2011njp]); the ms = +1 and -1 levels are lumped (zero field).

Levels: 0 = ground mₛ=0, 1 = ground mₛ=±1, 2 = excited mₛ=0, 3 = excited mₛ=±1, 4 = metastable singlet.
Rates in 1/µs: optical pumping beta·k_r (spin conserving), radiative decay k_r, intersystem crossing from the excited
state into the singlet (much faster from mₛ=±1), and singlet decay back to the ground state (preferring mₛ=0).
The spin-dependent crossing is what polarizes the spin and makes mₛ=±1 dimmer.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import expm

K_R, K_E0_S, K_E1_S, K_S_G0, K_S_G1 = 65.9, 11.0, 91.8, 4.87, 2.04     # 1/us, [tetienne2012]


def generator(beta: float) -> np.ndarray:
    """Rate matrix M with dp/dt = M p (columns sum to zero). beta = pump rate / k_r (saturation near 1)."""
    k = np.zeros((5, 5))
    k[2, 0] = k[3, 1] = beta * K_R          # k[i, j] = rate from level j to level i; optical pumping
    k[0, 2] = k[1, 3] = K_R                 # radiative decay (red photon)
    k[4, 2], k[4, 3] = K_E0_S, K_E1_S
    k[0, 4], k[1, 4] = K_S_G0, K_S_G1
    M = k - np.diag(k.sum(axis=0))
    return M


def fluorescence(beta: float, start: str, t_us) -> np.ndarray:
    """Photon emission rate (1/us) versus time after the laser turns on, starting in mₛ = 0 or ±1."""
    M = generator(beta); p0 = np.zeros(5); p0[0 if start == "0" else 1] = 1.0
    return np.array([K_R * (expm(M * t) @ p0)[2:4].sum() for t in np.atleast_1d(t_us)])


def readout_contrast(beta: float = 1.0, window_us: float = 0.3) -> float:
    t = np.linspace(0, window_us, 301)
    a, b = fluorescence(beta, "0", t), fluorescence(beta, "1", t)
    return float(1 - np.trapezoid(b, t) / np.trapezoid(a, t))


def polarization(beta: float = 1.0, t_us: float = 3.0) -> float:
    """Population of ground mₛ=0 (plus singlet share that returns there) after pumping from a mixed state."""
    p = expm(generator(beta) * t_us) @ np.array([1 / 3, 2 / 3, 0, 0, 0])
    return float(p[0] + p[2] + p[4] * K_S_G0 / (K_S_G0 + K_S_G1))
