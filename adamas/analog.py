"""Analog design quantities for diamond p-channel transistors, in the square-law approximation.

    gm = sqrt(2 k I_D) = 2 I_D / V_ov          gm / I_D = 2 / V_ov                  [silveira1996], [razavi2017]
    r_o = 1 / (lambda I_D)                      intrinsic gain = gm r_o = 2 / (lambda V_ov)   [gray2009]
    sigma(delta V_T) = A_VT / sqrt(W L)                                              [pelgrom1989]
    input-referred thermal noise  v_n^2 = 4 k T gamma / gm                           [razavi2017], [johnson1928], [nyquist1928]
    threshold-difference reference  V_ref = V_T,enh - V_T,dep                        [blauschild1978]
Photocurrent readout of NV spins [bourgeois2015], [siyushev2019] needs a transimpedance amplifier:
    i_n^2 = 4 k T / R_f + 2 q I_dc   (per hertz)

A_VT, lambda, and the noise factor gamma have not been published for diamond hole-gas transistors;
defaults are placeholders, and measuring them is experiment A-1 of the expert track.
"""
from __future__ import annotations
import math
from .constants import KB, Q
from .logic import Fet


def gm_s(f: Fet, i_d_a: float) -> float:
    return math.sqrt(2 * f.k * i_d_a)


def overdrive_v(f: Fet, i_d_a: float) -> float:
    return math.sqrt(2 * i_d_a / f.k)


def gm_over_id(f: Fet, i_d_a: float) -> float:
    return gm_s(f, i_d_a) / i_d_a


def intrinsic_gain(f: Fet, i_d_a: float, lam_per_v: float = 0.02) -> float:
    return gm_s(f, i_d_a) / (lam_per_v * i_d_a)


def cs_amp_gain_depletion_load(drv: Fet, i_d_a: float, lam_drv: float = 0.02, lam_load: float = 0.02) -> float:
    """Common-source stage whose load is a depletion transistor with gate tied to source (a current source)."""
    return -gm_s(drv, i_d_a) / ((lam_drv + lam_load) * i_d_a)


def sigma_vt_mv(a_vt_mv_um: float, w_um: float, l_um: float) -> float:
    return a_vt_mv_um / math.sqrt(w_um * l_um)


def thermal_noise_nv_rthz(f: Fet, i_d_a: float, t_k: float = 300.0, gamma: float = 2 / 3) -> float:
    return math.sqrt(4 * KB * t_k * gamma / gm_s(f, i_d_a)) * 1e9


def ed_reference_v(vt_enh: float = 1.5, vt_dep: float = -2.0) -> float:
    return vt_enh - vt_dep


def tia_noise_fa_rthz(r_f_ohm: float, i_dc_a: float = 0.0, t_k: float = 300.0) -> float:
    return math.sqrt(4 * KB * t_k / r_f_ohm + 2 * Q * i_dc_a) * 1e15


def pdmr_averaging_time_s(i_dc_a: float, contrast: float, r_f_ohm: float = 1e9, snr: float = 1.0) -> float:
    """Time to resolve a spin-dependent photocurrent change contrast * i_dc with the given signal-to-noise ratio."""
    i_n = tia_noise_fa_rthz(r_f_ohm, i_dc_a) * 1e-15          # A / sqrt(Hz)
    return (snr * i_n / (contrast * i_dc_a)) ** 2 / 2          # bandwidth = 1 / (2 t)
