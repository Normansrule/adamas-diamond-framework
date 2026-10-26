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

Phases P2 to P8 stay at outline level until their sources are in (docs/STATUS.md says why).
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
    {"id": "P2", "name": "Teaching lab", "budget": "US$1,000 to 12,000 (B tier)", "status": "outline",
     "goal": "Pulsed control (Rabi, Ramsey, echo), T1 and T2, vector magnetometry, boron activation energy.",
     "metric": "π pulse identified; T2* and T2 fitted with uncertainties; E_A within the B3 window.",
     "gate": "Can we hold a spin coherent and measure deep dopants reliably?"},
    {"id": "P3", "name": "Single NV", "budget": "US$10,000 to 100,000 (C tier)", "status": "outline",
     "goal": "Confocal microscope, antibunching, single-spin control, nuclear-spin register.",
     "metric": "g2(0) < 0.5; hyperfine-resolved ODMR; nuclear-spin Rabi.", "gate": "Do we have single, addressable registers?"},
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


def _index_md() -> str:
    rows = "\n".join(f"| {p['id']} | {p['name']} | {p['budget']} | {p['goal']} | {p['gate']} | {'[written](' + p['id'] + '_' + ('simulation' if p['id'] == 'P0' else 'proof_of_concept') + '.md)' if p['status'] == 'written' else 'outline'} |" for p in PHASES)
    return f"""# Build program

{GEN}

A ladder from a laptop to a pilot line. Each phase ends at a decision gate. P0 and P1 are written in full, with their gates evaluated by code; P2 to P8 are outlined in [phase0/BUILD_PROGRAM_OUTLINE.md](../phase0/BUILD_PROGRAM_OUTLINE.md) and are written one per release as their sources come in ([STATUS.md](../STATUS.md)).

| Phase | Name | Budget | Goal | Gate question | Status |
|---|---|---|---|---|---|
{rows}
"""


def write(folder: str = "docs/build") -> list[str]:
    d = ROOT / folder; d.mkdir(parents=True, exist_ok=True)
    out = []
    for name, text in (("README.md", _index_md()), ("P0_simulation.md", _p0_md()), ("P1_proof_of_concept.md", _p1_md())):
        (d / name).write_text(text, encoding="utf-8"); out.append(str(d / name))
    return out


def to_json() -> dict:
    """For the website: the ladder, the P0 gate, and the P1 simulated results."""
    g1 = p1_gate(); b = p1_bill()
    return {"phases": PHASES, "p0": p0_gate(), "p1": {**g1, "bill": {"low": b["low"], "high": b["high"]}, "pass_rate": p1_pass_rate()}}
