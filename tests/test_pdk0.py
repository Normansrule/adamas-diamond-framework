import math
from pathlib import Path

from adamas import gate_budget, pdk0


def test_gds_roundtrip_with_klayout_if_available(tmp_path):
    cells = pdk0.monitor_die()
    out = tmp_path / "die.gds"
    pdk0.write_gds(str(out), cells, "PDK0_MONITOR")
    assert out.stat().st_size > 5000
    try:
        import klayout.db as db
    except ImportError:
        return
    ly = db.Layout(); ly.read(str(out))
    top = ly.top_cell()
    assert top.name == "PDK0_MONITOR" and ly.cells() == len(cells)
    bb = top.bbox()
    assert math.isclose(bb.right * ly.dbu, 3000.0) and math.isclose(bb.top * ly.dbu, 3000.0)
    li = ly.layer(7, 0)                                        # QIMPLANT: 10 x 10 apertures
    assert sum(1 for _ in top.begin_shapes_rec(li)) == 100


def test_real8_encoding_matches_gds_convention():
    # 1.0 = 0x41 10 00 00 00 00 00 00 ; 0.001 = 0x3E 41 89 37 4B C6 A7 EF (standard GDS unit encodings)
    assert pdk0._real8(1.0).hex() == "4110000000000000"
    assert pdk0._real8(1e-3).hex().startswith("3e4189374bc6a7")   # last nibble differs by rounding


def test_pfet_obeys_gate_to_ohmic_rule():
    c = pdk0.pfet("t", 16.0, 2.0, True)
    gate = [b for b in c.boxes if b[0] == "GATE"][0]
    for b in (b for b in c.boxes if b[0] == "OHMIC"):
        gap = min(abs(b[1] - gate[3]), abs(gate[1] - b[3]))
        assert gap >= pdk0.RULES["ohmic_to_gate"] * pdk0.LAMBDA_UM - 1e-9


def test_published_pair_check():
    g = gate_budget.published_check()
    assert 24 < g.t_gate_us < 27
    assert g.f_coherent > 0.995                                # coherence explains almost none of the 0.33 gap
    assert abs(gate_budget.published_check(0.75).fidelity - 0.67) < 0.02
    assert abs(gate_budget.published_check(0.873).fidelity - 0.82) < 0.02
    parts = gate_budget.published_check(0.85, 0.01).breakdown()
    assert parts["preparation"] > parts["pulses"] > parts["dephasing"]
