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
    n = {}
    for ins in c:
        if ins.name in X.TWO_QUBIT:
            n[ins.name] = n.get(ins.name, 0) + len(ins.targets_copy()) // 2
    assert n.get("CZ", 0) == n.get("CX", 0) and "XCX" not in n   # CZ-native: Z-type checks on CZ, X-type on CNOT
    old = {ins.name for ins in X.native_circuit(5, 3, code, basis, cz_native=False)}
    assert ({"CZ", "XCX"} <= old) == (code == "xzzx")            # the older circuit is still available


def test_residual_cnot_bias_costs_performance():
    capped = X.worse_basis(5, 0.012, 100, "xzzx", shots=20000, seed=3)
    ideal = X.worse_basis(5, 0.012, 100, "xzzx", shots=20000, seed=3, eta_cnot=None)
    assert capped > 1.5 * ideal                       # bias-preserving CNOTs (impossible for two-level qubits) would help


def test_idle_dephasing_is_applied_once_per_round():
    c = X.noisy(X.native_circuit(3, 4, "xzzx"), 1e-3, 100, 1e-3, 0.0, 1e-3)
    data = X._data_qubits(c)
    assert sum(1 for i in c if i.name == "Z_ERROR" and {t.value for t in i.targets_copy()} == data) == 4


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
    up = [x for x in S["thr_upper"]["xzzx"] if x == x]
    assert S["eta_cnot"] == X.ETA_CNOT and all(u >= v * 0.95 for u, v in zip(S["thr_upper"]["xzzx"][:len(up)], xz))


def test_biased_resource_tables_order_the_codes():
    from adamas import resource as R
    n, st = R.WORKLOADS[R.RSA_JOB]
    std, cssb, xz = (R.estimate(n, st, 1000, 1000, model=m) for m in ("standard", "css_biased", "xzzx_biased"))
    assert cssb.physical_qubits > 3 * xz.physical_qubits          # biased noise hurts the standard code badly
    assert xz.distance <= std.distance + 2                          # XZZX recovers the depolarizing baseline
    for m in ("css_biased", "xzzx_biased"):
        lams = [r["Lambda"] for r in R.table_for(m)["fits"]["1000"]]
        assert all(a >= b for a, b in zip(lams, lams[1:]))          # slower readout never helps
