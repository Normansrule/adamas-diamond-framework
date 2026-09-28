from pathlib import Path

from adamas import traveler as T

ROOT = Path(__file__).resolve().parents[1]


def test_every_step_is_complete():
    assert len(T.STEPS) == 19 and len({s["id"] for s in T.STEPS}) == 19
    for s in T.STEPS:
        for key in ("why", "equipment", "params", "checks", "safety", "failures", "silicon", "short"):
            assert s[key], (s["id"], key)
        for name, unit, lo, hi, src in s["checks"]:
            assert lo is None or hi is None or lo < hi, (s["id"], name)


def test_thermal_budget_is_respected():
    assert T.thermal_violations() == []
    assert T.step_index("S07") < T.step_index("S09")          # NV anneal before gold
    assert T.step_index("S12") < T.step_index("S13")          # NO2 is capped immediately by ALD


def test_variants_and_geometry_reference_real_steps():
    for v in T.VARIANTS.values():
        assert set(v["skip"]) <= set(T.ORDER)
    for sh in T.XS:
        assert sh[6] in T.ORDER and (sh[7] is None or sh[7] in T.ORDER)
    # gold exists after S09 and is patterned into source and drain after S11
    k = T.step_index("S11")
    assert {sh[0] for sh in T.XS if T.visible(sh, k)} >= {"AuS", "AuD", "CHdev", "COr", "NV"}


def test_markdown_traveler_is_up_to_date():
    assert (ROOT / "docs" / "process" / "TRAVELER.md").read_text(encoding="utf-8") == T.to_markdown(), "run: make traveler"
