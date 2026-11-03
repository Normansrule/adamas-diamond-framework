"""Assemble the frames from tools/record_loop.mjs into docs/img/anim_equation_loop.gif (make loop-gif)."""
import sys
from pathlib import Path

from PIL import Image

frames_dir, out = Path(sys.argv[1]), Path(sys.argv[2])
frames = [Image.open(p).convert("RGB") for p in sorted(frames_dir.glob("f*.png"))]
w = 760
frames = [f.resize((w, round(f.height * w / f.width)), Image.LANCZOS).quantize(colors=128, method=Image.Quantize.MEDIANCUT) for f in frames]
durations = [110] * (len(frames) - 1) + [1800]
frames[0].save(out, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
print(out, len(frames), "frames", out.stat().st_size // 1024, "kB")
