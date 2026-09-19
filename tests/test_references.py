import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def test_reference_count_and_unique_keys():
    from refs_common import load
    refs = load()
    keys = [r.key for r in refs]
    assert len(keys) >= 300
    assert len(keys) == len(set(keys))


def test_every_cited_key_exists():
    out = subprocess.run([sys.executable, "check_citations.py"], cwd=ROOT / "tools", capture_output=True, text=True)
    assert out.returncode == 0, out.stdout
