"""Quantum Device Library (QDL): the room-temperature diamond devices ADAMAS can describe, simulate, and plan to build.

Each device carries what it should do, the gates it can hold and the entanglement it can make (with the evidence for
each), its use cases, the figures of merit (current value with its source versus target with its basis), the build
route on the process traveler (adamas.traveler) with the machines it needs (adamas.atlas), the steps the traveler does
not yet have, and simulated pass/fail checks.

Labels (one per claim):
* demonstrated: done in a laboratory at or near room temperature (about 300 K), with a cited paper;
* reported: published, but the number shown here is a bound or depends on special conditions stated next to it;
* simulated: computed by this package, not measured;
* proposed: on paper only (theory or a proposal), or an ADAMAS design idea;
* cryogenic: demonstrated only when cooled (a few kelvin), so it is not a room-temperature device today.

Honesty rules this module enforces (tests/test_qdl.py):
* "Transistor", "memory cell" and "resistor" are analogies only and always appear next to the real name.
* No parity with superconducting qubits is implied: those operate near 10 to 20 mK (base temperature below 20 mK, 14 mK
  under a 50-qubit load [krinner2019]); NV registers are small and their two-qubit numbers are far from a processor's.
* A Bell-state fidelity and a gate fidelity are different metrics, so they are kept in different fields and are never
  ranked against each other.
* Every number has a source key or a Python function; a number not yet confirmed from its paper is listed as "to
  confirm" (open_numbers()) and shown in docs/devices/README.md and docs/STATUS.md.

Pass/fail. Each check simulates a measurement with a fixed seed, analyzes it with the same code a student uses on real
data (adamas.fitting) where a fit applies, and compares the result with a threshold that is either sourced or an
ADAMAS design threshold stated as such. Each check has a degraded twin (one physical fault) that must fail; the pass
rate of the nominal check over independent seeds is computed by pass_rate() and written to the device pages.
"""
from __future__ import annotations

import copy
import functools
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STATUSES = ("demonstrated", "reported", "simulated", "proposed", "cryogenic")
STATUS_TEXT = {
    "demonstrated": "Demonstrated near room temperature, with a cited paper",
    "reported": "Published, with a bound or special conditions stated next to the number",
    "simulated": "Computed by this package, not measured",
    "proposed": "On paper only: theory, a proposal, or an ADAMAS design idea",
    "cryogenic": "Demonstrated only when cooled to a few kelvin; not a room-temperature device today",
}
FAMILIES = {
    "register": "Quantum register (computing)",
    "link": "Links between registers",
    "sensing": "Sensing (physics and engineering)",
    "chemistry": "Chemistry and materials analysis",
    "life": "Biology and medicine",
    "navigation": "Navigation",
    "comms": "Communications and microwave",
    "simulation": "Quantum simulation",
    "design": "Design and integration",
}
SUPERCONDUCTING_NOTE = ("Superconducting qubits operate near 10 to 20 mK (dilution-refrigerator base below 20 mK, 14 mK "
                        "under a 50-qubit load [krinner2019]). Nothing here implies parity with them.")


# ---------------------------------------------------------------------------------------------------------- helpers
def _fom(name, unit, better, current=None, target=None):
    return {"name": name, "unit": unit, "better": better, "current": current, "target": target}


def _cur(value, label, refs, conditions, err=None, bound=None, python=None):
    return {"value": value, "err": err, "bound": bound, "label": label, "refs": refs, "conditions": conditions, "python": python}


def _todo(text, refs):
    """A current value that exists in the literature but is not yet confirmed from the paper (listed in STATUS)."""
    return {"value": None, "todo": text, "label": "reported", "refs": refs, "conditions": ""}


def _tgt(value, basis, python=None, refs=()):
    return {"value": value, "basis": basis, "python": python, "refs": list(refs)}


def _g(name, label, refs, note=""):
    return {"name": name, "label": label, "refs": refs, "note": note}


# ------------------------------------------------------------------------------------------- computed design values
T2_ROOM_MS = 1.8           # electron Hahn-echo T2, 12C-enriched, room temperature [balasubramanian2009] (adamas.nv)


def r_max_nm(fidelity: float = 0.99, t2_ms: float = T2_ROOM_MS) -> float:
    """Largest NV-NV spacing whose coherence-limited gate bound 0.5 (1 + exp(-t/T2)), t = 1/(2 nu), nu = 52 MHz nm^3/r^3
    (adamas.coupling.gate_fidelity_bound, perpendicular orientation) still reaches `fidelity`. Assumptions: one spin's
    exponential echo decay, no control errors, perfect charge state. The two-spin stretched-echo model of
    adamas.gate_budget allows wider spacings; this library uses the stricter bound everywhere."""
    from .coupling import DIPOLAR_MHZ_NM3
    t_us = -math.log(2 * fidelity - 1) * t2_ms * 1e3
    nu_khz = 1e3 / (2 * t_us)
    return (DIPOLAR_MHZ_NM3 * 1e3 / nu_khz) ** (1 / 3)


def required_t2_us(r_nm: float = 10.0, fidelity: float = 0.99) -> float:
    """Echo time two NVs r_nm apart need for `fidelity` under the same bound as r_max_nm (adamas.coupling: single
    spin, exponential decay, no control errors). The two-spin, stretched-echo model of adamas.gate_budget is less strict
    (it allows wider spacings); this library uses the stricter bound throughout, so its numbers agree with each other."""
    from .coupling import gate_time_us
    return float(gate_time_us(r_nm)) / -math.log(2 * fidelity - 1)


def required_t2_10nm_us() -> float:
    return required_t2_us(10.0, 0.99)


def required_t2_10nm_ms() -> float:
    return required_t2_10nm_us() / 1e3


def nv_depth_nm(energy_kev: float) -> float:
    from .coupling import implant_rule_of_thumb
    return implant_rule_of_thumb(energy_kev)[0]


def measured_contrast() -> float:
    from .photophysics import measured_contrast as mc
    return float(mc())


def polarization() -> float:
    from .photophysics import polarization as p
    return float(p())


def gamma_mhz_per_mt() -> float:
    from .nv import GAMMA_MHZ_PER_MT
    return float(GAMMA_MHZ_PER_MT)


def dddt_khz_per_k() -> float:
    from .nv import DDDT_MHZ_PER_K
    return float(DDDT_MHZ_PER_K * 1e3)


PYTHON = {"adamas.qdl.r_max_nm": r_max_nm, "adamas.qdl.required_t2_10nm_us": required_t2_10nm_us, "adamas.qdl.required_t2_10nm_ms": required_t2_10nm_ms,
          "adamas.qdl.measured_contrast": measured_contrast, "adamas.qdl.polarization": polarization,
          "adamas.qdl.gamma_mhz_per_mt": gamma_mhz_per_mt, "adamas.qdl.dddt_khz_per_k": dddt_khz_per_k}


# --------------------------------------------------------------------------------------------------------- checks
def _k98() -> float:
    from .build_program import _k_normal
    return _k_normal()          # 98.98 % two-sided coverage per test, as in build program P2


def check_echo(seed=0, t2_us=1800.0, need_us=None, noise=0.003, amp=0.1):
    """Simulate a Hahn-echo decay (stretch 3) and fit it with adamas.fitting.fit_echo; pass when the fitted T2, less
    k standard errors, still exceeds what a 0.99 two-NV gate at 10 nm needs (required_t2_us, same bound as r_max_nm).
    The nominal 1.8 ms is the room-temperature value of 12C-enriched diamond [balasubramanian2009]."""
    from . import fitting, nv
    need = required_t2_10nm_us() if need_us is None else need_us
    r = np.random.default_rng(seed)
    x = np.linspace(0, 6000.0, 601)
    y = amp * nv.hahn_echo(x, t2_us, 3.0) + r.normal(0, noise, x.size)
    try:
        f = fitting.fit_echo(x, y); t2, e = float(f.params["T2_us"]), float(f.errors["T2_us"])
    except Exception:          # a failed fit is a failed check
        t2, e = float("nan"), float("inf")
    low = t2 - _k98() * e
    return {"value": t2, "err": e, "unit": "µs", "threshold": need, "pass": bool(np.isfinite(low) and low >= need),
            "what": f"fitted T₂ − k·σ ≥ {need:.0f} µs (0.99 gate at 10 nm)"}


def check_selective(seed=0, rabi_mhz=0.2, a_mhz=2.16, threshold=0.99):
    """Hamiltonian simulation of the electron-14N CNOT by a hyperfine-selective pi pulse (adamas.register.bell_fidelity):
    a strong drive also rotates the other hyperfine line. Deterministic (seed unused)."""
    from .register import bell_fidelity
    f = float(bell_fidelity(a_mhz, rabi_mhz))
    return {"value": f, "err": 0.0, "unit": "", "threshold": threshold, "pass": bool(f >= threshold),
            "what": f"Bell-state fidelity after the selective CNOT ≥ {threshold} (a Bell fidelity, not a gate fidelity)"}


def check_coupler(seed=0, r_nm=10.0, t2_us=1800.0, noise=0.02, fidelity=0.99):
    """Simulate a double-electron-resonance oscillation at nu = 52 MHz nm^3 / r^3, fit its frequency with
    adamas.fitting.fit_ramsey (time in ms, frequency in kHz), and pass when the fitted coupling, less k standard errors,
    is strong enough for a coherence-limited `fidelity` gate with T2 = 1.8 ms [balasubramanian2009] (r_max_nm)."""
    from . import fitting
    from .coupling import dipolar_coupling_khz
    nu = float(dipolar_coupling_khz(r_nm))
    nu_min = float(dipolar_coupling_khz(r_max_nm(fidelity, t2_us / 1e3)))
    r = np.random.default_rng(seed)
    x = np.linspace(0, 3.0, 1201)                      # ms
    y = 0.25 * (1 - np.cos(2 * np.pi * nu * x) * np.exp(-(x / (t2_us / 1e3)) ** 2)) + r.normal(0, noise, x.size)
    try:
        f = fitting.fit_ramsey(x, y); v, e = abs(float(f.params["detuning_MHz"])), float(f.errors["detuning_MHz"])
    except Exception:
        v, e = float("nan"), float("inf")
    low = v - _k98() * e
    return {"value": v, "err": e, "unit": "kHz", "threshold": nu_min, "pass": bool(np.isfinite(low) and low >= nu_min),
            "what": f"fitted coupling − k·σ ≥ {nu_min:.2f} kHz (r ≤ {r_max_nm(fidelity, t2_us / 1e3):.1f} nm)"}


def check_readout(seed=0, photons_per_rep=0.03, reps=5000, contrast=None, shots=2000, threshold=0.96):
    """Repetitive single-shot readout of a nuclear spin: each repetition maps the nuclear state onto the electron and
    counts photons (Poisson). Bright mean = reps x photons_per_rep, dark mean = bright x (1 - C) with C the measured
    contrast of adamas.photophysics. The count threshold is chosen on half the shots and the fidelity is evaluated on
    the other half. Assumes a quantum non-demolition readout (no nuclear flips during the sequence), which the real
    experiment does not have: there flips limit the fidelity, here photon statistics do. Pass when the fidelity reaches
    the demonstrated room-temperature 0.96 [dreau2013]. photons_per_rep is illustrative."""
    c = measured_contrast() if contrast is None else contrast
    r = np.random.default_rng(seed)
    lb = reps * photons_per_rep; ld = lb * (1 - c)
    b = r.poisson(lb, shots); d = r.poisson(ld, shots)
    h = shots // 2
    cand = np.arange(int(ld * 0.5), int(lb * 1.5) + 2)
    acc = [(np.mean(b[:h] >= t) + np.mean(d[:h] < t)) / 2 for t in cand]
    t = cand[int(np.argmax(acc))]
    fid = float((np.mean(b[h:] >= t) + np.mean(d[h:] < t)) / 2)
    err = math.sqrt(fid * (1 - fid) / shots)
    return {"value": fid, "err": err, "unit": "", "threshold": threshold, "pass": bool(fid >= threshold),
            "what": f"readout fidelity ≥ {threshold} [dreau2013], no nuclear flips modeled"}


