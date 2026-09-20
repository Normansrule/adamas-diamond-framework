"""Lithography scaling relations applied to diamond wafers.

Rayleigh scaling [mack2007], [levinson2019]:
    half pitch = k1 * lambda / NA          depth of focus = k2 * lambda / NA^2
Extreme ultraviolet (EUV) platforms: 13.5 nm at numerical aperture (NA) 0.33 and 0.55 [wagner2010],
[vanschoot2017], [asmleuv2026]. With k1 = 0.32 these give about 13 nm and 8 nm, the resolutions the
vendor quotes [asmleuv2026].
Photon shot noise [debisschop2017], [gallatin2005]: photons per unit area = dose / (h c / lambda).
Mirror train throughput: R^n with R about 0.70 per molybdenum/silicon mirror [bajt2002].
Electron range (Kanaya-Okayama) [kanaya1972]:  R[um] = 0.0276 A E^1.67 / (Z^0.89 rho), E in keV, rho in g/cm^3.
Normal-incidence Fresnel reflectance R = ((n - 1)/(n + 1))^2 with diamond index from [zaitsev2001].
"""
from __future__ import annotations
from dataclasses import dataclass
from .constants import H, C_LIGHT, Q


@dataclass(frozen=True)
class Tool:
    name: str
    wavelength_nm: float
    na: float
    k1: float
    wafer_mm: tuple[int, ...]   # wafer diameters the tool class normally accepts
    refs: tuple[str, ...]


TOOLS = {
    "i-line stepper": Tool("i-line stepper (mercury lamp)", 365.0, 0.60, 0.50, (50, 76, 100, 150, 200), ("mack2007",)),
    "KrF": Tool("Krypton fluoride (KrF) deep ultraviolet", 248.0, 0.80, 0.40, (150, 200, 300), ("mack2007",)),
    "ArF dry": Tool("Argon fluoride (ArF) dry", 193.0, 0.93, 0.35, (200, 300), ("levinson2019",)),
    "ArF immersion": Tool("Argon fluoride (ArF) water immersion", 193.0, 1.35, 0.30, (300,), ("levinson2019",)),
    "EUV 0.33": Tool("Extreme ultraviolet, NA 0.33", 13.5, 0.33, 0.32, (300,), ("wagner2010", "asmleuv2026")),
    "EUV 0.55": Tool("Extreme ultraviolet, high NA 0.55", 13.5, 0.55, 0.32, (300,), ("vanschoot2017", "asmleuv2026")),
}


def half_pitch_nm(wavelength_nm: float, na: float, k1: float = 0.32) -> float:
    return k1 * wavelength_nm / na


def depth_of_focus_nm(wavelength_nm: float, na: float, k2: float = 1.0) -> float:
    return k2 * wavelength_nm / na ** 2


def photon_energy_ev(wavelength_nm: float) -> float:
    return H * C_LIGHT / (wavelength_nm * 1e-9) / Q


def photons_per_nm2(dose_mj_cm2: float, wavelength_nm: float) -> float:
    """Incident photons per square nanometer for a given exposure dose."""
    return dose_mj_cm2 * 1e-3 / (photon_energy_ev(wavelength_nm) * Q) * 1e-14


def dose_noise_fraction(dose_mj_cm2: float, wavelength_nm: float, pixel_nm: float, absorbed: float = 0.2) -> float:
    """One-sigma relative fluctuation of absorbed photons in a pixel_nm x pixel_nm area (Poisson)."""
    n = photons_per_nm2(dose_mj_cm2, wavelength_nm) * pixel_nm ** 2 * absorbed
    return n ** -0.5


def mirror_throughput(reflectance: float = 0.70, mirrors: int = 10) -> float:
    return reflectance ** mirrors


def kanaya_okayama_range_um(energy_kev: float, a_g_mol: float, z: float, rho_g_cm3: float) -> float:
    return 0.0276 * a_g_mol * energy_kev ** 1.67 / (z ** 0.89 * rho_g_cm3)


SUBSTRATES = {"Silicon": (28.09, 14, 2.33), "Diamond": (12.011, 6, 3.515)}


def fresnel_reflectance(n: float) -> float:
    return ((n - 1) / (n + 1)) ** 2
