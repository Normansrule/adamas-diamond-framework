"""Magnetic dipole coupling between two NV electron spins, and how placement error limits scaling.

Coupling strength [neumann2010natphys], [dolde2013]:
    nu_dd(r, theta) = (mu0 gamma_e^2 hbar / (4 pi r^3)) |1 - 3 cos^2(theta)| / (2 pi)  ->  52 MHz nm^3 / r^3
Dolde and co-workers entangled two NVs about 25 nm apart at room temperature with fidelity 0.67 [dolde2013].
The scalable room-temperature architecture of [yao2012] builds on this coupling plus nuclear-spin memories.

Order-of-magnitude gate model used here: a controlled-phase gate needs t = 1 / (2 nu_dd); the electron
coherence decays as exp(-t / T2) during the gate, so F ~ 0.5 (1 + exp(-t / T2)). This ignores control
errors and is an upper bound.
"""
from __future__ import annotations
import numpy as np
from .constants import MU0, HBAR, GAMMA_E_HZ_PER_T

_GAMMA_RAD = 2 * np.pi * GAMMA_E_HZ_PER_T
DIPOLAR_MHZ_NM3 = MU0 * _GAMMA_RAD ** 2 * HBAR / (4 * np.pi) / (2 * np.pi) * 1e27 / 1e6  # about 52


def dipolar_coupling_khz(r_nm, theta_rad: float = np.pi / 2):
    r = np.asarray(r_nm, dtype=float)
    return DIPOLAR_MHZ_NM3 * 1e3 / r ** 3 * abs(1 - 3 * np.cos(theta_rad) ** 2)


def gate_time_us(r_nm, theta_rad: float = np.pi / 2):
    return 1e3 / (2 * dipolar_coupling_khz(r_nm, theta_rad))


def gate_fidelity_bound(r_nm, t2_ms: float = 1.8, theta_rad: float = np.pi / 2):
    return 0.5 * (1 + np.exp(-gate_time_us(r_nm, theta_rad) / (t2_ms * 1e3)))


def implant_rule_of_thumb(energy_kev: float) -> tuple[float, float]:
    """Very rough depth and straggle (nm) for nitrogen ions in diamond below about 30 keV.

    Roughly 1.5 nm of depth per keV with straggle near 40 percent of the depth, consistent with the
    shallow-implant literature ([pezzagna2010], [oforiokai2012]). Replace with a real SRIM run
    [ziegler2010] for design work; channeling makes real profiles deeper.
    """
    depth = 1.5 * energy_kev
    return depth, 0.4 * depth


def pair_yield(target_nm: float, sigma_nm: float, conv_yield: float, ions_per_site: int = 1,
               r_max_nm: float = 30.0, trials: int = 20000, seed: int = 1) -> float:
    """Monte Carlo probability that a designed two-site cell ends up as exactly one NV per site,
    closer than r_max_nm (the room-temperature coupling horizon of [dolde2013]).

    sigma_nm lumps mask aperture and ion straggle per axis; conv_yield is the nitrogen-to-NV conversion
    probability (about 1 percent for keV implants [pezzagna2010], tens of percent with donor co-doping
    [luhmann2019] or laser writing [chen2019]).
    """
    rng = np.random.default_rng(seed)
    n1 = rng.binomial(ions_per_site, conv_yield, trials)
    n2 = rng.binomial(ions_per_site, conv_yield, trials)
    p1 = rng.normal(0, sigma_nm, (trials, 3))
    p2 = rng.normal(0, sigma_nm, (trials, 3)) + np.array([target_nm, 0, 0])
    r = np.linalg.norm(p1 - p2, axis=1)
    return float(np.mean((n1 == 1) & (n2 == 1) & (r <= r_max_nm)))
