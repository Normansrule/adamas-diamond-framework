import math

import numpy as np

from adamas import coupling, nv, register


def test_zero_field_and_zeeman():
    lo, hi = nv.transition_frequencies_mhz([0, 0, 0])
    assert math.isclose(lo, 2870, abs_tol=1e-6) and math.isclose(hi, 2870, abs_tol=1e-6)
    lo, hi = nv.transition_frequencies_mhz([0, 0, 1.0])
    assert math.isclose(hi - lo, 2 * nv.GAMMA_MHZ_PER_MT, rel_tol=1e-6)


def test_temperature_shift():
    assert math.isclose(nv.zero_field_splitting_mhz(310) - nv.zero_field_splitting_mhz(300), -0.742, abs_tol=1e-9)


def test_odmr_has_dips():
    f = np.linspace(2800, 2940, 1401)
    s = nv.odmr_spectrum(f, np.array([0, 0, 1.0]), axes=nv.NV_AXES[:1], hyperfine=False)
    assert s.min() < 1.0 and s.max() <= 1.0


def test_rabi_pi_pulse():
    assert math.isclose(float(nv.rabi(0.1, 5.0)), 1.0, abs_tol=1e-9)


def test_dipolar_constant_and_scaling():
    assert 51.5 < coupling.DIPOLAR_MHZ_NM3 < 52.5
    assert math.isclose(coupling.dipolar_coupling_khz(10) / coupling.dipolar_coupling_khz(20), 8.0, rel_tol=1e-9)


def test_gate_fidelity_monotonic():
    r = np.array([5, 10, 20, 30, 50])
    fid = coupling.gate_fidelity_bound(r)
    assert np.all(np.diff(fid) < 0) and fid[0] > 0.999 and fid[-1] > 0.5


def test_pair_yield_limits():
    assert coupling.pair_yield(15, 2, 1.0, trials=4000) > 0.95
    assert coupling.pair_yield(15, 2, 0.01, trials=4000) < 0.01


def test_selective_pulse_sweet_spot():
    good = register.bell_fidelity(2.16)
    bad = register.bell_fidelity(2.16, 2.0)
    assert good > 0.999 and bad < 0.95
