"""Build program: the P0 gate from the validation matrix, the simulated P1 kit, and the generated phase documents."""
from pathlib import Path

import pytest

from adamas import build_program as B

ROOT = Path(__file__).resolve().parents[1]


def test_p0_gate_follows_the_validation_matrix():
    g = B.p0_gate()
    assert g["checks"] == g["pass"] + g["fail"] + g["known"]
    assert g["verdict"] == ("go" if g["fail"] == 0 else "stop")


def test_p1_simulated_kit_passes_and_recovers_the_inputs():
    th = B.p1_thermometer()
    assert th["slope_khz_k"] == pytest.approx(-74.2, abs=3 * th["slope_err_khz_k"])
    assert th["tolerance_khz_k"] == pytest.approx(2 * (th["slope_err_khz_k"] ** 2 + 0.7 ** 2) ** 0.5)
    assert B.p1_detection()["pass"] and B.p1_magnetometer()["pass"]


def test_p1_pass_rate_is_what_a_two_sigma_band_promises():
    assert 0.95 <= B.p1_pass_rate(400) <= 1.0          # two combined standard errors: at least the fit-only 95 %


def test_p1_bill_sums_the_part_lists():
    b = B.p1_bill()
    assert b["low"] == sum(r[3] for r in b["rows"]) and b["high"] == sum(r[4] for r in b["rows"]) and b["low"] < b["high"]


def test_phase_documents_are_current():
    for name, text in (("README.md", B._index_md()), ("P0_simulation.md", B._p0_md()), ("P1_proof_of_concept.md", B._p1_md())):
        assert (ROOT / "docs" / "build" / name).read_text(encoding="utf-8") == text, "run: adamas build docs"