def check_polarize(seed=0, beta=1.0, t_us=3.0, frac=0.99):
    """Rate-equation optical pumping (adamas.photophysics.polarization): pass when the pump has reached `frac` of its own
    steady state (ADAMAS design threshold: the reset is limited by physics, not by a short laser pulse)."""
    from .photophysics import polarization as pol
    p, ss = float(pol(beta, t_us)), float(pol(beta, 50.0))
    return {"value": p, "err": 0.0, "unit": "", "threshold": frac * ss, "pass": bool(p >= frac * ss),
            "what": f"polarization ≥ {frac:g} × steady state ({ss:.3f})"}


def check_rabi(seed=0, rabi_mhz=10.0, design_mhz=10.0, noise=0.004, amp=0.1, tol=0.05):
    """Simulate Rabi oscillations driven through the line, fit with adamas.fitting.fit_rabi, and pass when the fitted
    Rabi frequency, widened by k standard errors, stays within `tol` (5 %, ADAMAS design threshold) of the design value.
    The 10 MHz design value is illustrative (an ADAMAS choice, not a sourced number)."""
    from . import fitting, nv
    r = np.random.default_rng(seed)
    x = np.linspace(0, 0.5, 251)                        # µs
    y = amp * nv.rabi(x, rabi_mhz, 0.0, 2.0) + r.normal(0, noise, x.size)
    try:
        f = fitting.fit_rabi(x, y); v, e = float(f.params["rabi_MHz"]), float(f.errors["rabi_MHz"])
    except Exception:
        v, e = float("nan"), float("inf")
    return {"value": v, "err": e, "unit": "MHz", "threshold": design_mhz, "pass": bool(np.isfinite(v) and abs(v - design_mhz) + _k98() * e <= tol * design_mhz),
            "what": f"|Ω_fit − {design_mhz:g} MHz| + k·σ ≤ {100 * tol:g} %"}


def check_g2(seed=0, g0=0.2, tau_ns=12.0, noise=0.03):
    """Simulate a Hanbury Brown-Twiss correlation, fit with adamas.fitting.fit_g2, and pass when g2(0) is below 0.5 by
    more than two standard errors: one emitter [kurtsiefer2000]. g0 = 0.2 stands for background light (illustrative)."""
    from . import fitting
    r = np.random.default_rng(seed)
    x = np.linspace(-80, 80, 321)
    y = 1 - (1 - g0) * np.exp(-np.abs(x) / tau_ns) + r.normal(0, noise, x.size)
    try:
        f = fitting.fit_g2(x, y); v, e = float(f.params["g2_zero"]), float(f.errors["g2_zero"])
    except Exception:
        v, e = float("nan"), float("inf")
    return {"value": v, "err": e, "unit": "", "threshold": 0.5, "pass": bool(np.isfinite(v) and v + 2 * e < 0.5),
            "what": "g⁽²⁾(0) + 2σ < 0.5 [kurtsiefer2000]"}


def check_detect(seed=0, contrast=0.012, linewidth_mhz=6.0, noise=0.0012):
    """The build-program P1 detection test with this device's parameters: zero-field ODMR, fit with
    adamas.fitting.fit_odmr, pass when depth / sigma >= 5 and the center is within half a line width of 2870 MHz.
    Defaults are the A1 kit noise model (illustrative kit values, adamas.build_program)."""
    from . import fitting, nv
    r = np.random.default_rng(seed)
    f = np.arange(2790.0, 2950.0 + 1e-9, 0.5)
    y = nv.odmr_spectrum(f, np.zeros(3), contrast=contrast, linewidth_mhz=linewidth_mhz, hyperfine=False) + r.normal(0, noise, f.size)
    try:
        fit = fitting.fit_odmr(f, y, max_lines=1)
        snr = float(fit.params["depth1"] / fit.errors["depth1"]); ok_c = abs(fit.params["center1"] - 2870.0) < linewidth_mhz / 2
    except Exception:
        snr, ok_c = 0.0, False
    return {"value": snr, "err": 0.0, "unit": "σ", "threshold": 5.0, "pass": bool(snr >= 5 and ok_c),
            "what": "dip depth / σ ≥ 5 at 2870 MHz (five-sigma detection)"}


def check_thermo(seed=0, coupling=1.0):
    """The build-program P1 thermometer with a thermal-contact factor: the diamond sees `coupling` of the plate's
    temperature change (1 = good contact). Pass when the fitted dD/dT agrees with -74.2(7) kHz/K [acosta2010] within
    k combined standard errors (k for 98.98 % coverage, as the other checks). The D(T) model of adamas.nv is linear
    at exactly this slope, so the check tests the measurement chain (contact, fit), not the slope itself."""
    from . import build_program as B, fitting, nv
    r = np.random.default_rng(seed)
    f = np.arange(2840.0, 2900.0 + 1e-9, 0.25)
    t_k = np.array((20.0, 27.5, 35.0, 42.5, 50.0)) + 273.15
    c, e = [], []
    for t in t_k:
        t_d = 300.0 + coupling * (t - 300.0)
        shift = nv.zero_field_splitting_mhz(t_d) - nv.zero_field_splitting_mhz(300.0)
        y = nv.odmr_spectrum(f - shift, np.zeros(3), contrast=B.A1_CONTRAST, linewidth_mhz=B.A1_LINEWIDTH, hyperfine=False) + r.normal(0, B.A1_NOISE, f.size)
        try:
            fit = fitting.fit_odmr(f, y, max_lines=1); c.append(fit.params["center1"]); e.append(fit.errors["center1"])
        except Exception:
            return {"value": float("nan"), "err": float("inf"), "unit": "kHz/K", "threshold": B.DDDT_KHZ_K, "pass": False, "what": "fit failed"}
    c, e = np.array(c), np.array(e); w = 1 / e ** 2
    X = np.vstack([np.ones_like(t_k), t_k - t_k.mean()]).T
    cov = np.linalg.inv(X.T @ (w[:, None] * X)); beta = cov @ X.T @ (w * c)
    s, se = beta[1] * 1e3, math.sqrt(cov[1, 1]) * 1e3
    tol = _k98() * math.hypot(se, B.DDDT_SIGMA)
    return {"value": float(s), "err": float(se), "unit": "kHz/K", "threshold": B.DDDT_KHZ_K, "pass": bool(abs(s - B.DDDT_KHZ_K) <= tol),
            "what": f"|dD/dT − (−74.2)| ≤ {tol:.1f} kHz/K"}


CHECKS = {"echo": check_echo, "selective": check_selective, "coupler": check_coupler, "readout": check_readout,
          "polarize": check_polarize, "rabi": check_rabi, "g2": check_g2, "detect": check_detect, "thermo": check_thermo}


def _chk(kind, title, nominal, degraded, fault, threshold_src, seed=0):
    """seed: the seed the documents and the website show (the pass rate uses seeds 1000 and up)."""
    return {"kind": kind, "title": title, "nominal": nominal, "degraded": degraded, "fault": fault, "threshold_src": threshold_src, "seed": seed}


