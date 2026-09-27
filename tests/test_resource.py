import shutil

import pytest

from adamas import resource as R


def test_estimates_behave_physically():
    t = R.table()
    n, st = R.WORKLOADS["RSA-2048 scale (6,000 logical, 3×10⁹ steps)"]
    fast, slow = R.estimate(n, st, 100.0, 1000.0, t=t), R.estimate(n, st, 3000.0, 1000.0, t=t)
    assert fast.distance <= slow.distance and fast.runtime_hours < slow.runtime_hours
    assert R.estimate(n, st, 1000.0, 100.0, t=t).distance > R.estimate(n, st, 1000.0, 1000.0, t=t).distance   # shorter memory, larger code
    assert R.estimate(n, st, 10000.0, 100.0, t=t) is None                                                        # at threshold: no code helps
    lams = [r["Lambda"] for r in t["fits"]["1000"]]
    assert all(b <= a for a, b in zip(lams, lams[1:]))


def test_fit_recovers_known_lambda():
    A, lam = R.fit_lambda([3, 5, 7], [0.02 * 4.0 ** (-(d + 1) / 2) for d in (3, 5, 7)])
    assert abs(lam - 4.0) < 1e-9 and abs(A - 0.02) < 1e-12


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg missing")
def test_trailer_renders(tmp_path):
    from adamas import trailer
    p = trailer.render(tmp_path / "t.mp4", fast=True)
    assert p.stat().st_size > 10000
