"""Entanglement Lab (adamas.entangle): no-signaling, teleportation, CHSH, and the generated document."""
import json
import math
from pathlib import Path

import numpy as np
import pytest

from adamas import entangle as E

ROOT = Path(__file__).resolve().parents[1]


def test_bob_cannot_see_anything_alice_does():
    r = E.no_signaling_check(trials=100, seed=11)
    assert r["max_change"] < 1e-12                       # the theorem: exactly 0 up to round-off [ghirardi1980]
    assert r["max_conditional_change"] > 0.1             # yet the correlations are real once Alice's results are known


def test_signaling_game_is_a_coin_flip():
    g = E.signaling_game(rounds=20_000, seed=5)
    assert g["p_bob0_given_bit"][0] == pytest.approx(0.5, abs=1e-12)
    assert g["p_bob0_given_bit"][1] == pytest.approx(0.5, abs=1e-12)
    assert abs(g["correct"] - 0.5) < 4 * g["se"]


def test_bob_marginal_is_independent_of_alice_setting_for_any_state():
    rng = np.random.default_rng(3)
    for _ in range(20):
        rho = E.random_state(rng); b = rng.uniform(-math.pi, math.pi)
        marg = [E.joint_probabilities(rho, a, b).sum(axis=0) for a in (0.0, 0.7, math.pi / 2, 2.5)]
        for m in marg[1:]:
            assert np.allclose(m, marg[0], atol=1e-12)


def test_teleportation_needs_the_two_bits():
    t = E.teleport_check(trials=50, seed=4)
    assert t["min_with_bits"] == pytest.approx(1.0, abs=1e-12)
    assert t["max_without_bits"] == pytest.approx(0.5, abs=1e-12) and t["min_without_bits"] == pytest.approx(0.5, abs=1e-12)
    assert t["bob_without_bits_vs_mixed"] < 1e-12


def test_teleport_outcomes_are_equally_likely_and_noisy_pair_gives_one_plus_v_over_two():
    psi = E.random_qubit(np.random.default_rng(9))
    assert [p for p, _ in E.teleport(psi)] == pytest.approx([0.25] * 4, abs=1e-12)
    for v in (0.0, 0.3, 0.8, 1.0):
        assert E.teleport_fidelity(psi, True, E.werner(v)) == pytest.approx((1 + v) / 2, rel=1e-9)
        assert E.teleport_fidelity(psi, False, E.werner(v)) == pytest.approx(0.5, rel=1e-9)


def test_measure_and_prepare_reaches_two_thirds():
    m = E.measure_and_prepare_fidelity(trials=20_000, seed=2)
    assert abs(m["mean"] - 2 / 3) < 4 * m["se"]


def test_chsh_bounds_and_werner_threshold():
    assert E.chsh(E.dm(E.bell("phi+"))) == pytest.approx(E.TSIRELSON, rel=1e-9)        # [cirelson1980]
    assert E.TSIRELSON == pytest.approx(2 * math.sqrt(2), rel=1e-12)
    assert E.werner_threshold() == pytest.approx(1 / math.sqrt(2), rel=1e-12)
    for v in (0.2, 0.6, 0.9):
        assert E.chsh(E.werner(v)) == pytest.approx(2 * math.sqrt(2) * v, rel=1e-9)
    assert E.chsh(E.werner(0.70)) < E.LOCAL_BOUND < E.chsh(E.werner(0.72))
    # a product (unentangled) state never violates: random local angles
    rng = np.random.default_rng(1)
    prod = np.kron(E.dm(E.random_qubit(rng)), E.dm(E.random_qubit(rng)))
    for _ in range(50):
        assert abs(E.chsh(prod, *rng.uniform(-math.pi, math.pi, 4))) <= 2 + 1e-12


def test_werner_joint_probabilities_closed_form():
    for v, a, b in ((0.8, 0.3, 1.0), (1.0, 0.0, math.pi / 4), (0.4, -1.1, 2.0)):
        P = E.joint_probabilities(E.werner(v), a, b); c = v * math.cos(a - b)
        assert P == pytest.approx(np.array([[1 + c, 1 - c], [1 - c, 1 + c]]) / 4, rel=1e-9, abs=1e-15)


def test_light_time_and_pre_shared_reach():
    assert E.light_time_s(299_792_458.0) == pytest.approx(1.0, rel=1e-12)
    assert E.pre_shared_reach_km(1.0) == pytest.approx(299_792.458, rel=1e-12)


def test_timeline_labels_and_sources():
    labels = {lab for *_, lab in E.TIMELINE}
    assert labels <= {"theorem", "proposed then", "demonstrated, cryogenic", "proposed"}
    assert E.TIMELINE[-1][-1] == "proposed"                # room-temperature pre-shared memories: not demonstrated
    assert all(lab != "demonstrated" for *_, lab in E.TIMELINE)   # nothing room-temperature is claimed as shown


def test_generated_document_and_golden_are_current():
    assert (ROOT / "docs" / "ENTANGLEMENT.md").read_text(encoding="utf-8") == E.document(), "run: adamas build docs"
    g = json.loads((ROOT / "web" / "tests" / "entangle_golden.json").read_text(encoding="utf-8"))
    assert g == json.loads(json.dumps(E.golden())), "run: adamas build docs"
