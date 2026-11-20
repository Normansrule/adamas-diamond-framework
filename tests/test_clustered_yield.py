"""Clustered killer defects (v0.51.0): Stapper's negative-binomial yield, the fit of its cluster parameter, and P7's check."""
import math

import numpy as np
import pytest

from adamas import build_program as B
from adamas import wafer


def test_negative_binomial_yield_limits():
    assert wafer.negative_binomial_yield(9, 2, math.inf) == pytest.approx(wafer.poisson_yield(9, 2))
    assert wafer.negative_binomial_yield(9, 2, 1e9) == pytest.approx(wafer.poisson_yield(9, 2), rel=1e-6)
    assert wafer.negative_binomial_yield(100, 2, 0.5) == pytest.approx(5 ** -0.5)      # (1 + 2 / 0.5)^(-0.5)
    assert wafer.negative_binomial_yield(0, 2, 0.5) == 1.0
    ys = [wafer.negative_binomial_yield(100, 2, a) for a in (0.3, 1, 3, 10)]          # stronger clustering, higher yield
    assert ys == sorted(ys, reverse=True)


def test_cluster_parameter_is_recovered_from_counts():
    r = np.random.default_rng(1)
    for alpha in (0.5, 2.0):
        c = r.poisson(r.gamma(alpha, 1.5 / alpha, 200_000))
        assert wafer.fit_cluster_alpha(c) == pytest.approx(alpha, rel=0.05)
    a = wafer.fit_cluster_alpha(r.poisson(1.5, 200_000))
    assert a > 50                                                  # Poisson counts: no clustering (inf, or a very large alpha)
    assert math.isinf(wafer.fit_cluster_alpha([1, 1, 1, 1])) and math.isinf(wafer.fit_cluster_alpha([3]))
    with pytest.raises(ValueError):
        wafer.negative_binomial_yield(9, 2, 0)


def test_p7_clustered_line_is_explained_by_the_negative_binomial_model_only():
    x = B.p7_clustered()
    assert x["y_true"] == pytest.approx(5 ** -0.5) and set(x["models"]) == {"poisson", "murphy", "nb"}
    rates = B.p7_clustered_rates()
    assert rates["nb"] >= 0.93 and rates["poisson"] <= 0.1 and rates["murphy"] <= 0.1
    assert rates["alpha_median"] == pytest.approx(B.P7_ALPHA, rel=0.2)
