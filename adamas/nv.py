"""Nitrogen-vacancy (NV) center spin physics at room temperature.

Ground-state spin Hamiltonian (frequency units) [doherty2013], [maze2011]:
    H/h = D Sz^2 + E (Sx^2 - Sy^2) + gamma_e B . S   (+ hyperfine terms)
with D = 2870 MHz at 300 K, dD/dT = -74.2 kHz/K [acosta2010], gamma_e = 28.03 GHz/T.
Nitrogen-14 hyperfine splitting along the axis: |A_par| = 2.147 MHz (A_par = -2.147 MHz, quadrupole P = -5.016 MHz) [felton2009].
Optically detected magnetic resonance (ODMR) lines are modeled as Lorentzians [dreau2011].
"""
from __future__ import annotations
import numpy as np
from .constants import GAMMA_E_HZ_PER_T, H, G_E, MU_B

D_300K_MHZ = 2870.0
DDDT_MHZ_PER_K = -0.0742          # [acosta2010]
A_PAR_14N_MHZ = 2.147             # |A_par| of 14N [felton2009]
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


def lines_perturbative_mhz(b_mt: float, theta_deg: float, t_k: float = 300.0) -> tuple[float, float]:
    """ODMR lines to second order in the field (B << D / gamma), theta the angle between the field and the NV axis:
        f = D + 3 (gamma B_perp)^2 / (2 D) -/+ sqrt((gamma B_par)^2 + ((gamma B_perp)^2 / (2 D))^2)
    The square root treats the m_s = +1 and -1 pair as nearly degenerate: B_perp couples them through m_s = 0, which
    splits the lines by (gamma B_perp)^2 / D even for a field perpendicular to the axis. Away from 90 degrees it
    reduces to D -/+ gamma B_par + 3 (gamma B_perp)^2 / (2 D). Compare with transition_frequencies_mhz (exact)."""
    d = zero_field_splitting_mhz(t_k); g = GAMMA_MHZ_PER_MT
    bpar, bperp = b_mt * abs(np.cos(np.radians(theta_deg))), b_mt * abs(np.sin(np.radians(theta_deg)))
    shift, half = 3 * (g * bperp) ** 2 / (2 * d), float(np.hypot(g * bpar, (g * bperp) ** 2 / (2 * d)))
    return float(d + shift - half), float(d + shift + half)


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


def echo_mistimed(offset_us, detuning_mhz: float, t2star_us: float):
    """P(ms = -1) after pi/2_x, tau1, pi_x, tau2, pi/2_x for an ensemble with static Gaussian detunings (mean delta,
    exp(-(t/T2*)^2) decay): 0.5 (1 - cos(2 pi delta e) exp(-(e/T2*)^2)) with e = tau2 - tau1 [hahn1950]. A centred pi
    pulse (e = 0) refocuses every static detuning, whatever the total time; only the mistiming e dephases."""
    e = np.asarray(offset_us, dtype=float)
    return 0.5 * (1 - np.cos(2 * np.pi * detuning_mhz * e) * np.exp(-(e / t2star_us) ** 2))


def cw_odmr_sensitivity_t_rthz(linewidth_mhz: float, contrast: float, count_rate_hz: float) -> float:
    """Shot-noise-limited continuous-wave sensitivity, eta = (4 / (3 sqrt 3)) (h / (g mu_B)) dv / (C sqrt R) [dreau2011]."""
    return 4 / (3 * np.sqrt(3)) * H / (G_E * MU_B) * linewidth_mhz * 1e6 / (contrast * np.sqrt(count_rate_hz))


# Record room-temperature coherence numbers, seconds. Every entry cites its source.
ROOM_TEMP_COHERENCE = [
    ("Electron T2* (12C-enriched)", 100e-6, "balasubramanian2009"),   # order of magnitude; see [bauch2018]
    ("Electron T2*, record (phosphorus-doped, 12C)", 1.5e-3, "herbschleb2019"),
    ("Electron T2, Hahn echo (12C-enriched)", 1.8e-3, "balasubramanian2009"),
    ("Electron T2, Hahn echo (phosphorus-doped)", 2.4e-3, "herbschleb2019"),
    ("Electron T1", 6e-3, "jarmola2012"),
    ("Carbon-13 nuclear memory", 1.0, "maurer2012"),
]


# ---------------- strain from dislocations and the NV dephasing time (audit G5; order-of-magnitude model, proposed here) ----
# A straight dislocation strains the lattice as eps ~ b / (2 pi r); at density D the typical distance to the nearest one is
# r = 1 / (2 sqrt(D)). The NV spin-strain coupling of about 10.9 GHz per unit strain [marshall2022] turns the strain
# spread into a line spread df, and T2* ~ 1 / (pi df) for an ensemble. Measured anchors: heteroepitaxial single NV
# T2 = 5 us [nelz2019]; laterally overgrown heteroepitaxial T2* 1.1 to 4.8 us [oshnik2025]; low-strain HPHT
# T2* = 1.28 us, limited by strain and local charges [blinder2024]. An echo removes static strain, so T2 is set by
# noise along the dislocations and is not modeled here.
BURGERS_NM = 0.252                # diamond, a / sqrt(2)
SPIN_STRAIN_HZ = 10.9e9           # per unit strain [marshall2022]


def dislocation_strain(dislocations_cm2: float) -> float:
    r_m = 1.0 / (2.0 * np.sqrt(dislocations_cm2)) * 1e-2
    return BURGERS_NM * 1e-9 / (2 * np.pi * r_m)


def t2star_from_dislocations_us(dislocations_cm2: float) -> float:
    """Ensemble dephasing time limited by dislocation strain alone (upper bound; other noise lowers it)."""
    return float(1e6 / (np.pi * SPIN_STRAIN_HZ * dislocation_strain(dislocations_cm2)))
