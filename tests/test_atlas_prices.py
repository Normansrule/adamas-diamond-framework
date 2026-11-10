"""Machines and Facilities Atlas: every machine has exactly one price kind, every sourced price names a reference in the
database, every estimate points at a real experiment part, and the generated page is current."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from adamas import atlas_prices as A
from adamas import build_program as B
from adamas.atlas import ATLAS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from refs_common import load  # noqa: E402


def test_every_machine_has_exactly_one_kind_and_a_place():
    assert set(A.PLACE) == set(ATLAS)
    for i in ATLAS:
        primary = [i in A.SOURCED or i in A.ESTIMATE, i in A.INCLUDED, i in A.UNPRICED]
        assert sum(primary) == 1, i            # sourced or estimate (sourced wins), included, or unpriced: never two, never none
        fac, acc = A.PLACE[i]
        assert fac in A.FACILITY and acc in A.ACCESS
    assert all(r.strip() for r in A.UNPRICED.values())
    assert all(v[0] in ATLAS and v[0] not in A.INCLUDED for v in A.INCLUDED.values())


def test_sourced_prices_cite_the_reference_database():
    keys = {r.key: r for r in load()}
    quotes = [q for qs in A.SOURCED.values() for q in qs] + [(*f, "") for f in A.ACCESS_FEES]
    for key, listed, cur, unit, prices, _ in quotes:
        assert key in keys and keys[key].status == "V", key           # a page that was fetched and read
        assert "accessed" in keys[key].locator and listed and unit
        assert cur in ("USD", "EUR") and prices and all(v > 0 for v in prices.values())
    assert set(A.summary()["keys"]) <= set(keys)


def test_estimates_come_from_experiment_parts_lists():
    from adamas.experiments import EXPERIMENTS
    parts = {(e["id"], p[0]): (p[2], p[3]) for e in EXPERIMENTS for p in e["parts"]}
    for i, items in A.ESTIMATE.items():
        assert all(it in parts for it in items), i
        e = A.entry(i)["estimate"]
        assert e["usd_low"] == sum(parts[it][0] for it in items) and e["usd_high"] == sum(parts[it][1] for it in items)
        assert e["usd_low"] <= e["usd_high"]


def test_phase_machine_lists_are_in_the_atlas_and_counted():
    for ph in ("P3", "P4", "P5", "P6", "P7", "P8"):
        ids = getattr(B, f"{ph}_MACHINES")
        assert set(ids) <= set(ATLAS)
        assert all(ph in A.phases_using(i) for i in ids)
    s = A.summary()
    assert s["machines"] == len(ATLAS) == 60
    assert s["sourced"] + s["estimate"] + s["included"] + s["unpriced"] == 60
    assert s["by_phase"]["P8"]["unpriced"] == 4 and s["by_phase"]["P4"]["sourced"] >= 10


def test_p6_shuttle_price_and_short_cells():
    assert "70 EUR per Tiny Tapeout tile [tinytapeout2026]" in A.mpw_prices()
    assert f"minimum {A.XH018_MIN_MM2} mm²" in A.mpw_prices() and "not totalled" in B._p6_md()
    assert A.short_price("M18").startswith("not priced")
    assert "closest listed tool" in A.short_price("M22") and "[wnf2026]" in A.short_price("M22")
    assert A.short_price("M12") == "US$158 to 569 per hour, E-beam Lithography [wnf2026] ([Atlas](ATLAS.md))"


def test_money_format():
    assert A._money("USD", 49.4) == "US$49.4" and A._money("USD", 6325) == "US$6,325" and A._money("EUR", 1126) == "1,126 EUR"


@pytest.mark.parametrize("name", ["ATLAS.md"])
def test_atlas_page_is_current(name):
    assert (ROOT / "docs" / "build" / name).read_text(encoding="utf-8") == A.to_markdown(), "run: adamas build docs"
