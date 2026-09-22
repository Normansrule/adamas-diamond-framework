"""Power-converter loss model: what diamond buys over silicon carbide (SiC) and gallium nitride (GaN) in a real switch.

1. Temperature dependence of on-resistance (drift region, unipolar, fully or partially ionized):
       R_on(T) / R_on(300 K) = (T / 300)^alpha  /  [ f_ion(T) / f_ion(300) ]
   with lattice-scattering mobility exponents alpha: Si 2.4 [jacoboni1977], [arora1982]; 4H-SiC 2.4 [kimoto2014];
   GaN two-dimensional electron gas 1.5 [mishra2008]; diamond holes 2.8 [pernot2010]. f_ion is the ionized fraction of
   the drift-region acceptors from adamas.doping ([lagrange1998], [sze2006]); for Si, SiC, GaN it is taken as 1.
   The diamond drift doping is the unipolar-limit value N = eps Ec^2 / (2 q BV) [baliga1982].

2. Half-bridge switch loss, per switch, at duty 0.5 [erickson2020], [kassakian2023]:
       P_cond = I^2 R_on,sp / A          P_sw = f * (1/2) C_oss,sp A V^2      C_oss,sp ~ eps / W_drift = eps Ec / (2 BV)
   Optimizing the die area A gives
       A* = I sqrt( R_on,sp / (f C_oss,sp V^2 / 2) ),     P_min = 2 I V sqrt( f R_on,sp C_oss,sp / 2 ) ,
   so the material figure of merit for a hard-switched converter is sqrt(R_on,sp * C_oss,sp), the Baliga high-frequency
   figure of merit in another guise [baliga1989], [huang2004], [shenai2018]. Gate charge, reverse recovery, and dynamic
   R_on (a known GaN issue [uren2017], [meneghini2021]) are not modeled; this is a first-order comparison.

3. Junction-temperature ceiling per material, used for derating: Si 175 C [lutz2018], SiC 250 C (package-limited today,
   [she2017]), GaN 200 C [meneghini2021], diamond 400 C demonstrated [kawarada2014], [umezawa2012].
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from . import doping
from .constants import Q
from .materials import MATERIALS, Material, permittivity_f_cm
from .power import MEASURED_DIAMOND, ron_sp_mohm_cm2

MOBILITY_EXPONENT = {"Si": 2.4, "4H-SiC": 2.4, "GaN": 1.5, "Ga2O3": 1.8, "Diamond": 2.8}
TJ_MAX_C = {"Si": 175.0, "4H-SiC": 250.0, "GaN": 200.0, "Ga2O3": 250.0, "Diamond": 400.0}


def drift_doping_cm3(m: Material, bv_v: float) -> float:
    return permittivity_f_cm(m) * (m.ec_mv_cm * 1e6) ** 2 / (2 * Q * bv_v)


def ron_temperature_factor(name: str, t_k: float, bv_v: float = 1200.0, bulk_doped: bool = True) -> float:
    """R_on(T)/R_on(300 K). For diamond the drift-region boron ionization rises with T and fights the mobility fall."""
    fac = (t_k / 300.0) ** MOBILITY_EXPONENT[name]
    if name == "Diamond" and bulk_doped:
        n = drift_doping_cm3(MATERIALS["Diamond"], bv_v)
        d = doping.DOPANTS["C:B"]
        fac /= doping.ionized_fraction(d, n, t_k) / doping.ionized_fraction(d, n, 300.0)
    return fac


def coss_sp_f_cm2(m: Material, bv_v: float) -> float:
    return permittivity_f_cm(m) * (m.ec_mv_cm * 1e6) / (2 * bv_v)


@dataclass(frozen=True)
class SwitchDesign:
    area_cm2: float
    p_cond_w: float
    p_sw_w: float

    @property
    def p_total_w(self) -> float:
        return self.p_cond_w + self.p_sw_w


def optimum_switch(ron_sp_mohm_cm2: float, coss_sp: float, v_op: float, i_a: float, f_hz: float) -> SwitchDesign:
    r = ron_sp_mohm_cm2 * 1e-3
    k = 0.5 * coss_sp * v_op ** 2 * f_hz
    a = i_a * math.sqrt(r / k)
    return SwitchDesign(a, i_a ** 2 * r / a, k * a)


def material_switch(name: str, bv_v: float, v_op: float, i_a: float, f_hz: float, t_k: float = 300.0,
                    measured: str | None = None) -> SwitchDesign:
    """Ideal-limit switch of a material, or the measured diamond device `measured` (key of power.MEASURED_DIAMOND)."""
    m = MATERIALS[name]
    if measured:
        r = MEASURED_DIAMOND[measured]["ron_mohm_cm2"] * (bv_v / MEASURED_DIAMOND[measured]["bv_v"]) ** 2
    else:
        r = ron_sp_mohm_cm2(m, bv_v, "p" if name == "Diamond" else "n")
    r *= ron_temperature_factor(name, t_k, bv_v, bulk_doped=measured is None)
    return optimum_switch(r, coss_sp_f_cm2(m, bv_v), v_op, i_a, f_hz)


def converter_efficiency(name: str, bv_v: float, v_op: float, i_a: float, f_hz: float, n_switches: int = 6,
                         t_k: float = 300.0, measured: str | None = None) -> float:
    """Efficiency of an inverter whose only losses are its n switches (default: three-phase, 6 switches)."""
    p_out = v_op * i_a * 0.9                        # rough DC-bus to AC output power at 0.9 utilization
    loss = n_switches * material_switch(name, bv_v, v_op, i_a, f_hz, t_k, measured).p_total_w
    return p_out / (p_out + loss)


APPLICATIONS = [
    # name, bus voltage V, device class V, current A, switching Hz, sources
    ("Electric-vehicle traction inverter, 800 V bus", 800.0, 1200.0, 300.0, 20e3, ("reimers2019", "jung2017")),
    ("Data-center power supply, 400 V bus", 400.0, 650.0, 20.0, 300e3, ("masanet2020", "jones2016")),
    ("Solar string inverter, 1000 V", 1000.0, 1700.0, 50.0, 50e3, ("huang2017",)),
    ("Medium-voltage grid converter, 6.5 kV", 6500.0, 10000.0, 100.0, 5e3, ("huang2017", "she2017")),
    ("Down-hole and aerospace actuator, 300 C ambient", 270.0, 650.0, 10.0, 100e3, ("watson2015", "johnson2004")),
]