# ---------------------------------------------------------------------------------------------------------- devices
REGISTER = "Room-temperature qubit register chip"
DEVICES = [
 {"id": "QDL-01", "name": "NV electron-spin qubit cell", "family": "register",
  "analogy": {"label": "memory bit cell", "fits": "It holds one bit of state at one site and is written and read by wires and light.",
              "breaks": "It holds a quantum superposition, not a 0 or 1, it is read by averaging at room temperature, and it is not refreshed."},
  "function": "Hold one qubit in the electron spin of a nitrogen-vacancy (NV) center and rotate it with microwaves.",
  "explanation": ("A nitrogen atom next to a missing carbon atom traps two electrons whose spin (S = 1) has three levels. "
                  "Green light pumps it into mₛ = 0, microwaves near 2.87 GHz rotate it between mₛ = 0 and −1, and the red "
                  "fluorescence is dimmer in mₛ = ±1 ([gruber1997]; contrast 0.31 in the rate model of adamas.photophysics), which reads it out. At room temperature the spin keeps its "
                  "phase for milliseconds under a Hahn echo in ¹²C-enriched diamond. It is the qubit every other register "
                  "device in this library serves."),
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["rong2015", "balasubramanian2009", "doherty2013"],
             "note": SUPERCONDUCTING_NOTE},
  "gates": [_g("Single-qubit rotations (X, Y, arbitrary axis)", "demonstrated", ["rong2015"], "average fidelity 0.999952 by randomized benchmarking"),
            _g("Hahn echo and dynamical decoupling", "demonstrated", ["hahn1950", "balasubramanian2009"])],
  "entanglement": [_g("None alone; see the conditional gate (QDL-03) and the dipolar coupler (QDL-04)", "demonstrated", ["rong2015"])],
  "use_cases": [_g("Processor qubit in a small room-temperature register", "demonstrated", ["rong2015", "waldherr2014"]),
                _g("Single-spin sensor (see QDL-17)", "demonstrated", ["degen2017"])],
  "fom": {"f1q": _fom("Single-qubit gate fidelity", "", "higher",
                      _cur(0.999952, "demonstrated", ["rong2015"], "room temperature, randomized benchmarking"),
                      _tgt(0.9999, "ADAMAS design threshold (proposed): stay below 10⁻⁴ error so two-qubit gates dominate the budget")),
          "t2": _fom("Electron Hahn-echo T₂", "ms", "higher",
                     _cur(1.8, "demonstrated", ["balasubramanian2009"], "¹²C-enriched diamond, room temperature"),
                     _tgt(required_t2_10nm_ms(), "T₂ a 0.99 two-NV gate at 10 nm needs (single-spin exponential bound, as r_max)", "adamas.qdl.required_t2_10nm_ms"))},
  "route": {"variant": "qubit", "steps": ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S13", "S16", "S18", "S19"],
            "overrides": {"S03": "Grow with ¹²CH₄ (isotopically enriched) so ¹³C spins do not shorten T₂.",
                          "S06": "Implant single ¹⁵N⁺ per aperture at 2.5 to 10 keV (about 4 to 15 nm deep by the rule of thumb in adamas.coupling).",
                          "S18": "Find the NV, measure ODMR, Rabi, Ramsey and echo (experiments B1 and C1)."},
            "extra": [], "atlas": ["M01", "M10", "M12", "M20", "M21", "M22", "M47", "M49", "M51", "M52"]},
  "layers": ["Al₂O₃ passivation", "Microwave line (QDL-08)", "¹²C diamond cap with NV", "Diamond substrate"],
  "checks": [_chk("echo", "Echo long enough for a 0.99 gate at 10 nm", {"t2_us": 1800.0}, {"t2_us": 100.0},
                  "Natural-abundance carbon and surface spins cut T₂ to 100 µs", "adamas.qdl.required_t2_us (52 MHz nm³/r³ and the single-spin bound)")],
  "failures": ["Charge state flips to NV⁰ under light", "Surface spins shorten T₂ for shallow NVs", "Strain splits and broadens the lines"],
  "open_problems": ["Single-shot electron readout at room temperature does not exist yet (see QDL-05)."],
  "links": {"labs": ["labs/qubit.html", "labs/photon.html"], "chapters": ["06_nv_center_physics.md"], "experiments": ["B1", "C1"], "loop": ["rabi", "ramsey", "echo"]}},

 {"id": "QDL-02", "name": "Nuclear-spin memory", "family": "register",
  "analogy": {"label": "storage capacitor", "fits": "It holds state for a long time next to the active device.",
              "breaks": "It stores a quantum state, it does not leak charge, and reading it is not destructive in the same way."},
  "function": "Store a qubit for seconds in a nuclear spin (¹⁴N, ¹⁵N, or a nearby ¹³C) next to the NV.",
  "explanation": ("Nuclear spins have a magnetic moment about a thousand times smaller than the electron's, so they hardly "
                  "feel the noise that dephases the electron. The NV's own nitrogen nucleus is always there; ¹³C nuclei sit "
                  "at random sites. The electron writes and reads them through the hyperfine interaction (QDL-03)."),
  "status": {"label": "reported", "temperature_k": 300, "refs": ["maurer2012", "waldherr2014"],
             "note": "The second-scale memory time needs isotopically purified diamond, decoupling and laser dissipation [maurer2012]."},
  "gates": [_g("Nuclear rotations by radio-frequency pulses", "demonstrated", ["waldherr2014"]),
            _g("Electron-nuclear swap (store and retrieve)", "demonstrated", ["maurer2012"])],
  "entanglement": [_g("Electron-nuclear Bell states; three nuclear spins entangled", "demonstrated", ["waldherr2014"], "fidelity above 0.85 for the three-nuclear-spin state")],
  "use_cases": [_g("Long memory for a room-temperature register", "reported", ["maurer2012"]),
                _g("Ancilla for room-temperature error correction", "demonstrated", ["waldherr2014"]),
                _g("Readout amplifier by repetitive mapping (QDL-05)", "demonstrated", ["neumann2010science", "dreau2013"])],
  "fom": {"memory": _fom("Memory time", "s", "higher",
                         _cur(1.0, "reported", ["maurer2012"], "¹³C, isotopically purified, decoupling plus laser dissipation, room temperature", bound=">"),
                         _tgt(None, "Set by the link time it must bridge; no link exists at room temperature yet (QDL-13 to QDL-16)"))},
  "route": {"variant": "qubit", "steps": ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S13", "S16", "S18", "S19"],
            "overrides": {"S06": "Use ¹⁵N⁺ to tell implanted from native nitrogen; the ¹⁵N nucleus is the deterministic memory.",
                          "S18": "Add a radio-frequency source and find the nuclear transitions (Atlas M53)."},
            "extra": [], "atlas": ["M20", "M22", "M53", "M52", "M47", "M51"]},
  "layers": ["Al₂O₃ passivation", "Microwave and RF line", "¹²C cap: NV + ¹⁵N nucleus", "Diamond substrate"],
  "checks": [], "no_check": "No nuclear decoupling model in the package yet; listed in docs/STATUS.md.",
  "failures": ["Laser light during electron readout dephases the nucleus", "¹³C sites are random, so registers differ chip to chip"],
  "open_problems": ["A memory is only useful if a link can fill it; no room-temperature link exists yet."],
  "links": {"labs": ["labs/qubit.html"], "chapters": ["08_quantum_processor_architecture.md"], "experiments": ["C2"], "loop": []}},

 {"id": "QDL-03", "name": "Electron-nuclear conditional gate", "family": "register",
  "analogy": {"label": "transistor", "fits": "One spin switches what happens to the other, as a gate voltage switches a channel.",
              "breaks": "It is reversible and coherent, it has no gain, and it acts on superpositions."},
  "function": "Flip the electron only if the nucleus is in one state (a CNOT), using a pulse that resolves the hyperfine line.",
  "explanation": ("The ¹⁴N hyperfine coupling of about 2.16 MHz splits the electron line in three. A weak microwave pulse "
                  "narrower than that splitting flips the electron for one nuclear state only: a controlled NOT. The same "
                  "trick runs the other way with radio-frequency pulses. Noise filtering has pushed it to 0.9992 at room temperature."),
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["xie2023", "rong2015"], "note": SUPERCONDUCTING_NOTE},
  "gates": [_g("CNOT (electron target, nucleus control)", "demonstrated", ["xie2023", "rong2015"]),
            _g("Nuclear-controlled phase gates", "demonstrated", ["waldherr2014"])],
  "entanglement": [_g("Electron-nuclear Bell states, deterministic", "demonstrated", ["rong2015", "xie2023"])],
  "use_cases": [_g("Two-qubit gate inside one register", "demonstrated", ["xie2023"]),
                _g("Error correction with nuclear ancillas", "demonstrated", ["waldherr2014"])],
  "fom": {"cnot": _fom("CNOT gate fidelity", "", "higher",
                       _cur(0.9992, "demonstrated", ["xie2023"], "electron and ¹⁴N, room temperature, noise filtering", err=0.00007),
                       None)},
  "route": {"variant": "qubit", "steps": ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S13", "S16", "S18", "S19"],
            "overrides": {"S18": "Calibrate the selective π pulse on one hyperfine line (Rabi frequency well below 2.16 MHz)."},
            "extra": [], "atlas": ["M20", "M22", "M51", "M53", "M47"]},
  "layers": ["Microwave line", "NV + ¹⁴N/¹⁵N nucleus", "Diamond substrate"],
  "checks": [_chk("selective", "Bell state from the selective CNOT stays above 0.99", {"rabi_mhz": 0.2}, {"rabi_mhz": 1.0},
                  "Drive too strong: the pulse also rotates the neighboring hyperfine line", "ADAMAS design threshold 0.99 on the Bell-state fidelity")],
  "failures": ["Drive strong enough to excite the neighboring hyperfine line", "Field drift detunes the selective pulse"],
  "open_problems": ["Gates between nuclei of different NVs still go through the electrons (QDL-04)."],
  "links": {"labs": ["labs/qubit.html", "labs/addressing.html"], "chapters": ["08_quantum_processor_architecture.md"], "experiments": ["C2"], "loop": ["rabi", "crosstalk"]}},

 {"id": "QDL-04", "name": "NV-NV dipolar coupler", "family": "register",
  "analogy": {"label": "transistor", "fits": "One NV's state controls the phase picked up by its neighbor.",
              "breaks": "The coupling is always on, falls as 1/r³, and only works for NVs about 10 to 25 nm apart."},
  "function": "Entangle two NV electron spins through their magnetic dipole coupling, ν = 52 MHz nm³ / r³.",
  "explanation": ("Two electron spins a few nanometers apart feel each other's field. Echo pulses remove everything except "
                  "the coupling, and waiting t = 1/(2ν) makes a controlled-phase gate. At 25 nm that takes about 0.15 ms, "
                  "so coherence limits the spacing; at 10 nm placement is the hard part."),
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["dolde2013", "dolde2014", "joas2025"], "note": SUPERCONDUCTING_NOTE},
  "gates": [_g("Controlled phase (CZ) by free evolution under echo", "demonstrated", ["dolde2013", "joas2025"]),
            _g("Optimal-control entangling gate", "demonstrated", ["dolde2014"])],
  "entanglement": [_g("Electron-electron Bell states between two NVs", "demonstrated", ["dolde2013", "dolde2014"], "Bell-state fidelity, not gate fidelity"),
                   _g("Gate fidelity measured on a 9.5 nm pair", "demonstrated", ["joas2025"], "charge state pre-selected; a different metric from Bell fidelity")],
  "use_cases": [_g("Two-qubit gate between registers", "demonstrated", ["joas2025"]),
                _g("Building block of the scalable architecture", "proposed", ["yao2012"])],
  "fom": {"bell": _fom("Bell-state fidelity", "", "higher",
                       _cur(0.824, "demonstrated", ["dolde2014"], "two NVs about 25 nm apart, optimal control, room temperature"),
                       _tgt(0.5, "Entanglement witness: above 0.5 proves entanglement (build program P5)")),
          "gate": _fom("Two-qubit gate fidelity", "", "higher",
                       _cur(0.960, "demonstrated", ["joas2025"], "9.5 nm pair, ambient conditions, charge state pre-selected", err=0.025),
                       _tgt(0.99, "ADAMAS design target (proposed); the coherence bound allows it only for r ≤ r_max")),
          "r_max": _fom("Largest spacing for a 0.99 coherence-limited gate", "nm", "higher", None,
                        _tgt(r_max_nm(), "From ν = 52 MHz nm³/r³ and T₂ = 1.8 ms [balasubramanian2009], single-spin exponential bound; the two-spin stretched-echo model (adamas.gate_budget) allows wider spacings", "adamas.qdl.r_max_nm"))},
  "route": {"variant": "qubit", "steps": ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S13", "S16", "S18", "S19"],
            "overrides": {"S06": "Two apertures 10 to 15 nm apart, or one aperture with a dose that leaves two NVs inside (adamas.coupling.pair_yield).",
                          "S18": "Find a coupled pair by double electron-electron resonance (DEER) and measure ν."},
            "extra": [], "atlas": ["M12", "M20", "M21", "M22", "M24", "M25", "M47", "M51"]},
  "layers": ["Microwave line", "Two NVs 10 to 25 nm apart", "¹²C diamond"],
  "checks": [_chk("coupler", "Coupling strong enough for a 0.99 gate", {"r_nm": 10.0}, {"r_nm": 30.0},
                  "Placement error: the pair ends up 30 nm apart", "r_max from ν = 52 MHz nm³/r³ and T₂ = 1.8 ms [balasubramanian2009]")],
  "failures": ["Pair too far apart (placement)", "One NV in the wrong charge state", "Cannot address two NVs closer than the diffraction limit"],
  "open_problems": ["Placing NVs 10 nm apart with high yield", "Addressing each NV of a close pair separately (Addressing Lab)"],
  "links": {"labs": ["labs/addressing.html", "labs/machine.html"], "chapters": ["07_nv_fabrication_and_placement.md", "08_quantum_processor_architecture.md"], "experiments": ["C2"], "loop": ["budget", "crosstalk"]}},

 {"id": "QDL-05", "name": "Spin readout (four routes)", "family": "register",
  "analogy": {"label": "sense amplifier", "fits": "It turns a tiny state difference into a signal a circuit can use.",
              "breaks": "At room temperature the electron cannot yet be read in one shot; nuclear spins can."},
  "function": "Turn the spin state into a measurable signal: photons, photocurrent, or a charge state.",
  "explanation": ("Route 1, optical: count red photons; only a fraction of a photon per shot is detected, so the electron "
                  "readout is averaged. Route 2, spin-to-charge conversion (SCC): a timed laser sequence ionizes one spin state, "
                  "and the charge state is then read with many photons. Route 3, photoelectric detection of magnetic resonance (PDMR): read the electrons the "
                  "ionization frees as a current through electrodes. Route 4, nuclear single-shot: map the nucleus onto the "
                  "electron thousands of times and add up the photons."),
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["dreau2013", "shields2015", "siyushev2019", "hopper2018"],
             "note": "Single-shot readout at room temperature is demonstrated for nuclear spins only."},
  "gates": [_g("Projective measurement of the nucleus (single shot)", "demonstrated", ["neumann2010science", "dreau2013"]),
            _g("Averaged measurement of the electron", "demonstrated", ["hopper2018"])],
  "entanglement": [_g("None made; readout verifies the entanglement of QDL-03 and QDL-04", "demonstrated", ["dolde2013"])],
  "use_cases": [_g("Register readout", "demonstrated", ["dreau2013"]),
                _g("Electrical readout for chip-scale integration", "demonstrated", ["siyushev2019", "bourgeois2015"])],
  "fom": {"nuclear_ss": _fom("Nuclear single-shot readout fidelity", "", "higher",
                             _cur(0.96, "demonstrated", ["dreau2013"], "¹³C nucleus, 120 ms per readout, room temperature", err=0.012),
                             _tgt(0.96, "Reproduce the demonstrated value (check below)", refs=["dreau2013"])),
          "scc_noise": _fom("SCC readout noise relative to the projection limit", "×", "lower",
                            _cur(2.76, "demonstrated", ["shields2015"], "room temperature; conventional optical readout 10.6× on the same NV"),
                            _tgt(1.0, "Projection-noise limit (single-shot)")),
          "contrast": _fom("Optical readout contrast after pumping", "", "higher",
                           _cur(measured_contrast(), "simulated", [], "rate model of adamas.photophysics, β = 1, 0.3 µs window", python="adamas.qdl.measured_contrast"),
                           None)},
  "route": {"variant": "qubit", "steps": ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S13", "S14", "S16", "S18", "S19"],
            "overrides": {"S14": "Photocurrent electrodes on the QELEC layer for route 3 (photoelectric).",
                          "S18": "Add the orange/red charge-readout laser (Atlas M54) for SCC and the photocurrent chain (M55)."},
            "extra": [], "atlas": ["M47", "M49", "M50", "M54", "M55", "M13"]},
  "layers": ["Photocurrent electrodes", "Al₂O₃", "NV + nucleus", "Diamond substrate"],
  "checks": [_chk("readout", "Repetitive nuclear readout reaches 0.96", {"photons_per_rep": 0.03}, {"photons_per_rep": 0.0075},
                  "Collection efficiency four times lower (no solid-immersion lens or waveguide)", "0.96 demonstrated [dreau2013]")],
  "failures": ["Nuclear spin flips during long readout", "Background light lowers contrast", "Photocurrent leakage from surface conduction"],
  "open_problems": ["Single-shot electron readout at room temperature", "Photoelectric readout of one NV among close neighbors"],
  "links": {"labs": ["labs/photon.html"], "chapters": ["08_quantum_processor_architecture.md"], "experiments": ["C1"], "loop": ["contrast"]}},

 {"id": "QDL-06", "name": "Optical reset (initialization)", "family": "register",
  "analogy": {"label": "pull-down resistor", "fits": "It drains the state to a known value every cycle.",
              "breaks": "It works by optical pumping through a metastable level, not by dissipation in a resistor, and stops short of 100 % (0.82 in the rate model)."},
  "function": "Pump the electron into mₛ = 0 with green light before every operation.",
  "explanation": ("Under green light, mₛ = ±1 crosses more often into a metastable singlet that returns mostly to mₛ = 0, so "
                  "after about a microsecond the spin sits in mₛ = 0 with high but not perfect probability. Nuclear spins are "
                  "then initialized by swapping or by repeated measurement."),
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["gruber1997", "tetienne2012", "waldherr2014"], "note": ""},
  "gates": [_g("Reset of the electron to mₛ = 0", "demonstrated", ["gruber1997"]),
            _g("Nuclear-spin initialization", "demonstrated", ["waldherr2014"])],
  "entanglement": [],
  "use_cases": [_g("Every register and sensor cycle", "demonstrated", ["gruber1997", "barry2020"])],
  "fom": {"pol": _fom("Electron polarization after pumping", "", "higher",
                      _cur(polarization(), "simulated", [], "rate model, β = 1, 3 µs (adamas.photophysics)", python="adamas.qdl.polarization"),
                      None)},
  "route": {"variant": "qubit", "steps": ["S18"], "overrides": {"S18": "Laser pulses gated by an acousto-optic modulator (M39)."},
            "extra": [], "atlas": ["M38", "M39", "M42", "M46"]},
  "layers": ["Green light in", "NV", "Diamond"],
  "checks": [_chk("polarize", "Pump reaches its steady state", {"beta": 1.0, "t_us": 3.0}, {"beta": 1.0, "t_us": 0.1},
                  "Laser pulse too short (0.1 µs)", "ADAMAS design threshold: 0.99 of the steady state")],
  "failures": ["Too much power ionizes NV⁻ to NV⁰", "Pulse too short"],
  "open_problems": ["Electron polarization stops short of 100 % (0.82 in the rate model of adamas.photophysics); repeated measurement is needed for more."],
  "links": {"labs": ["labs/photon.html"], "chapters": ["06_nv_center_physics.md"], "experiments": ["B1"], "loop": ["contrast"]}},

 {"id": "QDL-07", "name": "Charge-control electrodes", "family": "register",
  "analogy": None,
  "function": "Hold the NV in its negative charge state (NV⁻) with a gate voltage or a doped junction.",
  "explanation": ("Only NV⁻ is a qubit. Surface termination and nearby dopants set the Fermi level, and electrodes can move it. "
                  "A p-i-n junction can also pump charge."),
  "status": {"label": "reported", "temperature_k": 300, "refs": ["hauf2011", "grotz2012", "doi2014"],
             "note": "Electrical charge control is reported; holding NV⁻ near 100 % under readout light is not."},
  "gates": [], "entanglement": [],
  "use_cases": [_g("Raise the probability that both NVs of a pair start in NV⁻", "proposed", ["grotz2012"]),
                _g("Electrically driven single-photon source", "demonstrated", ["mizuochi2012"])],
  "fom": {"nv_minus": _fom("NV⁻ fraction under readout", "", "higher", _todo("NV⁻ fraction under electrical control: confirm from the paper", ["grotz2012"]),
                           _tgt(None, "As high as the gate budget needs (Machine Builder)"))},
  "route": {"variant": "qubit", "steps": ["S01", "S02", "S03", "S06", "S07", "S13", "S14", "S16", "S18"],
            "overrides": {"S14": "Gate electrodes over the NV region on the QELEC layer."},
            "extra": [{"after": "S03", "id": "X07a", "title": "p-i-n doped growth (boron and phosphorus layers)",
                       "text": "Grow p-type (boron) and n-type (phosphorus) layers around an intrinsic NV layer.", "label": "proposed",
                       "refs": ["mizuochi2012"], "atlas": ["M01"]}],
            "atlas": ["M01", "M13", "M14", "M55"]},
  "layers": ["Gate electrode", "Al₂O₃", "Intrinsic layer with NV", "p⁺ / n⁺ layers (proposed)"],
  "checks": [], "no_check": "No charge-state model in the package yet; listed in docs/STATUS.md.",
  "failures": ["Surface conduction shorts the gate", "Ionization under light outruns the electrical restore"],
  "open_problems": ["Deterministic NV⁻ preparation at room temperature."],
  "links": {"labs": ["labs/bias.html"], "chapters": ["07_nv_fabrication_and_placement.md"], "experiments": [], "loop": []}},

 {"id": "QDL-08", "name": "Microwave drive line (coplanar waveguide)", "family": "register",
  "analogy": {"label": "word line with 50 Ω termination (resistor)", "fits": "It carries the control signal to many cells and is terminated so it does not reflect.",
              "breaks": "It is a classical wire: it drives qubits but carries no quantum information (the quantum wire is QDL-10)."},
  "function": "Carry microwave pulses to the NVs as an oscillating magnetic field.",
  "explanation": ("A gold coplanar waveguide (CPW) on the diamond carries microwave current near the 2.87 GHz resonance. The current makes a "
                  "magnetic field at the NV whose strength sets the Rabi frequency. A 50 Ω termination keeps reflections from "
                  "heating the chip unevenly. It is classical: noise on it is control error, not decoherence of a quantum bus."),
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["fuchs2009", "kim2019cmos"], "note": "Classical device."},
  "gates": [_g("Delivers the single-qubit gates of QDL-01", "demonstrated", ["fuchs2009"])],
  "entanglement": [],
  "use_cases": [_g("Every pulsed experiment", "demonstrated", ["fuchs2009"])],
  "fom": {},
  "route": {"variant": "qubit", "steps": ["S13", "S14", "S15", "S16", "S19"],
            "overrides": {"S16": "METAL2 layer: CPW with ground planes, 50 Ω characteristic impedance, wire-bonded to a terminated board."},
            "extra": [], "atlas": ["M11", "M13", "M28", "M41", "M51"]},
  "layers": ["Gold CPW (signal and grounds)", "Al₂O₃", "NV layer", "Diamond"],
  "checks": [_chk("rabi", "Line delivers the designed Rabi frequency", {"rabi_mhz": 10.0}, {"rabi_mhz": 5.0},
                  "6 dB of extra loss (bad bond or mismatch) halves the field", "ADAMAS design threshold: within 5 % of the design value, including k·σ")],
  "failures": ["Heating from high power", "Reflections from a poor termination"],
  "open_problems": ["Driving one NV of a close pair without the other (frequency or gradient addressing)."],
  "links": {"labs": ["labs/qubit.html", "labs/addressing.html"], "chapters": ["09_cmos_control_integration.md"], "experiments": ["B1"], "loop": ["rabi"]}},

 {"id": "QDL-09", "name": "Optical waveguide and photon collector", "family": "register",
  "analogy": {"label": "interconnect for light", "fits": "It routes signals (photons) to where they are measured.",
              "breaks": "It only improves collection; at room temperature it does not make photons indistinguishable."},
  "function": "Collect more of the NV's red light with nanowires, solid-immersion lenses or waveguides.",
  "explanation": ("Diamond's high refractive index traps most of the light inside. Etched nanopillars, solid-immersion lenses "
                  "and waveguides guide it out, which shortens every readout. This raises the photons-per-repetition input of "
                  "the readout check (QDL-05)."),
  "status": {"label": "reported", "temperature_k": 300, "refs": ["babinec2010", "hadden2010", "riedel2017"],
             "note": "Collection gains are reported at room temperature; the exact factor for each structure is to be confirmed."},
  "gates": [], "entanglement": [],
  "use_cases": [_g("Faster readout in registers and sensors", "reported", ["babinec2010", "hadden2010"])],
  "fom": {"gain": _fom("Collection gain over bulk", "×", "higher", _todo("Photon-collection gain of diamond nanowires: confirm from the paper", ["babinec2010"]), None)},
  "route": {"variant": "qubit", "steps": ["S01", "S02", "S03", "S05", "S06", "S07", "S18"],
            "overrides": {},
            "extra": [{"after": "S07", "id": "X09a", "title": "Nanophotonic etch (nanopillars or waveguides)",
                       "text": "Electron-beam lithography of a hard mask, then oxygen inductively coupled plasma reactive-ion etching (ICP-RIE) of pillars or waveguides around the NVs.",
                       "label": "reported", "refs": ["babinec2010", "burek2012"], "atlas": ["M12", "M16"]}],
            "atlas": ["M12", "M16", "M47"]},
  "layers": ["Etched diamond nanopillar", "NV inside the pillar", "Diamond"],
  "checks": [], "no_check": "No optical (photonic) model in the package yet; its effect enters QDL-05's readout check.",
  "failures": ["Etch damage near the NV", "Surface charge in the pillar"],
  "open_problems": ["Indistinguishable photons need cryogenics (see QDL-11)."],
  "links": {"labs": ["labs/photon.html"], "chapters": ["08_quantum_processor_architecture.md"], "experiments": [], "loop": []}},

 {"id": "QDL-10", "name": "Dark-spin chain bus", "family": "link",
  "analogy": {"label": "quantum wire", "fits": "It carries quantum information from one register to another.",
              "breaks": "It is a chain of nitrogen spins, and nobody has built one yet."},
  "function": "Move a qubit between NV registers 100 nm or more apart through a chain of optically dark nitrogen spins.",
  "explanation": ("Yao and co-workers proposed chains of 5 to 20 nitrogen spins about 10 to 20 nm apart, swept by microwave "
                  "pulses, to connect NV registers that can each be addressed optically. It assumes an NV T₁ of 100 to 250 ms, "
                  "cooling to about 250 K, a donut-shaped readout beam and a field gradient."),
  "status": {"label": "proposed", "temperature_k": None, "refs": ["yao2012"], "note": "Theory; chains not yet built."},
  "gates": [_g("State transfer along the chain", "proposed", ["yao2012"])],
  "entanglement": [_g("Entanglement between distant registers", "proposed", ["yao2012"])],
  "use_cases": [_g("Wiring a room-temperature processor", "proposed", ["yao2012"])],
  "fom": {},
  "route": {"variant": "qubit", "steps": ["S01", "S02", "S03", "S06", "S07", "S18"], "overrides": {},
            "extra": [{"after": "S06", "id": "X10a", "title": "Dark-spin chain placement",
                       "text": "Implant nitrogen chains with 10 to 20 nm pitch between register sites; no known process reaches this yet.",
                       "label": "proposed", "refs": ["yao2012"], "atlas": ["M20", "M21"]}],
            "atlas": ["M20", "M21", "M22"]},
  "layers": ["Register", "N–N–N chain", "Register"],
  "checks": [], "no_check": "Theory only; no simulation in the package.",
  "failures": ["Nitrogen spins in the chain are missing or misplaced"],
  "open_problems": ["Building chains with the needed spacing", "Holding T₁ long enough"],
  "links": {"labs": ["labs/machine.html"], "chapters": ["08_quantum_processor_architecture.md"], "experiments": [], "loop": []}},

 {"id": "QDL-11", "name": "Photonic link node (cryogenic)", "family": "link",
  "analogy": None,
  "function": "Entangle distant NVs by interfering their photons.",
  "explanation": ("Two NVs each emit a photon entangled with their spin; a beam splitter and detectors herald entanglement "
                  "between them. It works only at a few kelvin, where the zero-phonon line is narrow; at room temperature only "
                  "about 3 % of the light is in that line and it is broad. It is kept in the library as the reference link."),
  "status": {"label": "cryogenic", "temperature_k": 4, "refs": ["bernien2013", "hensen2015", "pompili2021", "faraon2011"],
             "note": "Demonstrated only at cryogenic temperature (about 4 K). " + SUPERCONDUCTING_NOTE},
  "gates": [_g("Heralded remote entanglement", "cryogenic", ["bernien2013", "pompili2021"])],
  "entanglement": [_g("Spin-spin entanglement over distance", "cryogenic", ["bernien2013", "hensen2015"]),
                   _g("Three-node network", "cryogenic", ["pompili2021"])],
  "use_cases": [_g("Quantum network and repeater", "cryogenic", ["pompili2021", "hermans2022"])],
  "fom": {"zpl": _fom("Zero-phonon fraction of the emission", "", "higher",
                      _cur(0.03, "demonstrated", ["faraon2011"], "room-temperature emission; cavities raise it more than tenfold below 10 K"), None)},
  "route": {"variant": "qubit", "steps": ["S01", "S02", "S03", "S05", "S06", "S07", "S18"], "overrides": {},
            "extra": [{"after": "S07", "id": "X11a", "title": "Nanophotonic etch (cavity)", "text": "As QDL-09, with a cavity.",
                       "label": "cryogenic", "refs": ["faraon2011"], "atlas": ["M12", "M16"]}],
            "atlas": ["M47", "M49", "M50"]},
  "layers": ["Cavity", "NV", "Diamond"],
  "checks": [_chk("g2", "The link uses one emitter", {"g0": 0.2}, {"g0": 2 / 3},
                  "Three NVs in the spot instead of one", "0.5 criterion [kurtsiefer2000]")],
  "failures": ["Spectral diffusion broadens the line", "Low photon rate"],
  "open_problems": ["A room-temperature photonic interface (unsolved); see QDL-13 to QDL-16."],
  "links": {"labs": ["labs/photon.html"], "chapters": ["08_quantum_processor_architecture.md"], "experiments": ["C1"], "loop": []}},

 {"id": "QDL-12", "name": "Ensemble magnetometer", "family": "sensing",
  "analogy": None,
  "function": "Measure magnetic fields with millions of NVs at once, by the shift of their optically detected magnetic resonance (ODMR) lines.",
  "explanation": ("A field B shifts the ODMR lines by 28 MHz per mT along each NV axis. Four crystal orientations give a "
                  "vector magnetometer. It is the device that already pays: commercial sensors and teaching kits exist."),
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["barry2020", "wolf2015", "stuerner2021"], "note": ""},
  "gates": [], "entanglement": [_g("None needed (classical ensemble average)", "demonstrated", ["barry2020"])],
  "use_cases": [_g("Magnetic anomaly and current sensing", "demonstrated", ["barry2020"]),
                _g("Teaching lab (experiments A1, A2, B2)", "demonstrated", ["sewani2020"])],
  "fom": {"gamma": _fom("Line shift per field", "MHz/mT", "higher", _cur(gamma_mhz_per_mt(), "reported", ["doherty2013"], "physical constant, g = 2.0028 (adamas.nv)", python="adamas.qdl.gamma_mhz_per_mt"), None),
          "sens": _fom("Sensitivity", "T/√Hz", "lower", _todo("Ensemble sensitivity records: confirm from the paper", ["wolf2015", "barry2020"]), None)},
  "route": {"variant": "sensor", "steps": ["S01", "S02", "S06", "S07", "S18", "S19"],
            "overrides": {"S06": "High dose for an ensemble layer (traveler S06 [pezzagna2010]), or buy irradiated high-pressure high-temperature (HPHT) diamond (M31)."},
            "extra": [], "atlas": ["M30", "M31", "M32", "M33", "M34", "M35", "M36"]},
  "layers": ["Microwave antenna", "NV ensemble layer", "Diamond"],
  "checks": [_chk("detect", "The dip is detected", {"contrast": 0.012}, {"contrast": 0.0006},
                  "Contrast twenty times lower (misaligned filter lets green through)", "five-sigma convention (build program P1)")],
  "failures": ["Laser intensity noise", "Strain broadening"],
  "open_problems": ["Reaching the shot-noise limit in a small package"],
  "links": {"labs": ["labs/lattice.html"], "chapters": ["06_nv_center_physics.md"], "experiments": ["A1", "A2", "B2"], "loop": ["odmr"]}},

 # ---------------- room-temperature link options (all proposed)
 {"id": "QDL-13", "name": "Optomechanical repeater node", "family": "link", "analogy": None,
  "function": "Link registers at room temperature by converting spin states through a mechanical resonator to light.",
  "explanation": "A proposal for a room-temperature quantum repeater that uses optomechanics instead of the cryogenic zero-phonon line. On paper only.",
  "status": {"label": "proposed", "temperature_k": 300, "refs": ["ji2022"], "note": "Proposal; nothing built."},
  "gates": [_g("Heralded remote entanglement", "proposed", ["ji2022"])], "entanglement": [_g("Spin-spin over distance", "proposed", ["ji2022"])],
  "use_cases": [_g("Room-temperature quantum network", "proposed", ["ji2022"])], "fom": {},
  "route": {"variant": "qubit", "steps": ["S01", "S02", "S03", "S06", "S07"], "overrides": {},
            "extra": [{"after": "S07", "id": "X13a", "title": "Optomechanical resonator fabrication", "text": "Not specified in the traveler.",
                       "label": "proposed", "refs": ["ji2022"], "atlas": ["M12", "M16"]}], "atlas": ["M12", "M16"]},
  "layers": ["Optomechanical resonator", "NV", "Diamond"], "checks": [], "no_check": "Proposal; no model in the package.",
  "failures": ["Thermal phonons at 300 K"], "open_problems": ["Any experimental demonstration"],
  "links": {"labs": [], "chapters": ["08_quantum_processor_architecture.md"], "experiments": [], "loop": []}},

 {"id": "QDL-14", "name": "Phonon (strain) bus through a diamond nanobeam", "family": "link", "analogy": None,
  "function": "Couple distant NVs through the vibrations of a diamond beam they sit in.",
  "explanation": ("Strain changes the NV's levels, so a vibrating beam can drive the spin; this coupling is demonstrated. "
                  "Using one mechanical mode to entangle two NVs is a proposal; thermal phonons at 300 K are the obstacle."),
  "status": {"label": "proposed", "temperature_k": 300, "refs": ["rabl2010", "ovartchaiyapong2014", "teissier2014"],
             "note": "Spin-strain coupling demonstrated; spin-spin link proposed."},
  "gates": [_g("Spin driven by a mechanical mode", "demonstrated", ["ovartchaiyapong2014", "teissier2014"]),
            _g("Spin-spin gate through a phonon", "proposed", ["rabl2010"])],
  "entanglement": [_g("NV-NV via a shared mode", "proposed", ["rabl2010"])],
  "use_cases": [_g("On-chip room-temperature link", "proposed", ["rabl2010"])], "fom": {},
  "route": {"variant": "qubit", "steps": ["S01", "S02", "S03", "S05", "S06", "S07", "S18"], "overrides": {},
            "extra": [{"after": "S07", "id": "X14a", "title": "Released diamond nanobeam", "text": "Undercut etch to free a beam with NVs inside.",
                       "label": "reported", "refs": ["ovartchaiyapong2014"], "atlas": ["M12", "M16"]}], "atlas": ["M12", "M16"]},
  "layers": ["Released beam with NVs", "Gap", "Diamond"], "checks": [], "no_check": "No mechanical model in the package.",
  "failures": ["Thermal phonon occupation at 300 K"], "open_problems": ["High-Q beams and strong single-phonon coupling"],
  "links": {"labs": [], "chapters": ["08_quantum_processor_architecture.md"], "experiments": [], "loop": []}},

 {"id": "QDL-15", "name": "Ferromagnet-mediated coupler", "family": "link", "analogy": None,
  "function": "Couple NVs microns apart through spin waves in a ferromagnetic strip.",
  "explanation": "A proposal: a ferromagnet between two NVs carries their interaction as virtual spin waves, extending its range.",
  "status": {"label": "proposed", "temperature_k": 300, "refs": ["trifunovic2013"], "note": "Proposal."},
  "gates": [_g("Long-range two-qubit gate", "proposed", ["trifunovic2013"])], "entanglement": [_g("NV-NV over microns", "proposed", ["trifunovic2013"])],
  "use_cases": [_g("Wiring registers", "proposed", ["trifunovic2013"])], "fom": {},
  "route": {"variant": "qubit", "steps": ["S01", "S02", "S03", "S06", "S07", "S13"], "overrides": {},
            "extra": [{"after": "S13", "id": "X15a", "title": "Ferromagnet strip deposition", "text": "Not specified in the traveler.",
                       "label": "proposed", "refs": ["trifunovic2013"], "atlas": ["M13"]}], "atlas": ["M13"]},
  "layers": ["Ferromagnet strip", "Al₂O₃", "Two NVs", "Diamond"], "checks": [], "no_check": "Proposal; no model in the package.",
  "failures": ["Magnetic noise from the ferromagnet dephases the NVs"], "open_problems": ["Any demonstration"],
  "links": {"labs": [], "chapters": ["08_quantum_processor_architecture.md"], "experiments": [], "loop": []}},

 {"id": "QDL-16", "name": "Nuclear-spin-mediated coupler", "family": "link", "analogy": None,
  "function": "Use nuclear spins between NVs to relay their interaction.",
  "explanation": "A proposal in which nuclear spins mediate coupling between electron spins, relaxing the spacing requirement of QDL-04.",
  "status": {"label": "proposed", "temperature_k": 300, "refs": ["bermudez2011"], "note": "Proposal."},
  "gates": [_g("Nuclear-mediated two-qubit gate", "proposed", ["bermudez2011"])], "entanglement": [_g("Electron-electron through nuclei", "proposed", ["bermudez2011"])],
  "use_cases": [_g("Wiring registers", "proposed", ["bermudez2011"])], "fom": {},
  "route": {"variant": "qubit", "steps": ["S01", "S02", "S03", "S06", "S07", "S18"], "overrides": {}, "extra": [], "atlas": ["M20", "M22", "M53"]},
  "layers": ["NV", "Nuclear spins", "NV"], "checks": [], "no_check": "Proposal; no model in the package.",
  "failures": ["Random nuclear positions"], "open_problems": ["Any demonstration"],
  "links": {"labs": [], "chapters": ["08_quantum_processor_architecture.md"], "experiments": [], "loop": []}},

 # ---------------- sensing, chemistry, life sciences, navigation, communications, simulation
 {"id": "QDL-17", "name": "Scanning-probe magnetometer tip", "family": "sensing", "analogy": None,
  "function": "Image magnetic fields at the nanoscale with one NV in a diamond tip scanned over a sample.",
  "explanation": "One shallow NV at the apex of a diamond pillar on an atomic force microscope (AFM) cantilever maps stray fields of magnets, currents and superconductors.",
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["casola2018", "rondin2014"], "note": ""},
  "gates": [_g("Single-qubit sensing sequences", "demonstrated", ["degen2017"])], "entanglement": [],
  "use_cases": [_g("Condensed-matter and data-storage imaging", "demonstrated", ["casola2018"])],
  "fom": {"res": _fom("Spatial resolution", "nm", "lower", _todo("Tip spatial resolution: confirm from the paper", ["casola2018"]), None)},
  "route": {"variant": "sensor", "steps": ["S01", "S02", "S06", "S07", "S18"], "overrides": {"S06": "Shallow single NVs (2.5 keV)."},
            "extra": [{"after": "S07", "id": "X17a", "title": "Pillar tip etch and cantilever mount", "text": "Etch a pillar around the NV and attach it to a cantilever.",
                       "label": "reported", "refs": ["casola2018"], "atlas": ["M12", "M16", "M24"]}], "atlas": ["M24", "M47", "M49"]},
  "layers": ["Diamond tip with NV", "Sample surface"],
  "checks": [_chk("detect", "Single-NV dip is detected", {"contrast": 0.2, "linewidth_mhz": 2.0, "noise": 0.02}, {"contrast": 0.02, "linewidth_mhz": 2.0, "noise": 0.02},
                  "Background light swamps the single NV", "five-sigma convention (build program P1)")],
  "failures": ["Tip-sample distance drifts", "Shallow-NV coherence loss"], "open_problems": ["Coherence of NVs within 10 nm of the surface"],
  "links": {"labs": [], "chapters": ["06_nv_center_physics.md"], "experiments": ["C1"], "loop": ["odmr"]}},

 {"id": "QDL-18", "name": "Nanoscale nuclear magnetic resonance (NMR) sensor", "family": "chemistry", "analogy": None,
  "function": "Record nuclear magnetic resonance from zeptoliter to picoliter volumes on the diamond surface.",
  "explanation": "A shallow NV detects the oscillating field of nuclear spins in a sample on the surface; ensembles with synchronized readout resolve chemical shifts.",
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["staudacher2013", "mamin2013", "aslam2017", "glenn2018", "lovchinsky2016"], "note": ""},
  "gates": [_g("Dynamical-decoupling sensing sequences", "demonstrated", ["staudacher2013", "mamin2013"])], "entanglement": [],
  "use_cases": [_g("Chemistry of tiny samples", "demonstrated", ["glenn2018"]), _g("Single-protein detection", "demonstrated", ["lovchinsky2016"])],
  "fom": {"res": _fom("Spectral resolution", "Hz", "lower", _todo("Chemical-shift resolution: confirm from the paper", ["glenn2018"]), None)},
  "route": {"variant": "sensor", "steps": ["S01", "S02", "S06", "S07", "S18"], "overrides": {"S06": "Shallow NVs (2.5 keV, about 4 nm deep by adamas.coupling)."},
            "extra": [], "atlas": ["M20", "M22", "M47", "M51"]},
  "layers": ["Sample (liquid)", "Shallow NV layer", "Diamond"], "checks": [], "no_check": "No NMR model in the package yet.",
  "failures": ["Surface spins shorten coherence"], "open_problems": ["Robust shallow NVs"],
  "links": {"labs": [], "chapters": ["10_current_experiments_and_industry.md"], "experiments": [], "loop": ["echo"]}},

 {"id": "QDL-19", "name": "Quantum diamond microscope", "family": "sensing", "analogy": None,
  "function": "Image magnetic fields over millimeters with a camera looking at an NV layer.",
  "explanation": "A thin NV ensemble layer under the sample is imaged onto a camera; each pixel is a magnetometer. Used on rocks, cells and working chips.",
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["levine2019", "turner2020", "lesage2013"], "note": ""},
  "gates": [], "entanglement": [],
  "use_cases": [_g("Failure analysis of integrated circuits", "demonstrated", ["turner2020"]), _g("Imaging magnetotactic bacteria", "demonstrated", ["lesage2013"])],
  "fom": {"pix": _fom("Field sensitivity per pixel", "T/√Hz", "lower", _todo("Per-pixel sensitivity: confirm from the paper", ["levine2019"]), None)},
  "route": {"variant": "sensor", "steps": ["S01", "S02", "S06", "S07", "S18"], "overrides": {"S06": "Shallow dense ensemble layer."},
            "extra": [], "atlas": ["M20", "M22", "M38", "M43"]},
  "layers": ["Sample", "NV ensemble layer", "Diamond", "Camera optics"],
  "checks": [_chk("detect", "Per-pixel dip is detected", {"contrast": 0.012}, {"contrast": 0.0006}, "Green background reaches the camera: twenty times less contrast", "five-sigma convention (build program P1)")],
  "failures": ["Strain gradients across the field"], "open_problems": ["Sensitivity per pixel at video rate"],
  "links": {"labs": [], "chapters": ["10_current_experiments_and_industry.md"], "experiments": ["A1"], "loop": ["odmr"]}},

 {"id": "QDL-20", "name": "Diamond thermometer (bulk and nanodiamond)", "family": "life", "analogy": None,
  "function": "Measure temperature through the shift of the zero-field splitting D with temperature.",
  "explanation": "D falls by about 74 kHz per kelvin near room temperature. Nanodiamonds inside cells report local temperature.",
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["acosta2010", "kucsko2013", "toyli2013"], "note": ""},
  "gates": [], "entanglement": [],
  "use_cases": [_g("Temperature inside living cells", "demonstrated", ["kucsko2013"]), _g("Hot-spot mapping in chips", "proposed", ["turner2020"])],
  "fom": {"dddt": _fom("dD/dT", "kHz/K", "larger magnitude", _cur(-74.2, "demonstrated", ["acosta2010"], "weighted average of four samples near 300 K", err=0.7),
                       None)},
  "route": {"variant": "sensor", "steps": ["S01", "S02", "S06", "S07", "S18"], "overrides": {},
            "extra": [{"after": "S07", "id": "X20a", "title": "Nanodiamond milling and surface treatment", "text": "Mill irradiated, annealed diamond to nanodiamonds; or buy them.",
                       "label": "demonstrated", "refs": ["kucsko2013"], "atlas": ["M31"]}], "atlas": ["M31", "M37", "M44"]},
  "layers": ["Nanodiamond with NVs", "Cell or chip"],
  "checks": [_chk("thermo", "dD/dT agrees with −74.2(7) kHz/K", {"coupling": 1.0}, {"coupling": 0.8},
                  "Poor thermal contact: the diamond sees 80 % of the change", "±k combined σ around [acosta2010] (98.98 % coverage)")],
  "failures": ["Laser heating", "Strain shifts D"], "open_problems": ["Calibration in biological media"],
  "links": {"labs": ["labs/heat.html"], "chapters": ["06_nv_center_physics.md"], "experiments": ["A3"], "loop": ["odmr"]}},

 {"id": "QDL-21", "name": "Biomagnetic sensor (neuron action potentials)", "family": "life", "analogy": None,
  "function": "Detect the magnetic field of a firing nerve without touching it.",
  "explanation": "An optimized ensemble magnetometer detects action potentials of single neurons in a worm and a squid axon, non-invasively.",
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["barry2016"], "note": ""},
  "gates": [], "entanglement": [],
  "use_cases": [_g("Non-invasive neural recording", "demonstrated", ["barry2016"])],
  "fom": {"sens": _fom("Sensitivity", "T/√Hz", "lower", _todo("Biomagnetic sensitivity: confirm from the paper", ["barry2016"]), None)},
  "route": {"variant": "sensor", "steps": ["S01", "S02", "S06", "S07", "S18", "S19"], "overrides": {}, "extra": [], "atlas": ["M38", "M40", "M58"]},
  "layers": ["Tissue", "NV ensemble", "Diamond"],
  "checks": [_chk("detect", "Signal is detected", {"contrast": 0.012}, {"contrast": 0.0006}, "Twenty times less contrast (stray light)", "five-sigma convention (build program P1)")],
  "failures": ["Laser heating of tissue", "Ambient magnetic noise"], "open_problems": ["Sensitivity for human-scale magnetoencephalography"],
  "links": {"labs": [], "chapters": ["10_current_experiments_and_industry.md"], "experiments": [], "loop": ["odmr"]}},

 {"id": "QDL-22", "name": "Optical hyperpolarizer", "family": "life", "analogy": None,
  "function": "Transfer the NV's optical spin polarization to ¹³C nuclei to boost magnetic resonance signals.",
  "explanation": "Green light polarizes the NV; microwaves or level crossings pass that polarization to nuclear spins, in crystals and powders, at room temperature.",
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["london2013", "king2015", "ajoy2018"], "note": ""},
  "gates": [_g("Polarization transfer (electron to nuclei)", "demonstrated", ["london2013"])], "entanglement": [],
  "use_cases": [_g("Brighter agents for magnetic resonance imaging (MRI) and NMR", "proposed", ["ajoy2018"])],
  "fom": {"gain": _fom("Signal enhancement over thermal", "×", "higher", _todo("Hyperpolarization enhancement: confirm from the paper", ["king2015"]), None)},
  "route": {"variant": "sensor", "steps": ["S01", "S02", "S06", "S07", "S18"], "overrides": {}, "extra": [], "atlas": ["M31", "M38", "M53"]},
  "layers": ["¹³C nuclei", "NV", "Diamond powder or crystal"], "checks": [], "no_check": "No polarization-transfer model in the package.",
  "failures": ["Spin diffusion barrier near the NV"], "open_problems": ["Transferring polarization to molecules outside the diamond"],
  "links": {"labs": [], "chapters": ["10_current_experiments_and_industry.md"], "experiments": [], "loop": []}},

 {"id": "QDL-23", "name": "Diamond gyroscope", "family": "navigation", "analogy": None,
  "function": "Sense rotation through the geometric phase of NV or ¹⁴N nuclear spins.",
  "explanation": "Proposals use the nuclear spin as a rotation sensor, for navigation without satellite positioning (GPS) together with the magnetometer.",
  "status": {"label": "proposed", "temperature_k": 300, "refs": ["ledbetter2012", "ajoy2012"], "note": "Proposal."},
  "gates": [_g("Nuclear Ramsey sequence", "proposed", ["ledbetter2012"])], "entanglement": [],
  "use_cases": [_g("Navigation without GPS", "proposed", ["ledbetter2012"])], "fom": {},
  "route": {"variant": "sensor", "steps": ["S01", "S02", "S06", "S07", "S18", "S19"], "overrides": {}, "extra": [], "atlas": ["M53", "M59"]},
  "layers": ["NV ensemble with ¹⁴N", "Diamond"], "checks": [], "no_check": "Proposal; no model in the package.",
  "failures": ["Magnetic field drift mimics rotation"], "open_problems": ["Competitive bias stability"],
  "links": {"labs": ["labs/globe.html"], "chapters": ["11_proposed_experiments_and_roadmap.md"], "experiments": [], "loop": []}},

 {"id": "QDL-24", "name": "Electric-field and stress sensor", "family": "chemistry", "analogy": None,
  "function": "Measure electric fields and stress through the NV's strain and Stark shifts.",
  "explanation": "The NV levels respond to electric fields and stress; NVs in a diamond-anvil cell image stress and magnetism at megabar pressure.",
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["dolde2011", "hsieh2019"], "note": ""},
  "gates": [], "entanglement": [],
  "use_cases": [_g("Electric-field sensing with a single NV", "demonstrated", ["dolde2011"]), _g("Materials at megabar pressure", "demonstrated", ["hsieh2019"])],
  "fom": {"e": _fom("Electric-field sensitivity", "V/cm/√Hz", "lower", _todo("Electric-field sensitivity: confirm from the paper", ["dolde2011"]), None)},
  "route": {"variant": "sensor", "steps": ["S01", "S02", "S06", "S07", "S18"], "overrides": {"S06": "Shallow NV layer in an anvil culet for pressure work."},
            "extra": [], "atlas": ["M20", "M22", "M47"]},
  "layers": ["Sample under pressure", "NV layer in the anvil", "Diamond anvil"], "checks": [], "no_check": "No Stark or stress model in the package beyond adamas.nv strain.",
  "failures": ["Field and strain mix in the signal"], "open_problems": ["Separating electric and strain contributions"],
  "links": {"labs": ["labs/lattice.html"], "chapters": ["06_nv_center_physics.md"], "experiments": [], "loop": []}},

 {"id": "QDL-25", "name": "Room-temperature maser", "family": "comms", "analogy": None,
  "function": "Amplify or emit microwaves near 9 GHz with optically pumped NVs in a cavity.",
  "explanation": "Optical pumping inverts the NV population; in a high-Q microwave cavity this gives continuous-wave maser action without cryogenics.",
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["breeze2018"], "note": ""},
  "gates": [], "entanglement": [],
  "use_cases": [_g("Low-noise microwave amplifier", "proposed", ["breeze2018"]), _g("Maser-assisted ensemble readout (ADAMAS idea)", "proposed", ["breeze2018"])],
  "fom": {"f": _fom("Operating frequency (about)", "GHz", "set by design", _cur(9, "demonstrated", ["breeze2018"], "continuous wave, room temperature, in a cavity"), None)},
  "route": {"variant": "sensor", "steps": ["S01", "S06", "S07"], "overrides": {"S06": "High-density NV ensemble (or irradiated HPHT)."},
            "extra": [{"after": "S07", "id": "X25a", "title": "Cavity assembly (sapphire or dielectric resonator)", "text": "Mount the diamond in a high-Q microwave cavity with a magnet.",
                       "label": "demonstrated", "refs": ["breeze2018"], "atlas": ["M28"]}], "atlas": ["M31", "M38", "M43"]},
  "layers": ["Microwave cavity", "NV-rich diamond", "Pump laser"], "checks": [], "no_check": "No maser model in the package.",
  "failures": ["Pump heating"], "open_problems": ["Compact pumping"],
  "links": {"labs": [], "chapters": ["10_current_experiments_and_industry.md"], "experiments": [], "loop": []}},

 {"id": "QDL-26", "name": "Many-body quantum simulator (dense ensemble)", "family": "simulation", "analogy": None,
  "function": "Study interacting spin physics with dense NV ensembles whose dipolar coupling is strong.",
  "explanation": "Dense NV ensembles show discrete time-crystalline order and emergent hydrodynamics at room temperature. A surface-spin simulator is proposed.",
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["choi2017", "zu2021"], "note": "The surface-spin version is proposed [cai2013]."},
  "gates": [_g("Global Floquet driving of the ensemble", "demonstrated", ["choi2017"])],
  "entanglement": [_g("Many-body correlations (not individually addressed)", "demonstrated", ["choi2017", "zu2021"]),
                   _g("Patterned surface-spin lattice", "proposed", ["cai2013"])],
  "use_cases": [_g("Time crystals and hydrodynamics", "demonstrated", ["choi2017", "zu2021"])], "fom": {},
  "route": {"variant": "sensor", "steps": ["S01", "S02", "S06", "S07", "S18"], "overrides": {"S06": "High dose for a dense ensemble."}, "extra": [], "atlas": ["M20", "M22", "M51"]},
  "layers": ["Dense NV ensemble", "Diamond"], "checks": [], "no_check": "No many-body model in the package.",
  "failures": ["Disorder from P1 centers"], "open_problems": ["Single-site control"],
  "links": {"labs": [], "chapters": ["11_proposed_experiments_and_roadmap.md"], "experiments": [], "loop": []}},

 # ---------------- design and integration
 {"id": "QDL-27", "name": "CMOS control and readout chiplet", "family": "design", "analogy": None,
  "function": "Generate the microwaves and read the photons or photocurrent with a silicon chip bonded to the diamond.",
  "explanation": "Silicon CMOS can synthesize the microwave drive, filter the green light and detect red photons on one chip; diamond chiplets bonded on CMOS are demonstrated.",
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["kim2019cmos", "ibrahim2021"], "note": ""},
  "gates": [_g("On-chip microwave drive and optical detection for continuous-wave ODMR", "demonstrated", ["kim2019cmos"]), _g("Pulsed single-qubit gates from the chiplet", "proposed", ["ibrahim2021"])], "entanglement": [],
  "use_cases": [_g("Chip-scale magnetometer", "demonstrated", ["kim2019cmos", "ibrahim2021"]), _g("Control plane for a register (build program P6)", "proposed", ["ibrahim2021"])],
  "fom": {},
  "route": {"variant": "qubit", "steps": ["S19"], "overrides": {"S19": "Flip-chip or wire-bond the diamond onto the CMOS die."},
            "extra": [{"after": "S19", "id": "X27a", "title": "CMOS die from a multi-project wafer (MPW) shuttle", "text": "Design with open tools (M00) and order a shuttle.",
                       "label": "demonstrated", "refs": ["kim2019cmos"], "atlas": ["M00", "M29"]}], "atlas": ["M00", "M26", "M29"]},
  "layers": ["Diamond chiplet", "Bond", "CMOS die (synthesizer, photodiode, filter)"],
  "checks": [_chk("rabi", "On-chip driver delivers the design Rabi frequency", {"rabi_mhz": 10.0}, {"rabi_mhz": 5.0},
                  "Driver gives half the current", "ADAMAS design threshold: within 5 % of the design value, including k·σ")],
  "failures": ["Heating from the driver near the diamond", "Green light leaking through the filter"], "open_problems": ["Driving many qubits independently"],
  "links": {"labs": ["labs/stack.html"], "chapters": ["09_cmos_control_integration.md"], "experiments": [], "loop": ["rabi"]}},

 {"id": "QDL-28", "name": "Packaged sensor module", "family": "design", "analogy": None,
  "function": "Put the diamond, light source, filter, detector and antenna in one portable package.",
  "explanation": "Compact and portable NV magnetometers are built and sold; the A1 kit is the teaching version.",
  "status": {"label": "demonstrated", "temperature_k": 300, "refs": ["stuerner2021", "webb2019"], "note": ""},
  "gates": [], "entanglement": [],
  "use_cases": [_g("Field magnetometry", "demonstrated", ["stuerner2021"]), _g("Teaching", "demonstrated", ["sewani2020"])],
  "fom": {},
  "route": {"variant": "sensor", "steps": ["S19"], "overrides": {"S19": "Assemble diamond, LED or laser, filter, photodiode and loop antenna."},
            "extra": [], "atlas": ["M30", "M31", "M32", "M33", "M34", "M35", "M36"]},
  "layers": ["Housing", "Antenna", "Diamond", "Filter and photodiode"],
  "checks": [_chk("detect", "The module sees the dip", {"contrast": 0.012}, {"contrast": 0.0006}, "Filter misaligned: twenty times less contrast", "five-sigma convention (build program P1)")],
  "failures": ["Laser or LED drift"], "open_problems": ["Power and size for field use"],
  "links": {"labs": [], "chapters": ["10_current_experiments_and_industry.md"], "experiments": ["A1"], "loop": ["odmr"]}},
]
BY_ID = {d["id"]: d for d in DEVICES}


