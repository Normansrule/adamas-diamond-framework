"""Animated figures (GIF): a Rabi rotation on the Bloch sphere, and an ODMR sweep as the field ramps.
Physics: [rabi1937] [jelezko2004a] for the rotation; [doherty2013] [rondin2014] for the spectrum. Same functions as adamas.nv."""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from . import nv
from .figures import COLORS, INK, RED


def bloch_rabi(out: Path, frames: int = 40) -> Path:
    fig = plt.figure(figsize=(9, 4.4), dpi=80)
    ax3 = fig.add_subplot(1, 2, 1, projection="3d"); ax2 = fig.add_subplot(1, 2, 2)
    u, v = np.mgrid[0:2 * np.pi:40j, 0:np.pi:20j]
    t = np.linspace(0, 1.0, frames); omega = 2.0            # MHz: one full rotation in 0.5 us
    p = nv.rabi(t, omega)
    ax2.plot(t, p, color=COLORS["Diamond"], lw=2); dot, = ax2.plot([], [], "o", color=RED, ms=9)
    ax2.set_xlabel("Microwave pulse length (µs)"); ax2.set_ylabel("Probability of mₛ = −1"); ax2.set_title("Rabi oscillation, Ω = 2 MHz")
    def draw(i):
        ax3.cla(); ax3.plot_wireframe(np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v), color="#c9d3da", lw=0.4)
        th = 2 * np.pi * omega * t[i]                        # rotation angle about x
        vec = np.array([0, np.sin(th), np.cos(th)])
        ax3.quiver(0, 0, 0, *vec, color=RED, lw=3, arrow_length_ratio=0.12)
        ax3.text(0, 0, 1.25, "|0⟩  (bright)", ha="center", fontsize=9); ax3.text(0, 0, -1.4, "|−1⟩  (dim)", ha="center", fontsize=9)
        ax3.set_xlim(-1, 1); ax3.set_ylim(-1, 1); ax3.set_zlim(-1, 1); ax3.set_box_aspect((1, 1, 1)); ax3.set_axis_off(); ax3.set_title("The spin on the Bloch sphere", fontsize=11)
        ax3.view_init(20, 30 + 0.3 * i)
        dot.set_data([t[i]], [p[i]])
        return dot,
    ani = FuncAnimation(fig, draw, frames=frames, interval=60)
    out.mkdir(parents=True, exist_ok=True); path = out / "anim_rabi_bloch.gif"
    ani.save(path, writer=PillowWriter(fps=15)); plt.close(fig); return path


def odmr_sweep(out: Path, frames: int = 50) -> Path:
    fig, ax = plt.subplots(figsize=(8, 4), dpi=80)
    f = np.linspace(2700, 3040, 1400)
    line, = ax.plot([], [], color=COLORS["Diamond"], lw=1.8); txt = ax.text(2705, 0.905, "", fontsize=11, color=INK)
    ax.set_xlim(f[0], f[-1]); ax.set_ylim(0.9, 1.005); ax.set_xlabel("Microwave frequency (MHz)"); ax.set_ylabel("Red fluorescence (normalized)")
    ax.set_title("Optically detected magnetic resonance as a magnet approaches", fontsize=11)
    b_dir = np.array([0.35, 0.55, 0.76])
    def draw(i):
        b = 5.0 * i / (frames - 1)
        line.set_data(f, nv.odmr_spectrum(f, b * b_dir, linewidth_mhz=1.5, hyperfine=False)); txt.set_text(f"|B| = {b:.1f} mT")
        return line, txt
    ani = FuncAnimation(fig, draw, frames=frames, interval=80)
    path = out / "anim_odmr_sweep.gif"; ani.save(path, writer=PillowWriter(fps=12)); plt.close(fig); return path


def make_all(out: str | Path = "docs/img") -> list[Path]:
    out = Path(out); return [bloch_rabi(out), odmr_sweep(out)] + make_all_v15(out) + make_all_v28(out)


# ---------------- v0.15 animations: every one driven by a package model ----------------
from itertools import product  # noqa: E402
from matplotlib.colors import PowerNorm  # noqa: E402


