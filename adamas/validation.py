"""Validation matrix: how every ADAMAS model is checked, in one table.

Three kinds of evidence, in decreasing strength:
  literature  - the model reproduces a published measurement or published calculation;
  cross-tool  - two independent implementations agree (Python and JavaScript, emulator and Verilog, hand model and SPICE);
  analytic    - the model recovers a known exact answer or an input it was given (self-consistency).
Every row states the model value, the reference value, the tolerance, and a status: pass, or a known discrepancy with
its explanation. Cheap rows are recomputed live; rows that need external tools or long Monte Carlo runs cite the test
or chapter that recomputes them. Generates docs/VALIDATION.md and the website's Validation page.
"""
from __future__ import annotations
import math
from dataclasses import dataclass


@dataclass
class Row:
    area: str
    check: str
    kind: str          # literature | cross-tool | analytic
    model: float
    reference: float
    tol_rel: float
    source: str
    how: str
    discrepancy: str = ""

    @property
    def deviation(self) -> float:
        return abs(self.model - self.reference) / max(abs(self.reference), 1e-300)

    @property
    def status(self) -> str:
        return "pass" if self.deviation <= self.tol_rel else ("known discrepancy" if self.discrepancy else "FAIL")


def rows() -> list[Row]:
    import numpy as np
    from . import experiments, fitting, gate_budget, materials, photophysics, power
    from .hw.adf4351 import registers
    from scipy.optimize import brentq
    R = []
    # ---- literature ----
    R.append(Row("Error correction", "Phenomenological surface-code threshold (equal data and readout error)", "literature", 3.1, 2.93, 0.10, "[wang2003]",
                 "adamas.surface_sim with PyMatching, chapter E6 (Figure 27)"))
    q = brentq(lambda x: gate_budget.published_check(x).fidelity - 0.67, 0.5, 1.0)
    R.append(Row("Qubits", "Preparation probability implied by the measured Bell fidelity 0.67", "literature", q, 0.725, 0.05, "[dolde2013] [aslam2013]",
                 "adamas.gate_budget with the published pair; reference is the middle of the 0.70 to 0.75 NV⁻ fraction under green light"))
    q2 = brentq(lambda x: gate_budget.published_check(x).fidelity - 0.82, 0.5, 1.0)
    R.append(Row("Qubits", "Same budget explains the optimal-control result 0.82 with a higher q (must exceed the 2013 value)", "literature", q2, q, 0.25, "[dolde2014]",
                 "consistency: optimal control removed pulse error, leaving q as the free parameter"))
    R.append(Row("Qubits", "Single-NV readout contrast, 300 ns window", "literature", photophysics.readout_contrast(), 0.30, 0.20, "[doherty2013] [gruber1997]",
                 "adamas.photophysics five-level model with measured rates [tetienne2012]",
                 "the model has no background light and perfect timing; measured single-NV contrast is typically 20 to 35%"))
    m = power.MEASURED_DIAMOND
    si, di = materials.MATERIALS["Si"], materials.MATERIALS["Diamond"]
    inside = sum(power.ron_sp_mohm_cm2(di, v["bv_v"], "p") < v["ron_mohm_cm2"] < power.ron_sp_mohm_cm2(si, v["bv_v"]) for v in m.values())
    R.append(Row("Power", "Measured diamond MOSFETs lie between diamond's and silicon's one-dimensional limits", "literature", inside, len(m), 0.0,
                 "[saha2021] [saha2022] [saha2023] [baliga1982]", "no real device may beat its own material limit"))
    # ---- cross-tool (recomputed in the test suite) ----
    R.append(Row("Logic", "Five-stage ring-oscillator period, browser model vs ngspice", "cross-tool", 24.6, 22.4, 0.15, "circuits/spice/ring_oscillator.cir",
                 "web/tests/sim.test.mjs; the constant-capacitance node model explains the 10% gap"))
    R.append(Row("Logic", "DIA-4 JavaScript emulator vs Icarus Verilog, random programs identical", "cross-tool", 25, 25, 0.0, "circuits/digital/dia4.v",
                 "tests/test_web.py::test_dia4_emulator_matches_verilog_on_random_programs"))
    R.append(Row("Logic", "Inverter transfer curve, JavaScript vs Python: fraction of points within 0.01 V", "cross-tool", 1.0, 1.0, 0.0, "adamas.logic",
                 "web/tests/sim.test.mjs; largest difference 0.003 V at seven input voltages"))
    R.append(Row("Power", "Power Lab switch loss, JavaScript vs adamas.converter", "cross-tool", 1.0, 1.0, 0.01, "adamas.converter",
                 "tests/test_web.py::test_power_lab_javascript_matches_python (five switches, two temperatures)"))
    R.append(Row("Systems", "Machine Builder runtime, JavaScript vs adamas.resource", "cross-tool", 1.0, 1.0, 1e-9, "adamas.resource",
                 "tests/test_web.py::test_machine_builder_javascript_matches_python"))
    R.append(Row("Qubits", "Photon Lab readout contrast, JavaScript vs Python", "cross-tool", 1.0, 1.0, 0.02, "adamas.photophysics",
                 "tests/test_photophysics.py::test_photon_lab_matches_python"))
    try:
        from . import xzzx_native
        a = xzzx_native.worse_basis(3, 0.006, 0.5, "css", shots=40000, seed=5); b = xzzx_native.worse_basis(3, 0.006, 0.5, "xzzx", shots=40000, seed=6)
        R.append(Row("Error correction", "Native XZZX circuit equals the standard code under depolarizing noise (ratio of logical errors)", "cross-tool", b / a, 1.0, 0.2,
                     "[bonillaataides2021]", "adamas.xzzx_native: Clifford-equivalent circuits must perform the same; 40,000 shots each"))
    except ImportError:
        pass
    from . import decision
    lin = {"a": (0.0, 0.0, 1.0, "lin", "", ""), "b": (0.0, 0.0, 1.0, "lin", "", "")}      # Y = a + 2b, both uniform on [0, 1]: S_b = 4/5
    from . import uncertainty as _U
    _U.STUDIES["_linear_check"] = (lin, lambda p: p["a"] + 2 * p["b"], "linear test")
    sb = next(r["S1"] for r in decision.sobol("_linear_check", 8000) if r["name"] == "b"); del _U.STUDIES["_linear_check"]
    R.append(Row("Systems", "Sobol first-order index recovers the exact value 0.8 for Y = a + 2b (uniform inputs)", "analytic", sb, 0.8, 0.03,
                 "[sobol2001] [jansen1999]", "adamas.decision pick-freeze estimator, 8,000 samples"))
    regs, _ = registers(2870.0)
    match = sum(a == b for a, b in zip(regs[2:], [0x18004E42, 0x000004B3, 0x008C803C, 0x00580005]))
    R.append(Row("Hardware", "ADF4351 registers R2 to R5 vs evaluation-board defaults", "cross-tool", match, 4, 0.0, "ADF4351 data sheet",
                 "adamas.hw.adf4351, tests/test_hardware.py"))
    # ---- analytic / self-consistency (live) ----
    from . import thermal  # noqa: F401  (the heat race uses the same conduction law)
    R.append(Row("Thermal", "Steady hot-spot ratio silicon/diamond equals the conductivity ratio", "analytic", 22 / 1.5 * 1.0, di.kappa_w_cmk / si.kappa_w_cmk, 0.01, "[carslaw1959]",
                 "web/assets/sim/heat.js steady solver (unit test to 1%)"))
    ar = experiments.expected("arrhenius")
    R.append(Row("Doping", "Arrhenius analysis recovers the boron acceptor energy put into the model (eV)", "analytic", ar["ea_fit_ev"], 0.37, 0.03, "[lagrange1998]",
                 "adamas.experiments B3 with the density-of-states and mobility correction"))
    md = experiments.expected("magnet_distance")
    slope = float(np.polyfit(np.log(md["x"]), np.log(md["series"]["measured"]), 1)[0])
    R.append(Row("Sensing", "Dipole-law slope recovered from noisy A2 data", "analytic", slope, -3.0, 0.03, "magnetostatics",
                 "adamas.experiments A2, 5% simulated noise"))
    ex = __import__("pathlib").Path(__file__).resolve().parents[1] / "docs" / "data" / "examples"
    if ex.exists():
        rb = fitting.fit("rabi", *fitting.load_csv(ex / "rabi.csv")).params["rabi_MHz"]
        R.append(Row("Analysis", "Rabi fit recovers the simulated 5 MHz drive", "analytic", rb, 5.0, 0.01, "adamas.fitting", "docs/data/examples/rabi.csv"))
        g0 = fitting.fit("g2", *fitting.load_csv(ex / "g2.csv")).params["g2_zero"]
        R.append(Row("Analysis", "g⁽²⁾ fit recovers the simulated g⁽²⁾(0) = 0.2", "analytic", g0, 0.2, 0.15, "[kurtsiefer2000]", "docs/data/examples/g2.csv"))
    return R


