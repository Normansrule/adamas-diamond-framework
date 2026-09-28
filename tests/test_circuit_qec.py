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


def test_dephasing_is_invisible_to_z_memory_and_xzzx_balances_it():
    z = cq.biased_idle_error(5, 30000.0, "z", "dephase", shots=20000, seed=2)
    x = cq.biased_idle_error(5, 30000.0, "x", "dephase", shots=20000, seed=2)
    xz = max(cq.biased_idle_error(5, 30000.0, b, "xzzx_dephase", shots=20000, seed=2) for b in "zx")
    assert x > 5 * z                 # standard code: only the X memory suffers
    assert xz < x / 2                # XZZX: the worse basis is much better


def test_numpy_scalars_are_accepted():
    import numpy as np
    p = np.float64(0.006)            # numpy 2 reprs this as np.float64(0.006); the circuit must still build
    c = cq.circuit(3, 2, p, p, p, p)
    assert "DEPOLARIZE1(0.006)" in str(c)
