"""A 20-second trailer rendered entirely from code (the idea of Remotion, done with matplotlib and ffmpeg).

    python -m adamas.trailer [out.mp4] [--fast]

Five scenes, each driven by the package's own models: the diamond lattice with an NV center [wort2008], heat escaping
from silicon and diamond [carslaw1959] [wei1993], the NV resonance splitting in a magnetic field [doherty2013], a surface
code catching errors [dennis2002], and the closing card.
"""
from __future__ import annotations
import sys
from itertools import product
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter
from matplotlib.colors import PowerNorm

from . import nv

BG, INK, TEAL, VIOLET, RED, MUTE = "#05070d", "#e8f1f8", "#2de2e6", "#9d7bff", "#ff5d6c", "#8ea3b5"
FPS, SCENE_S = 24, 4.0


def _lattice():
    base = np.array([[0, 0, 0], [0, .5, .5], [.5, 0, .5], [.5, .5, 0], [.25, .25, .25], [.25, .75, .75], [.75, .25, .75], [.75, .75, .25]])
    atoms = np.array([b + np.array(c) for c in product(range(2), repeat=3) for b in base])
    atoms -= atoms.mean(0)
    bonds = [(i, j) for i in range(len(atoms)) for j in range(i + 1, len(atoms)) if abs(np.linalg.norm(atoms[i] - atoms[j]) - np.sqrt(3) / 4) < .02]
    nv_i = int(np.argmin(np.linalg.norm(atoms, axis=1)))
    return atoms, bonds, nv_i


def _heat_frames(n=60, steps=90):
    out = []
    for kappa_ratio in (1.0, 14.7):
        T = np.zeros((n, n)); f = 0.24 * kappa_ratio / 14.7; frames = []
        for s in range(steps):
            for _ in range(6):
                T[1:-1, 1:-1] += f * (T[2:, 1:-1] + T[:-2, 1:-1] + T[1:-1, 2:] + T[1:-1, :-2] - 4 * T[1:-1, 1:-1])
                T[n // 3 - 2:n // 3 + 2, n // 2 - 3:n // 2 + 3] += 0.08
                T[-1, :] = 0
            frames.append(T.copy())
        out.append(frames)
    return out


def render(path: str | Path = "docs/img/trailer.mp4", fast: bool = False) -> Path:
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fps = 8 if fast else FPS
    per = int(SCENE_S * fps) if not fast else 3
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor=BG)
    atoms, bonds, nv_i = _lattice()
    heat = _heat_frames()
    rng = np.random.default_rng(5)
    freqs = np.linspace(2780, 2960, 700)
    writer = FFMpegWriter(fps=fps, codec="libx264", extra_args=["-pix_fmt", "yuv420p", "-crf", "30", "-preset", "slow"])

    def title(ax, big, small, alpha=1.0):
        ax.text(0.05, 0.9, big, color=INK, fontsize=34, fontweight="bold", transform=ax.transAxes, alpha=alpha, va="top")
        ax.text(0.05, 0.8, small, color=MUTE, fontsize=17, transform=ax.transAxes, alpha=alpha, va="top")

    with writer.saving(fig, str(path), dpi=100):
        for scene in range(5):
            for k in range(per):
                u = k / max(per - 1, 1); fade = min(1.0, 4 * u, 4 * (1 - u) + 0.25)
                fig.clf(); ax = fig.add_axes([0, 0, 1, 1], facecolor=BG); ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")
                if scene == 0:
                    th = 0.6 + 2 * np.pi * u * 0.35; ph = 0.35
                    R = np.array([[np.cos(th), 0, np.sin(th)], [0, 1, 0], [-np.sin(th), 0, np.cos(th)]]) @ np.array([[1, 0, 0], [0, np.cos(ph), -np.sin(ph)], [0, np.sin(ph), np.cos(ph)]])
                    p = atoms @ R.T * 3.2; x, y, z = 12.2 + p[:, 0], 4.5 + p[:, 1], p[:, 2]
                    for i, j in bonds:
                        ax.plot([x[i], x[j]], [y[i], y[j]], color=TEAL, lw=1.4, alpha=.45 * fade)
                    o = np.argsort(z); ax.scatter(x[o], y[o], s=60 + 40 * (z[o] - z.min()), color=TEAL, alpha=fade)
                    ax.scatter([x[nv_i]], [y[nv_i]], s=1500 * (1 + .3 * np.sin(12 * u)), color=RED, alpha=.25 * fade); ax.scatter([x[nv_i]], [y[nv_i]], s=260, color=RED, alpha=fade)
                    ax.text(0.9, 5.2, "ADAMAS", color=INK, fontsize=72, fontweight="bold", alpha=fade)
                    ax.text(0.95, 4.2, "Diamond chips, from wafer to qubit", color="#9fe8f2", fontsize=22, alpha=fade)
                elif scene == 1:
                    title(ax, "Diamond moves heat 15× better", "Same power, same geometry: silicon (left) and diamond (right)", fade)
                    idx = min(len(heat[0]) - 1, int(u * (len(heat[0]) - 1)))
                    for m, x0 in ((0, 1.2), (1, 8.6)):
                        ax.imshow(heat[m][idx], extent=[x0, x0 + 6.2, 0.6, 6.4], cmap="inferno", norm=PowerNorm(0.35, vmin=0, vmax=heat[0][-1].max()), alpha=fade)
                        ax.text(x0, 6.6, ["Silicon", "Diamond"][m], color=INK, fontsize=16, alpha=fade)
                elif scene == 2:
                    title(ax, "Its qubit works at room temperature", "Nitrogen-vacancy resonance splitting as a magnet approaches", fade)
                    b = 5.0 * u
                    spec = nv.odmr_spectrum(freqs, b * np.array([0.35, 0.55, 0.76]), linewidth_mhz=1.5, hyperfine=False)
                    xs = 1 + 14 * (freqs - freqs[0]) / (freqs[-1] - freqs[0]); ys = 1 + 5.2 * (spec - spec.min()) / (1 - spec.min() + 1e-9)
                    ax.plot(xs, ys, color=TEAL, lw=3, alpha=fade); ax.text(12.5, 6.7, f"|B| = {b:.1f} mT", color=INK, fontsize=18, alpha=fade)
                elif scene == 3:
                    title(ax, "Errors get caught, not avoided", "A surface code: flipped qubits (red) light up their checks", fade)
                    n = 9
                    for i in range(n):
                        for j in range(n):
                            err = rng.random() < 0.06
                            ax.scatter(3 + i * 1.1, 0.8 + j * 0.65, s=150 if err else 60, color=RED if err else VIOLET, alpha=fade * (1 if err else .6))
                else:
                    ax.text(1, 5.4, "Eleven interactive labs.", color=INK, fontsize=40, fontweight="bold", alpha=fade)
                    ax.text(1, 4.4, "525 references. Physics tested against Python, SPICE, and Verilog.", color="#9fe8f2", fontsize=20, alpha=fade)
                    ax.text(1, 2.2, "normansrule.github.io/adamas-diamond-framework", color=TEAL, fontsize=22, alpha=fade)
                writer.grab_frame(facecolor=BG)
    plt.close(fig)
    return path


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    p = render(args[0] if args else "docs/img/trailer.mp4", fast="--fast" in sys.argv)
    print("wrote", p, f"{p.stat().st_size / 1e6:.2f} MB")
