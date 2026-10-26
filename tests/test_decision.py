import pytest

pytest.importorskip("stim")
from adamas import decision as D  # noqa: E402
from adamas import resource as R  # noqa: E402


def test_sobol_indices_are_sane_and_match_the_physics():
    p = {r["name"]: r for r in D.sobol("power")}
    assert p["Diamond permittivity"]["ST"] < D.RESOLUTION                          # enters only weakly, through the drift doping
    # with a weakly ionized drift f_ion ~ sqrt(K/N) and N ~ Ec^2, so the ratio goes as sqrt(mu * Ec): mobility dominates
    assert p["Diamond hole mobility"]["S1"] > 2.5 * p["Diamond critical field"]["S1"]
    assert 0.9 < sum(r["S1"] for r in p.values()) < 1.1                           # nearly additive model
    q = D.sobol("quantum")
    assert q[0]["name"] == "Readout time" and q[0]["S1"] > 0.9


def test_roadmap_ranks_by_value_per_dollar_and_maps_every_input():
    rm = D.roadmap()
    assert {r["name"] for r in rm} == set(D.MEASURE)
    vals = [r["S1_per_10k"] for r in rm]
    assert vals == sorted(vals, reverse=True)
    assert rm[0]["name"] == "Diamond hole mobility" and rm[0]["experiment"] == "B3"


def test_code_decision_with_residual_cnot_bias():
    for metric in (0, 1):
        d = D.code_decision(metric=metric)
        assert d["choice"] == "xzzx"
        P = d["payoff"]
        assert all(P[("xzzx", e)][metric] < P[("css", e)][metric] for e in (10.0, 100.0))     # XZZX wins once gates are biased
        assert P[("xzzx", 0.5)][metric] < 1.1 * P[("css", 0.5)][metric]                     # and ties (within 10 %) without bias
        assert 0 <= d["evpi"] < 0.1 * d["expected"]["xzzx"]                                # so the bias is worth little for the choice
    lams = [r["Lambda"] for r in R.table_eta("css", 0.5)["fits"]["1000"]]
    assert all(a >= b for a, b in zip(lams, lams[1:]))
