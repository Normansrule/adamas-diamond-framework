"""Build program P0 to P8: the ladder from a laptop to a pilot line (docs/phase0/BUILD_PROGRAM_OUTLINE.md).

Every phase uses one template: goal, physics and equations (with assumptions and validity), machines (Atlas IDs),
budget, facility, procedure, expected results simulated by this package, pass/fail metrics, failure modes, sources,
and the decision gate. Phases P0 and P1 are written in full here, and their gates are evaluated by code:

* P0 Simulation passes when every model reproduces its calibration point within its stated tolerance. The verdict is
  computed from the validation matrix (adamas.validation), so it changes when a check changes.
* P1 Proof of concept is the A1 kit used as a magnetometer and a thermometer. Its expected results are simulated with
  the A1 noise model of adamas.experiments (contrast 1.2 %, line width 6 MHz, noise 0.12 % per point; illustrative
  kit values, not a measurement), and fitted with the same code a student uses on real data (adamas.fitting). The
  pass/fail tolerances come from those fits and from the published uncertainty of dD/dT, -74.2(7) kHz/K
  [acosta2010], not from a typed-in number.

* P2 Teaching lab, P3 Single NV, P4 Devices, P5 Placement, P6 Integration and P7 Pilot line are written in full too; their tests are set so a correct
  setup passes the whole gate 95 % of the time, and P3 to P7 run each test on a degraded twin (one physical or process
  fault) that must fail.

P8 Frontier is written as an evidence ledger: its claims and readiness levels are checked by deterministic rules in code,
each tested on inflated-claim twins (docs/STATUS.md lists what is not sourced).
"""
from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

PHASES = [
    {"id": "P0", "name": "Simulation", "budget": "US$0", "status": "written",
     "goal": "Every later step is runnable in the app and calibrated against published data.",
     "metric": "Every model reproduces its calibration point within its stated tolerance (validation matrix).",
     "gate": "Do the models agree with published data well enough to plan hardware?"},
    {"id": "P1", "name": "Proof of concept", "budget": "computed from the A1, A2, and A3 part lists", "status": "written",
     "goal": "An ensemble ODMR magnetometer and thermometer from the A1 kit.",
     "metric": "Dip found near 2870 MHz; splitting follows the dipole law; dD/dT agrees with -74.2(7) kHz/K within the combined uncertainty.",
     "gate": "Is the signal-to-noise good enough to move to pulsed control?"},
    {"id": "P2", "name": "Teaching lab", "budget": "computed from the B1, B2, and B3 part lists", "status": "written",
     "goal": "Pulsed control (Rabi, Ramsey, echo), vector magnetometry, boron activation energy.",
     "metric": "Rabi frequency, T2*, T2, |B|, and E_A each recover the simulated value within the fit's uncertainty; echo outlives T2* by a large factor.",
     "gate": "Can we hold a spin coherent and measure deep dopants reliably?"},
    {"id": "P3", "name": "Single NV", "budget": "computed from the C1 part list", "status": "written",
     "goal": "Confocal microscope, antibunching, single-spin control, nuclear-spin register.",
     "metric": "g2(0) + k sigma < 0.5; three hyperfine lines spaced by 2.147 MHz; full nuclear-spin Rabi transfer; each degraded twin fails.", "gate": "Do we have single, addressable registers?"},
    {"id": "P4", "name": "Devices", "budget": "computed from the C2 part list", "status": "written",
     "goal": "Hydrogen-terminated FETs with Al2O3: contact resistance, threshold matching, mobility and threshold on the PDK-0 monitor die (breakdown and hot tests are not simulated yet).",
     "metric": "Contact resistance (TLM) at most 10 ohm mm; threshold spread within 200 mV; mobility and threshold match the PDK-0 model; each degraded twin fails.", "gate": "Do our devices match the models, run to run?"},
    {"id": "P5", "name": "Placement", "budget": "shared facility", "status": "written",
     "goal": "Implant through masks, anneal, conversion statistics, NV pairs closer than 30 nm.",
     "metric": "Conversion yield measured; coupled pairs found; Bell fidelity above 0.5.", "gate": "Is placement yield good enough to plan arrays?"},
    {"id": "P6", "name": "Integration", "budget": "packaging line or MPW partner", "status": "written",
     "goal": "Diamond chiplets bonded to silicon CMOS control; multi-cell arrays.",
     "metric": "T₂ kept through bonding (ratio at least 0.8); on-chip Rabi within 5 % of design; repetition-code gain above zero.", "gate": "Does integration keep coherence and yield?"},
    {"id": "P7", "name": "Pilot line and products", "budget": "fab", "status": "written",
     "goal": "Wafer-scale flow, statistical process control, first products.",
     "metric": "Process in statistical control on a monitor-die chart; yield explained by counted killer defects.", "gate": "Which product line pays for the line?"},
    {"id": "P8", "name": "Frontier and humanity", "budget": "application-specific", "status": "written",
     "goal": "Grid and EV efficiency, space electronics, medical magnetometry, navigation.",
     "metric": "Evidence ledger: each claim and readiness level passes rules checked by code.", "gate": "Where does diamond beat the incumbent, with evidence?"},
]

DDDT_KHZ_K, DDDT_SIGMA = -74.2, 0.7          # weighted average over four samples near 300 K [acosta2010]


# ---------------------------------------------------------------- P0 ------------------------------------------------
def p0_gate() -> dict:
    """The P0 gate, evaluated from the validation matrix: pass if no check fails; known discrepancies are listed."""
    from . import validation
    rows = validation.rows()
    known = [r for r in rows if r.status == "known discrepancy"]
    n_fail = sum(r.status == "FAIL" for r in rows)
    return {"checks": len(rows), "pass": sum(r.status == "pass" for r in rows), "fail": n_fail, "known": len(known),
            "known_checks": [r.check for r in known], "kinds": {k: sum(r.kind == k for r in rows) for k in ("literature", "cross-tool", "analytic")},
            "verdict": "go" if n_fail == 0 else "stop"}


# ---------------------------------------------------------------- P1 ------------------------------------------------
A1_NOISE = 0.0012            # per point, on a normalized baseline (adamas.experiments, odmr_ensemble)
A1_CONTRAST = 0.012
A1_LINEWIDTH = 6.0           # MHz, full width at half maximum


def p1_thermometer(temps_c=(20.0, 27.5, 35.0, 42.5, 50.0), seed: int = 11) -> dict:
    """Simulated dD/dT run of the A1 kit: zero-field spectra at five plate temperatures, each fitted with
    adamas.fitting.fit_odmr; a weighted straight line through the centers gives the slope and its standard error.
    The model shifts D linearly, D(T) = 2870 MHz + dD/dT (T - 300 K) (adamas.nv). The slope was measured between 280 and
    330 K [acosta2010], so the run stays inside that range (293 to 323 K, room temperature and up, so a heater is enough); over wider ranges D(T) is not linear [toyli2012]."""
    from . import fitting, nv
    r = np.random.default_rng(seed)
    f = np.arange(2840.0, 2900.0 + 1e-9, 0.25)
    t_k = np.array(temps_c) + 273.15
    centers, errs = [], []
    for t in t_k:
        shift = nv.zero_field_splitting_mhz(t) - nv.zero_field_splitting_mhz(300.0)      # the spectrum moves rigidly with D
        y = nv.odmr_spectrum(f - shift, np.zeros(3), contrast=A1_CONTRAST, linewidth_mhz=A1_LINEWIDTH, hyperfine=False) + r.normal(0, A1_NOISE, f.size)
        fit = fitting.fit_odmr(f, y, max_lines=1)
        centers.append(fit.params["center1"]); errs.append(fit.errors["center1"])
    c, e = np.array(centers), np.array(errs)
    w = 1 / e ** 2
    X = np.vstack([np.ones_like(t_k), t_k - t_k.mean()]).T
    cov = np.linalg.inv(X.T @ (w[:, None] * X))
    beta = cov @ X.T @ (w * c)
    slope_khz, slope_err_khz = beta[1] * 1e3, math.sqrt(cov[1, 1]) * 1e3
    combined = math.hypot(slope_err_khz, DDDT_SIGMA)
    return {"temps_c": list(temps_c), "centers_mhz": c.tolist(), "center_errs_mhz": e.tolist(),
            "slope_khz_k": float(slope_khz), "slope_err_khz_k": float(slope_err_khz), "reference_khz_k": DDDT_KHZ_K,
            "tolerance_khz_k": 2 * combined, "pass": bool(abs(slope_khz - DDDT_KHZ_K) <= 2 * combined)}


def p1_magnetometer() -> dict:
    """A2 run (adamas.experiments, 5 % noise per point): the log-log slope of splitting versus distance with its
    standard error; pass when -3 lies within two standard errors."""
    from . import experiments
    d = experiments.expected("magnet_distance")
    x, y = np.log(np.array(d["x"])), np.log(np.array(d["series"]["measured"]))
    p, cov = np.polyfit(x, y, 1, cov=True)
    se = math.sqrt(cov[0, 0])
    return {"slope": float(p[0]), "slope_err": float(se), "pass": bool(abs(p[0] + 3) <= 2 * se)}


def p1_detection(seed: int = 5) -> dict:
    """Is the zero-field dip detected, and how strongly? Signal-to-noise = fitted depth / its standard error (this
    project's criterion: at least 5, the usual five-sigma detection convention)."""
    from . import fitting, nv
    r = np.random.default_rng(seed)
    f = np.arange(2790.0, 2950.0 + 1e-9, 0.5)
    y = nv.odmr_spectrum(f, np.zeros(3), contrast=A1_CONTRAST, linewidth_mhz=A1_LINEWIDTH, hyperfine=False) + r.normal(0, A1_NOISE, f.size)
    fit = fitting.fit_odmr(f, y, max_lines=1)
    snr = fit.params["depth1"] / fit.errors["depth1"]
    return {"center_mhz": fit.params["center1"], "center_err_mhz": fit.errors["center1"], "snr": float(snr),
            "pass": bool(snr >= 5 and abs(fit.params["center1"] - 2870.0) < A1_LINEWIDTH / 2)}


def p1_bill() -> dict:
    """Parts and price range for P1: A1 plus A2 plus the heater and temperature sensor of A3 (approximate 2026 street
    prices from adamas.experiments; estimates, not quotes)."""
    from .experiments import EXPERIMENTS
    by = {e["id"]: e for e in EXPERIMENTS}
    rows = [("A1", *p) for p in by["A1"]["parts"]] + [("A2", *p) for p in by["A2"]["parts"]] + \
           [("A3", *p) for p in by["A3"]["parts"] if p[0] in ("Heater", "Temperature sensors")]
    lo = sum(r[3] for r in rows); hi = sum(r[4] for r in rows)
    return {"rows": rows, "low": lo, "high": hi}


def p1_gate() -> dict:
    det, mag, th = p1_detection(), p1_magnetometer(), p1_thermometer()
    ok = det["pass"] and mag["pass"] and th["pass"]
    return {"detection": det, "magnetometer": mag, "thermometer": th, "verdict": "go" if ok else "stop"}


def p1_pass_rate(runs: int = 400) -> float:
    """How often a kit that behaves exactly like the model passes the thermometer criterion, over independent noise
    draws. The tolerance is two combined standard errors, the fit's and the published one, so a good kit passes more
    often than the 95 % a two-standard-error band on the fit alone would give."""
    return sum(p1_thermometer(seed=1000 + k)["pass"] for k in range(runs)) / runs


def p1_figure(out: str | Path = "docs/img") -> Path:
    """Figure 54: expected P1 results, simulated with the A1 noise model and fitted with adamas.fitting."""
    import matplotlib.pyplot as plt
    from . import fitting, nv
    from .figures import COLORS, GOLD, INK, RED, _finish
    out = Path(out)
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.6)); plt.subplots_adjust(wspace=.32)
    r = np.random.default_rng(5); f = np.arange(2790.0, 2950.0 + 1e-9, 0.5)
    y = nv.odmr_spectrum(f, np.zeros(3), contrast=A1_CONTRAST, linewidth_mhz=A1_LINEWIDTH, hyperfine=False) + r.normal(0, A1_NOISE, f.size)
    fit = fitting.fit_odmr(f, y, max_lines=1); det = p1_detection()
    ax[0].plot(f, y, ".", ms=3, color="#8b98a5"); ax[0].plot(fit.x, fit.model, color=COLORS["Diamond"], lw=2)
    ax[0].set_title(f"1. Find the dip: {det['center_mhz']:.2f} ± {det['center_err_mhz']:.2f} MHz, signal-to-noise {det['snr']:.0f}", fontsize=10.5)
    ax[0].set_xlabel("microwave frequency (MHz)"); ax[0].set_ylabel("red fluorescence (normalized)")
    from . import experiments
    d = experiments.expected("magnet_distance"); m = p1_magnetometer()
    ax[1].loglog(d["x"], d["series"]["measured"], "o", color=GOLD); ax[1].loglog(d["x"], d["series"]["dipole law"], color=INK, lw=1.2)
    ax[1].set_title(f"2. Weigh a magnet: slope {m['slope']:.2f} ± {m['slope_err']:.2f} (dipole law −3)", fontsize=10.5)
    ax[1].set_xlabel("magnet distance (cm)"); ax[1].set_ylabel("outer line splitting (MHz)")
    from matplotlib.ticker import FixedLocator, NullFormatter, ScalarFormatter
    ax[1].xaxis.set_major_locator(FixedLocator([3, 4, 5, 6, 8, 10])); ax[1].xaxis.set_major_formatter(ScalarFormatter()); ax[1].xaxis.set_minor_formatter(NullFormatter())
    ax[1].yaxis.set_major_formatter(ScalarFormatter())
    th = p1_thermometer(); t = np.array(th["temps_c"]); c = np.array(th["centers_mhz"]); e = np.array(th["center_errs_mhz"])
    ax[2].errorbar(t, c, yerr=e, fmt="o", color=COLORS["Diamond"], capsize=3)
    tt = np.linspace(t.min() - 3, t.max() + 3, 50)
    ax[2].plot(tt, nv.zero_field_splitting_mhz(300.0) + DDDT_KHZ_K * 1e-3 * (tt + 273.15 - 300), color=RED, lw=1.2, label="−74.2 kHz/K [acosta2010]")
    ax[2].legend(fontsize=8, loc="upper right")
    ax[2].set_title(f"3. Thermometer: {th['slope_khz_k']:.1f} ± {th['slope_err_khz_k']:.1f} kHz/K (pass within ±{th['tolerance_khz_k']:.1f})", fontsize=10.5)
    ax[2].set_xlabel("diamond temperature (°C)"); ax[2].set_ylabel("fitted D (MHz)")
    return _finish(fig, out, "fig54_build_p1.png", "simulated with the A1 noise model (adamas.experiments) and fitted by adamas.fitting; adamas.build_program; [acosta2010] [doherty2013]")



# ---------------------------------------------------------------- P2 ------------------------------------------------
P2_TESTS = 5                 # Rabi, T2*, T2, |B|, E_A: the gate needs all of them
P2_GATE_COVERAGE = 0.95      # a correct setup should get "go" 95 % of the time
P2_TEST_COVERAGE = P2_GATE_COVERAGE ** (1 / P2_TESTS)     # so each test covers 98.98 % (independent tests)


def _k_normal(coverage: float = P2_TEST_COVERAGE) -> float:
    from scipy.stats import norm
    return float(norm.ppf(0.5 + coverage / 2))


def _within(value, expected, err, k: float | None = None) -> bool:
    """Pass when the fit lands within k of its own standard errors of the value it should find (k from the coverage)."""
    return bool(abs(value - expected) <= (_k_normal() if k is None else k) * err)


def p2_pulsed(seed: int = 4) -> dict:
    """B1: fit the simulated Rabi, Ramsey, and echo data (adamas.experiments: absolute noise 0.004 per point, 0.003 for
    the echo, on a signal of amplitude 0.1) with adamas.fitting and compare each parameter with the value put in
    (experiments.PULSED_TRUTH)."""
    from . import experiments, fitting
    T = experiments.PULSED_TRUTH; d = experiments.expected("pulsed", seed)["panels"]
    xr, yr = map(np.array, d["Rabi (µs)"]); xm, ym = map(np.array, d["Ramsey (µs)"]); xe, ye = map(np.array, d["Echo (µs)"])
    fr, fm, fe = fitting.fit_rabi(xr, yr), fitting.fit_ramsey(xm, ym), fitting.fit_echo(xe, ye)
    om, om_e = fr.params["rabi_MHz"], fr.errors["rabi_MHz"]
    t2s, t2s_e = abs(fm.params["T2star_us"]), fm.errors["T2star_us"]
    t2, t2_e = fe.params["T2_us"], fe.errors["T2_us"]
    return {"rabi_mhz": om, "rabi_err": om_e, "pi_ns": 500.0 / om, "pi_err_ns": 500.0 * om_e / om ** 2, "rabi_pass": _within(om, T["rabi_mhz"], om_e),
            "t2star_us": t2s, "t2star_err": t2s_e, "t2star_pass": _within(t2s, T["t2star_us"], t2s_e),
            "t2_us": t2, "t2_err": t2_e, "t2_pass": _within(t2, T["t2_us"], t2_e),
            "echo_gain": t2 / t2s, "echo_pass": bool(t2 / t2s > ECHO_GAIN_MIN), "truth": T}


ECHO_GAIN_MIN = 10.0        # this project's threshold: the echo must outlive free dephasing by an order of magnitude
VECTOR_LINE_REL = 0.01      # relative uncertainty of each orientation's half-splitting in the simulated B2 data


def p2_vector(seed: int = 4) -> dict:
    """B2: |B| from the four orientation half-splittings s_i = gamma |B . n_i|, sum_i (B . n_i)^2 = (4/3) |B|^2 for the
    tetrahedral NV axes [rondin2014]. The error is propagated from each line's uncertainty: here the 1 % put into the
    simulation; on real data, use each line's fit uncertainty. P2 tests the magnitude only, not the direction."""
    from . import experiments
    d = experiments.expected("vector", seed); s = np.array(d["series"]["fitted"]) / nv_gamma()
    b = math.sqrt(0.75 * float(np.sum(s ** 2))); b_err = 0.75 / b * math.sqrt(float(np.sum((s * VECTOR_LINE_REL * s) ** 2)))
    truth = float(np.linalg.norm(experiments.VECTOR_B_MT))
    return {"b_mt": b, "b_err": b_err, "truth_mt": truth, "pass": _within(b, truth, b_err)}


def nv_gamma() -> float:
    from . import nv
    return nv.GAMMA_MHZ_PER_MT


