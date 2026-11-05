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

* P2 Teaching lab, P3 Single NV and P4 Devices are written in full too; their tests are set so a correct setup passes the whole gate
  95 % of the time, and P3 and P4 run each test on a degraded twin (one physical or process fault) that must fail.

Phases P5 to P8 stay at outline level until their sources are in (docs/STATUS.md says why).
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
    {"id": "P4", "name": "Devices", "budget": "computed from the C2 part list", "status": "written",
     "goal": "Hydrogen-terminated FETs with Al2O3: contact resistance, threshold matching, mobility and threshold on the PDK-0 monitor die (breakdown and hot tests are not simulated yet).",
     "metric": "Contact resistance (TLM) at most 10 ohm mm; threshold spread within 200 mV; mobility and threshold match the PDK-0 model; each degraded twin fails.", "gate": "Do our devices match the models, run to run?"},
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
    from . import atlas
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
    rows += "\n" + "\n".join(f"| {k} | {acr['MPCVD'] if k == 'M01' else atlas.tool(k)} | {use[k]} | not priced (no source yet) |" for k in bill["unpriced"])
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
- **Photoelectric NV readout** (Atlas M55, listed in the outline for P4 and P6): belongs with the quantum track and is left to P6.

## Failure modes

- **Contact residue:** high R_c with a normal R_sh; keep the surface clean and the time short between hydrogen termination (S08) and the gold (S09).
- **Lost termination:** high R_sh everywhere, or patchy termination that shows as a large threshold spread; repeat the hydrogen plasma (S08) and store in clean nitrogen.
- **Oxide thickness off:** mobility off by the oxide ratio; measure C_ox on the MOS capacitor and check the ALD cycle count.
- **Threshold drift during hot tests:** mobile charge or NO₂ desorption (traveler S17); use the high-temperature oxide option for hot operation.

## Decision gate

*Do our devices match the models, and is the process stable from run to run?* {verdict} Run-to-run stability needs at least two runs through the same checks; go to P6 when both runs pass and the measured mobility and threshold have been entered into the models.

Sources: [sze2006] [pelgrom1989] [kawarada2014] [kawarada2023] [kasu2012] [liu2017]
"""


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


DOCS = {"P0": "P0_simulation.md", "P1": "P1_proof_of_concept.md", "P2": "P2_teaching_lab.md", "P3": "P3_single_nv.md", "P4": "P4_devices.md"}


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
    use = {"M53": "needed for the nuclear-spin test", "M54": "for the charge-state check (not yet simulated)"}
    rows = rows.replace("|  | Laser and optics", "| (not in the Atlas) | Laser and optics")
    rows += "\n" + "\n".join(f"| {m} | {atlas.tool(m)} | {use[m]} | not priced (no source yet) |" for m in bill["unpriced"])
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
    for name, text in (("README.md", _index_md()), (DOCS["P0"], _p0_md()), (DOCS["P1"], _p1_md()), (DOCS["P2"], _p2_md()), (DOCS["P3"], _p3_md()), (DOCS["P4"], _p4_md())):
        (d / name).write_text(text, encoding="utf-8"); out.append(str(d / name))
    return out


def to_json() -> dict:
    """For the website: the ladder, the P0 gate, and the P1 to P4 simulated results."""
    g1, b1, g2, b2, b3, b4 = p1_gate(), p1_bill(), p2_gate(), p2_bill(), p3_bill(), p4_bill()
    return {"phases": PHASES, "docs": DOCS, "p0": p0_gate(), "p1": {**g1, "bill": {"low": b1["low"], "high": b1["high"]}, "pass_rate": p1_pass_rate()},
            "p2": {**g2, "bill": {"low": b2["low"], "high": b2["high"]}, "pass_rates": p2_pass_rates()},
            "p3": _finite({**p3_gate(), "degraded": p3_degraded(), "bill": {"low": b3["low"], "high": b3["high"]}, "pass_rates": p3_pass_rates()}),
            "p4": _finite({**p4_gate(), "degraded": p4_degraded(), "bill": {"low": b4["low"], "high": b4["high"]}, "pass_rates": p4_pass_rates()})}


def _finite(o):
    """JSON has no NaN: replace non-finite floats (an unresolved fit) with None."""
    if isinstance(o, dict):
        return {k: _finite(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_finite(v) for v in o]
    if isinstance(o, float) and not math.isfinite(o):
        return None
    return o
