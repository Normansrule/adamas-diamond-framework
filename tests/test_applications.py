import math

from adamas import converter, scaling


def test_ron_temperature_trends():
    for n in ("Si", "4H-SiC", "GaN"):
        assert converter.ron_temperature_factor(n, 500) > converter.ron_temperature_factor(n, 400) > 1.0
    d = [converter.ron_temperature_factor("Diamond", t) for t in (300, 400, 500)]
    assert d[0] > d[1] > d[2] > 1.0           # bulk-doped drift: ionization gain with T, but still far above ideal (f_ion << 1), audit G6
    assert 150 < d[0] < 250                   # 1 / f_ion at 300 K for the 1.2 kV drift (about 0.5 % ionized)
    assert converter.ron_temperature_factor("Diamond", 500, bulk_doped=False) > 1.0                                    # hole gas has none
    assert math.isclose(converter.ron_temperature_factor("Si", 300), 1.0)


def test_switch_optimum_is_a_minimum_and_matches_closed_form():
    r, c, v, i, f = 20.0, 1e-9, 800.0, 300.0, 20e3
    d = converter.optimum_switch(r, c, v, i, f)
    assert math.isclose(d.p_cond_w, d.p_sw_w, rel_tol=1e-9)                     # equal split at the optimum
    closed = 2 * i * v * math.sqrt(f * r * 1e-3 * c / 2)
    assert math.isclose(d.p_total_w, closed, rel_tol=1e-9)
    for a in (d.area_cm2 * 0.5, d.area_cm2 * 2.0):
        assert i ** 2 * r * 1e-3 / a + 0.5 * c * v ** 2 * f * a > d.p_total_w


def test_material_ordering_matches_figures_of_merit():
    losses = {n: converter.material_switch(n, 1200, 800, 300, 20e3).p_total_w for n in ("Si", "4H-SiC", "GaN", "Diamond")}
    assert losses["GaN"] < losses["4H-SiC"] < losses["Diamond"] < losses["Si"]   # 300 K: a bulk-doped diamond drift loses to SiC
    hot = {n: converter.material_switch(n, 1200, 800, 300, 20e3, t_k=523.0).p_total_w for n in ("4H-SiC", "Diamond")}
    assert hot["Diamond"] < hot["4H-SiC"]                                            # and wins when hot
    meas = converter.material_switch("Diamond", 1200, 800, 300, 20e3, measured="saha2022").p_total_w
    assert losses["4H-SiC"] < meas < losses["Si"]                              # today's diamond: better than ideal Si, worse than ideal SiC
    assert 0.99 < converter.converter_efficiency("4H-SiC", 1200, 800, 300, 20e3) < 1.0


def test_quantum_sizing_arithmetic():
    assert math.isclose(scaling.wall_clock_hours("RSA-2048, 2021 layout", 1e-3), 8000.0)
    s = scaling.summary("RSA-2048, 2021 layout", cycle_s=1e-3)
    assert s["nv_cells"] == 5_000_000 and s["die_side_mm"] < 76 / math.sqrt(2) and s["wafers_76mm"] < 1
    assert scaling.die_side_mm(1_000_000, 2.0) == 2 * scaling.die_side_mm(1_000_000, 1.0)
    assert scaling.control_power_w(5_000_000) < 25_000                          # below a dilution-refrigerator plant [krinner2019]
