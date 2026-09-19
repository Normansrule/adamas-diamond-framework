import math

from adamas import doping, logic, materials, power, thermal, wafer


def test_foms_relative_to_silicon():
    f = materials.normalized_foms()
    assert f["Si"]["BFOM"] == 1.0
    assert 4.0e4 < f["Diamond"]["BFOM"] < 6.0e4
    assert f["Diamond"]["KFOM"] > f["4H-SiC"]["KFOM"] > 1 > f["Ga2O3"]["KFOM"]
    assert math.isclose(f["Diamond"]["JFOM"], 2500, rel_tol=1e-6)


def test_incomplete_ionization_ordering():
    frac = {k: doping.ionized_fraction(d, 1e17) for k, d in doping.DOPANTS.items()}
    assert frac["Si:B"] > 0.8
    assert 1e-3 < frac["C:B"] < 2e-2
    assert frac["C:P"] < frac["C:B"]
    assert frac["C:N"] < 1e-9


def test_boron_activation_rises_with_temperature():
    d = doping.DOPANTS["C:B"]
    assert doping.ionized_fraction(d, 1e17, 600) > 10 * doping.ionized_fraction(d, 1e17, 300)


def test_on_resistance_scaling_and_measured_point():
    si, c = materials.MATERIALS["Si"], materials.MATERIALS["Diamond"]
    assert math.isclose(power.ron_sp_mohm_cm2(si, 2000) / power.ron_sp_mohm_cm2(si, 1000), 4.0, rel_tol=1e-9)
    ideal = power.ron_sp_mohm_cm2(c, 2608, "p")
    measured = power.MEASURED_DIAMOND["saha2021"]["ron_mohm_cm2"]
    assert ideal < measured < power.ron_sp_mohm_cm2(si, 2608)


def test_transit_frequency():
    assert 100 < power.ft_transit_ghz(1e7, 100) < 200


def test_hotspot_inverse_in_kappa():
    si = thermal.hotspot_rise_k(1.0, 1.5, 50)
    c = thermal.hotspot_rise_k(1.0, 22.0, 50)
    assert math.isclose(si / c, 22.0 / 1.5, rel_tol=1e-9)


def test_wafer_math():
    assert wafer.dies_per_wafer(300, 100) > wafer.dies_per_wafer(76, 100) > 0
    assert math.isclose(wafer.poisson_yield(100, 0.0), 1.0)
    assert wafer.murphy_yield(100, 1.0) > wafer.poisson_yield(100, 1.0)


def test_inverter_inverts():
    drv = logic.Fet(vth=1.5, w_um=200)
    load = logic.Fet(vth=-2.0, w_um=25)
    vin, vout = logic.inverter_vtc(drv, load, vdd=10.0, n=41)
    assert vout[0] > 9.5 and vout[-1] < 1.0
    assert all(b <= a + 1e-6 for a, b in zip(vout, vout[1:]))
