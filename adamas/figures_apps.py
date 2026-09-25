"""Application-track figures (28 to 34): power circuits versus SiC and GaN, thermal ceilings, application map,
silicon-versus-diamond radar, and the size of a room-temperature quantum computer."""
from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from . import converter, gate_budget, materials, pdk0, scaling, thermal
from .figures import COLORS, GOLD, GREEN, INK, RED, _finish

NAMES = ["Si", "4H-SiC", "GaN", "Diamond"]
LABEL = {"Si": "Silicon", "4H-SiC": "Silicon carbide", "GaN": "Gallium nitride", "Diamond": "Diamond (ideal, holes)"}


def fig_ron_temperature(out: Path) -> Path:
    t = np.linspace(300, 650, 120)
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    for n in NAMES:
        ax.plot(t - 273.15, [converter.ron_temperature_factor(n, x) for x in t], color=COLORS[n], lw=2.4,
                label=LABEL[n].replace(" (ideal, holes)", ", bulk boron-doped drift"))
    ax.plot(t - 273.15, [converter.ron_temperature_factor("Diamond", x, bulk_doped=False) for x in t], color=COLORS["Diamond"],
            lw=2, ls="--", label="Diamond hole-gas channel (no ionization gain)")
    for n in NAMES:
        ax.axvline(converter.TJ_MAX_C[n], color=COLORS[n], ls=":", lw=1)
    ax.text(170, 0.1, "Si ceiling", fontsize=8, rotation=90, color=COLORS["Si"])
    ax.text(395, 0.1, "diamond demonstrated", fontsize=8, rotation=90, color=COLORS["Diamond"])
    ax.set_yscale("log"); ax.set_ylim(0.08, 10)
    ax.set_xlabel("Junction temperature (°C)")
    ax.set_ylabel("On-resistance relative to 27 °C")
    ax.set_title("Heat makes every other switch worse; bulk-doped diamond gets better")
    ax.legend(fontsize=8.5, loc="lower right")
    ax.grid(True, which="both", alpha=0.15)
    return _finish(fig, out, "fig28_ron_vs_temperature.png",
                   "[jacoboni1977] [arora1982] [kimoto2014] [mishra2008] [pernot2010] [lagrange1998] [kawarada2014] [lutz2018]; ceilings are package and reliability limits")


def fig_converter_loss(out: Path) -> Path:
    f = np.logspace(3, 6.5, 80)
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8))
    ax = axes[0]
    for n in NAMES:
        ax.loglog(f / 1e3, [converter.material_switch(n, 1200, 800, 300, x).p_total_w for x in f], color=COLORS[n], lw=2.4, label=LABEL[n])
    ax.loglog(f / 1e3, [converter.material_switch("Diamond", 1200, 800, 300, x, measured="saha2022").p_total_w for x in f],
              color=RED, lw=2.4, ls="--", label="Diamond, measured device scaled [saha2022]")
    ax.axvspan(8, 30, color=GOLD, alpha=0.2); ax.text(9, 3.5, "traction-inverter\nswitching band", fontsize=8.5)
    ax.set_xlabel("Switching frequency (kHz)")
    ax.set_ylabel("Loss per switch, area-optimized (W)")
    ax.set_title("800 V bus, 300 A, 1200 V class: loss ∝ √(R·C·f)", fontsize=11)
    ax.legend(fontsize=8); ax.grid(True, which="both", alpha=0.15)
    ax = axes[1]
    apps = converter.APPLICATIONS
    x = np.arange(len(apps)); w = 0.16
    keys = NAMES + ["meas"]
    for i, n in enumerate(keys):
        vals = []
        for name, vb, cls, cur, fs, _ in apps:
            d = converter.material_switch("Diamond", cls, vb, cur, fs, measured="saha2022") if n == "meas" else converter.material_switch(n, cls, vb, cur, fs)
            vals.append(100 * (1 - converter.converter_efficiency("Diamond" if n == "meas" else n, cls, vb, cur, fs, measured="saha2022" if n == "meas" else None)))
        ax.bar(x + (i - 2) * w, vals, w, color=RED if n == "meas" else COLORS[n], hatch="//" if n == "meas" else None,
               label="Diamond, measured 2022" if n == "meas" else LABEL[n])
    ax.set_yscale("log")
    ax.set_xticks(x, [a[0].split(",")[0].replace(" traction inverter", "\ninverter").replace(" power supply", "\npower supply").replace(" grid converter", "\ngrid converter").replace(" and aerospace actuator", "\nactuator") for a in apps], fontsize=8)
    ax.set_ylabel("Switch loss as % of output (log)")
    ax.set_title("Five applications, switch-loss floor by material", fontsize=11)
    ax.legend(fontsize=7.5, ncol=2); ax.grid(True, which="both", axis="y", alpha=0.15)
    return _finish(fig, out, "fig29_converter_loss.png",
                   "[erickson2020] [kassakian2023] [baliga1989] [huang2004] [shenai2018] [reimers2019] [jung2017] [masanet2020] [huang2017] [watson2015] [saha2022]; adamas.converter model")


