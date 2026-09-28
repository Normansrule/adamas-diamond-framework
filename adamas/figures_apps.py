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


def fig_resource_estimate(out: Path) -> Path:
    """Figure 39: space-time cost of NV machines from circuit-level error rates (project X-2)."""
    from . import resource as R
    t = R.table()
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.9))
    tr = np.logspace(np.log10(30), 4, 40)
    cols = [COLORS["Diamond"], COLORS["4H-SiC"], RED]
    ax = axes[0]
    for (name, (n, st)), c in zip(R.WORKLOADS.items(), cols):
        for t2, ls in [(1000.0, "-"), (100.0, "--")]:
            y = [(e.runtime_hours if (e := R.estimate(n, st, x, t2, t=t)) else np.nan) for x in tr]
            ax.loglog(tr / 1e3, y, ls, color=c, lw=2.2, label=name.split(" (")[0] if t2 == 1000.0 else None)
        ax.axhline(R.superconducting_reference(n, st).runtime_hours, color=c, lw=1, ls=":")
    for yv, lab in [(24, "1 day"), (24 * 365, "1 year")]:
        ax.axhline(yv, color=INK, lw=.6, alpha=.4); ax.text(0.032, yv * 1.15, lab, fontsize=8, color=INK)
    ax.set_xlabel("Ancilla readout time (ms)"); ax.set_ylabel("Runtime (hours)")
    ax.set_title("Runtime (solid 1 s memory, dashed 0.1 s;\ndotted: superconducting at measured Λ = 2.14)", fontsize=10); ax.legend(fontsize=8); ax.grid(True, which="both", alpha=.12)
    ax = axes[1]
    n, st = R.WORKLOADS["RSA-2048 scale (6,000 logical, 3×10⁹ steps)"]
    for t2, ls in [(1000.0, "-"), (100.0, "--")]:
        es = [R.estimate(n, st, x, t2, t=t) for x in tr]
        ax.semilogx(tr / 1e3, [e.distance if e else np.nan for e in es], ls, color=COLORS["Diamond"], lw=2.2, label=f"distance, T₂ mem {t2 / 1e3:g} s")
    ax2 = ax.twinx()
    for t2, ls in [(1000.0, "-"), (100.0, "--")]:
        es = [R.estimate(n, st, x, t2, t=t) for x in tr]
        ax2.semilogx(tr / 1e3, [e.physical_qubits / 1e6 if e else np.nan for e in es], ls, color=GOLD, lw=2)
    ax.set_xlabel("Ancilla readout time (ms)"); ax.set_ylabel("Code distance", color=COLORS["Diamond"]); ax2.set_ylabel("Physical qubits (millions)", color=GOLD)
    ax.set_title("RSA-2048-scale job: slow readout raises the distance", fontsize=10); ax.legend(fontsize=8, loc="upper left"); ax.grid(True, alpha=.12)
    ax = axes[2]
    reads = [30, 100, 1000, 10000]; x = np.arange(len(reads))
    prep, gates = 5.0, 4 * 25.0
    ax.bar(x, [prep] * 4, color=COLORS["Si"], label="prepare ancilla")
    ax.bar(x, [gates] * 4, bottom=[prep] * 4, color=COLORS["GaN"], label="4 dipolar gates (25 µs each)")
    ax.bar(x, reads, bottom=[prep + gates] * 4, color=COLORS["Diamond"], label="read ancilla")
    ax.set_yscale("log"); ax.set_ylim(1, 3e4); ax.set_xticks(x); ax.set_xticklabels([f"{r / 1e3:g} ms" for r in reads]); ax.set_xlabel("Readout time")
    ax.set_ylabel("One syndrome round (µs)"); ax.set_title("Once readout is fast, the gates set the clock", fontsize=10); ax.legend(fontsize=8, loc="upper left")
    fig.subplots_adjust(wspace=0.55)
    return _finish(fig, out, "fig39_resource_estimate.png",
                   "[fowler2012] [litinski2019] [google2025] [dolde2013] [maurer2012] [gidney2021stim]; adamas.resource model (illustrative workloads, NV noise p_link 0.3%)")