# --------------------------------------------------------------------------------------------------- evaluation
def run_check(dev_id: str, index: int = 0, degraded: bool = False, seed: int | None = None) -> dict:
    """Run check `index` of a device; seed None uses the check's documented seed."""
    c = BY_ID[dev_id]["checks"][index]
    return CHECKS[c["kind"]](seed=c["seed"] if seed is None else seed, **(c["degraded"] if degraded else c["nominal"]))


def pass_rate(dev_id: str, index: int = 0, runs: int = 200, degraded: bool = False) -> float:
    """Fraction of independent seeds (1000 + k) on which the check passes."""
    return sum(run_check(dev_id, index, degraded, 1000 + k)["pass"] for k in range(runs)) / runs


def build_process(dev: dict) -> list[dict]:
    """The device's physical build, in order: traveler steps (with this device's overrides) and steps the traveler
    does not have yet (marked missing)."""
    from .traveler import STEPS
    steps = {s["id"]: s for s in STEPS}
    out = []
    extras = {}
    for x in dev["route"].get("extra", []):
        extras.setdefault(x["after"], []).append(x)
    for sid in dev["route"]["steps"]:
        s = steps[sid]
        out.append({"id": sid, "title": s["title"], "t_max_c": s["t_max_c"], "text": dev["route"]["overrides"].get(sid, s["why"]),
                    "safety": s.get("safety", []), "missing": False, "label": "traveler"})
        for x in extras.pop(sid, []):
            out.append({"id": x["id"], "title": x["title"], "t_max_c": None, "text": x["text"], "safety": [], "missing": True, "label": x["label"], "refs": x["refs"], "atlas": x["atlas"]})
    for xs in extras.values():
        for x in xs:
            out.append({"id": x["id"], "title": x["title"], "t_max_c": None, "text": x["text"], "safety": [], "missing": True, "label": x["label"], "refs": x["refs"], "atlas": x["atlas"]})
    return out