def fig_application_map(out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10.5, 6))
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(1e1, 1e5); ax.set_ylim(1e3, 1e11)
    regions = [("Si", 10, 6500, 1e3, 3e4, "Silicon IGBT and MOSFET"), ("4H-SiC", 600, 2e4, 5e3, 5e5, "Silicon carbide"),
               ("GaN", 20, 900, 5e4, 3e7, "Gallium nitride"), ("Diamond", 600, 3e4, 1e4, 1e8, "Diamond: this framework's target")]
    for n, x0, x1, y0, y1, lab in regions:
        ax.fill_between([x0, x1], y0, y1, color=COLORS[n], alpha=0.18)
        ax.text(x0 * 1.1, y1 / 1.6, lab, color=COLORS[n], fontsize=9, fontweight="bold")
    apps = [(800, 2e4, "EV traction inverter\n[reimers2019]"), (400, 3e5, "Data-center supply\n[masanet2020]"), (48, 2e6, "Point-of-load converter\n[lidow2019]"),
            (1000, 5e4, "Solar inverter [huang2017]"), (6500, 5e3, "Medium-voltage grid\n[huang2017]"), (2e4, 3e3, "HVDC / traction [she2017]"),
            (50, 3e9, "5G radio amplifier\n[mishra2008]"), (100, 5e9, "GaN-on-diamond radar\n[francis2010]"), (300, 1e5, "300 °C actuator\n[watson2015]"),
            (100, 1e6, "Venus / reactor electronics\n[neudeck2019]"), (10, 2.87e9, "NV qubit microwave drive\n[doherty2013]")]
    for v, f, lab in apps:
        ax.plot(v, f, "o", color=INK, ms=6); ax.annotate(lab, (v, f), xytext=(5, 4), textcoords="offset points", fontsize=7.5)
    ax.set_xlabel("Device blocking voltage (V)")
    ax.set_ylabel("Switching or operating frequency (Hz)")
    ax.set_title("Where each semiconductor plays, and where applications sit (regions are this repository's judgment)")
    ax.grid(True, which="both", alpha=0.12)
    return _finish(fig, out, "fig30_application_map.png",
                   "[she2017] [jones2016] [amano2018] [huang2017] [reimers2019] [masanet2020] [lidow2019] [mishra2008] [francis2010] [watson2015] [neudeck2019]")


def fig_thermal_ceiling(out: Path) -> Path:
    q = np.logspace(1, 4, 100)              # W/cm^2 dissipated on a 1 mm^2 die
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    for n in NAMES:
        m = materials.MATERIALS[n]
        kappa = m.kappa_w_cmk
        dt = [thermal.hotspot_rise_k(x * 0.01, kappa, 564.0) for x in q]     # 1 mm^2 disk, radius 564 um, substrate = same material
        ax.loglog(q, np.array(dt) + 60, color=COLORS[n], lw=2.4, label=f"{LABEL[n].split(' (')[0]} substrate, 60 °C coolant")
        ax.axhline(converter.TJ_MAX_C[n], color=COLORS[n], ls=":", lw=1)
    ax.set_xlabel("Heat flux through a 1 mm² die (W/cm²)")
    ax.set_ylabel("Junction temperature (°C), spreading only")
    ax.set_title("Thermal ceiling: diamond both conducts more and tolerates more")
    ax.legend(fontsize=8.5, loc="upper left"); ax.grid(True, which="both", alpha=0.15)
    return _finish(fig, out, "fig31_thermal_ceiling.png", "[carslaw1959] [wei1993] [glassbrenner1964] [moore2014] [barcohen2016] [lutz2018] [kawarada2014]")


