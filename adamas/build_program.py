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

* P2 Teaching lab and P3 Single NV are written in full too; their tests are set so a correct setup passes the whole gate
  95 % of the time, and P3 runs each test on a degraded twin (one physical fault) that must fail.

Phases P4 to P8 stay at outline level until their sources are in (docs/STATUS.md says why).
"""
from __future__ import annotations

import math
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
    {"id": "P4", "name": "Devices", "budget": "university cleanroom", "status": "outline",
     "goal": "Hydrogen-terminated FETs with Al2O3; I-V, breakdown, and temperature tests.",
     "metric": "Working FETs on a hot chuck; mobility, threshold, and contact resistance extracted.", "gate": "Do our devices match the models, run to run?"},
    {"id": "P5", "name": "Placement", "budget": "shared facility", "status": "outline",
     "goal": "Implant through masks, anneal, conversion statistics, NV pairs closer than 30 nm.",
     "metric": "Conversion yield measured; coupled pairs found; Bell fidelity above 0.5.", "gate": "Is placement yield good enough to plan arrays?"},
    {"id": "P6", "name": "Integration", "budget": "packaging line or MPW partner", "status": "outline",
     "goal": "Diamond chiplets bonded to silicon CMOS control; multi-cell arrays.",
     "metric": "Chiplet works after bonding; repetition-code gain (criterion to define).", "gate": "Does integration keep coherence and yield?"},
    {"id": "P7", "name": "Pilot line and products", "budget": "fab", "status": "outline",
     "goal": "Wafer-scale flow, statistical process control, first products.",
     "metric": "Defect density and yield on control charts; first product qualified.", "gate": "Which product line pays for the line?"},
    {"id": "P8", "name": "Frontier and humanity", "budget": "application-specific", "status": "outline",
     "goal": "Grid and EV efficiency, space electronics, medical magnetometry, navigation.",
     "metric": "Honest technology readiness level per application.", "gate": "Where does diamond beat the incumbent, with evidence?"},
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
P3_TEST_COVERAGE = P3_GATE_COVERAGE ** (1 / P3_TESTS)     # so each test covers 98.30 % (independent tests)
P3_RUNS = 400
P3_RHO2 = 0.8                # signal fraction squared, rho^2 = (S / (S + B))^2: illustrative background, as in experiment C1
P3_TAU_NS = 12.0             # antibunching time constant of the simulated data (illustrative, as in experiment C1)
P3_G2_NOISE = 0.03           # per 1 ns bin of the normalized histogram (illustrative)
P3_ODMR = {"contrast": 0.25, "linewidth_mhz": 0.4, "noise": 0.01}          # one NV, low microwave power (illustrative)
P3_BROAD_MHZ = 3.0           # degraded twin: power-broadened line, wider than the 2.147 MHz spacing
P3_NUC_RABI_MHZ = 0.01       # 10 kHz nuclear Rabi frequency (illustrative); [jelezko2004b] showed the oscillation
P3_NUC_NOISE = 0.05          # per point, after normalizing with bright (ms = 0) and dark (ms = -1) reference counts (illustrative)


def _k3() -> float:
    return _k_normal(P3_TEST_COVERAGE)


def g2_zero_expected(emitters: int = 1, rho2: float = P3_RHO2) -> float:
    """g2(0) of N identical, independent emitters seen through uncorrelated background: 1 - rho^2 / N, where rho is the
    fraction of detected light that comes from the emitters. Valid for continuous excitation and a detector time
    resolution much shorter than the antibunching time; one emitter with no background gives 0 [kurtsiefer2000]."""
    return 1.0 - rho2 / emitters


def _g2_data(seed: int, emitters: int):
    r = np.random.default_rng(seed); tau = np.linspace(-80, 80, 161); g0 = g2_zero_expected(emitters)
    return tau, 1 - (1 - g0) * np.exp(-np.abs(tau) / P3_TAU_NS) + r.normal(0, P3_G2_NOISE, tau.size), g0


def _nuc_data(seed: int, detuning_mhz: float):
    r = np.random.default_rng(seed); t = np.linspace(0.0, 300.0, 121)          # µs
    om = P3_NUC_RABI_MHZ; oe = math.hypot(om, detuning_mhz)
    return t, (om / oe) ** 2 * np.sin(np.pi * oe * t) ** 2 + r.normal(0, P3_NUC_NOISE, t.size)


def p3_antibunching(seed: int = 4, emitters: int = 1) -> dict:
    """C1, Hanbury Brown-Twiss: simulate the normalized coincidence histogram g2(tau) = 1 - (1 - g0) exp(-|tau|/tau1)
    with g0 from g2_zero_expected, fit with adamas.fitting.fit_g2, and pass when g2(0) + k sigma < 0.5 (one emitter).
    The degraded twin has two emitters in the focus (emitters=2), the one physical fault this test must catch."""
    from . import fitting
    tau, y, g0 = _g2_data(seed, emitters)
    f = fitting.fit_g2(tau, y); v, e = float(f.params["g2_zero"]), float(f.errors["g2_zero"])
    return {"emitters": emitters, "put_in": g0, "g2_zero": v, "err": e, "k": _k3(), "pass": bool(v + _k3() * e < 0.5)}


def p3_hyperfine(seed: int = 4, linewidth_mhz: float = P3_ODMR["linewidth_mhz"]) -> dict:
    """C1, low-power ODMR of one NV at zero field: three lines split by the 14N hyperfine coupling |A_par| = 2.147 MHz
    [felton2009] (adamas.nv). Fit with adamas.fitting.fit_odmr (up to three lines); pass when exactly three lines are
    found and their mean spacing (outer separation / 2) lies within k of its standard error of |A_par|. The degraded
    twin is power-broadened (linewidth P3_BROAD_MHZ, wider than the spacing), so the triplet is not resolved."""
    from . import fitting, nv
    r = np.random.default_rng(seed); f = np.linspace(2863.0, 2877.0, 281)
    y = nv.odmr_spectrum(f, np.zeros(3), axes=np.array([[0, 0, 1.0]]), contrast=P3_ODMR["contrast"], linewidth_mhz=linewidth_mhz, hyperfine=True) \
        + r.normal(0, P3_ODMR["noise"], f.size)
    out = {"linewidth_mhz": linewidth_mhz, "put_in": nv.A_PAR_14N_MHZ, "lines": 0, "spacing_mhz": float("nan"), "err": float("nan"), "k": _k3(), "pass": False}
    try:
        fit = fitting.fit_odmr(f, y, max_lines=3)
    except (ValueError, RuntimeError):
        return out
    c = sorted((fit.params[k], fit.errors[f"center{k[6:]}"]) for k in fit.params if k.startswith("center"))
    out["lines"] = len(c)
    if len(c) == 3:
        a, e = (c[2][0] - c[0][0]) / 2, math.hypot(c[2][1], c[0][1]) / 2
        out.update(spacing_mhz=float(a), err=float(e), pass_=bool(np.isfinite(e) and abs(a - nv.A_PAR_14N_MHZ) <= _k3() * e))
        out["pass"] = out.pop("pass_")
    return out


def p3_nuclear_rabi(seed: int = 4, detuning_mhz: float = 0.0) -> dict:
    """C1 extended: drive the 14N nuclear spin with an RF pulse of growing length and read it out through the electron
    (a nuclear-state-selective microwave pi pulse, then optical readout), as in [jelezko2004b]. The normalized signal is
    the flipped population P(t) = (Omega^2 / Omega_eff^2) sin^2(pi Omega_eff t), Omega_eff = sqrt(Omega^2 + delta^2)
    (rotating-wave limit, Omega much smaller than the RF frequency; no decay over the window). Fit with
    adamas.fitting.fit_rabi; the transferred population is twice the fitted amplitude. Pass when it is consistent with
    full transfer, |transfer - 1| <= k sigma: the drive is on resonance with an addressable nuclear transition. The degraded
    twin is driven off resonance by one Rabi frequency, so only half the population moves."""
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
    which the degraded twin wrongly passes. Binomial standard error of a rate p: sqrt(p (1 - p) / runs)."""
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
    not quotes). The RF source for the nuclear spin (Atlas M53) has no sourced price and is listed without one."""
    from .experiments import EXPERIMENTS
    by = {e["id"]: e for e in EXPERIMENTS}
    rows = [("C1", *p) for p in by["C1"]["parts"]]
    return {"rows": rows, "low": sum(r[3] for r in rows), "high": sum(r[4] for r in rows), "headline": by["C1"]["cost"], "unpriced": ["M53"]}


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
    a = ax[1]; f = np.linspace(2863.0, 2877.0, 281)
    for lw, col, lab, off in ((P3_ODMR["linewidth_mhz"], COLORS["Diamond"], "low power", 0.0), (P3_BROAD_MHZ, RED, "power-broadened (degraded twin)", -0.12)):
        y = nv.odmr_spectrum(f, np.zeros(3), axes=np.array([[0, 0, 1.0]]), contrast=P3_ODMR["contrast"], linewidth_mhz=lw, hyperfine=True) + np.random.default_rng(4).normal(0, P3_ODMR["noise"], f.size)
        a.plot(f, y + off, ".", ms=2.5, color=col, label=lab)
    hf = g["hyperfine"]; a.legend(fontsize=8, loc="lower left")
    a.set_title(f"2. Hyperfine triplet: spacing {hf['spacing_mhz']:.3f} ± {hf['err']:.3f} MHz (|A∥| {nv.A_PAR_14N_MHZ} MHz)", fontsize=10.5)
    a.set_xlabel("microwave frequency (MHz)"); a.set_ylabel("fluorescence (normalized; red offset −0.12)")
    a = ax[2]
    for det, col, lab in ((0.0, COLORS["Diamond"], "on resonance"), (P3_NUC_RABI_MHZ, RED, "detuned by Ω (degraded twin)")):
        x, y = _nuc_data(4, det); a.plot(x, y, ".", ms=3, color=col, alpha=.6)
        r = p3_nuclear_rabi(detuning_mhz=det); fit = fitting.fit_rabi(x, y)
        a.plot(fit.x, fit.model, color=col, lw=2, label=f"{lab}: transfer {r['transfer']:.2f} ± {r['transfer_err']:.2f}")
    a.set_ylim(-0.2, 1.45); a.legend(fontsize=8, loc="upper right")
    a.set_title(f"3. Nuclear-spin Rabi: {g['nuclear_rabi']['rabi_khz']:.2f} ± {g['nuclear_rabi']['rabi_err_khz']:.2f} kHz", fontsize=10.5)
    a.set_xlabel("RF pulse length (µs)"); a.set_ylabel("flipped nuclear population")
    return _finish(fig, out, "fig56_build_p3.png", "simulated and fitted by adamas.build_program and adamas.fitting (illustrative inputs); [kurtsiefer2000] [felton2009] [jelezko2004b]")


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


DOCS = {"P0": "P0_simulation.md", "P1": "P1_proof_of_concept.md", "P2": "P2_teaching_lab.md", "P3": "P3_single_nv.md"}


def _index_md() -> str:
    rows = "\n".join(f"| {p['id']} | {p['name']} | {p['budget']} | {p['goal']} | {p['gate']} | {'[written](' + DOCS[p['id']] + ')' if p['status'] == 'written' else 'outline'} |" for p in PHASES)
    done = [p["id"] for p in PHASES if p["status"] == "written"]
    return f"""# Build program

