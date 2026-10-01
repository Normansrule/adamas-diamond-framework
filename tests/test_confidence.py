import json
import shutil
import subprocess
from pathlib import Path

import pytest

from adamas import uncertainty as U
from adamas import validation as V

ROOT = Path(__file__).resolve().parents[1]


def test_no_validation_row_fails_and_discrepancies_are_explained():
    for r in V.rows():
        assert r.status != "FAIL", (r.check, r.model, r.reference)
        if r.status == "known discrepancy":
            assert len(r.discrepancy) > 20


def test_validation_markdown_is_current():
    assert (ROOT / "docs" / "VALIDATION.md").read_text(encoding="utf-8") == V.to_markdown(), "run: make validation"


def test_power_ratio_depends_only_on_mobility_and_field():
    b = U.baseline(U.POWER)
    assert abs(U.power_ratio(b) - (3800 * 10 ** 2 / (950 * 3 ** 2)) ** 0.5) < 1e-6
    assert abs(U.power_ratio({**b, "Diamond permittivity": 5.6}) - U.power_ratio(b)) < 1e-9


def test_monte_carlo_is_below_the_optimistic_baseline_and_tornado_is_ordered():
    mc = U.monte_carlo("power", 1000)
    assert mc["p10"] < mc["p50"] < mc["p90"] and mc["p50"] < mc["baseline"]
    t = U.tornado("quantum")
    assert t[0]["name"] == "Readout time" and all(a["swing"] >= b["swing"] for a, b in zip(t, t[1:]))


@pytest.mark.skipif(shutil.which("node") is None, reason="node missing")
def test_browser_monte_carlo_agrees_with_python(tmp_path):
    js = tmp_path / "u.mjs"
    js.write_text(f"import * as U from '{(ROOT / 'web/assets/sim/uncertainty.js').as_uri()}';\n"
                  f"const P = {json.dumps({k: list(v) for k, v in U.POWER.items()})};\n"
                  "const s = U.lhs(P, 4000).map(U.powerRatio).sort((a, b) => a - b); console.log(U.percentile(s, 0.5));")
    js_p50 = float(subprocess.run(["node", str(js)], capture_output=True, text=True, check=True).stdout)
    assert abs(js_p50 / U.monte_carlo("power", 4000)["p50"] - 1) < 0.03
