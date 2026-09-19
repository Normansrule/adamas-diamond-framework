"""Regenerate every figure used by the README and docs into docs/img/."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adamas.figures import make_all  # noqa: E402

if __name__ == "__main__":
    for p in make_all(ROOT / "docs" / "img"):
        print("wrote", p.relative_to(ROOT))