def missing_steps() -> list[tuple[str, str, str]]:
    """(device, step id, title) for every build step the traveler does not have yet."""
    return [(d["id"], x["id"], x["title"]) for d in DEVICES for x in d["route"].get("extra", [])]


def open_numbers() -> list[tuple[str, str, str]]:
    """(device, figure of merit, what to confirm) for every current value not yet confirmed from its paper."""
    return [(d["id"], f["name"], f["current"]["todo"]) for d in DEVICES for f in d["fom"].values() if f["current"] and f["current"].get("todo")]


def refs_used() -> set[str]:
    keys = set()
    for d in DEVICES:
        keys |= set(d["status"]["refs"])
        for g in d["gates"] + d["entanglement"] + d["use_cases"]:
            keys |= set(g["refs"])
        for f in d["fom"].values():
            for part in ("current", "target"):
                if f[part]:
                    keys |= set(f[part].get("refs", []))
        for x in d["route"].get("extra", []):
            keys |= set(x["refs"])
    return keys | {"krinner2019", "balasubramanian2009", "kurtsiefer2000", "acosta2010", "dreau2013"}


@functools.lru_cache(maxsize=None)
def _results() -> dict:
    return {d["id"]: [{"nominal": run_check(d["id"], i), "degraded": run_check(d["id"], i, True)} for i in range(len(d["checks"]))] for d in DEVICES}


