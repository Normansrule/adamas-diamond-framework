"""App icons drawn from the ADAMAS logo (the gem of web/assets/site.js), so no binary icon files live in the repository.

    python -m adamas.icons OUT.png [SIZE]      one icon (the desktop build uses desktop/build/icon.png at 1024)

adamas.site calls write_web_icons() for the installable web app (192 and 512 pixels, plus a maskable variant with the
safe-zone padding that Android and desktop launchers crop to).
"""
from __future__ import annotations
import sys
from pathlib import Path

GEM = [(8, 4), (24, 4), (30, 12), (16, 29), (2, 12)]                               # logo outline, 32-unit box
FACETS = [[(8, 4), (12, 12), (16, 4), (20, 12), (24, 4)], [(2, 12), (30, 12)], [(12, 12), (16, 29), (20, 12)]]


def draw(size: int = 512, maskable: bool = False):
    from PIL import Image, ImageDraw, ImageFilter
    S = 4 * size                                                                    # supersample for smooth edges
    bg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(bg)
    r = 0 if maskable else int(S * 0.22)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=r, fill=(5, 7, 13, 255))
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse([S * .18, S * .12, S * .82, S * .76], fill=(45, 226, 230, 90)); glow = glow.filter(ImageFilter.GaussianBlur(S * .09))
    bg = Image.alpha_composite(bg, glow)
    if r:
        m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, S - 1, S - 1], radius=r, fill=255); bg.putalpha(m)
    pad = 0.24 if maskable else 0.14                                               # maskable icons keep the art inside the 80% safe zone
    import numpy as np
    k = S * (1 - 2 * pad) / 32
    ox, oy = S * pad, S * pad + S * 0.02
    P = lambda pts: [(ox + x * k, oy + y * k) for x, y in pts]                      # noqa: E731
    t = np.add.outer(np.arange(S), np.arange(S)) / (2.0 * S)                        # teal to violet, top-left to bottom-right
    rgba = np.stack([111 + 46 * t, 243 - 120 * t, np.full_like(t, 255), np.full_like(t, 255)], axis=-1).astype(np.uint8)
    grad = Image.fromarray(rgba, "RGBA")
    mask = Image.new("L", (S, S), 0); ImageDraw.Draw(mask).polygon(P(GEM), fill=255)
    bg.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(bg)
    for f in FACETS:
        d.line(P(f), fill=(28, 52, 96, 255), width=max(2, int(S * 0.009)), joint="curve")
    return bg.resize((size, size), Image.LANCZOS)


def write(path: str | Path, size: int = 512, maskable: bool = False) -> Path:
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True); draw(size, maskable).save(p); return p


def write_web_icons(out_dir: str | Path) -> list[Path]:
    d = Path(out_dir)
    return [write(d / "icon-192.png", 192), write(d / "icon-512.png", 512), write(d / "maskable-512.png", 512, maskable=True),
            write(d / "apple-touch-icon.png", 180)]


if __name__ == "__main__":
    print(write(sys.argv[1] if len(sys.argv) > 1 else "icon.png", int(sys.argv[2]) if len(sys.argv) > 2 else 1024))
