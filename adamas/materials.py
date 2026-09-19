"""Room-temperature semiconductor property database and classic figures of merit.

Property values are the commonly quoted 300 K numbers from [sze2006], [wort2008], [tsao2018],
[donato2020], [kimoto2014], [mishra2008], and [pearton2018]. Diamond mobilities are the record
time-of-flight values of [isberg2002]; real doped layers are lower ([pernot2010], [pernot2008]).
Treat every entry as "best reported bulk value", not as a guaranteed device parameter.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from .constants import EPS0


@dataclass(frozen=True)
class Material:
    name: str
    eg_ev: float          # bandgap, eV
    ec_mv_cm: float       # critical (breakdown) field, MV/cm
    mu_n: float           # electron mobility, cm^2/(V s)
    mu_p: float           # hole mobility, cm^2/(V s)
    eps_r: float          # relative permittivity
    vsat_cm_s: float      # saturated drift velocity, cm/s
    kappa_w_cmk: float    # thermal conductivity, W/(cm K)
    lattice: str
    a_angstrom: float     # lattice constant a, angstrom
    max_wafer_mm: float   # largest single-crystal wafer in production or reproducible pilot, mm
    refs: tuple[str, ...]


MATERIALS: dict[str, Material] = {
    "Si": Material("Silicon (Si)", 1.12, 0.3, 1400, 450, 11.7, 1.0e7, 1.5, "diamond cubic", 5.431, 300,
                   ("sze2006",)),
    "4H-SiC": Material("Silicon carbide (4H-SiC)", 3.26, 2.5, 1000, 120, 9.7, 2.0e7, 4.9, "hexagonal", 3.073, 200,
                       ("kimoto2014", "tsao2018")),
    "GaN": Material("Gallium nitride (GaN)", 3.4, 3.3, 1200, 30, 9.0, 2.5e7, 2.3, "wurtzite", 3.189, 150,
                    ("mishra2008", "tsao2018")),
    "Ga2O3": Material("Gallium oxide (beta-Ga2O3)", 4.85, 8.0, 250, 0.0, 10.0, 1.5e7, 0.2, "monoclinic", 12.23, 150,
                      ("pearton2018", "higashiwaki2012")),
    "Diamond": Material("Diamond (C)", 5.47, 10.0, 4500, 3800, 5.7, 1.5e7, 22.0, "diamond cubic", 3.567, 76,
                        ("isberg2002", "wort2008", "donato2020", "e6orbray2026")),
}


def _mu(m: Material, carrier: str) -> float:
    return m.mu_n if carrier == "n" else m.mu_p


def baliga_fom(m: Material, carrier: str = "n") -> float:
    """Baliga figure of merit, BFOM = eps * mu * Ec^3 [baliga1982]. Low-frequency unipolar conduction loss."""
    return m.eps_r * _mu(m, carrier) * m.ec_mv_cm ** 3


def baliga_hf_fom(m: Material, carrier: str = "n") -> float:
    """Baliga high-frequency figure of merit, BHFFOM = mu * Ec^2 [baliga1989]. Switching loss."""
    return _mu(m, carrier) * m.ec_mv_cm ** 2


def johnson_fom(m: Material) -> float:
    """Johnson figure of merit, JFOM = (Ec * vsat / (2 pi))^2 [johnson1965]. Power-frequency product."""
    return (m.ec_mv_cm * m.vsat_cm_s / (2 * math.pi)) ** 2


def keyes_fom(m: Material) -> float:
    """Keyes figure of merit, KFOM = kappa * sqrt(c * vsat / (4 pi eps)) [keyes1972]. Thermal limit on switching."""
    c_cm_s = 2.998e10
    return m.kappa_w_cmk * math.sqrt(c_cm_s * m.vsat_cm_s / (4 * math.pi * m.eps_r))


def normalized_foms(carrier_for_diamond: str = "p") -> dict[str, dict[str, float]]:
    """All four figures of merit divided by the silicon value.

    Diamond defaults to holes because boron (p-type) is the only dopant that is practical today
    ([kalish1999], [donato2020]); every other material uses electrons.
    """
    si = MATERIALS["Si"]
    out: dict[str, dict[str, float]] = {}
    for key, m in MATERIALS.items():
        c = carrier_for_diamond if key == "Diamond" else "n"
        out[key] = {
            "BFOM": baliga_fom(m, c) / baliga_fom(si),
            "BHFFOM": baliga_hf_fom(m, c) / baliga_hf_fom(si),
            "JFOM": johnson_fom(m) / johnson_fom(si),
            "KFOM": keyes_fom(m) / keyes_fom(si),
        }
    return out


def permittivity_f_cm(m: Material) -> float:
    return m.eps_r * EPS0 * 1e-2