def fig_process_flow(out: Path) -> Path:
    """Figure 41: the T1 process flow as a subway map, with modules, peak temperatures, and optional branches."""
    from matplotlib.patches import FancyBboxPatch
    from . import traveler as T
    mods = {m[0]: m for m in T.MODULES}
    fig, ax = plt.subplots(figsize=(18, 5.4)); ax.set_xlim(-0.8, len(T.STEPS) - 0.2); ax.set_ylim(-3.0, 2.6); ax.axis("off")
    ax.plot([0, len(T.STEPS) - 1], [0, 0], color="#c9d3da", lw=7, zorder=0, solid_capstyle="round")
    branch = {"S06": 1.3, "S07": 1.3, "S12": -1.3}
    for k, st in enumerate(T.STEPS):
        c = mods[st["module"]][2]; y = branch.get(st["id"], 0.0)
        if y:
            ax.plot([k - 0.5, k, k + 0.5], [0, y, 0], color=c, lw=3, alpha=.55, zorder=1)
        ax.scatter(k, y, s=520, color=c, edgecolor=INK, lw=1.2, zorder=3)
        ax.text(k, y, st["id"][1:], ha="center", va="center", fontsize=8.5, fontweight="bold", color=INK, zorder=4)
        if y > 0:
            ax.text(k, y + 0.38, st["short"], ha="center", va="bottom", fontsize=9, color=INK)
        elif y < 0:
            ax.text(k, y - 0.38, st["short"], ha="center", va="top", fontsize=9, color=INK)
        else:
            ax.text(k, -0.45 - 0.42 * (k % 2), st["short"], ha="center", va="top", fontsize=9, color=INK)
        ax.text(k, 2.35, f"{st['t_max_c']}°", ha="center", fontsize=8, color=RED if st["t_max_c"] > 500 else "#5b6775")
    ax.text(-0.75, 2.35, "peak", fontsize=8, color="#5b6775", ha="left")
    for mid, name, col in T.MODULES:
        ks = [k for k, s_ in enumerate(T.STEPS) if s_["module"] == mid]
        ax.add_patch(FancyBboxPatch((min(ks) - .45, -2.85), max(ks) - min(ks) + .9, .4, boxstyle="round,pad=0.02", color=col, alpha=.35))
        ax.text((min(ks) + max(ks)) / 2, -2.65, name, ha="center", va="center", fontsize=9.5, fontweight="bold", color=INK)
    ax.text(5.5, 2.0, "quantum branch: NV windows", fontsize=9, color=RED, ha="center")
    ax.text(11, -2.2, "option A: NO₂ doping", fontsize=9, color="#0b8a93", ha="center")
    ax.set_title("Process traveler T1: hydrogen-terminated diamond transistors with optional NV qubit windows (19 steps)", fontsize=12)
    return _finish(fig, out, "fig41_process_flow.png", "[kawarada2023] [kasu2012] [pezzagna2010] [hauf2011] [lu2013]; adamas.traveler")


