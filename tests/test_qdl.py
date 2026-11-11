"""Quantum Device Library (adamas.qdl): completeness, sources, traced numbers, routes, pass/fail checks, honesty guards,
and that the generated pages are current."""
import json
import math
import re
from pathlib import Path

import pytest

from adamas import atlas, qdl, traveler

ROOT = Path(__file__).resolve().parents[1]
BIB = (ROOT / "references" / "references.bib").read_text(encoding="utf-8")
KEYS = set(re.findall(r"@\w+\{([^,]+),", BIB))
FIELDS = ("id", "name", "family", "analogy", "function", "explanation", "status", "gates", "entanglement", "use_cases",
          "fom", "route", "layers", "checks", "failures", "open_problems", "links")


def test_every_device_is_complete_and_uses_known_labels():
    ids = [d["id"] for d in qdl.DEVICES]
    assert len(ids) == len(set(ids)) >= 28
    for d in qdl.DEVICES:
        assert all(f in d for f in FIELDS), d["id"]
        assert d["status"]["label"] in qdl.STATUSES and d["family"] in qdl.FAMILIES
        assert d["function"] and d["explanation"] and d["status"]["refs"]
        for g in d["gates"] + d["entanglement"] + d["use_cases"]:
            assert g["label"] in qdl.STATUSES and g["refs"], (d["id"], g)
        assert d["checks"] or d.get("no_check"), f"{d['id']}: a check or the reason there is none"


def test_every_source_key_exists_in_the_bibliography():
    missing = qdl.refs_used() - KEYS
    assert not missing, missing


def test_every_figure_of_merit_is_traced_to_a_source_or_to_code():
    for d in qdl.DEVICES:
        for k, f in d["fom"].items():
            c, t = f["current"], f["target"]
            assert c or t, (d["id"], k)
            if c and not c.get("todo"):
                assert c["label"] in qdl.STATUSES
                if c.get("python"):
                    assert qdl.PYTHON[c["python"]]() == pytest.approx(c["value"], rel=1e-9), (d["id"], k)
                else:
                    assert c["refs"], (d["id"], k)
                if c["label"] == "simulated":
                    assert c.get("python"), f"{d['id']} {k}: a simulated number names its function"
            if t and t["value"] is not None and t.get("python"):
                assert qdl.PYTHON[t["python"]]() == pytest.approx(t["value"], rel=1e-9), (d["id"], k)
            if t and t["value"] is not None and not t.get("python"):
                assert t.get("refs") or "ADAMAS" in t["basis"] or "witness" in t["basis"] or "limit" in t["basis"], (d["id"], k)


def test_computed_design_values_follow_the_coupling_law():
    from adamas.coupling import gate_fidelity_bound
    assert gate_fidelity_bound(qdl.r_max_nm(0.99), qdl.T2_ROOM_MS) == pytest.approx(0.99, rel=1e-9)
    assert qdl.r_max_nm(0.9) > qdl.r_max_nm(0.99) > 10.0       # a looser target allows a wider spacing
    assert gate_fidelity_bound(10.0, qdl.required_t2_10nm_ms()) == pytest.approx(0.99, rel=1e-9)   # one model for both


def test_routes_use_real_traveler_steps_and_atlas_machines():
    steps = {s["id"] for s in traveler.STEPS}
    for d in qdl.DEVICES:
        r = d["route"]
        assert r["variant"] in traveler.VARIANTS
        assert set(r["steps"]) <= steps and set(r["overrides"]) <= set(r["steps"]), d["id"]
        assert set(r["atlas"]) <= set(atlas.ATLAS), d["id"]
        for x in r["extra"]:
            assert x["id"] not in steps and set(x["atlas"]) <= set(atlas.ATLAS) and x["refs"]
            assert x["after"] in r["steps"], f"{d['id']} {x['id']}: anchor step must be on the route"
        b = qdl.build_process(d)
        assert [s["id"] for s in b if not s["missing"] and not s["extension"]] == r["steps"]
        assert sum(s["missing"] or s["extension"] for s in b) == len(r["extra"])


def test_extra_step_ids_are_unique():
    ids = [sid for _, sid, _ in qdl.missing_steps()]
    assert len(ids) == len(set(ids))


def test_atlas_matches_the_build_program_outline():
    text = (ROOT / "docs" / "phase0" / "BUILD_PROGRAM_OUTLINE.md").read_text(encoding="utf-8")
    rows = dict(re.findall(r"^\| (M\d\d) \| ([^|]+?) \|", text, flags=re.M))
    assert set(rows) == set(atlas.ATLAS) and len(rows) == 60
    assert all(atlas.ATLAS[k][0] == v.strip() for k, v in rows.items())


