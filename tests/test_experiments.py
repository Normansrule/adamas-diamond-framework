from pathlib import Path

import pytest

from adamas import experiments as X

ROOT = Path(__file__).resolve().parents[1]
BOUNDS = {"A": (0, 1000), "B": (500, 20000), "C": (5000, 200000), "D": (50000, 1e9)}


def test_catalog_is_complete_and_priced_by_tier():
    assert len(X.EXPERIMENTS) == 10 and {e["tier"] for e in X.EXPERIMENTS} == set("ABCD")
    for e in X.EXPERIMENTS:
        lo, hi = e["cost"]; blo, bhi = BOUNDS[e["tier"]]
        assert 0 <= lo <= hi and blo <= max(hi, blo) and hi <= bhi, e["id"]
        assert e["parts"] and e["safety"] and e["steps"] and e["analysis"] and e["refs"]
        names = {c[0] for c in e["scene"]}
        for title, detail, uses in e["steps"]:
            assert set(uses) <= names, (e["id"], title, set(uses) - names)
        assert e["lab"].startswith("explorer") or (ROOT / "web" / e["lab"].split("#")[0]).exists()


@pytest.mark.parametrize("kind", sorted({e["expected"] for e in X.EXPERIMENTS}))
def test_expected_results_are_physical(kind):
    r = X.expected(kind)
    assert r
    if kind == "arrhenius":
        assert abs(r["ea_fit_ev"] - 0.37) < 0.03            # the corrected fit recovers the boron level
    if kind == "magnet_distance":
        import numpy as np
        slope = np.polyfit(np.log(r["x"]), np.log(r["series"]["dipole law"]), 1)[0]
        assert abs(slope + 3) < 1e-9


def test_markdown_is_up_to_date():
    assert (ROOT / "docs" / "experiments" / "EXPERIMENTS.md").read_text(encoding="utf-8") == X.to_markdown(), "run: make experiments"
