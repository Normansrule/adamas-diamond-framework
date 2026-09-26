"""Build the ADAMAS website (GitHub Pages): landing page, six interactive labs, the explorer, and data files.

    python -m adamas.site [out_dir]        (default: site/)

Static files live in web/. This builder injects the shared <head> into each lab, writes data/site.json from the Python
package (so every number on the site comes from the same cited models), copies the precomputed surface-code data and
the figure images, and renders the explorer. Browser simulations are pure JavaScript modules under web/assets/sim/,
unit-tested with node and, for the DIA-4 emulator, checked against the Verilog on random programs.
"""
from __future__ import annotations
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def site_data() -> dict:
    from . import materials, power, stdcells
    sys.path.insert(0, str(ROOT / "tools"))
    from refs_common import load
    foms = materials.normalized_foms()
    names = {"Si": "Silicon", "4H-SiC": "Silicon carbide", "GaN": "Gallium nitride", "Ga2O3": "Gallium oxide", "Diamond": "Diamond"}
    mats = {k: {"name": names[k], "eg": m.eg_ev, "ec": m.ec_mv_cm, "kappa": m.kappa_w_cmk, "mup": m.mu_p,
                "bfom": round(foms[k]["BFOM"], 1)} for k, m in materials.MATERIALS.items()}
    refs = load()
    pick = [r for r in refs if r.status == "V" and r.locator not in ("book", "report")]
    step = max(1, len(pick) // 64)
    chips = [{"key": r.key, "short": f"{r.authors.split(',')[0].split(';')[0]} et al. ({r.year}), {r.venue}"} for r in pick[::step]][:64]
    data = {
        "numbers": {"bfom": round(foms["Diamond"]["BFOM"]), "kappa_ratio": round(materials.MATERIALS["Diamond"].kappa_w_cmk / materials.MATERIALS["Si"].kappa_w_cmk, 1),
                    "best_bv": max(v["bv_v"] for v in power.MEASURED_DIAMOND.values()), "t2_ms": 1.8, "references": len(refs),
                    "figures": len(list((ROOT / "docs" / "img").glob("fig*.png")))},
        "materials": mats,
        "material_sources": "[sze2006] [kimoto2014] [mishra2008] [pearton2018] [isberg2002] [wort2008] [baliga1982]",
        "references": chips,
        "dia4_layout": None,
    }
    net = ROOT / "circuits" / "digital" / "dia4_netlist.v"
    if net.exists():
        sys.path.insert(0, str(ROOT / "circuits" / "digital"))
        import place
        placed, st = place.place(place.parse(net))
        data["dia4_layout"] = {"w": st["core_w_um"], "h": st["core_h_um"], "row": stdcells.ROW_HEIGHT_UM,
                               "cells": [{"n": n, "t": t, "x": round(x, 2), "y": round(y, 2), "w": stdcells.CELLS[t][3] * stdcells.PITCH_UM}
                                         for t, n, _, x, y in placed]}
    return data


def build(out: str | Path = "site") -> Path:
    from . import explorer
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(WEB, out, ignore=shutil.ignore_patterns("tests", "_head.txt", "node_modules"))
    head = (WEB / "labs" / "_head.txt").read_text(encoding="utf-8")
    for page in (out / "labs").glob("*.html"):
        page.write_text(page.read_text(encoding="utf-8").replace("<!--HEAD-->", head), encoding="utf-8")
    (out / "data").mkdir(exist_ok=True)
    (out / "data" / "site.json").write_text(json.dumps(site_data()), encoding="utf-8")
    sm = ROOT / "docs" / "data" / "surface_map.json"
    if sm.exists():
        shutil.copy(sm, out / "data" / "surface_map.json")
    shutil.copytree(ROOT / "docs" / "img", out / "img")
    html = explorer.build_html().replace('<a href="https://github.com/Normansrule/adamas-diamond-framework">Repository</a>',
                                         '<a href="index.html">← ADAMAS home</a><a href="https://github.com/Normansrule/adamas-diamond-framework">Repository</a>')
    (out / "explorer.html").write_text(html, encoding="utf-8")
    (out / ".nojekyll").write_text("")
    return out


if __name__ == "__main__":
    p = build(sys.argv[1] if len(sys.argv) > 1 else ROOT / "site")
    print("built", p, sum(1 for _ in p.rglob("*")), "files")
