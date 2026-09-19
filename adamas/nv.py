"""Nitrogen-vacancy (NV) center spin physics at room temperature.

Ground-state spin Hamiltonian (frequency units) [doherty2013], [maze2011]:
    H/h = D Sz^2 + E (Sx^2 - Sy^2) + gamma_e B . S   (+ hyperfine terms)
with D = 2870 MHz at 300 K, dD/dT = -74.2 kHz/K [acosta2010], gamma_e = 28.03 GHz/T.
Nitrogen-14 hyperfine splitting along the axis: 2.16 MHz [felton2009].
Optically detected magnetic resonance (ODMR) lines are modeled as Lorentzians [dreau2011].
"""
from __future__ import annotations
import numpy as np
from .constants import GAMMA_E_HZ_PER_T, H, G_E, MU_B

D_300K_MHZ = 2870.0
DDDT_MHZ_PER_K = -0.0742          # [acosta2010]
A_PAR_14N_MHZ = 2.16              # [felton2009]
ZPL_NM = 637.0                    # zero-phonon line [davies1976], [doherty2013]
GAMMA_MHZ_PER_MT = GAMMA_E_HZ_PER_T * 1e-9   # 28.03 MHz/mT

SX = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=complex) / np.sqrt(2)
SY = np.array([[0, -1j, 0], [1j, 0, -1j], [0, 1j, 0]], dtype=complex) / np.sqrt(2)
SZ = np.diag([1, 0, -1]).astype(complex)

# The four NV axes in a (100) crystal [doherty2013]; (111)-grown layers can align all NVs on one axis
# ([michl2014], [lesik2014], [fukui2014]).
NV_AXES = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]]) / np.sqrt(3)


def zero_field_splitting_mhz(t_k: float = 300.0) -> float:
    return D_300K_MHZ + DDDT_MHZ_PER_K * (t_k - 300.0)


def hamiltonian_mhz(b_mt, e_mhz: float = 0.0, t_k: float = 300.0) -> np.ndarray:
    """3x3 Hamiltonian in the NV frame (z along the N-to-V axis); b_mt is a 3-vector in millitesla."""
    bx, by, bz = b_mt
    d = zero_field_splitting_mhz(t_k)
    return d * SZ @ SZ + e_mhz * (SX @ SX - SY @ SY) + GAMMA_MHZ_PER_MT * (bx * SX + by * SY + bz * SZ)


def transition_frequencies_mhz(b_mt, e_mhz: float = 0.0, t_k: float = 300.0) -> tuple[float, float]:
    """The two spin transitions out of the lowest level (mostly ms = 0)."""
    ev = np.linalg.eigvalsh(hamiltonian_mhz(b_mt, e_mhz, t_k))
    return float(ev[1] - ev[0]), float(ev[2] - ev[0])


def odmr_spectrum(freq_mhz, b_lab_mt, axes=NV_AXES, contrast=0.03, linewidth_mhz=1.0, hyperfine=True):
    """Normalized fluorescence versus microwave frequency for an ensemble (or one axis)."""
    f = np.asarray(freq_mhz, dtype=float)
    signal = np.ones_like(f)
    b_lab = np.asarray(b_lab_mt, dtype=float)
    shifts = (-A_PAR_14N_MHZ, 0.0, A_PAR_14N_MHZ) if hyperfine else (0.0,)
    for ax in np.atleast_2d(axes):
        b_par = float(b_lab @ ax)
        b_perp = float(np.sqrt(max(b_lab @ b_lab - b_par ** 2, 0.0)))
        for f0 in transition_frequencies_mhz((b_perp, 0.0, b_par)):
            for s in shifts:
                hw = linewidth_mhz / 2
                signal -= (contrast / (len(np.atleast_2d(axes)) * len(shifts))) * hw ** 2 / ((f - f0 - s) ** 2 + hw ** 2)
    return signal


def rabi(t_us, rabi_mhz: float, detuning_mhz: float = 0.0, t_decay_us: float = np.inf):
    """Probability of leaving ms = 0 under a resonant or detuned drive [jelezko2004a]."""
    t = np.asarray(t_us, dtype=float)
    w = np.hypot(rabi_mhz, detuning_mhz)
    return (rabi_mhz / w) ** 2 * np.sin(np.pi * w * t) ** 2 * np.exp(-t / t_decay_us) \
        + 0.5 * (rabi_mhz / w) ** 2 * (1 - np.exp(-t / t_decay_us))


def ramsey(tau_us, detuning_mhz: float, t2star_us: float, p: float = 2.0):
    """Free-induction decay: 0.5 (1 + cos(2 pi delta tau) exp(-(tau/T2*)^p)) [degen2017]."""
    tau = np.asarray(tau_us, dtype=float)
    return 0.5 * (1 + np.cos(2 * np.pi * detuning_mhz * tau) * np.exp(-(tau / t2star_us) ** p))


def hahn_echo(tau_us, t2_us: float, p: float = 3.0):
    """Echo envelope exp(-(tau/T2)^p); p near 3 for a slowly fluctuating spin bath [delange2010]."""
    return np.exp(-(np.asarray(tau_us, dtype=float) / t2_us) ** p)


def cw_odmr_sensitivity_t_rthz(linewidth_mhz: float, contrast: float, count_rate_hz: float) -> float:
    """Shot-noise-limited continuous-wave sensitivity, eta = (4 / (3 sqrt 3)) (h / (g mu_B)) dv / (C sqrt R) [dreau2011]."""
    return 4 / (3 * np.sqrt(3)) * H / (G_E * MU_B) * linewidth_mhz * 1e6 / (contrast * np.sqrt(count_rate_hz))


# Record room-temperature coherence numbers, seconds. Every entry cites its source.
ROOM_TEMP_COHERENCE = [
    ("Electron T2* (12C-enriched)", 100e-6, "balasubramanian2009"),   # order of magnitude; see [bauch2018]
    ("Electron T2, Hahn echo (12C-enriched)", 1.8e-3, "balasubramanian2009"),
    ("Electron T2, Hahn echo (phosphorus-doped)", 2.4e-3, "herbschleb2019"),
    ("Electron T1", 6e-3, "jarmola2012"),
    ("Carbon-13 nuclear memory", 1.0, "maurer2012"),
]
