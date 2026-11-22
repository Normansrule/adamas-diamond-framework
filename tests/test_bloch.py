"""adamas.bloch: Bloch equations against the Lindblad master equation, gates as rotations, and |r|^2 + C^2 = 1."""
import json
import math
from pathlib import Path

import numpy as np
import pytest

from adamas import bloch as B

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("seed", range(6))
def test_bloch_equations_match_lindblad(seed):
    rng = np.random.default_rng(seed)
    r0 = rng.normal(size=3); r0 *= rng.uniform(0, 1) / np.linalg.norm(r0)
    t1 = rng.uniform(1, 20); p = dict(rabi_mhz=rng.uniform(0, 4), detuning_mhz=rng.uniform(-2, 2), phase=rng.uniform(-3, 3),
                                      t1_us=t1, t2_us=rng.uniform(0.2, 2 * t1), z_eq=rng.uniform(-1, 1))
    t = rng.uniform(0.1, 5)
    assert np.allclose(B.evolve(r0, t, **p), B.lindblad_evolve(r0, t, **p), atol=1e-10)


def test_pi_pulse_and_free_relaxation():
    assert np.allclose(B.evolve([0, 0, 1], 0.1, rabi_mhz=5.0), [0, 0, -1], atol=1e-12)      # 1 / (2 Omega)
    r = B.evolve([0, 0, -1], 1e7, t1_us=B.T1_ROOM_US, t2_us=B.T2_ROOM_US, z_eq=0.3)
    assert np.allclose(r, [0, 0, 0.3], atol=1e-9)
    with pytest.raises(ValueError):
        B.lindblad_evolve([1, 0, 0], 1.0, t1_us=1.0, t2_us=3.0)


def test_every_gate_is_a_rotation():
    rng = np.random.default_rng(1)
    for g, u in B.GATES.items():
        n, th = B.axis_angle(u)
        v = B.rotation(n, th)
        phase = np.trace(v.conj().T @ u) / 2
        assert abs(abs(phase) - 1) < 1e-12 and np.allclose(u, phase * v), g
        r = rng.normal(size=3); r /= np.linalg.norm(r)
        assert np.isclose(np.linalg.norm(B.apply_gate(r, u)), 1.0)
    assert B.axis_angle(B.GATES["T"])[1] == pytest.approx(math.pi / 4)
    for g in "XYZH":                                     # a pi turn about -n is the same gate: the sign is fixed
        n, _ = B.axis_angle(-B.GATES[g])
        assert next(x for x in n if abs(x) > 1e-9) > 0
        n2, _ = B.axis_angle(1j * B.GATES[g])
        assert np.allclose(n, n2)
    assert np.allclose(B.apply_gate([0, 0, 1], B.GATES["H"]), [1, 0, 0])


def test_entanglement_shrinks_the_arrow_for_random_pure_states():
    rng = np.random.default_rng(2)
    for _ in range(50):
        psi = rng.normal(size=4) + 1j * rng.normal(size=4); psi /= np.linalg.norm(psi)
        c = B.concurrence(psi)
        for q in (0, 1):
            r = B.reduced_bloch(psi, q)
            assert np.dot(r, r) + c * c == pytest.approx(1.0, abs=1e-12)
    bell = B.partly_entangled(math.pi / 4)
    assert np.allclose(B.reduced_bloch(bell), 0) and B.concurrence(bell) == pytest.approx(1.0)


def test_room_temperature_numbers():
    assert 1e-4 < B.thermal_z(300) < 1e-3                      # in the dark the arrow relaxes to (almost) the center
    assert B.thermal_z(4) > B.thermal_z(300)
    assert 0 < B.reset_z() < 1
    assert B.T2_ROOM_US <= 2 * B.T1_ROOM_US


def test_golden_and_document_are_current():
    g = json.loads((ROOT / "web" / "tests" / "bloch_golden.json").read_text(encoding="utf-8"))
    new = B.golden()
    for a, b in zip(g["evolve"], new["evolve"]):
        assert np.allclose(a["r"], b["r"], atol=1e-12)
    assert g["reset_z"] == pytest.approx(new["reset_z"], abs=1e-12)
    assert (ROOT / "docs" / "BLOCH.md").read_text(encoding="utf-8") == B.document()