def fig_radar(out: Path) -> Path:
    props = [("Bandgap", "eg_ev", False), ("Breakdown\nfield", "ec_mv_cm", False), ("Thermal\nconductivity", "kappa_w_cmk", False),
             ("Electron\nmobility", "mu_n", False), ("Hole\nmobility", "mu_p", False), ("Saturation\nvelocity", "vsat_cm_s", False)]
    ang = np.linspace(0, 2 * np.pi, len(props), endpoint=False).tolist(); ang += ang[:1]
    fig, ax = plt.subplots(figsize=(6.8, 6.4), subplot_kw=dict(polar=True))
    for n in ["Si", "4H-SiC", "GaN", "Diamond"]:
        m = materials.MATERIALS[n]
        vals = []
        for _, attr, _inv in props:
            v = getattr(m, attr) if hasattr(m, attr) else 0
            vmax = max(getattr(materials.MATERIALS[k], attr) if hasattr(materials.MATERIALS[k], attr) else 0 for k in materials.MATERIALS)
            vals.append(np.log10(1 + 9 * v / vmax) if vmax else 0)
        vals += vals[:1]
        ax.plot(ang, vals, color=COLORS[n], lw=2.2, label=LABEL[n].split(" (")[0]); ax.fill(ang, vals, color=COLORS[n], alpha=0.08)
    ax.set_xticks(ang[:-1], [p[0] for p in props], fontsize=9)
    ax.set_yticks([]); ax.set_ylim(0, 1)
    ax.set_title("Material scorecard (log scale, each axis normalized to the best)", fontsize=11, pad=18)
    ax.legend(loc="lower right", bbox_to_anchor=(1.25, -0.08), fontsize=8.5)
    return _finish(fig, out, "fig32_material_radar.png", "[sze2006] [kimoto2014] [mishra2008] [isberg2002] [wort2008] [tsao2018]")


def fig_quantum_sizing(out: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8))
    ax = axes[0]
    cyc = np.logspace(-7, -1, 100)
    for w, c in [("RSA-2048, 2021 layout", COLORS["Si"]), ("RSA-2048, 2025 layout", RED), ("FeMoco energy (chemistry)", COLORS["Diamond"]), ("100 logical qubits, d = 17", GREEN)]:
        ax.loglog(cyc, [scaling.wall_clock_hours(w, x) for x in cyc], lw=2.3, color=c, label=f"{w} [{scaling.WORKLOADS[w]['ref']}]")
    ys = {"superconducting": 5e5, "neutral atoms": 3e-1, "trapped ions": 3e0, "NV, optical repetitive readout": 3e1, "NV, electrical readout (proposed)": 5e5}
    for p, x in scaling.PLATFORM_CYCLE_S.items():
        ax.axvline(x, color=INK, ls=":", lw=1); ax.text(x * 1.15, ys[p], p, rotation=90, fontsize=7.5, va="bottom" if ys[p] < 1e3 else "top")
    ax.set_ylim(1e-1, 1e7)
    ax.axhline(24 * 365, color=GOLD, lw=1.5); ax.text(1.3e-7, 24 * 365 * 1.4, "one year", fontsize=8.5, color="#b86e1f")
    ax.set_xlabel("Error-correction cycle time (s)"); ax.set_ylabel("Wall-clock time (hours)")
    ax.set_title("Slow readout is the price of room temperature", fontsize=11)
    ax.legend(fontsize=7.5, loc="upper left"); ax.grid(True, which="both", alpha=0.15)
    ax = axes[1]
    yields = np.array([0.02, 0.05, 0.1, 0.25, 0.5, 0.9])
    for w, c in [("RSA-2048, 2021 layout", COLORS["Si"]), ("FeMoco energy (chemistry)", COLORS["Diamond"]), ("100 logical qubits, d = 17", GREEN)]:
        cells = scaling.cells_needed(scaling.WORKLOADS[w]["physical_qubits"])
        ax.loglog(yields * 100, [scaling.die_side_mm(cells, 1.0, fill=0.6) / np.sqrt(y) for y in yields], "o-", color=c, lw=2.2, label=w)
    ax.axhline(76 / np.sqrt(2), color=INK, ls="--", lw=1); ax.text(2.2, 60, "largest square die on a 76 mm wafer", fontsize=8)
    ax.set_xlabel("Working-cell yield (%)"); ax.set_ylabel("Side of the diamond die (mm), 1 µm cell pitch")
    ax.set_title("Area is not the problem: even 5 million cells fit one die", fontsize=11)
    ax.legend(fontsize=8); ax.grid(True, which="both", alpha=0.15)
    return _finish(fig, out, "fig33_quantum_sizing.png",
                   "[gidney2021] [gidney2025] [babbush2018] [fowler2012] [google2025] [bluvstein2024] [monroe2013] [neumann2010science] [hopper2018] [e6orbray2026]; adamas.scaling model")


