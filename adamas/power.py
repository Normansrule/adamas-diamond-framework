"""Unipolar power-device limits and radio-frequency estimates.

Ideal specific on-resistance of a drift region [baliga1982]:
    R_on,sp = 4 BV^2 / (eps mu Ec^3)
which assumes fully ionized dopants. Diamond violates that assumption at 300 K (see adamas.doping),
so the "ideal diamond" line is an upper bound on what boron-doped drift layers deliver [donato2020].
Transit-time cutoff frequency: f_T = vsat / (2 pi Lg) [sze2006].
"""
from __future__ import annotations
import math
from .materials import Material, permittivity_f_cm

# Measured lateral diamond MOSFET on a 2-inch-class heteroepitaxial wafer [saha2021]:
MEASURED_DIAMOND = {"saha2021": {"bv_v": 2608.0, "ron_mohm_cm2": 19.74}}


def ron_sp_mohm_cm2(m: Material, bv_v: float, carrier: str = "n") -> float:
    mu = m.mu_n if carrier == "n" else m.mu_p
    ec = m.ec_mv_cm * 1e6
    return 4 * bv_v ** 2 / (permittivity_f_cm(m) * mu * ec ** 3) * 1e3


def ft_transit_ghz(vsat_cm_s: float, gate_length_nm: float) -> float:
    return vsat_cm_s / (2 * math.pi * gate_length_nm * 1e-7) / 1e9