def heat_race(out: Path, frames: int = 36) -> Path:
    """Same hot spot, silicon versus diamond, explicit heat equation ([carslaw1959] [wei1993])."""
    n = 56
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.9), dpi=72)
    Ts = [np.zeros((n, n)), np.zeros((n, n))]; alpha = [1.5 / (2.33 * 0.705), 22 / (3.52 * 0.509)]
    ims = []
    for ax, name in zip(axes, ["Silicon", "Diamond"]):
        im = ax.imshow(np.zeros((n, n)), cmap="inferno", norm=PowerNorm(0.45, 0, 1)); ax.set_title(name, fontsize=12); ax.axis("off"); ims.append(im)
    txt = fig.suptitle("", fontsize=11)
    def step(i):
        for m in range(2):
            T = Ts[m]; f = 0.24 * alpha[m] / alpha[1]
            for _ in range(8):
                T[1:-1, 1:-1] += f * (T[2:, 1:-1] + T[:-2, 1:-1] + T[1:-1, 2:] + T[1:-1, :-2] - 4 * T[1:-1, 1:-1])
                T[6:10, n // 2 - 3:n // 2 + 3] += 0.04; T[-1, :] = 0
        top = max(Ts[0].max(), 1e-9)
        for m in range(2):
            ims[m].set_data(Ts[m] / top)
        txt.set_text(f"Peak temperature rise: diamond is {Ts[0].max() / max(Ts[1].max(), 1e-9):.1f}× cooler")
        return ims
    ani = FuncAnimation(fig, step, frames=frames, interval=90)
    p = out / "anim_heat_race.gif"; ani.save(p, writer=PillowWriter(fps=10)); plt.close(fig); return p


def surface_decode(out: Path, frames: int = 30, d: int = 7) -> Path:
    """Random bit flips on a surface code, their syndrome, and the decoder's matching ([dennis2002] [higgott2022])."""
    from . import surface_sim
    rng = np.random.default_rng(3)
    fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=72)
    def draw(i):
        ax.cla(); ax.set_xlim(-1, d); ax.set_ylim(-1, d); ax.set_aspect("equal"); ax.axis("off")
        errs = rng.random((d, d)) < 0.06            # horizontal edges (data qubits between checks and boundaries)
        errv = rng.random((d - 1, d - 1)) < 0.06    # vertical edges between checks of neighboring rows
        syn = np.zeros((d, d - 1), bool)
        for r in range(d):
            for c in range(d):
                ax.plot([c - .5, c + .5], [r, r], color="#ff5d6c" if errs[r, c] else "#3a5a78", lw=4 if errs[r, c] else 2)
                if errs[r, c]:
                    if c > 0: syn[r, c - 1] ^= True
                    if c < d - 1: syn[r, c] ^= True
        for r in range(d - 1):
            for c in range(d - 1):
                ax.plot([c + .5, c + .5], [r, r + 1], color="#ff5d6c" if errv[r, c] else "#3a5a78", lw=4 if errv[r, c] else 2)
                if errv[r, c]:
                    syn[r, c] ^= True; syn[r + 1, c] ^= True
        for r in range(d):
            for c in range(d - 1):
                ax.scatter(c + .5, r, s=140 if syn[r, c] else 40, color="#ff5d6c" if syn[r, c] else "#16263d", edgecolors="#3a5a78", zorder=3)
        errs = np.concatenate([errs.ravel(), errv.ravel()])
        ax.set_title(f"Round {i + 1}: {errs.sum()} flips light up {syn.sum()} checks", fontsize=11)
        return []
    ani = FuncAnimation(fig, draw, frames=frames, interval=500)
    p = out / "anim_surface_code.gif"; ani.save(p, writer=PillowWriter(fps=2)); plt.close(fig); return p


