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
    for name, text in (("README.md", B._index_md()), (B.DOCS["P0"], B._p0_md()), (B.DOCS["P1"], B._p1_md()), (B.DOCS["P2"], B._p2_md()), (B.DOCS["P3"], B._p3_md()), (B.DOCS["P4"], B._p4_md()), (B.DOCS["P5"], B._p5_md()), (B.DOCS["P6"], B._p6_md()), (B.DOCS["P7"], B._p7_md()), (B.DOCS["P8"], B._p8_md())):
        assert (ROOT / "docs" / "build" / name).read_text(encoding="utf-8") == text, "run: adamas build docs"


def test_p3_gate_passes_and_every_degraded_twin_fails():
    g, b = B.p3_gate(), B.p3_degraded()
    assert g["verdict"] == "go" and not any(v["pass"] for v in b.values())
    assert g["hyperfine"]["lines"] == 3 and b["hyperfine"]["lines"] < 3       # power broadening hides the triplet
    assert g["hyperfine"]["max_fwhm_mhz"] < g["hyperfine"]["spacing_mhz"]
    assert b["nuclear_rabi"]["transfer"] == pytest.approx(0.5, abs=3 * b["nuclear_rabi"]["transfer_err"])


def test_p3_g2_zero_model_and_coverage():
    assert B.g2_zero_expected(1, 1.0) == 0.0 and B.g2_zero_expected(2, 1.0) == 0.5        # ideal one and two emitters
    assert B.g2_zero_expected(1) == pytest.approx(1 - B.P3_RHO2, rel=1e-9)
    assert 0.5 < B.g2_zero_expected(2) < 1 - B.P3_RHO2 / 2                     # a second NV adds light, not background
    assert B.P3_TEST_COVERAGE ** B.P3_TESTS == pytest.approx(B.P3_GATE_COVERAGE, rel=1e-9)


def test_p3_pass_rates_meet_the_design():
    r = B.p3_pass_rates(200)
    assert r["gate"] >= 0.95 - 3 * (0.95 * 0.05 / 200) ** 0.5, r            # at least 95 % within three binomial standard errors
    assert all(v <= 0.03 for v in r["degraded"].values()), r                  # a faulty setup rarely passes


def test_p3_json_has_no_nan():
    import json
    json.dumps(B.to_json()["p3"], allow_nan=False)


def test_p3_tests_draw_independent_noise():
    import numpy as np
    a, b, c = (B._rng(7, i).normal(size=5) for i in range(3))
    assert not (np.allclose(a, b) or np.allclose(b, c))


def test_p4_gate_passes_and_every_degraded_twin_fails():
    g, b = B.p4_gate(), B.p4_degraded()
    assert g["verdict"] == "go"
    assert not (b["tlm"]["pass"] or b["matching"]["pass"] or (b["extraction"]["mu_pass"] and b["extraction"]["vt_pass"]))
    e = b["extraction"]
    assert e["mu"] == pytest.approx(150 * 30 / B.P4_TOX_BAD_NM, abs=3 * e["mu_err"])      # the oxide ratio, as the doc says


def test_p4_extraction_is_exact_on_noise_free_model_data():
    from adamas.logic import Fet
    from scipy.optimize import brentq
    import numpy as np
    fet = Fet(w_um=B.P4_FET_W_UM, l_um=B.P4_FET_L_UM); r1 = B.P4_RC_OHM_MM / (fet.w_um * 1e-3); vgs = np.linspace(2, 8, 25)
    i = np.array([brentq(lambda x: fet.current(v - x * r1, B.P4_VDS_V - 2 * x * r1) - x, 0, B.P4_VDS_V / (2 * r1)) for v in vgs])
    mu, vt = B._extract(vgs, i, B.P4_RC_OHM_MM)[:2]
    assert mu == pytest.approx(fet.mu_cm2_vs, rel=1e-9) and vt == pytest.approx(fet.vth, rel=1e-9)


def test_p4_tlm_model_is_the_textbook_line():
    r0, r1 = B.tlm_resistance_ohm(0.0), B.tlm_resistance_ohm(10.0)
    assert r0 == pytest.approx(2 * B.P4_RC_OHM_MM / (B.P4_TLM_W_UM * 1e-3), rel=1e-9)
    assert (r1 - r0) == pytest.approx(B.P4_RSH_KOHM * 1e3 * 10.0 / B.P4_TLM_W_UM, rel=1e-9)


def test_p4_pass_rates_meet_the_design():
    r = B.p4_pass_rates(300)
    assert r["gate"] >= 0.95 - 3 * (0.95 * 0.05 / 300) ** 0.5, r
    assert all(v <= 0.03 for v in r["degraded"].values()), r


def test_p5_gate_passes_and_every_degraded_twin_fails():
    g, b = B.p5_gate(), B.p5_degraded()
    assert g["verdict"] == "go"
    # the Bell twin sits at F = 1/2, so about 2 % of seeds would pass it; the default seed is one that fails (rates: test below)
    assert not (b["yield"]["pass"] or b["pairs"]["pass"] or b["bell"]["pass"])
    assert b["pairs"]["found"] < b["pairs"]["predicted"]              # wide apertures: pairs too far apart to couple