{GEN}

A ladder from a laptop to a pilot line. Each phase ends at a decision gate. {', '.join(done[:-1])} and {done[-1]} are written in full, with their gates evaluated by code; the rest are outlined in [phase0/BUILD_PROGRAM_OUTLINE.md](../phase0/BUILD_PROGRAM_OUTLINE.md) and are written one per release as their sources come in ([STATUS.md](../STATUS.md)).

| Phase | Name | Budget | Goal | Gate question | Status |
|---|---|---|---|---|---|
{rows}
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
    from . import atlas, nv
    from .experiments import EXPERIMENTS
    by = {e["id"]: e for e in EXPERIMENTS}
    g, b, bill, rates = p3_gate(), p3_degraded(), p3_bill(), p3_pass_rates(P3_RUNS)
    ab, hf, nr = g["antibunching"], g["hyperfine"], g["nuclear_rabi"]
    yes = lambda v: "yes" if v else "no"   # noqa: E731
    pct = lambda v: f"{100 * v:.1f} %"   # noqa: E731
    parts = {"Oil or air objective": "M47", "Scanning": "M48", "Single-photon detectors": "M49", "Time tagger": "M50", "Electronic-grade diamond": "M52", "Microwave and control": "M51"}
    rows = "\n".join(f"| {parts.get(r[1], '')} | {r[1]} ({r[0]}) | {r[2]} | {r[3]:,} to {r[4]:,} |" for r in bill["rows"])
    rows += "\n" + "\n".join(f"| {m} | {atlas.tool(m)} | needed for the nuclear-spin test | not priced (no source yet) |" for m in bill["unpriced"])
    machines = ", ".join(f"{m} {atlas.tool(m)}" for m in P3_MACHINES)
    steps = "\n".join(f"{i + 1}. **{s[0]}.** {s[1]}" for i, s in enumerate(by["C1"]["steps"]))
    safety = " ".join(by["C1"]["safety"])
    hf_fit = f"{hf['spacing_mhz']:.3f} ± {hf['err']:.3f} MHz" if hf["lines"] == 3 else f"{hf['lines']} line(s) found"
    hb = b["hyperfine"]; hb_fit = f"{hb['spacing_mhz']:.3f} ± {hb['err']:.3f} MHz" if hb["lines"] == 3 else f"{hb['lines']} line(s) found, triplet not resolved"
    return f"""# P3 · Single NV: one emitter, its nuclear spin, and a two-qubit register

{GEN}

**Status: written in full.** Budget: **US${bill['low']:,} to {bill['high']:,}** for the C1 parts listed below (approximate 2026 street prices from the experiment list, estimates and not quotes; the experiment page gives a reviewer estimate of US${bill['headline'][0]:,} to {bill['headline'][1]:,} for a complete setup). The RF source for the nuclear spin is not priced yet ([STATUS.md](../STATUS.md)). Gate verdict in simulation: **{g['verdict']}**.

Every input below is **illustrative** (chosen to look like a typical room-temperature confocal setup, not measured), except the ¹⁴N hyperfine constant, which is sourced. The phase is **simulated**: no ADAMAS hardware has run it.

## Goal

Find one NV center, prove it is one (photon antibunching), resolve the ¹⁴N nuclear spin it carries (hyperfine triplet), and rotate that nuclear spin coherently (nuclear-spin Rabi). These are the Device Library's QDL-01 (electron-spin qubit cell) and QDL-02 (nuclear-spin memory) on one NV, the pair that QDL-03 (electron–nuclear conditional gate) entangles; QDL-03's gate is not tested here.

## Physics and equations

- **Antibunching:** one emitter cannot give two photons at once, so the normalized coincidence rate g⁽²⁾(τ) = 1 − (1 − g₀) e^(−|τ|/τ₁) dips at zero delay [kurtsiefer2000]. For N identical, independent emitters seen through uncorrelated background, g₀ = 1 − ρ²/N, where ρ is the fraction of detected light that comes from the emitters. Valid for continuous excitation and a detector time resolution much shorter than τ₁. g₀ < 0.5 rules out two or more emitters. Simulated with ρ² = {P3_RHO2:g} (illustrative), so one NV gives g₀ = {g2_zero_expected(1):.2f} and two give {g2_zero_expected(2):.2f}.
- **Hyperfine triplet:** the ¹⁴N nucleus (spin 1) splits each electron-spin line into three, spaced by |A∥| = {nv.A_PAR_14N_MHZ} MHz [felton2009]. The lines are resolved only when each is narrower than the spacing, so the microwave power must be low (power broadening widens the line). Simulated at zero field with a {P3_ODMR['linewidth_mhz']:g} MHz line width (illustrative).
- **Nuclear-spin Rabi:** an RF field drives the nuclear spin; the flipped population is P(t) = (Ω²/Ω_eff²) sin²(πΩ_eff t), Ω_eff = √(Ω² + δ²). Valid in the rotating-wave limit (Ω much smaller than the RF frequency) and over a window short compared with the nuclear coherence time. The nuclear state is read through the electron: a microwave π pulse selective on one hyperfine line flips the electron only for one nuclear state, then the electron is read optically [jelezko2004b]. In the electron's ms = 0 state the ¹⁴N transitions sit near the quadrupole frequency |P| = 5.016 MHz [felton2009], split by any bias field. Simulated with Ω = {1e3 * P3_NUC_RABI_MHZ:g} kHz (illustrative).

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

1. **Pick a nuclear transition.** Apply a small bias field along the NV axis so the ¹⁴N transitions near |P| no longer overlap; find the one you want with an RF sweep read through the electron.
2. **Map the nucleus onto the electron.** Calibrate a microwave π pulse that is selective on one hyperfine line (Rabi frequency well below {nv.A_PAR_14N_MHZ} MHz).
3. **Sweep the RF pulse length.** For each length: initialize with the green laser, apply the RF pulse, apply the selective π pulse, read the electron optically. Record bright (ms = 0) and dark (ms = −1) reference counts in the same run and normalize with them.
4. **Fit.** `python -m adamas.fit rabi nuclear.csv` (time in µs); the transferred population is twice the fitted amplitude.

## Expected results (simulated)

Each test is shown with its **degraded twin**: the same simulation with one physical fault, which the test must catch.

![Expected P3 results](../img/fig56_build_p3.png)

## Pass/fail

The gate needs all {P3_TESTS} tests to pass, so each is set for {100 * P3_TEST_COVERAGE:.2f} % coverage and a correct setup gets "go" at least {100 * P3_GATE_COVERAGE:.0f} % of the time: k = {rates['k']:.2f} standard errors. Rates are over {rates['runs']} simulated runs (binomial standard error {100 * rates['se_test']:.1f} percentage points per test, {100 * rates['se_gate']:.1f} for the gate).

| Test | Criterion | Put in | Fitted | Pass? | Correct setups passing |
|---|---|---|---|---|---|
| One emitter (antibunching) | g⁽²⁾(0) + kσ < 0.5 | g₀ = {ab['put_in']:.2f} | {ab['g2_zero']:.3f} ± {ab['err']:.3f} | {yes(ab['pass'])} | {pct(rates['antibunching'])} |
| Nuclear spin resolved (hyperfine) | three lines; mean spacing within kσ of {nv.A_PAR_14N_MHZ} MHz [felton2009] | {hf['put_in']} MHz | {hf_fit} | {yes(hf['pass'])} | {pct(rates['hyperfine'])} |
| Nuclear spin driven (Rabi) | transferred population within kσ of 1 | Ω = {nr['put_in_khz']:g} kHz, δ = 0 | {nr['transfer']:.3f} ± {nr['transfer_err']:.3f} ({nr['rabi_khz']:.2f} ± {nr['rabi_err_khz']:.2f} kHz) | {yes(nr['pass'])} | {pct(rates['nuclear_rabi'])} |
| **Gate: every row passes** | | | | **{yes(g['verdict'] == 'go')}** | **{pct(rates['gate'])}** |

The degraded twins, one fault each. The last column is how often the faulty setup wrongly passes.

| Test | Fault | Fitted | Pass? | Faulty setups passing |
|---|---|---|---|---|
| Antibunching | two NVs in the focus (g₀ = {b['antibunching']['put_in']:.2f}) | {b['antibunching']['g2_zero']:.3f} ± {b['antibunching']['err']:.3f} | {yes(b['antibunching']['pass'])} | {pct(rates['degraded']['antibunching'])} |
| Hyperfine | power-broadened line, {P3_BROAD_MHZ:g} MHz wide | {hb_fit} | {yes(hb['pass'])} | {pct(rates['degraded']['hyperfine'])} |
| Nuclear Rabi | RF detuned by one Rabi frequency (half the population moves) | {b['nuclear_rabi']['transfer']:.3f} ± {b['nuclear_rabi']['transfer_err']:.3f} | {yes(b['nuclear_rabi']['pass'])} | {pct(rates['degraded']['nuclear_rabi'])} |

The antibunching test passes correct setups more often than its {100 * P3_TEST_COVERAGE:.2f} % design because it is one-sided and the simulated g₀ sits well below 0.5. The nuclear Rabi fit leaves its decay time free over a window with no decay, which inflates the amplitude's error, so that test is also conservative. A single "stop" on real data is a reason to repeat the failing measurement before changing the setup.

## Not yet simulated

- **Single-shot readout** of the nuclear spin (repetitive readout [neumann2010science]) belongs to this phase; the Device Library's readout check covers optical readout only, so it has no criterion here.
- **Charge state** (NV⁻ versus NV⁰) under the green laser, which Atlas M54 measures, has no model in the package yet.
- **The electron–nuclear gate** (CNOT) is computed in `adamas.register` as a Bell-state fidelity, not a gate fidelity, and is not part of this gate ([STATUS.md](../STATUS.md)).

## Failure modes

- **Two emitters in the spot:** g⁽²⁾(0) near 0.5 or above; move to another spot or use a sample with fewer NVs.
- **Background light:** raises g⁽²⁾(0) for a single NV too; tighten the pinhole and the filters before blaming the emitter.
- **Power broadening:** the triplet merges into one line; lower the microwave power until the lines separate.
- **Detuned RF:** the nuclear Rabi oscillation is faster and never reaches full contrast; re-find the transition with an RF sweep.
- **Drift:** the stage drifts off the NV during long runs; re-centre on the spot between measurements.

## Decision gate

*Do we have single, addressable registers?* {'All simulated tests pass and every degraded twin fails, so the analysis can tell a working register from a broken one; the gate is decided by the measured values on your setup.' if g['verdict'] == 'go' and not any(v['pass'] for v in b.values()) else 'On this run a simulated test fails or a degraded twin passes; a correct setup fails about one time in twenty, so repeat it before changing the analysis.'} Go to P5 (placement) when one emitter, its resolved nucleus, and full nuclear Rabi contrast are measured on the same NV.

Sources: [kurtsiefer2000] [gruber1997] [jelezko2004a] [jelezko2004b] [felton2009] [doherty2013] [neumann2010science]
"""