def ring_oscillator(out: Path, frames: int = 40) -> Path:
    """Five-stage E/D ring oscillator, integrated with the square-law model of adamas.logic ([sze2006] [liu2017])."""
    from .logic import Fet
    drv, load = Fet(mu_cm2_vs=150, vth=1.5, w_um=16, l_um=2), Fet(mu_cm2_vs=150, vth=-2.0, w_um=2, l_um=2)
    cox = 9 * 8.854e-14 / 30e-7; C = cox * 16 * 2 * 1e-8 + 20e-15; vdd, dt = 10.0, 2e-11
    v = np.array([0, 10, 0, 10, 0], float); hist = []
    for s in range(15000):
        i_up = np.array([load.current(0, vdd - x) for x in v]); i_dn = np.array([drv.current(v[k - 1], v[k]) for k in range(5)])
        v = np.clip(v + (i_up - i_dn) / C * dt, 0, vdd)
        if s % 15 == 0: hist.append(v.copy())
    hist = np.array(hist); t = np.arange(len(hist)) * 15 * dt * 1e9
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=72); cols = [COLORS["Diamond"], "#9d7bff", "#ff5d8f", "#ffc46b", "#48e5a3"]
    lines = [ax.plot([], [], color=c, lw=2)[0] for c in cols]
    ax.set_xlim(0, 60); ax.set_ylim(-0.5, 10.5); ax.set_xlabel("time (ns)"); ax.set_ylabel("|V| (V)"); ax.set_title("Five diamond logic gates chasing each other", fontsize=11)
    def draw(i):
        j = min(len(t) - 1, 200 + i * 15); lo = max(0, j - 200)
        for k, ln in enumerate(lines):
            ln.set_data(t[lo:j] - t[lo], hist[lo:j, k])
        return lines
    ani = FuncAnimation(fig, draw, frames=frames, interval=80)
    p = out / "anim_ring_oscillator.gif"; ani.save(p, writer=PillowWriter(fps=12)); plt.close(fig); return p


def crystal_spin(out: Path, frames: int = 48) -> Path:
    """Rotating diamond lattice with a glowing NV center ([wort2008] [doherty2013])."""
    base = np.array([[0, 0, 0], [0, .5, .5], [.5, 0, .5], [.5, .5, 0], [.25, .25, .25], [.25, .75, .75], [.75, .25, .75], [.75, .75, .25]])
    A = np.array([b + np.array(c) for c in product(range(2), repeat=3) for b in base]); A -= A.mean(0)
    B = [(i, j) for i in range(len(A)) for j in range(i + 1, len(A)) if abs(np.linalg.norm(A[i] - A[j]) - np.sqrt(3) / 4) < .02]
    nv_i = int(np.argmin(np.linalg.norm(A, axis=1)))
    fig = plt.figure(figsize=(5, 5), dpi=72, facecolor="#05070d"); ax = fig.add_axes([0, 0, 1, 1], facecolor="#05070d")
    def draw(i):
        ax.cla(); ax.set_xlim(-1.4, 1.4); ax.set_ylim(-1.4, 1.4); ax.axis("off")
        th = 2 * np.pi * i / frames; R = np.array([[np.cos(th), 0, np.sin(th)], [0, 1, 0], [-np.sin(th), 0, np.cos(th)]])
        P = A @ R.T @ np.array([[1, 0, 0], [0, np.cos(.4), -np.sin(.4)], [0, np.sin(.4), np.cos(.4)]]).T
        for a, b in B:
            ax.plot(P[[a, b], 0], P[[a, b], 1], color="#2de2e6", lw=1.2, alpha=.45)
        o = np.argsort(P[:, 2]); ax.scatter(P[o, 0], P[o, 1], s=40 + 40 * (P[o, 2] + 1), color="#6ff3ff")
        ax.scatter(*P[nv_i, :2], s=700 * (1 + .4 * np.sin(4 * th)), color="#ff5d6c", alpha=.25); ax.scatter(*P[nv_i, :2], s=110, color="#ff5d6c")
        return []
    ani = FuncAnimation(fig, draw, frames=frames, interval=70)
    p = out / "anim_crystal.gif"; ani.save(p, writer=PillowWriter(fps=14)); plt.close(fig); return p


def make_all_v15(out: str | Path = "docs/img") -> list[Path]:
    out = Path(out); return [heat_race(out), surface_decode(out), ring_oscillator(out), crystal_spin(out), equations_montage(out)]


