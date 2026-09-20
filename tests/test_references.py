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


def test_verifier_compare_is_robust_to_bad_crossref_records():
    from refs_common import Ref
    import verify_refs
    ref = Ref("dolde2013", "Dolde, F.; Jakobi, I.", "2013", "Room-temperature entanglement between single defect spins in diamond",
              "Nature Physics", "9, 139", ("qc",), "K")
    good = {"title": ["Room-temperature entanglement between single defect spins in diamond"], "volume": "9",
            "issued": {"date-parts": [[2013, 2]]}, "author": [{"family": "Dolde"}]}
    assert verify_refs.compare(ref, good)[0]
    no_year = dict(good, issued={"date-parts": [[None]]})          # the record shape that crashed v0.2.0
    ok, _, problems = verify_refs.compare(ref, no_year)
    assert not ok and "Crossref has no year" in problems
    wrong_volume = dict(good, volume="10")
    assert "volume 9 vs Crossref 10" in verify_refs.compare(ref, wrong_volume)[2]
    assert not verify_refs.compare(ref, {})[0]
