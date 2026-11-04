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


def test_p2_fits_recover_what_was_put_in():
    g = B.p2_gate()
    assert g["verdict"] == "go" and g["pulsed"]["echo_gain"] > 10
    assert abs(g["arrhenius"]["method_bias_ev"]) < 0.01            # the T^-0.7 correction is good to 1 % of 0.37 eV


def test_p2_gate_passes_a_correct_setup_about_95_percent_of_the_time():
    r = B.p2_pass_rates(300)
    assert 0.95 - 3 * r["se_gate"] <= r["gate"] <= 1.0, r      # 95 % within three binomial standard errors (300 runs)
    assert all(r[k] >= 0.96 for k in ("rabi_pass", "t2star_pass", "t2_pass", "vector", "arrhenius")), r


def test_phase_documents_are_current():
    for name, text in (("README.md", B._index_md()), (B.DOCS["P0"], B._p0_md()), (B.DOCS["P1"], B._p1_md()), (B.DOCS["P2"], B._p2_md()), (B.DOCS["P3"], B._p3_md())):
        assert (ROOT / "docs" / "build" / name).read_text(encoding="utf-8") == text, "run: adamas build docs"


def test_p3_gate_passes_and_every_degraded_twin_fails():
    g, b = B.p3_gate(), B.p3_degraded()
    assert g["verdict"] == "go" and not any(v["pass"] for v in b.values())
    assert g["hyperfine"]["lines"] == 3 and b["hyperfine"]["lines"] < 3       # power broadening hides the triplet
    assert b["nuclear_rabi"]["transfer"] == pytest.approx(0.5, abs=3 * b["nuclear_rabi"]["transfer_err"])


def test_p3_g2_zero_model_and_coverage():
    assert B.g2_zero_expected(1, 1.0) == 0.0 and B.g2_zero_expected(2, 1.0) == 0.5        # ideal one and two emitters
    assert B.P3_TEST_COVERAGE ** B.P3_TESTS == pytest.approx(B.P3_GATE_COVERAGE, rel=1e-9)


def test_p3_pass_rates_meet_the_design():
    r = B.p3_pass_rates(200)
    assert r["gate"] >= 0.95 - 3 * (0.95 * 0.05 / 200) ** 0.5, r            # at least 95 % within three binomial standard errors
    assert all(v <= 0.03 for v in r["degraded"].values()), r                  # a faulty setup rarely passes


def test_p3_json_has_no_nan():
    import json
    json.dumps(B.to_json()["p3"], allow_nan=False)