def to_json() -> dict:
    """For the website (site.json["qdl"]): devices, check results at seed 0, build processes, and Atlas names."""
    from .atlas import ATLAS
    devs = []
    for d in DEVICES:
        e = {k: v for k, v in d.items()}
        e["build"] = build_process(d)
        e["results"] = copy.deepcopy(_results()[d["id"]])
        e["atlas_names"] = {a: ATLAS[a][0] for a in d["route"]["atlas"]}
        devs.append(e)
    return {"devices": devs, "statuses": STATUS_TEXT, "families": FAMILIES, "superconducting": SUPERCONDUCTING_NOTE,
            "dipolar_mhz_nm3": _dip(), "t2_room_ms": T2_ROOM_MS, "r_max_nm": r_max_nm()}


def _dip() -> float:
    from .coupling import DIPOLAR_MHZ_NM3
    return float(DIPOLAR_MHZ_NM3)


def golden() -> dict:
    """Python values the browser's live coupler panel must reproduce (web/tests/qdl.test.mjs, relative 1e-9)."""
    from .coupling import dipolar_coupling_khz, gate_fidelity_bound, gate_time_us
    rows = [[r, float(dipolar_coupling_khz(r)), float(gate_time_us(r)), float(gate_fidelity_bound(r, T2_ROOM_MS))] for r in (5.0, 9.5, 10.0, 15.0, 25.0, 40.0)]
    return {"dipolar_mhz_nm3": _dip(), "t2_ms": T2_ROOM_MS, "rows": rows, "r_max_099": r_max_nm(0.99), "r_max_09": r_max_nm(0.9)}


