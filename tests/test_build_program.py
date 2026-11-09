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
    for name, text in (("README.md", B._index_md()), (B.DOCS["P0"], B._p0_md()), (B.DOCS["P1"], B._p1_md()), (B.DOCS["P2"], B._p2_md()), (B.DOCS["P3"], B._p3_md()), (B.DOCS["P4"], B._p4_md()), (B.DOCS["P5"], B._p5_md())):
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


def test_no_separable_state_beats_one_half():
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