def test_p5_parity_estimator_is_the_exact_bell_fidelity():
    import numpy as np
    from adamas import entangle as E
    rng = np.random.default_rng(3); phi = np.linspace(0, np.pi, B.P5_PARITY_PHASES, endpoint=False)
    for _ in range(20):
        rho = E.random_state(rng)
        f, _ = B.bell_fidelity_estimate(float((rho[0, 0] + rho[3, 3]).real), phi, [B.parity_after_analysis(rho, x) for x in phi])
        assert f == pytest.approx(float((E.bell("phi+").conj() @ rho @ E.bell("phi+")).real), abs=1e-12)
    # the simulated Werner data follow the same model: parity -A cos 2phi with A = v
    pop, a = B.bell_tomography_expected(0.67); v = (4 * 0.67 - 1) / 3
    for x in phi[:4]:
        assert B.parity_after_analysis(E.werner(v), x) == pytest.approx(-a * np.cos(2 * x), abs=1e-12)
    assert pop == pytest.approx(float((E.werner(v)[0, 0] + E.werner(v)[3, 3]).real), rel=1e-12)


def test_p5_no_separable_state_beats_one_half():
    """The Bell check's threshold: product states (and so their mixtures) never exceed fidelity 1/2 with |Phi+>."""
    import numpy as np
    from adamas import entangle as E
    rng = np.random.default_rng(4); best = 0.0
    for _ in range(4000):
        v = np.kron(E.random_qubit(rng), E.random_qubit(rng)); best = max(best, abs(np.vdot(E.bell("phi+"), v)) ** 2)
    assert best <= 0.5 + 1e-12 and best > 0.49


def test_p5_pair_count_follows_the_binomial_model():
    assert B._p_two(0.01, 50) == pytest.approx(1225 * 1e-4 * 0.99 ** 48, rel=1e-12)
    assert 0.3 < B.p5_window_fraction() < 0.9
    assert B.p5_window_fraction(B.P5_APERTURE_BAD_NM) < 0.2 * B.p5_window_fraction()


def test_p5_pass_rates_meet_the_design():
    r = B.p5_pass_rates(300)
    assert r["gate"] >= 0.95 - 3 * (0.95 * 0.05 / 300) ** 0.5, r
    assert all(v <= 0.05 for v in r["degraded"].values()), r


def test_p5_local_fluence_is_stated():
    assert B.p5_local_fluence_cm2() == pytest.approx(50 / (3.141592653589793 * (10e-7) ** 2), rel=1e-12)
    assert "cm⁻²" in B._p5_md() and "[dolde2014]" not in B._p5_md()



def test_p6_gate_passes_and_every_degraded_twin_fails():
    g, b = B.p6_gate(), B.p6_degraded()
    assert g["verdict"] == "go" and not any(v["pass"] for v in b.values())
    assert b["drive"]["rabi_mhz"] == pytest.approx(B.P6_RABI_BAD_MHZ, rel=0.05)     # the fit recovers the half-current Rabi


def test_p6_repetition_model():
    from adamas.qec import repetition_logical_error
    for p in (0.01, 0.1, 0.25):
        assert repetition_logical_error(p) == pytest.approx(3 * p ** 2 - 2 * p ** 3, rel=1e-12)
        assert B.repetition_fidelity(p, 1.0) == pytest.approx(1 - repetition_logical_error(p), rel=1e-12)
    for f0, pe in ((B.P6_F0, 0.0590), (B.P6_F0_BAD, 0.3110)):
        p = B.repetition_break_even(f0)
        assert p == pytest.approx(pe, abs=5e-4) and B.repetition_fidelity(p, f0) == pytest.approx(1 - p, abs=1e-9)
    assert B.P6_P_INJECT < B.repetition_break_even(B.P6_F0_BAD)                    # so the twin's correction cannot help


def test_p6_pass_rates_meet_the_design():
    r = B.p6_pass_rates(300)
    assert r["gate"] >= 0.95 - 3 * (0.95 * 0.05 / 300) ** 0.5, r
    assert all(v <= 0.05 for v in r["degraded"].values()), r
    a = 1 - B.P6_TEST_COVERAGE                          # k's promise: with the truth on the limit, at most a wrong passes
    assert all(v <= a + 3 * (a * (1 - a) / 300) ** 0.5 for v in r["at_limit"].values()), r["at_limit"]


def test_p6_limit_twin_sits_on_the_limit():
    assert B.repetition_fidelity(B.P6_P_INJECT, B.p6_f0_at_limit()) == pytest.approx(1 - B.P6_P_INJECT, rel=1e-12)



def test_p7_gate_passes_and_every_degraded_twin_fails():
    g, b = B.p7_gate(), B.p7_degraded()
    assert g["verdict"] == "go" and not any(v["pass"] for v in b.values())
    assert b["yield"]["ring_yield"] < b["yield"]["centre_yield"] - 0.2       # the twin's loss sits at the edge


