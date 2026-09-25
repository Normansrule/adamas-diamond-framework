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
    out = Path(out); return [bloch_rabi(out), odmr_sweep(out)]
