from adamas.hw import adf4351, odmr_sweep


def test_evaluation_board_register_defaults():
    r, info = adf4351.registers(2870.0)
    assert r[2] == 0x18004E42 and r[3] == 0x000004B3 and r[4] == 0x008C803C and r[5] == 0x00580005
    assert info["int"] == 114 and info["frac"] == 4 and info["mod"] == 5 and info["divider"] == 1


def test_frequency_reconstruction_across_the_band():
    for f in (35.0, 137.5, 999.9, 2200.0, 2869.7, 2870.0, 3456.1, 4400.0):
        r, info = adf4351.registers(f)
        assert abs(info["actual_mhz"] - f) <= 0.1 / info["divider"] + 1e-9, f
        int_ = (r[0] >> 15) & 0xFFFF; frac = (r[0] >> 3) & 0xFFF; mod = (r[1] >> 3) & 0xFFF; div = 1 << ((r[4] >> 20) & 7)
        assert abs(25.0 * (int_ + frac / mod) / div - info["actual_mhz"]) < 1e-9
        assert 2200.0 <= info["vco_mhz"] <= 4400.0


def test_write_order_and_sweep_logic():
    written, lines = [], []
    values = iter([0.5, 0.7] * 1000)
    odmr_sweep.sweep(lambda words: written.append(words), lambda: next(values), 2860.0, 2861.0, 0.5, 2, lines.append)
    assert len(written) == 3 and written[0][0] & 7 == 5 and written[0][-1] & 7 == 0     # R5 first, R0 last
    assert lines[-1] == "END" and lines[0].startswith("2860.000,0.6")


def test_out_of_range_is_rejected():
    import pytest
    with pytest.raises(ValueError):
        adf4351.registers(5000.0)