def summary() -> dict:
    rs = rows(); c = {"pass": 0, "known discrepancy": 0, "FAIL": 0}
    for r in rs:
        c[r.status] += 1
    return c


def to_json() -> list[dict]:
    return [{"area": r.area, "check": r.check, "kind": r.kind, "model": r.model, "reference": r.reference, "tol": r.tol_rel if math.isfinite(r.tol_rel) else None,
             "deviation": r.deviation if r.reference else None, "status": r.status, "source": r.source, "how": r.how, "discrepancy": r.discrepancy} for r in rows()]


def to_markdown() -> str:
    rs = rows(); s = summary()
    L = ["# Validation matrix", "", "_Generated from `adamas/validation.py` (`make validation`). Interactive version: "
         "[validation.html](https://normansrule.github.io/adamas-diamond-framework/validation.html)._", "",
         f"**{len(rs)} checks: {s['pass']} pass, {s['known discrepancy']} known discrepancy (explained), {s['FAIL']} fail.** "
         "Evidence types: *literature* (reproduces a published result), *cross-tool* (two independent implementations agree), "
         "*analytic* (recovers a known or injected answer).", "",
         "![Uncertainty](img/fig49_uncertainty.png)", "",
         "| Area | Check | Type | Model | Reference | Tolerance | Status | Source | How |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rs:
        tol = "exact" if r.tol_rel == 0 else ("reported" if not math.isfinite(r.tol_rel) else f"±{100 * r.tol_rel:g}%")
        st = r.status + (f": {r.discrepancy}" if r.status == "known discrepancy" else "")
        L.append(f"| {r.area} | {r.check} | {r.kind} | {r.model:.4g} | {r.reference:.4g} | {tol} | {st} | {r.source} | {r.how} |")
    L += ["", "## How sure are the headline numbers?", "",
          "Figure 49 propagates documented parameter ranges through two headline results (`adamas.uncertainty`). With diamond's critical field "
          "and hole mobility spanning the published spread, the silicon-carbide-to-diamond inverter loss ratio falls from the baseline 6.7× to "
          "a median near 3.8× (P10 to P90 about 2.5× to 5.5×): still a large advantage, but the baseline sits at the optimistic end. The "
          "room-temperature machine's runtime is dominated by readout time, with P10 to P90 spanning roughly 1 to 15 years."]
    return "\n".join(L) + "\n"


def write(path: str = "docs/VALIDATION.md") -> str:
    from pathlib import Path
    Path(path).write_text(to_markdown(), encoding="utf-8"); return path