def p2_arrhenius(seed: int = 4) -> dict:
    """B3: corrected Arrhenius fit of the simulated resistivity (3 % noise). The correction R T^-0.7 is approximate,
    so even noise-free data give a slightly different E_A (the method bias); the fit is compared with E_A + bias.
    The fit uses only the lowest-temperature points, so its error has few degrees of freedom: the criterion uses the
    Student-t factor for the same coverage as the other tests."""
    from scipy.stats import t as student_t
    from . import doping, experiments, fitting
    d = experiments.expected("arrhenius", seed); x = np.array(d["x"]); R = np.array(d["series"]["resistivity (Ω·cm)"])
    f = fitting.fit_arrhenius(x, R)
    clean = fitting.fit_arrhenius(x, experiments.arrhenius_resistivity(1000 / x)).params["E_A_eV"]
    truth = doping.DOPANTS["C:B"].ea_ev
    n = max(5, len(x) // 3); k = float(student_t.ppf(0.5 + P2_TEST_COVERAGE / 2, n - 2))   # same point selection as fitting.fit_arrhenius
    return {"ea_ev": f.params["E_A_eV"], "ea_err": f.errors["E_A_eV"], "truth_ev": truth, "method_bias_ev": clean - truth,
            "points": n, "k": k, "pass": _within(f.params["E_A_eV"], clean, f.errors["E_A_eV"], k)}


def p2_gate(seed: int = 4) -> dict:
    pu, ve, ar = p2_pulsed(seed), p2_vector(seed), p2_arrhenius(seed)
    ok = pu["rabi_pass"] and pu["t2star_pass"] and pu["t2_pass"] and pu["echo_pass"] and ve["pass"] and ar["pass"]
    return {"pulsed": pu, "vector": ve, "arrhenius": ar, "verdict": "go" if ok else "stop"}


P2_RUNS = 1000


def p2_pass_rates(runs: int = P2_RUNS) -> dict:
    """Fraction of independent simulated runs in which each P2 test passes, and all of them together ("gate"). Each
    test is built for P2_TEST_COVERAGE, so the gate should pass P2_GATE_COVERAGE of correct setups; the binomial
    standard error of a rate p is sqrt(p (1 - p) / runs)."""
    keys = ("rabi_pass", "t2star_pass", "t2_pass")
    c = {k: 0 for k in keys + ("vector", "arrhenius", "gate")}
    for k in range(runs):
        g = p2_gate(2000 + k); pu = g["pulsed"]
        for q in keys:
            c[q] += pu[q]
        c["vector"] += g["vector"]["pass"]; c["arrhenius"] += g["arrhenius"]["pass"]; c["gate"] += g["verdict"] == "go"
    out = {k: v / runs for k, v in c.items()}
    out["runs"] = runs; out["se_test"] = math.sqrt(P2_TEST_COVERAGE * (1 - P2_TEST_COVERAGE) / runs)
    out["se_gate"] = math.sqrt(P2_GATE_COVERAGE * (1 - P2_GATE_COVERAGE) / runs); out["k"] = _k_normal()
    return out


def p2_bill() -> dict:
    from .experiments import EXPERIMENTS
    by = {e["id"]: e for e in EXPERIMENTS}
    rows = [(i, *p) for i in ("B1", "B2", "B3") for p in by[i]["parts"]]
    return {"rows": rows, "low": sum(r[3] for r in rows), "high": sum(r[4] for r in rows),
            "headline": {i: by[i]["cost"] for i in ("B1", "B2", "B3")}}


def p2_figure(out: str | Path = "docs/img") -> Path:
    """Figure 55: expected P2 results, simulated by adamas.experiments and fitted by adamas.fitting."""
    import matplotlib.pyplot as plt
    from . import experiments, fitting
    from .figures import COLORS, GOLD, INK, RED, _finish
    out = Path(out); g = p2_gate(); d = experiments.expected("pulsed")["panels"]
    fig, ax = plt.subplots(1, 4, figsize=(20, 4.6)); plt.subplots_adjust(wspace=.32)
    for a, (key, fn, title) in zip(ax[:3], (("Rabi (µs)", fitting.fit_rabi, f"Rabi: Ω = {g['pulsed']['rabi_mhz']:.3f} ± {g['pulsed']['rabi_err']:.3f} MHz, π pulse {g['pulsed']['pi_ns']:.1f} ns"),
                                            ("Ramsey (µs)", fitting.fit_ramsey, f"Ramsey: T₂* = {g['pulsed']['t2star_us']:.3f} ± {g['pulsed']['t2star_err']:.3f} µs"),
                                            ("Echo (µs)", fitting.fit_echo, f"Echo: T₂ = {g['pulsed']['t2_us']:.0f} ± {g['pulsed']['t2_err']:.0f} µs"))):
        x, y = map(np.array, d[key]); f = fn(x, y)
        a.plot(x, y, ".", ms=3, color="#8b98a5"); a.plot(f.x, f.model, color=COLORS["Diamond"], lw=2); a.set_title(title, fontsize=10.5); a.set_xlabel({"Rabi (µs)": "pulse length (µs)", "Ramsey (µs)": "free time τ (µs)", "Echo (µs)": "free time (µs)"}[key]); a.set_ylabel("contrast")
    a = ax[3]; ar = g["arrhenius"]; e = experiments.expected("arrhenius"); x = np.array(e["x"]); R = np.array(e["series"]["resistivity (Ω·cm)"])
    a.semilogy(x, R, "o", ms=4, color=GOLD); f = fitting.fit_arrhenius(x, R); a.semilogy(f.x, f.model, color=INK, lw=1.5)
    a.set_title(f"Boron: E_A = {ar['ea_ev']:.3f} ± {ar['ea_err']:.3f} eV (put in {ar['truth_ev']:g})", fontsize=10.5); a.set_xlabel("1000 / T (1/K)"); a.set_ylabel("resistivity (Ω·cm)")
    return _finish(fig, out, "fig55_build_p2.png", "simulated with adamas.experiments (B1, B3) and fitted by adamas.fitting; adamas.build_program; [barry2020] [hahn1950] [lagrange1998]")


# ---------------------------------------------------------------- P3 ------------------------------------------------
P3_TESTS = 3                 # antibunching, hyperfine triplet, nuclear-spin Rabi: the gate needs all of them
P3_GATE_COVERAGE = 0.95
P3_TEST_COVERAGE = P3_GATE_COVERAGE ** (1 / P3_TESTS)     # so each test covers 98.30 % (independent noise per test, see _rng)
P3_RUNS = 400
P3_RHO2 = 0.8                # rho^2 for one NV, rho = S / (S + B): illustrative background, as in experiment C1
P3_TAU_NS = 12.0             # antibunching time constant of the simulated data (illustrative, as in experiment C1)
P3_G2_NOISE = 0.03           # per 1 ns bin of the normalized histogram (illustrative)
P3_BIAS_MT = 1.0             # small axial bias field that separates the ms = +1 and -1 lines (illustrative)
P3_ODMR = {"contrast": 0.25, "linewidth_mhz": 0.4, "noise": 0.01}          # one NV, low microwave power (illustrative)
P3_BROAD_MHZ = 3.0           # degraded twin: power-broadened line, wider than the 2.147 MHz spacing
P3_RESOLVED_SNR = 5.0        # this project's criterion: the outer spacing exceeds five of its standard errors
P3_NUC_RABI_MHZ = 0.01       # 10 kHz nuclear Rabi frequency (illustrative)
P3_NUC_NOISE = 0.05          # per point, after normalizing with bright (ms = 0) and dark (ms = -1) reference counts (illustrative)


def _k3() -> float:
    """Two-sided coverage factor of each two-sided P3 test (hyperfine, nuclear Rabi)."""
    return _k_normal(P3_TEST_COVERAGE)


def _k3_one_sided() -> float:
    """One-sided coverage factor of the antibunching test (it only asks whether g2(0) is below 0.5)."""
    from scipy.stats import norm
    return float(norm.ppf(P3_TEST_COVERAGE))


def _rng(seed: int, test: int) -> np.random.Generator:
    """An independent random stream per test (0 antibunching, 1 hyperfine, 2 nuclear Rabi), so the three tests of one
    simulated setup have independent noise, as the coverage formula assumes. A degraded twin reuses its test's stream
    (common random numbers), so the fault, not the noise, is what differs."""
    return np.random.default_rng([seed, test])


def g2_zero_expected(emitters: int = 1, rho2_one: float = P3_RHO2) -> float:
    """g2(0) of N identical, independent emitters seen through uncorrelated background: 1 - rho_N^2 / N, where rho_N is
    the fraction of detected light that comes from the emitters. The background B is fixed by rho2_one (the value for
    one emitter, B/S = 1/rho_1 - 1), so rho_N = N / (N + B/S): a second NV adds light, not background. Valid for
    continuous, low-power excitation (bunching from the metastable singlet at |tau| > tau1 is neglected) and a detector
    time resolution much shorter than the antibunching time; one emitter with no background gives 0 [kurtsiefer2000]."""
    b_over_s = 1.0 / math.sqrt(rho2_one) - 1.0
    rho = emitters / (emitters + b_over_s)
    return 1.0 - rho ** 2 / emitters


def _g2_data(seed: int, emitters: int):
    r = _rng(seed, 0); tau = np.linspace(-80, 80, 161); g0 = g2_zero_expected(emitters)
    return tau, 1 - (1 - g0) * np.exp(-np.abs(tau) / P3_TAU_NS) + r.normal(0, P3_G2_NOISE, tau.size), g0


def _odmr_data(seed: int, linewidth_mhz: float):
    """One NV in a small axial field: the window covers the ms = 0 to -1 line only, near D - gamma_e B."""
    from . import nv
    f0 = nv.transition_frequencies_mhz((0.0, 0.0, P3_BIAS_MT))[0]
    f = np.linspace(f0 - 7.0, f0 + 7.0, 281)
    y = nv.odmr_spectrum(f, np.array([0, 0, P3_BIAS_MT]), axes=np.array([[0, 0, 1.0]]), contrast=P3_ODMR["contrast"], linewidth_mhz=linewidth_mhz, hyperfine=True)
    return f, y + _rng(seed, 1).normal(0, P3_ODMR["noise"], f.size)


def _nuc_data(seed: int, detuning_mhz: float):
    r = _rng(seed, 2); t = np.linspace(0.0, 300.0, 121)          # µs
    om = P3_NUC_RABI_MHZ; oe = math.hypot(om, detuning_mhz)
    return t, (om / oe) ** 2 * np.sin(np.pi * oe * t) ** 2 + r.normal(0, P3_NUC_NOISE, t.size)


def p3_antibunching(seed: int = 4, emitters: int = 1) -> dict:
    """C1, Hanbury Brown-Twiss: simulate the normalized coincidence histogram g2(tau) = 1 - (1 - g0) exp(-|tau|/tau1)
    with g0 from g2_zero_expected, fit with adamas.fitting.fit_g2, and pass when g2(0) + k sigma < 0.5 (one emitter;
    one-sided k). The degraded twin has two emitters in the focus (emitters=2), the one physical fault it must catch."""
    from . import fitting
    tau, y, g0 = _g2_data(seed, emitters)
    f = fitting.fit_g2(tau, y); v, e = float(f.params["g2_zero"]), float(f.errors["g2_zero"])
    k = _k3_one_sided()
    return {"emitters": emitters, "put_in": g0, "g2_zero": v, "err": e, "k": k, "pass": bool(np.isfinite(e) and v + k * e < 0.5)}


def p3_hyperfine(seed: int = 4, linewidth_mhz: float = P3_ODMR["linewidth_mhz"]) -> dict:
    """C1, low-power ODMR of one NV in a small axial field (P3_BIAS_MT; strain mixing is neglected, valid when
    gamma_e B is much larger than the strain splitting E): the ms = 0 to -1 line splits into three, spaced by the 14N
    hyperfine coupling |A_par| (2.147 MHz [felton2009], adamas.nv). Fit with adamas.fitting.fit_odmr (up to three
    lines). The test asks whether the nucleus is RESOLVED, not whether the constant is reproduced: pass when exactly
    three lines are found, the mean spacing (outer separation / 2) is at least P3_RESOLVED_SNR of its standard errors,
    and every fitted line is narrower (full width) than the spacing. The spacing is reported next to |A_par| for
    comparison only, because the published value's own uncertainty is not yet recorded (docs/STATUS.md). The degraded
    twin is power-broadened (linewidth P3_BROAD_MHZ, wider than the spacing), so the triplet is not resolved."""
    from . import fitting, nv
    f, y = _odmr_data(seed, linewidth_mhz)
    out = {"linewidth_mhz": linewidth_mhz, "reference": nv.A_PAR_14N_MHZ, "lines": 0, "spacing_mhz": float("nan"), "err": float("nan"),
           "max_fwhm_mhz": float("nan"), "pass": False}
    import warnings
    try:
        with warnings.catch_warnings():                 # a broadened (degraded) spectrum can leave a line's covariance undefined
            warnings.simplefilter("ignore", category=Warning)
            fit = fitting.fit_odmr(f, y, max_lines=3)
    except (ValueError, RuntimeError):
        return out
    idx = [k[6:] for k in fit.params if k.startswith("center")]
    c = sorted((fit.params[f"center{i}"], fit.errors[f"center{i}"]) for i in idx)
    out["lines"] = len(c)
    if len(c) == 3:
        a, e = (c[2][0] - c[0][0]) / 2, math.hypot(c[2][1], c[0][1]) / 2
        fwhm = max(2 * abs(fit.params[f"hwhm{i}"]) for i in idx)
        out.update(spacing_mhz=float(a), err=float(e), max_fwhm_mhz=float(fwhm))
        out["pass"] = bool(np.isfinite(e) and e > 0 and a / e >= P3_RESOLVED_SNR and fwhm < a)
    return out


def p3_nuclear_rabi(seed: int = 4, detuning_mhz: float = 0.0) -> dict:
    """C1 extended: initialize the 14N nuclear spin by optical pumping near the excited-state level anticrossing
    [jacques2009], drive it with an RF pulse of growing length, and read it out through the electron (a
    nuclear-state-selective microwave pi pulse, then optical readout; the method of [jelezko2004b], shown there on a
    13C nucleus). Assumes a pure initial nuclear state: with an unpolarized nucleus the contrast is smaller. The
    normalized signal is the flipped population P(t) = (Omega^2 / Omega_eff^2) sin^2(pi Omega_eff t),
    Omega_eff = sqrt(Omega^2 + delta^2) (rotating-wave limit, Omega much smaller than the RF frequency; no decay over the
    window). Fit with adamas.fitting.fit_rabi; the transferred population is twice the fitted amplitude. Pass when it
    is consistent with full transfer, |transfer - 1| <= k sigma: the drive is on resonance. The degraded twin is driven
    off resonance by one Rabi frequency, so only half the population moves."""
    from . import fitting
    t, y = _nuc_data(seed, detuning_mhz); om = P3_NUC_RABI_MHZ; oe = math.hypot(om, detuning_mhz)
    f = fitting.fit_rabi(t, y)
    tr, tr_e = 2 * f.params["amplitude"], 2 * f.errors["amplitude"]
    return {"detuning_mhz": detuning_mhz, "put_in_khz": om * 1e3, "rabi_khz": f.params["rabi_MHz"] * 1e3, "rabi_err_khz": f.errors["rabi_MHz"] * 1e3,
            "transfer": float(tr), "transfer_err": float(tr_e), "expected_transfer": (om / oe) ** 2, "k": _k3(),
            "pass": bool(np.isfinite(tr_e) and abs(tr - 1.0) <= _k3() * tr_e)}


def p3_gate(seed: int = 4) -> dict:
    ab, hf, nr = p3_antibunching(seed), p3_hyperfine(seed), p3_nuclear_rabi(seed)
    ok = ab["pass"] and hf["pass"] and nr["pass"]
    return {"antibunching": ab, "hyperfine": hf, "nuclear_rabi": nr, "verdict": "go" if ok else "stop"}


def p3_degraded(seed: int = 4) -> dict:
    """Each test run on its degraded twin (one physical fault each); every one must fail."""
    return {"antibunching": p3_antibunching(seed, emitters=2), "hyperfine": p3_hyperfine(seed, linewidth_mhz=P3_BROAD_MHZ),
            "nuclear_rabi": p3_nuclear_rabi(seed, detuning_mhz=P3_NUC_RABI_MHZ)}


def p3_pass_rates(runs: int = P3_RUNS) -> dict:
    """Fraction of independent simulated runs (seeds 3000 + i) in which each test passes on a correct setup, and in
    which the degraded twin wrongly passes. Binomial standard error at the design rate p: sqrt(p (1 - p) / runs)."""
    c = {k: 0 for k in ("antibunching", "hyperfine", "nuclear_rabi", "gate")}; d = {k: 0 for k in ("antibunching", "hyperfine", "nuclear_rabi")}
    for i in range(runs):
        g = p3_gate(3000 + i); b = p3_degraded(3000 + i)
        for k in d:
            c[k] += g[k]["pass"]; d[k] += b[k]["pass"]
        c["gate"] += g["verdict"] == "go"
    out = {k: v / runs for k, v in c.items()}
    out["degraded"] = {k: v / runs for k, v in d.items()}
    out.update(runs=runs, k=_k3(), se_test=math.sqrt(P3_TEST_COVERAGE * (1 - P3_TEST_COVERAGE) / runs),
               se_gate=math.sqrt(P3_GATE_COVERAGE * (1 - P3_GATE_COVERAGE) / runs))
    return out


def p3_bill() -> dict:
    """Parts and price range for P3: the C1 part list (approximate 2026 street prices from adamas.experiments; estimates,
    not quotes). The RF source for the nuclear spin (Atlas M53) and the charge-state
    laser (M54) have no sourced price and are listed without one."""
    from .experiments import EXPERIMENTS
    by = {e["id"]: e for e in EXPERIMENTS}
    rows = [("C1", *p) for p in by["C1"]["parts"]]
    return {"rows": rows, "low": sum(r[3] for r in rows), "high": sum(r[4] for r in rows), "headline": by["C1"]["cost"], "unpriced": ["M53", "M54"]}


P3_MACHINES = ("M47", "M48", "M49", "M50", "M51", "M52", "M53", "M54")


def p3_figure(out: str | Path = "docs/img") -> Path:
    """Figure 56: expected P3 results (nominal and degraded twin), simulated here and fitted by adamas.fitting."""
    import matplotlib.pyplot as plt
    from . import fitting, nv
    from .figures import COLORS, INK, RED, _finish
    out = Path(out); g = p3_gate()
    fig, ax = plt.subplots(1, 3, figsize=(19, 4.8)); plt.subplots_adjust(wspace=.3)
    a = ax[0]
    for n, col, lab in ((1, COLORS["Diamond"], "one NV"), (2, RED, "two NVs (degraded twin)")):
        x, y, _ = _g2_data(4, n); a.plot(x, y, ".", ms=2.5, color=col, alpha=.6)
        r = p3_antibunching(emitters=n); fit = fitting.fit_g2(x, y); a.plot(fit.x, fit.model, color=col, lw=2, label=f"{lab}: g⁽²⁾(0) = {r['g2_zero']:.2f} ± {r['err']:.2f}")
    a.axhline(0.5, color=INK, ls="--", lw=1); a.set_ylim(0, 1.25); a.legend(fontsize=8, loc="lower right")
    a.set_title("1. Antibunching: pass when g⁽²⁾(0) + kσ < 0.5 (dots data, lines fits)", fontsize=10.5); a.set_xlabel("delay τ (ns)"); a.set_ylabel("g⁽²⁾(τ)")
    a = ax[1]
    for lw, col, lab, off in ((P3_ODMR["linewidth_mhz"], COLORS["Diamond"], "low power", 0.0), (P3_BROAD_MHZ, RED, "power-broadened (degraded twin)", -0.12)):
        f, y = _odmr_data(4, lw)
        a.plot(f, y + off, ".", ms=2.5, color=col, label=lab)
    hf = g["hyperfine"]; a.legend(fontsize=8, loc="lower left")
    a.set_title(f"2. Hyperfine triplet resolved: spacing {hf['spacing_mhz']:.3f} ± {hf['err']:.3f} MHz (|A∥| {nv.A_PAR_14N_MHZ} MHz)", fontsize=10.5)
    a.set_xlabel(f"microwave frequency (MHz), ms = 0 to −1 at {P3_BIAS_MT:g} mT"); a.set_ylabel("fluorescence (normalized; red offset −0.12)")
    a = ax[2]
    for det, col, lab in ((0.0, COLORS["Diamond"], "on resonance"), (P3_NUC_RABI_MHZ, RED, "detuned by Ω (degraded twin)")):
        x, y = _nuc_data(4, det); a.plot(x, y, ".", ms=3, color=col, alpha=.6)
        r = p3_nuclear_rabi(detuning_mhz=det); fit = fitting.fit_rabi(x, y)
        a.plot(fit.x, fit.model, color=col, lw=2, label=f"{lab}: transfer {r['transfer']:.2f} ± {r['transfer_err']:.2f}")
    a.set_ylim(-0.2, 1.45); a.legend(fontsize=8, loc="upper right")
    a.set_title(f"3. Nuclear-spin Rabi: {g['nuclear_rabi']['rabi_khz']:.2f} ± {g['nuclear_rabi']['rabi_err_khz']:.2f} kHz", fontsize=10.5)
    a.set_xlabel("RF pulse length (µs)"); a.set_ylabel("flipped nuclear population")
    return _finish(fig, out, "fig56_build_p3.png", "simulated and fitted by adamas.build_program and adamas.fitting (illustrative inputs); [kurtsiefer2000] [felton2009] [jelezko2004b]")



# ---------------------------------------------------------------- P4 ------------------------------------------------
P4_CHECKS = 4                # contact resistance, threshold matching, mobility, threshold: the gate needs all of them
P4_GATE_COVERAGE = 0.95
P4_TEST_COVERAGE = P4_GATE_COVERAGE ** (1 / P4_CHECKS)     # so each check covers 98.73 % (independent noise per test)
P4_RUNS = 1000
# Illustrative inputs. The FET values are the defaults of adamas.logic.Fet (the PDK-0 design values the Transistor Lab and
# the SPICE models use, illustrative values inside published ranges); the rest are chosen to look like a typical run.
P4_RSH_KOHM = 10.0           # sheet resistance of the hydrogen-terminated channel, kΩ/sq (inside the S08 window, 3 to 30)
P4_RC_OHM_MM = 3.0           # contact resistance, Ω·mm (below the S17 limit of 10)
P4_RC_BAD_OHM_MM = 20.0      # degraded twin: residue under the gold contacts
P4_TLM_W_UM = 100.0          # pad width of the PDK-0 TLM ladder (adamas.pdk0.tlm_ladder)
P4_TLM_GAPS_UM = (2.0, 4.0, 8.0, 16.0, 32.0)               # its gaps (adamas.pdk0.tlm_ladder)
P4_TLM_NOISE = 0.02          # relative, per resistance (illustrative)
P4_AVT_MV_UM = 226.0         # Pelgrom coefficient A_VT: sigma(V_T) = A_VT / sqrt(W L), so 40 mV at 16/2 µm (illustrative)
P4_AVT_BAD_MV_UM = 1130.0    # degraded twin: patchy hydrogen termination, five times the spread
P4_MATCH_GEOMS = ((4.0, 2.0), (8.0, 2.0), (16.0, 2.0), (32.0, 2.0))   # PDK-0 enhancement FETs with L = 2 µm, 4 copies each (adamas.pdk0)
P4_VT_GROUP_SIZE = 4
P4_VT_LIMIT_V = 0.2          # traveler S17 limit on sigma(V_T) in 4-device groups (an ADAMAS target, with Pelgrom area scaling [pelgrom1989])
P4_FET_W_UM, P4_FET_L_UM = 16.0, 2.0                       # the PDK-0 cell PFET_W16_L2_E used for extraction
P4_TOX_BAD_NM = 45.0         # degraded twin: an Al2O3 gate 1.5 times too thick (ALD cycle count off)
P4_ID_NOISE = 0.01           # relative, per drain-current reading (illustrative)
P4_VDS_V = 0.1               # linear-regime drain bias of the transfer curve


def _k4() -> float:
    return _k_normal(P4_TEST_COVERAGE)


def _k4_one_sided() -> float:
    from scipy.stats import norm
    return float(norm.ppf(P4_TEST_COVERAGE))


def _rng4(seed: int, test: int) -> np.random.Generator:
    """Independent stream per test (0 TLM, 1 matching, 2 extraction); a degraded twin reuses its test's stream."""
    return np.random.default_rng([seed, 4, test])


def tlm_resistance_ohm(gap_um, rsh_kohm: float = P4_RSH_KOHM, rc_ohm_mm: float = P4_RC_OHM_MM, w_um: float = P4_TLM_W_UM):
    """Transfer length method: R(d) = 2 Rc / W + R_sh d / W (two contacts in series with the channel) [sze2006]. Valid
    for contacts longer than the transfer length and a uniform sheet; Rc is in Ω·mm, so Rc / W uses W in mm."""
    d = np.asarray(gap_um, float)
    return 2 * rc_ohm_mm / (w_um * 1e-3) + rsh_kohm * 1e3 * d / w_um


def p4_tlm(seed: int = 4, rc_ohm_mm: float = P4_RC_OHM_MM) -> dict:
    """PDK-0 TLM ladder: simulate R(d) with P4_TLM_NOISE, fit a straight line weighted by the relative noise, and read
    Rc = intercept x W / 2 and R_sh = slope x W. Pass when Rc + k sigma <= 10 Ω·mm (traveler S17) and R_sh lies inside
    the S08 window (3 to 30 kΩ/sq). The degraded twin has residue under the contacts (Rc = P4_RC_BAD_OHM_MM)."""
    d = np.array(P4_TLM_GAPS_UM); r_true = tlm_resistance_ohm(d, rc_ohm_mm=rc_ohm_mm)
    r = r_true * (1 + _rng4(seed, 0).normal(0, P4_TLM_NOISE, d.size))
    (m, b), cov = np.polyfit(d, r, 1, w=1 / (P4_TLM_NOISE * r), cov="unscaled")
    w_mm = P4_TLM_W_UM * 1e-3
    rc, rc_e = b * w_mm / 2, math.sqrt(cov[1, 1]) * w_mm / 2
    rsh, rsh_e = m * P4_TLM_W_UM / 1e3, math.sqrt(cov[0, 0]) * P4_TLM_W_UM / 1e3
    k = _k4_one_sided()
    return {"gaps_um": d.tolist(), "r_ohm": r.tolist(), "rc_put_in": rc_ohm_mm, "rc_ohm_mm": float(rc), "rc_err": float(rc_e),
            "rsh_kohm": float(rsh), "rsh_err": float(rsh_e), "k": k, "limit_ohm_mm": 10.0,
            "pass": bool(rc + k * rc_e <= 10.0 and 3.0 <= rsh <= 30.0)}


def p4_matching(seed: int = 4, avt_mv_um: float = P4_AVT_MV_UM) -> dict:
    """Threshold matching on the four PDK-0 enhancement FETs with L = 2 µm (W = 4, 8, 16, 32 µm), four copies each.
    Pelgrom scaling, sigma(V_T) = A_VT / sqrt(W L) [pelgrom1989] (valid for closely spaced, identical devices), lets the
    four geometries be pooled: each deviation from its group mean is multiplied by sqrt(W L), giving one estimate of A_VT
    with 12 degrees of freedom. The check applies the traveler S17 limit (200 mV, an ADAMAS target) to the smallest
    device, sigma(4/2) = A_VT / sqrt(8 µm²), using the one-sided upper confidence bound of A_VT at the per-check coverage.
    The degraded twin has patchy hydrogen termination (A_VT = P4_AVT_BAD_MV_UM)."""
    from scipy.stats import chi2
    r = _rng4(seed, 1); ss = 0.0; dof = 0; vts = []
    for w, l in P4_MATCH_GEOMS:
        vt = 1.0 + r.normal(0, avt_mv_um / 1e3 / math.sqrt(w * l), P4_VT_GROUP_SIZE); vts.append(vt.tolist())
        ss += w * l * float(np.sum((vt - vt.mean()) ** 2)); dof += P4_VT_GROUP_SIZE - 1
    a_hat = math.sqrt(ss / dof); a_up = a_hat * math.sqrt(dof / chi2.ppf(1 - P4_TEST_COVERAGE, dof))
    smallest = min(w * l for w, l in P4_MATCH_GEOMS)
    return {"avt_put_in_mv_um": avt_mv_um, "avt_mv_um": 1e3 * a_hat, "avt_upper_mv_um": 1e3 * a_up, "dof": dof, "vt": vts,
            "s_mv": 1e3 * a_hat / math.sqrt(smallest), "upper_mv": 1e3 * a_up / math.sqrt(smallest), "limit_mv": 1e3 * P4_VT_LIMIT_V,
            "pass": bool(a_up / math.sqrt(smallest) <= P4_VT_LIMIT_V)}


EPS0_F_CM = 8.8541878128e-14     # vacuum permittivity in F/cm (adamas.constants.EPS0 is in F/m)


def _fet(tox_nm: float | None = None):
    from .logic import Fet
    return Fet(w_um=P4_FET_W_UM, l_um=P4_FET_L_UM) if tox_nm is None else Fet(w_um=P4_FET_W_UM, l_um=P4_FET_L_UM, tox_nm=tox_nm)


def _transfer_data(seed: int, tox_nm: float, rc_ohm_mm: float = P4_RC_OHM_MM):
    """Linear-regime transfer curve |I_D|(|V_GS|) at |V_DS| = P4_VDS_V of PFET_W16_L2_E, from the square law of
    adamas.logic.Fet with each contact (R_c / W) in series: the device sees V_GS - I R_c/W and V_DS - 2 I R_c/W, and I is
    solved self-consistently. Relative noise P4_ID_NOISE per reading."""
    from scipy.optimize import brentq
    fet = _fet(tox_nm); rc1 = rc_ohm_mm / (fet.w_um * 1e-3)
    vgs = np.linspace(2.0, 8.0, 25)
    i = np.array([brentq(lambda x: fet.current(v - x * rc1, P4_VDS_V - 2 * x * rc1) - x, 0.0, P4_VDS_V / (2 * rc1)) for v in vgs])
    return vgs, i * (1 + _rng4(seed, 2).normal(0, P4_ID_NOISE, vgs.size))


def _extract(vgs, i, rc_ohm_mm: float):
    """Remove the contacts, then fit the triode law. With R1 = R_c / W per contact: V_DS' = V_DS - 2 I R1,
    V_GS' = V_GS - I R1, g = I / V_DS' = k (V_GS' - V_T - V_DS'/2), a straight line in x = V_GS' - V_DS'/2 with slope k
    and intercept -k V_T [sze2006]. Returns (mu, V_T, cov of the line, k)."""
    nom = _fet(); r1 = rc_ohm_mm / (nom.w_um * 1e-3)
    vds_i = P4_VDS_V - 2 * i * r1; x = vgs - i * r1 - vds_i / 2; g = i / vds_i
    g_err = P4_ID_NOISE * g * P4_VDS_V / vds_i              # dg/g = (dI/I) V_DS / V_DS': removing the contacts amplifies noise
    (m, b), cov = np.polyfit(x, g, 1, w=1 / g_err, cov="unscaled")
    cox = nom.eps_ox * EPS0_F_CM / (nom.tox_nm * 1e-7)
    return m * nom.l_um / (cox * nom.w_um), -b / m, cov, m, b, cox


def p4_extraction(seed: int = 4, tox_nm: float | None = None) -> dict:
    """Mobility and threshold of PFET_W16_L2_E from the linear-regime transfer curve, with the contacts removed using
    the contact resistance MEASURED on the TLM ladder of the same run (p4_tlm). Its uncertainty is propagated (numerical
    derivative of mu and V_T with respect to R_c, added in quadrature to the fit's errors), so the TLM and extraction
    checks are correlated. mu = k L / (C_ox W) with C_ox from the PDK-0 oxide (30 nm, relative permittivity 9). Pass when
    both lie within k sigma of the PDK-0 values: the device matches the model. The degraded twin's Al2O3 is
    P4_TOX_BAD_NM thick while the analysis assumes 30 nm, so mu comes out at 30/45 (two thirds) of its true value."""
    nom = _fet(); tox = nom.tox_nm if tox_nm is None else tox_nm
    tlm = p4_tlm(seed); rc, rc_e = tlm["rc_ohm_mm"], tlm["rc_err"]
    vgs, i = _transfer_data(seed, tox)
    mu, vt, cov, m, b, cox = _extract(vgs, i, rc)
    h = 0.01 * rc_e
    mu_p, vt_p = _extract(vgs, i, rc + h)[:2]; mu_m, vt_m = _extract(vgs, i, rc - h)[:2]
    dmu, dvt = (mu_p - mu_m) / (2 * h), (vt_p - vt_m) / (2 * h)
    mu_e = math.hypot(math.sqrt(cov[0, 0]) * nom.l_um / (cox * nom.w_um), dmu * rc_e)
    jac = np.array([b / m ** 2, -1 / m]); vt_e = math.hypot(math.sqrt(float(jac @ cov @ jac)), dvt * rc_e)
    k = _k4()
    return {"tox_nm": tox, "rc_used_ohm_mm": rc, "mu": float(mu), "mu_err": float(mu_e), "mu_model": nom.mu_cm2_vs, "vt": float(vt), "vt_err": float(vt_e),
            "vt_model": nom.vth, "k": k, "mu_pass": _within(mu, nom.mu_cm2_vs, mu_e, k), "vt_pass": _within(vt, nom.vth, vt_e, k)}


def p4_gate(seed: int = 4) -> dict:
    t, m, e = p4_tlm(seed), p4_matching(seed), p4_extraction(seed)
    ok = t["pass"] and m["pass"] and e["mu_pass"] and e["vt_pass"]
    return {"tlm": t, "matching": m, "extraction": e, "verdict": "go" if ok else "stop"}


def p4_degraded(seed: int = 4) -> dict:
    """Each test on its degraded twin (one process fault each); every one must fail."""
    return {"tlm": p4_tlm(seed, rc_ohm_mm=P4_RC_BAD_OHM_MM), "matching": p4_matching(seed, avt_mv_um=P4_AVT_BAD_MV_UM),
            "extraction": p4_extraction(seed, tox_nm=P4_TOX_BAD_NM)}


def p4_pass_rates(runs: int = P4_RUNS) -> dict:
    """Pass rates over simulated runs (seeds 4000 + i) for correct setups, and wrong-pass rates for the degraded twins."""
    keys = ("tlm", "matching", "mu", "vt", "gate"); c = dict.fromkeys(keys, 0); d = dict.fromkeys(("tlm", "matching", "extraction"), 0)
    for i in range(runs):
        g = p4_gate(4000 + i); b = p4_degraded(4000 + i)
        c["tlm"] += g["tlm"]["pass"]; c["matching"] += g["matching"]["pass"]; c["mu"] += g["extraction"]["mu_pass"]; c["vt"] += g["extraction"]["vt_pass"]
        c["gate"] += g["verdict"] == "go"
        d["tlm"] += b["tlm"]["pass"]; d["matching"] += b["matching"]["pass"]; d["extraction"] += b["extraction"]["mu_pass"] and b["extraction"]["vt_pass"]
    out = {k: v / runs for k, v in c.items()}
    out["degraded"] = {k: v / runs for k, v in d.items()}
    out.update(runs=runs, k=_k4(), k_one=_k4_one_sided(), se_test=math.sqrt(P4_TEST_COVERAGE * (1 - P4_TEST_COVERAGE) / runs),
               se_gate=math.sqrt(P4_GATE_COVERAGE * (1 - P4_GATE_COVERAGE) / runs))
    return out



def p4_bill() -> dict:
    """Parts and price range for P4: the C2 part list (approximate 2026 street prices from adamas.experiments; estimates,
    not quotes). The high-voltage curve tracer (Atlas M18) and the photoelectric readout chain (M55) have no sourced
    price and are listed without one."""
    from .experiments import EXPERIMENTS
    by = {e["id"]: e for e in EXPERIMENTS}
    rows = [("C2", *p) for p in by["C2"]["parts"]]
    return {"rows": rows, "low": sum(r[3] for r in rows), "high": sum(r[4] for r in rows), "headline": by["C2"]["cost"], "unpriced": ["M18", "M55"]}


P4_MACHINES = ("M01", "M10", "M11", "M12", "M13", "M14", "M15", "M16", "M17", "M18", "M19")


def p4_figure(out: str | Path = "docs/img") -> Path:
    """Figure 57: expected P4 results (nominal and degraded twin), simulated and fitted here."""
    import matplotlib.pyplot as plt
    from .figures import COLORS, INK, RED, _finish
    out = Path(out); g, b = p4_gate(), p4_degraded()
    fig, ax = plt.subplots(1, 3, figsize=(19, 4.8)); plt.subplots_adjust(wspace=.3)
    a = ax[0]; xx = np.linspace(0, 34, 50)
    for r, col, lab in ((g["tlm"], COLORS["Diamond"], "clean contacts"), (b["tlm"], RED, "residue under the gold (degraded twin)")):
        a.plot(r["gaps_um"], r["r_ohm"], "o", ms=5, color=col)
        a.plot(xx, 2 * r["rc_ohm_mm"] / (P4_TLM_W_UM * 1e-3) + r["rsh_kohm"] * 1e3 * xx / P4_TLM_W_UM, color=col, lw=2,
               label=f"{lab}: Rc = {r['rc_ohm_mm']:.1f} ± {r['rc_err']:.1f} Ω·mm")
    a.legend(fontsize=8, loc="upper left"); a.set_xlim(0, 34); a.set_ylim(0, None)
    a.set_title("1. Contacts (TLM): pass when Rc + kσ ≤ 10 Ω·mm", fontsize=10.5); a.set_xlabel("gap between pads (µm)"); a.set_ylabel("resistance (Ω), pads 100 µm wide")
    a = ax[1]
    for r, col, off, lab in ((g["matching"], COLORS["Diamond"], -0.12, "uniform termination"), (b["matching"], RED, 0.12, "patchy termination (degraded twin)")):
        for grp, vt in enumerate(r["vt"]):
            a.plot(np.full(len(vt), grp + 1 + off), vt, "o", ms=5, color=col, label=f"{lab}: σ(4/2) bound {r['upper_mv']:.0f} mV" if grp == 0 else None)
    a.set_ylim(0.2, 2.1); a.legend(fontsize=8, loc="upper left"); a.set_xticks(range(1, len(P4_MATCH_GEOMS) + 1), [f"{w:g}/{l:g}" for w, l in P4_MATCH_GEOMS])
    a.set_title(f"2. Threshold matching: pass when the σ(V_T) bound ≤ {P4_VT_LIMIT_V * 1e3:.0f} mV", fontsize=10.5); a.set_xlabel("FET W/L (µm), four copies each"); a.set_ylabel("|V_T| (V)")
    a = ax[2]
    for tox, col, lab in ((30.0, COLORS["Diamond"], "30 nm Al₂O₃"), (P4_TOX_BAD_NM, RED, f"{P4_TOX_BAD_NM:g} nm Al₂O₃ (degraded twin)")):
        vgs, i = _transfer_data(4, tox); e = p4_extraction(4, None if tox == 30.0 else tox)
        r1 = e["rc_used_ohm_mm"] / (P4_FET_W_UM * 1e-3); vds_i = P4_VDS_V - 2 * i * r1; x = vgs - i * r1 - vds_i / 2
        _, _, _, m_fit, b_fit, _ = _extract(vgs, i, e["rc_used_ohm_mm"])
        a.plot(x, 1e3 * i / vds_i, "o", ms=3.5, color=col)
        a.plot(x, 1e3 * (m_fit * x + b_fit), color=col, lw=1.5, label=f"{lab}: µ = {e['mu']:.0f} ± {e['mu_err']:.0f} cm²/V·s")
    a.axhline(0, color=INK, lw=.6); a.legend(fontsize=8, loc="upper left")
    a.set_title("3. Mobility and threshold of the 16/2 FET: match the model (150 cm²/V·s, 1.0 V)", fontsize=10.5)
    a.set_xlabel("|V_GS'| − |V_DS'|/2 at the channel (V)"); a.set_ylabel("channel conductance, contacts removed (mS)")
    return _finish(fig, out, "fig57_build_p4.png", "simulated and fitted by adamas.build_program (illustrative inputs; FET model adamas.logic); [sze2006] [pelgrom1989]")


def _p4_rates_note(rates: dict) -> str:
    """The sentences under the P4 pass/fail table, written from the computed rates so they cannot go stale."""
    design = P4_TEST_COVERAGE; se = rates["se_test"]
    out = []
    for key, name in (("tlm", "contact"), ("matching", "matching"), ("mu", "mobility"), ("vt", "threshold")):
        v = rates[key]
        word = "more often than" if v > design + 3 * se else "less often than" if v < design - 3 * se else "about as often as"
        out.append(f"the {name} check passes correct runs {word} designed ({100 * v:.1f} %)")
    text = "Against the {:.2f} % design per check: ".format(100 * design) + "; ".join(out) + ". "
    text += ("A check whose value sits far inside its limit passes almost always, so the gate rate is set by the others; the mobility and threshold checks are correlated (one fit gives both). "
             "Departures from the design come from removing the contacts (a nonlinear correction) and from weights computed from noisy currents. ")
    text += (f"Over {rates['runs']} runs the gate passes {100 * rates['gate']:.1f} % of correct runs" +
             (", at least the 95 % it is designed for." if rates["gate"] >= P4_GATE_COVERAGE - 3 * rates["se_gate"] else ", below the 95 % it is designed for: the tolerances need widening."))
    return text


def _p4_md() -> str:
    from . import atlas, atlas_prices
    from .experiments import EXPERIMENTS
    from .traveler import STEPS
    by = {e["id"]: e for e in EXPERIMENTS}; st = {s["id"]: s for s in STEPS}
    g, b, bill, rates = p4_gate(), p4_degraded(), p4_bill(), p4_pass_rates(P4_RUNS)
    t, m, e = g["tlm"], g["matching"], g["extraction"]; bt, bm, be = b["tlm"], b["matching"], b["extraction"]
    yes = lambda v: "yes" if v else "no"   # noqa: E731
    pct = lambda v: f"{100 * v:.1f} %"   # noqa: E731
    parts = {"Cleanroom access": "M10 to M16", "Hydrogen plasma": "M01", "Probe station and analyzer": "M17"}
    acr = {"MPCVD": "microwave plasma chemical vapor deposition (MPCVD)"}
    rows = "\n".join(f"| {parts.get(r[1], '(not in the Atlas)')} | {r[1]} ({r[0]}) | {r[2]} | {r[3]:,} to {r[4]:,} |" for r in bill["rows"])
    use = {"M18": "breakdown tests (not yet simulated)", "M55": "photoelectric NV readout (not yet simulated)"}
    rows += "\n" + "\n".join(f"| {k} | {acr['MPCVD'] if k == 'M01' else atlas.tool(k)} | {use[k]} | {atlas_prices.short_price(k)} |" for k in bill["unpriced"])
    machines = ", ".join(f"{k} {atlas.tool(k)}" for k in P4_MACHINES)
    steps = "\n".join(f"{i + 1}. **{s[0]}.** {s[1]}" for i, s in enumerate(by["C2"]["steps"]))
    hazards = " ".join(dict.fromkeys(h for sid in ("S02", "S03", "S09", "S12", "S13", "S15", "S17") for h in st[sid]["safety"] if not h.startswith("As ")))
    verdict = ("All simulated checks pass and every degraded twin fails, so the analysis can tell a good run from a faulty one; the gate is decided by the measured values on your wafer."
               if g["verdict"] == "go" and not (bt["pass"] or bm["pass"] or (be["mu_pass"] and be["vt_pass"]))
               else "On this run a simulated check fails or a degraded twin passes; a correct run fails about one time in twenty, so repeat it before changing the analysis.")
    return f"""# P4 · Devices: hydrogen-terminated diamond field-effect transistors

{GEN}

**Status: written in full.** Budget: **US${bill['low']:,} to {bill['high']:,}** for the C2 parts listed below (approximate 2026 street prices from the experiment list, estimates and not quotes; the experiment page gives a reviewer estimate of US${bill['headline'][0]:,} to {bill['headline'][1]:,}). The high-voltage curve tracer and the photoelectric readout chain are not priced yet ([STATUS.md](../STATUS.md)). Gate verdict in simulation: **{g['verdict']}**.

Every input below is **illustrative**: the transistor values are the design values of `adamas.logic` for process design kit 0 (PDK-0), the ones the Transistor Lab and the circuit-simulator (SPICE) models use, chosen inside published ranges; the rest are chosen to look like a typical run. The pass limits are **ADAMAS engineering targets** written into process traveler T1 (steps S08 and S17), not values from the literature. The phase is **simulated**: no ADAMAS hardware has run it.

## Goal

Run process traveler T1 (hydrogen-terminated transistors) on one or two plates in a university cleanroom (experiment C2) and turn the PDK-0 monitor die into numbers: contact and sheet resistance, threshold matching, and the channel mobility and threshold of the field-effect transistor (FET). P4 is the classical track; it meets the quantum track of nitrogen-vacancy (NV) centers (P3, P5) at P6.

## Physics and equations

- **Transfer length method (TLM):** pads of width W at gaps d give R(d) = 2R_c/W + R_sh·d/W, two contacts in series with the channel [sze2006]. A straight line through R(d) gives the sheet resistance R_sh from the slope and the contact resistance R_c from the intercept. Valid for contacts longer than the transfer length and a uniform sheet. The PDK-0 ladder has pads {P4_TLM_W_UM:g} µm wide and gaps of {', '.join(f'{x:g}' for x in P4_TLM_GAPS_UM)} µm (`adamas.pdk0`).
- **Threshold matching:** the spread of V_T between nominally identical, closely spaced transistors falls with gate area, σ(V_T) = A_VT/√(WL) [pelgrom1989]. The monitor die has four copies of each FET geometry (`adamas.pdk0`); the four enhancement-mode geometries with L = 2 µm (W = {', '.join(f'{w:g}' for w, _ in P4_MATCH_GEOMS)} µm) are pooled by scaling each deviation by √(WL), which gives one estimate of A_VT with {m['dof']} degrees of freedom. Its one-sided upper confidence bound, Â·√(dof/χ²) with the χ² quantile at the per-check coverage, is converted back to σ(V_T) of the smallest device (4/2 µm) and compared with the traveler's {P4_VT_LIMIT_V * 1e3:.0f} mV, an ADAMAS target motivated by this area scaling.
- **Mobility and threshold:** in the linear (triode) region the square law gives I_D = k[(V_GS − V_T)V_DS − V_DS²/2], k = µC_ox·W/L [sze2006], with C_ox = ε_ox ε₀/t_ox. Each contact adds R_c/W, so the channel sees V_DS' = V_DS − 2I_D R_c/W and V_GS' = V_GS − I_D R_c/W. Then g = I_D/V_DS' = k(V_GS' − V_T − V_DS'/2) is a straight line in x = V_GS' − V_DS'/2: slope k, intercept −kV_T. Leaving out the V_DS/2 term would bias V_T by V_DS/2. R_c is the value **measured on the TLM** of the same run, and its uncertainty is carried into µ and V_T, so the contact and extraction checks are correlated. Valid for a long channel below saturation. The device is PFET_W16_L2_E of the monitor die; the model values are µ = 150 cm²/V·s, |V_T| = 1.0 V and 30 nm of Al₂O₃ with relative permittivity 9 (`adamas.logic`, illustrative; 30 nm lies between the traveler's thin option A, about 10 nm, and thick option B, 100 to 200 nm, at step S13).

Diamond FETs are p-channel; magnitudes are used throughout, as in `adamas.logic`. The simulated curves come from `adamas.logic.Fet`, the square law the Transistor Lab runs, and a test checks that the analysis returns its µ and V_T exactly from noise-free data.

## Machines and consumables

Atlas machines for this phase: {machines}.

| Atlas | Part (experiment) | Specification | US$ |
|---|---|---|---|
{rows}

## Facility and safety

A university cleanroom with wet benches, lithography, evaporation, atomic layer deposition (ALD), plasma tools, a {acr['MPCVD']} reactor for the hydrogen plasma, and a probe station. {hazards} Hydrofluoric and perchloric acids, nitrogen dioxide, trimethylaluminium and high-voltage tests each need your institution's specific training and sign-off before first use; this page does not replace that training.

## Procedure

C2:

{steps}

On the monitor die (traveler S17): measure the TLM ladder first, so its contact resistance is available when you extract the FET; then V_T on the four copies of each enhancement-mode FET with L = 2 µm; then the transfer curve of PFET_W16_L2_E at |V_DS| = {P4_VDS_V:g} V, |V_GS| from 2 to 8 V; then the metal-oxide-semiconductor (MOS) capacitor, whose capacitance–voltage (C–V) curve measures C_ox directly instead of assuming the oxide thickness.

## Expected results (simulated)

Each test is shown with its **degraded twin**: the same simulation with one process fault, which the test must catch.

![Expected P4 results](../img/fig57_build_p4.png)

## Pass/fail

The gate needs all {P4_CHECKS} checks to pass, so each is set for {100 * P4_TEST_COVERAGE:.2f} % coverage: k = {rates['k_one']:.2f} for the one-sided contact-resistance check and {rates['k']:.2f} for the two-sided mobility and threshold checks; the matching check uses the χ² bound at the same coverage. Each test draws its own noise, but the extraction uses the contact resistance measured by the TLM, so those two checks are correlated. Rates are over {rates['runs']} simulated runs (binomial standard error at the design rate: {100 * rates['se_test']:.1f} percentage points per check, {100 * rates['se_gate']:.1f} for the gate).

| Check | Criterion | Put in | Measured | Pass? | Correct runs passing |
|---|---|---|---|---|---|
| Contact resistance (TLM) | R_c + kσ ≤ 10 Ω·mm (S17, ADAMAS); R_sh in 3 to 30 kΩ/sq (S08, ADAMAS) | R_c {t['rc_put_in']:g} Ω·mm, R_sh {P4_RSH_KOHM:g} kΩ/sq | R_c {t['rc_ohm_mm']:.2f} ± {t['rc_err']:.2f} Ω·mm, R_sh {t['rsh_kohm']:.2f} ± {t['rsh_err']:.2f} kΩ/sq | {yes(t['pass'])} | {pct(rates['tlm'])} |
| Threshold matching | upper bound on σ(V_T) of the 4/2 FET ≤ {m['limit_mv']:.0f} mV (S17, ADAMAS) | A_VT = {m['avt_put_in_mv_um']:.0f} mV·µm | A_VT {m['avt_mv_um']:.0f} mV·µm; σ(4/2) {m['s_mv']:.0f} mV, bound {m['upper_mv']:.0f} mV | {yes(m['pass'])} | {pct(rates['matching'])} |
| Mobility | within kσ of {e['mu_model']:g} cm²/V·s (model) | {e['mu_model']:g} | {e['mu']:.1f} ± {e['mu_err']:.1f} | {yes(e['mu_pass'])} | {pct(rates['mu'])} |
| Threshold | within kσ of {e['vt_model']:g} V (model) | {e['vt_model']:g} V | {e['vt']:.3f} ± {e['vt_err']:.3f} V | {yes(e['vt_pass'])} | {pct(rates['vt'])} |
| **Gate: every row passes** | | | | **{yes(g['verdict'] == 'go')}** | **{pct(rates['gate'])}** |

The degraded twins, one process fault each. The last column is how often the faulty run wrongly passes.

| Test | Fault | Measured | Pass? | Faulty runs passing |
|---|---|---|---|---|
| Contact resistance | residue under the gold contacts (R_c = {P4_RC_BAD_OHM_MM:g} Ω·mm) | {bt['rc_ohm_mm']:.1f} ± {bt['rc_err']:.1f} Ω·mm | {yes(bt['pass'])} | {pct(rates['degraded']['tlm'])} |
| Threshold matching | patchy hydrogen termination (A_VT = {bm['avt_put_in_mv_um']:.0f} mV·µm) | σ(4/2) {bm['s_mv']:.0f} mV, bound {bm['upper_mv']:.0f} mV | {yes(bm['pass'])} | {pct(rates['degraded']['matching'])} |
| Mobility and threshold | Al₂O₃ {P4_TOX_BAD_NM:g} nm thick, analysis assumes 30 nm | µ {be['mu']:.1f} ± {be['mu_err']:.1f} cm²/V·s, V_T {be['vt']:.3f} V | {yes(be['mu_pass'] and be['vt_pass'])} | {pct(rates['degraded']['extraction'])} |

{_p4_rates_note(rates)}

A failed mobility or threshold check on real devices says the device and the model disagree. The MOS capacitor tells you which: if C_ox matches 30 nm of Al₂O₃, the mobility is really different, and the model should be recalibrated with the measured value (C2, step 4); if not, the oxide is off.

A thicker oxide in a real device also moves V_T (through the oxide charge); the twin changes only C_ox, so the threshold check is not what catches it.

The sheet-resistance window is the one traveler step S08 sets for the bare hydrogen-terminated surface in air, reused here for the finished channel under Al₂O₃ without nitrogen dioxide (NO₂). With the NO₂ option (S12) the expected sheet resistance is 0.5 to 5 kΩ/sq, so use that window instead.

## Not yet simulated

- **Hot operation** (traveler S17 tests at 25, 200 and 300 °C [kawarada2014]): the FET model has no temperature dependence yet.
- **Breakdown** (Atlas M18): the breakdown field versus dislocation density has a proposed fit in `adamas.power`, but no simulated test structure here.
- **On/off ratio** (S17: at least 10⁶) and **ring-oscillator delay** (S17: within a factor of 2 of the model): no noise model for the off current or the oscillator yet.
- **Photoelectric NV readout** (Atlas M55, listed in the outline for P4 and P6): belongs with the quantum track; P6 still assumes optical readout and lists the photoelectric chain as open ([STATUS.md](../STATUS.md)).

## Failure modes

- **Contact residue:** high R_c with a normal R_sh; keep the surface clean and the time short between hydrogen termination (S08) and the gold (S09).
- **Lost termination:** high R_sh everywhere, or patchy termination that shows as a large threshold spread; repeat the hydrogen plasma (S08) and store in clean nitrogen.
- **Oxide thickness off:** mobility off by the oxide ratio; measure C_ox on the MOS capacitor and check the ALD cycle count.
- **Threshold drift during hot tests:** mobile charge or NO₂ desorption (traveler S17); use the high-temperature oxide option for hot operation.

## Decision gate

*Do our devices match the models, and is the process stable from run to run?* {verdict} Run-to-run stability needs at least two runs through the same checks; go to P6 when both runs pass and the measured mobility and threshold have been entered into the models.

Sources: [sze2006] [pelgrom1989] [kawarada2014] [kawarada2023] [kasu2012] [liu2017]
"""


# ---------------------------------------------------------------- P5 ------------------------------------------------
P5_CHECKS = 3                # conversion yield, coupled pairs, Bell fidelity: the gate needs all of them
P5_GATE_COVERAGE = 0.95
P5_TEST_COVERAGE = P5_GATE_COVERAGE ** (1 / P5_CHECKS)     # so each check covers 98.30 %
P5_RUNS = 1000
# Sourced values: conversion yield about 1 % at 2.5 to 5 keV and the 0.5 % acceptance limit (traveler S07, [pezzagna2010]);
# the published room-temperature Bell fidelity 0.67 [dolde2013]; the 5 to 120 kHz coupling window of experiment D1.
# Everything else is illustrative and labeled so.
P5_ETA = 0.01                # nitrogen-to-NV conversion yield put in (S07: about 1 % at 2.5 to 5 keV [pezzagna2010])
P5_ETA_MIN = 0.005           # S07 acceptance: yield at least 0.5 % (an ADAMAS target, set from the about 1 % reported in [pezzagna2010])
P5_ETA_BAD = 0.002           # degraded twin: residual oxygen etched the surface during the anneal (S07 failure mode; illustrative value)
P5_WITNESS_SITES = 200       # witness (calibration) array: apertures counted by confocal microscopy (illustrative)
P5_WITNESS_IONS = 50         # ions per witness aperture (illustrative; local fluence about 1.6e13 cm^-2, see p5_local_fluence_cm2)
P5_PAIR_SITES = 1000         # pair field: apertures searched for coupled pairs (illustrative)
P5_PAIR_IONS = 50            # ions per pair aperture (illustrative)
P5_ENERGY_KEV = 5.0          # implant energy, inside the S06 window of 2.5 to 10 keV
P5_APERTURE_NM = 20.0        # aperture diameter, inside the S06 window of 10 to 60 nm (illustrative)
P5_APERTURE_BAD_NM = 120.0   # degraded twin: PMMA over-developed, apertures outside the S06 window
P5_WINDOW_KHZ = (5.0, 120.0) # couplings kept for gates (experiment D1)
P5_BELL_F = 0.67             # Bell-state fidelity put in: the published room-temperature value [dolde2013]
P5_POP_NOISE = 0.03          # error of the measured population sum p00 + p11 (illustrative)
P5_PARITY_NOISE = 0.06       # per point of the parity oscillation, 16 analysis phases (illustrative)
P5_PARITY_PHASES = 16
NV_AXIS = np.array([1.0, 1.0, 1.0]) / math.sqrt(3)         # [111]; the implant comes in along [001]


def p5_local_fluence_cm2(ions: int = P5_PAIR_IONS, aperture_nm: float = P5_APERTURE_NM) -> float:
    """Ions per aperture area. 50 ions through 20 nm is about 1.6e13 cm^-2: above S06's 1e8 to 1e11 cm^-2 for single
    centers and at its ensemble ceiling (1e13), so the about 1 % yield of [pezzagna2010] is extrapolated to this fluence."""
    return ions / (math.pi * (aperture_nm * 1e-7 / 2) ** 2)


def _k5() -> float:
    return _k_normal(P5_TEST_COVERAGE)


def _k5_one_sided() -> float:
    from scipy.stats import norm
    return float(norm.ppf(P5_TEST_COVERAGE))


def _rng5(seed: int, test: int) -> np.random.Generator:
    """Independent stream per test (0 witness array, 1 pair field, 2 Bell tomography); a twin reuses its test's stream."""
    return np.random.default_rng([seed, 5, test])


def p5_yield(seed: int = 5, eta: float = P5_ETA) -> dict:
    """Witness array (traveler S06, S07): P5_WITNESS_SITES apertures with P5_WITNESS_IONS ions each; each ion becomes an NV
    with probability eta, so NVs per aperture are binomial. Confocal counting (with the antibunching test of P3 to tell
    one, two or three NVs apart) gives eta_hat = NVs / ions. Pass when the one-sided Clopper-Pearson lower bound at the
    per-check coverage is at least 0.5 % (S07 [pezzagna2010]). Assumes every NV in an aperture is counted and native
    nitrogen is told apart by the ¹⁵N hyperfine lines (S06)."""
    from scipy.stats import beta
    counts = _rng5(seed, 0).binomial(P5_WITNESS_IONS, eta, P5_WITNESS_SITES)
    n, x = P5_WITNESS_SITES * P5_WITNESS_IONS, int(counts.sum())
    lo = float(beta.ppf(1 - P5_TEST_COVERAGE, x, n - x + 1)) if x > 0 else 0.0
    return {"eta_put_in": eta, "counts": counts.tolist(), "nv": x, "ions": n, "eta": x / n, "eta_err": math.sqrt(max(x, 1) * (n - x) / n) / n,
            "eta_lower": lo, "limit": P5_ETA_MIN, "pass": bool(lo >= P5_ETA_MIN)}


def _pair_geometry(rng: np.random.Generator, size: int, aperture_nm: float) -> np.ndarray:
    """Separation vectors (nm) of two ions through one aperture: uniform on the aperture disc in the surface plane, plus
    Gaussian straggle in all three axes with the rule-of-thumb sigma of adamas.coupling (0.4 x depth at P5_ENERGY_KEV)."""
    from .coupling import implant_rule_of_thumb
    _, sig = implant_rule_of_thumb(P5_ENERGY_KEV)
    def one():
        rad = aperture_nm / 2 * np.sqrt(rng.random(size)); ang = 2 * np.pi * rng.random(size)
        return np.stack([rad * np.cos(ang), rad * np.sin(ang), np.zeros(size)], 1) + rng.normal(0, sig, (size, 3))
    return one() - one()


def pair_couplings_khz(sep_nm: np.ndarray) -> np.ndarray:
    """Secular dipolar coupling 52 MHz nm^3 |1 - 3 cos^2 theta| / r^3 (adamas.coupling), theta between the separation
    and a common [111] quantization axis. An approximation: NVs on different axes change the angular factor."""
    from .coupling import dipolar_coupling_khz
    r = np.linalg.norm(sep_nm, axis=1); cos = np.abs(sep_nm @ NV_AXIS) / r
    return np.asarray(dipolar_coupling_khz(r, np.arccos(np.clip(cos, 0, 1))), float)


@lru_cache(maxsize=8)
def p5_window_fraction(aperture_nm: float = P5_APERTURE_NM, samples: int = 200_000) -> float:
    """Probability that a two-NV aperture has its coupling inside the D1 window (fixed-seed Monte Carlo)."""
    c = pair_couplings_khz(_pair_geometry(np.random.default_rng(55), samples, aperture_nm))
    return float(np.mean((c >= P5_WINDOW_KHZ[0]) & (c <= P5_WINDOW_KHZ[1])))


def _p_two(eta: float, n: int = P5_PAIR_IONS) -> float:
    return math.comb(n, 2) * eta ** 2 * (1 - eta) ** (n - 2)


def p5_pairs(seed: int = 5, aperture_nm: float = P5_APERTURE_NM, eta: float = P5_ETA, eta_measured: dict | None = None) -> dict:
    """Pair field: P5_PAIR_SITES apertures with P5_PAIR_IONS ions each. Apertures with exactly two NVs are candidates;
    a double electron-electron resonance (DEER) measurement gives each candidate's coupling, and pairs inside the D1
    window (5 to 120 kHz) are kept. The prediction uses the yield MEASURED on the witness array of the same run and the
    designed aperture: N_pred = M P2(eta_hat) f_window, with P2 the binomial probability of exactly two NVs. Pass when at
    least one pair is found and N_found lies within k sigma of N_pred (binomial counting error plus the yield's error,
    propagated). Assumes couplings are measured exactly (DEER resolution far finer than the window). The degraded twin's
    apertures are P5_APERTURE_BAD_NM wide while the analysis assumes the design."""
    w = eta_measured or p5_yield(seed)
    r = _rng5(seed, 1)
    nv = r.binomial(P5_PAIR_IONS, eta, P5_PAIR_SITES); two = int(np.sum(nv == 2))
    coup = pair_couplings_khz(_pair_geometry(r, two, aperture_nm)) if two else np.array([])
    found = coup[(coup >= P5_WINDOW_KHZ[0]) & (coup <= P5_WINDOW_KHZ[1])]
    f = p5_window_fraction(); e, e_err = w["eta"], w["eta_err"]
    p = _p_two(e) * f; pred = P5_PAIR_SITES * p
    h = 1e-6; dp = (_p_two(e + h) - _p_two(e - h)) / (2 * h) * f * P5_PAIR_SITES
    sig = math.sqrt(P5_PAIR_SITES * p * (1 - p) + (dp * e_err) ** 2)
    k = _k5()
    return {"aperture_nm": aperture_nm, "two_nv_sites": two, "couplings_khz": coup.tolist(), "found": int(found.size),
            "found_khz": sorted(found.tolist(), reverse=True), "window_fraction": f, "predicted": pred, "predicted_err": sig, "k": k,
            "pass": bool(found.size >= 1 and abs(found.size - pred) <= k * sig)}


def parity_after_analysis(rho: np.ndarray, phi: float) -> float:
    """<Z1 Z2> after a pi/2 analysis pulse of phase phi on each NV, U = exp(-i pi/4 (cos phi X + sin phi Y)). Its cos 2phi
    part is -2 Re rho(00,11), so A = -2 <P cos 2phi> over equally spaced phases and F = (p00 + p11 + A)/2 is the exact
    fidelity with |Phi+> for any two-qubit state (tests/test_build_program.py checks it on random states)."""
    from .entangle import X, Y, Z
    c, s = math.cos(math.pi / 4), math.sin(math.pi / 4)
    u = c * np.eye(2) - 1j * s * (math.cos(phi) * X + math.sin(phi) * Y); w = np.kron(u, u)
    return float(np.trace(w @ rho @ w.conj().T @ np.kron(Z, Z)).real)


def bell_fidelity_estimate(pop: float, phi, parity) -> tuple[float, float]:
    """(F, A) from the population sum and the parity at equally spaced phases over [0, pi)."""
    a = float(-2 * np.mean(np.asarray(parity) * np.cos(2 * np.asarray(phi))))
    return (pop + a) / 2, a


def bell_tomography_expected(f: float) -> tuple[float, float]:
    """Population sum p00 + p11 and parity amplitude A of a Bell pair mixed with white noise (a Werner state, as in
    adamas.entangle) of fidelity F: visibility v = (4F - 1)/3, p00 + p11 = (1 + v)/2, A = v, and F = (p00 + p11 + A)/2."""
    v = (4 * f - 1) / 3
    return (1 + v) / 2, v


def p5_bell(seed: int = 5, f_true: float | None = P5_BELL_F, pairs: dict | None = None) -> dict:
    """Bell-state tomography on the strongest coupled pair found (gate time 1 / (2 nu)): measure the population sum with
    error P5_POP_NOISE, and the parity oscillation P(phi) = -A cos(2 phi) (parity_after_analysis) over P5_PARITY_PHASES analysis
    phases with P5_PARITY_NOISE per point; A comes from the cos 2phi component (the phase reference is fixed by the sequence). F = (p00 + p11 + A)/2. Pass when
    F - k sigma > 1/2 (one-sided): a fidelity with a Bell state above 1/2 proves entanglement, because no separable
    state exceeds 1/2 (tests/test_build_program.py checks this numerically). Charge-state pre-selected runs, as in
    experiment D1. f_true=None is the degraded twin: the 'pair' is not coupled, so the gate leaves at most classical
    correlations; the twin uses the best such state, 1/2 (|00><00| + |11><11|), which has p00 + p11 = 1, A = 0, F = 1/2."""
    pairs = pairs or p5_pairs(seed)
    if f_true is not None and not pairs["found"]:
        return {"pair_khz": None, "gate_us": None, "f": None, "f_err": None, "pass": False, "f_put_in": f_true}
    nu = pairs["found_khz"][0] if pairs["found"] else None
    pop, amp = (1.0, 0.0) if f_true is None else bell_tomography_expected(f_true)
    r = _rng5(seed, 2)
    pop_m = pop + r.normal(0, P5_POP_NOISE)
    phi = np.linspace(0, np.pi, P5_PARITY_PHASES, endpoint=False)
    par = -amp * np.cos(2 * phi) + r.normal(0, P5_PARITY_NOISE, phi.size)    # parity_after_analysis of the state, plus noise
    f, a = bell_fidelity_estimate(pop_m, phi, par)       # fixed phase reference: a free-phase fit, sqrt(c^2 + s^2), is biased upward near A = 0
    a_err = P5_PARITY_NOISE * math.sqrt(2 / phi.size); f_err = 0.5 * math.hypot(P5_POP_NOISE, a_err)
    k = _k5_one_sided()
    return {"pair_khz": nu, "gate_us": (1e3 / (2 * nu)) if nu else None, "f_put_in": 0.5 if f_true is None else f_true,
            "pop": float(pop_m), "amp": float(a), "phi": phi.tolist(), "parity": par.tolist(), "f": float(f), "f_err": float(f_err), "k": k,
            "pass": bool(f - k * f_err > 0.5)}


def p5_gate(seed: int = 5) -> dict:
    y = p5_yield(seed); p = p5_pairs(seed, eta_measured=y); b = p5_bell(seed, pairs=p)
    ok = y["pass"] and p["pass"] and b["pass"]
    return {"yield": y, "pairs": p, "bell": b, "verdict": "go" if ok else "stop"}


def p5_degraded(seed: int = 5) -> dict:
    """Each test on its degraded twin (one fault each); every one must fail."""
    return {"yield": p5_yield(seed, eta=P5_ETA_BAD), "pairs": p5_pairs(seed, aperture_nm=P5_APERTURE_BAD_NM), "bell": p5_bell(seed, f_true=None)}


def p5_pass_rates(runs: int = P5_RUNS) -> dict:
    """Pass rates over simulated runs (seeds 5000 + i) for correct setups, and wrong-pass rates for the degraded twins."""
    keys = ("yield", "pairs", "bell"); c = dict.fromkeys(keys + ("gate",), 0); d = dict.fromkeys(keys, 0)
    for i in range(runs):
        g = p5_gate(5000 + i); b = p5_degraded(5000 + i)
        for k in keys:
            c[k] += g[k]["pass"]; d[k] += b[k]["pass"]
        c["gate"] += g["verdict"] == "go"
    out = {k: v / runs for k, v in c.items()}
    out["degraded"] = {k: v / runs for k, v in d.items()}
    out.update(runs=runs, k=_k5(), k_one=_k5_one_sided(), se_test=math.sqrt(P5_TEST_COVERAGE * (1 - P5_TEST_COVERAGE) / runs),
               se_gate=math.sqrt(P5_GATE_COVERAGE * (1 - P5_GATE_COVERAGE) / runs))
    return out


def p5_bill() -> dict:
    """Parts and price range for P5: the D1 part list (estimates from adamas.experiments, not quotes). The annealing
    furnace (Atlas M22) and SIMS (M23) are rented by the hour; their rates are in adamas.atlas_prices."""
    from .experiments import EXPERIMENTS
    by = {e["id"]: e for e in EXPERIMENTS}
    rows = [("D1", *p) for p in by["D1"]["parts"]]
    return {"rows": rows, "low": sum(r[3] for r in rows), "high": sum(r[4] for r in rows), "headline": by["D1"]["cost"], "unpriced": ["M22", "M23"]}


P5_MACHINES = ("M08", "M10", "M12", "M20", "M21", "M22", "M23", "M24", "M47", "M51", "M52", "M54")


def p5_figure(out: str | Path = "docs/img") -> Path:
    """Figure 58: expected P5 results (nominal and degraded twin), simulated and analyzed here."""
    import matplotlib.pyplot as plt
    from scipy.stats import binom
    from .figures import COLORS, INK, RED, _finish
    out = Path(out); g, b = p5_gate(), p5_degraded()
    fig, ax = plt.subplots(1, 3, figsize=(19, 4.8)); plt.subplots_adjust(wspace=.3)
    a = ax[0]; kk = np.arange(0, 5)
    for r, col, off, lab in ((g["yield"], COLORS["Diamond"], -0.18, "good anneal"), (b["yield"], RED, 0.18, "etched surface (twin)")):
        h = np.bincount(r["counts"], minlength=5)[:5]
        a.bar(kk + off, h, width=0.36, color=col, alpha=.85, label=f"{lab}: η = {100 * r['eta']:.2f} %, bound {100 * r['eta_lower']:.2f} %")
    a.plot(kk, P5_WITNESS_SITES * binom.pmf(kk, P5_WITNESS_IONS, P5_ETA), "k_", ms=22, mew=2, label=f"expected, η = {100 * P5_ETA:g} %")
    a.set_ylim(0, 1.5 * P5_WITNESS_SITES); a.legend(fontsize=8, loc="upper right", borderaxespad=0.3); a.set_xticks(kk)
    a.set_title(f"1. Conversion yield: pass when the lower bound ≥ {100 * P5_ETA_MIN:g} % (S07)", fontsize=10.5)
    a.set_xlabel(f"NV centers per aperture ({P5_WITNESS_IONS} ions each)"); a.set_ylabel(f"apertures (of {P5_WITNESS_SITES})")
    a = ax[1]; bins = np.logspace(-3, 4, 43)
    for r, col, lab in ((g["pairs"], COLORS["Diamond"], f"{P5_APERTURE_NM:g} nm apertures"), (b["pairs"], RED, f"{P5_APERTURE_BAD_NM:g} nm apertures (degraded twin)")):
        a.hist(np.clip(r["couplings_khz"], 1.01e-3, 1e4), bins=bins, histtype="step", lw=2, color=col,
               label=f"{lab}: {r['found']} in window, {r['predicted']:.0f} ± {r['predicted_err']:.0f} predicted")
    a.axvspan(*P5_WINDOW_KHZ, color=COLORS["Diamond"], alpha=.08); a.set_xscale("log")
    a.set_ylim(0, 1.45 * a.get_ylim()[1])
    a.legend(fontsize=8, loc="upper left"); a.set_title("2. Coupled pairs: found within kσ of the prediction", fontsize=10.5)
    a.set_xlabel("dipolar coupling of two-NV apertures (kHz; first bin: 0.001 or less); shaded: kept (D1)"); a.set_ylabel("apertures")
    a = ax[2]; phi = np.array(g["bell"]["phi"]); xx = np.linspace(0, np.pi, 200)
    for r, col, lab in ((g["bell"], COLORS["Diamond"], "coupled pair"), (b["bell"], RED, "uncoupled pair, classical correlations (degraded twin)")):
        a.plot(phi, r["parity"], "o", ms=5, color=col)
        a.plot(xx, -r["amp"] * np.cos(2 * xx), color=col, lw=1.8, label=f"{lab}: F = {r['f']:.3f} ± {r['f_err']:.3f}")
    a.axhline(0, color=INK, lw=.6); a.legend(fontsize=8, loc="lower left"); a.set_ylim(-1, 1)
    a.set_title("3. Bell fidelity: pass when F − kσ > 1/2 (entanglement proved)", fontsize=10.5)
    a.set_xlabel("analysis phase φ (rad)"); a.set_ylabel("parity ⟨Z₁Z₂⟩ after the analysis pulses")
    return _finish(fig, out, "fig58_build_p5.png", "simulated by adamas.build_program (illustrative inputs except the sourced yield and fidelity); [pezzagna2010] [dolde2013]")


def _p5_rates_note(rates: dict) -> str:
    """The sentences under the P5 pass/fail table, written from the computed rates."""
    design = P5_TEST_COVERAGE; se = rates["se_test"]; out = []
    for key, name in (("yield", "yield"), ("pairs", "pair-search"), ("bell", "Bell")):
        v = rates[key]
        word = "more often than" if v > design + 3 * se else "less often than" if v < design - 3 * se else "about as often as"
        out.append(f"the {name} check passes correct runs {word} designed ({100 * v:.1f} %)")
    text = "Against the {:.2f} % design per check: ".format(100 * design) + "; ".join(out) + ". "
    text += (f"With these inputs the yield and Bell checks sit far from their limits ({100 * P5_ETA:g} % against {100 * P5_ETA_MIN:g} %, a fidelity of {P5_BELL_F} against 1/2), "
             "so the pair-search check sets the gate rate. ")
    alpha = 1 - design; tw = rates["degraded"]["bell"]; se_a = math.sqrt(alpha * design / rates["runs"])
    text += (f"The Bell twin sits exactly on the limit (F = 1/2), so by construction it passes at the one-sided rate {100 * alpha:.1f} %; "
             f"over these runs it passed {100 * tw:.1f} %, " + ("within three standard errors of that. " if abs(tw - alpha) <= 3 * se_a else "more than three standard errors away: check the noise model. ") +
             "A real pair just above 1/2 would also fail often: the test proves entanglement only when the fidelity clears 1/2 by a few standard errors. ")
    text += (f"Over {rates['runs']} runs the gate passes {100 * rates['gate']:.1f} % of correct runs" +
             (", at least the 95 % it is designed for." if rates["gate"] >= P5_GATE_COVERAGE - 3 * rates["se_gate"] else ", below the 95 % it is designed for: the tolerances need widening."))
    return text


def _p5_md() -> str:
    from . import atlas, atlas_prices, gate_budget
    from .coupling import implant_rule_of_thumb
    from .experiments import EXPERIMENTS
    from .traveler import STEPS
    by = {e["id"]: e for e in EXPERIMENTS}; st = {s["id"]: s for s in STEPS}
    g, b, bill, rates = p5_gate(), p5_degraded(), p5_bill(), p5_pass_rates(P5_RUNS)
    y, p, be = g["yield"], g["pairs"], g["bell"]; by_, bp, bb = b["yield"], b["pairs"], b["bell"]
    yes = lambda v: "yes" if v else "no"   # noqa: E731
    pct = lambda v: f"{100 * v:.1f} %"   # noqa: E731
    depth, strag = implant_rule_of_thumb(P5_ENERGY_KEV)
    lo, hi = gate_budget.coherence_limited_range()
    parts = {"Implantation": "M20, M21", "Confocal setups": "M47, M54", "Control electronics": "M51", "Materials": "M52"}
    rows = "\n".join(f"| {parts.get(r[1], '(not in the Atlas)')} | {r[1]} (D1) | {r[2]} | {r[3]:,} to {r[4]:,} |" for r in bill["rows"])
    use = {"M22": "vacancy anneal (S07)", "M23": "implant depth profile (S06)"}
    rows += "\n" + "\n".join(f"| {k} | {atlas.tool(k)} | {use[k]} | {atlas_prices.short_price(k)} |" for k in bill["unpriced"])
    machines = ", ".join(f"{k} {atlas.tool(k)}" for k in P5_MACHINES).replace("CVD diamond", "chemical vapor deposition (CVD) diamond")
    steps = "\n".join(f"{i + 1}. **{s[0]}.** {s[1]}" for i, s in enumerate(by["D1"]["steps"]))
    hazards = " ".join(dict.fromkeys([h for sid in ("S02", "S06", "S07", "S18") for h in st[sid]["safety"] if not h.startswith("As ")] + by["D1"]["safety"]))
    pair_txt = f"{be['pair_khz']:.1f} kHz, gate time 1/(2ν) = {be['gate_us']:.1f} µs" if be["pair_khz"] else "none found"
    verdict = ("All simulated checks pass and every degraded twin fails, so the analysis can tell a good run from a faulty one; the gate is decided by the numbers measured on your sample."
               if g["verdict"] == "go" and not (by_["pass"] or bp["pass"] or bb["pass"])
               else "On this run a simulated check fails or a degraded twin passes; a correct run fails about one time in twenty, so repeat it before changing the analysis.")
    text = f"""# P5 · Placement: implanted NV pairs, coupled and entangled

{GEN}

**Status: written in full.** Budget: **US${bill['low']:,} to {bill['high']:,}** for the D1 parts listed below (estimates from the experiment list, not quotes). The annealing furnace and secondary-ion mass spectrometry (SIMS) are rented by the hour in a shared facility; the table gives published hourly rates, which are not added to the total because the hours are not modelled. Gate verdict in simulation: **{g['verdict']}**.

Sourced inputs: the conversion yield put in ({100 * P5_ETA:g} %) come from [pezzagna2010], and its acceptance limit ({100 * P5_ETA_MIN:g} %, traveler step S07) is an ADAMAS target set from it; the Bell-state fidelity put in ({P5_BELL_F}) is the published room-temperature value for an NV pair [dolde2013]; the 5 to 120 kHz coupling window is experiment D1's. Every other input (aperture counts, ions per aperture, noise levels) is **illustrative**. The phase is **simulated**: no ADAMAS hardware has run it.

## Goal

Place nitrogen-vacancy (NV) centers with nanometre control: implant ¹⁵N through apertures (traveler S06), anneal so vacancies find the nitrogen (S07), count how many ions became NV centers, find apertures that hold exactly two NVs coupled strongly enough for a two-qubit gate, and entangle one such pair at room temperature. P5 answers whether placement is good enough to plan arrays (P6).

## Physics and equations

- **Conversion yield η:** each implanted nitrogen becomes an NV with probability η, so an aperture with n ions holds k NVs with the binomial probability C(n,k) η^k (1 − η)^(n−k). Counting NVs on a witness array of M apertures gives η̂ = (NVs counted)/(M n); its one-sided Clopper–Pearson lower bound at the per-check coverage is compared with the S07 limit. About 1 % is reported at 2.5 to 5 keV, rising with energy [pezzagna2010]. Valid when every NV in an aperture is counted (confocal counting: brightness steps calibrated on single NVs, with antibunching from P3 to confirm single centers; two versus three is the least certain count) and implanted ¹⁵N is told from native ¹⁴N by its hyperfine lines.
- **Where the ions stop:** at {P5_ENERGY_KEV:g} keV the rule of thumb of `adamas.coupling` gives a depth of about {depth:.1f} nm with {strag:.1f} nm straggle, per axis [pezzagna2010] [oforiokai2012]; replace it with a run of SRIM (the Stopping and Range of Ions in Matter code) [ziegler2010] for design work (channeling makes real profiles deeper). Each ion enters at a uniformly random point of a {P5_APERTURE_NM:g} nm aperture. {P5_PAIR_IONS} ions per aperture is a local fluence of about {p5_local_fluence_cm2():.1e} cm⁻², above S06's range for single centers and at its ensemble ceiling, so the {100 * P5_ETA:g} % yield is extrapolated to this fluence (an assumption to check on the witness array).
- **Coupling:** two NVs at separation r couple with ν = 52 MHz·nm³ |1 − 3cos²θ| / r³ [neumann2010natphys] [dolde2013], θ between the separation and the quantization axis (taken here as [111] for both; NVs on different axes, as experiment D1 selects for addressing, change the angular factor). A controlled-phase gate takes 1/(2ν). Each candidate's coupling is measured by double electron–electron resonance (DEER), and pairs between 5 and 120 kHz are kept (experiment D1's window).
- **Pair count:** an aperture with n ions holds exactly two NVs with P₂ = C(n,2) η² (1 − η)^(n−2), and a fraction f of such pairs falls in the window (Monte Carlo over the geometry above; f = {p['window_fraction']:.3f} for the design). The expected number of usable pairs in M apertures is N = M P₂ f, computed with the yield **measured** on the witness array of the same run; its error combines binomial counting and the yield's error, so the yield and pair checks are correlated.
- **Bell fidelity:** after the gate, measure the populations p00 + p11 and the parity ⟨Z₁Z₂⟩ after a π/2 analysis pulse of phase φ on each NV. Its cos 2φ part is −A cos 2φ with A = 2 Re ρ(00,11), so F = (p00 + p11 + A)/2 is the exact fidelity with the Bell state |Φ⁺⟩ for any two-qubit state (a test checks it on random states). A fidelity above 1/2 proves entanglement: no unentangled (separable) state reaches more than 1/2 with a Bell state, which a test checks numerically. The simulated state is a Bell pair mixed with white noise (a Werner state, as in `adamas.entangle`); real errors are not white, but the estimator does not depend on that.

## Machines and consumables

Atlas machines for this phase: {machines}. Optional: M25 (laser writing of vacancies) to raise the yield, and M08 for photoluminescence maps of the witness array.

| Atlas | Part (experiment) | Specification | US$ |
|---|---|---|---|
{rows}

## Facility and safety

A shared ion-beam facility with a low-energy implanter, an electron-beam lithography tool for the aperture mask, a high-vacuum furnace, a wet bench, and a confocal microscope with microwave control. {hazards} Ion implanters, furnaces, strong acids and Class 3B/4 lasers each need your institution's specific training and sign-off before first use; this page does not replace that training.

## Procedure

Traveler steps S06 (implant through apertures) and S07 (anneal, tri-acid clean, oxygen termination), then D1:

{steps}

On the sample, keep two fields side by side: a **witness array** ({P5_WITNESS_SITES} apertures, {P5_WITNESS_IONS} ions each) that is only counted, and a **pair field** ({P5_PAIR_SITES} apertures, {P5_PAIR_IONS} ions each) that is searched for coupled pairs. Count the witness array first, so its yield is available when you predict the pair count.

## Expected results (simulated)

Each test is shown with its **degraded twin**: the same simulation with one fault, which the test must catch.

![Expected P5 results](../img/fig58_build_p5.png)

## Pass/fail

The gate needs all {P5_CHECKS} checks to pass, so each is set for {100 * P5_TEST_COVERAGE:.2f} % coverage: the yield check uses the exact Clopper–Pearson quantile, the Bell check k = {rates['k_one']:.2f} (one-sided) and the pair count k = {rates['k']:.2f} (two-sided). Rates are over {rates['runs']} simulated runs (binomial standard error at the design rate: {100 * rates['se_test']:.1f} percentage points per check, {100 * rates['se_gate']:.1f} for the gate).

| Check | Criterion | Put in | Measured | Pass? | Correct runs passing |
|---|---|---|---|---|---|
| Conversion yield (witness array) | lower bound ≥ {100 * P5_ETA_MIN:g} % (S07, ADAMAS target) | η = {100 * y['eta_put_in']:g} % | {y['nv']} NVs from {y['ions']:,} ions: {100 * y['eta']:.2f} ± {100 * y['eta_err']:.2f} %, bound {100 * y['eta_lower']:.2f} % | {yes(y['pass'])} | {pct(rates['yield'])} |
| Coupled pairs (pair field) | at least 1 found, and within kσ of the prediction | design aperture {P5_APERTURE_NM:g} nm | {p['two_nv_sites']} two-NV apertures, {p['found']} in the window; predicted {p['predicted']:.1f} ± {p['predicted_err']:.1f} | {yes(p['pass'])} | {pct(rates['pairs'])} |
| Bell fidelity (strongest pair: {pair_txt}) | F − kσ > 1/2 | F = {be['f_put_in']} [dolde2013] | {'not measured' if be['f'] is None else f"{be['f']:.3f} ± {be['f_err']:.3f}"} | {yes(be['pass'])} | {pct(rates['bell'])} |
| **Gate: every row passes** | | | | **{yes(g['verdict'] == 'go')}** | **{pct(rates['gate'])}** |

The degraded twins, one fault each. The last column is how often the faulty run wrongly passes.

| Test | Fault | Measured | Pass? | Faulty runs passing |
|---|---|---|---|---|
| Conversion yield | residual oxygen etched the surface during the anneal (S07 failure mode; η = {100 * P5_ETA_BAD:g} %, illustrative) | {100 * by_['eta']:.2f} %, bound {100 * by_['eta_lower']:.2f} % | {yes(by_['pass'])} | {pct(rates['degraded']['yield'])} |
| Coupled pairs | the poly(methyl methacrylate) (PMMA) resist over-developed: apertures {P5_APERTURE_BAD_NM:g} nm, outside the S06 window of 10 to 60 nm | {bp['found']} in the window, {bp['predicted']:.1f} ± {bp['predicted_err']:.1f} predicted | {yes(bp['pass'])} | {pct(rates['degraded']['pairs'])} |
| Bell fidelity | the "pair" is not coupled: at best classical correlations, F = 1/2 | {bb['f']:.3f} ± {bb['f_err']:.3f} | {yes(bb['pass'])} | {pct(rates['degraded']['bell'])} |

{_p5_rates_note(rates)}

The simulation puts in the published fidelity rather than computing it. The coherence-limited budget of `adamas.gate_budget` gives {lo:.2f} to {hi:.2f} for the published pair, above the measured 0.67: a known discrepancy carried here from P0 ([VALIDATION.md](../VALIDATION.md)). P5 is where it gets measured: compare your fidelity with the budget for your pair's coupling and coherence times, and attribute the gap (D1, step 5).

## Not yet simulated

- **Depth-dependent coherence:** shallow NVs lose coherence to surface spins [oforiokai2012]; S07 asks for an echo T₂ of at least 10 µs (an ADAMAS target), and the budget needs the measured value.
- **Charge state:** the Bell check assumes charge-state pre-selected runs (D1, step 3). Without pre-selection an unprepared fraction 1 − q² of runs drags the fidelity toward 1/4 (`adamas.gate_budget`).
- **Addressing:** pairs on the same crystal axis cannot be driven one at a time (Addressing Lab); the pair search here does not reject them.
- **Deterministic placement** (laser writing, M25; single-ion detection): not modelled.

## Failure modes

- **Low yield, dark surface layer:** residual oxygen etched the surface during the anneal (S07); improve the vacuum or use forming gas.
- **Too few or too many NVs per aperture:** dose or aperture size off (S06); recalibrate on the witness array.
- **Pairs too far apart:** apertures wider than designed (check them by scanning electron microscopy, S06) or straggle larger than planned (deeper or channeled ions; SIMS).
- **Fidelity at or below 1/2:** weak coupling, short T₂ near the surface, pulse errors, or a mis-identified pair; repeat the coupling measurement and the coherence times before blaming the gate.

## Decision gate

*Is placement yield good enough to plan arrays?* {verdict} An array of N cells needs N usable pairs; with the measured yield and window fraction, about 1/(P₂ f) = {1 / (_p_two(y['eta']) * p['window_fraction']):.0f} apertures are searched per usable pair at this dose. That is optimistic: D1 also needs the two NVs on different axes so each can be driven alone, which for random orientations keeps 3 of 4 pairs (about {4 / 3 / (_p_two(y['eta']) * p['window_fraction']):.0f} apertures per pair), and the [111]-only angular factor is an approximation. That number, not the gate verdict alone, decides whether P6 plans arrays of aperture-implanted pairs or waits for deterministic placement.

Sources: SOURCES_LINE
"""
    import re
    keys = list(dict.fromkeys(re.findall(r"\[([a-z][a-z0-9]*\d{4}[a-z0-9]*)\]", text)))
    return text.replace("SOURCES_LINE", " ".join(f"[{k}]" for k in keys))


# ---------------------------------------------------------------- P6 ------------------------------------------------
P6_CHECKS = 3                # coherence kept through bonding, on-chip drive, repetition-code gain: the gate needs all three
P6_GATE_COVERAGE = 0.95
P6_TEST_COVERAGE = P6_GATE_COVERAGE ** (1 / P6_CHECKS)     # so each check covers 98.30 %
P6_RUNS = 1000
# Illustrative inputs: the echo and Rabi data reuse the B1 noise model of adamas.experiments (amplitude 0.1; 0.004 per Rabi point, and
# 0.0015 per echo point, which is B1's 0.003 averaged four times longer); the design Rabi frequency, its 5 % tolerance and the twin's half current are
# ADAMAS design values from Quantum Device Library entry QDL-27 (adamas.qdl), not sourced numbers. The coherence-loss limit and the repetition-code numbers are
# this project's choices, labeled ADAMAS or illustrative.
P6_T2_US = 300.0             # echo T2 before bonding (the B1 value of adamas.experiments.PULSED_TRUTH; illustrative)
P6_STRETCH = 1.5             # echo stretch exponent (B1 value; illustrative)
P6_ECHO_NOISE = 0.0015       # per echo point: four times B1's averaging, so half its noise (illustrative)
P6_T2_BAD_US = 150.0         # degraded twin: bonding damaged the diamond surface and halved T2 (illustrative)
P6_T2_RATIO_MIN = 0.8        # ADAMAS target: bonding may cost at most 20 % of T2 (one-sided lower bound of the ratio)
P6_RABI_DESIGN_MHZ = 10.0    # on-chip driver design Rabi frequency (ADAMAS design value, QDL-27)
P6_RABI_BAD_MHZ = 5.0        # degraded twin: the driver gives half the current (QDL-27 failure mode)
P6_RABI_TOL = 0.05           # QDL-27: within 5 % of the design value, including k sigma (an ADAMAS design threshold)
P6_RABI_DECAY_US = 0.8       # B1 value; illustrative
P6_P_INJECT = 0.25           # bit-flip probability injected on each qubit (illustrative; error injection is the method of [waldherr2014])
P6_F0 = 0.90                 # fidelity of encoding plus decoding through the chiplet (illustrative)
P6_F0_BAD = 0.70             # degraded twin: drive crosstalk from the chiplet spoils the encoding gates (illustrative)
P6_FID_NOISE = 0.01          # error of each measured fidelity (illustrative)


def _k6() -> float:
    return _k_normal(P6_TEST_COVERAGE)


def _k6_one_sided() -> float:
    from scipy.stats import norm
    return float(norm.ppf(P6_TEST_COVERAGE))


def _rng6(seed: int, test: int) -> np.random.Generator:
    """Independent stream per test (0 echo before, 1 echo after, 2 Rabi, 3 repetition code); twins reuse their streams."""
    return np.random.default_rng([seed, 6, test])


def _echo_data(rng: np.random.Generator, t2_us: float):
    te = np.linspace(0, 600, 61)
    return te, 0.1 * np.exp(-(te / t2_us) ** P6_STRETCH) + rng.normal(0, P6_ECHO_NOISE, te.size)


def p6_coherence(seed: int = 6, t2_after_us: float = P6_T2_US) -> dict:
    """Echo T2 of the same NV before bonding (external drive) and after (through the chiplet), each fitted with
    adamas.fitting.fit_echo (stretched exponential). Pass when the one-sided lower bound of T2_after / T2_before, ratio
    minus k sigma with the two fit errors propagated, is at least P6_T2_RATIO_MIN (an ADAMAS target). The degraded
    twin's bonding halves T2."""
    from . import fitting
    xb, yb = _echo_data(_rng6(seed, 0), P6_T2_US); xa, ya = _echo_data(_rng6(seed, 1), t2_after_us)
    fb, fa = fitting.fit_echo(xb, yb), fitting.fit_echo(xa, ya)
    tb, eb, ta, ea = fb.params["T2_us"], fb.errors["T2_us"], fa.params["T2_us"], fa.errors["T2_us"]
    ratio = ta / tb; r_err = ratio * math.hypot(ea / ta, eb / tb); k = _k6_one_sided()
    return {"t2_before_us": tb, "t2_before_err": eb, "t2_after_us": ta, "t2_after_err": ea, "t2_after_put_in": t2_after_us,
            "ratio": ratio, "ratio_err": r_err, "ratio_lower": ratio - k * r_err, "limit": P6_T2_RATIO_MIN, "k": k,
            "x": xa.tolist(), "y_before": yb.tolist(), "y_after": ya.tolist(), "pass": bool(ratio - k * r_err >= P6_T2_RATIO_MIN)}


def p6_drive(seed: int = 6, rabi_mhz: float = P6_RABI_DESIGN_MHZ) -> dict:
    """Rabi oscillation driven by the chiplet's on-chip microwave driver, fitted with adamas.fitting.fit_rabi. Pass when
    |Omega - Omega_design| + k sigma <= 5 % of the design (the QDL-27 criterion), with the one-sided k so that a driver
    exactly at either limit passes at most 1 - P6_TEST_COVERAGE of the time, as in the other two checks. The degraded twin's driver gives half
    the current, so half the Rabi frequency."""
    from . import fitting
    t = np.linspace(0, 1.0, 101)
    y = 0.05 * (1 - np.cos(2 * np.pi * rabi_mhz * t) * np.exp(-t / P6_RABI_DECAY_US)) + _rng6(seed, 2).normal(0, 0.004, t.size)
    f = fitting.fit_rabi(t, y); om, om_e = abs(f.params["rabi_MHz"]), f.errors["rabi_MHz"]; k = _k6_one_sided()
    return {"rabi_put_in": rabi_mhz, "rabi_mhz": om, "rabi_err": om_e, "design": P6_RABI_DESIGN_MHZ, "tol": P6_RABI_TOL, "k": k, "t": t.tolist(), "y": y.tolist(),
            "pass": bool(abs(om - P6_RABI_DESIGN_MHZ) + k * om_e <= P6_RABI_TOL * P6_RABI_DESIGN_MHZ)}


def repetition_fidelity(p: float, f0: float = P6_F0) -> float:
    """Three-qubit repetition code with bit flips of probability p on each qubit: the majority vote fails with
    p_L = 3p^2 - 2p^3 [shor1995] (adamas.qec). Encoding and decoding succeed with probability f0; when they fail the
    result is random (fidelity 1/2). The unprotected baseline 1 - p it is compared with assumes perfect preparation and
    readout of the single qubit, so the comparison favors the baseline. A model of this repository; f0 is illustrative."""
    from .qec import repetition_logical_error
    return f0 * (1 - repetition_logical_error(p)) + (1 - f0) / 2


def repetition_break_even(f0: float = P6_F0) -> float | None:
    """Smallest p > 0 at which the corrected fidelity reaches 1 - p (None if correction never helps)."""
    from scipy.optimize import brentq
    h = lambda p: repetition_fidelity(p, f0) - (1 - p)   # noqa: E731
    grid = np.linspace(1e-6, 0.5 - 1e-6, 2000); v = np.array([h(x) for x in grid]); idx = np.nonzero(v > 0)[0]
    if idx.size == 0:
        return None
    i = idx[0]
    return float(grid[0]) if i == 0 else float(brentq(h, grid[i - 1], grid[i]))


def p6_repetition(seed: int = 6, f0: float = P6_F0) -> dict:
    """Error-injection test of the repetition code run through the chiplet (the error-injection method of [waldherr2014]): inject bit
    flips with probability P6_P_INJECT on each qubit and measure the fidelity with and without correction. Without
    correction one qubit keeps fidelity 1 - p. Pass when the gain F_corrected - F_uncorrected exceeds k sigma (one-sided).
    The degraded twin's encoding gates are spoiled by drive crosstalk (f0 = P6_F0_BAD), so correction no longer helps."""
    r = _rng6(seed, 3); p = P6_P_INJECT
    fc = repetition_fidelity(p, f0) + r.normal(0, P6_FID_NOISE); fu = 1 - p + r.normal(0, P6_FID_NOISE)
    gain, g_err = fc - fu, math.sqrt(2) * P6_FID_NOISE; k = _k6_one_sided()
    return {"p": p, "f0": f0, "f_corrected": fc, "f_uncorrected": fu, "gain": gain, "gain_err": g_err, "k": k,
            "pass": bool(gain - k * g_err > 0)}


def p6_gate(seed: int = 6) -> dict:
    c, d, q = p6_coherence(seed), p6_drive(seed), p6_repetition(seed)
    return {"coherence": c, "drive": d, "repetition": q, "verdict": "go" if c["pass"] and d["pass"] and q["pass"] else "stop"}


def p6_degraded(seed: int = 6) -> dict:
    """Each test on its degraded twin (one fault each); every one must fail."""
    return {"coherence": p6_coherence(seed, P6_T2_BAD_US), "drive": p6_drive(seed, P6_RABI_BAD_MHZ), "repetition": p6_repetition(seed, P6_F0_BAD)}


def p6_f0_at_limit(p: float = P6_P_INJECT) -> float:
    """Encoding fidelity at which the corrected fidelity equals 1 - p, so the true gain is exactly zero."""
    from .qec import repetition_logical_error
    return (0.5 - p) / (0.5 - repetition_logical_error(p))


def p6_at_limit(seed: int = 6) -> dict:
    """Each test with its true value exactly on its limit (T2 ratio 0.8, Rabi frequency 5 % above design, zero code
    gain). k is chosen so that each passes at most 1 - P6_TEST_COVERAGE of the time."""
    return {"coherence": p6_coherence(seed, P6_T2_RATIO_MIN * P6_T2_US), "drive": p6_drive(seed, (1 + P6_RABI_TOL) * P6_RABI_DESIGN_MHZ),
            "repetition": p6_repetition(seed, p6_f0_at_limit())}


@lru_cache(maxsize=4)
def p6_pass_rates(runs: int = P6_RUNS) -> dict:
    """Pass rates over simulated runs (seeds 6000 + i) for correct setups, wrong-pass rates for the degraded twins, and
    wrong-pass rates with the truth exactly on each limit (what k controls)."""
    keys = ("coherence", "drive", "repetition"); c = dict.fromkeys(keys + ("gate",), 0); d = dict.fromkeys(keys, 0); e = dict.fromkeys(keys, 0)
    for i in range(runs):
        g = p6_gate(6000 + i); b = p6_degraded(6000 + i); a = p6_at_limit(6000 + i)
        for k in keys:
            c[k] += g[k]["pass"]; d[k] += b[k]["pass"]; e[k] += a[k]["pass"]
        c["gate"] += g["verdict"] == "go"
    out = {k: v / runs for k, v in c.items()}
    out["degraded"] = {k: v / runs for k, v in d.items()}
    out["at_limit"] = {k: v / runs for k, v in e.items()}
    out.update(runs=runs, k=_k6(), k_one=_k6_one_sided(), se_test=math.sqrt(P6_TEST_COVERAGE * (1 - P6_TEST_COVERAGE) / runs),
               se_gate=math.sqrt(P6_GATE_COVERAGE * (1 - P6_GATE_COVERAGE) / runs))
    return out


P6_MACHINES = ("M00", "M26", "M27", "M28", "M29", "M47", "M53", "M55")


def p6_figure(out: str | Path = "docs/img") -> Path:
    """Figure 59: expected P6 results (nominal and degraded twin), simulated and fitted here."""
    import matplotlib.pyplot as plt
    from .figures import COLORS, INK, RED, _finish
    from . import fitting
    out = Path(out); g, b = p6_gate(), p6_degraded()
    fig, ax = plt.subplots(1, 3, figsize=(19, 4.8)); plt.subplots_adjust(wspace=.3)
    a = ax[0]; x = np.array(g["coherence"]["x"])
    fb = fitting.fit_echo(x, np.array(g["coherence"]["y_before"]))
    a.plot(x, g["coherence"]["y_before"], "o", ms=3.5, color=INK, alpha=.6)
    a.plot(fb.x, fb.model, color=INK, lw=1.2, alpha=.7, label=f"before bonding: T₂ = {g['coherence']['t2_before_us']:.0f} ± {g['coherence']['t2_before_err']:.0f} µs")
    for r, col, lab in ((g["coherence"], COLORS["Diamond"], "after bonding"), (b["coherence"], RED, "after a damaging bond (twin)")):
        a.plot(x, r["y_after"], "o", ms=3.5, color=col); f = fitting.fit_echo(x, np.array(r["y_after"]))
        a.plot(f.x, f.model, color=col, lw=1.8, label=f"{lab}: ratio {r['ratio']:.2f}, bound {r['ratio_lower']:.2f}")
    a.legend(fontsize=8, loc="upper right"); a.set_ylim(-0.01, 0.14)
    a.set_title(f"1. Coherence kept: pass when the T₂ ratio bound ≥ {P6_T2_RATIO_MIN:g} (ADAMAS)", fontsize=10.5)
    a.set_xlabel("echo free time 2τ (µs)"); a.set_ylabel("echo contrast")
    a = ax[1]; t = np.array(g["drive"]["t"])
    for r, col, lab in ((g["drive"], COLORS["Diamond"], "on-chip driver"), (b["drive"], RED, "driver at half current (twin)")):
        a.plot(t, r["y"], "o", ms=3.5, color=col)
        f = fitting.fit_rabi(t, np.array(r["y"]))
        a.plot(f.x, f.model, color=col, lw=1.5,
               label=f"{lab}: Ω = {r['rabi_mhz']:.2f} ± {r['rabi_err']:.2f} MHz (fit)")
    a.legend(fontsize=8, loc="upper right"); a.set_ylim(-0.02, 0.16); a.set_xlim(0, 0.4)
    a.set_title(f"2. On-chip drive: within {100 * P6_RABI_TOL:g} % of the {P6_RABI_DESIGN_MHZ:g} MHz design (QDL-27)", fontsize=10.5)
    a.set_xlabel("pulse length (µs; first 0.4 µs of the 1 µs record)"); a.set_ylabel("population transferred (contrast)")
    a = ax[2]; pp = np.linspace(0, 0.5, 101)
    a.plot(pp, 1 - pp, color=INK, lw=1.5, ls="--", label="one qubit, no correction: 1 − p")
    a.plot(pp, [repetition_fidelity(x) for x in pp], color=COLORS["Diamond"], lw=2, label=f"corrected, encoding fidelity {P6_F0:g}")
    a.plot(pp, [repetition_fidelity(x, P6_F0_BAD) for x in pp], color=RED, lw=2, label=f"corrected, crosstalk ({P6_F0_BAD:g}, twin)")
    for r, col in ((g["repetition"], COLORS["Diamond"]), (b["repetition"], RED)):
        a.errorbar([r["p"]], [r["f_corrected"]], yerr=[P6_FID_NOISE], fmt="o", color=col, ms=6, capsize=3)
    a.errorbar([g["repetition"]["p"]], [g["repetition"]["f_uncorrected"]], yerr=[P6_FID_NOISE], fmt="s", color=INK, ms=5, capsize=3)
    a.axvline(P6_P_INJECT, color=INK, lw=.6, alpha=.5); a.legend(fontsize=8, loc="upper right"); a.set_ylim(0.45, 1.02)
    a.set_title("3. Repetition code: corrected beats uncorrected by kσ", fontsize=10.5)
    a.set_xlabel("injected bit-flip probability p per qubit"); a.set_ylabel("fidelity of the stored state")
    return _finish(fig, out, "fig59_build_p6.png", "simulated and fitted by adamas.build_program and adamas.fitting (illustrative inputs); [shor1995] [waldherr2014]")


def _p6_rates_note(rates: dict) -> str:
    alpha = 1 - P6_TEST_COVERAGE; se = math.sqrt(alpha * P6_TEST_COVERAGE / rates["runs"]); lim = rates["at_limit"]
    ok = all(v <= alpha + 3 * se for v in lim.values())
    text = (f"Here k sets what each check lets through when the true value sits exactly on its limit: at most {100 * alpha:.1f} % wrong passes. "
            f"Simulated on the limit (T₂ ratio {P6_T2_RATIO_MIN:g}, Ω = {(1 + P6_RABI_TOL) * P6_RABI_DESIGN_MHZ:g} MHz, f₀ = {p6_f0_at_limit():.3f} so the true gain is zero), "
            f"the checks pass {100 * lim['coherence']:.1f} %, {100 * lim['drive']:.1f} % and {100 * lim['repetition']:.1f} % of runs" +
            (", within three standard errors of that. " if ok else ": more than three standard errors above it, so k is too small for this noise model. "))
    text += ("How often a correct run passes is the test's power, which depends on how far the true value sits from the limit, not on k alone. "
             "With these illustrative inputs the coherence ratio (0.94) and the drive (10 MHz against a 0.5 MHz band) sit far inside their limits, "
             "and the repetition-code gain, about four standard errors above zero, is the check that decides the rate. ")
    text += (f"Over {rates['runs']} runs the gate passes {100 * rates['gate']:.1f} % of correct runs" +
             (", at least the 95 % it is designed for." if rates["gate"] >= P6_GATE_COVERAGE - 3 * rates["se_gate"] else ", below the 95 % it is designed for: the tolerances need widening."))
    return text


def _p6_md() -> str:
    import re
    from . import atlas, atlas_prices
    from .traveler import STEPS
    st = {s["id"]: s for s in STEPS}
    g, b, rates = p6_gate(), p6_degraded(), p6_pass_rates(P6_RUNS)
    c, d, q = g["coherence"], g["drive"], g["repetition"]; bc, bd, bq = b["coherence"], b["drive"], b["repetition"]
    yes = lambda v: "yes" if v else "no"   # noqa: E731
    pct = lambda v: f"{100 * v:.1f} %"   # noqa: E731
    from .qec import repetition_logical_error
    pl = repetition_logical_error(P6_P_INJECT)
    machines = ", ".join(f"{k} {atlas.tool(k)}" for k in P6_MACHINES)
    hazards = " ".join(dict.fromkeys(h for sid in ("S18", "S19") for h in st[sid]["safety"]))
    verdict = ("All simulated checks pass and every degraded twin fails, so the analysis can tell a good chiplet from a faulty one; the gate is decided by the numbers measured on your assembly."
               if g["verdict"] == "go" and not (bc["pass"] or bd["pass"] or bq["pass"])
               else f"On this run a simulated check fails or a degraded twin passes; a correct run fails about {100 * (1 - rates['gate']):.1f} % of the time, so repeat it before changing the analysis.")
    text = f"""# P6 · Integration: diamond chiplets on silicon control

{GEN}

**Status: written in full.** Budget: **not totalled.** Published prices now exist for a multi-project wafer (MPW) shuttle ({atlas_prices.mpw_prices()}) and hourly rates for wafer bonding, dicing and wire bonding [wnf2026] (see the [Atlas](ATLAS.md)). They are not added up because the die area and the tool hours are not modelled, and no die or flip-chip bonder rate is sourced ([STATUS.md](../STATUS.md)). Gate verdict in simulation: **{g['verdict']}**.

Every input is **illustrative** except where a source is cited: the echo and Rabi data reuse the B1 noise model of `adamas.experiments`; the design Rabi frequency, its 5 % tolerance and the twin's half current are ADAMAS design values from Quantum Device Library entry QDL-27 (`adamas.qdl`), not measured numbers; the T₂ limit and the repetition-code numbers are this project's choices. The phase is **simulated**: no ADAMAS hardware has run it. Silicon complementary metal-oxide-semiconductor (CMOS) chips that drive and read nitrogen-vacancy (NV) centers in a diamond placed on them are **demonstrated** for magnetometry [kim2019cmos] [ibrahim2021]; driving a qubit register through such a chip is **proposed** here.

## Goal

Bond a diamond chiplet carrying characterized NV centers (from P3 and P5) to a CMOS control die, and show that the assembly keeps what the bare diamond had: the same coherence, a drive that delivers its design Rabi frequency, and a small error-correcting code that still helps. P6 answers whether integration keeps coherence and yield, before arrays of cells are planned.

## Physics and equations

- **Coherence through bonding:** the Hahn-echo signal decays as exp[−(2τ/T₂)ⁿ] (stretch exponent n set by the spin bath; `adamas.fitting.fit_echo`). The same NV is measured before bonding with an external drive and after bonding through the chiplet; the ratio R = T₂,after/T₂,before has error R√[(σ_a/T₂,a)² + (σ_b/T₂,b)²]. Pass when R − kσ_R ≥ {P6_T2_RATIO_MIN:g} (an ADAMAS target: bonding may cost at most {100 * (1 - P6_T2_RATIO_MIN):.0f} % of T₂).
- **On-chip drive:** a resonant drive gives P(t) = ½[1 − cos(2πΩt) e^(−t/τ)] (`adamas.fitting.fit_rabi`); Ω is proportional to the driver's current. Pass when |Ω − Ω_design| + kσ ≤ {100 * P6_RABI_TOL:g} % of Ω_design = {P6_RABI_DESIGN_MHZ:g} MHz (the QDL-27 criterion, an ADAMAS design threshold). The one-sided k is used at each edge of the band, so a driver exactly 5 % off passes at the same rate as the other checks' limits.
- **Repetition-code gain:** three qubits (the electron and two nuclear spins of one cell, the register of the room-temperature three-qubit code of [waldherr2014]) store one bit; each flips with probability p and majority voting fails with p_L = 3p² − 2p³ [shor1995]. It is modeled here for bit flips; a phase-flip code is the same circuit in a basis rotated by Hadamard gates and has the same p_L. If encoding and decoding succeed with probability f₀ and give a random result otherwise, the corrected fidelity is f₀(1 − p_L) + (1 − f₀)/2, against 1 − p for one unprotected qubit, whose preparation and readout are taken as perfect (so the comparison favors the unprotected qubit). At the injected p = {P6_P_INJECT:g} (illustrative), p_L = {pl:.4f}. With f₀ = {P6_F0:g} the code helps only for p between {repetition_break_even():.3f} and 0.5: imperfect encoding costs more than it saves when errors are rare, which is why the test injects errors. With the twin's f₀ = {P6_F0_BAD:g} the break-even moves to p = {repetition_break_even(P6_F0_BAD):.3f}, beyond the injected {P6_P_INJECT:g}. Pass when the measured gain exceeds kσ (one-sided). This model is this repository's and f₀ = {P6_F0:g} is illustrative. A three-qubit code corrects one kind of error only: the bit-flip code does not correct phase errors.

## Machines and facility

Atlas machines for this phase: {machines}. Design the CMOS die with open tools (M00) and order it on an MPW shuttle (M29); flip-chip or wire-bond the diamond onto it (M26, M28; traveler S19). A packaging line or an MPW partner provides the bonding.

## Facility and safety

{hazards} Laser dicing and Class 3B/4 lasers each need your institution's specific training and sign-off before first use; this page does not replace that training.

## Procedure

1. **Characterize before bonding.** On the chosen NV (from P3 or P5): echo T₂ with an external drive, and the nuclear spins of the register.
2. **Bond** the diamond chiplet onto the CMOS die (S19): flip-chip or wire bonds; check wire-bond pull strength (S19, at least 3 gf, an ADAMAS target).
3. **Drive through the chip.** Rabi oscillation from the on-chip driver at its design current; compare with the design.
4. **Re-measure coherence** of the same NV through the chiplet.
5. **Run the repetition code** with injected bit flips of probability p on each qubit, with and without correction (the error-injection method of [waldherr2014]).

## Expected results (simulated)

Each test is shown with its **degraded twin**: the same simulation with one fault, which the test must catch.

![Expected P6 results](../img/fig59_build_p6.png)

## Pass/fail

The gate needs all {P6_CHECKS} checks to pass, so each uses k = {rates['k_one']:.2f} (one-sided, {100 * P6_TEST_COVERAGE:.2f} %): a check whose true value sits exactly on its limit passes at most {100 * (1 - P6_TEST_COVERAGE):.1f} % of the time. Rates are over {rates['runs']} simulated runs (binomial standard error at the design rate: {100 * rates['se_test']:.1f} percentage points per check, {100 * rates['se_gate']:.1f} for the gate).

| Check | Criterion | Put in | Measured | Pass? | Correct runs passing |
|---|---|---|---|---|---|
| Coherence kept through bonding | R − kσ ≥ {P6_T2_RATIO_MIN:g} (ADAMAS) | T₂ {P6_T2_US:g} µs before and after | before {c['t2_before_us']:.0f} ± {c['t2_before_err']:.0f} µs, after {c['t2_after_us']:.0f} ± {c['t2_after_err']:.0f} µs; R = {c['ratio']:.3f} ± {c['ratio_err']:.3f} | {yes(c['pass'])} | {pct(rates['coherence'])} |
| On-chip drive | within {100 * P6_RABI_TOL:g} % of {P6_RABI_DESIGN_MHZ:g} MHz with kσ (QDL-27, ADAMAS design value) | {d['rabi_put_in']:g} MHz | {d['rabi_mhz']:.3f} ± {d['rabi_err']:.3f} MHz | {yes(d['pass'])} | {pct(rates['drive'])} |
| Repetition-code gain at p = {P6_P_INJECT:g} | gain − kσ > 0 | f₀ = {P6_F0:g} | corrected {q['f_corrected']:.3f}, uncorrected {q['f_uncorrected']:.3f}; gain {q['gain']:.3f} ± {q['gain_err']:.3f} | {yes(q['pass'])} | {pct(rates['repetition'])} |
| **Gate: every row passes** | | | | **{yes(g['verdict'] == 'go')}** | **{pct(rates['gate'])}** |

The degraded twins, one fault each. The last column is how often the faulty run wrongly passes.

| Test | Fault | Measured | Pass? | Faulty runs passing |
|---|---|---|---|---|
| Coherence | bonding damaged the surface and halved T₂ (illustrative) | R = {bc['ratio']:.3f}, bound {bc['ratio_lower']:.3f} | {yes(bc['pass'])} | {pct(rates['degraded']['coherence'])} |
| Drive | driver gives half the current (a QDL-27 failure mode) | {bd['rabi_mhz']:.3f} ± {bd['rabi_err']:.3f} MHz | {yes(bd['pass'])} | {pct(rates['degraded']['drive'])} |
| Repetition code | drive crosstalk spoils the encoding gates, f₀ = {P6_F0_BAD:g} (illustrative) | gain {bq['gain']:.3f} ± {bq['gain_err']:.3f} | {yes(bq['pass'])} | {pct(rates['degraded']['repetition'])} |

{_p6_rates_note(rates)}

## Not yet simulated

- **Multi-cell arrays:** P6's outline includes them; no model links two cells yet (P5 gives the pair yield, the link between cells is open, [STATUS.md](../STATUS.md)).
- **Photoelectric readout** (Atlas M55) through the chiplet: no noise model yet; the checks here assume optical readout.
- **Heating by the on-chip driver** and **green light leaking through the filter** (QDL-27 failure modes): no thermal or optical model of the assembly.
- **Phase errors** in the repetition code: the three-qubit code corrects bit flips only.

## Failure modes

- **Coherence lost at bonding:** surface damage, contamination or stress from the bond; compare T₂ of an unbonded reference chiplet from the same plate.
- **Driver below design:** current limit, a bad bond in the drive loop, or impedance mismatch; measure the driver's current on a test structure.
- **No code gain:** encoding gates spoiled by crosstalk from the chip's drive lines, or by heating; repeat with the external drive to locate the cause.
- **Die-attach voids** (S19): metallize the diamond's back side (titanium, platinum and gold, Ti/Pt/Au).

## Decision gate

*Does integration keep coherence and yield?* {verdict} Yield across many chiplets needs the same three checks on every bonded die; go to P7 when a batch of chiplets passes at a rate that the pilot-line economics (P7) can afford.

Sources: SOURCES_LINE
"""
    keys = list(dict.fromkeys(re.findall(r"\[([a-z][a-z0-9]*\d{4}[a-z0-9]*)\]", text)))
    return text.replace("SOURCES_LINE", " ".join(f"[{k}]" for k in keys))



# ---------------------------------------------------------------- P7 ------------------------------------------------
P7_CHECKS = 2                # the line is in statistical control, and its yield is explained by its killer defects
P7_GATE_COVERAGE = 0.95
P7_TEST_COVERAGE = P7_GATE_COVERAGE ** (1 / P7_CHECKS)     # so each check covers 97.47 %
P7_RUNS = 1000
# Wafer and die: 2-inch heteroepitaxial single-crystal wafers are published [kim2021] [qu2024]; the die is the 3 mm PDK-0
# monitor die (adamas.pdk0). Contact resistance is P4's illustrative value (P4_RC_OHM_MM). Every other number below is
# illustrative.
P7_WAFER_MM = 51.0           # 2-inch wafer [kim2021]
P7_EDGE_MM = 2.0             # edge exclusion: no die closer than this to the rim (illustrative)
P7_DIE_MM = 3.0              # PDK-0 monitor die (adamas.pdk0.monitor_die)
P7_BASELINE_WAFERS = 20      # phase I: wafers that set the control limits (illustrative)
P7_MONITOR_WAFERS = 20       # phase II: wafers judged against them (illustrative)
P7_RC_SIGMA = 0.3            # wafer-to-wafer spread of the wafer-mean contact resistance, Ω·mm (illustrative)
P7_RC_SHIFT_SIGMA = 4.0      # degraded twin: from wafer 31 on, contact residue raises Rc by 4 sigma (illustrative)
P7_SHIFT_FROM = 10           # index within phase II where the twin's shift starts (wafer 31 of 40)
P7_D0_CM2 = 2.0              # mean killer-defect density, cm^-2 (illustrative; inspection counts killer defects only)
P7_DEFECT_MONITORS = 10      # defect-monitor wafers inspected in full to measure D0, apart from the product wafers (illustrative)
P7_RING_MM = 4.0             # degraded twin: dies whose centre is within this of the edge exclusion lose growth uniformity
P7_RING_FAIL = 0.5           # ... and fail with this extra probability (illustrative)


def _k7() -> float:
    return _k_normal(P7_TEST_COVERAGE)


def _rng7(seed: int, test: int) -> np.random.Generator:
    """Independent stream per test (0 control chart, 1 wafer maps); twins reuse their streams."""
    return np.random.default_rng([seed, 7, test])


def p7_die_sites(wafer_mm: float = P7_WAFER_MM, die_mm: float = P7_DIE_MM, edge_mm: float = P7_EDGE_MM) -> np.ndarray:
    """Centres (mm) of the whole dies on a square grid, centred on the wafer, that lie entirely inside the usable
    radius wafer/2 - edge."""
    r = wafer_mm / 2 - edge_mm; n = int(wafer_mm // die_mm) + 2
    c = (np.arange(n) - (n - 1) / 2) * die_mm
    xx, yy = np.meshgrid(c, c); h = die_mm / 2
    far = np.hypot(np.abs(xx) + h, np.abs(yy) + h)          # the farthest corner from the wafer centre
    keep = far <= r
    return np.column_stack([xx[keep], yy[keep]])


def p7_control_limits(baseline: np.ndarray, n_monitor: int = P7_MONITOR_WAFERS, coverage: float = P7_TEST_COVERAGE) -> dict:
    """Shewhart individuals chart [shewhart1931] with limits from phase I. Shewhart's 3 sigma gives a false alarm on
    0.27 % of points; to keep the whole phase II run at 1 - coverage, the per-point false-alarm rate is
    1 - coverage^(1/n) and the limits are mean +- t s sqrt(1 + 1/m) with the Student t quantile for m - 1 degrees of
    freedom (a prediction interval for a new wafer, which accounts for limits estimated from m wafers). Each point is
    then covered exactly. The phase II points share the estimated mean and s, so they are positively dependent and, by
    the Sidak and Kimball inequalities, the whole run is covered at least at the coverage (simulated: about 97.7 % for
    a design of 97.47 %, so the chart is slightly conservative)."""
    from scipy.stats import t as student
    m = baseline.size; mean = float(baseline.mean()); s = float(baseline.std(ddof=1))
    a_pt = 1 - coverage ** (1 / n_monitor); k = float(student.ppf(1 - a_pt / 2, m - 1))
    half = k * s * math.sqrt(1 + 1 / m)
    return {"mean": mean, "s": s, "k": k, "alpha_point": a_pt, "lcl": mean - half, "ucl": mean + half}


def p7_spc(seed: int = 7, shift_sigma: float = 0.0) -> dict:
    """Wafer-mean contact resistance of the monitor die (TLM, as in P4) on 40 wafers in a row: 20 set the limits,
    20 are judged. Pass when no judged wafer falls outside the limits. The degraded twin's last 10 wafers carry
    contact residue that raises Rc by P7_RC_SHIFT_SIGMA standard deviations."""
    r = _rng7(seed, 0)
    base = P4_RC_OHM_MM + r.normal(0, P7_RC_SIGMA, P7_BASELINE_WAFERS)
    mon = P4_RC_OHM_MM + r.normal(0, P7_RC_SIGMA, P7_MONITOR_WAFERS)
    mon[P7_SHIFT_FROM:] += shift_sigma * P7_RC_SIGMA
    lim = p7_control_limits(base)
    out = [int(i) for i in np.nonzero((mon < lim["lcl"]) | (mon > lim["ucl"]))[0]]
    return {**lim, "baseline": base.tolist(), "monitor": mon.tolist(), "out_of_control": out, "shift_sigma": shift_sigma,
            "n_baseline": P7_BASELINE_WAFERS, "n_monitor": P7_MONITOR_WAFERS, "shift_wafer": P7_BASELINE_WAFERS + P7_SHIFT_FROM + 1,
            "first_alarm": (P7_BASELINE_WAFERS + out[0] + 1) if out else None, "pass": not out}


def p7_yield(seed: int = 7, ring: bool = False) -> dict:
    """Yield of the 20 judged product wafers against the defect density measured on separate defect-monitor wafers.
    Every die site gets a killer-defect density drawn from Murphy's triangular distribution on [0, 2 D0] and a Poisson
    number of killer defects for its area; a product die works when it has none, so its expected yield is Murphy's
    ((1 - e^(-A D0)) / (A D0))^2 [murphy1964] exactly. D0 is measured by inspecting every site of P7_DEFECT_MONITORS
    defect-monitor wafers that run the same steps (independent of the product dies). Pass when the product yield
    agrees with the Murphy prediction from that D0 within k sigma (two-sided), with sigma^2 = Y(1 - Y)/n + (Y' sigma_D0)^2
    (independent samples; sigma_D0 from the spread of the per-site counts, delta method for Y'). The degraded twin adds
    a ring of non-uniform growth near the edge whose dies fail with probability P7_RING_FAIL whatever their defects."""
    r = _rng7(seed, 1); sites = p7_die_sites(); n_w = P7_MONITOR_WAFERS; n = sites.shape[0] * n_w
    a_cm2 = (P7_DIE_MM / 10) ** 2
    d = r.triangular(0, P7_D0_CM2, 2 * P7_D0_CM2, n); good = r.poisson(a_cm2 * d) == 0
    n_m = sites.shape[0] * P7_DEFECT_MONITORS
    c = r.poisson(a_cm2 * r.triangular(0, P7_D0_CM2, 2 * P7_D0_CM2, n_m))
    rad = np.tile(np.hypot(sites[:, 0], sites[:, 1]), n_w)
    in_ring = rad > P7_WAFER_MM / 2 - P7_EDGE_MM - P7_RING_MM
    if ring:
        good = good & ~(in_ring & (r.random(n) < P7_RING_FAIL))
    from .wafer import murphy_yield
    d0 = float(c.sum() / (n_m * a_cm2)); d0_err = float(c.std(ddof=1) / math.sqrt(n_m) / a_cm2)
    y_meas = float(good.mean()); y_pred = murphy_yield(P7_DIE_MM ** 2, d0)
    h = 1e-6; slope = (murphy_yield(P7_DIE_MM ** 2, d0 + h) - murphy_yield(P7_DIE_MM ** 2, d0 - h)) / (2 * h)
    sigma = math.hypot(math.sqrt(y_meas * (1 - y_meas) / n), slope * d0_err); k = _k7()
    ring_yield = float(good[in_ring].mean()); centre_yield = float(good[~in_ring].mean())
    return {"dies_per_wafer": int(sites.shape[0]), "dies": int(n), "d0_cm2": d0, "d0_err": d0_err, "monitor_sites": int(n_m),
            "y_meas": y_meas, "y_pred": y_pred, "y_poisson": math.exp(-a_cm2 * d0), "diff": y_meas - y_pred, "sigma": sigma, "k": k,
            "ring_yield": ring_yield, "centre_yield": centre_yield, "ring": ring,
            "map": [[float(x), float(y), bool(g)] for (x, y), g in zip(sites, good[:sites.shape[0]])],
            "pass": bool(abs(y_meas - y_pred) <= k * sigma)}


def p7_gate(seed: int = 7) -> dict:
    s, y = p7_spc(seed), p7_yield(seed)
    return {"spc": s, "yield": y, "verdict": "go" if s["pass"] and y["pass"] else "stop"}


def p7_degraded(seed: int = 7) -> dict:
    """Each test on its degraded twin (one fault each); every one must fail."""
    return {"spc": p7_spc(seed, P7_RC_SHIFT_SIGMA), "yield": p7_yield(seed, ring=True)}


@lru_cache(maxsize=4)
def p7_pass_rates(runs: int = P7_RUNS) -> dict:
    """Pass rates over simulated runs (seeds 7000 + i) for correct lines, and wrong-pass rates for the degraded twins."""
    keys = ("spc", "yield"); c = dict.fromkeys(keys + ("gate",), 0); d = dict.fromkeys(keys, 0)
    for i in range(runs):
        g = p7_gate(7000 + i); b = p7_degraded(7000 + i)
        for k in keys:
            c[k] += g[k]["pass"]; d[k] += b[k]["pass"]
        c["gate"] += g["verdict"] == "go"
    out = {k: v / runs for k, v in c.items()}
    out["degraded"] = {k: v / runs for k, v in d.items()}
    out.update(runs=runs, k=_k7(), se_test=math.sqrt(P7_TEST_COVERAGE * (1 - P7_TEST_COVERAGE) / runs),
               se_gate=math.sqrt(P7_GATE_COVERAGE * (1 - P7_GATE_COVERAGE) / runs))
    return out


def p7_good_dies_table(d0_cm2: float, areas_mm2=(1.0, 9.0, 25.0, 100.0)) -> list[dict]:
    """Good dies per 2-inch wafer against die area at a measured D0 (Murphy yield, gross dies from the edge-loss formula
    of adamas.wafer). Cost per good die is the wafer cost divided by this number; no wafer cost is sourced yet."""
    from .wafer import dies_per_wafer, murphy_yield
    return [{"area_mm2": a, "gross": dies_per_wafer(P7_WAFER_MM - 2 * P7_EDGE_MM, a), "yield": murphy_yield(a, d0_cm2),
             "good": dies_per_wafer(P7_WAFER_MM - 2 * P7_EDGE_MM, a) * murphy_yield(a, d0_cm2)} for a in areas_mm2]



def p7_bill() -> dict:
    """Parts and price range for P7: the D2 part list (estimates from adamas.experiments, not quotes)."""
    from .experiments import EXPERIMENTS
    by = {e["id"]: e for e in EXPERIMENTS}
    rows = [("D2", *p) for p in by["D2"]["parts"]]
    return {"rows": rows, "low": sum(r[3] for r in rows), "high": sum(r[4] for r in rows), "headline": by["D2"]["cost"]}


P7_MACHINES = ("M01", "M03", "M05", "M06", "M07", "M09", "M16", "M17", "M18", "M23")


def p7_figure(out: str | Path = "docs/img") -> Path:
    """Figure 60: expected P7 results (nominal and degraded twin), simulated and analyzed here."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle
    from .figures import COLORS, INK, RED, _finish
    from .wafer import murphy_yield
    out = Path(out); g, b = p7_gate(), p7_degraded()
    fig, ax = plt.subplots(1, 4, figsize=(23, 5.2), gridspec_kw={"width_ratios": [1.5, 1, 1, 1.15]}); plt.subplots_adjust(wspace=.28)
    a = ax[0]; s, t = g["spc"], b["spc"]; m = P7_BASELINE_WAFERS
    xb = np.arange(1, m + 1); xm = np.arange(m + 1, m + P7_MONITOR_WAFERS + 1)
    a.plot(xb, s["baseline"], "o-", ms=4, lw=.8, color=INK, alpha=.6, label="phase I: sets the limits")
    a.plot(xm, t["monitor"], "s--", ms=6, lw=.8, color=RED, mfc="none", label=f"twin: contact residue from wafer {m + P7_SHIFT_FROM + 1} (+{P7_RC_SHIFT_SIGMA:g}σ; same wafers before it)")
    a.plot(xm, s["monitor"], "o-", ms=4, lw=.8, color=COLORS["Diamond"], label="phase II, correct line: in control")
    for v in (s["lcl"], s["ucl"]):
        a.axhline(v, color=INK, ls="--", lw=1)
    a.axhline(s["mean"], color=INK, lw=.6, alpha=.6); a.axvline(m + .5, color=INK, lw=.6, alpha=.4)
    a.legend(fontsize=8, loc="upper left"); a.set_ylim(min(s["lcl"], min(s["baseline"])) - 0.4, max(t["monitor"]) + 1.2)
    a.set_title(f"1. Control chart: limits ±{s['k']:.2f}·s·√(1+1/m) from phase I [shewhart1931]", fontsize=10.5)
    a.set_xlabel("wafer in the order processed"); a.set_ylabel("wafer-mean contact resistance (Ω·mm)")
    r_use = P7_WAFER_MM / 2 - P7_EDGE_MM
    for a, y, title in ((ax[1], g["yield"], "2. Wafer map, correct line"), (ax[2], b["yield"], "3. Wafer map, twin: edge ring")):
        a.add_patch(Circle((0, 0), P7_WAFER_MM / 2, fill=False, color=INK, lw=1.2))
        a.add_patch(Circle((0, 0), r_use, fill=False, color=INK, lw=.6, ls=":"))
        if y["ring"]:
            a.add_patch(Circle((0, 0), r_use - P7_RING_MM, fill=False, color=RED, lw=1.6, ls="--"))
            a.text(0, -26.5, f"dashed red: inner edge of the {P7_RING_MM:g} mm ring", ha="center", fontsize=8, color=RED)
        h = P7_DIE_MM / 2
        for x0, y0, ok in y["map"]:
            a.add_patch(Rectangle((x0 - h + .1, y0 - h + .1), P7_DIE_MM - .2, P7_DIE_MM - .2, color=COLORS["Diamond"] if ok else RED, alpha=.85 if ok else .95))
        a.set_xlim(-27, 27); a.set_ylim(-27, 27); a.set_aspect("equal"); a.set_xticks([]); a.set_yticks([])
        a.set_title(f"{title}\nfirst wafer; lot yield {100 * y['y_meas']:.1f} % (Murphy predicts {100 * y['y_pred']:.1f} %)", fontsize=10.5)
        a.set_ylim(-28, 27)
        for sp in a.spines.values():
            sp.set_visible(False)
    a = ax[3]; xx = np.linspace(0.01, 2.0, 200)
    a.plot(xx, np.exp(-xx), color=INK, lw=1.2, ls="--", label="Poisson e^(−AD₀)")
    a.plot(xx, [murphy_yield(100 * x, 1.0) for x in xx], color=INK, lw=1.8, label="Murphy [murphy1964]")
    for y, col, lab in ((g["yield"], COLORS["Diamond"], "correct line"), (b["yield"], RED, "edge-ring twin")):
        ad = (P7_DIE_MM / 10) ** 2 * y["d0_cm2"]
        a.errorbar([ad], [y["y_meas"]], yerr=[y["k"] * y["sigma"]], fmt="o", color=col, ms=6, capsize=3, label=f"{lab}: measured, ±kσ")
    a.legend(fontsize=8, loc="upper right"); a.set_ylim(0, 1.05)
    a.set_title("4. Product yield against A·D₀ from defect-monitor wafers", fontsize=10.5)
    a.set_xlabel("die area × killer-defect density, A·D₀"); a.set_ylabel("yield")
    return _finish(fig, out, "fig60_build_p7.png", "simulated and analyzed by adamas.build_program (illustrative inputs; 2-inch wafer [kim2021]); [shewhart1931] [murphy1964]")


def _p7_rates_note(rates: dict) -> str:
    design = P7_TEST_COVERAGE; se = rates["se_test"]; out = []
    for key, name in (("spc", "control-chart"), ("yield", "yield")):
        v = rates[key]
        word = "more often than" if v > design + 3 * se else "less often than" if v < design - 3 * se else "about as often as"
        out.append(f"the {name} check passes correct runs {word} designed ({100 * v:.1f} %)")
    text = "Against the {:.2f} % design per check: ".format(100 * design) + "; ".join(out) + ". "
    text += ("Here a correct run sits exactly on the model each check tests (a stable process; a yield set by random killer defects), "
             "so its pass rate is the check's coverage: at least the design for the chart (slightly conservative, because the judged wafers share the estimated limits) "
             "and the design for large samples for the yield check (normal approximation). ")
    text += (f"Over {rates['runs']} runs the gate passes {100 * rates['gate']:.1f} % of correct runs" +
             (", consistent with the 95 % it is designed for." if rates["gate"] >= P7_GATE_COVERAGE - 3 * rates["se_gate"] else ", below the 95 % it is designed for: the limits need widening."))
    return text


def _p7_md() -> str:
    import re
    from . import atlas
    from .traveler import STEPS
    from .wafer import dies_per_wafer
    st = {s["id"]: s for s in STEPS}
    g, b, rates = p7_gate(), p7_degraded(), p7_pass_rates(P7_RUNS)
    s, y = g["spc"], g["yield"]; bs, by = b["spc"], b["yield"]
    yes = lambda v: "yes" if v else "no"   # noqa: E731
    pct = lambda v: f"{100 * v:.1f} %"   # noqa: E731
    money = lambda v: f"${v / 1e6:g} M"   # noqa: E731
    bill = p7_bill(); table = p7_good_dies_table(y["d0_cm2"])
    machines = ", ".join(f"{k} {atlas.tool(k)}" for k in P7_MACHINES).replace("YSZ", "yttria-stabilized zirconia (YSZ)", 1)
    hazards = " ".join(dict.fromkeys(h for sid in ("S03", "S17") for h in st[sid]["safety"]))
    verdict = ("Both simulated checks pass and both degraded twins fail, so the analysis can tell a stable, defect-limited line from a drifting or edge-limited one; the gate is decided by the numbers measured on your line."
               if g["verdict"] == "go" and not (bs["pass"] or by["pass"])
               else f"On this run a simulated check fails or a degraded twin passes; a correct line fails about {100 * (1 - rates['gate']):.1f} % of the time, so repeat it before changing the analysis.")
    parts = "\n".join(f"| {r[1]} | {r[2]} | {money(r[3])} to {money(r[4])} |" for r in bill["rows"]).replace("ALD", "atomic layer deposition (ALD)", 1)
    good = "\n".join(f"| {t['area_mm2']:g} | {t['gross']} | {pct(t['yield'])} | {t['good']:.0f} |" for t in table)
    text = f"""# P7 · Pilot line and products: statistical control and yield

{GEN}

**Status: written in full.** Budget: **{money(bill['low'])} to {money(bill['high'])}** (experiment D2's part list: planning estimates, not quotes). Gate verdict in simulation: **{g['verdict']}**.

Every input is **illustrative** except where a source is cited: the wafer is 2 inches, the size of published heteroepitaxial single-crystal diamond wafers [kim2021] [qu2024] (one 92 mm plate has been grown [schreck2017]; 3-inch wafers are an industry announcement without published data [e6orbray2026]); the die is the {P7_DIE_MM:g} mm PDK-0 monitor die (`adamas.pdk0`). The contact resistance is P4's illustrative value. The process spread, the defect density and both faults are chosen to look like a typical line, not measured. The phase is **simulated**: no diamond pilot line runs PDK-0 today, so the whole phase is **proposed**.

## Goal

Run the PDK-0 flow on many wafers in a row and show two things a pilot line needs before any product: that the process is **stable** (a monitor-die parameter stays inside control limits wafer after wafer) and that its **yield is understood** (the fraction of working dies is what its counted killer defects predict). Then rank products by good dies per wafer, which with a wafer cost gives the cost per good die.

## Physics and equations

- **Control chart:** each wafer's mean contact resistance R_c (from the transfer-length method, TLM, on the monitor die, as in P4) is plotted in processing order. Shewhart's chart [shewhart1931] flags a wafer outside mean ± 3σ, which a stable process does on 0.27 % of points. Here {P7_BASELINE_WAFERS} wafers (phase I) set the limits and the next {P7_MONITOR_WAFERS} (phase II) are judged. To keep the whole phase II run's false-alarm rate at most 1 − {100 * P7_TEST_COVERAGE:.2f} %, each point gets α = 1 − {P7_TEST_COVERAGE:.4f}^(1/{P7_MONITOR_WAFERS}) = {s['alpha_point']:.2e}, and because the limits are estimated from m = {P7_BASELINE_WAFERS} wafers they are a prediction interval: mean ± t·s·√(1 + 1/m) with the Student t quantile for m − 1 degrees of freedom, t = {s['k']:.2f}. The judged wafers share the estimated limits, so they are positively dependent and the run's false-alarm rate is at most the design (Šidák and Kimball inequalities); simulated it is about 2.3 %. Pass when no phase II wafer is outside. Assumes independent, normally distributed wafer means; wider limits than Shewhart's catch large shifts quickly but small drifts slowly.
- **Yield:** a die works when it carries no killer defect. If killer defects fall at random with density D, a die of area A works with probability e^(−AD) (Poisson). Densities vary across a wafer and between wafers; Murphy took a triangular distribution of D on [0, 2D₀] and found Y = [(1 − e^(−AD₀))/(AD₀)]² [murphy1964]; Stapper's clustered models generalize this [stapper1983] (`adamas.wafer`). D₀ is measured by inspecting every site of {P7_DEFECT_MONITORS} defect-monitor wafers that run the same steps ({y['monitor_sites']} sites, killer defects only); electrical test counts the working product dies. Pass when the product yield agrees with Murphy's prediction from that D₀ within k = {y['k']:.2f} standard errors (two-sided), with σ² = Y(1 − Y)/n + (Y′σ_D₀)² for the two independent samples (σ_D₀ from the spread of the per-site counts). At A·D₀ = {(P7_DIE_MM / 10) ** 2 * y['d0_cm2']:.2f} the Poisson and Murphy yields differ by only {100 * (y['y_pred'] - y['y_poisson']):.1f} percentage points, less than σ, so this check tests whether the measured defect density explains the yield (or a systematic loss adds to it), not which model is right; telling the models apart needs larger dies.
- **Cost per good die:** gross dies per wafer N = π(d/2)²/A − πd/√(2A) (the edge-loss approximation of `adamas.wafer`, with d the usable diameter) times the yield gives the good dies; the wafer's cost divided by that number is the cost per good die. No wafer cost is sourced yet, so this page gives the good dies, not the cost.

## Machines and facility

Atlas machines for this phase: {machines}, plus every P4 machine for the device flow. Experiment D2 lists the line: {"; ".join(f"{r[1].lower()} ({r[2]})" for r in bill['rows'])}. A fab or a consortium pilot line, not a university cleanroom.

| Part (D2) | What | Price range (estimate) |
|---|---|---|
{parts}

D2 budgets 3-inch wafers; this page simulates 2-inch wafers, the largest size with published quality data in this repository's sources, so the wafer line is an upper estimate for it.

## Facility and safety

A pilot line needs a full semiconductor-fab environmental health and safety (EHS) program. {hazards} Each hazardous process needs your institution's or company's specific training and sign-off before first use; this page does not replace that training.

## Procedure

1. **Baseline.** Run the PDK-0 traveler on {P7_BASELINE_WAFERS} wafers without changing recipes; measure the monitor die on each (S17) and set the control limits.
2. **Monitor.** Keep running; plot every new wafer on the chart before releasing it. A point outside the limits stops the line until its cause is found.
3. **Inspect and test.** Map killer defects on every site of the defect-monitor wafers (birefringence, etch pits, optical inspection; Atlas M09) and test every product die electrically.
4. **Compare.** Predict the yield from the counted killer defects with Murphy's model and compare with the measured yield. Map where the failing dies are: a pattern (edge, centre, a quadrant) means a systematic cause, not random defects.
5. **Rank products** by good dies per wafer at your D₀ and die size, then by cost per good die once wafer costs are known.

## Expected results (simulated)

Each test is shown with its **degraded twin**: the same simulation with one fault, which the test must catch.

![Expected P7 results](../img/fig60_build_p7.png)

## Pass/fail

The gate needs both checks to pass, so each is set for {100 * P7_TEST_COVERAGE:.2f} % coverage. Rates are over {rates['runs']} simulated runs (binomial standard error at the design rate: {100 * rates['se_test']:.1f} percentage points per check, {100 * rates['se_gate']:.1f} for the gate).

| Check | Criterion | Put in | Measured | Pass? | Correct runs passing |
|---|---|---|---|---|---|
| Process in control | no phase II wafer outside mean ± {s['k']:.2f}·s·√(1+1/m) | R_c {P4_RC_OHM_MM:g} ± {P7_RC_SIGMA:g} Ω·mm per wafer | limits {s['lcl']:.2f} to {s['ucl']:.2f} Ω·mm; {len(s['out_of_control'])} wafers outside | {yes(s['pass'])} | {pct(rates['spc'])} |
| Yield explained by killer defects | \\|Y − Y_Murphy(D₀)\\| ≤ kσ | D₀ = {P7_D0_CM2:g} cm⁻² | D₀ = {y['d0_cm2']:.2f} ± {y['d0_err']:.2f} cm⁻² (monitors); Y = {pct(y['y_meas'])} against {pct(y['y_pred'])} predicted (σ {100 * y['sigma']:.2f} points), {y['dies']} product dies | {yes(y['pass'])} | {pct(rates['yield'])} |
| **Gate: every row passes** | | | | **{yes(g['verdict'] == 'go')}** | **{pct(rates['gate'])}** |

The degraded twins, one fault each. The last column is how often the faulty run wrongly passes.

| Test | Fault | Measured | Pass? | Faulty runs passing |
|---|---|---|---|---|
| Control chart | contact residue raises R_c by {P7_RC_SHIFT_SIGMA:g}σ from wafer {P7_BASELINE_WAFERS + P7_SHIFT_FROM + 1} (illustrative) | {len(bs['out_of_control'])} wafers outside; first alarm at wafer {bs['first_alarm']} | {yes(bs['pass'])} | {pct(rates['degraded']['spc'])} |
| Yield | non-uniform growth near the edge: dies within {P7_RING_MM:g} mm of the edge exclusion fail half the time (illustrative) | Y = {pct(by['y_meas'])} against {pct(by['y_pred'])} predicted; edge ring {pct(by['ring_yield'])}, centre {pct(by['centre_yield'])} | {yes(by['pass'])} | {pct(rates['degraded']['yield'])} |

{_p7_rates_note(rates)} The chart's twin shifts by {P7_RC_SHIFT_SIGMA:g}σ because limits this wide catch a 1σ drift only slowly; small drifts need a cumulative-sum or moving-average chart (not yet simulated).

## Products: good dies per 2-inch wafer

At the measured D₀ = {y['d0_cm2']:.2f} cm⁻², usable diameter {P7_WAFER_MM - 2 * P7_EDGE_MM:g} mm. Gross dies come from the edge-loss formula; the simulated wafer's square grid fits {y['dies_per_wafer']} whole {P7_DIE_MM:g} mm dies, close to the formula's {dies_per_wafer(P7_WAFER_MM - 2 * P7_EDGE_MM, P7_DIE_MM ** 2)}.

| Die area (mm²) | Gross dies | Murphy yield | Good dies |
|---|---|---|---|
{good}

Yield falls steeply with die area, so at this D₀ small dies (sensors, discrete switches) get by far the most good dies per wafer, and large dies (qubit arrays, large power switches) need a lower D₀. Which product pays for the line also needs each product's price and test cost, which are not sourced ([STATUS.md](../STATUS.md)).

## Not yet simulated

- **Spatially clustered defects:** each die's density is drawn independently; real defects cluster (Stapper's negative-binomial model [stapper1983]), which raises yield at a given D₀ and widens wafer-to-wafer spread.
- **Small drifts:** cumulative-sum (CUSUM) or exponentially weighted moving-average (EWMA) charts.
- **Several parameters at once:** only R_c is charted; a line charts every traveler check (threshold, sheet resistance, leakage, NV yield).
- **Defect density's effect on leakage and coherence:** dislocation densities by substrate class are in `adamas.wafer`, but no model links them to leakage current or T₂ yet.
- **Product qualification:** reliability tests per product (temperature, humidity, high-voltage life) need sourced criteria.

## Failure modes

- **Out-of-control point:** a recipe, chamber or source-gas change; stop, find the cause, and decide whether the wafers since the last good point are usable.
- **Yield below prediction:** a systematic loss (edge ring, a bad mask area, a probe-card fault); look at where failing dies sit on the map.
- **Yield above prediction:** the inspection counts defects that do not kill, or the monitor wafers see more defects than the product wafers; recalibrate which defect classes are killers against electrical test.
- **D₀ too high for the product:** grow on lower-dislocation substrates (homoepitaxial on high-pressure high-temperature, HPHT, seeds) or reduce particles; compare substrate classes in `adamas.wafer`.

## Decision gate

*Which product line pays for the line?* {verdict} The simulation can rank products by good dies per wafer, which favours small dies; the economic answer needs sourced wafer, test and product prices. Go to P8 when one product's measured cost per good die is below its price.

Sources: SOURCES_LINE
"""
    keys = list(dict.fromkeys(re.findall(r"\[([a-z][a-z0-9]*\d{4}[a-z0-9]*)\]", text)))
    return text.replace("SOURCES_LINE", " ".join(f"[{k}]" for k in keys))



# ---------------------------------------------------------------- P8 ------------------------------------------------
# P8 is not one experiment: it asks, application by application, whether diamond beats the incumbent, with evidence.
# The answer is an evidence ledger whose rules are evaluated by code, so an inflated claim cannot be typed in:
#   R1  a "beats" or "does not beat" claim needs either a computed comparison that is decisive over a sourced parameter
#       RANGE (10th percentile above 1, or 90th below 1; a single point value is never decisive) or a cited measured
#       comparison (both values and their source) pointing the same way; and a claim may not contradict a decisive
#       computed comparison (no hiding a loss, no hiding a win). "not compared" is allowed only where no comparison
#       is attempted on purpose.
#   R2  the technology readiness level (TRL) [mankins1995] may not exceed the cap of the strongest evidence cited, and a
#       claim resting on a computed comparison is capped at 3 (analytical proof of concept).
#   R3  every application names its key unsolved problem.
P8_TRL_CAP = {"proposed": 2, "simulated": 2, "demonstrated": 4, "relevant environment": 5, "prototype": 6, "commercial": 9}
P8_COMPUTED_CAP = 3
P8_TRL_WORDS = {1: "basic principles observed", 2: "concept formulated", 3: "analytical and experimental proof of concept",
                4: "component validated in the lab", 5: "component validated in a relevant environment",
                6: "prototype in a relevant environment", 7: "prototype in an operational environment",
                8: "system complete and qualified", 9: "system proven in operation"}
P8_SAMPLES = 2000            # Latin-hypercube samples of the sourced parameter ranges (adamas.uncertainty.POWER)
P8_T_HOT_K = 523.0           # 250 °C: silicon carbide's package-limited junction ceiling today [she2017]
P8_T_SIC_COOLED_K = 373.0    # a cooled silicon carbide switch at 100 °C, for the fairer hot comparison (illustrative)


def _p8_ratio(p: dict, t_diamond_k: float, t_sic_k: float) -> float:
    """adamas.uncertainty.power_ratio with each switch at its own junction temperature (equal temperatures give
    exactly power_ratio)."""
    from dataclasses import replace
    from . import converter, materials, power
    d = replace(materials.MATERIALS["Diamond"], ec_mv_cm=p["Diamond critical field"], mu_p=p["Diamond hole mobility"], eps_r=p["Diamond permittivity"])
    s = replace(materials.MATERIALS["4H-SiC"], ec_mv_cm=p["SiC critical field"], mu_n=p["SiC electron mobility"])
    rc = lambda m, name, car, t: (power.ron_sp_mohm_cm2(m, 1200.0, car) * converter.ron_temperature_factor(name, t, 1200.0, m=m)  # noqa: E731
                                  * converter.coss_sp_f_cm2(m, 1200.0))
    return math.sqrt(rc(s, "4H-SiC", "n", t_sic_k) / rc(d, "Diamond", "p", t_diamond_k))


def p8_loss_ratio_percentiles(t_k: float, n: int = P8_SAMPLES, seed: int = 11, t_sic_k: float | None = None) -> dict:
    """SiC loss / diamond loss of a 1200 V switch at its area optimum over the sourced parameter ranges of
    adamas.uncertainty.POWER, diamond at junction temperature t_k and silicon carbide at t_sic_k (default: the same).
    Above 1: diamond loses less. The diamond drift is idealized bulk boron-doped (uncompensated), so its resistance
    carries the ionized fraction at t_k (adamas.converter); the hole-mobility range is that of intrinsic material, an
    upper bound for a doped drift. Same topology and thermal design; linear output capacitance, hard switching;
    packaging, gate drive and reliability are not in the model."""
    from .uncertainty import POWER, sample
    ts = t_k if t_sic_k is None else t_sic_k
    r = np.array([_p8_ratio(p, t_k, ts) for p in sample(POWER, n, seed)])
    return {"t_k": t_k, "t_sic_k": ts, "p10": float(np.percentile(r, 10)), "p50": float(np.percentile(r, 50)), "p90": float(np.percentile(r, 90))}


def p8_crossover_k(pct: str = "p50", lo: float = 300.0, hi: float = 600.0) -> float | None:
    """Equal junction temperature at which the chosen percentile of the loss ratio reaches 1 (None if not in range)."""
    from scipy.optimize import brentq
    f = lambda t: p8_loss_ratio_percentiles(t)[pct] - 1.0   # noqa: E731
    return None if f(lo) * f(hi) > 0 else float(brentq(f, lo, hi, xtol=0.5))


def p8_measured_device_ratio(t_k: float) -> float:
    """SiC loss / diamond loss with the best demonstrated diamond device (the 3.66 kV NO2-doped MOSFET [saha2023],
    scaled to 1200 V by BV^2; a lateral 2DHG device, no ionization factor) against ideal-limit silicon carbide, both at
    t_k. A point comparison of one measured device with an ideal limit, so unfavourable to diamond."""
    from .converter import material_switch
    d = material_switch("Diamond", 1200.0, 800.0, 200.0, 2e4, t_k, measured="saha2023")
    s = material_switch("4H-SiC", 1200.0, 800.0, 200.0, 2e4, t_k)
    return s.p_total_w / d.p_total_w


def _p8_kappa() -> dict:
    from .materials import MATERIALS
    r = MATERIALS["Diamond"].kappa_w_cmk / MATERIALS["4H-SiC"].kappa_w_cmk
    return {"p10": r, "p50": r, "p90": r, "t_k": 300.0, "point": True}


def p8_comparisons() -> dict:
    """The computed comparisons the ledger uses; each value is a ratio where above 1 favours diamond."""
    return {"loss_300k": p8_loss_ratio_percentiles(300.0), "loss_hot": p8_loss_ratio_percentiles(P8_T_HOT_K),
            "loss_hot_cooled_sic": p8_loss_ratio_percentiles(P8_T_HOT_K, t_sic_k=P8_T_SIC_COOLED_K), "kappa": _p8_kappa()}


# Each row: the claim this program makes, the evidence behind it, and its TRL. Claims and TRLs are this repository's
# judgment; the rules below check them against the evidence. "undecided" means no decisive comparison is sourced.
P8_APPS = [
    {"id": "ev300", "name": "EV traction inverter switch, 300 K junction", "incumbent": "silicon carbide MOSFET [reimers2019]",
     "metric": "switch loss at the area optimum (idealized bulk-doped diamond drift)", "computed": "loss_300k", "cited": None, "claim": "does not beat",
     "evidence": "demonstrated", "evidence_text": "3.66 kV NO₂-doped lateral diamond MOSFETs on heteroepitaxial wafers [saha2023]", "trl": 3,
     "problem": "boron is only partly ionized at room temperature, so a bulk-doped vertical drift has a high resistance; surface-doped lateral devices avoid it but are not demonstrated at traction-inverter current"},
    {"id": "hot", "name": "Hot power switch, both junctions at 250 °C", "incumbent": "silicon carbide MOSFET at its package ceiling [she2017]",
     "metric": "switch loss at the area optimum (idealized bulk-doped diamond drift)", "computed": "loss_hot", "cited": None, "claim": "beats",
     "evidence": "simulated", "evidence_text": "model only: the bulk-doped vertical drift is not demonstrated; the demonstrated hot devices are lateral FETs at 400 °C [kawarada2014]", "trl": 2,
     "problem": "the win needs silicon carbide forced to its ceiling; a vertical bulk-doped diamond switch, and a package and gate insulator that last years at 250 °C, do not exist yet"},
    {"id": "hot_cooled", "name": "Hot diamond (250 °C) against cooled silicon carbide (100 °C)", "incumbent": "silicon carbide MOSFET with more cooling",
     "metric": "switch loss at the area optimum (idealized bulk-doped diamond drift)", "computed": "loss_hot_cooled_sic", "cited": None, "claim": "undecided",
     "evidence": "simulated", "evidence_text": "model only", "trl": 2,
     "problem": "the value of running hot is a smaller cooling system, which this loss model does not price"},
    {"id": "spreader", "name": "Heat spreader under GaN transistors", "incumbent": "silicon carbide substrate",
     "metric": "substrate thermal conductivity (single-crystal point values; the channel temperature also depends on the interface)", "computed": "kappa", "cited": None, "claim": "undecided",
     "evidence": "demonstrated", "evidence_text": "4-inch GaN-on-diamond substrates [francis2010]", "trl": 4,
     "problem": "the thermal boundary resistance at the GaN–diamond interface and polycrystalline diamond's lower conductivity can erase the gain; no sourced channel-temperature comparison"},
    {"id": "detector", "name": "Radiation detector and beam monitor", "incumbent": "silicon detector",
     "metric": "radiation hardness (dose to failure)", "computed": None, "cited": None, "claim": "undecided",
     "evidence": "relevant environment", "evidence_text": "diamond detectors for particle physics, including beam tests and irradiation studies, reviewed in [tapper2000]", "trl": 5,
     "problem": "no sourced dose-to-failure numbers for diamond and silicon here; charge-collection distance of polycrystalline material and the cost of single-crystal plates"},
    {"id": "rf", "name": "RF power amplifier", "incumbent": "GaN transistor", "metric": "output power density at matched frequency and efficiency",
     "computed": None, "cited": None, "claim": "undecided",
     "evidence": "demonstrated", "evidence_text": "3.8 W/mm RF power density from an Al₂O₃-gated diamond MOSFET [imanishi2019]", "trl": 4,
     "problem": "no GaN number at matched conditions is sourced here; surface-conductivity stability under RF drive"},
    {"id": "magnetometer", "name": "NV magnetometer (field, medical, geophysical)", "incumbent": "fluxgate, optically pumped or SQUID magnetometers",
     "metric": "sensitivity at room temperature", "computed": None, "cited": None, "claim": "undecided",
     "evidence": "demonstrated", "evidence_text": "compact nanotesla-sensitivity NV magnetometer [webb2019]; sensitivity limits reviewed in [barry2020]", "trl": 4,
     "problem": "medical use (brain and heart signals) needs femtotesla-level sensitivity; no sourced requirement or incumbent number is in this repository yet"},
    {"id": "logic", "name": "High-temperature logic", "incumbent": "silicon carbide and silicon-on-insulator logic [watson2015]",
     "metric": "gates working at temperature", "computed": None, "cited": None, "claim": "undecided",
     "evidence": "demonstrated", "evidence_text": "logic gates from hydrogen-terminated diamond FETs [liu2017]", "trl": 3,
     "problem": "only p-type FETs are mature, so complementary logic and its static power are open"},
    {"id": "navigation", "name": "GPS-free navigation by magnetic-anomaly maps", "incumbent": "inertial navigation with fluxgate or optically pumped magnetometers",
     "metric": "position error over time", "computed": None, "cited": None, "claim": "undecided",
     "evidence": "proposed", "evidence_text": "no diamond navigation result is sourced here", "trl": 2,
     "problem": "a vector magnetometer with sourced sensitivity, drift and vehicle-noise rejection; anomaly-map resolution"},
    {"id": "register", "name": "Room-temperature few-qubit register", "incumbent": "none: no comparison with superconducting or trapped-ion processors is made, and none is implied",
     "metric": "none", "computed": None, "cited": None, "claim": "not compared",
     "evidence": "demonstrated", "evidence_text": "two-NV entanglement at room temperature [dolde2013]", "trl": 3,
     "problem": "coupling more than a few spins with high fidelity; readout time (P3 to P6 of this program)"},
]


def _p8_cited_direction(cited: dict | None) -> str | None:
    """A cited measured comparison {'diamond': x, 'incumbent': y, 'higher_is_better': bool, 'key': ...} -> its verdict."""
    if not isinstance(cited, dict) or cited.get("diamond") is None or cited.get("incumbent") is None or not cited.get("key"):
        return None
    better = cited["diamond"] > cited["incumbent"] if cited.get("higher_is_better", True) else cited["diamond"] < cited["incumbent"]
    return "beats" if better else "does not beat"


def p8_check(app: dict, comps: dict | None = None) -> dict:
    """Apply rules R1 to R3 to one ledger row."""
    comps = comps if comps is not None else p8_comparisons()
    c = comps.get(app["computed"]) if app["computed"] else None
    if c is None:
        decisive = None
    elif c.get("point") or c["p10"] == c["p90"]:
        decisive = "undecided"                       # a point value is never decisive
    else:
        decisive = "beats" if c["p10"] > 1 else "does not beat" if c["p90"] < 1 else "undecided"
    cited = _p8_cited_direction(app.get("cited")); claim = app["claim"]
    if claim in ("beats", "does not beat"):
        r1 = (decisive == claim) or (decisive is None and cited == claim)
    elif claim == "not compared":
        r1 = c is None and not app.get("cited")
    else:
        r1 = decisive in (None, "undecided") and cited is None
    cap = P8_TRL_CAP[app["evidence"]]
    if claim in ("beats", "does not beat") and decisive in ("beats", "does not beat"):
        cap = min(cap, P8_COMPUTED_CAP)
    r2 = 1 <= app["trl"] <= cap; r3 = bool(app["problem"].strip())
    return {"id": app["id"], "computed": c, "decisive": decisive, "r1": bool(r1), "r2": bool(r2), "r3": r3, "cap": cap, "pass": bool(r1 and r2 and r3)}


def p8_gate() -> dict:
    comps = p8_comparisons(); rows = [p8_check(a, comps) for a in P8_APPS]
    beats = [a["id"] for a, r in zip(P8_APPS, rows) if r["pass"] and a["claim"] == "beats"]
    return {"rows": rows, "comparisons": comps, "beats": beats, "crossover_p50_k": p8_crossover_k("p50"),
            "crossover_p10_k": p8_crossover_k("p10"), "measured_ratio_300k": p8_measured_device_ratio(300.0),
            "measured_ratio_hot": p8_measured_device_ratio(P8_T_HOT_K), "verdict": "go" if all(r["pass"] for r in rows) else "stop"}


def p8_degraded() -> dict:
    """Five inflated claims (one fault each); the rules must reject every one."""
    by = {a["id"]: a for a in P8_APPS}; comps = p8_comparisons()
    wrong = {"diamond": 1.0, "incumbent": 2.0, "higher_is_better": True, "key": "illustrative"}
    return {"hidden_loss": p8_check({**by["ev300"], "claim": "beats"}, comps),
            "inflated_trl": p8_check({**by["magnetometer"], "trl": 6}, comps),
            "unsupported_win": p8_check({**by["rf"], "claim": "beats"}, comps),
            "point_value_win": p8_check({**by["spreader"], "claim": "beats"}, comps),
            "wrong_way_citation": p8_check({**by["detector"], "claim": "beats", "cited": wrong}, comps)}


P8_MACHINES = ("M56", "M57", "M58", "M59")
P8_CLAIM_COLORS = {"beats": "#0fa3b1", "does not beat": "#e63946", "undecided": "#9aa6b2", "not compared": "#d9dee4"}


def p8_figure(out: str | Path = "docs/img") -> Path:
    """Figure 61: P8's computed comparison (switch loss against junction temperature) and the evidence ledger."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from .figures import COLORS, INK, RED, _finish
    out = Path(out); g = p8_gate()
    fig, ax = plt.subplots(1, 2, figsize=(20, 6.4), gridspec_kw={"width_ratios": [1, 1.3]}); plt.subplots_adjust(wspace=.62)
    a = ax[0]; ts = np.linspace(300, 600, 25); pc = [p8_loss_ratio_percentiles(t, 400) for t in ts]
    a.fill_between(ts, [p["p10"] for p in pc], [p["p90"] for p in pc], color=COLORS["Diamond"], alpha=.25, label="10th to 90th percentile, sourced ranges")
    a.plot(ts, [p["p50"] for p in pc], color=COLORS["Diamond"], lw=2, label="median (idealized bulk-doped drift)")
    a.axhline(1, color=INK, lw=1, ls="--"); a.text(305, 1.04, "above: diamond loses less than SiC", fontsize=8.5, color=INK)
    a.axvline(P8_T_HOT_K, color=RED, lw=1, ls="-"); a.text(P8_T_HOT_K + 3, 2.75, "SiC package\nceiling [she2017]", fontsize=8, color=RED, va="top")
    for key, ls in (("crossover_p50_k", ":"), ("crossover_p10_k", "-.")):
        a.axvline(g[key], color=INK, lw=.8, ls=ls)
    a.text(g["crossover_p50_k"] + 3, 0.18, f"median crosses 1\nat {g['crossover_p50_k']:.0f} K", fontsize=8)
    a.text(g["crossover_p10_k"] + 3, 0.5, f"90 % of samples\nabove 1 from {g['crossover_p10_k']:.0f} K", fontsize=8)
    for key, col, fmt in (("loss_300k", RED, "o"), ("loss_hot", COLORS["Diamond"], "o"), ("loss_hot_cooled_sic", "#6b7785", "s")):
        c = g["comparisons"][key]; a.errorbar([c["t_k"] + (6 if fmt == "s" else 0)], [c["p50"]], yerr=[[c["p50"] - c["p10"]], [c["p90"] - c["p50"]]], fmt=fmt, color=col, ms=7, capsize=4)
    a.text(P8_T_HOT_K - 8, g["comparisons"]["loss_hot_cooled_sic"]["p10"] - 0.12, "SiC cooled to 373 K", fontsize=8, color="#6b7785", ha="right")
    a.plot([300, P8_T_HOT_K], [g["measured_ratio_300k"], g["measured_ratio_hot"]], "x", color=INK, ms=8, mew=2, label="demonstrated device [saha2023] vs ideal SiC")
    a.set_ylim(0, 2.9); a.set_xlim(295, 605); a.legend(fontsize=8, loc="upper left", bbox_to_anchor=(0, 0.93))
    a.set_title("1. SiC loss ÷ diamond loss, 1200 V switch at its area optimum\n(both at the same junction temperature unless marked; simulated)", fontsize=10.5)
    a.set_xlabel("junction temperature (K)"); a.set_ylabel("loss ratio")
    a = ax[1]; rows = {r["id"]: r for r in g["rows"]}; apps = P8_APPS[::-1]
    for i, x in enumerate(apps):
        a.barh(i, x["trl"], color=P8_CLAIM_COLORS[x["claim"]], height=.6)
        a.plot([rows[x["id"]]["cap"]] * 2, [i - .38, i + .38], color=INK, lw=2)
        basis = " (simulated)" if x["computed"] and x["claim"] in ("beats", "does not beat") else ""
        a.text(max(x["trl"], rows[x["id"]]["cap"]) + .15, i, f"{x['claim']}{basis} · {x['evidence']}", va="center", fontsize=8)
    a.set_yticks(range(len(apps)), [x["name"] for x in apps], fontsize=8.5); a.set_xlim(0, 12); a.set_xticks(range(1, 10))
    a.legend(handles=[Patch(color=v, label=k) for k, v in P8_CLAIM_COLORS.items()], fontsize=8, loc="lower right", title="claim", title_fontsize=8)
    a.set_xlabel("technology readiness level claimed (bar) and the cap its evidence allows (black tick)")
    a.set_title("2. Evidence ledger: claim, evidence label and readiness [mankins1995]", fontsize=10.5)
    return _finish(fig, out, "fig61_build_p8.png", "computed by adamas.build_program and adamas.uncertainty over sourced parameter ranges; claims and levels are this repository's judgment, checked by rules R1 to R3")


def _p8_range(c: dict) -> str:
    if c.get("point") or c["p10"] == c["p90"]:
        return f"{c['p50']:.2f} (point values; not decisive)"
    return f"{c['p10']:.2f} to {c['p90']:.2f} (median {c['p50']:.2f})"


def _p8_md() -> str:
    import re
    from . import atlas
    from .uncertainty import POWER
    g, b = p8_gate(), p8_degraded(); rows = {r["id"]: r for r in g["rows"]}; cmp_ = g["comparisons"]
    yes = lambda v: "yes" if v else "no"   # noqa: E731
    by = {a["id"]: a for a in P8_APPS}
    ledger = "\n".join(
        f"| {a['name']} | {a['incumbent']} | {a['metric']} | "
        + (_p8_range(cmp_[a['computed']]) if a["computed"] else "none sourced")
        + f" | **{a['claim']}**{' (simulated)' if a['computed'] and a['claim'] in ('beats', 'does not beat') else ''} | {a['evidence']}: {a['evidence_text']} | {a['trl']} (cap {rows[a['id']]['cap']}) | {yes(rows[a['id']]['pass'])} |"
        for a in P8_APPS)
    problems = "\n".join(f"- **{a['name']}:** {a['problem']}." for a in P8_APPS)
    ranges = "; ".join(f"{k} {v[1]:g} to {v[2]:g} {v[4]} {v[5]}".replace("  ", " ") for k, v in POWER.items())
    machines = ", ".join(f"{k} {atlas.tool(k)}" for k in P8_MACHINES)
    twins = (f"| Hide a loss | claims the 300 K inverter switch **beats** SiC | computed ratio {cmp_['loss_300k']['p10']:.2f} to {cmp_['loss_300k']['p90']:.2f}, decisively below 1 | R1 | {yes(b['hidden_loss']['pass'])} |\n"
             f"| Inflate readiness | gives the NV magnetometer TRL 6 | its evidence is a lab demonstration, cap {b['inflated_trl']['cap']} | R2 | {yes(b['inflated_trl']['pass'])} |\n"
             f"| Unsupported win | claims the RF amplifier **beats** GaN | no computed or cited comparison | R1 | {yes(b['unsupported_win']['pass'])} |\n"
             f"| Point value as proof | claims the heat spreader **beats** SiC from two conductivities | a point value is not decisive | R1 | {yes(b['point_value_win']['pass'])} |\n"
             f"| Citation the wrong way | claims the detector **beats** silicon with a citation whose numbers favour silicon | the cited direction contradicts the claim | R1 | {yes(b['wrong_way_citation']['pass'])} |")
    beats = "; ".join(by[i]["name"] for i in g["beats"]) or "none"
    hot, cold, cool = cmp_["loss_hot"], cmp_["loss_300k"], cmp_["loss_hot_cooled_sic"]
    text = f"""# P8 · Frontier: where diamond beats the incumbent, with evidence

{GEN}

**Status: written in full.** Budget: **not priced** (application-specific test benches, shielded rooms and irradiation facilities; no sourced prices). Gate verdict: **{g['verdict']}**.

P8 is not one experiment. It asks, application by application, whether diamond beats the device it would replace, and answers with an **evidence ledger** whose rules are evaluated by code, so an inflated claim fails the build the way a failed measurement fails the earlier phases. Claims and readiness levels are this repository's judgment; the rules check them against the evidence. Nothing here is a new measurement: comparisons are **computed** over sourced parameter ranges or **cited**, and every row is labeled with the evidence behind it.

## Goal

For each application in the outline (grid and electric-vehicle power, hot and harsh-environment electronics, radiation detection, medical and field magnetometry, navigation, room-temperature quantum registers): name the incumbent, compare where a comparison can be computed or is published, assign a technology readiness level (TRL) no higher than the evidence allows, and name the key unsolved problem. Terms in the ledger: EV, electric vehicle; SiC, silicon carbide; MOSFET, metal-oxide-semiconductor field-effect transistor (FET); 2DHG, two-dimensional hole gas; GaN, gallium nitride; RF, radio frequency; NV, nitrogen-vacancy center; SQUID, superconducting quantum interference device; GPS, Global Positioning System.

## Rules (evaluated by code)

- **R1 Claim follows evidence.** "Beats" or "does not beat" needs either a computed comparison that is decisive over a sourced parameter **range** (its 10th percentile above 1, or its 90th below 1; a single point value is never decisive) or a cited measured comparison, with both numbers and the source, pointing the same way. A claim may not contradict a decisive computed comparison: no hiding a loss, and no hiding a win. "Undecided" means no decisive comparison is sourced; "not compared" is used only where no comparison is attempted on purpose.
- **R2 Readiness follows evidence.** TRL follows the NASA scale [mankins1995]; the cap is set by the strongest cited evidence: proposed or simulated ≤ {P8_TRL_CAP['simulated']}, demonstrated in a lab ≤ {P8_TRL_CAP['demonstrated']}, a component in a relevant environment ≤ {P8_TRL_CAP['relevant environment']}, a prototype in a relevant environment ≤ {P8_TRL_CAP['prototype']}, commercial ≤ {P8_TRL_CAP['commercial']}. A claim that rests on a computed comparison is capped at {P8_COMPUTED_CAP}.
- **R3 Name the problem.** Every application states its key unsolved problem.

## Physics and equations

- **Power switch loss:** with conduction loss I²R_on,sp/A and hard-switching loss ½C_oss,sp·A·V²·f, the area A that minimizes their sum gives a loss proportional to √(R_on,sp · C_oss,sp), so the ratio of silicon carbide's loss to diamond's is √[(R·C)_SiC / (R·C)_diamond] for a 1200 V device (`adamas.converter.optimum_switch`, `adamas.uncertainty.power_ratio`). Assumes a linear output capacitance (fully depleted drift), hard switching, the same converter topology and thermal design, and ignores packaging, gate drive and reliability. R_on includes the lattice mobility at the junction temperature and, for diamond's idealized bulk boron-doped vertical drift, the ionized fraction of the (uncompensated) boron, which is small at room temperature and grows with temperature. The diamond hole-mobility range is that of intrinsic material, an upper bound for a doped drift. Parameter ranges (Latin-hypercube sampled, {P8_SAMPLES} samples): {ranges}.
- **Result:** at 300 K the ratio is {cold['p10']:.2f} to {cold['p90']:.2f} (10th to 90th percentile): this diamond switch **loses**. With both junctions at {P8_T_HOT_K:.0f} K, silicon carbide's package-limited ceiling [she2017], it is {hot['p10']:.2f} to {hot['p90']:.2f}: diamond **wins**; the median crosses 1 at {g['crossover_p50_k']:.0f} K and 90 % of the samples are above 1 from {g['crossover_p10_k']:.0f} K. That win needs silicon carbide forced to its ceiling: cooled to {P8_T_SIC_COOLED_K:.0f} K against diamond at {P8_T_HOT_K:.0f} K, the ratio is {cool['p10']:.2f} to {cool['p90']:.2f}, **undecided**. And it is for an idealized device: the best demonstrated diamond switch [saha2023], a lateral 2DHG device scaled to 1200 V, against ideal silicon carbide gives {g['measured_ratio_300k']:.2f} at 300 K and {g['measured_ratio_hot']:.2f} at {P8_T_HOT_K:.0f} K (one device against an ideal limit, so unfavourable to diamond, but measured).
- **Heat spreading:** single-crystal thermal conductivity, diamond {cmp_['kappa']['p50']:.1f} times silicon carbide's (`adamas.materials`, point values). A point value is not decisive, and the transistor's channel temperature also depends on the GaN–diamond interface.
- **Readiness:** TRL 1 to 9 [mankins1995]: {"; ".join(f"{k} {v}" for k, v in P8_TRL_WORDS.items())}.

## Evidence ledger

| Application | Incumbent | Metric | Comparison (above 1 favours diamond) | Claim | Evidence | TRL | Rules pass? |
|---|---|---|---|---|---|---|---|
{ledger}

## Machines and facility

Atlas machines for this phase: {machines}. Each application needs its own facility: a converter test bench, a magnetically shielded room, an irradiation facility, a vehicle with a magnetic-anomaly map.

## Facility and safety

High-voltage converter tests run behind interlocked shields; irradiation is done only at licensed facilities under their radiation-safety program; lasers for NV magnetometers are Class 3B or 4. Each needs your institution's specific training and sign-off before first use; this page does not replace that training.

## Procedure

1. **For each application,** find the incumbent's number for the metric that matters, from a source.
2. **Compute** the comparison where a model exists, over sourced parameter ranges, or **cite** a measured one with both numbers.
3. **Assign** the TRL from the strongest evidence, not from the hope.
4. **Run the rules** (`adamas build docs` does it); fix the claim, not the rule, when one fails.
5. **Test** the leading application on its bench (M56 for power) to turn a computed comparison into a measured one.

## Expected results

![P8 comparison and ledger](../img/fig61_build_p8.png)

## Pass/fail

The gate passes when every ledger row passes R1 to R3. The rules are deterministic, so there is no pass rate; instead each rule is tested on a **degraded twin**: an inflated claim that it must reject.

| Twin | Fault | Why it must fail | Rule | Passes? |
|---|---|---|---|---|
{twins}

## Key unsolved problems

{problems}

## Not yet sourced

- Incumbent numbers for magnetometry (femtotesla-level medical requirements, fluxgate and optically pumped sensitivities) and for GaN RF power density at matched conditions.
- Any diamond navigation result, and a magnetic-anomaly navigation requirement.
- Radiation-hardness numbers (dose to failure) for diamond and silicon devices.
- A channel-temperature comparison of GaN on diamond and on silicon carbide.
- Prices of the test benches, shielded rooms and irradiation time, and of the cooling that a hot switch would save.

## Failure modes

- **A model comparison taken for a measurement:** the loss ratio is simulated; only a bench measurement (M56) at matched junction temperature makes it evidence of the next level.
- **Unfair comparisons:** an incumbent at a worse operating point (forced hot instead of cooled), a different topology, or a cherry-picked parameter; the ranges here are sourced and sampled, and the cooled case is shown.
- **Readiness drift:** levels raised by enthusiasm; rule R2 stops that in this repository.

## Decision gate

*Where does diamond beat the incumbent, with evidence?* With the evidence in this repository, the rows that claim a win and pass the rules are: {beats}. That win is computed for an idealized device and needs silicon carbide at its ceiling; the demonstrated diamond device still loses there, and against cooled silicon carbide the comparison is undecided. Everywhere else the honest answer is "does not beat", "undecided" or "not compared", and the key problem above says what would change it. Building a vertical diamond switch and measuring it hot on the converter bench is the experiment that would move the power rows.

Sources: SOURCES_LINE
"""
    keys = list(dict.fromkeys(re.findall(r"\[([a-z][a-z0-9]*\d{4}[a-z0-9]*)\]", text)))
    return text.replace("SOURCES_LINE", " ".join(f"[{k}]" for k in keys))


# ---------------------------------------------------------------- documents ----------------------------------------
GEN = "_Generated from `adamas/build_program.py` (`adamas build docs`); every number below is computed by the package._"


def _p0_md() -> str:
    from . import action, loop
    g = p0_gate()
    scenes = "\n".join(f"| {s['title']} | `{s['id']}` | {', '.join('[' + r + ']' for r in s['refs'])} |" for s in action.SCENES)
    panels = "\n".join(f"| {p['title']} | `{p['python']}` | {p['lab'].split('/')[-1]} |" for p in loop.PANELS.values())
    known = "\n".join(f"- {k}" for k in g["known_checks"]) or "- none"
    gate0 = (f"**Go**: no check fails. The {len(g['known_checks'])} known discrepancy (or discrepancies) move forward to the phase that can measure them; the Bell-fidelity one goes to P5, where two-NV entanglement is measured."
             if g["verdict"] == "go" else f"**Stop**: {g['fail']} check(s) fail; fix the model or its reference before planning hardware.")
    return f"""# P0 · Simulation

{GEN}

**Status: written in full.** Budget: US$0 (open-source tools on a laptop, Atlas item M00). Gate verdict today: **{g['verdict']}**.

## Goal

Make every later step runnable in the app first, and calibrate each model against published data, a second independent implementation, or a known answer. Hardware is planned only from models that pass this phase.

## Physics and equations

The {len(action.SCENES)} equations in action, one per experiment plus the power and error-correction limits (assumptions and validity ranges on each scene, [Equations in Action](../EQUATIONS_IN_ACTION.md)):

| Scene | ID | Sources |
|---|---|---|
{scenes}

The equation-in-the-loop panels the labs carry, each with its reference implementation (assumption checks run live in the lab):

| Panel | Reference implementation | Lab |
|---|---|---|
{panels}

Larger simulations: circuit-level surface and XZZX codes in Stim with PyMatching decoding (`adamas.circuit_qec`, `adamas.xzzx_native`), the Lindblad and echo gate budget (`adamas.gate_budget`, `adamas.opensys`), yield models (`adamas.wafer`), and the converter loss model (`adamas.converter`).

## Machines and facility

M00: a workstation with Python 3.10 or newer, Node.js, and the open tools in [DEVELOPMENT_UBUNTU.md](../DEVELOPMENT_UBUNTU.md) (Stim, PyMatching, ngspice, Icarus Verilog, Yosys, KLayout, OpenROAD). No laboratory, no safety training.

## Procedure

```bash
pip install -e ".[dev]" && (cd web && npm ci)
python -m pytest -q -rs          # every model test; -rs prints why anything skipped
(cd web && npm test)              # browser physics against Python golden values
make validation                   # the validation matrix below
make serve                        # run every lab locally
```

## Expected results and pass/fail

The validation matrix ([VALIDATION.md](../VALIDATION.md)) has **{g['checks']} checks**: {g['kinds']['literature']} against published results, {g['kinds']['cross-tool']} between two independent implementations, and {g['kinds']['analytic']} against known or injected answers.

| Criterion | Result | Pass? |
|---|---|---|
| No check fails | {g['fail']} fail | {'yes' if g['fail'] == 0 else 'no'} |
| Checks within tolerance | {g['pass']} of {g['checks']} | {'yes' if g['fail'] == 0 else 'no'} |
| Known discrepancies, explained and carried forward | {g['known']} | listed below |

Known discrepancies (each says why, in the matrix):

{known}

## Failure modes

- A model can pass its one calibration point and still be wrong elsewhere. Each scene and panel states its validity range, and the labs flag states outside it.
- A cross-tool check catches a coding error but not a shared wrong assumption. The literature checks are the ones that test physics.
- Unmeasured inputs (the NV two-qubit gate bias, the inter-cell link) are assumptions, listed in [STATUS.md](../STATUS.md); P0 cannot validate them.

## Decision gate

*Do the models agree with published data well enough to plan hardware?* {gate0}

Sources: see each scene and panel; validation sources in [VALIDATION.md](../VALIDATION.md).
"""


def _p1_md() -> str:
    from .experiments import EXPERIMENTS
    by = {e["id"]: e for e in EXPERIMENTS}
    gate, bill, rate = p1_gate(), p1_bill(), p1_pass_rate()
    det, mag, th = gate["detection"], gate["magnetometer"], gate["thermometer"]
    atlas = {"NV-rich diamond": "M31", "Green source": "M30", "Red filter": "M32", "Photodetector": "M33", "Microwave source": "M34", "Antenna": "M35",
             "Controller": "M36", "Mechanics": "M37", "Ruler or printed rail": "M37", "Second magnet (optional)": "M37", "Non-magnetic stand": "M37",
             "Heater": "M37", "Temperature sensors": "M37"}
    rows = "\n".join(f"| {atlas.get(r[1], '')} | {r[1]} ({r[0]}) | {r[2]} | {r[3]:,} to {r[4]:,} |" for r in bill["rows"])
    steps = lambda e: "\n".join(f"{i + 1}. **{s[0]}.** {s[1]}" for i, s in enumerate(by[e]["steps"]))   # noqa: E731
    safety = " ".join(by["A1"]["safety"] + by["A3"]["safety"][:1])
    yes = lambda b: "yes" if b else "no"   # noqa: E731
    return f"""# P1 · Proof of concept: an ODMR magnetometer and thermometer

{GEN}

**Status: written in full.** Budget: **US${bill['low']:,} to {bill['high']:,}** (sum of the part ranges below; approximate 2026 street prices from the experiment list, estimates and not quotes). Gate verdict in simulation: **{gate['verdict']}**.

## Goal

Build the A1 kit and use it twice: as a magnetometer (the splitting of the lines follows the field of a magnet, experiment A2) and as a thermometer (the zero-field splitting D moves with temperature). Both are ensemble measurements on a diamond with many NV centers.

## Physics and equations

- **Lines in a field** ([Chapter 6](../06_nv_center_physics.md)): f± = D ± γₑB∥ + O(B⊥²/D), γₑ = 28.03 MHz/mT [doherty2013]. Valid while γₑB ≪ D; the Lattice Lab's panel shows the second-order term and its error against exact diagonalization.
- **Dipole field on the magnet's axis:** B = μ₀m/(2πr³), so the splitting falls as r⁻³ (slope −3 on a log-log plot). Valid when r is several times the magnet's size.
- **Temperature:** D(T) ≈ 2870 MHz + (dD/dT)(T − 300 K) with dD/dT = −74.2(7) kHz/K, a weighted average of four samples measured between 280 and 330 K [acosta2010]. The run stays inside that range (20 to 50 °C); over wider ranges D(T) is not linear [toyli2012].

## Machines and consumables

| Atlas | Part (experiment) | Specification | US$ |
|---|---|---|---|
{rows}

## Facility and safety

A desk. {safety}

## Procedure

**Magnetometer (A1, then A2):**

A1:

{steps('A1')}

A2:

{steps('A2')}

**Thermometer (new in P1):** remove the magnets and move steel away (the zero-field spectrum must not change when you move them further); glue the heater resistor and the thermistor next to the diamond on the antenna board; record a zero-field spectrum at {', '.join(f'{t:g}' for t in th['temps_c'][:-1])}, and {th['temps_c'][-1]:g} °C, waiting until the thermistor reading is stable at each; fit each spectrum with `python -m adamas.fit odmr file.csv`, then fit a straight line to the centers, weighted by their uncertainties.

## Expected results (simulated)

The kit is simulated with the A1 noise model of `adamas.experiments` (contrast {100 * A1_CONTRAST:.1f} %, line width {A1_LINEWIDTH:.0f} MHz, noise {100 * A1_NOISE:.2f} % per point; illustrative kit values, not a measurement) and fitted by `adamas.fitting`, the code you use on real data.

![Expected P1 results](../img/fig54_build_p1.png)

## Pass/fail

| Test | Criterion | Simulated result | Pass? |
|---|---|---|---|
| Find the dip | Signal-to-noise of the fitted depth at least 5 (five-sigma detection), center within half a line width of 2870 MHz | {det['snr']:.0f}; {det['center_mhz']:.2f} ± {det['center_err_mhz']:.2f} MHz | {yes(det['pass'])} |
| Magnetometer | Log-log slope within two standard errors of −3 | {mag['slope']:.3f} ± {mag['slope_err']:.3f} | {yes(mag['pass'])} |
| Thermometer | Slope within two combined standard errors of −74.2 kHz/K (fit and published uncertainty) | {th['slope_khz_k']:.1f} ± {th['slope_err_khz_k']:.1f} kHz/K; tolerance ±{th['tolerance_khz_k']:.1f} | {yes(th['pass'])} |

A kit that behaves exactly like the model passes the thermometer test in **{100 * rate:.1f} %** of {400} simulated runs (more than 95 % because the tolerance also includes the published uncertainty). A single failed run is therefore unlikely to be noise alone; repeat the run before concluding.

## Failure modes

- **Heating moves more than the diamond.** The heater also warms the photodiode, the amplifier, and the laser or LED; their drift changes the baseline, not the line center, so fit centers rather than reading a single frequency.
- **Stray field.** A magnet or steel nearby splits and shifts the lines and mimics a temperature change; check with the magnets removed.
- **Strain.** Many ensembles show a strain splitting at zero field that a single Lorentzian fits poorly; fit two lines and track their mean.
- **Thermistor offset.** Place the sensor as close to the diamond as possible and wait for equilibrium; a lag between sensor and diamond flattens the slope.

## Decision gate

*Is the signal-to-noise good enough to move to pulsed control?* {'All three continuous-wave tests above pass in simulation.' if gate['verdict'] == 'go' else 'At least one continuous-wave test above fails in simulation; fix that first.'} The pulsed decision needs one more number the kit can measure: the dip depth when the microwave is pulsed (P2, experiment B1). Move to P2 when your measured detection signal-to-noise is at least the five-sigma criterion above and the thermometer slope passes.

Sources: [doherty2013] [acosta2010] [stegemann2023] [williams2026] [gruber1997]
"""


DOCS = {"P0": "P0_simulation.md", "P1": "P1_proof_of_concept.md", "P2": "P2_teaching_lab.md", "P3": "P3_single_nv.md", "P4": "P4_devices.md", "P5": "P5_placement.md", "P6": "P6_integration.md", "P7": "P7_pilot_line.md", "P8": "P8_frontier.md"}


def _index_md() -> str:
    rows = "\n".join(f"| {p['id']} | {p['name']} | {p['budget']} | {p['goal']} | {p['gate']} | {'[written](' + DOCS[p['id']] + ')' if p['status'] == 'written' else 'outline'} |" for p in PHASES)
    done = [p["id"] for p in PHASES if p["status"] == "written"]
    return f"""# Build program

{GEN}

A ladder from a laptop to a pilot line. Each phase ends at a decision gate. {', '.join(done[:-1])} and {done[-1]} are written in full, with their gates evaluated by code; {('the rest are outlined in [phase0/BUILD_PROGRAM_OUTLINE.md](../phase0/BUILD_PROGRAM_OUTLINE.md) and are written one per release as their sources come in ([STATUS.md](../STATUS.md)).' if len(done) < len(PHASES) else 'the outline they started from is [phase0/BUILD_PROGRAM_OUTLINE.md](../phase0/BUILD_PROGRAM_OUTLINE.md), and what is still unsourced is in [STATUS.md](../STATUS.md).')}

| Phase | Name | Budget | Goal | Gate question | Status |
|---|---|---|---|---|---|
{rows}

Every machine these phases name (M00 to M59), with its facility, access mode and a published, estimated or missing price, is in the [Machines and Facilities Atlas](ATLAS.md).
"""


def _p2_md() -> str:
    from .experiments import EXPERIMENTS
    by = {e["id"]: e for e in EXPERIMENTS}
    g, bill, rates = p2_gate(), p2_bill(), p2_pass_rates(P2_RUNS)
    pu, ve, ar, T = g["pulsed"], g["vector"], g["arrhenius"], g["pulsed"]["truth"]
    yes = lambda b: "yes" if b else "no"   # noqa: E731
    rows = "\n".join(f"| {r[1]} ({r[0]}) | {r[2]} | {r[3]:,} to {r[4]:,} |" for r in bill["rows"])
    steps = lambda e: "\n".join(f"{i + 1}. **{st[0]}.** {st[1]}" for i, st in enumerate(by[e]["steps"]))   # noqa: E731
    safety = " ".join(by["B1"]["safety"] + by["B2"]["safety"] + by["B3"]["safety"])
    head = ", ".join(f"{k} US${lo:,} to {hi:,}" for k, (lo, hi) in bill["headline"].items())
    return f"""# P2 · Teaching lab: pulsed control, vector magnetometry, and deep dopants

{GEN}

**Status: written in full.** Budget: **US${bill['low']:,} to {bill['high']:,}** for the parts listed below (approximate 2026 street prices from the experiment list, estimates and not quotes; the experiment pages give reviewer estimates for complete setups: {head}). Gate verdict in simulation: **{g['verdict']}**.

## Goal

Move from continuous-wave ODMR to pulsed control of an NV ensemble (experiment B1), measure a full magnetic-field vector with the four NV orientations (B2), and measure how deep the boron acceptor in diamond is (B3). These are the skills P3 (single NVs) and P4 (devices) assume.

## Physics and equations

- **Rabi:** P₋₁(t) = (Ω²/Ω_eff²) sin²(πΩ_eff t), Ω_eff = √(Ω² + δ²); a π pulse lasts 1/(2Ω) [rabi1937]. Valid in the rotating-wave limit Ω ≪ D.
- **Ramsey:** the measured contrast follows ½[1 − cos(2πδτ) e^(−(τ/T₂*)²)] (the sign depends on the phase of the last π/2 pulse); the Gaussian envelope comes from quasi-static detunings in an ensemble [ramsey1950] [barry2020].
- **Hahn echo:** C(τ) = e^(−(τ/T₂)ⁿ); the π pulse refocuses static detunings, so T₂ ≫ T₂* [hahn1950]. The stretch n depends on the noise: about 3 for a slow nuclear-spin bath [childress2006] [barry2020]; the simulated data use 1.5.
- **Vector field:** each orientation's half-splitting gives |B·n̂ᵢ|γₑ; for the four tetrahedral axes Σᵢ(B·n̂ᵢ)² = (4/3)|B|², which over-determines the field [rondin2014].
- **Deep acceptor:** p(T) from charge neutrality with E_A = {ar['truth_ev']:g} eV and compensating donors [lagrange1998]; plotting ln(R T^−0.7) against 1/T removes the T^1.5 density of states [sze2006] and the T^−2.2 lattice mobility [pernot2010], so the slope is E_A/k in the compensated regime.

The Qubit Lab, Lattice Lab, and the Equations in Action page run the same equations.

## Machines and consumables

| Part (experiment) | Specification | US$ |
|---|---|---|
{rows}

## Facility and safety

A teaching lab with laser controls. {safety}

## Procedure

B1 (pulsed control):

{steps('B1')}

B2 (vector magnetometry):

{steps('B2')}

B3 (boron activation):

{steps('B3')}

## Expected results (simulated)

The data are simulated by `adamas.experiments` with the values below put in (illustrative values inside the ranges reported for NV ensembles [barry2020]) and fitted by `adamas.fitting`, the code you use on real data.

![Expected P2 results](../img/fig55_build_p2.png)

## Pass/fail

The gate needs all {P2_TESTS} fitted values to pass (plus the echo threshold, which the simulated data clear by a wide margin), so each test is set for {100 * P2_TEST_COVERAGE:.2f} % coverage and a correct setup gets "go" {100 * P2_GATE_COVERAGE:.0f} % of the time: a fit passes when it lands within {rates['k']:.2f} of its own standard errors of the value it should find (Student-t factor {ar['k']:.2f} for E_A, whose fit uses only {ar['points']} points). E_A is compared with the value put in plus the method bias of the T^−0.7 correction, found by fitting the noise-free model. The last column is how often a correct setup passes over {rates['runs']} simulated runs (binomial standard error {100 * rates['se_test']:.1f} percentage points per test, {100 * rates['se_gate']:.1f} for the gate).

| Test | Put in | Fitted | Pass? | Correct setups passing |
|---|---|---|---|---|
| Rabi frequency (π pulse) | {T['rabi_mhz']:g} MHz | {pu['rabi_mhz']:.3f} ± {pu['rabi_err']:.3f} MHz ({pu['pi_ns']:.1f} ns) | {yes(pu['rabi_pass'])} | {100 * rates['rabi_pass']:.1f} % |
| Dephasing T₂* (Ramsey) | {T['t2star_us']:g} µs | {pu['t2star_us']:.3f} ± {pu['t2star_err']:.3f} µs | {yes(pu['t2star_pass'])} | {100 * rates['t2star_pass']:.1f} % |
| Coherence T₂ (echo) | {T['t2_us']:g} µs | {pu['t2_us']:.0f} ± {pu['t2_err']:.0f} µs | {yes(pu['t2_pass'])} | {100 * rates['t2_pass']:.1f} % |
| Field magnitude from four orientations | {ve['truth_mt']:.3f} mT | {ve['b_mt']:.3f} ± {ve['b_err']:.3f} mT (error from a {100 * VECTOR_LINE_REL:g} % line uncertainty) | {yes(ve['pass'])} | {100 * rates['vector']:.1f} % |
| Boron activation energy | {ar['truth_ev']:g} eV (method bias {ar['method_bias_ev']:+.4f}) | {ar['ea_ev']:.3f} ± {ar['ea_err']:.3f} eV | {yes(ar['pass'])} | {100 * rates['arrhenius']:.1f} % |
| Echo outlives dephasing (this project's threshold) | T₂/T₂* > {ECHO_GAIN_MIN:g} | {pu['echo_gain']:.0f} | {yes(pu['echo_pass'])} | |
| **Gate: every row passes** | | | **{yes(g['verdict'] == 'go')}** | **{100 * rates['gate']:.1f} %** |

A correct setup still fails the gate about one time in twenty, so a single "stop" is a reason to repeat the failing measurement, not to abandon the phase. On real data, use each line's fit uncertainty for the field-magnitude error instead of the {100 * VECTOR_LINE_REL:g} % assumed here; P2 tests the field's magnitude, not its direction.

## Not yet simulated

The longitudinal relaxation time T₁ belongs in this phase but has no model in the package yet, so it has no pass/fail criterion here ([STATUS.md](../STATUS.md)).

## Failure modes

- **Microwave power drift** changes Ω between Rabi and Ramsey runs; recalibrate the π pulse before each sequence.
- **Pulse timing:** a π pulse that is not centred lets static detuning back in (the Qubit Lab shows how fast this hurts).
- **Coil heating (B2):** the field drifts as the coils warm; limit duty cycle and recalibrate each axis.
- **Contacts (B3):** non-ohmic contacts on diamond add their own temperature dependence; check the current-voltage curve is straight at every temperature.
- **Uncompensated samples (B3):** the slope approaches E_A/2; the sample's compensation must be known before comparing.

## Decision gate

*Can we hold a spin coherent and measure deep dopants reliably?* {'All simulated tests pass, so the procedure and the analysis are ready; the gate is decided by the measured values on your setup.' if g['verdict'] == 'go' else 'A simulated test fails on this run; a correct setup does that about one time in twenty, so repeat it before changing the analysis.'} Go to P3 when your measured T₂ is long enough for the single-NV gates you plan (the gate budget in E5) and to P4 when the B3 activation energy is reproduced on your samples.

Sources: [rabi1937] [ramsey1950] [hahn1950] [childress2006] [barry2020] [rondin2014] [lagrange1998] [sze2006] [pernot2010] [sewani2020]
"""


def _p3_md() -> str:
    from . import atlas, atlas_prices, nv
    from .experiments import EXPERIMENTS
    by = {e["id"]: e for e in EXPERIMENTS}
    g, b, bill, rates = p3_gate(), p3_degraded(), p3_bill(), p3_pass_rates(P3_RUNS)
    ab, hf, nr = g["antibunching"], g["hyperfine"], g["nuclear_rabi"]
    yes = lambda v: "yes" if v else "no"   # noqa: E731
    pct = lambda v: f"{100 * v:.1f} %"   # noqa: E731
    parts = {"Oil or air objective": "M47", "Scanning": "M48", "Single-photon detectors": "M49", "Time tagger": "M50", "Electronic-grade diamond": "M52", "Microwave and control": "M51"}
    rows = "\n".join(f"| {parts.get(r[1], '')} | {r[1]} ({r[0]}) | {r[2]} | {r[3]:,} to {r[4]:,} |" for r in bill["rows"])
    use = {"M53": "needed for the nuclear-spin test", "M54": "for the charge-state check (not yet simulated)"}
    rows = rows.replace("|  | Laser and optics", "| (not in the Atlas) | Laser and optics")
    rows += "\n" + "\n".join(f"| {m} | {atlas.tool(m)} | {use[m]} | {atlas_prices.short_price(m)} |" for m in bill["unpriced"])
    machines = ", ".join(f"{m} {atlas.tool(m)}" for m in P3_MACHINES)
    steps = "\n".join(f"{i + 1}. **{s[0]}.** {s[1]}" for i, s in enumerate(by["C1"]["steps"]))
    safety = " ".join(by["C1"]["safety"])
    hf_fit = f"{hf['spacing_mhz']:.3f} ± {hf['err']:.3f} MHz, widest line {hf['max_fwhm_mhz']:.2f} MHz" if hf["lines"] == 3 else f"{hf['lines']} line(s) found"
    hb = b["hyperfine"]; hb_fit = f"{hb['spacing_mhz']:.3f} ± {hb['err']:.3f} MHz" if hb["lines"] == 3 else f"{hb['lines']} line(s) found, triplet not resolved"
    return f"""# P3 · Single NV: one emitter and its nuclear spin

{GEN}

**Status: written in full.** Budget: **US${bill['low']:,} to {bill['high']:,}** for the C1 parts listed below (approximate 2026 street prices from the experiment list, estimates and not quotes; the experiment page gives a reviewer estimate of US${bill['headline'][0]:,} to {bill['headline'][1]:,} for a complete setup). The RF source for the nuclear spin and the charge-state laser are not priced yet ([STATUS.md](../STATUS.md)). Gate verdict in simulation: **{g['verdict']}**.

Every input below is **illustrative** (chosen to look like a typical room-temperature confocal setup, not measured), except the ¹⁴N hyperfine constant, which is sourced. The phase is **simulated**: no ADAMAS hardware has run it.

## Goal

Find one nitrogen-vacancy (NV) center, prove it is one (photon antibunching), resolve the ¹⁴N nuclear spin it carries (hyperfine triplet in optically detected magnetic resonance, ODMR), and rotate that nuclear spin coherently (nuclear-spin Rabi). These are the Quantum Device Library's (QDL) QDL-01 (electron-spin qubit cell) and QDL-02 (nuclear-spin memory) on one NV, the pair that QDL-03 (electron–nuclear conditional gate, a controlled-NOT or CNOT) entangles; QDL-03's gate is not tested here, and ¹⁴N is a spin-1 nucleus, so it holds three levels, not two.

## Physics and equations

- **Antibunching:** one emitter cannot give two photons at once, so the normalized coincidence rate g⁽²⁾(τ) = 1 − (1 − g₀) e^(−|τ|/τ₁) dips at zero delay [kurtsiefer2000]. For N identical, independent emitters seen through uncorrelated background, g₀ = 1 − ρ²/N, where ρ is the fraction of detected light that comes from the emitters. Valid for continuous, low-power excitation (the bunching above 1 at longer delays, from the metastable singlet, is neglected) and a detector time resolution much shorter than τ₁. g₀ < 0.5 rules out two or more emitters. Simulated with ρ² = {P3_RHO2:g} for one NV (illustrative), so one NV gives g₀ = {g2_zero_expected(1):.2f}; a second NV adds light but not background, so ρ grows and two NVs give {g2_zero_expected(2):.2f}.
- **Hyperfine triplet:** the ¹⁴N nucleus (spin 1) splits each electron-spin line into three, spaced by |A∥| = {nv.A_PAR_14N_MHZ} MHz [felton2009]. The lines are resolved only when each is narrower than the spacing, so the microwave power must be low (power broadening widens the line). Simulated on the ms = 0 to −1 line in a {P3_BIAS_MT:g} mT axial bias field, which separates it from the ms = +1 line (γₑB = {P3_BIAS_MT * 28.03:.2f} MHz with γₑ = 28.03 MHz/mT [doherty2013]); strain mixing is neglected, valid while γₑB is much larger than the strain splitting E. Line width {P3_ODMR['linewidth_mhz']:g} MHz (illustrative). The test asks whether the triplet is resolved; it does not test the value of |A∥|, whose published uncertainty is not yet recorded here ([STATUS.md](../STATUS.md)).
- **Nuclear-spin Rabi:** a radio-frequency (RF) field drives the nuclear spin; the flipped population is P(t) = (Ω²/Ω_eff²) sin²(πΩ_eff t), Ω_eff = √(Ω² + δ²). Valid in the rotating-wave limit (Ω much smaller than the RF frequency) and over a window short compared with the nuclear coherence time. The model assumes the nucleus starts in one pure state, which green light alone does not give at low field (the three nuclear levels stay about equally populated); optical pumping near the excited-state level anticrossing polarizes it [jacques2009]. The nuclear state is read through the electron: a microwave π pulse selective on one hyperfine line flips the electron only for one nuclear state, then the electron is read optically (the method of [jelezko2004b], shown there on a ¹³C nucleus). In the electron's ms = 0 state the ¹⁴N transitions sit near the quadrupole frequency |P| = 5.016 MHz [felton2009], split by any bias field. Simulated with Ω = {1e3 * P3_NUC_RABI_MHZ:g} kHz (illustrative).

The Photon Lab runs the antibunching equation.

## Machines and consumables

Atlas machines for this phase: {machines}.

| Atlas | Part (experiment) | Specification | US$ |
|---|---|---|---|
{rows}

## Facility and safety

A research lab with an optical table and a laser-controlled area. {safety} Class 3B and 4 lasers need your institution's laser-safety training and a named laser-safety officer before first light; this page does not replace that training.

## Procedure

C1 (find and prove a single NV, resolve its nucleus):

{steps}

Nuclear-spin Rabi (extends C1, uses Atlas M53):

1. **Polarize the nucleus.** Set the axial field near the excited-state level anticrossing, where green light pumps the ¹⁴N spin into one state [jacques2009]; check the polarization from the relative depth of the three hyperfine lines.
2. **Pick a nuclear transition.** The ¹⁴N transitions near |P| move with the field; find the one that starts from the polarized state with an RF sweep read through the electron.
3. **Map the nucleus onto the electron.** Calibrate a microwave π pulse that is selective on one hyperfine line (Rabi frequency well below {nv.A_PAR_14N_MHZ} MHz).
4. **Sweep the RF pulse length.** For each length: polarize with the green laser, apply the RF pulse, apply the selective π pulse, read the electron optically. Record bright (ms = 0) and dark (ms = −1) reference counts in the same run and normalize with them.
5. **Fit.** `python -m adamas.fit rabi nuclear.csv` (time in µs); the transferred population is twice the fitted amplitude.

## Expected results (simulated)

Each test is shown with its **degraded twin**: the same simulation with one physical fault, which the test must catch.

![Expected P3 results](../img/fig56_build_p3.png)

## Pass/fail

The gate needs all {P3_TESTS} tests to pass, so each is set for {100 * P3_TEST_COVERAGE:.2f} % coverage and a correct setup gets "go" at least {100 * P3_GATE_COVERAGE:.0f} % of the time: k = {ab['k']:.2f} standard errors for the one-sided antibunching test and {rates['k']:.2f} for the two-sided nuclear Rabi test. The hyperfine test has its own criterion (resolution, below). Each test draws its own noise, so the tests are independent. Rates are over {rates['runs']} simulated runs (binomial standard error at the design rate: {100 * rates['se_test']:.1f} percentage points per test, {100 * rates['se_gate']:.1f} for the gate).

| Test | Criterion | Put in | Fitted | Pass? | Correct setups passing |
|---|---|---|---|---|---|
| One emitter (antibunching) | g⁽²⁾(0) + kσ < 0.5 | g₀ = {ab['put_in']:.2f} | {ab['g2_zero']:.3f} ± {ab['err']:.3f} | {yes(ab['pass'])} | {pct(rates['antibunching'])} |
| Nuclear spin resolved (hyperfine) | three lines; spacing at least {P3_RESOLVED_SNR:g}σ; every line narrower than the spacing | {hf['reference']} MHz [felton2009] | {hf_fit} | {yes(hf['pass'])} | {pct(rates['hyperfine'])} |
| Nuclear spin driven (Rabi) | transferred population within kσ of 1 | Ω = {nr['put_in_khz']:g} kHz, δ = 0 | {nr['transfer']:.3f} ± {nr['transfer_err']:.3f} ({nr['rabi_khz']:.2f} ± {nr['rabi_err_khz']:.2f} kHz) | {yes(nr['pass'])} | {pct(rates['nuclear_rabi'])} |
| **Gate: every row passes** | | | | **{yes(g['verdict'] == 'go')}** | **{pct(rates['gate'])}** |

The degraded twins, one fault each. The last column is how often the faulty setup wrongly passes.

| Test | Fault | Fitted | Pass? | Faulty setups passing |
|---|---|---|---|---|
| Antibunching | two NVs in the focus (g₀ = {b['antibunching']['put_in']:.2f}) | {b['antibunching']['g2_zero']:.3f} ± {b['antibunching']['err']:.3f} | {yes(b['antibunching']['pass'])} | {pct(rates['degraded']['antibunching'])} |
| Hyperfine | power-broadened line, {P3_BROAD_MHZ:g} MHz wide | {hb_fit} | {yes(hb['pass'])} | {pct(rates['degraded']['hyperfine'])} |
| Nuclear Rabi | RF detuned by one Rabi frequency (half the population moves) | {b['nuclear_rabi']['transfer']:.3f} ± {b['nuclear_rabi']['transfer_err']:.3f} | {yes(b['nuclear_rabi']['pass'])} | {pct(rates['degraded']['nuclear_rabi'])} |

The antibunching and hyperfine tests are not calibrated to {100 * P3_TEST_COVERAGE:.2f} %: their pass rates depend on how far the simulated g₀ sits below 0.5 and how well the lines are resolved, both wide margins here. The nuclear Rabi fit leaves its decay time free over a window with no decay, which inflates the amplitude's error, so that test is also conservative. A single "stop" on real data is a reason to repeat the failing measurement before changing the setup.

## Not yet simulated

- **Single-shot readout** of the nuclear spin (repetitive readout [neumann2010science]) belongs to this phase; the Device Library's readout check covers optical readout only, so it has no criterion here.
- **Charge state** (NV⁻ versus NV⁰) under the green laser, which Atlas M54 measures, has no model in the package yet.
- **The value of |A∥|.** The test checks that the triplet is resolved, not that the spacing reproduces {nv.A_PAR_14N_MHZ} MHz, because the published uncertainty of that constant is not recorded in the package yet.
- **The electron–nuclear gate** (CNOT) is computed in `adamas.register` as a Bell-state fidelity, not a gate fidelity, and is not part of this gate ([STATUS.md](../STATUS.md)).

## Failure modes

- **Two emitters in the spot:** g⁽²⁾(0) near 0.5 or above; move to another spot or use a sample with fewer NVs.
- **Background light:** raises g⁽²⁾(0) for a single NV too; tighten the pinhole and the filters before blaming the emitter.
- **Power broadening:** the triplet merges into one line; lower the microwave power until the lines separate.
- **Detuned RF:** the nuclear Rabi oscillation is faster and never reaches full contrast; re-find the transition with an RF sweep.
- **Drift:** the stage drifts off the NV during long runs; re-centre on the spot between measurements.

## Decision gate

*Do we have single, addressable registers?* {'All simulated tests pass and every degraded twin fails, so the analysis can tell a working register from a broken one; the gate is decided by the measured values on your setup.' if g['verdict'] == 'go' and not any(v['pass'] for v in b.values()) else 'On this run a simulated test fails or a degraded twin passes; a correct setup fails about one time in twenty, so repeat it before changing the analysis.'} Go to P5 (placement) when one emitter, its resolved nucleus, and full nuclear Rabi contrast are measured on the same NV.

Sources: [kurtsiefer2000] [gruber1997] [jelezko2004a] [jelezko2004b] [jacques2009] [felton2009] [doherty2013] [neumann2010science]
"""


def write(folder: str = "docs/build") -> list[str]:
    d = ROOT / folder; d.mkdir(parents=True, exist_ok=True)
    out = []
    for name, text in (("README.md", _index_md()), (DOCS["P0"], _p0_md()), (DOCS["P1"], _p1_md()), (DOCS["P2"], _p2_md()), (DOCS["P3"], _p3_md()), (DOCS["P4"], _p4_md()), (DOCS["P5"], _p5_md()), (DOCS["P6"], _p6_md()), (DOCS["P7"], _p7_md()), (DOCS["P8"], _p8_md())):
        (d / name).write_text(text, encoding="utf-8"); out.append(str(d / name))
    from . import atlas_prices
    out.append(atlas_prices.write(f"{folder}/ATLAS.md"))
    return out


def to_json() -> dict:
    """For the website: the ladder, the P0 gate, the P1 to P8 results, and the priced Machines and Facilities Atlas."""
    g1, b1, g2, b2, b3, b4, b5 = p1_gate(), p1_bill(), p2_gate(), p2_bill(), p3_bill(), p4_bill(), p5_bill()
    return {"phases": PHASES, "docs": DOCS, "p0": p0_gate(), "p1": {**g1, "bill": {"low": b1["low"], "high": b1["high"]}, "pass_rate": p1_pass_rate()},
            "p2": {**g2, "bill": {"low": b2["low"], "high": b2["high"]}, "pass_rates": p2_pass_rates()},
            "p3": _finite({**p3_gate(), "degraded": p3_degraded(), "bill": {"low": b3["low"], "high": b3["high"]}, "pass_rates": p3_pass_rates()}),
            "p4": _finite({**p4_gate(), "degraded": p4_degraded(), "bill": {"low": b4["low"], "high": b4["high"]}, "pass_rates": p4_pass_rates()}),
            "p5": _finite({**p5_gate(), "degraded": p5_degraded(), "bill": {"low": b5["low"], "high": b5["high"]}, "pass_rates": p5_pass_rates()}),
            "p6": _finite({**p6_gate(), "degraded": p6_degraded(), "pass_rates": p6_pass_rates()}),
            "p7": _finite({**p7_gate(), "degraded": p7_degraded(), "pass_rates": p7_pass_rates(), "good_dies": p7_good_dies_table(p7_gate()["yield"]["d0_cm2"])}),
            "p8": _finite({**p8_gate(), "degraded": p8_degraded(), "apps": P8_APPS}), "atlas": _atlas_json()}


def _atlas_json() -> dict:
    from . import atlas_prices
    return atlas_prices.to_json()


def _finite(o):
    """JSON has no NaN: replace non-finite floats (an unresolved fit) with None."""
    if isinstance(o, dict):
        return {k: _finite(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_finite(v) for v in o]
    if isinstance(o, float) and not math.isfinite(o):
        return None
    return o