def fig_readiness(out: Path) -> Path:
    apps = ["Heat spreader / package", "Radiation detector", "Quantum magnetometer", "RF power amplifier", "Kilovolt discrete switch",
            "EV traction inverter", "Data-center supply", "300 °C+ electronics", "Small logic (10³ gates)", "Few-qubit accelerator", "Error-corrected QC"]
    cols = ["Silicon", "Silicon carbide", "Gallium nitride", "Diamond today", "Diamond potential"]
    #   0 not applicable, 1 research, 2 demonstrated, 3 commercial, 4 dominant   (this repository's judgment)
    z = np.array([[1, 1, 1, 4, 4], [2, 2, 1, 3, 4], [0, 1, 1, 3, 4], [2, 1, 4, 2, 3], [2, 4, 2, 2, 4], [3, 4, 1, 1, 3], [3, 2, 4, 1, 3],
                  [1, 3, 1, 2, 4], [4, 2, 1, 2, 2], [0, 0, 0, 3, 4], [1, 0, 0, 0, 2]])
    fig, ax = plt.subplots(figsize=(9, 6.2))
    im = ax.imshow(z, cmap="YlGn", vmin=0, vmax=4, aspect="auto")
    ax.set_xticks(range(len(cols)), cols, fontsize=9); ax.set_yticks(range(len(apps)), apps, fontsize=9)
    words = ["n/a", "research", "demonstrated", "commercial", "dominant"]
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            ax.text(j, i, words[z[i, j]], ha="center", va="center", fontsize=7.5, color="black" if z[i, j] < 3 else "white")
    ax.set_title("Application readiness matrix (scores are this repository's judgment; see chapter E11 for sources)")
    fig.colorbar(im, ticks=range(5)).ax.set_yticklabels(words)
    return _finish(fig, out, "fig34_application_readiness.png",
                   "[francis2010] [tapper2000] [webb2019] [imanishi2019] [saha2023] [reimers2019] [jones2016] [watson2015] [liu2017] [olcf2025] [google2025]")


LAYER_COLORS = {"OHMIC": "#d4a017", "ISO": "#7a8793", "ENH": "#e63946", "GATE": "#0fa3b1", "VIA": "#111111", "METAL2": "#8a62d6",
                "QIMPLANT": "#2a9d4b", "QELEC": "#f4a261"}


def fig_pdk0_die(out: Path) -> Path:
    """Figure 35: the PDK-0 monitor die, flattened one level, drawn from the same generator that writes the GDS."""
    from matplotlib.patches import Rectangle
    cells = pdk0.monitor_die(); top, subs = cells[0], {c.name: c for c in cells[1:]}
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6.4))
    ax = axes[0]
    def draw(ax, cell, ox, oy, alpha=0.8):
        for layer, x0, y0, x1, y1 in cell.boxes:
            ax.add_patch(Rectangle((x0 + ox, y0 + oy), x1 - x0, y1 - y0, color=LAYER_COLORS.get(layer, "k"), alpha=alpha, lw=0))
        for name, x, y in cell.refs:
            draw(ax, subs[name], ox + x, oy + y, alpha)
    draw(ax, top, 0, 0)
    ax.set_xlim(0, 3000); ax.set_ylim(0, 3000); ax.set_aspect("equal")
    ax.set_xlabel("µm"); ax.set_title("PDK-0 monitor die, 3 × 3 mm (6 masks + 2 quantum masks)", fontsize=11)
    for k, (n, c) in enumerate(LAYER_COLORS.items()):
        ax.add_patch(Rectangle((2100, 300 + 110 * k), 80, 80, color=c)); ax.text(2200, 330 + 110 * k, n, fontsize=8)
    ax = axes[1]
    f = subs["PFET_W16_L2_E"]
    draw(ax, f, 0, 0, alpha=0.7)
    ax.set_xlim(-20, 20); ax.set_ylim(-16, 16); ax.set_aspect("equal")
    ax.set_xlabel("µm"); ax.set_title("Enhancement p-FET, W/L = 16/2 µm: gold ohmics, gate on Al₂O₃, C-O isolation frame", fontsize=10)
    ax.annotate("C-H channel\n(untouched surface)", (0, 4), xytext=(6, 11), fontsize=8.5, arrowprops=dict(arrowstyle="->"))
    return _finish(fig, out, "fig35_pdk0_monitor_die.png", "[meadconway1980] [kawarada2014] [kitabayashi2017] [liu2017] [pelgrom1989] [stapper1983] [hauf2011]; adamas.pdk0 generator")


