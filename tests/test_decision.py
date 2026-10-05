import pytest

pytest.importorskip("stim")
from adamas import decision as D  # noqa: E402
from adamas import resource as R  # noqa: E402


def test_sobol_indices_are_sane_and_match_the_physics():
    p = {r["name"]: r for r in D.sobol("power")}
    assert p["Diamond permittivity"]["ST"] < D.RESOLUTION                          # cancels exactly in the loss ratio
    assert abs(p["Diamond hole mobility"]["S1"] - p["Diamond critical field"]["S1"]) < 0.06   # mu*Ec^2 over similar log ranges
    assert 0.9 < sum(r["S1"] for r in p.values()) < 1.1                           # nearly additive model
    q = D.sobol("quantum")
    assert q[0]["name"] == "Readout time" and q[0]["S1"] > 0.9


def test_roadmap_ranks_by_value_per_dollar_and_maps_every_input():
    rm = D.roadmap()
    assert {r["name"] for r in rm} == set(D.MEASURE)
    vals = [r["S1_per_10k"] for r in rm]
    assert vals == sorted(vals, reverse=True)
    assert rm[0]["name"] == "Diamond hole mobility" and rm[0]["experiment"] == "B3"


def test_xzzx_dominates_so_bias_information_has_no_decision_value():
    for metric in (0, 1):
        d = D.code_decision(metric=metric)
        assert d["xzzx_dominates"] and d["choice"] == "xzzx" and abs(d["evpi"]) < 1e-9
    # a contrived prior cannot change a dominated choice
    assert D.code_decision(prior={0.5: 0.98, 10.0: 0.01, 100.0: 0.01})["choice"] == "xzzx"
    lams = [r["Lambda"] for r in R.table_eta("css", 0.5)["fits"]["1000"]]
    assert all(a >= b for a, b in zip(lams, lams[1:]))
