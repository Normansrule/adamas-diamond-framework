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
# Measured lateral NO2-doped diamond MOSFETs from one group, on heteroepitaxial wafers. Baliga figure of merit = BV^2 / R_on,sp.
#   saha2021: 2608 V, 345 MW/cm^2                                      [saha2021]
#   saha2022: 2568 V, 7.54 mOhm cm^2, 874.6 MW/cm^2 (polished surface) [saha2022]; numbers as reported in [kasu2022talk]
#   saha2023: 3659 V, 173 MW/cm^2; R_on,sp derived here as BV^2 / BFOM [saha2023]
MEASURED_DIAMOND = {
    "saha2021": {"bv_v": 2608.0, "ron_mohm_cm2": 19.74},
    "saha2022": {"bv_v": 2568.0, "ron_mohm_cm2": 7.54},
    "saha2023": {"bv_v": 3659.0, "ron_mohm_cm2": 3659.0 ** 2 / 173e6 * 1e3},
}


def bfom_mw_cm2(bv_v: float, ron_mohm_cm2: float) -> float:
    return bv_v ** 2 / (ron_mohm_cm2 * 1e-3) / 1e6


def ron_sp_mohm_cm2(m: Material, bv_v: float, carrier: str = "n") -> float:
    mu = m.mu_n if carrier == "n" else m.mu_p
    ec = m.ec_mv_cm * 1e6
    return 4 * bv_v ** 2 / (permittivity_f_cm(m) * mu * ec ** 3) * 1e3


def ft_transit_ghz(vsat_cm_s: float, gate_length_nm: float) -> float:
    return vsat_cm_s / (2 * math.pi * gate_length_nm * 1e-7) / 1e9