def fig_published_gate_check(out: Path) -> Path:
    """Figure 36: project Q-1b, the gate budget evaluated with the published parameters of [dolde2013]."""
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    q = np.linspace(0.5, 1.0, 120)
    case = gate_budget.DOLDE2013
    for eps, c in [(0.0, COLORS["Diamond"]), (0.01, GOLD), (0.02, RED), (0.03, COLORS["Si"])]:
        ax.plot(q, [gate_budget.GateBudget(nu_khz=case["nu_dq_khz"], t2_us=case["t2a_us"], t2b_us=case["t2b_us"], echo=True,
                                           q_prep=x, pulse_error=eps, n_pulses=case["n_pulses"]).fidelity for x in q],
                color=c, lw=2.3, label=f"pulse error {eps:.0%}")
    ax.axhspan(0.63, 0.71, color=INK, alpha=0.12); ax.text(0.51, 0.715, "measured 0.67 ± 0.04 [dolde2013]", fontsize=8.5)
    ax.axhline(0.82, color=INK, ls=":"); ax.text(0.51, 0.83, "0.82 after optimal control [dolde2014]", fontsize=8.5)
    ax.axvspan(0.70, 0.75, color=RED, alpha=0.15); ax.text(0.725, 0.36, "NV⁻ fraction\n[aslam2013]", ha="center", fontsize=8)
    ax.set_xlabel("Per-NV preparation probability q"); ax.set_ylabel("Predicted Bell-state fidelity")
    ax.set_title("Q-1b: published pair (4.93 kHz, T₂ᴰᵠ 150 and 514 µs, 25 nm) puts coherence at 0.998", fontsize=10.5)
    ax.legend(fontsize=8.5, loc="lower right"); ax.grid(True, alpha=0.15); ax.set_ylim(0.3, 1.0)
    return _finish(fig, out, "fig36_published_gate_check.png", "[dolde2013] [dolde2014] [aslam2013]; adamas.gate_budget model")


def fig_placed_dia4(out: Path) -> Path:
    """Figure 37: DIA-4 placed on PDK-0 rows (no routing), colored by cell type."""
    import sys
    from matplotlib.patches import Rectangle
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "circuits" / "digital"))
    import place as pl
    from . import stdcells
    net = Path(__file__).resolve().parents[1] / "circuits" / "digital" / "dia4_netlist.v"
    if not net.exists():
        return net
    placed, st = pl.place(pl.parse(net))
    colors = {"INV": COLORS["Si"], "NAND2": COLORS["Diamond"], "NOR2": COLORS["4H-SiC"], "NOR3": COLORS["GaN"], "DFF": RED, "BUF": GREEN}
    fig, ax = plt.subplots(figsize=(8.5, 8))
    for t, name, pins, x, y in placed:
        ax.add_patch(Rectangle((x, y), stdcells.CELLS[t][3] * stdcells.PITCH_UM, stdcells.ROW_HEIGHT_UM, facecolor=colors[t], edgecolor="white", lw=0.4))
    ax.set_xlim(0, st["core_w_um"]); ax.set_ylim(0, st["core_h_um"]); ax.set_aspect("equal")
    for t, c in colors.items():
        ax.add_patch(Rectangle((0, 0), 0, 0, color=c, label=t))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=6, fontsize=8.5)
    ax.set_xlabel("µm")
    ax.set_title(f"DIA-4 on PDK-0: {st['cells']} cells, {st['rows']} rows, {st['core_w_um']:.0f} × {st['core_h_um']:.0f} µm, "
                 f"{st['utilization']:.0%} utilization, wirelength {st['hpwl_um'] / 1e3:.0f} mm", fontsize=10)
    return _finish(fig, out, "fig37_dia4_placed.png", "[weste2011] [meadconway1980] [liu2017] [faggin1996] [ajayi2019]; circuits/digital/place.py")


ALL = [fig_ron_temperature, fig_converter_loss, fig_application_map, fig_thermal_ceiling, fig_radar, fig_quantum_sizing, fig_readiness, fig_pdk0_die, fig_published_gate_check, fig_placed_dia4]


def make_all(out: str | Path = "docs/img") -> list[Path]:
    return [f(Path(out)) for f in ALL]
