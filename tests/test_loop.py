"""Equation-in-the-loop registry and the v0.28 simulations (addressing, gate bias)."""
import json
import math
from pathlib import Path

import pytest

from adamas import addressing as A
from adamas import gatebias as G
from adamas import loop, nv

ROOT = Path(__file__).resolve().parents[1]


def test_registry_is_complete_and_cites_known_sources():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from refs_common import load
    keys = {r.key for r in load()}
    for pid, p in loop.PANELS.items():
        assert (ROOT / "web" / p["lab"]).exists(), pid
        assert p["assumptions"] and p["units"] and p["refs"], pid
        assert set(p["refs"]) <= keys, (pid, set(p["refs"]) - keys)
        for k, v in p["vars"].items():
            assert v["name"] and "unit" in v and v["src"], (pid, k)
            assert v.get("derived") or v["min"] < v["max"], (pid, k)
            assert f'data-k="{k}"' in p["html"], (pid, k)          # every symbol is clickable in the equation
        mod, fn = p["python"].rsplit(".", 1)
        assert callable(getattr(__import__(mod, fromlist=[fn]), fn)), p["python"]


def test_golden_and_registry_files_are_current():
    g = json.loads((ROOT / "web" / "tests" / "loop_golden.json").read_text())
    assert json.loads(json.dumps(loop.golden())) == g, "run: adamas build docs"
    assert json.loads((ROOT / "web" / "tests" / "loop_registry.json").read_text()) == json.loads(json.dumps(loop.PANELS))


def test_mistimed_echo_refocuses_and_matches_ramsey_shape():
    assert nv.echo_mistimed(0.0, 2.0, 0.5) == pytest.approx(0.0)
    # with e = tau the mistimed echo is the Ramsey signal mirrored: 1 - P_ramsey
    assert nv.echo_mistimed(0.7, 1.3, 0.9) == pytest.approx(1 - float(nv.ramsey(0.7, 1.3, 0.9)))


def test_airy_spot_is_about_half_a_wavelength_over_na():
    assert A.spot_fwhm_nm(532, 0.95) == pytest.approx(0.5145 * 532 / 0.95, rel=2e-3)
    assert A.airy_intensity(0.0) == pytest.approx(1.0) and A.airy_intensity(0.61 * 532 / 0.95) < 1e-3   # first dark ring


def test_spectral_route_depends_on_field_direction():
    assert A.spectral_separation_mhz(5, 0, 0) < 1e-6                     # [001]: all four axes equivalent
    assert A.spectral_separation_mhz(5, 54.7356, 45) > 50                 # along [111]: one axis stands out
    assert A.gradient_shift_mhz(0.1, 15) == pytest.approx(4.2, abs=0.05)  # 0.1 G/nm at 15 nm: about 4 MHz (audit Q4)
    v = A.verdict(30.0, 1.0, 2.0)
    assert v["resolved"] and v["selective"] and v["crosstalk"] == pytest.approx(4 / 904)
    assert A.crosstalk(A.max_rabi_for_crosstalk(10.0, 0.01), 10.0) == pytest.approx(0.01)


@pytest.mark.parametrize("q", [0, 1])
@pytest.mark.parametrize("p", "XYZ")
@pytest.mark.parametrize("circ", [[("H", (1,)), ("CZ", (0, 1)), ("H", (1,))], [("CX", (0, 1)), ("H", (0,)), ("CX", (1, 0))]])
def test_pauli_propagation_matches_stim(q, p, circ):
    stim = pytest.importorskip("stim")
    for start in range(len(circ) + 1):
        ps = stim.PauliString(2); ps[q] = p
        c = stim.Circuit("\n".join(f"{g} {' '.join(map(str, qs))}" for g, qs in circ[start:])) if start < len(circ) else stim.Circuit()
        out = ps.after(c) if len(c) else ps
        res = G.propagate({q: p}, circ[start:])
        assert [res[k] for k in (0, 1)] == [{0: "I", 1: "X", 2: "Y", 3: "Z"}[out[k]] for k in (0, 1)]


def test_cz_keeps_the_bias_and_the_hczh_cnot_inverts_it_on_the_target():
    for eta in (1.0, 10.0, 100.0):
        b = G.output_bias("cz", eta)
        assert b[0] == pytest.approx(eta) and b[1] == pytest.approx(eta)
        c = G.output_bias("cnot", eta)
        assert c[0] == pytest.approx(eta, rel=0.01)          # the control only sees CZ and idles
        short = G.output_bias("cnot", eta, h_frac=1e-9)[1]     # Hadamards of negligible length: Z <-> X, Y unchanged
        assert short == pytest.approx(1 / (2 * eta + 1), rel=1e-6)
        assert c[1] >= short                                     # errors after the last H stay Z, so finite H raises it
    assert G.output_distribution("cnot", 100, 0.2)["spread"] > G.output_distribution("cnot", 100, 0.002)["spread"]
    assert not math.isnan(G.output_distribution("cz", 0.5)["spread"])
