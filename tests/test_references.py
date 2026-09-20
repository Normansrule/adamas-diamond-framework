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


def test_verifier_tolerates_umlauts_volume_suffixes_and_missing_authors():
    from refs_common import Ref
    import verify_refs
    ref = Ref("x2021", "Stuerner, F. M.; Brenneis, A.", "2021", "Integrated and portable magnetometer based on nitrogen-vacancy ensembles in diamond",
              "Advanced Quantum Technologies", "4, 2000111", ("sens",), "K")
    hit = {"title": [ref.title], "volume": "4", "issued": {"date-parts": [[2021]]}, "author": [{"family": "Stürner"}]}
    assert verify_refs.compare(ref, hit)[0]
    old = Ref("c1918", "Czochralski, J.", "1918", "Ein neues Verfahren", "Z. Phys. Chem.", "92, 219", ("si",), "K")
    assert verify_refs.compare(old, {"title": ["Ein neues Verfahren"], "volume": "92U", "issued": {"date-parts": [[1918]]},
                                     "author": [{"family": "Czochralski"}]})[0]
    assert verify_refs.compare(ref, dict(hit, author=[]))[0]          # exact title, publisher deposited no authors
    assert "johnson1965" in verify_refs.load_overrides()


def test_verifier_handles_multiline_markup_titles_and_odd_family_names():
    from refs_common import Ref
    import verify_refs
    ref = Ref("kasu2017", "Kasu, M.", "2017", "Diamond field-effect transistors for RF power electronics: novel NO2 hole doping and "
              "low-temperature deposited Al2O3 passivation", "Japanese Journal of Applied Physics", "56, 01AA01", ("dev",), "K")
    messy = ("Diamond field-effect transistors for RF power electronics: Novel NO\\n                    <sub>2</sub>\\n"
             "                    hole doping and low-temperature deposited Al\\n                    <sub>2</sub>\\n"
             "                    O\\n                    <sub>3</sub>\\n                    passivation")
    hit = {"title": [messy], "volume": "56", "issued": {"date-parts": [[2017]]}, "author": [{"family": "Kasu"}]}
    ok, sim, problems = verify_refs.compare(ref, hit)
    assert ok and sim > 0.97, problems
    ko = Ref("kanaya1972", "Kanaya, K.; Okayama, S.", "1972", "Penetration and energy-loss theory of electrons in solid targets",
             "Journal of Physics D", "5, 43", ("lit",), "K")
    assert verify_refs.compare(ko, {"title": [ko.title], "volume": "5", "issued": {"date-parts": [[1972]]},
                                    "author": [{"family": "K Kanaya"}]})[0]
    ov = verify_refs.load_overrides()
    assert ov["gorini1976"][0] == "CONFIRMED" and ov["moore1965"][0] == "NOT-INDEXED"


def test_packaging_files_are_intact_and_versions_agree():
    import re
    import adamas
    root = ROOT
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    assert "[project]" in pyproject and "cff-version" in citation
    version = re.search(r'^version = "([^"]+)"', pyproject, re.M).group(1)
    assert adamas.__version__ == version
    assert f"version: {version}" in citation
