import pytest

stim = pytest.importorskip("stim")
pytest.importorskip("pymatching")
from adamas import xzzx_native as X  # noqa: E402


@pytest.mark.parametrize("code", ["css", "xzzx"])
@pytest.mark.parametrize("basis", ["z", "x"])
def test_native_circuits_are_deterministic_without_noise(code, basis):
    c = X.native_circuit(5, 3, code, basis)
    det, obs = c.compile_detector_sampler(seed=3).sample(200, separate_observables=True)
    assert not det.any() and not obs.any()
    if code == "xzzx":
        names = {ins.name for ins in c}
        assert {"CZ", "XCX"} <= names                     # natively different gates, not an emulation


def test_codes_agree_under_depolarizing_noise():
    a = X.worse_basis(3, 0.006, 0.5, "css", shots=40000, seed=5)
    b = X.worse_basis(3, 0.006, 0.5, "xzzx", shots=40000, seed=6)
    assert abs(a / b - 1) < 0.2                           # Clifford equivalence: same performance, within sampling error


def test_xzzx_wins_under_strong_bias():
    a = X.worse_basis(5, 0.006, 100, "css", shots=20000)
    b = X.worse_basis(5, 0.006, 100, "xzzx", shots=20000)
    assert a > 2.5 * b


def test_cached_study_shows_opposite_trends():
    S = X.cached_study()
    css, xz = S["thr"]["css"], S["thr"]["xzzx"]
    assert css[-2] < css[0] and xz[-2] > 1.4 * xz[0]
