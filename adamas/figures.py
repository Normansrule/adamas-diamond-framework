"""Every figure in the README and docs is generated here, from the cited models in this package.

Rule of the repository: a figure may only plot (a) a number that carries a [bibkey] in the package, or
(b) the output of an equation that carries a [bibkey]. Each figure prints its sources in a footer line.

Run:  python examples/make_all_figures.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from . import coupling, doping, logic, materials, nv, power, register, thermal, wafer  # noqa: E402

COLORS = {"Si": "#7a8793", "4H-SiC": "#e0a030", "GaN": "#8a62d6", "Ga2O3": "#d65f5f", "Diamond": "#0fa3b1"}
INK, RED, GREEN, GOLD = "#1d2733", "#e63946", "#2a9d4b", "#f4a261"
SHORT = {"Si": "Silicon", "4H-SiC": "Silicon\ncarbide", "GaN": "Gallium\nnitride", "Ga2O3": "Gallium\noxide",
         "Diamond": "Diamond"}

ABBR = {"Si": "Si", "4H-SiC": "SiC", "GaN": "GaN", "Ga2O3": "Ga₂O₃", "Diamond": "Diamond"}

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold", "axes.spines.top": False,
    "axes.spines.right": False, "axes.edgecolor": INK, "text.color": INK, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "legend.frameon": False, "figure.dpi": 130,
})


def _finish(fig, out: Path, name: str, sources: str) -> Path:
    fig.text(0.01, -0.12 if name.startswith("fig12") or name.startswith("fig02") else -0.035, f"Sources: {sources}", fontsize=7.5, color="#5b6775", ha="left", va="top")
    out.mkdir(parents=True, exist_ok=True)
    path = out / name
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def fig_material_properties(out: Path) -> Path:
    """Five headline properties, five materials. Values and sources: adamas.materials.MATERIALS."""
    props = [("Bandgap (eV)", "eg_ev"), ("Breakdown field (MV/cm)", "ec_mv_cm"),
             ("Thermal conductivity (W/cm·K)", "kappa_w_cmk"), ("Electron mobility (cm²/V·s)", "mu_n"),
             ("Hole mobility (cm²/V·s)", "mu_p")]
    fig, axes = plt.subplots(1, 5, figsize=(15, 3.6))
    keys = list(materials.MATERIALS)
    for ax, (label, attr) in zip(axes, props):
        vals = [getattr(materials.MATERIALS[k], attr) for k in keys]
        bars = ax.bar(range(len(keys)), vals, color=[COLORS[k] for k in keys])
        ax.set_xticks(range(len(keys)), [ABBR[k] for k in keys], fontsize=9, rotation=35)
        ax.set_title(label, fontsize=10.5)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v, f"{v:g}", ha="center", va="bottom", fontsize=8)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
    fig.suptitle("Why diamond? The raw material numbers", fontweight="bold", fontsize=14, y=1.04)
    return _finish(fig, out, "fig01_material_properties.png",
                   "[sze2006] [kimoto2014] [mishra2008] [pearton2018] [isberg2002] [wort2008] [tsao2018]")


def fig_foms(out: Path) -> Path:
    """Figures of merit relative to silicon: [baliga1982] [baliga1989] [johnson1965] [keyes1972]."""
    foms = materials.normalized_foms()
    names = list(next(iter(foms.values())).keys())
    keys = list(foms)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    width = 0.16
    for i, k in enumerate(keys):
        vals = [max(foms[k][n], 1e-2) for n in names]
        ax.bar(np.arange(len(names)) + (i - 2) * width, vals, width, color=COLORS[k], label=SHORT[k].replace("\n", " "))
    ax.set_yscale("log")
    ax.set_xticks(range(len(names)), names)
    ax.axhline(1, color=INK, lw=0.8, ls=":")
    ax.set_ylabel("Figure of merit relative to silicon (log scale)")
    ax.set_title("Figures of merit: how much better than silicon, in theory?")
    ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.1))
    return _finish(fig, out, "fig02_figures_of_merit.png",
                   "[baliga1982] [baliga1989] [johnson1965] [keyes1972] [huang2004]; diamond evaluated with holes")


def fig_ron_bv(out: Path) -> Path:
    """Unipolar limit R_on,sp = 4 BV^2 / (eps mu Ec^3) [baliga1982] with a measured diamond point [saha2021]."""
    bv = np.logspace(2, 4.7, 200)
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    for k, m in materials.MATERIALS.items():
        carrier = "p" if k == "Diamond" else "n"
        ax.loglog(bv, [power.ron_sp_mohm_cm2(m, v, carrier) for v in bv], color=COLORS[k], lw=2.4,
                  label=f"{SHORT[k].replace(chr(10), ' ')} limit")
    pt = power.MEASURED_DIAMOND["saha2021"]
    ax.plot(pt["bv_v"], pt["ron_mohm_cm2"], "*", ms=18, color=RED, mec=INK, label="Measured diamond MOSFET [saha2021]")
    ax.annotate("Real device today:\n2608 V, 19.74 mΩ·cm²\n(about 1000× above its own limit,\nso large headroom remains)",
                (pt["bv_v"], pt["ron_mohm_cm2"]), xytext=(150, 60), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.set_xlabel("Breakdown voltage (V)")
    ax.set_ylabel("Specific on-resistance (mΩ·cm²)   lower is better")
    ax.set_title("Power switch limit lines: on-resistance versus blocking voltage")
    ax.legend(fontsize=8.5, loc="lower right")
    ax.grid(True, which="both", alpha=0.15)
    return _finish(fig, out, "fig03_ron_vs_bv.png", "[baliga1982] [donato2020] [saha2021]")


def fig_ionization(out: Path) -> Path:
    """Incomplete ionization of deep dopants [sze2006] with activation energies [lagrange1998] [koizumi1997] [farrer1969]."""
    t = np.linspace(250, 900, 140)
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    style = {"Si:B": (COLORS["Si"], "-"), "Si:P": (COLORS["Si"], "--"), "C:B": (COLORS["Diamond"], "-"),
             "C:P": (COLORS["Diamond"], "--"), "C:N": (RED, ":")}
    for key, d in doping.DOPANTS.items():
        frac = [max(doping.ionized_fraction(d, 1e17, tk), 1e-16) for tk in t]
        c, ls = style.get(key, (INK, "-"))
        ax.semilogy(t, frac, color=c, ls=ls, lw=2.4, label=f"{key}  ({d.ea_ev:g} eV)")
    ax.axvline(300, color=INK, lw=0.8, ls=":")
    ax.text(305, 2e-12, "room\ntemperature", fontsize=8.5)
    ax.set_ylim(1e-13, 2)
    ax.set_xlabel("Temperature (K)")
    ax.set_ylabel("Fraction of dopant atoms that donate a carrier")
    ax.set_title("The doping problem: diamond's dopants are deep (10¹⁷ cm⁻³)")
    ax.legend(title="Host:dopant (activation energy)", fontsize=9)
    ax.grid(True, which="both", alpha=0.15)
    return _finish(fig, out, "fig04_dopant_ionization.png",
                   "[sze2006] [lagrange1998] [koizumi1997] [farrer1969] [kalish1999]")


def fig_hotspot(out: Path) -> Path:
    """Hot-spot temperature rise, circular source on a half-space: dT = P / (4 kappa a) [carslaw1959]."""
    a = np.logspace(1, 3, 100)
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    for k, m in materials.MATERIALS.items():
        ax.loglog(a, [thermal.hotspot_rise_k(1.0, m.kappa_w_cmk, r) for r in a], color=COLORS[k], lw=2.4,
                  label=SHORT[k].replace("\n", " "))
    ax.set_xlabel("Hot-spot radius (µm)")
    ax.set_ylabel("Temperature rise for 1 W (K)")
    ax.set_title("Heat: the same 1 W hot spot on five substrates")
    ax.legend()
    ax.grid(True, which="both", alpha=0.15)
    return _finish(fig, out, "fig05_hotspot.png", "[carslaw1959] [wei1993] [olson1993] and material sources of Figure 1")


def fig_wafer_timeline(out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    cmap = {"Silicon": COLORS["Si"], "Silicon carbide (4H-SiC)": COLORS["4H-SiC"],
            "Diamond (single crystal)": COLORS["Diamond"]}
    for name, pts in wafer.WAFER_HISTORY.items():
        pts = sorted(pts)
        if name.startswith("Diamond"):
            ax.plot([p[0] for p in pts], [p[1] for p in pts], "o", ms=9, color=cmap[name], label=name)
            for yr, note in wafer.DIAMOND_NOTES.items():
                d = dict(pts)[yr]
                off = (-30, -16) if yr == 2014 else (6, 8)
                ax.annotate(note, (yr, d), xytext=off, textcoords="offset points", fontsize=8, color=cmap[name])
        else:
            pts = pts + [(2026, pts[-1][1])]
            ax.step([p[0] for p in pts], [p[1] for p in pts], where="post", lw=2.4, color=cmap[name], label=name)
    ax.set_yscale("log")
    ax.set_yticks([10, 25, 51, 100, 150, 200, 300], ["10", "25", "51 (2 in)", "100", "150", "200", "300"])
    ax.set_xlabel("Year")
    ax.set_ylabel("Wafer diameter (mm)")
    ax.set_title("Wafer size: diamond is roughly where silicon was in the early 1970s")
    ax.legend(loc="upper left")
    ax.set_xlim(1958, 2034)
    ax.grid(True, alpha=0.15)
    return _finish(fig, out, "fig06_wafer_timeline.png",
                   "[plummer2000] [kimoto2014] [yamada2014] [schreck2017] [kim2021] [e6orbray2026]; silicon and SiC dates approximate")


def fig_nv_levels(out: Path) -> Path:
    """Energy-level diagram of the negatively charged nitrogen-vacancy center [doherty2013] [manson2006] [goldman2015]."""
    fig, ax = plt.subplots(figsize=(8.6, 5.6))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    def level(x0, x1, y, label, color=INK, side="left"):
        ax.plot([x0, x1], [y, y], color=color, lw=3)
        if side == "left":
            ax.text(x0 - 0.15, y, label, ha="right", va="center", fontsize=10)
        else:
            ax.text(x1 + 0.15, y, label, ha="left", va="center", fontsize=10)

    level(1.6, 4.2, 1.0, "mₛ = 0")
    level(1.6, 4.2, 2.0, "mₛ = ±1")
    level(1.6, 4.2, 7.5, "mₛ = 0")
    level(1.6, 4.2, 8.3, "mₛ = ±1")
    level(6.6, 8.6, 5.6, "¹A₁", side="right")
    level(6.6, 8.6, 3.8, "¹E", side="right")
    ax.text(2.9, 0.35, "Ground state ³A₂", ha="center", fontweight="bold")
    ax.text(2.9, 8.9, "Excited state ³E", ha="center", fontweight="bold")
    ax.text(7.6, 6.2, "Singlet states\n(the dark shortcut)", ha="center", fontweight="bold", fontsize=9.5)
    ax.annotate("", (2.2, 7.4), (2.2, 1.1), arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=3))
    ax.text(2.05, 4.4, "green laser\n532 nm", color=GREEN, ha="right", fontsize=9.5)
    ax.annotate("", (3.4, 1.1), (3.4, 7.4), arrowprops=dict(arrowstyle="-|>", color=RED, lw=3))
    ax.text(3.55, 4.9, "red glow\n637 to 800 nm", color=RED, fontsize=9.5)
    ax.annotate("", (6.6, 5.7), (4.25, 8.25), arrowprops=dict(arrowstyle="-|>", color=INK, lw=2))
    ax.text(5.5, 7.5, "strong from ±1", fontsize=9, rotation=-38)
    ax.annotate("", (7.6, 3.9), (7.6, 5.5), arrowprops=dict(arrowstyle="-|>", color="#8d5524", lw=2))
    ax.text(7.75, 4.65, "1042 nm", fontsize=9, color="#8d5524")
    ax.annotate("", (4.25, 1.05), (6.6, 3.7), arrowprops=dict(arrowstyle="-|>", color=INK, lw=2))
    ax.text(5.6, 2.0, "returns mostly to 0", fontsize=9, rotation=40)
    ax.annotate("", (4.6, 2.0), (4.6, 1.0), arrowprops=dict(arrowstyle="<->", color=GOLD, lw=2.5))
    ax.text(4.75, 1.45, "microwaves\n2.87 GHz", color="#b86e1f", fontsize=9.5)
    ax.set_title("The nitrogen-vacancy (NV) center: a qubit you set with green light and read with red light")
    return _finish(fig, out, "fig07_nv_levels.png", "[doherty2013] [manson2006] [goldman2015] [robledo2011njp]")


def fig_odmr(out: Path) -> Path:
    """Optically detected magnetic resonance from H = D Sz^2 + gamma B.S [doherty2013], hyperfine [felton2009]."""
    f = np.linspace(2780, 2960, 1800)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    for b, c in [(0.0, INK), (1.0, COLORS["Diamond"]), (2.0, RED)]:
        axes[0].plot(f, nv.odmr_spectrum(f, b * np.array([1, 1, 1]) / np.sqrt(3), axes=nv.NV_AXES[:1],
                                         linewidth_mhz=0.6) - 0.02 * b, color=c, lw=1.4,
                     label=f"{b:g} mT along the NV axis")
    axes[0].set_title("One NV center: the field splits the line")
    axes[0].set_xlabel("Microwave frequency (MHz)")
    axes[0].set_ylabel("Red fluorescence (normalized, offset)")
    axes[0].legend(fontsize=8.5, loc="lower left")
    b_lab = 3.0 * np.array([0.35, 0.55, 0.76])
    axes[1].plot(f, nv.odmr_spectrum(f, b_lab, linewidth_mhz=1.5, hyperfine=False), color=COLORS["Diamond"], lw=1.4)
    axes[1].set_title("Many NV centers, four crystal orientations: a vector compass")
    axes[1].set_xlabel("Microwave frequency (MHz)")
    return _finish(fig, out, "fig08_odmr.png", "[gruber1997] [doherty2013] [felton2009] [rondin2014] [barry2020]")


def fig_coherent_control(out: Path) -> Path:
    t = np.linspace(0, 1.0, 600)
    tau = np.linspace(0, 12, 800)
    te = np.linspace(0, 5000, 500)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    axes[0].plot(t, nv.rabi(t, 5.0, t_decay_us=2.0), color=COLORS["Diamond"], lw=1.8)
    axes[0].set_title("Rabi oscillation: the qubit gate")
    axes[0].set_xlabel("Microwave pulse length (µs)")
    axes[0].set_ylabel("Probability of mₛ = −1")
    axes[1].plot(tau, nv.ramsey(tau, 1.0, 5.0), color=RED, lw=1.8)
    axes[1].set_title("Ramsey fringes: T₂* dephasing")
    axes[1].set_xlabel("Free evolution time (µs)")
    axes[2].plot(te / 1000, nv.hahn_echo(te, 1800.0), color=INK, lw=2, label="T₂ = 1.8 ms [balasubramanian2009]")
    axes[2].plot(te / 1000, nv.hahn_echo(te, 600.0), color=COLORS["Si"], lw=2, ls="--",
                 label="T₂ = 0.6 ms, natural carbon [mizuochi2009]")
    axes[2].set_title("Hahn echo: T₂ coherence")
    axes[2].set_xlabel("Total free evolution time (ms)")
    axes[2].legend(fontsize=8)
    return _finish(fig, out, "fig09_coherent_control.png",
                   "[jelezko2004a] [childress2006] [balasubramanian2009] [mizuochi2009] [delange2010]")


def fig_coupling(out: Path) -> Path:
    """Dipolar coupling 52 MHz nm^3 / r^3 and the room-temperature scaling horizon [dolde2013] [neumann2010natphys]."""
    r = np.linspace(4, 60, 300)
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8))
    ax = axes[0]
    ax.semilogy(r, coupling.dipolar_coupling_khz(r), color=COLORS["Diamond"], lw=2.6, label="NV to NV coupling")
    for label, t2_s, key in [("1/T₂ (12C-enriched)", 1.8e-3, "balasubramanian2009"),
                             ("1/T₂ (natural carbon)", 0.6e-3, "mizuochi2009")]:
        ax.axhline(1e-3 / t2_s, ls="--", color=INK, lw=1)
        ax.text(59, 1e-3 / t2_s * 1.15, f"{label} [{key}]", ha="right", fontsize=8)
    ax.plot([9.8, 25], coupling.dipolar_coupling_khz(np.array([9.8, 25.0])), "*", ms=15, color=RED, mec=INK)
    ax.annotate("[neumann2010natphys]\n≈10 nm pair", (9.8, coupling.dipolar_coupling_khz(9.8)), xytext=(13, 120), fontsize=8.5,
                arrowprops=dict(arrowstyle="->"))
    ax.annotate("[dolde2013]\n≈25 nm pair, entangled", (25, coupling.dipolar_coupling_khz(25.0)), xytext=(30, 12), fontsize=8.5,
                arrowprops=dict(arrowstyle="->"))
    ax.set_xlabel("Distance between NV centers (nm)")
    ax.set_ylabel("Coupling strength (kHz)")
    ax.set_title("Two qubits talk through magnetism, and it fades as 1/r³")
    ax.grid(True, which="both", alpha=0.15)
    ax2 = axes[1]
    for t2, c in [(0.6, COLORS["Si"]), (1.8, COLORS["Diamond"]), (2.4, RED)]:
        ax2.plot(r, coupling.gate_fidelity_bound(r, t2_ms=t2), color=c, lw=2.4, label=f"T₂ = {t2} ms")
    ax2.axhline(0.99, color=INK, ls=":", lw=1)
    ax2.text(58, 0.992, "≈99% needed for error correction [fowler2012]", ha="right", fontsize=8.5)
    ax2.set_ylim(0.5, 1.005)
    ax2.set_xlabel("Distance between NV centers (nm)")
    ax2.set_ylabel("Upper bound on two-qubit gate fidelity")
    ax2.set_title("Design rule: keep coupled qubits within about 15 nm")
    ax2.legend()
    ax2.grid(True, alpha=0.15)
    return _finish(fig, out, "fig10_dipolar_coupling.png",
                   "[neumann2010natphys] [dolde2013] [balasubramanian2009] [herbschleb2019] [fowler2012]; bound is this repo's model")


def fig_pair_yield(out: Path) -> Path:
    sig = np.linspace(1, 20, 12)
    ys = np.array([0.01, 0.03, 0.1, 0.25, 0.5, 0.75, 1.0])
    z = np.array([[coupling.pair_yield(15.0, s, y, trials=6000) for s in sig] for y in ys])
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    im = ax.imshow(z, origin="lower", aspect="auto", cmap="viridis",
                   extent=[sig[0], sig[-1], -0.5, len(ys) - 0.5])
    ax.set_yticks(range(len(ys)), [f"{y:.0%}" for y in ys])
    ax.set_xlabel("Placement blur per axis, mask plus ion straggle (nm)")
    ax.set_ylabel("Nitrogen-to-NV conversion yield")
    ax.set_title("Manufacturing yield of one working two-qubit cell (target spacing 15 nm)")
    fig.colorbar(im, label="Probability the cell works")
    ax.text(1.5, 0.1, "keV implant today [pezzagna2010]", color="white", fontsize=8.5)
    ax.text(1.5, 4.1, "donor co-doping, laser writing [luhmann2019] [chen2019]", color="white", fontsize=8.5)
    return _finish(fig, out, "fig11_pair_yield.png",
                   "[pezzagna2010] [toyli2010] [scarabelli2016] [jakobi2016] [luhmann2019] [chen2019]; Monte Carlo model of this repo")


def fig_inverter(out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    drv = logic.Fet(mu_cm2_vs=150, vth=1.5, w_um=200)
    load = logic.Fet(mu_cm2_vs=150, vth=-2.0, w_um=25)
    vin, vout = logic.inverter_vtc(drv, load, vdd=10.0)
    ax.plot(vin, vout, color=COLORS["Diamond"], lw=2.6, label="p-channel only, enhancement/depletion style [liu2017]")
    n_fet = logic.Fet(mu_cm2_vs=150, vth=2.0, w_um=100)
    p_fet = logic.Fet(mu_cm2_vs=150, vth=2.0, w_um=100)
    vin2, vout2 = logic.inverter_vtc(n_fet, p_fet, vdd=10.0, complementary=True)
    ax.plot(vin2, vout2, color=RED, lw=2.2, ls="--",
            label="Projected complementary pair, needs n-channel [liao2024]")
    ax.plot([0, 10], [0, 10], color=INK, lw=0.7, ls=":")
    ax.set_xlabel("|Input voltage| (V)")
    ax.set_ylabel("|Output voltage| (V)")
    ax.set_title("A diamond logic inverter (square-law model)")
    ax.legend(fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.16))
    return _finish(fig, out, "fig12_inverter_vtc.png", "[sze2006] [liu2014] [liu2017] [liao2024]; level-1 model of this repo")


def fig_coherence_bars(out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9, 4.2))
    rows = nv.ROOM_TEMP_COHERENCE
    vals = [r[1] for r in rows]
    ax.barh(range(len(rows)), vals, color=[COLORS["Diamond"]] * (len(rows) - 1) + [RED])
    ax.set_xscale("log")
    ax.set_yticks(range(len(rows)), [f"{r[0]}\n[{r[2]}]" for r in rows], fontsize=8.5)
    for i, v in enumerate(vals):
        ax.text(v * 1.2, i, f"{v * 1e3:g} ms" if v < 1 else f"{v:g} s", va="center", fontsize=9)
    ax.axvline(50e-9, color=INK, ls=":")
    ax.text(65e-9, 0.6, "one fast gate\n≈ 50 ns\n[fuchs2009]", fontsize=8.5)
    ax.set_xlim(1e-8, 30)
    ax.set_xlabel("Time at room temperature (seconds, log scale)")
    ax.set_title("How long does the quantum information survive with no refrigerator?")
    return _finish(fig, out, "fig13_room_temp_coherence.png",
                   "[balasubramanian2009] [herbschleb2019] [jarmola2012] [maurer2012] [fuchs2009]")


def fig_lattice(out: Path) -> Path:
    """Diamond-cubic conventional cell. Silicon and diamond share it: a = 5.431 vs 3.567 angstrom [sze2006] [wort2008]."""
    base = np.array([[0, 0, 0], [0, .5, .5], [.5, 0, .5], [.5, .5, 0]])
    corners = np.array([[x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)])
    faces = np.array([[.5, .5, 0], [.5, .5, 1], [.5, 0, .5], [.5, 1, .5], [0, .5, .5], [1, .5, .5]])
    inner = base + 0.25
    atoms = np.unique(np.vstack([corners, faces, inner]), axis=0)
    fig = plt.figure(figsize=(12.5, 5))
    specs = [("Silicon: a = 5.431 Å", 5.431, COLORS["Si"], False), ("Diamond: a = 3.567 Å", 3.567, COLORS["Diamond"], False),
             ("Diamond with one NV center", 3.567, COLORS["Diamond"], True)]
    for i, (title, a, color, with_nv) in enumerate(specs):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        pts = atoms * a
        n_site, v_site = np.array([.25, .25, .25]) * a, np.array([.5, .5, 0]) * a
        for p in pts:
            for q in pts:
                d = np.linalg.norm(p - q)
                if 0 < d < 0.44 * a:
                    ax.plot(*zip(p, q), color="#9aa5b1", lw=1.3, zorder=1)
        for p in pts:
            if with_nv and np.allclose(p, n_site):
                ax.scatter(*p, s=170, color=RED, edgecolor=INK, zorder=3)
                ax.text(*(p + 0.12), "N", color=RED, fontweight="bold")
            elif with_nv and np.allclose(p, v_site):
                ax.scatter(*p, s=170, facecolor="white", edgecolor=INK, linestyle="--", zorder=3)
                ax.text(*(p + 0.12), "V", fontweight="bold")
            else:
                ax.scatter(*p, s=70, color=color, edgecolor=INK, linewidth=0.4, zorder=2)
        ax.set_xlim(0, 5.431); ax.set_ylim(0, 5.431); ax.set_zlim(0, 5.431)
        ax.set_box_aspect((1, 1, 1))
        ax.set_axis_off()
        ax.view_init(18, 28)
        ax.set_title(title, fontsize=11)
    fig.suptitle("Same crystal pattern, tighter and stiffer bonds (drawn to the same scale)", fontweight="bold", y=0.98)
    return _finish(fig, out, "fig14_lattice.png", "[sze2006] [wort2008] [doherty2013]")


def fig_register(out: Path) -> Path:
    """Bell-state fidelity of the electron plus nitrogen-14 register versus microwave drive strength."""
    a = 2.16
    omegas = np.linspace(0.2, 4.0, 60)
    fid = [register.bell_fidelity(a, w) for w in omegas]
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ax.plot(omegas, fid, color=COLORS["Diamond"], lw=2.4)
    ax.axvline(a / np.sqrt(3), color=RED, ls="--")
    ax.text(a / np.sqrt(3) + 0.05, 0.62, "sweet spot Ω = A/√3\n(unwanted line gets a full 2π turn)", color=RED, fontsize=9)
    ax.set_xlabel("Microwave Rabi frequency Ω (MHz)")
    ax.set_ylabel("Bell-state fidelity (pulse error only)")
    ax.set_title("Two qubits inside one defect: electron spin plus nitrogen-14 nucleus")
    ax.grid(True, alpha=0.15)
    return _finish(fig, out, "fig15_register_fidelity.png", "[felton2009] [dutt2007] [neumann2008] [vandersar2012]; simulation of this repo")


def fig_cost_yield(out: Path) -> Path:
    die = np.logspace(-1, 2.3, 100)
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    for label, dia, d0, c in [("Silicon 300 mm, 0.1 defects/cm²", 300, 0.1, COLORS["Si"]),
                              ("Silicon carbide 200 mm, 0.5 defects/cm²", 200, 0.5, COLORS["4H-SiC"]),
                              ("Diamond 76 mm, 5 defects/cm² (assumed)", 76, 5.0, COLORS["Diamond"]),
                              ("Diamond 76 mm, 100 defects/cm² (assumed)", 76, 100.0, RED)]:
        ax.loglog(die, [max(wafer.good_dies(dia, a, d0), 1e-1) for a in die], color=c, lw=2.3, label=label)
    ax.set_ylim(0.5, 1e6)
    ax.set_xlabel("Die area (mm²)")
    ax.set_ylabel("Good dies per wafer")
    ax.set_title("Wafer economics: small dies first")
    ax.legend(fontsize=8.5)
    ax.grid(True, which="both", alpha=0.15)
    return _finish(fig, out, "fig16_good_dies.png", "[murphy1964] [stapper1983] [e6orbray2026]; defect densities are labeled assumptions")


ALL = [fig_material_properties, fig_foms, fig_ron_bv, fig_ionization, fig_hotspot, fig_wafer_timeline, fig_nv_levels,
       fig_odmr, fig_coherent_control, fig_coupling, fig_pair_yield, fig_inverter, fig_coherence_bars, fig_lattice,
       fig_register, fig_cost_yield]


def make_all(out: str | Path = "docs/img") -> list[Path]:
    out = Path(out)
    return [f(out) for f in ALL]