def test_missing_steps_and_open_numbers_are_listed_in_status():
    status = (ROOT / "docs" / "STATUS.md").read_text(encoding="utf-8")
    assert "docs/devices/README.md" in status
    for dev, sid, _ in qdl.missing_steps():
        assert sid in status, f"{dev} {sid} missing from docs/STATUS.md"
    for dev, name, _ in qdl.open_numbers():
        assert f"| {dev} | {name} |" in status, f"{dev} {name} missing from docs/STATUS.md"


def test_confirmed_numbers_match_their_papers():
    """Values read from the papers in v0.42.0; a change must be re-checked against the paper."""
    want = {("QDL-09", "gain"): (10, "babinec2010"), ("QDL-12", "sens"): (0.9, "wolf2015"), ("QDL-17", "res"): (20, "maletinsky2012"),
            ("QDL-18", "res"): (3, "glenn2018"), ("QDL-21", "sens"): (15, "barry2016"), ("QDL-22", "gain"): (170000, "king2015"),
            ("QDL-24", "e"): (140, "dolde2011")}
    for (dev, k), (v, key) in want.items():
        c = qdl.BY_ID[dev]["fom"][k]["current"]
        assert c["value"] == v and c["refs"] == [key] and c["conditions"] and not c.get("todo"), (dev, k)
    assert all(qdl.BY_ID[d]["fom"][k]["current"]["label"] == "demonstrated" for d, k in want)       # all at room temperature
    units = {("QDL-12", "sens"): "pT/√Hz", ("QDL-21", "sens"): "pT/√Hz", ("QDL-24", "e"): "V/cm/√Hz", ("QDL-18", "res"): "Hz", ("QDL-17", "res"): "nm"}
    assert all(qdl.BY_ID[d]["fom"][k]["unit"] == u for (d, k), u in units.items())
    assert len(qdl.open_numbers()) == 2


@pytest.mark.parametrize("dev,i", [(d["id"], i) for d in qdl.DEVICES for i in range(len(d["checks"]))])
def test_each_check_passes_nominal_and_fails_its_degraded_twin(dev, i):
    assert qdl.run_check(dev, i)["pass"] and not qdl.run_check(dev, i, degraded=True)["pass"]


def test_checks_pass_correct_setups_and_reject_faulty_ones_over_many_seeds():
    for d in qdl.DEVICES:
        for i in range(len(d["checks"])):
            assert qdl.pass_rate(d["id"], i, 60) >= 0.9, (d["id"], i)
            assert qdl.pass_rate(d["id"], i, 60, degraded=True) <= 0.05, (d["id"], i)


def test_honesty_guards():
    for d in qdl.DEVICES:
        st = d["status"]
        if st["label"] == "cryogenic":
            assert st["temperature_k"] is not None and st["temperature_k"] < 77, d["id"]      # never shown as a 300 K device
        if d["analogy"]:
            assert d["analogy"]["label"] and d["analogy"]["fits"] and d["analogy"]["breaks"]
        for k, f in d["fom"].items():
            n = f["name"].lower()
            assert not ("bell" in n and "gate" in n), "Bell and gate fidelity are different fields"
    coupler = qdl.BY_ID["QDL-04"]["fom"]
    assert "bell" in coupler and "gate" in coupler and coupler["bell"]["current"]["refs"] != coupler["gate"]["current"]["refs"]
    assert "krinner2019" in qdl.SUPERCONDUCTING_NOTE and "mK" in qdl.SUPERCONDUCTING_NOTE
    docs = qdl.documents()
    for d in qdl.DEVICES:
        if d["analogy"]:
            page = docs[f"{d['id']}.md"]
            assert f"{d['analogy']['label']} (analogy)" in page and d["name"] in page     # always next to the real name


def test_generated_pages_and_golden_values_are_current():
    for name, text in qdl.documents().items():
        assert (ROOT / "docs" / "devices" / name).read_text(encoding="utf-8") == text, "run: adamas build docs"
    g = json.loads((ROOT / "web" / "tests" / "qdl_golden.json").read_text(encoding="utf-8"))
    ref = qdl.golden()
    assert g["rows"] == ref["rows"] and math.isclose(g["r_max_099"], ref["r_max_099"], rel_tol=1e-9)


def test_site_json_carries_the_library():
    j = qdl.to_json()
    assert len(j["devices"]) == len(qdl.DEVICES) and all("build" in d and "results" in d for d in j["devices"])
    json.dumps(j)                                                                                   # serializable
