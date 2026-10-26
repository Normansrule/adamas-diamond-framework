"""Telling two NV centers apart when they sit inside one laser spot (audit Q4, chapter 7.2b).

A coupled pair sits 10 to 30 nm apart [dolde2013] [joas2025], but a diffraction-limited focus is a few hundred nm wide,
so both centers see the same light and the same microwave. This module computes the three numbers that decide whether
they can still be addressed one at a time:

1. The laser spot. The focal intensity of an aberration-free lens is the Airy pattern I(v) = [2 J1(v) / v]^2 with
   v = 2 pi NA r / lambda [born1999]; its full width at half maximum is found numerically (about 0.51 lambda / NA).
2. The spectral separation of the two centers' microwave lines. Spectral route: NVs on different <111> axes see
   different field projections, so their lines split apart (exact spin-1 eigenvalues, adamas.nv) [dolde2013]. Gradient
   route: a field gradient G shifts the line of a center at distance dx by gamma_e G dx [grinolds2011] [zhang2017addr].
3. Crosstalk. A resonant drive of Rabi frequency Omega on one line excites a line detuned by Delta with peak probability
   Omega^2 / (Omega^2 + Delta^2) [rabi1937]; the lines are resolved only when Delta is larger than the line width, about
   1 / (pi T2*) for exponential decay. Selective driving therefore trades speed (large Omega) against crosstalk.

Model limits: point-like NVs, uniform microwave field, crosstalk as the worst case over pulse length (a shaped pulse
does better), no hyperfine structure (the 14N triplet, about 2.15 MHz apart [felton2009], blurs separations of a few MHz).
"""
from __future__ import annotations
import math

import numpy as np
from scipy.special import j1

from . import nv

GAMMA = nv.GAMMA_MHZ_PER_MT          # MHz per mT
G_PER_NM_TO_MT_PER_NM = 0.1          # 1 G = 0.1 mT


def airy_intensity(r_nm, wavelength_nm: float = 532.0, na: float = 0.95):
    """Normalized focal intensity of the Airy pattern at radius r [born1999]."""
    v = 2 * np.pi * na * np.asarray(r_nm, dtype=float) / wavelength_nm
    v = np.where(v == 0, 1e-12, v)
    return (2 * j1(v) / v) ** 2


def spot_fwhm_nm(wavelength_nm: float = 532.0, na: float = 0.95) -> float:
    """Full width at half maximum of the Airy focus, by bisection on I(r) = 1/2."""
    lo, hi = 0.0, wavelength_nm / na
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if airy_intensity(mid, wavelength_nm, na) > 0.5 else (lo, mid)
    return 2 * (lo + hi) / 2


def lines_on_axis(b_mt: float, b_theta_deg: float, b_phi_deg: float, axis) -> tuple[float, float]:
    """ODMR lines (MHz) of an NV whose symmetry axis is `axis` (unit vector) in a field of magnitude b_mt pointing along
    (theta, phi) in the crystal frame; exact spin-1 eigenvalues of D Sz^2 + gamma B.S in the NV frame (adamas.nv)."""
    th, ph = math.radians(b_theta_deg), math.radians(b_phi_deg)
    bvec = b_mt * np.array([math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)])
    a = np.asarray(axis, dtype=float); a = a / np.linalg.norm(a)
    b_par = float(bvec @ a); b_perp = float(np.linalg.norm(bvec - b_par * a))
    return nv.transition_frequencies_mhz((b_perp, 0.0, b_par))


def best_line(b_mt: float, b_theta_deg: float, b_phi_deg: float, axis_a=nv.NV_AXES[0], axis_b=nv.NV_AXES[1]) -> tuple[int, float, float]:
    """The line of NV A a selective drive should use: (index 0 or 1, its frequency in MHz, its distance Delta to the
    nearest line of NV B in MHz). The drive picks A's line that is farthest from every B line."""
    la, lb = lines_on_axis(b_mt, b_theta_deg, b_phi_deg, axis_a), lines_on_axis(b_mt, b_theta_deg, b_phi_deg, axis_b)
    d = [min(abs(x - y) for y in lb) for x in la]
    k = 1 if d[1] > d[0] + 1e-6 else 0          # ties (within 1 Hz) go to the lower line
    return k, float(la[k]), float(d[k])


def spectral_separation_mhz(b_mt: float, b_theta_deg: float, b_phi_deg: float, axis_a=nv.NV_AXES[0], axis_b=nv.NV_AXES[1]) -> float:
    """Detuning Delta (MHz) of NV B from the best line of NV A (see best_line): the selectivity budget of the spectral route."""
    return best_line(b_mt, b_theta_deg, b_phi_deg, axis_a, axis_b)[2]


def gradient_shift_mhz(gradient_g_per_nm: float, dx_nm: float) -> float:
    """Line shift between two NVs dx apart along a field gradient G: gamma_e G dx [grinolds2011]."""
    return GAMMA * gradient_g_per_nm * G_PER_NM_TO_MT_PER_NM * dx_nm


def crosstalk(rabi_mhz: float, detuning_mhz: float) -> float:
    """Peak excitation of a line detuned by Delta under a drive of Rabi frequency Omega [rabi1937]."""
    return rabi_mhz ** 2 / (rabi_mhz ** 2 + detuning_mhz ** 2)


def linewidth_mhz(t2star_us: float) -> float:
    """Line width (full width at half maximum) for the Gaussian free-induction decay exp(-(t/T2*)^2) used by nv.ramsey:
    the spectrum is exp(-(pi f T2*)^2), so FWHM = 2 sqrt(ln 2) / (pi T2*) = 0.530 / T2* (an exponential decay would
    give 1 / (pi T2*), 1.67 times narrower)."""
    return 2.0 * math.sqrt(math.log(2.0)) / (math.pi * t2star_us)


def max_rabi_for_crosstalk(detuning_mhz: float, eps: float = 0.01) -> float:
    """Largest Rabi frequency that keeps the crosstalk at or below eps: Omega = Delta sqrt(eps / (1 - eps))."""
    return detuning_mhz * math.sqrt(eps / (1 - eps))


def verdict(separation_mhz: float, t2star_us: float, rabi_mhz: float, eps: float = 0.01) -> dict:
    """Is a selective pi pulse possible? Needs separation above the line width and crosstalk at or below eps."""
    lw, xt = linewidth_mhz(t2star_us), crosstalk(rabi_mhz, separation_mhz)
    return {"linewidth_mhz": lw, "crosstalk": xt, "resolved": separation_mhz > lw, "selective": separation_mhz > lw and xt <= eps,
            "pi_time_ns": 500.0 / rabi_mhz, "max_rabi_mhz": max_rabi_for_crosstalk(separation_mhz, eps)}
