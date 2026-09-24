"""Error budget for the room-temperature NV-NV entangling gate (expert-track project Q-1).

The Lindblad model in adamas.opensys assumes Markovian noise. Real NV dephasing is dominated by a slow
nuclear-spin bath, so coherence decays as exp(-(t/T2*)^2) in free evolution and, for a slow bath,
exp(-(t/T2)^3) under a Hahn echo [hahn1950], [delange2010], [maze2008prb], [dobrovitski2008].

Gate: H = 2 pi nu |11><11| = 2 pi nu (1 - Z1 - Z2 + Z1 Z2) / 4 with nu = 52 MHz nm^3 / r^3
[neumann2010natphys], [dolde2013]. A simultaneous pi pulse on both spins at half time cancels every
single-spin Z term (including quasi-static detuning) and keeps Z1 Z2, so the echo gate equals CZ up to
local phases, with the same duration t = 1 / (2 nu).

All noise here is diagonal and independent on the two spins. If spin k keeps a coherence factor w_k,
the state fidelity of CZ|++> is exactly
        F_coherent = (1 + w1)(1 + w2) / 4 .
Preparation: each NV must be in the negative charge state (about 0.70 to 0.75 under green light
[aslam2013]) and spin polarized [manson2006], [robledo2011njp]. With per-NV preparation probability q
and no post-selection, a failed preparation is modeled as a fully mixed two-qubit state (fidelity 1/4):
        F = q^2 (1 - eps)^n_pulses F_coherent + (1 - q^2) / 4 .
Double-quantum encoding (|+1>, |-1> as the qubit on both NVs) quadruples the coupling and doubles the
sensitivity to magnetic noise, a technique used in NV-NV coupling experiments [neumann2010natphys], [dolde2013].

This is a model of this repository. It does not claim to know the sample parameters of any published
experiment; it shows which parameter combinations are consistent with reported fidelities
(0.67 [dolde2013], 0.82 [dolde2014]).
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .coupling import dipolar_coupling_khz


@dataclass(frozen=True)
class GateBudget:
    r_nm: float = 25.0
    t2star_us: float = 30.0          # free-induction dephasing time of each NV
    t2_us: float = 600.0             # Hahn-echo time of each NV
    echo: bool = True
    double_quantum: bool = False
    q_prep: float = 1.0              # per-NV probability of correct charge and spin state (1 = post-selected)
    pulse_error: float = 0.0         # error per pi or pi/2 pulse
    n_pulses: int = 6
    nu_khz: float | None = None      # override the 52/r^3 coupling with a measured value (orientation changes it)
    t2b_us: float | None = None      # second spin's echo time when the two differ

    @property
    def coupling_khz(self) -> float:
        if self.nu_khz is not None:
            return self.nu_khz
        return float(dipolar_coupling_khz(self.r_nm)) * (4.0 if self.double_quantum else 1.0)

    @property
    def t_gate_us(self) -> float:
        return 1e3 / (2 * self.coupling_khz)

    def _w(self, t2_us: float) -> float:
        k = 2.0 if (self.double_quantum and self.nu_khz is None) else 1.0   # a measured DQ T2 already includes the factor
        if self.echo:
            return float(np.exp(-(self.t_gate_us * k ** (2 / 3) / t2_us) ** 3))
        return float(np.exp(-(self.t_gate_us * k / self.t2star_us) ** 2))

    @property
    def w(self) -> float:
        """Single-spin coherence factor at the end of the gate (first spin)."""
        return self._w(self.t2_us)

    @property
    def f_coherent(self) -> float:
        wb = self._w(self.t2b_us) if self.t2b_us else self.w
        return (1 + self.w) * (1 + wb) / 4

    @property
    def fidelity(self) -> float:
        good = self.q_prep ** 2
        return good * (1 - self.pulse_error) ** self.n_pulses * self.f_coherent + (1 - good) / 4

    def breakdown(self) -> dict:
        """Infidelity attributed to each mechanism, switching them on one at a time."""
        from dataclasses import replace as _r
        ideal = _r(self, t2star_us=1e9, t2_us=1e9, t2b_us=None, q_prep=1.0, pulse_error=0.0)
        deph = _r(self, q_prep=1.0, pulse_error=0.0)
        puls = _r(self, q_prep=1.0)
        return {"dephasing": ideal.fidelity - deph.fidelity, "pulses": deph.fidelity - puls.fidelity,
                "preparation": puls.fidelity - self.fidelity, "total_fidelity": self.fidelity}


# Published pair of [dolde2013]: two NVs 25 +/- 2 nm apart with different orientations; single-quantum dipolar coupling
# 4.93 +/- 0.05 kHz (the 52/r^3 rule gives 3.3 kHz at 25 nm; the angular factor accounts for the rest); double-quantum
# echo times T2A = 150 +/- 18 us and T2B = 514 +/- 50 us; echo on both spins; Bell fidelity 0.67 +/- 0.04, raised to
# 0.82 with optimal-control pulses on the same pair [dolde2014]. Pulse count of the tomography sequence is an estimate.
DOLDE2013 = {"r_nm": 25.0, "nu_sq_khz": 4.93, "nu_dq_khz": 4 * 4.93, "t2a_us": 150.0, "t2b_us": 514.0, "fidelity": 0.67,
             "fidelity_optimal_control": 0.82, "n_pulses": 8}


def published_check(q_prep: float = 1.0, pulse_error: float = 0.0) -> GateBudget:
    c = DOLDE2013
    return GateBudget(r_nm=c["r_nm"], nu_khz=c["nu_dq_khz"], t2_us=c["t2a_us"], t2b_us=c["t2b_us"], echo=True,
                      double_quantum=True, q_prep=q_prep, pulse_error=pulse_error, n_pulses=c["n_pulses"])


def required_t2_us(r_nm: float, target: float, double_quantum: bool = False) -> float:
    """Echo T2 (both spins equal, perfect preparation and pulses) needed to reach a target fidelity."""
    lo, hi = 1.0, 1e7
    for _ in range(80):
        mid = (lo * hi) ** 0.5
        if GateBudget(r_nm, 1e9, mid, True, double_quantum).fidelity >= target:
            hi = mid
        else:
            lo = mid
    return hi
