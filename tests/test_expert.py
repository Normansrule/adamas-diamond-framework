import math
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from adamas import analog, coupling, digital, litho, opensys, qec

ROOT = Path(__file__).resolve().parents[1]


def test_rayleigh_matches_vendor_resolution():
    assert abs(litho.half_pitch_nm(13.5, 0.33) - 13) < 0.5      # [asmleuv2026]
    assert abs(litho.half_pitch_nm(13.5, 0.55) - 8) < 0.5
    assert litho.depth_of_focus_nm(13.5, 0.55) < litho.depth_of_focus_nm(13.5, 0.33)


def test_euv_photon_statistics():
    assert math.isclose(litho.photon_energy_ev(13.5), 91.84, abs_tol=0.05)
    ratio = litho.photons_per_nm2(30, 193) / litho.photons_per_nm2(30, 13.5)
    assert math.isclose(ratio, 193 / 13.5, rel_tol=1e-9)
    assert 0.02 < litho.mirror_throughput() < 0.04


def test_electron_range_shorter_in_diamond():
    si = litho.kanaya_okayama_range_um(30, *litho.SUBSTRATES["Silicon"])
    c = litho.kanaya_okayama_range_um(30, *litho.SUBSTRATES["Diamond"])
    assert c < si and 4 < c < 7


def test_gate_model_is_static_power_dominated():
    g = digital.EDGate()
    est = digital.processor_estimate(770, g)
    assert g.strength_ratio > 8
    assert est["static_fraction"] > 0.9
    faster = digital.processor_estimate(770, g.scaled(1.0))
    assert faster["f_clk_hz"] > 3 * est["f_clk_hz"]
    assert math.isclose(faster["power_w"] * faster["static_fraction"], est["power_w"] * est["static_fraction"], rel_tol=1e-9)


def test_analog_relations():
    f = digital.EDGate().driver
    i = 1e-4
    assert math.isclose(analog.gm_over_id(f, i), 2 / analog.overdrive_v(f, i), rel_tol=1e-9)
    assert math.isclose(analog.sigma_vt_mv(5, 4, 1) * 2, analog.sigma_vt_mv(5, 1, 1), rel_tol=1e-9)
    assert 3.5 < analog.tia_noise_fa_rthz(1e9) < 4.5
    assert analog.ed_reference_v() == 3.5


def test_surface_code_arithmetic():
    assert qec.surface_code_qubits(3) == 17
    assert qec.distance_for_target(2e-2, 1e-9) is None
    out = qec.nv_cells_needed(1, 1e-3, 1e-9)
    assert out["distance"] == 17 and out["physical_qubits"] == 577
    assert math.isclose(qec.repetition_logical_error(0.01), 2.98e-4, rel_tol=1e-9)


def test_lindblad_below_simple_bound_and_trace_preserving():
    for r in (10, 25):
        assert opensys.cz_gate_fidelity(r) < coupling.gate_fidelity_bound(r)
    assert opensys.cz_gate_fidelity(10, t2_ms=1e6, t1_ms=1e7) > 0.9999


def test_c13_bath_natural_abundance():
    t = np.median(opensys.t2star_us_c13(0.011, samples=60))
    assert 1.0 < t < 8.0                                        # microseconds; [childress2006], [mizuochi2009]
    assert 19 < opensys.E_13C_KHZ_NM3 < 21


def test_decoupling_reproduces_delange():
    echo = opensys.t2_under_cpmg_us(1, grid=600)
    assert 2.3 < echo < 3.5                                     # measured 2.8 microseconds [delange2010]
    assert opensys.t2_under_cpmg_us(8, grid=600) > 3 * echo


