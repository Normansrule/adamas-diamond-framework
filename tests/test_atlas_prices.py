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
        primary = [i in A.SOURCED or i in A.ESTIMATE, i in A.INCLUDED, i in A.NO_COST, i in A.UNPRICED]
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
    assert sum(s[k] for k in A.KINDS) == 60
    assert (s["sourced"], s["estimate"], s["included"], s["no cost"], s["unpriced"]) == (22, 20, 1, 1, 16)   # as stated in CHANGELOG and AUDIT
    assert s["by_phase"]["P8"]["unpriced"] == 4 and s["by_phase"]["P4"]["sourced"] == 11


def test_p6_shuttle_price_and_short_cells():
    assert "70 EUR per Tiny Tapeout tile [tinytapeout2026]" in A.mpw_prices()
    assert f"minimum {A.XH018_MIN_MM2} mm²" in A.mpw_prices() and "not totalled" in B._p6_md()
    assert A.short_price("M18").startswith("not priced")
    assert all("closest listed tool" in A.short_price(i) for i in A.SUBSTITUTE)
    assert "closest listed tool" not in A.short_price("M12") and A.SUBSTITUTE <= set(A.SOURCED)
    assert A.short_price("M12") == ("US$158 to 569 per hour, E-beam Lithography [wnf2026]; users outside the University of "
                                    "Washington add 15.6 % ([Atlas](ATLAS.md))")
    assert "4 metal layers" in A.mpw_prices()


def test_money_format():
    assert A._money("USD", 49.4) == "US$49.40" and A._money("USD", 6325) == "US$6,325" and A._money("EUR", 1126) == "1,126 EUR"


# Every sourced number as read from its page on 10 November 2026. A change here must be re-checked against the page.
GOLDEN = {
    ("M06", "maf2023"): (34, 40, 126), ("M06", "ccmr2026"): (49.95,), ("M07", "maf2023"): (55, 64, 200), ("M07", "ccmr2026"): (51.0,),
    ("M10", "wnf2026"): (13, 38), ("M11", "wnf2026"): (63, 189, 38, 114), ("M12", "wnf2026"): (158, 569), ("M13", "wnf2026"): (89, 267),
    ("M14", "wnf2026"): (38, 114), ("M15", "wnf2026"): (63, 189), ("M16", "wnf2026"): (89, 267), ("M17", "wnf2026"): (38, 114),
    ("M19", "wnf2026"): (63, 189), ("M19", "maf2023"): (22, 26, 126), ("M20", "mibl2024"): (51, 102, 204),
    ("M21", "maf2023"): (55, 64, 200), ("M21", "ccmr2026"): (116.35,), ("M22", "wnf2026"): (63, 189), ("M23", "maf2023"): (90, 100, 225),
    ("M24", "maf2023"): (22, 26, 126), ("M24", "ccmr2026"): (49.4,), ("M26", "wnf2026"): (89, 267), ("M27", "wnf2026"): (63, 189),
    ("M28", "wnf2026"): (63, 189), ("M29", "tinytapeout2026"): (70,), ("M29", "europractice2026"): (1080, 1126),
    ("M31", "lattispec2026"): (510,), ("M52", "e6cvd2026"): (865, 565, 2545, 1730),
}


def test_sourced_values_match_the_golden_table():
    got = {}
    for i, qs in A.SOURCED.items():
        for k, _, _, _, p, _ in qs:
            got.setdefault((i, k), ()); got[(i, k)] += tuple(p.values())
    assert got == GOLDEN
    assert [tuple(f[4].values()) for f in A.ACCESS_FEES] == [(127, 127, 6325), (2500,)]
    assert (A.WNF_OVERHEAD_PCT, A.WNF_NOTCH_USD, A.WNF_ABOVE_NOTCH_PCT, A.XH018_MIN_MM2) == (15.6, 5000, 33, 10)


@pytest.mark.parametrize("name", ["ATLAS.md"])
def test_atlas_page_is_current(name):
    assert (ROOT / "docs" / "build" / name).read_text(encoding="utf-8") == A.to_markdown(), "run: adamas build docs"
