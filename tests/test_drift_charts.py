"""Small drifts in the pilot line (v0.52.0): CUSUM [page1954] and EWMA [roberts1959] against Shewhart at equal false-alarm rate."""
import numpy as np
import pytest

from adamas import build_program as B


def test_charts_share_the_false_alarm_rate_of_the_gate():
    x = B.p7_drift_charts.__wrapped__(0.0)                      # stable lines, fresh draws from the detection stream
    for c in ("shewhart", "cusum", "ewma"):
        assert x[c]["alarm_rate"] == pytest.approx(1 - B.P7_TEST_COVERAGE, abs=0.012)


def test_cusum_and_ewma_beat_shewhart_on_a_small_drift_and_all_catch_a_large_one():
    d = B.p7_drift_charts()
    assert d["cusum"]["detected_after_shift"] > 2.5 * d["shewhart"]["detected_after_shift"]
    assert d["ewma"]["detected_after_shift"] > 2.5 * d["shewhart"]["detected_after_shift"]
    assert max(d[c]["detected_after_shift"] for c in ("gate", "shewhart", "cusum", "ewma")) < 0.5      # "most still go unseen"
    assert d["gate"]["threshold"] > d["shewhart"]["threshold"] and d["gate"]["caught"] <= d["shewhart"]["caught"]
    big = B.p7_drift_charts.__wrapped__(4.0)
    assert all(big[c]["detected_after_shift"] > 0.95 for c in ("shewhart", "cusum", "ewma"))


def test_chart_statistics_by_hand():
    z = np.array([[0.0, 1.0, 1.0, -2.0]])
    s = B._p7_chart_stats(z, m=20)
    assert s["cusum"][0].tolist() == pytest.approx([0.0, 0.5, 1.0, 1.5])     # C+ 0, .5, 1, 0; C- 0, 0, 0, 1.5
    lam = B.P7_EWMA_LAMBDA
    assert s["ewma"][0, 0] == 0.0
    assert s["ewma"][0, 1] == pytest.approx(lam / np.sqrt(lam / (2 - lam) * (1 - (1 - lam) ** 4)))
    assert s["shewhart"][0, 3] == pytest.approx(2 / np.sqrt(1 + 1 / 20))
    down = B._p7_chart_stats(np.array([[-1.0, -1.0]]), m=20)["cusum"][0].tolist()
    assert down == pytest.approx([0.5, 1.0])                                    # the lower side C- alone