def test_p7_murphy_is_the_expected_yield_of_the_simulation():
    """Triangular densities on [0, 2 D0] plus Poisson defects give Murphy's yield exactly; checked by quadrature."""
    import numpy as np
    from scipy.integrate import quad
    from adamas.wafer import murphy_yield
    for ad in (0.05, 0.18, 1.0, 3.0):
        y, _ = quad(lambda x: np.exp(-ad * x) * (x if x <= 1 else 2 - x), 0, 2)   # D = x D0, triangular density on [0, 2]
        assert y == pytest.approx(murphy_yield(100 * ad, 1.0), rel=1e-10)


def test_p7_control_limits_are_a_prediction_interval():
    import numpy as np
    from scipy.stats import t
    base = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    lim = B.p7_control_limits(base, n_monitor=10, coverage=0.9)        # the formula as documented; run coverage: test below
    a = 1 - 0.9 ** 0.1; half = t.ppf(1 - a / 2, 4) * base.std(ddof=1) * (1 + 1 / 5) ** 0.5
    assert (lim["lcl"], lim["ucl"]) == pytest.approx((3 - half, 3 + half), rel=1e-12)
    assert B.p7_die_sites().shape[0] == pytest.approx(B.p7_good_dies_table(1.0, (9.0,))[0]["gross"], rel=0.05)


def test_p7_sampler_reproduces_murphy():
    """The simulated product dies' mean yield over seeds is Murphy's yield at the true D0 (not just the formula)."""
    import numpy as np
    from adamas.wafer import murphy_yield
    ys = [B.p7_yield(9000 + i)["y_meas"] for i in range(40)]
    y = murphy_yield(B.P7_DIE_MM ** 2, B.P7_D0_CM2); n = 40 * B.p7_yield()["dies"]
    assert np.mean(ys) == pytest.approx(y, abs=4 * (y * (1 - y) / n) ** 0.5)


def test_p7_pass_rates_meet_the_design():
    r = B.p7_pass_rates(300); c = B.P7_TEST_COVERAGE; se = (c * (1 - c) / 300) ** 0.5
    assert r["gate"] >= 0.95 - 3 * (0.95 * 0.05 / 300) ** 0.5, r
    assert r["spc"] >= c - 3 * se and r["yield"] >= c - 3 * se, r              # each check's false-alarm rate
    assert all(v <= 0.05 for v in r["degraded"].values()), r



def test_p8_ledger_passes_and_every_inflated_claim_is_rejected():
    g, b = B.p8_gate(), B.p8_degraded()
    assert g["verdict"] == "go" and not any(v["pass"] for v in b.values())
    assert not b["hidden_loss"]["r1"] and not b["inflated_trl"]["r2"] and not b["unsupported_win"]["r1"]
    assert not b["point_value_win"]["r1"] and not b["wrong_way_citation"]["r1"]
    assert g["beats"] == ["hot"]                                   # the only win, and it is simulated
    assert g["measured_ratio_hot"] < 1                              # the demonstrated device still loses hot


def test_p8_power_comparison_flips_with_temperature():
    """Bulk-doped diamond loses to SiC at 300 K and wins at 523 K over the sourced ranges; the crossover is between."""
    cold, hot = B.p8_loss_ratio_percentiles(300.0), B.p8_loss_ratio_percentiles(523.0)
    assert cold["p90"] < 1 < hot["p10"]
    assert 300 < B.p8_crossover_k("p50") < B.p8_crossover_k("p10") < 523
    from adamas import uncertainty as U
    mc = U.monte_carlo("power", B.P8_SAMPLES)                    # the same samples as the uncertainty study
    assert (cold["p10"], cold["p90"]) == pytest.approx((mc["p10"], mc["p90"]), rel=1e-12)
    cool = B.p8_loss_ratio_percentiles(523.0, t_sic_k=373.0)          # SiC cooled: no longer decisive
    assert cool["p10"] < 1 < cool["p90"]


def test_p8_rules_cover_every_claim_type():
    a = {"id": "x", "computed": None, "cited": None, "claim": "undecided", "evidence": "proposed", "trl": 3, "problem": "p"}
    assert not B.p8_check(a)["r2"] and B.p8_check({**a, "trl": 2})["pass"]
    assert not B.p8_check({**a, "trl": 2, "problem": " "})["r3"]
    good = {"diamond": 2.0, "incumbent": 1.0, "higher_is_better": True, "key": "x2000"}
    assert B.p8_check({**a, "trl": 2, "claim": "beats", "cited": good})["r1"]
    assert not B.p8_check({**a, "trl": 2, "claim": "beats", "cited": "a measured comparison [x2000]"})["r1"]   # text is not numbers
    assert not B.p8_check({**a, "trl": 2, "claim": "beats", "cited": {**good, "higher_is_better": False}})["r1"]
    assert not B.p8_check({**B.P8_APPS[0], "trl": 4})["r2"]                 # a computed claim is capped at 3
    assert not B.p8_check({**B.P8_APPS[1], "claim": "undecided"})["r1"]          # hiding a decisive win also fails