@pytest.mark.skipif(shutil.which("iverilog") is None, reason="Icarus Verilog not installed")
def test_dia4_simulates(tmp_path):
    d = ROOT / "circuits" / "digital"
    exe = tmp_path / "dia4"
    for tb in ("dia4_tb.v", "dia4_call_tb.v"):                  # countdown program, then nested CALL/RET
        subprocess.run(["iverilog", "-o", str(exe), str(d / "dia4.v"), str(d / tb)], check=True)
        out = subprocess.run(["vvp", str(exe)], capture_output=True, text=True, check=True).stdout
        assert "PASS" in out, tb


@pytest.mark.skipif(shutil.which("ngspice") is None, reason="ngspice not installed")
def test_ring_oscillator_runs():
    out = subprocess.run(["ngspice", "-b", "ring_oscillator.cir"], cwd=ROOT / "circuits" / "spice",
                         capture_output=True, text=True).stdout
    period = [l for l in out.splitlines() if l.startswith("period")]
    assert period and 5e-9 < float(period[0].split("=")[1].split()[0]) < 1e-7


def test_gate_budget_limits_and_closed_form():
    from adamas.gate_budget import GateBudget, required_t2_us
    perfect = GateBudget(10.0, t2star_us=1e9, t2_us=1e9)
    assert math.isclose(perfect.fidelity, 1.0, abs_tol=1e-12)
    assert math.isclose(GateBudget(25.0, echo=False, t2star_us=1.0).fidelity, 0.25, abs_tol=1e-6)      # fully dephased
    assert math.isclose(GateBudget(25.0, q_prep=0.0).fidelity, 0.25, abs_tol=1e-12)                      # never prepared
    g = GateBudget(25.0)
    assert math.isclose(g.fidelity, (1 + g.w) ** 2 / 4, rel_tol=1e-12)
    assert GateBudget(25.0, double_quantum=True).t_gate_us == g.t_gate_us / 4
    assert GateBudget(25.0, double_quantum=True).fidelity > g.fidelity
    assert required_t2_us(25, 0.99) > required_t2_us(10, 0.99)
    parts = GateBudget(25.0, q_prep=0.85, pulse_error=0.01).breakdown()
    assert math.isclose(1 - parts["total_fidelity"], parts["dephasing"] + parts["pulses"] + parts["preparation"], rel_tol=1e-9)


def test_gate_budget_matches_lindblad_for_pure_dephasing_form():
    # for diagonal noise the closed form F = (1 + w)^2 / 4 must agree with the master-equation result
    import numpy as np
    from adamas import opensys
    from adamas.coupling import dipolar_coupling_khz
    r, t2_ms = 20.0, 1.0
    t_gate_us = 1e3 / (2 * float(dipolar_coupling_khz(r)))
    w = np.exp(-t_gate_us / (t2_ms * 1e3))
    assert math.isclose(opensys.cz_gate_fidelity(r, t2_ms, t1_ms=1e9), (1 + w) ** 2 / 4, rel_tol=1e-6)


def test_surface_code_simulator_reproduces_threshold_behavior():
    sim = pytest.importorskip("adamas.surface_sim")
    if sim.pymatching is None:
        pytest.skip("PyMatching not installed")
    assert sim.logical_error_rate(5, 0.0, 0.0, shots=200)[0] == 0.0
    below = [sim.logical_error_rate(d, 0.015, 0.015, shots=3000, seed=d)[0] for d in (3, 7)]
    above = [sim.logical_error_rate(d, 0.045, 0.045, shots=3000, seed=d)[0] for d in (3, 7)]
    assert below[1] < below[0] / 3            # below threshold a larger code is much better
    assert above[1] > above[0]                # above threshold it is worse
    assert 0.025 < sim.threshold_estimate(shots=3000, steps=5) < 0.036      # published: 0.0293 [wang2003]
    p_d, p_m = sim.effective_rates(1e-3, 3e-3, 1e-2)
    assert math.isclose(p_d, 1e-3 + 4 * 8 / 15 * 3e-3) and math.isclose(p_m, 1e-2 + 4 * 8 / 15 * 3e-3)
    assert sim.effective_rates(1e-3, 3e-3, 1e-2, f_link=0.0) == (1e-3, 1e-2)
