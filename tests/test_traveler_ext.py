"""Extension steps X07a to X27a: each is written for the device that routes through it, with sourced parameters,
an evidence label, real Atlas machines, and the traveler's thermal rule respected."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from adamas import qdl, traveler
from adamas import traveler_ext as X
from adamas.atlas import ATLAS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from refs_common import load  # noqa: E402

KEY = re.compile(r"\[([a-z][a-z0-9]*\d{4}[a-z0-9]*)\]")


def test_every_device_extra_step_is_written():
    extras = {x["id"]: (d["id"], x) for d in qdl.DEVICES for x in d["route"].get("extra", [])}
    assert set(extras) == set(X.BY_ID) and len(X.EXTENSIONS) == 11
    assert qdl.missing_steps() == []
    for sid, (dev, x) in extras.items():
        e = X.BY_ID[sid]
        assert e["devices"] == [dev] and e["after"] == x["after"], sid


def test_fields_labels_sources_and_machines():
    keys = {r.key for r in load()}
    modules = {m[0] for m in traveler.MODULES}
    for e in X.EXTENSIONS:
        assert e["label"] in X.LABELS and e["module"] in modules and e["after"] in traveler.ORDER
        assert set(e["atlas"]) <= set(ATLAS) and e["safety"] and e["failures"] and e["checks"] and e["silicon"]
        for _, _, src in e["params"]:
            cited = KEY.findall(src)
            assert cited or src == "ADAMAS", (e["id"], src)        # every parameter has a paper or is an ADAMAS rule
            assert set(cited) <= keys
        for _, _, lo, hi, src in e["checks"]:
            assert src.startswith("ADAMAS") or KEY.search(src), (e["id"], src)
            assert lo is None or hi is None or lo <= hi


def test_steps_after_gold_respect_the_thermal_rule():
    first_metal = traveler.step_index("S09")
    late = [e for e in X.EXTENSIONS if traveler.step_index(e["after"]) >= first_metal]
    assert {e["id"] for e in late} == {"X15a", "X27a"}
    for e in late:
        assert e["t_max_c"] is None or e["t_max_c"] <= 500, e["id"]
        assert any(c[1] == "°C" and c[3] is not None and c[3] <= 500 for c in e["checks"]), e["id"]   # the rule is a check


def test_labels_have_web_styles_and_refs_are_counted():
    html = (ROOT / "web" / "devices.html").read_text(encoding="utf-8")
    assert all(f".st.{lab}" in html for lab in X.LABELS)
    used = qdl.refs_used()
    assert {"babinec2010", "tao2014", "maletinsky2012", "breeze2018"} <= used
    assert X.badge(X.BY_ID["X15a"]) == "proposed · cryogenic" and X.badge(X.BY_ID["X09a"]) == "demonstrated"


def test_device_machines_include_extension_machines():
    for d in qdl.DEVICES:
        m = set(qdl.route_atlas(d))
        assert set(d["route"]["atlas"]) <= m
        for x in d["route"].get("extra", []):
            assert set(X.BY_ID[x["id"]]["atlas"]) <= m, (d["id"], x["id"])


def test_proposed_steps_say_so_and_cmos_target_is_computed():
    for e in X.EXTENSIONS:
        if e["label"] == "proposed":
            assert any("proposal" in b or "to source" in b or "No device" in b or "no process" in b for _, b, _ in e["params"]), e["id"]
    c = [ch for ch in X.BY_ID["X27a"]["checks"] if ch[0] == "Magnetic sensitivity"][0]
    assert c[3] == X.KIM2019_TARGET_FACTOR * X.KIM2019_SENS_UT


def test_device_pages_show_extension_steps():
    d = qdl.BY_ID["QDL-09"]
    b = [s for s in qdl.build_process(d) if s["id"] == "X09a"][0]
    assert b["extension"] and not b["missing"] and b["label"] == "demonstrated" and "babinec2010" in b["refs"]
    assert "### X09a" in traveler.to_markdown()
    assert (ROOT / "docs" / "process" / "TRAVELER.md").read_text(encoding="utf-8") == traveler.to_markdown(), "run: adamas build docs"


def test_v044_parameters_match_their_sources():
    """Values read in v0.44.0; a change must be re-checked against the source."""
    from adamas.traveler_ext import BY_ID
    p = {s["id"]: {n: (v, k) for n, v, k in s["params"]} for s in BY_ID.values()}
    assert p["X07a"]["Doping"] == ("Phosphorus about 1 × 10¹⁸ cm⁻³ (n-layer), boron about 1 × 10¹⁹ cm⁻³ (p-type substrate)", "[mizuochi2014]")
    assert "4 × 10⁴ photons per second" in p["X07a"]["Operating point"][0] and "14 mA" in p["X07a"]["Operating point"][0]
    assert "to source" in p["X07a"]["Layer thicknesses, growth temperature, gas mix, substrate orientation"][0]
    r = p["X13a"]["Demonstrated diamond resonator (not the proposal's membrane)"]
    assert r[1] == "[mitchell2016]" and "6.1 to 6.8 × 10⁴" in r[0] and "above 9000" in r[0] and "940 nm" in r[0]
    assert BY_ID["X13a"]["label"] == "proposed"                 # the proposal stays proposed; the microdisk is a demonstrated alternative
    assert "Adámas Nanotechnologies" in p["X20a"]["Material"][0]       # the supplier's own spelling, as in [lattispec2026]
    d = p["X25a"]["Diamond"][0]
    assert "nitric acid for 48 h" in d and "2.1 × 2.1 × 2.6 mm³" in d and "{100} faces" in d
    rect = next(c for c in BY_ID["X07a"]["checks"] if c[0].startswith("Diode rectifies"))[4]
    assert "nine orders of magnitude at 30 V" in rect and "[mizuochi2014]" in rect
    assert "not stated there" in r[0] and "(demonstrated)" in r[0]
    e = p["X13a"]["Etch conditions from the same group's later microdisk paper"]            # v0.47.0
    assert "reported, preprint" in e[0] and e[1] == "[mitchell2019]" and "250 °C" in e[0] and "1000 W" in e[0] and "30 standard cubic centimetres per minute (sccm)" in e[0]
    d = p["X25a"]["Irradiation stated by a later room-temperature maser amplifier"]
    assert "reported, preprint" in d[0] and d[1] == "[day2024]" and "3 MeV" in d[0] and "1 × 10¹⁸ cm⁻²" in d[0] and "not stated" in d[0]
