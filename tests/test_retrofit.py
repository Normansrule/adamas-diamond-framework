"""Retrofit Map (adamas.retrofit): every route and product is labeled, cited and tied to real build stages and devices."""
from __future__ import annotations

import sys
from pathlib import Path

from adamas import retrofit as R
from adamas.qdl import DEVICES
from adamas.traveler import STEPS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from refs_common import load  # noqa: E402


def test_routes_and_products_are_labeled_and_cited():
    keys = {r.key for r in load()}
    stages = {k for k, _, _ in R.STAGES}
    ids = [r[0] for r in R.ROUTES]
    assert len(ids) == len(set(ids)) == 31
    for r in R.routes():
        assert r["stage"] in stages and r["level"] in R.LEVELS and r["refs"] and set(r["refs"]) <= keys, r["id"]
        assert r["fact"].strip() and r["left"].strip()
    devices = {d["id"] for d in DEVICES}
    for p in R.products():
        assert p["device"] in devices and p["level"] in ("in production", "on diamond") and set(p["refs"]) <= keys, p["name"]
    assert {s for _, _, st in R.STAGES for s in st} <= {s["id"] for s in STEPS}


def test_retrofit_routes_are_never_called_demonstrated_on_diamond():
    # a retrofit is proven elsewhere; the text must say so, and company claims must be marked
    for r in R.routes():
        if r["level"] == "retrofit":
            assert any(w in (r["fact"] + r["left"]) for w in ("silicon", "SiC", "non-diamond", "Not shown on diamond", "proposal")), r["id"]
    for rid in ("R03", "R06", "R08", "R14", "R15", "R22"):
        assert "company statement" in next(x for x in R.routes() if x["id"] == rid)["fact"], rid


def test_summary_counts_and_step_levels():
    s = R.summary()
    assert (s["routes"], s["in production"], s["on diamond"], s["retrofit"], s["proposed"]) == (31, 10, 18, 3, 0)
    assert s["devices_on_market"] == ["QDL-01", "QDL-12", "QDL-17", "QDL-19", "QDL-20"]
    assert sum(s["steps_by_level"].values()) == len(STEPS) == 20
    assert s["step_levels"]["S15"] == s["step_levels"]["S16"] == "retrofit"      # standard lithography and metal steps
    assert s["step_levels"]["S06"] == "in production"                            # implantation services list diamond


def test_numbers_match_their_sources():
    f = {r["id"]: r["fact"] for r in R.routes()}
    assert "about 90 mm" in f["R04"] and "155 carats" in f["R04"] and "4 × 10⁷ cm⁻²" in f["R04"]
    assert "6 kW at 2.45 GHz" in f["R07"] and "10 to 220 Torr" in f["R07"]
    assert "4 to 5 MeV" in f["R10"] and "3 × 10¹⁷ cm⁻²" in f["R10"]
    assert "Sq 0.361 nm" in f["R13"] and "13.3 µm/h" in f["R13"]
    assert "45.1 nm/min" in f["R21"] and "16.9 : 1" in f["R21"] and "0.47 nm" in f["R21"]
    assert "1700 V" in f["R23"] and "1200 V" in f["R23"] and "450 °C" in f["R23"]
    assert "45 %" in f["R19"] and "200 nm" in f["R19"]
    assert "1500 hours at 400 °C" in f["R27"] and "290 °C" in f["R28"] and "5 W" in f["R30"]
    p = {x["name"]: x["fact"] for x in R.products()}
    assert "2 µT/√Hz" in p["Qnami ProteusQ scanning NV microscope"] and "two qubits" in p["Quantum Brilliance room-temperature diamond quantum accelerator"]


def test_page_is_current_and_figure_is_listed():
    assert (ROOT / "docs" / "process" / "RETROFIT.md").read_text(encoding="utf-8") == R.to_markdown(), "run: adamas build docs"
    from adamas import figures_apps
    assert figures_apps.fig_retrofit_map in figures_apps.ALL
    assert "superconducting" in R.to_markdown() and "none is compared" in R.to_markdown()