# ---------------- v0.26: equations in action, four at once ----------------
def equations_montage(out: str | Path = "docs/img", frames: int = 48) -> Path:
    """Four equations sweeping their main variable: ODMR splitting with B, a Rabi pulse, Ramsey dephasing, and wafer yield.
    The same models as the interactive page (adamas.action); [doherty2013] [jelezko2004a] [ramsey1950] [murphy1964]."""
    from . import wafer
    from .figures import GREEN
    out = Path(out)
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.2), dpi=72); plt.subplots_adjust(hspace=.62, wspace=.28)
    f = np.linspace(2700, 3040, 700); t = np.linspace(0, 1, 300); tau = np.linspace(0, 3, 300); d0 = np.logspace(-1, 1.3, 120)
    a0, a1, a2, a3 = axs.flat
    l0, = a0.plot([], [], color=COLORS["Diamond"], lw=2); a0.set_xlim(2700, 3040); a0.set_ylim(.986, 1.002); a0.set_xlabel("frequency (MHz)", fontsize=9)
    a1.plot(t, nv.rabi(t, 5), color="#7b5cd6", lw=2); d1, = a1.plot([], [], "o", color=RED, ms=9); a1.set_xlabel("pulse length τ (µs)", fontsize=9)
    a2.plot(tau, .5 * (1 + np.exp(-tau ** 2)), ":", color="#9aa6b2"); a2.plot(tau, .5 * (1 - np.exp(-tau ** 2)), ":", color="#9aa6b2")
    a2.plot(tau, nv.ramsey(tau, 2, 1), color="#d6457a", lw=1.8); d2, = a2.plot([], [], "o", color=RED, ms=9); a2.set_xlabel("free time τ (µs)", fontsize=9)
    a3.semilogx(d0, [wafer.good_dies(76, 25, x) for x in d0], color=GREEN, lw=2); d3, = a3.plot([], [], "o", color=RED, ms=9); a3.set_xlabel("killer defects D₀ (/cm²)", fontsize=9)
    T = [a.set_title("", fontsize=10.5, loc="left") for a in axs.flat]
    for a in axs.flat:
        a.tick_params(labelsize=8)
    fig.suptitle("Equations in action: every symbol is a slider at normansrule.github.io/adamas-diamond-framework/action.html", fontsize=10, color=INK, y=.995)
    def draw(i):
        u = 0.5 - 0.5 * np.cos(2 * np.pi * i / frames)
        B = 6 * u; lo, hi = nv.transition_frequencies_mhz((0, 0, B))
        l0.set_data(f, 1 - sum(.012 * 9 / ((f - x) ** 2 + 9) for x in ((lo, hi) if B > .05 else (2870,))))
        T[0].set_text(f"$f_\\pm = D \\pm \\gamma_e B$:  B = {B:.1f} mT → {lo:.0f}, {hi:.0f} MHz")
        x = u; d1.set_data([x], [nv.rabi(x, 5)]); T[1].set_text(f"Rabi: Ω = 5 MHz, τ = {1000 * x:.0f} ns → P = {float(nv.rabi(x, 5)):.2f}")
        x = 3 * u; d2.set_data([x], [nv.ramsey(x, 2, 1)]); T[2].set_text(f"Ramsey: τ = {x:.2f} µs, envelope $e^{{-(\\tau/T_2^*)^2}}$ = {np.exp(-x * x):.2f}")
        x = 10 ** (-1 + 2.3 * u); g = wafer.good_dies(76, 25, x); d3.set_data([x], [g]); T[3].set_text(f"Yield: D₀ = {x:.2g}/cm² → {g:.0f} good 25 mm² dies")
        return l0, d1, d2, d3
    ani = FuncAnimation(fig, draw, frames=frames, interval=90)
    out.mkdir(parents=True, exist_ok=True); p = out / "anim_equations.gif"; ani.save(p, writer=PillowWriter(fps=11)); plt.close(fig); return p