def fig_thermal_budget(out: Path) -> Path:
    """Figure 42: the thermal budget, the ordering rule every diamond flow must respect."""
    from . import traveler as T
    fig, ax = plt.subplots(figsize=(13, 4.6))
    k = np.arange(len(T.STEPS)); t = [s_["t_max_c"] for s_ in T.STEPS]
    mods = {m[0]: m[2] for m in T.MODULES}
    ax.bar(k, t, color=[mods[s_["module"]] for s_ in T.STEPS], edgecolor=INK, lw=.6)
    ax.axvline(T.step_index("S09") - .5, color=GOLD, lw=2); ax.text(T.step_index("S09") - .4, 1030, "first gold: from here on stay below 500 °C", fontsize=9, color=INK)
    for yv, lab in [(1064, "gold melts (1064 °C)"), (500, "post-metal ceiling (ADAMAS)"), (450, "option-B ALD (450 °C)")]:
        ax.axhline(yv, color=RED if yv > 1000 else INK, ls="--", lw=1, alpha=.7); ax.text(len(T.STEPS) - .5, yv + 12, lab, ha="right", fontsize=8.5)
    ax.set_xticks(k); ax.set_xticklabels([s_["id"] for s_ in T.STEPS], fontsize=8); ax.set_ylabel("Peak temperature (°C)"); ax.set_ylim(0, 1200)
    ax.set_title("Thermal budget: everything hot (growth, NV anneal) must happen before the first metal", fontsize=11)
    return _finish(fig, out, "fig42_thermal_budget.png", "[pezzagna2010] [kawarada2014] [kasu2012] [lu2013]; adamas.traveler")


def fig_cross_sections(out: Path) -> Path:
    """Figure 43: the device cross-section after every step, drawn from the same geometry as the web traveler."""
    from matplotlib.patches import Rectangle
    from . import traveler as T
    n = len(T.STEPS); cols = 5; rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(17, 2.6 * rows))
    for k, ax in enumerate(axes.flat):
        ax.axis("off")
        if k >= n:
            continue
        ax.set_xlim(20, 880); ax.set_ylim(360, 0)
        for sh in T.XS:
            if not T.visible(sh, k):
                continue
            name, x0, x1, y, h, col = sh[:6]
            if col == "holes":
                ax.scatter(np.arange(x0 + 8, x1, 16), [y + 1] * len(np.arange(x0 + 8, x1, 16)), s=4, color=COLORS["Diamond"], zorder=5)
            elif col == "no2":
                ax.scatter(np.arange(x0 + 8, x1, 14), [y + 3] * len(np.arange(x0 + 8, x1, 14)), s=10, color="#ff5d8f", zorder=5)
            else:
                ax.add_patch(Rectangle((x0, y), x1 - x0, h, color={"gold": "#e0b030"}.get(col, col), alpha=.95 if name not in ("laser",) else .35, zorder=2 if name in ("sub", "epi") else 3))
        ax.set_title(f"{T.STEPS[k]['id']}  {T.STEPS[k]['short']}", fontsize=10, loc="left", fontweight="bold")
    fig.suptitle("Cross-section after each step (not to scale): substrate, epilayer, C–H / C–O surfaces, hole gas, gold, NO₂, Al₂O₃, gate, vias, pads, NV centers", fontsize=11, y=1.0)
    return _finish(fig, out, "fig43_cross_sections.png", "adamas.traveler geometry; process after [kawarada2023] [kasu2012] [pezzagna2010]")


