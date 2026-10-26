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
    # Single-crystal diamond, peer-reviewed only: plates; mosaic (tiled, not one crystal) [yamada2014]; one 92 mm
    # iridium-heteroepitaxy plate [schreck2017]; 2-inch heteroepitaxial wafers on sapphire [kim2021] and Ir/YSZ/Si [qu2024].
    "Diamond (single crystal)": [(2004, 8), (2014, 51), (2017, 92), (2021, 51), (2024, 51)],
}
DIAMOND_NOTES = {2004: "HPHT/CVD plates", 2014: "mosaic 2-inch (tiled)", 2017: "Ir/YSZ/Si 92 mm (one plate)",
                 2021: "sapphire hetero 2-inch", 2024: "Ir/YSZ/Si 2-inch"}
# Industry announcements without published quality data: labeled "reported", plotted hollow (audit G1, G2).
DIAMOND_ANNOUNCED = [(2026, 76, "3-inch process announced, industry claim [e6orbray2026]")]

# Dislocation density by substrate class, cm^-2 (typical, low, high); audit G3:
# heteroepitaxial at the growth surface of wafer-scale material [kim2021] [qu2024] [nelz2019], thinner layers higher
# (above 1e10 right after nucleation, about 2e7 to 1e8 at 1 to 2 mm thickness [stehl2013]); CVD on HPHT seeds [friel2009] [gaukroger2008]; HPHT plates [sumiya2012].
DISLOCATIONS_CM2 = {"HPHT plate": (1e2, 1e1, 1e3), "CVD on HPHT (homoepitaxial)": (1e4, 1e3, 1e5),
                    "Heteroepitaxial (Ir/YSZ/Si, sapphire)": (2e7, 1e7, 1e8)}


def dies_per_wafer(diameter_mm: float, die_area_mm2: float) -> int:
    d, a = diameter_mm, die_area_mm2
    return max(0, int(math.pi * (d / 2) ** 2 / a - math.pi * d / math.sqrt(2 * a)))


def poisson_yield(die_area_mm2: float, d0_per_cm2: float) -> float:
    return math.exp(-die_area_mm2 * 1e-2 * d0_per_cm2)


def murphy_yield(die_area_mm2: float, d0_per_cm2: float) -> float:
    x = die_area_mm2 * 1e-2 * d0_per_cm2
    return 1.0 if x == 0 else (-math.expm1(-x) / x) ** 2   # expm1 keeps precision when A*D0 is tiny


def good_dies(diameter_mm: float, die_area_mm2: float, d0_per_cm2: float) -> float:
    return dies_per_wafer(diameter_mm, die_area_mm2) * murphy_yield(die_area_mm2, d0_per_cm2)
