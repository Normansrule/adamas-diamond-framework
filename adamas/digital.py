"""Delay, power, and gate-budget estimates for single-carrier (p-channel only) diamond logic.

Ratioed enhancement/depletion logic is the style silicon used before complementary logic took over
[meadconway1980], [rabaey2003], and the style every unipolar technology still uses: organic [myny2012],
metal-oxide thin-film [biggs2021], [ozer2024], and early carbon-nanotube processors [shulaker2013].
Diamond inverters, NOR, and NAND gates in this style: [liu2014], [liu2017].

Model (first order, long channel, [rabaey2003]):
    C_in   = Cox W L (+ overlap, ignored)
    t_rise = C_L (V/2) / I_load          t_fall = C_L (V/2) / (I_drv - I_load)
    P_static = V I_load * (fraction of time the output is low)      P_dyn = a C_L V^2 f
Wire delay, when needed, follows Elmore [elmore1948].
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from .constants import EPS0
from .logic import Fet

# Historical and unipolar reference processors. Numbers are as reported in the cited papers;
# entries marked approx should be re-checked against the paper before quoting.
REFERENCE_PROCESSORS = [
    # name, devices or gates, unit, clock_hz, technology, bibkey
    ("Intel 4004 (1971)", 2300, "transistors", 740e3, "p-channel silicon-gate MOS, 10 um", "faggin1996"),
    ("Organic 8-bit (2012)", 3381, "transistors (approx)", 40, "p-type organic thin film", "myny2012"),
    ("Carbon nanotube computer (2013)", 178, "transistors", 1e3, "p-type carbon nanotube FETs", "shulaker2013"),
    ("RV16X-NANO (2019)", 14000, "transistors", 1e4, "complementary carbon nanotube FETs", "hills2019"),
    ("PlasticARM (2021)", 18334, "NAND2-equivalent gates", 29e3, "n-type metal-oxide thin film, resistive load", "biggs2021"),
    ("Flex-RV (2024)", 12600, "gates (approx)", 60e3, "n-type metal-oxide thin film", "ozer2024"),
]


def gate_capacitance_f(f: Fet) -> float:
    cox = f.eps_ox * EPS0 * 1e-2 / (f.tox_nm * 1e-7)       # F/cm^2
    return cox * f.w_um * f.l_um * 1e-8


@dataclass(frozen=True)
class EDGate:
    driver: Fet = Fet(mu_cm2_vs=150, vth=1.5, w_um=16.0, l_um=2.0)
    load: Fet = Fet(mu_cm2_vs=150, vth=-2.0, w_um=2.0, l_um=2.0)
    vdd: float = 10.0
    fanout: int = 3
    c_wire_f: float = 20e-15

    @property
    def c_load_f(self) -> float:
        return self.fanout * gate_capacitance_f(self.driver) + self.c_wire_f

    @property
    def i_load_a(self) -> float:
        return self.load.current(0.0, self.vdd)

    @property
    def i_driver_a(self) -> float:
        return self.driver.current(self.vdd, self.vdd)

    @property
    def strength_ratio(self) -> float:
        return self.i_driver_a / self.i_load_a

    @property
    def t_rise_s(self) -> float:
        return self.c_load_f * self.vdd / 2 / self.i_load_a

    @property
    def t_fall_s(self) -> float:
        return self.c_load_f * self.vdd / 2 / (self.i_driver_a - self.i_load_a)

    @property
    def t_pd_s(self) -> float:
        return 0.5 * (self.t_rise_s + self.t_fall_s)

    def static_power_w(self, low_fraction: float = 0.5) -> float:
        return self.vdd * self.i_load_a * low_fraction

    def dynamic_power_w(self, f_hz: float, activity: float = 0.1) -> float:
        return activity * self.c_load_f * self.vdd ** 2 * f_hz

    def scaled(self, gate_length_um: float) -> "EDGate":
        """Constant W/L shrink of both transistors (no velocity saturation, so optimistic below ~0.5 um)."""
        s = gate_length_um / self.driver.l_um
        return replace(self, driver=replace(self.driver, w_um=self.driver.w_um * s, l_um=gate_length_um),
                       load=replace(self.load, w_um=self.load.w_um * s, l_um=gate_length_um),
                       c_wire_f=self.c_wire_f * s)


def processor_estimate(n_gates: int, gate: EDGate = EDGate(), logic_depth: int = 24, activity: float = 0.1) -> dict:
    """Clock, power, and areal power for an n_gates block. logic_depth = gates per pipeline stage."""
    f = 1.0 / (logic_depth * 2 * gate.t_pd_s)
    p = n_gates * (gate.static_power_w() + gate.dynamic_power_w(f, activity))
    return {"f_clk_hz": f, "power_w": p, "static_fraction": n_gates * gate.static_power_w() / p,
            "t_pd_ns": gate.t_pd_s * 1e9, "power_per_gate_mw": p / n_gates * 1e3}