def fig_expected_tier_a(out: Path) -> Path:
    """Figure 44: what a working tier-A setup should show (ODMR, magnet law, heat-spreader race), with fits."""
    from scipy.optimize import curve_fit
    from . import experiments as X
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.9))
    r = X.expected("odmr_ensemble"); f = np.array(r["x"]); ax = axes[0]
    for (name, y), c in zip(r["series"].items(), [COLORS["Diamond"], RED]):
        ax.plot(f, y, ".", ms=3, color=c, alpha=.55, label=f"{name} (simulated data)")
    lor = lambda x, a, x0, w, c0: c0 - a * w ** 2 / ((x - x0) ** 2 + w ** 2)  # noqa: E731
    y0 = np.array(r["series"]["no magnet"]); p, _ = curve_fit(lor, f, y0, p0=[0.01, 2870, 6, 1])
    ax.plot(f, lor(f, *p), color=INK, lw=1.8, label=f"Lorentzian fit: D = {p[1]:.1f} MHz, contrast {100 * p[0] / p[3]:.1f}%")
    ax.plot(f, r["model"]["magnet near"], color=RED, lw=1.4, label="model: 4 orientations × 2 lines")
    ax.axvline(2870, color=INK, ls=":", lw=1); ax.text(2873, 1.004, "D = 2870 MHz", fontsize=8.5)
    ax.text(2795, 0.968, "a magnet splits one dip into up to eight", fontsize=8.5, color=RED)
    ax.set_xlabel(r["xlabel"]); ax.set_ylabel(r["ylabel"]); ax.set_title("A1 · ODMR of an NV ensemble", fontsize=11); ax.legend(fontsize=7, loc="center left", bbox_to_anchor=(0.0, 0.62)); ax.grid(True, which="both", alpha=.12)
    r = X.expected("magnet_distance"); ax = axes[1]; d = np.array(r["x"]); meas = np.array(r["series"]["measured"])
    ax.errorbar(d, meas, yerr=0.05 * meas, fmt="o", color=RED, capsize=3, label="measured (±5%)")
    k, b = np.polyfit(np.log(d), np.log(meas), 1); dd = np.linspace(2.5, 11, 50)
    ax.loglog(dd, np.exp(b) * dd ** k, color=INK, lw=1.8, label=f"fit: slope {k:.2f} (dipole: −3)")
    ax.set_xlabel(r["xlabel"]); ax.set_ylabel(r["ylabel"]); ax.set_title("A2 · Weigh a magnet with light", fontsize=11); ax.legend(fontsize=8); ax.grid(True, which="both", alpha=.15)
    from matplotlib.ticker import FixedLocator, ScalarFormatter
    ax.xaxis.set_major_locator(FixedLocator([3, 4, 5, 6, 8, 10])); ax.xaxis.set_major_formatter(ScalarFormatter()); ax.xaxis.set_minor_locator(plt.NullLocator())
    ax.text(0.04, 0.06, "splitting = 2γB, γ = 28 MHz/mT\nB ∝ m / r³", transform=ax.transAxes, fontsize=8.5, bbox=dict(boxstyle="round", fc="white", ec="#dde3e8"))
    r = X.expected("heat_spreaders"); ax = axes[2]; t = np.array(r["x"])
    cols = {"silicon": COLORS["Si"], "aluminium": GOLD, "copper": "#b87333", "diamond": COLORS["Diamond"]}
    for name, y in r["series"].items():
        ax.plot(t, y, color=cols[name], lw=2.2, label=f"{name}: {y[-1]:.1f} K at 3 min")
    ax.set_xlabel(r["xlabel"]); ax.set_ylabel(r["ylabel"]); ax.set_title("A3 · Heat-spreader race, 1.5 W heater", fontsize=11); ax.legend(fontsize=8); ax.grid(True, which="both", alpha=.12)
    ax.text(0.45, 0.08, "paste and heat sink add a floor\nthat no plate can remove", transform=ax.transAxes, fontsize=8.5, color="#5b6775")
    return _finish(fig, out, "fig44_expected_tier_a.png", "[stegemann2023] [williams2026] [doherty2013] [wei1993]; simulated with adamas.nv and adamas.experiments (noise levels typical of tier-A photodiode readout)")


