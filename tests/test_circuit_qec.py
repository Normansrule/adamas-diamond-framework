import pytest

from adamas import circuit_qec as cq

pytestmark = pytest.mark.skipif(cq.stim is None, reason="pip install stim pymatching")


def test_below_and_above_circuit_threshold():
    lo3, lo5 = (cq.logical_error(d, 0.003, 0.003, 0.003, 0.003, shots=20000, seed=d)[0] for d in (3, 5))
    hi3, hi5 = (cq.logical_error(d, 0.016, 0.016, 0.016, 0.016, shots=20000, seed=d)[0] for d in (3, 5))
    assert lo5 < lo3 and hi5 > hi3


def test_slow_readout_erodes_the_code():
    fast = cq.nv_logical_error(5, 100.0, shots=20000, seed=1)
    slow = cq.nv_logical_error(5, 30000.0, shots=20000, seed=1)
    assert slow > 5 * fast
    assert cq.p_idle(0.0, 1000.0) == 0.0 and abs(cq.p_idle(1e12, 1.0) - 0.75) < 1e-9
