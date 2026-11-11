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
    for e in X.EXTENSIONS:
        if traveler.step_index(e["after"]) >= first_metal:
            assert e["t_max_c"] is None or e["t_max_c"] <= 500, e["id"]
            assert any(c[3] is not None and c[3] <= 500 and c[1] == "°C" for c in e["checks"]) or e["t_max_c"] is not None, e["id"]


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
