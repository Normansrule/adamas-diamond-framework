"""Fab Journey (adamas.journey): four scopes, real steps and machines, computed checkpoints, safety, the photo log,
and generated pages."""
import re
from pathlib import Path

import pytest

from adamas import atlas, journey, traveler

ROOT = Path(__file__).resolve().parents[1]
KEYS = set(re.findall(r"@\w+\{([^,]+),", (ROOT / "references" / "references.bib").read_text(encoding="utf-8")))


def test_four_scopes_with_the_planned_step_counts():
    assert [len(journey.steps(L["id"])) for L in journey.LEVELS] == [10, 11, 12, 8]
    ids = [s["id"] for L in journey.LEVELS for s in journey.steps(L["id"])]
    assert len(ids) == len(set(ids))


def test_every_step_is_complete_and_uses_real_machines():
    tsteps = {s["id"] for s in traveler.STEPS}
    for L in journey.LEVELS:
        for s in journey.steps(L["id"]):
            assert s["title"] and s["action"] and s["label"] in ("demonstrated", "reported", "simulated", "proposed")
            assert {p["id"] for p in s["parts"]} <= set(atlas.ATLAS), s["id"]
            assert s["diagram"]["kind"] in ("setup", "section", "yield", "spc", "gate")
            if L["id"] == "L2" and s.get("traveler"):
                assert s["id"] in tsteps
            assert set(s["refs"]) <= KEYS, s["id"]


def test_l2_follows_the_coupled_pair_route_and_the_cross_sections_chain():
    from adamas import qdl
    s2 = journey.steps("L2")
    assert [s["id"] for s in s2 if s.get("traveler")] == qdl.BY_ID["QDL-04"]["route"]["steps"]
    for a, b in zip(s2, s2[1:]):
        assert b["diagram"]["before"] == a["diagram"]["after"]           # each step starts where the last one ended
    assert "7.5 ± 3.0 nm" in " ".join(next(s for s in s2 if s["id"] == "S06")["diagram"]["after"])   # 5 keV, rule of thumb


def test_nothing_is_labeled_demonstrated_without_our_own_evidence():
    assert all(s["label"] != "demonstrated" for L in journey.LEVELS for s in journey.steps(L["id"]))


def test_every_hands_on_step_has_safety_text_and_no_dangling_references():
    for L in journey.LEVELS:
        for s in journey.steps(L["id"]):
            if s["diagram"]["kind"] in ("setup", "section"):
                assert s["safety"], s["id"]
            assert not any(x.strip().startswith("As S") for x in s["safety"]), s["id"]


def test_hazardous_steps_carry_safety_and_point_to_training():
    for L in journey.LEVELS:
        for s in journey.steps(L["id"]):
            if s.get("traveler"):
                t = next(x for x in traveler.STEPS if x["id"] == s["id"])
                assert set(t["safety"]) <= set(s["safety"]) or any(x.startswith("As S") for x in t["safety"])
    assert "training" in journey.TRAINING and all(journey.steps("L0")[0]["safety"])
    md = journey.documents()
    assert all(journey.TRAINING in md[f"{L['id']}.md"] for L in journey.LEVELS)


def test_checkpoints_are_computed_and_pass_for_a_correct_setup():
    n = 0
    for L in journey.LEVELS:
        for s in journey.steps(L["id"]):
            for c in s["checkpoints"]:
                n += 1
                assert c["python"].startswith("adamas.") and c["value"]
                assert c["pass"] in (True, None), (s["id"], c)
    assert n >= 10


def test_placement_yield_is_a_probability_and_peaks_near_one_nv_per_site():
    ys = {n: journey.placement_yield(n) for n in (1, 30, 100, 300, 1000)}
    assert all(0 <= y <= 1 for y in ys.values()) and ys[100] > ys[30] and ys[100] > ys[300] > ys[1000]   # peak near 1/conversion
    assert journey.cells_to_write(100, 0.05) == pytest.approx(2000.0) and journey.cells_to_write(1, 0) == float("inf")


def test_photo_log_rows_are_open_licensed_credited_and_exist():
    for r in journey.images():
        assert r["license"] in journey.LICENSES, r
        assert r["author"] and r["source"].startswith("http") and r["credit"], r
        assert (ROOT / "docs" / "img" / "photos" / r["file"]).exists(), r
    shown = [s for L in journey.LEVELS for s in journey.steps(L["id"]) if s["photo"]["status"] == "photo"]
    assert len(shown) == len([r for r in journey.images() if r.get("step")])


def test_generated_pages_are_current():
    for name, text in journey.documents().items():
        assert (ROOT / "docs" / "journey" / name).read_text(encoding="utf-8") == text, "run: adamas build docs"
