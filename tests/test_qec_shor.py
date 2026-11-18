"""Phase-flip and nine-qubit codes (v0.50.0): the closed-form failure probabilities agree with exhaustive decoding."""
import pytest

from adamas import qec


@pytest.mark.parametrize("px,pz", [(0.0, 0.0), (1e-3, 2e-3), (0.01, 0.01), (0.05, 0.02), (0.2, 0.1), (0.3, 0.4), (0.5, 0.5)])
def test_nine_qubit_formula_matches_exhaustive_decoding(px, pz):
    a, b = qec.shor9_logical_error(px, pz), qec.shor9_exhaustive(px, pz)
    assert all(a[k] == pytest.approx(b[k], abs=1e-12) for k in ("bit", "phase", "total"))


def test_check_matrices_encode_one_qubit_and_correct_every_single_flip():
    def rank(vs):
        basis = []
        for v in vs:
            for b in basis:
                v = min(v, v ^ b)
            if v:
                basis.append(v)
        return len(basis)
    assert all(bin(z & x).count("1") % 2 == 0 for z in qec._ZCHECKS for x in qec._XCHECKS)   # Z and X checks commute
    assert rank(qec._ZCHECKS) == 6 and rank(qec._XCHECKS) == 2                              # 9 - 6 - 2 = 1 encoded qubit
    assert len(qec._span(qec._XCHECKS)) == 4 and len(qec._span(qec._ZCHECKS)) == 64
    for p in (1e-4, 1e-6):                                      # no first-order term: every single flip is corrected
        f = qec.shor9_exhaustive(p, p)
        assert f["bit"] / p < 1e-2 and f["phase"] / p < 1e-2
    assert qec.shor9_logical_error(0.5, 0.5)["total"] == pytest.approx(0.75)   # pure noise: same as an unencoded qubit


def test_three_qubit_code_under_both_error_types_by_enumeration():
    for p in (0.01, 0.1, 0.3, 0.5):
        prob = lambda e: p ** bin(e).count("1") * (1 - p) ** (3 - bin(e).count("1"))      # noqa: E731
        bit = sum(prob(e) for e in range(8) if bin(e).count("1") >= 2)                       # majority vote fails
        phase = sum(prob(e) for e in range(8) if bin(e).count("1") % 2 == 1)                 # odd number of Z: logical Z
        assert qec.repetition_both(p) == pytest.approx(1 - (1 - bit) * (1 - phase), abs=1e-12)
        assert qec.phase_flip_logical_error(p) == pytest.approx(bit, abs=1e-12)              # same count in the Hadamard basis
    assert qec.repetition_both(0.5) == pytest.approx(0.75)
    assert all(qec.repetition_both(p) > 1 - (1 - p) ** 2 for p in (0.001, 0.01, 0.1, 0.3, 0.49))


def test_break_even_of_the_nine_qubit_code():
    b = qec.shor9_break_even()
    assert 0.07 < b < 0.09
    unenc = lambda p: 1 - (1 - p) ** 2                          # noqa: E731
    assert qec.shor9_logical_error(b * 0.9, b * 0.9)["total"] < unenc(b * 0.9)
    assert qec.shor9_logical_error(b * 1.1, b * 1.1)["total"] > unenc(b * 1.1)
    assert qec.shor9_logical_error(b, b)["total"] == pytest.approx(unenc(b), abs=1e-9)