# ---------------- v0.28: the physics the audit changed, animated ----------------
def hot_switch(out: str | Path = "docs/img", frames: int = 44) -> Path:
    """Why a bulk-doped diamond switch loses at room temperature and wins hot: the ionized boron fraction and the
    resulting switch loss versus junction temperature (adamas.converter; [pernot2010] [lagrange1998] [erickson2020])."""
    from . import converter
    from .materials import MATERIALS
    out = Path(out)
    T = np.linspace(300, 650, 120); d = MATERIALS["Diamond"]
    fion = [100 * converter.drift_ionized_fraction(d, 1200.0, t) for t in T]
    loss = {n: [converter.material_switch(n, 1200, 800, 300, 20e3, t_k=t).p_total_w for t in T] for n in ("4H-SiC", "GaN", "Diamond")}
    lab = {"4H-SiC": "silicon carbide", "GaN": "gallium nitride", "Diamond": "diamond, bulk-doped drift"}
    ceil = {n: converter.TJ_MAX_C[n] + 273.15 for n in ("4H-SiC", "GaN", "Diamond")}            # junction-temperature limits
    fig, (a0, a1) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=72); plt.subplots_adjust(wspace=.3, bottom=.16, top=.78)
    a0.semilogy(T, fion, color=COLORS["Diamond"], lw=2.2); a0.set_xlabel("junction temperature (K)", fontsize=9); a0.set_ylabel("boron ionized (%)", fontsize=9)
    a0.set_title("A 1.2 kV drift's boron wakes up with heat", fontsize=10.5, pad=26); m0, = a0.plot([], [], "o", color=RED, ms=8); t0 = a0.text(310, 30, "", fontsize=10)
    for n, c in (("4H-SiC", COLORS["4H-SiC"]), ("GaN", COLORS["GaN"]), ("Diamond", COLORS["Diamond"])):
        ok = T <= ceil[n]
        a1.semilogy(T[ok], np.array(loss[n])[ok], color=c, lw=2.2, label=lab[n]); a1.semilogy(T[~ok], np.array(loss[n])[~ok], ":", color=c, lw=1.4)
    a1.set_xlabel("junction temperature (K)", fontsize=9); a1.set_ylabel("loss per switch (W), EV inverter", fontsize=9)
    a1.legend(fontsize=8, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, handlelength=1.4, columnspacing=1)
    gap = np.array(loss["Diamond"]) - np.array(loss["4H-SiC"]); i = int(np.argmax(gap < 0))  # computed crossing, not typed in
    assert gap[0] > 0 and gap[i] < 0, "diamond and SiC losses do not cross in 300-650 K; the title would be wrong"
    x_sic = T[i - 1] + (T[i] - T[i - 1]) * gap[i - 1] / (gap[i - 1] - gap[i])               # linear interpolation
    a1.set_title(f"Diamond passes SiC at {x_sic:.0f} K and keeps going where GaN cannot\n(dotted: above that material's junction-temperature limit)", fontsize=10, pad=26); m1 = a1.axvline(300, color=RED, lw=1.2)
    t1 = a1.text(0.98, 0.04, "", transform=a1.transAxes, ha="right", fontsize=10, zorder=5,
                 bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))
    def draw(i):
        k = int(i * (len(T) - 1) / (frames - 1)); m0.set_data([T[k]], [fion[k]]); t0.set_text(f"{T[k]:.0f} K: {fion[k]:.2f} % ionized")
        m1.set_xdata([T[k], T[k]]); r = loss["4H-SiC"][k] / loss["Diamond"][k]; t1.set_text(f"SiC ÷ diamond loss = {r:.2f}"); return m0, t0, m1, t1
    ani = FuncAnimation(fig, draw, frames=frames, interval=90)
    path = out / "anim_hot_switch.gif"; ani.save(path, writer=PillowWriter(fps=11)); plt.close(fig); return path


def addressing_sweep(out: str | Path = "docs/img", frames: int = 46) -> Path:
    """Two NVs in one laser spot, told apart by crystal axis: the eight ODMR lines of the four <111> axes as the field
    turns from [001] to [111] at 5 mT (adamas.addressing; [dolde2013] [doherty2013])."""
    from . import addressing as A
    out = Path(out)
    th = np.linspace(0, 54.7356, 90); ax_cols = [COLORS["Diamond"], GOLD_, "#9d7bff", "#8b98a5"]
    lines = np.array([[A.lines_on_axis(5.0, t, 45.0, a) for a in nv.NV_AXES] for t in th])     # (theta, axis, 2)
    fig, (a0, a1) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=72); plt.subplots_adjust(wspace=.28, bottom=.16, top=.84)
    for k in range(4):
        for j in range(2):
            a0.plot(th, lines[:, k, j], color=ax_cols[k], lw=2 if k < 2 else 1.2, ls="--" if k == 2 else "-",
                    label=(["NV A, axis [111]", "NV B, axis [1-1-1]", "axis [-11-1]: same lines as B in this plane", "axis [-1-11]"][k] if j == 0 else None))
    a0.set_xlabel("field angle from [001] toward [111] (degrees), 5 mT", fontsize=9); a0.set_ylabel("ODMR line (MHz)", fontsize=9); a0.legend(fontsize=8, loc="center left")
    a0.set_title("Same spot, different axes: the lines separate", fontsize=10.5); vl = a0.axvline(0, color=RED, lw=1.2)
    f = np.linspace(2700, 3040, 1600); sp, = a1.plot([], [], color=INK, lw=1.4); a1.set_xlim(2700, 3040); a1.set_ylim(.95, 1.003)
    a1.set_xlabel("frequency (MHz)", fontsize=9); a1.set_ylabel("fluorescence (illustrative dip depth and width)", fontsize=9); txt = a1.text(2710, .955, "", fontsize=10)
    a1.set_title("What the joint readout sees", fontsize=10.5)
    def draw(i):
        k = int(i * (len(th) - 1) / (frames - 1)); vl.set_xdata([th[k], th[k]])
        y = 1 - sum(0.012 * 1.5 ** 2 / ((f - x) ** 2 + 1.5 ** 2) for x in lines[k].ravel())
        sp.set_data(f, y); sep = A.spectral_separation_mhz(5.0, th[k], 45.0)
        txt.set_text(f"θ = {th[k]:.0f}°: A and B {sep:.1f} MHz apart"); return vl, sp, txt
    ani = FuncAnimation(fig, draw, frames=frames, interval=90)
    path = out / "anim_addressing.gif"; ani.save(path, writer=PillowWriter(fps=11)); plt.close(fig); return path


