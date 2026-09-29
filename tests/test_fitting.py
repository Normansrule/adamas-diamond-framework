from pathlib import Path

import numpy as np
import pytest

from adamas import fitting, glossary

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "docs" / "data" / "examples"


def load(name):
    return fitting.load_csv(EX / f"{name}.csv")


def test_fits_recover_the_simulated_truth():
    assert abs(fitting.fit("rabi", *load("rabi")).params["rabi_MHz"] - 5.0) < 0.05
    assert abs(fitting.fit("ramsey", *load("ramsey")).params["detuning_MHz"] - 3.0) < 0.05
    assert abs(fitting.fit("echo", *load("echo")).params["T2_us"] - 300) < 30
    assert abs(fitting.fit("arrhenius", *load("arrhenius")).params["E_A_eV"] - 0.37) < 0.02
    assert fitting.fit("g2", *load("g2")).params["g2_zero"] < 0.3
    iv = fitting.fit("iv", *load("iv_vgs7"))
    assert abs(iv.params["overdrive_V"] - 5.5) < 0.05              # |V_GS| = 7 V, threshold 1.5 V
    z = fitting.fit("odmr", *load("odmr_zero_field"))
    assert len(z.params) == 4 and abs(z.params["center1"] - 2870) < 0.5
    m = fitting.fit("odmr", *load("odmr_with_magnet"))
    assert (len(m.params) - 1) // 3 >= 4
    assert any("mT" in n for n in m.notes)


def test_uncertainties_and_cli(capsys):
    r = fitting.fit("rabi", *load("rabi"))
    assert all(np.isfinite(v) and v > 0 for v in r.errors.values())
    assert 0.2 < r.chi2_red < 5
    assert fitting.main(["rabi", str(EX / "rabi.csv")]) == 0
    assert "π pulse" in capsys.readouterr().out


def test_example_files_are_current(tmp_path):
    fresh = fitting.example_datasets(tmp_path)
    for p in fresh:
        a, b = np.loadtxt(p, delimiter=",", skiprows=1), np.loadtxt(EX / p.name, delimiter=",", skiprows=1)
        assert np.allclose(a, b), p.name


def test_bad_input_is_explained(tmp_path):
    f = tmp_path / "x.csv"; f.write_text("a,b\n1,2\n")
    with pytest.raises(ValueError):
        fitting.load_csv(f)


def test_glossary_is_complete_and_current():
    for k, (full, d) in glossary.TERMS.items():
        assert full and d.endswith("."), k
    assert (ROOT / "docs" / "GLOSSARY.md").read_text(encoding="utf-8") == glossary.to_markdown()