def fig_expected_tier_b(out: Path) -> Path:
    """Figure 45: tier-B expected results: pulsed control with fits, vector magnetometry, and dopant activation."""
    from scipy.optimize import curve_fit
    from . import experiments as X
    fig = plt.figure(figsize=(17, 8.6)); gs = fig.add_gridspec(2, 3, hspace=.38, wspace=.28)
    P = X.expected("pulsed")["panels"]
    specs = [("Rabi (µs)", lambda t, a, f, T, c: c + a * (1 - np.cos(2 * np.pi * f * t) * np.exp(-t / T)), [0.05, 5, 0.8, 0], "Rabi: Ω = {1:.2f} MHz, π pulse = {pi:.0f} ns"),
             ("Ramsey (µs)", lambda t, a, f, T, c: c + a * (1 - np.cos(2 * np.pi * f * t) * np.exp(-(t / T) ** 2)), [0.05, 3, 0.6, 0], "Ramsey: detuning {1:.2f} MHz, T₂* = {2:.2f} µs"),
             ("Echo (µs)", lambda t, a, T, n, c: c + a * np.exp(-(t / T) ** n), [0.1, 300, 1.5, 0], "Echo: T₂ = {1:.0f} µs, n = {2:.2f}")]
    for k, (key, fn, p0, fmt) in enumerate(specs):
        ax = fig.add_subplot(gs[0, k]); x, y = map(np.array, P[key])
        ax.plot(x, y, "o", ms=3, color=COLORS["Diamond"], alpha=.7, label="simulated data")
        p, cov = curve_fit(fn, x, y, p0=p0, maxfev=20000); xx = np.linspace(x.min(), x.max(), 400)
        ax.plot(xx, fn(xx, *p), color=RED, lw=1.8, label="fit")
        ax.set_title(fmt.format(*p, pi=500 / p[1] if k == 0 else 0), fontsize=10.5); ax.set_xlabel(key.split(" ")[0] + " time (µs)"); ax.set_ylabel("Contrast"); ax.grid(True, which="both", alpha=.12); ax.legend(fontsize=8)
    r = X.expected("vector"); ax = fig.add_subplot(gs[1, 0]); x = np.arange(4)
    ax.bar(x - .18, r["series"]["applied"], .36, color=COLORS["Si"], label="applied field"); ax.bar(x + .18, r["series"]["fitted"], .36, color=COLORS["Diamond"], label="fitted from 8 lines")
    ax.set_xticks(x); ax.set_xticklabels(["[111]", "[1̄1̄1]", "[1̄11̄]", "[11̄1̄]"]); ax.set_ylabel(r["ylabel"]); ax.set_title(f"B2 · Vector magnetometry: B = ({', '.join(f'{v:.1f}' for v in r['B'])}) mT", fontsize=10.5); ax.legend(fontsize=8)
    r = X.expected("arrhenius"); ax = fig.add_subplot(gs[1, 1:]); x = np.array(r["x"]); R = np.array(r["series"]["resistivity (Ω·cm)"])
    ax.semilogy(x, R, "o", color=RED, label="simulated four-point data, [B] = 3×10¹⁷, [N] = 5×10¹⁶ cm⁻³")
    T = 1000 / x; kfit = np.polyfit(x[:9], np.log(R[:9] * T[:9] ** -0.7), 1)
    ax.semilogy(x[:9], np.exp(np.polyval(kfit, x[:9])) * T[:9] ** 0.7, color=INK, lw=2, label=f"corrected fit: E_A = {r['ea_fit_ev']:.3f} eV (raw slope {r['ea_raw_ev']:.3f} eV)")
    ax.axhspan(R.min(), R.min() * 3, color=COLORS["Diamond"], alpha=.08); ax.text(x.min() + .05, R.min() * 1.4, "hot: boron wakes up, resistance drops", fontsize=9)
    ax.set_xlabel(r["xlabel"]); ax.set_ylabel(r["ylabel"]); ax.set_title("B3 · Dopant activation: recover the 0.37 eV boron level", fontsize=10.5, pad=34); ax.legend(fontsize=8.5); ax.grid(True, which="both", alpha=.15)
    sec = ax.secondary_xaxis("top", functions=(lambda v: 1000 / np.maximum(v, 1e-9) - 273.15, lambda c: 1000 / (c + 273.15))); sec.set_xlabel("Temperature (°C)")
    return _finish(fig, out, "fig45_expected_tier_b.png", "[sewani2020] [hahn1950] [rondin2014] [lagrange1998] [sze2006]; simulated with adamas.experiments")