def gate_bias(out: str | Path = "docs/img", frames: int = 50) -> Path:
    """A phase (Z) error on the target in the middle of the gate, followed to the output: a CZ keeps it a Z; a CNOT
    built as H·CZ·H turns it into a bit flip (adamas.gatebias, Stim-checked; [guillaud2019] [etxezarreta2025])."""
    from . import gatebias as G
    out = Path(out)
    fig, axes = plt.subplots(2, 1, figsize=(9, 4.6), dpi=72); plt.subplots_adjust(hspace=.45, top=.9, bottom=.04, left=.04, right=.98)
    cols = {"X": RED, "Y": "#9d7bff", "Z": COLORS["Diamond"]}
    specs = [("cz", [("CZ", 0.5)], "CZ gate (native, diagonal): the phase error leaves as a phase error"),
             ("cnot", [("H", 0.25), ("CZ", 0.5), ("H", 0.75)], "CNOT built as H · CZ · H: the phase error leaves as a bit flip")]
    tokens = []
    for ax, (kind, gates, title) in zip(axes, specs):
        ax.set_xlim(0, 1); ax.set_ylim(-0.3, 1.3); ax.axis("off"); ax.set_title(title, fontsize=10.5, loc="left")
        for y, name in ((1, "control"), (0, "target")):
            ax.plot([0.08, 0.98], [y, y], color="#9aa6b2", lw=1.6); ax.text(0.0, y, name, fontsize=9, va="center")
        for g, x in gates:
            if g == "H":
                ax.add_patch(plt.Rectangle((x - 0.03, -0.18), 0.06, 0.36, color="#dfe6ec", zorder=3)); ax.text(x, 0, "H", ha="center", va="center", fontsize=11, zorder=4)
            else:
                ax.plot([x, x], [0, 1], color=INK, lw=1.6); ax.plot([x, x], [0, 1], "o", color=INK, ms=7)
        tok = ax.text(0.5, 0, "Z", ha="center", va="center", fontsize=12, fontweight="bold", color="white",
                      bbox=dict(boxstyle="circle,pad=0.3", fc=cols["Z"], ec="none"), zorder=5)
        tokens.append((kind, gates, tok))
    fig.text(0.04, 0.005, "Gate positions are schematic, not to time scale (the CZ takes most of the gate time).", fontsize=8.5, color="#5a6878")
    def at(kind, gates, x):   # Pauli on the target after the gates left of x, for a Z injected just after the CZ
        passed = [(g, (1,) if g == "H" else (0, 1)) for g, gx in gates if 0.5 < gx < x]
        return G.propagate({1: "Z"}, passed)[1]
    def draw(i):
        x = 0.52 + 0.44 * i / (frames - 1); arts = []
        for kind, gates, tok in tokens:
            p = at(kind, gates, x); tok.set_position((x, 0)); tok.set_text(p); tok.get_bbox_patch().set_facecolor(cols[p]); arts.append(tok)
        return arts
    ani = FuncAnimation(fig, draw, frames=frames, interval=80)
    path = out / "anim_gate_bias.gif"; ani.save(path, writer=PillowWriter(fps=12)); plt.close(fig); return path


GOLD_ = "#e0a030"


def make_all_v28(out: str | Path = "docs/img") -> list[Path]:
    out = Path(out); return [hot_switch(out), addressing_sweep(out), gate_bias(out)]
