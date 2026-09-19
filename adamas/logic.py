"""Digital logic on diamond: square-law field-effect transistor (FET) model and inverter transfer curves.

Why this module exists: diamond has excellent p-channel transistors (hydrogen-terminated surface
channels: [kawarada1994], [kawarada2017], [sasama2022]) but only a first n-channel demonstration
[liao2024], so today's diamond logic is p-channel only, built from an enhancement-mode driver and a
depletion-mode load ([liu2014], [liu2017]). Complementary logic on one diamond wafer is a research
target ([zhao2024]).

Model: long-channel square law [sze2006]
    triode:      I = k ((Vov) Vds - Vds^2 / 2),   saturation: I = k Vov^2 / 2,   k = mu Cox W / L
Default numbers are illustrative, chosen inside the ranges reported in the papers above.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .constants import EPS0


@dataclass(frozen=True)
class Fet:
    mu_cm2_vs: float = 150.0   # channel mobility
    tox_nm: float = 30.0       # gate insulator thickness (atomic-layer-deposited aluminum oxide)
    eps_ox: float = 9.0
    w_um: float = 100.0
    l_um: float = 2.0
    vth: float = 1.0           # magnitude of threshold; positive = enhancement, negative = depletion

    @property
    def k(self) -> float:      # A/V^2
        cox = self.eps_ox * EPS0 * 1e-2 / (self.tox_nm * 1e-7)  # F/cm^2
        return self.mu_cm2_vs * cox * self.w_um / self.l_um

    def current(self, vgs: float, vds: float) -> float:
        """Drain current magnitude for gate drive vgs and drain bias vds (both as magnitudes)."""
        vov = vgs - self.vth
        if vov <= 0 or vds <= 0:
            return 0.0
        return self.k * (vov * vds - vds ** 2 / 2) if vds < vov else self.k * vov ** 2 / 2


def inverter_vtc(driver: Fet, load: Fet, vdd: float = 10.0, n: int = 201, complementary: bool = False):
    """Voltage transfer curve, in magnitude convention (diamond p-channel rails are negative in the lab).

    complementary=False: single-carrier enhancement/depletion inverter [liu2017]; load has gate tied to source.
    complementary=True: the load is the opposite-carrier transistor, driven by (vdd - vin).
    """
    vin = np.linspace(0, vdd, n)
    vout = np.empty(n)
    grid = np.linspace(0, vdd, 2001)
    for i, v in enumerate(vin):
        i_drv = np.array([driver.current(v, vo) for vo in grid])
        vg_load = (vdd - v) if complementary else 0.0
        i_load = np.array([load.current(vg_load, vdd - vo) for vo in grid])
        vout[i] = grid[np.argmin(np.abs(i_drv - i_load))]
    return vin, vout


def noise_margins(vin, vout):
    """Low and high noise margins from the unity-gain points of the transfer curve."""
    gain = np.gradient(vout, vin)
    idx = np.where(gain <= -1)[0]
    if len(idx) == 0:
        return 0.0, 0.0, float(np.min(gain))
    vil, vih = vin[idx[0]], vin[idx[-1]]
    voh, vol = vout[idx[0]], vout[idx[-1]]
    return float(vil - vol), float(voh - vih), float(np.min(gain))