# --------------------------------------------------------------------------------------------------------- documents
GEN = "_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._"
RUNS = 200


def _fmt(v, unit=""):
    if v is None:
        return "—"
    if isinstance(v, float) and (abs(v) >= 1e4 or (0 < abs(v) < 1e-3)):
        s = f"{v:.3g}"
    elif isinstance(v, float):
        s = f"{v:.4g}"
    else:
        s = str(v)
    return f"{s} {unit}".strip()


def _refs(keys) -> str:
    return " ".join(f"[{k}]" for k in keys)


def _device_md(d: dict, rates: dict) -> str:
    st = d["status"]
    L = [f"# {d['id']} {d['name']}", "", GEN, "",
         f"**Status: {st['label']}** ({STATUS_TEXT[st['label']]}). " + (f"Operating temperature: about {st['temperature_k']} K. " if st["temperature_k"] else "") + _refs(st["refs"]),
         ""]
    if st.get("note"):
        L += [st["note"], ""]
    if d["analogy"]:
        a = d["analogy"]
        L += [f"**Analogy only:** a {a['label']} (analogy) — the real device is the {d['name']}. Fits: {a['fits']} Breaks: {a['breaks']}", ""]
    L += ["## What it should do", "", d["function"], "", d["explanation"], ""]
    for title, rows in (("Gates it can hold", d["gates"]), ("Entanglement", d["entanglement"]), ("Use cases", d["use_cases"])):
        L += [f"## {title}", ""]
        if not rows:
            L += ["None.", ""]
            continue
        L += ["| What | Label | Sources | Note |", "|---|---|---|---|"]
        L += [f"| {g['name']} | {g['label']} | {_refs(g['refs'])} | {g.get('note', '')} |" for g in rows]
        L += [""]
    L += ["## Figures of merit (current versus target)", ""]
    if d["fom"]:
        L += ["| Figure of merit | Current | Label and conditions | Target | Basis |", "|---|---|---|---|---|"]
        for f in d["fom"].values():
            c, t = f["current"], f["target"]
            if c is None:
                cur, lab = "—", ""
            elif c.get("todo"):
                cur, lab = "to confirm", f"{c['todo']} {_refs(c['refs'])}"
            else:
                cur = (c.get("bound") or "") + _fmt(c["value"], f["unit"]) + (f" ± {_fmt(c['err'])}" if c.get("err") else "")
                lab = f"{c['label']}: {c['conditions']} {_refs(c['refs'])}".strip()
            tv = "—" if not t or t["value"] is None else _fmt(t["value"], f["unit"])
            tb = "" if not t else t["basis"] + (f" (`{t['python']}`)" if t.get("python") else "") + (" " + _refs(t["refs"]) if t.get("refs") else "")
            L.append(f"| {f['name']} | {cur} | {lab} | {tv} | {tb} |")
        L += [""]
    else:
        L += ["None quantified yet.", ""]
    L += ["## How to build it", "", f"Traveler variant: `{d['route']['variant']}` (docs/process/TRAVELER.md). Steps marked **missing** are not in the traveler yet (docs/STATUS.md).", "",
          "| Step | What | Max °C | Notes |", "|---|---|---|---|"]
    for s in build_process(d):
        note = ("**missing** (" + s["label"] + ") " + _refs(s.get("refs", []))) if s["missing"] else ("Safety: " + " ".join(s["safety"]) if s["safety"] else "")
        L.append(f"| {s['id']} | **{s['title']}.** {s['text']} | {s['t_max_c'] if s['t_max_c'] is not None else '—'} | {note} |")
    L += ["", "Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.", ""]
    from .atlas import ATLAS
    L += ["Machines (Atlas): " + "; ".join(f"{a} {ATLAS[a][0]}" for a in d["route"]["atlas"]), ""]
    L += ["## Pass/fail checks (simulated)", ""]
    if d["checks"]:
        L += ["| Check | Nominal (documented seed) | Degraded twin | Fault | Threshold source | Pass rate |", "|---|---|---|---|---|---|"]
        for i, c in enumerate(d["checks"]):
            r = _results()[d["id"]][i]; p = rates[(d["id"], i)]
            se = math.sqrt(max(p * (1 - p), 1e-12) / RUNS)
            L.append(f"| {c['title']}: {r['nominal']['what']} | {_fmt(r['nominal']['value'], r['nominal']['unit'])}, **{'pass' if r['nominal']['pass'] else 'FAIL'}** | "
                     f"{_fmt(r['degraded']['value'], r['degraded']['unit'])}, **{'pass' if r['degraded']['pass'] else 'fail'}** | {c['fault']} | {c['threshold_src']} | {p:.2f} ± {se:.2f} ({RUNS} seeds) |")
        L += [""]
    else:
        L += [d.get("no_check", ""), ""]
    L += ["## Failure modes", ""] + [f"- {x}" for x in d["failures"]] + ["", "## Open problems", ""] + [f"- {x}" for x in d["open_problems"]] + [""]
    lk = d["links"]
    L += ["## Links", "", "Labs: " + (", ".join(lk["labs"]) or "—") + ". Chapters: " + (", ".join(f"[{c}](../{c})" for c in lk["chapters"]) or "—") +
          ". Experiments: " + (", ".join(lk["experiments"]) or "—") + ". Equation panels: " + (", ".join(lk["loop"]) or "—") + ".", ""]
    return "\n".join(L)