def write(folder: str = "docs/build") -> list[str]:
    d = ROOT / folder; d.mkdir(parents=True, exist_ok=True)
    out = []
    for name, text in (("README.md", _index_md()), (DOCS["P0"], _p0_md()), (DOCS["P1"], _p1_md()), (DOCS["P2"], _p2_md()), (DOCS["P3"], _p3_md())):
        (d / name).write_text(text, encoding="utf-8"); out.append(str(d / name))
    return out


def to_json() -> dict:
    """For the website: the ladder, the P0 gate, and the P1, P2 and P3 simulated results."""
    g1, b1, g2, b2, b3 = p1_gate(), p1_bill(), p2_gate(), p2_bill(), p3_bill()
    return {"phases": PHASES, "docs": DOCS, "p0": p0_gate(), "p1": {**g1, "bill": {"low": b1["low"], "high": b1["high"]}, "pass_rate": p1_pass_rate()},
            "p2": {**g2, "bill": {"low": b2["low"], "high": b2["high"]}, "pass_rates": p2_pass_rates()},
            "p3": _finite({**p3_gate(), "degraded": p3_degraded(), "bill": {"low": b3["low"], "high": b3["high"]}, "pass_rates": p3_pass_rates()})}


def _finite(o):
    """JSON has no NaN: replace non-finite floats (an unresolved fit) with None."""
    if isinstance(o, dict):
        return {k: _finite(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_finite(v) for v in o]
    if isinstance(o, float) and not math.isfinite(o):
        return None
    return o