def fig_expected_tier_cd(out: Path) -> Path:
    """Figure 46: tier-C and tier-D expected results: antibunching, hyperfine triplet, transistor, Bell fidelity, yield."""
    from . import experiments as X
    fig, axes = plt.subplots(2, 3, figsize=(17, 8.6)); plt.subplots_adjust(hspace=.38, wspace=.28)
    rng = np.random.default_rng(2); ax = axes[0, 0]
    img = rng.poisson(20, (80, 80)).astype(float); yy, xx = np.mgrid[0:80, 0:80]
    for cx, cy in rng.uniform(5, 75, (9, 2)):
        img += 260 * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * 1.4 ** 2))
    im = ax.imshow(img, cmap="magma", extent=[0, 20, 0, 20]); fig.colorbar(im, ax=ax, label="kcounts/s")
    ax.set_title("C1 · Confocal scan: isolated spots are NV candidates", fontsize=10.5); ax.set_xlabel("µm"); ax.set_ylabel("µm")
    P = X.expected("single_nv")["panels"]; ax = axes[0, 1]; t, g = map(np.array, P["g2"])
    ax.plot(t, g, ".", color=COLORS["Diamond"], ms=4); ax.plot(t, 1 - 0.8 * np.exp(-np.abs(t) / 12), color=RED, lw=1.8)
    ax.axhline(0.5, color=INK, ls="--", lw=1); ax.text(-78, 0.53, "single-emitter threshold g⁽²⁾(0) = 0.5", fontsize=8.5)
    ax.set_xlabel("Delay τ (ns)"); ax.set_ylabel("g⁽²⁾(τ)"); ax.set_title("C1 · Antibunching proves one emitter", fontsize=10.5); ax.grid(True, alpha=.12)
    ax = axes[0, 2]; f, s_ = map(np.array, P["hyperfine"]); ax.plot(f, s_, color=COLORS["Diamond"], lw=1.2)
    for k in (-1, 0, 1):
        ax.axvline(2870 + 2.16 * k, color=RED, ls=":", lw=1)
    ax.set_xlabel("Frequency (MHz)"); ax.set_ylabel("Fluorescence"); ax.set_title("C1 · ¹⁴N hyperfine triplet, 2.16 MHz apart", fontsize=10.5)
    r = X.expected("fet_curves"); ax = axes[1, 0]
    for (name, y), c in zip(r["series"].items(), [COLORS["Si"], GOLD, COLORS["4H-SiC"], COLORS["Diamond"]]):
        ax.plot(r["x"], y, color=c, lw=2, label=name)
    ax.set_xlabel(r["xlabel"]); ax.set_ylabel(r["ylabel"]); ax.set_title("C2 · Output curves of a hole-gas transistor (model)", fontsize=10.5); ax.legend(fontsize=8); ax.grid(True, alpha=.12)
    r = X.expected("bell_q"); ax = axes[1, 1]; ax.plot(r["x"], r["series"]["model (published pair)"], color=COLORS["Diamond"], lw=2.5, label="ADAMAS budget, published pair")
    for q, F, lab in r["marks"]:
        ax.plot(q, F, "*", ms=14, color=RED); ax.annotate(f"{lab}: {F}", (q, F), xytext=(q - 0.13, F + 0.06), fontsize=9, arrowprops=dict(arrowstyle="->", lw=.8))
    ax.axhline(0.5, color=INK, ls=":", lw=1); ax.text(0.51, 0.52, "entanglement threshold", fontsize=8.5)
    ax.set_xlabel(r["xlabel"]); ax.set_ylabel(r["ylabel"]); ax.set_title("D1 · Two-qubit fidelity is set by charge-state preparation", fontsize=10.5); ax.legend(fontsize=8); ax.grid(True, alpha=.12)
    r = X.expected("good_dies"); ax = axes[1, 2]
    for (name, y), c in zip(r["series"].items(), [COLORS["Diamond"], GOLD, RED]):
        ax.loglog(r["x"], np.maximum(y, 1e-1), color=c, lw=2.2, label=name)
    ax.set_xlabel(r["xlabel"]); ax.set_ylabel(r["ylabel"]); ax.set_title("D2 · Good dies per 3-inch wafer (Murphy yield)", fontsize=10.5); ax.legend(fontsize=8); ax.grid(True, which="both", alpha=.15)
    return _finish(fig, out, "fig46_expected_tier_cd.png", "[kurtsiefer2000] [doherty2013] [kawarada2023] [dolde2013] [dolde2014] [murphy1964]; simulated with adamas.experiments")