def _index_md(rates: dict) -> str:
    L = ["# Quantum Device Library", "", GEN, "",
         "The room-temperature diamond devices ADAMAS describes, with what each should do, the gates and entanglement it can hold, "
         "its use cases, its figures of merit with sources, and its build route on the process traveler. Analogies to silicon parts "
         "(transistor, memory cell, resistor) are analogies only and always appear next to the real name.", "",
         SUPERCONDUCTING_NOTE, "", "Bell-state fidelity and gate fidelity are different metrics; they sit in different columns and are not ranked against each other.", "",
         "## Status labels", ""] + [f"- **{k}**: {v}" for k, v in STATUS_TEXT.items()] + [""]
    for fam, title in FAMILIES.items():
        rows = [d for d in DEVICES if d["family"] == fam]
        if not rows:
            continue
        L += [f"## {title}", "", "| Device | Status | What it does | Checks |", "|---|---|---|---|"]
        for d in rows:
            ch = ", ".join(("pass" if _results()[d["id"]][i]["nominal"]["pass"] else "FAIL") + f" ({rates[(d['id'], i)]:.2f})" for i in range(len(d["checks"]))) or "—"
            L.append(f"| [{d['id']} {d['name']}]({d['id']}.md) | {d['status']['label']} | {d['function']} | {ch} |")
        L += [""]
    L += ["## Build steps the traveler does not have yet", "", "| Device | Step | Title |", "|---|---|---|"] + [f"| {a} | {b} | {c} |" for a, b, c in missing_steps()] + [""]
    L += ["## Numbers to confirm from the papers", "", "| Device | Figure of merit | To confirm |", "|---|---|---|"] + [f"| {a} | {b} | {c} |" for a, b, c in open_numbers()] + [""]
    L += ["## How pass/fail is computed", "",
          "Each check simulates a measurement with a fixed seed, analyzes it with adamas.fitting where a fit applies, and compares it with a sourced threshold "
          "or an ADAMAS design threshold stated as such. Each has a degraded twin with one physical fault, which must fail. The pass rate column is the "
          f"fraction of {RUNS} independent seeds on which the nominal check passes.", ""]
    return "\n".join(L)


@functools.lru_cache(maxsize=None)
def _rates() -> dict:
    return {(d["id"], i): pass_rate(d["id"], i, RUNS) for d in DEVICES for i in range(len(d["checks"]))}


def documents() -> dict[str, str]:
    r = _rates()
    out = {"README.md": _index_md(r)}
    out.update({f"{d['id']}.md": _device_md(d, r) for d in DEVICES})
    return out


def write(folder: str = "docs/devices") -> list[str]:
    d = ROOT / folder; d.mkdir(parents=True, exist_ok=True)
    out = []
    for name, text in documents().items():
        (d / name).write_text(text, encoding="utf-8"); out.append(str(d / name))
    g = ROOT / "web" / "tests" / "qdl_golden.json"
    g.write_text(json.dumps(golden(), indent=1) + "\n", encoding="utf-8"); out.append(str(g))
    return out
