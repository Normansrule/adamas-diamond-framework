import shutil
import subprocess
from pathlib import Path

from adamas import stdcells

ROOT = Path(__file__).resolve().parents[1]


def test_timing_is_monotone_in_load_and_series_stack():
    t = stdcells.timing("NOR2")
    for row in t.delay_ns:
        assert row[0] < row[1] < row[2]
    assert stdcells.timing("NAND2").delay_ns[0][0] > stdcells.timing("NOR2").delay_ns[0][0]     # series pull-up is slower
    assert 0.5 < t.delay_ns[0][0] < 20


def test_lef_and_liberty_are_written_and_consistent(tmp_path):
    lef, lib = tmp_path / "a.lef", tmp_path / "a.lib"
    stdcells.write_lef(str(lef)); stdcells.write_liberty(str(lib))
    text = lef.read_text()
    assert text.count("MACRO ") == len(stdcells.CELLS) and "SITE core" in text
    for name in stdcells.CELLS:
        assert f"cell({name})" in lib.read_text()
    if shutil.which("yosys"):
        out = subprocess.run(["yosys", "-q", "-p", f"read_liberty -lib {lib}"], capture_output=True, text=True)
        assert out.returncode == 0, out.stderr


def test_placement_of_dia4_if_netlist_exists():
    import sys
    sys.path.insert(0, str(ROOT / "circuits" / "digital"))
    import place as pl
    net = ROOT / "circuits" / "digital" / "dia4_netlist.v"
    if not net.exists():
        return
    insts = pl.parse(net)
    placed, st = pl.place(insts)
    assert len(placed) == len(insts) > 100
    assert st["core_w_um"] * st["core_h_um"] * st["utilization"] >= st["cell_area_um2"] * 0.99
    xs = [(x, y) for *_, x, y in placed]
    assert len(set(xs)) == len(xs)                                    # no two cells at the same origin


def test_orfs_platform_is_complete_and_readable(tmp_path):
    from adamas import orfs_platform
    files = {p.name for p in orfs_platform.write(tmp_path)}
    for need in ("config.mk", "setRC.tcl", "pdn.tcl", "adamas_pdk0.tech.lef", "adamas_ed.lef", "adamas_ed_timed.lib", "adamas_ed.gds", "adamas_pdk0.lyt"):
        assert need in files
    tech = (tmp_path / "adamas_pdk0.tech.lef").read_text()
    assert "TYPE CUT ;" in tech and "LAYER VIA" not in tech            # the v0.7.0 bug: 'LAYER VIA CUT' without TYPE
    macro = (tmp_path / "adamas_ed.lef").read_text()
    assert "MACRO TIEHI" in macro and "MACRO FILL1" in macro
    # no signal pin may touch a power rail on the same layer
    for name in stdcells.CELLS:
        g = stdcells.geometry(name)
        for rect in g["pins"].values():
            assert rect[1] >= 3 + 2 and rect[3] <= stdcells.ROW_HEIGHT_UM - 3 - 2
    try:
        import klayout.db as db
    except ImportError:
        return
    ly = db.Layout(); ly.read(str(tmp_path / "adamas_ed.gds"))
    assert {c.name for c in ly.each_cell()} >= set(stdcells.CELLS)
