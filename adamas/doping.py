"""Incomplete dopant ionization: the central obstacle for room-temperature diamond electronics.

Charge neutrality for a single acceptor level with compensation Nd [sze2006], as applied to
diamond in [donato2020] and [lagrange1998]:

    p (p + Nd) / (Na - Nd - p) = (Nv / g) exp(-Ea / kT),   Nv = 2 (2 pi m* k T / h^2)^(3/2)

The same expression holds for donors with n, Nc, and the donor degeneracy.
Activation energies: boron 0.37 eV ([collins1971], [chrenko1973]), phosphorus 0.57 eV
([koizumi1997], [katagiri2004]), substitutional nitrogen 1.7 eV [farrer1969]; silicon dopants
about 0.045 eV [sze2006]. Density-of-states masses are adjustable parameters; the diamond electron
value follows the valley masses of [nava1980].
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from .constants import H, KB, KB_EV, M0


@dataclass(frozen=True)
class Dopant:
    label: str
    host: str
    kind: str        # "acceptor" or "donor"
    ea_ev: float     # activation energy, eV
    g: float         # level degeneracy
    m_dos: float     # density-of-states effective mass in units of m0
    refs: tuple[str, ...]


DOPANTS = {
    "Si:B": Dopant("Boron in silicon", "Si", "acceptor", 0.045, 4, 0.81, ("sze2006",)),
    "Si:P": Dopant("Phosphorus in silicon", "Si", "donor", 0.045, 2, 1.08, ("sze2006",)),
    "C:B": Dopant("Boron in diamond", "Diamond", "acceptor", 0.37, 4, 0.9, ("collins1971", "lagrange1998")),
    "C:P": Dopant("Phosphorus in diamond", "Diamond", "donor", 0.57, 2, 1.8, ("koizumi1997", "nava1980")),
    "C:N": Dopant("Nitrogen in diamond", "Diamond", "donor", 1.7, 2, 1.8, ("farrer1969",)),
}


def band_dos_cm3(m_dos: float, t_k: float) -> float:
    """Effective density of states, cm^-3 [sze2006]."""
    return 2 * (2 * math.pi * m_dos * M0 * KB * t_k / H ** 2) ** 1.5 * 1e-6


def free_carriers_cm3(d: Dopant, n_dopant: float, t_k: float = 300.0, n_comp: float = 0.0) -> float:
    """Free carrier density from the neutrality equation above (closed-form quadratic root)."""
    k = band_dos_cm3(d.m_dos, t_k) / d.g * math.exp(-d.ea_ev / (KB_EV * t_k))
    b = n_comp + k
    c = -k * (n_dopant - n_comp)
    return (-b + math.sqrt(b * b - 4 * c)) / 2


def ionized_fraction(d: Dopant, n_dopant: float, t_k: float = 300.0, n_comp: float = 0.0) -> float:
    return free_carriers_cm3(d, n_dopant, t_k, n_comp) / n_dopant
