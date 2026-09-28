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
    out = Path(out); return [bloch_rabi(out), odmr_sweep(out)] + make_all_v15(out)


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
    out = Path(out); return [heat_race(out), surface_decode(out), ring_oscillator(out), crystal_spin(out)]
