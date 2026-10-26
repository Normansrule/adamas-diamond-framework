"""First-order thermal models for comparing substrates.

Spreading resistance of a circular, isothermal heat source of radius a on a half-space
[carslaw1959]:  R = 1 / (4 kappa a).  One-dimensional slab: R = t / (kappa A).
Diamond's 22 W/(cm K) ([wei1993], [olson1993], [inyushkin2018]) is the reason GaN-on-diamond
radio-frequency transistors run cooler ([pomeroy2014], [sun2015], [malakoutian2021]).
"""
from __future__ import annotations


def spreading_resistance_k_w(kappa_w_cmk: float, radius_um: float) -> float:
    return 1.0 / (4.0 * kappa_w_cmk * radius_um * 1e-4)


def hotspot_rise_k(power_w: float, kappa_w_cmk: float, radius_um: float) -> float:
    return power_w * spreading_resistance_k_w(kappa_w_cmk, radius_um)


def slab_resistance_k_w(thickness_um: float, kappa_w_cmk: float, area_mm2: float) -> float:
    return (thickness_um * 1e-4) / (kappa_w_cmk * area_mm2 * 1e-2)


def slowest_mode_time_s(kappa_w_cmk: float, rho_c_j_cm3k: float, thickness_cm: float) -> float:
    """Time constant of the slowest thermal mode of a slab of thickness L with an insulated top and an isothermal bottom:
    tau = 4 L^2 / (pi^2 alpha), alpha = kappa / (rho c) [carslaw1959]. After 3 tau the temperature is within 5 % of
    steady state. This is the geometry of the Heat Race lab's cross-section (its sides are insulated too)."""
    import math
    return 4.0 * thickness_cm ** 2 * rho_c_j_cm3k / (math.pi ** 2 * kappa_w_cmk)

