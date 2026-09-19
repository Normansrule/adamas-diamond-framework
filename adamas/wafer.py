"""Wafer economics: die count, yield, and the historical wafer-diameter race.

Gross dies per wafer (standard edge-loss approximation, see [plummer2000]):
    DPW = pi (d/2)^2 / A  -  pi d / sqrt(2 A)
Yield models: Poisson Y = exp(-A D0); Murphy Y = ((1 - exp(-A D0)) / (A D0))^2 ([murphy1964], [stapper1983]).
"""
from __future__ import annotations
import math

# (year, diameter in mm). Silicon and SiC dates are approximate industry history ([plummer2000], [kimoto2014]).
WAFER_HISTORY = {
    "Silicon": [(1960, 25), (1964, 51), (1972, 76), (1976, 100), (1983, 150), (1992, 200), (2002, 300)],
    "Silicon carbide (4H-SiC)": [(1991, 25), (1997, 51), (2001, 76), (2006, 100), (2012, 150), (2022, 200)],
    # Single-crystal diamond: mosaic [yamada2014]; iridium heteroepitaxy [schreck2017]; sapphire
    # heteroepitaxy [kim2020], [kim2021]; reproducible 3-inch wafer-scale single crystal [e6orbray2026].
    "Diamond (single crystal)": [(2004, 8), (2014, 51), (2017, 92), (2021, 51), (2026, 76)],
}
DIAMOND_NOTES = {2004: "HPHT/CVD plates", 2014: "mosaic 2-inch", 2017: "Ir/YSZ/Si 92 mm (one-off)",
                 2021: "sapphire hetero 2-inch", 2026: "3-inch reproducible"}


def dies_per_wafer(diameter_mm: float, die_area_mm2: float) -> int:
    d, a = diameter_mm, die_area_mm2
    return max(0, int(math.pi * (d / 2) ** 2 / a - math.pi * d / math.sqrt(2 * a)))


def poisson_yield(die_area_mm2: float, d0_per_cm2: float) -> float:
    return math.exp(-die_area_mm2 * 1e-2 * d0_per_cm2)


def murphy_yield(die_area_mm2: float, d0_per_cm2: float) -> float:
    x = die_area_mm2 * 1e-2 * d0_per_cm2
    return 1.0 if x == 0 else ((1 - math.exp(-x)) / x) ** 2


def good_dies(diameter_mm: float, die_area_mm2: float, d0_per_cm2: float) -> float:
    return dies_per_wafer(diameter_mm, die_area_mm2) * murphy_yield(die_area_mm2, d0_per_cm2)
