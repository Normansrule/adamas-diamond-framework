"""Write the ADAMAS-PDK-0 monitor die to GDS and a preview PNG.   python circuits/layout/make_pdk0_monitor.py"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from adamas import pdk0  # noqa: E402

cells = pdk0.monitor_die()
out = ROOT / "circuits" / "layout" / "pdk0_monitor.gds"
pdk0.write_gds(str(out), cells, "PDK0_MONITOR")
print("wrote", out.relative_to(ROOT), pdk0.summarize(cells))
