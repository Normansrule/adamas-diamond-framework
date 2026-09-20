"""Expert-track figures (17 to 25). Same rule as adamas.figures: every plotted number or equation carries a [bibkey]."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from . import analog, coupling, digital, litho, opensys, qec
from .figures import COLORS, GOLD, GREEN, INK, RED, _finish


def fig_litho_tools(out: Path) -> Path:
    names = list(litho.TOOLS)
    hp = [litho.half_pitch_nm(t.wavelength_nm, t.na, t.k1) for t in litho.TOOLS.values()]
    dof = [litho.depth_of_focus_nm(t.wavelength_nm, t.na) for t in litho.TOOLS.values()]
    fits = [76 in t.wafer_mm for t in litho.TOOLS.values()]
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8))
    bars = axes[0].bar(names, hp, color=[COLORS["Diamond"] if f else COLORS["Si"] for f in fits])
    axes[0].set_yscale("log")
    for b, v in zip(bars, hp):
        axes[0].text(b.get_x() + b.get_width() / 2, v * 1.08, f"{v:.0f} nm", ha="center", fontsize=9)
    axes[0].set_ylabel("Single-exposure half pitch, k₁λ/NA (nm)")
    axes[0].set_title("Resolution by tool (teal: accepts 76 mm wafers natively)")
    axes[0].tick_params(axis="x", rotation=25)
    axes[1].bar(names, dof, color=COLORS["Si"])
    axes[1].set_yscale("log")
    axes[1].axhspan(100, 2000, color=GOLD, alpha=0.25)
    axes[1].text(0.02, 0.93, "gold band: local thickness variation a diamond wafer must beat\n(assumed 0.1 to 2 µm today; measuring it is experiment L-1)",
                 transform=axes[1].transAxes, fontsize=8.5, va="top")
    axes[1].set_ylim(30, 4000)
    axes[1].set_ylabel("Depth of focus, λ/NA² (nm)")
    axes[1].set_title("Focus budget shrinks faster than resolution")
    axes[1].tick_params(axis="x", rotation=25)
    return _finish(fig, out, "fig17_litho_tools.png", "[mack2007] [levinson2019] [wagner2010] [vanschoot2017] [asmleuv2026]; flatness band is an assumption")


def fig_litho_stochastics(out: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.6))
    dose = np.linspace(10, 100, 50)
    for lam, c, lab in [(193.0, COLORS["Si"], "193 nm (6.4 eV photons)"), (13.5, RED, "13.5 nm (92 eV photons)")]:
        axes[0].semilogy(dose, litho.photons_per_nm2(dose, lam), color=c, lw=2.4, label=lab)
    axes[0].set_xlabel("Exposure dose (mJ/cm²)")
    axes[0].set_ylabel("Incident photons per nm²")
    axes[0].set_title("EUV delivers 14× fewer photons per unit dose")
    axes[0].legend()
    axes[0].grid(True, which="both", alpha=0.15)
    e = np.linspace(5, 100, 60)
    for name, (a, z, rho) in litho.SUBSTRATES.items():
        axes[1].loglog(e, litho.kanaya_okayama_range_um(e, a, z, rho), lw=2.4,
                       color=COLORS["Si"] if name == "Silicon" else COLORS["Diamond"], label=name)
    axes[1].set_xlabel("Electron beam energy (keV)")
    axes[1].set_ylabel("Electron range in the substrate (µm)")
    axes[1].set_title("Electron-beam proximity range: shorter in diamond")
    axes[1].legend()
    axes[1].grid(True, which="both", alpha=0.15)
    return _finish(fig, out, "fig18_litho_stochastics_ebeam.png", "[debisschop2017] [gallatin2005] [kanaya1972] [chang1975] [reimer1998]")


def fig_processor_landscape(out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9.6, 5.4))
    for name, n, unit, f, tech, key in digital.REFERENCE_PROCESSORS:
        ax.loglog(n, f, "o", ms=9, color=COLORS["Si"], mec=INK)
        ax.annotate(f"{name}\n[{key}]", (n, f), xytext=(7, 4), textcoords="offset points", fontsize=7.8)
    g = digital.EDGate()
    for n_gates, label in [(770, "“Diamond-4004”, 770 gates"), (12600, "bit-serial RISC-V class, 12,600 gates")]:
        xs, ys = [], []
        for lg in (2.0, 1.0, 0.5):
            est = digital.processor_estimate(n_gates, g.scaled(lg))
            xs.append(n_gates * 3)
            ys.append(est["f_clk_hz"])
        ax.loglog(xs, ys, "-*", ms=13, color=COLORS["Diamond"], mec=INK)
        ax.annotate(label + "\nL = 2, 1, 0.5 µm (model)", (xs[0], ys[0]), xytext=(10, -48), textcoords="offset points",
                    fontsize=8, color=COLORS["Diamond"])
    ax.set_xlabel("Transistors (or gate-equivalents, as reported)")
    ax.set_ylabel("Clock frequency (Hz)")
    ax.set_xlim(80, 1e6)
    ax.set_ylim(10, 3e8)
    ax.set_title("Single-carrier processors that were actually built, and modeled diamond design points")
    ax.grid(True, which="both", alpha=0.15)
    return _finish(fig, out, "fig19_processor_landscape.png",
                   "[faggin1996] [myny2012] [shulaker2013] [hills2019] [biggs2021] [ozer2024]; stars: adamas.digital model after [liu2017] [rabaey2003]")


def fig_logic_scaling(out: Path) -> Path:
    lg = np.logspace(np.log10(0.25), np.log10(4), 30)
    g = digital.EDGate()
    est = [digital.processor_estimate(770, g.scaled(x)) for x in lg]
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    ax.loglog(lg, [e["f_clk_hz"] / 1e6 for e in est], color=COLORS["Diamond"], lw=2.6, label="Clock (MHz), 24 gates per stage")
    ax.loglog(lg, [e["power_w"] for e in est], color=RED, lw=2.6, label="Total power (W), 770 gates")
    ax.loglog(lg, [e["static_fraction"] for e in est], color=INK, lw=1.6, ls="--", label="Static fraction of power")
    ax.axvspan(0.25, 0.5, color=GOLD, alpha=0.2)
    ax.text(0.26, 2.0, "velocity saturation\nnot modeled here", fontsize=8.5)
    ax.set_xlabel("Gate length (µm), constant W/L shrink")
    ax.set_title("Ratioed diamond logic: speed scales, static power does not")
    ax.legend(fontsize=8.5)
    ax.grid(True, which="both", alpha=0.15)
    return _finish(fig, out, "fig20_logic_scaling.png", "[rabaey2003] [meadconway1980] [liu2017] [dennard1974]; adamas.digital model")


def fig_analog(out: Path) -> Path:
    f = digital.EDGate().driver
    i = np.logspace(-7, -3, 80)
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.6))
    axes[0].loglog(i * 1e6, [analog.gm_over_id(f, x) for x in i], color=COLORS["Diamond"], lw=2.4, label="gm/I_D (1/V)")
    axes[0].loglog(i * 1e6, [analog.intrinsic_gain(f, x) for x in i], color=RED, lw=2.4, label="Intrinsic gain gm·r_o (λ = 0.02 /V assumed)")
    axes[0].axhline(38.7, color=INK, ls=":", lw=1)
    axes[0].text(0.12, 45, "weak-inversion ceiling q/kT at 300 K (square law invalid above it)", fontsize=8)
    axes[0].set_xlabel("Drain current (µA), W/L = 8")
    axes[0].set_title("Transconductance efficiency and gain", fontsize=11)
    axes[0].legend(fontsize=8.5)
    axes[0].grid(True, which="both", alpha=0.15)
    ipc = np.logspace(-13, -9, 60)
    for c, col in [(0.01, COLORS["Si"]), (0.05, COLORS["Diamond"]), (0.2, RED)]:
        axes[1].loglog(ipc * 1e12, [analog.pdmr_averaging_time_s(x, c) for x in ipc], color=col, lw=2.4, label=f"contrast {c:.0%}")
    axes[1].set_xlabel("Photocurrent per NV site (pA)")
    axes[1].set_ylabel("Averaging time for signal-to-noise 1 (s)")
    axes[1].set_title("Electrical spin readout noise budget (1 GΩ feedback)", fontsize=11)
    axes[1].legend(fontsize=8.5)
    axes[1].grid(True, which="both", alpha=0.15)
    return _finish(fig, out, "fig21_analog_design.png", "[silveira1996] [razavi2017] [gray2009] [johnson1928] [bourgeois2015] [siyushev2019]; λ is an assumed placeholder")


def fig_lindblad(out: Path) -> Path:
    r = np.linspace(6, 40, 30)
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    ax.plot(r, coupling.gate_fidelity_bound(r, 1.8), color=COLORS["Si"], lw=2, ls="--", label="Simple bound of Chapter 7 (one dephasing channel)")
    for t2, c in [(1.8, COLORS["Diamond"]), (2.4, RED)]:
        ax.plot(r, [opensys.cz_gate_fidelity(x, t2) for x in r], color=c, lw=2.6, label=f"Lindblad, both spins, T₂ = {t2} ms, T₁ = 6 ms")
    ax.plot([25, 25], [0.67, 0.82], "k*", ms=13)
    ax.annotate("measured: 0.67 [dolde2013]\n→ 0.82 with optimal control [dolde2014]", (25, 0.745), xytext=(27, 0.62), fontsize=8.5,
                arrowprops=dict(arrowstyle="->"))
    ax.axhline(0.99, color=INK, ls=":", lw=1)
    ax.set_ylim(0.55, 1.005)
    ax.set_xlabel("Distance between NV centers (nm)")
    ax.set_ylabel("Entangling-gate state fidelity")
    ax.set_title("Open-system simulation of the NV–NV gate")
    ax.legend(fontsize=8.5, loc="lower left")
    ax.grid(True, alpha=0.15)
    return _finish(fig, out, "fig22_lindblad_gate.png", "[lindblad1976] [gorini1976] [dolde2013] [dolde2014] [jarmola2012] [balasubramanian2009] [herbschleb2019]")


def fig_bath_and_dd(out: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.6))
    conc = np.array([0.011, 0.005, 0.002, 0.001, 0.0005, 0.0002])
    med, lo, hi = [], [], []
    for c in conc:
        x = opensys.t2star_us_c13(c, radius_nm=4.0 if c > 0.004 else 8.0, samples=120)
        x = x[np.isfinite(x)]
        med.append(np.median(x)); lo.append(np.percentile(x, 25)); hi.append(np.percentile(x, 75))
    axes[0].fill_between(conc * 100, lo, hi, color=COLORS["Diamond"], alpha=0.25, label="middle 50% of random configurations")
    axes[0].loglog(conc * 100, med, "o-", color=COLORS["Diamond"], lw=2.4, label="median T₂* (model)")
    axes[0].axvline(1.1, color=INK, ls=":")
    axes[0].text(1.0, med[0] * 6, "natural\nabundance", ha="right", fontsize=8.5)
    axes[0].set_xlabel("Carbon-13 concentration (%)")
    axes[0].set_ylabel("T₂* (µs)")
    axes[0].set_title("Isotope purification buys dephasing time")
    axes[0].legend(fontsize=8.5)
    axes[0].grid(True, which="both", alpha=0.15)
    n = np.array([1, 2, 4, 8, 16, 32, 64, 128])
    t2 = np.array([opensys.t2_under_cpmg_us(int(k)) for k in n])
    axes[1].loglog(n, t2, "o-", color=RED, lw=2.4, label="simulated, bath of [delange2010]")
    axes[1].loglog(n, t2[0] * n ** (2 / 3), color=INK, ls="--", lw=1.2, label="N^(2/3) law")
    axes[1].axhline(25.0, color=COLORS["Si"], ls=":")
    axes[1].text(1.1, 27, "bath correlation time τc = 25 µs", fontsize=8.5)
    axes[1].set_xlabel("Number of π pulses, N")
    axes[1].set_ylabel("Coherence time T₂ (µs)")
    axes[1].set_title("Dynamical decoupling in a nitrogen-rich crystal")
    axes[1].legend(fontsize=8.5)
    axes[1].grid(True, which="both", alpha=0.15)
    return _finish(fig, out, "fig23_bath_and_decoupling.png",
                   "[maze2008prb] [dobrovitski2008] [mizuochi2009] [balasubramanian2009] [delange2010] [cywinski2008] [bargill2013]")


def fig_qec(out: Path) -> Path:
    p = np.logspace(-4, np.log10(8e-3), 60)
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    for target, c in [(1e-6, COLORS["Si"]), (1e-9, COLORS["Diamond"]), (1e-12, RED)]:
        cells = [qec.nv_cells_needed(1, x, target)["nv_cells"] for x in p]
        ax.loglog(p, cells, color=c, lw=2.4, label=f"logical error {target:.0e}")
    ax.axvline(8e-3, color=INK, ls=":")
    ax.text(7.5e-3, 14, "electron-nuclear gate,\nroom temperature\n[rong2015]", ha="right", fontsize=8.5)
    ax.axvline(7.8e-4, color=INK, ls=":")
    ax.text(7.4e-4, 14, "[xie2023]", ha="right", fontsize=8.5)
    ax.set_xlabel("Physical error rate per operation")
    ax.set_ylabel("NV cells per logical qubit (4 qubits per cell)")
    ax.set_title("Surface-code overhead expressed in NV cells")
    ax.legend(fontsize=8.5)
    ax.grid(True, which="both", alpha=0.15)
    return _finish(fig, out, "fig24_qec_overhead.png", "[fowler2012] [dennis2002] [rong2015] [xie2023] [waldherr2014]")


def fig_stack_map(out: Path) -> Path:
    """One-page map of the expert track: length scales from wafer to qubit."""
    items = [(76e-3, "3-inch wafer [e6orbray2026]", COLORS["Diamond"]), (1e-3, "quantum chiplet, 1 mm", COLORS["Diamond"]),
             (2e-6, "transistor gate today, 2 µm [liu2017]", COLORS["Si"]), (3.0e-7, "i-line half pitch", COLORS["Si"]),
             (2e-7, "laser-writing accuracy [chen2017]", GREEN), (3e-8, "NV–NV coupling horizon [dolde2013]", RED),
             (1.3e-8, "EUV 0.33 half pitch [asmleuv2026]", COLORS["Si"]), (8e-9, "EUV 0.55 half pitch [asmleuv2026]", COLORS["Si"]),
             (5e-9, "implant straggle at 5 keV [pezzagna2010]", GREEN), (3.567e-10, "lattice constant [wort2008]", INK)]
    fig, ax = plt.subplots(figsize=(13, 4.2))
    ax.set_xscale("log")
    ax.set_xlim(1e-10, 0.3)
    ax.set_ylim(0, 1.15)
    ax.get_yaxis().set_visible(False)
    ax.spines["left"].set_visible(False)
    for k, (x, label, c) in enumerate(items):
        y = [0.2, 0.2, 0.41, 0.62, 1.0, 0.2, 0.41, 0.62, 0.83, 0.2][k]
        ax.plot([x, x], [0, y], color=c, lw=1.5)
        ax.plot(x, y, "o", color=c, ms=7)
        ax.text(x, y + 0.04, label, fontsize=8, ha="center", color=c)
    ax.set_xlabel("Length (m)")
    ax.set_title("Nine orders of magnitude on one wafer")
    return _finish(fig, out, "fig25_length_scales.png", "[e6orbray2026] [liu2017] [chen2017] [dolde2013] [asmleuv2026] [pezzagna2010] [wort2008]")


ALL = [fig_litho_tools, fig_litho_stochastics, fig_processor_landscape, fig_logic_scaling, fig_analog, fig_lindblad,
       fig_bath_and_dd, fig_qec, fig_stack_map]


def make_all(out: str | Path = "docs/img") -> list[Path]:
    return [f(Path(out)) for f in ALL]