def fig_experiment_ladder(out: Path) -> Path:
    """Figure 47: the experiment ladder: what each budget lets you prove, from a glowing diamond to a pilot line."""
    from . import experiments as X
    fig, ax = plt.subplots(figsize=(16, 6.6))
    levels = ["see NV glow", "sense a field", "measure heat flow", "control a spin", "measure a dopant", "isolate one qubit", "build a transistor", "entangle two qubits", "manufacture"]
    ylev = {"A1": 0, "A2": 1, "B2": 1.45, "A3": 2, "B1": 3, "B3": 4, "C1": 5, "C2": 6, "D1": 7, "D2": 8}
    short = {"A1": "A1 NV glow and ODMR", "A2": "A2 weigh a magnet (adds to A1)", "A3": "A3 heat-spreader race", "B1": "B1 Rabi, Ramsey, echo",
             "B2": "B2 vector magnetometry", "B3": "B3 boron activation energy", "C1": "C1 single NV, antibunching", "C2": "C2 cleanroom transistor",
             "D1": "D1 room-temperature entanglement", "D2": "D2 3-inch pilot line"}
    for k, (tid, t) in enumerate(X.TIERS.items()):
        lo, hi = [(1e2, 1e3), (1e3, 1e4), (1e4, 1e5), (1e5, 1e8)][k]
        ax.axvspan(lo, hi, color=t["color"], alpha=.10); ax.text(np.sqrt(lo * hi), 8.75, f"Tier {tid} · {t['name']}\n{t['range']}", ha="center", fontsize=9.5, fontweight="bold", color=INK)
    for e in X.EXPERIMENTS:
        lo = max(e["cost"][0], 60); hi = max(e["cost"][1], lo * 2.2); y = ylev[e["id"]]; c = X.TIERS[e["tier"]]["color"]
        ax.plot([lo, hi], [y, y], color=c, lw=9, alpha=.8, solid_capstyle="round")
        ax.text(hi * 1.25, y, short[e["id"]], ha="left", va="center", fontsize=9, color=INK)
    ax.set_xscale("log"); ax.set_xlim(40, 1e8); ax.set_ylim(-0.6, 9.4); ax.yaxis.set_minor_locator(plt.NullLocator())
    ax.set_yticks(range(len(levels))); ax.set_yticklabels(levels); ax.set_xlabel("Approximate cost (US$, 2026, log scale)")
    ax.set_title("The experiment ladder: each order of magnitude in budget unlocks a new thing you can prove about diamond", fontsize=11.5)
    ax.grid(True, axis="x", which="both", alpha=.15)
    return _finish(fig, out, "fig47_experiment_ladder.png", "adamas.experiments (prices are approximate street prices; verify with vendors)")


ALL = [fig_ron_temperature, fig_converter_loss, fig_application_map, fig_thermal_ceiling, fig_radar, fig_quantum_sizing, fig_readiness, fig_pdk0_die, fig_published_gate_check, fig_placed_dia4, fig_resource_estimate, fig_process_flow, fig_thermal_budget, fig_cross_sections, fig_expected_tier_a, fig_expected_tier_b, fig_expected_tier_cd, fig_experiment_ladder]


def make_all(out: str | Path = "docs/img") -> list[Path]:
    return [f(Path(out)) for f in ALL]
