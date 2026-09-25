"""Row-based placement of the synthesized DIA-4 on the PDK-0 cell library, and a DEF for OpenROAD (project P-2).

This is not a router. It parses Yosys' netlist, assigns cells to rows with a simple net-connectivity ordering
(greedy min-cut style), writes (1) a placed GDS built from the cell layouts, (2) a DEF with the same placement that
OpenROAD can route, and (3) a summary: core area, utilization, and total half-perimeter wirelength [weste2011].
Usage: python circuits/digital/place.py  [netlist]  (default dia4_netlist.v)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from adamas import pdk0, stdcells  # noqa: E402

INST = re.compile(r"^\s*(BUF|INV|NAND2|NOR2|NOR3|DFF)\s+(\S+)\s*\((.*?)\);", re.S | re.M)
PIN = re.compile(r"\.(\w+)\(([^)]*)\)")


def parse(path: Path):
    text = path.read_text()
    insts = []
    for m in INST.finditer(text):
        pins = {k: v.strip() for k, v in PIN.findall(m.group(3))}
        insts.append((m.group(1), m.group(2).strip("\\"), pins))
    return insts


def place(insts, utilization=0.6):
    widths = {n: stdcells.CELLS[n][3] * stdcells.PITCH_UM for n in stdcells.CELLS}
    total = sum(widths[t] for t, _, _ in insts)
    core_area = total * stdcells.ROW_HEIGHT_UM / utilization
    side = core_area ** 0.5
    n_rows = max(1, round(side / stdcells.ROW_HEIGHT_UM))
    row_w = total / utilization / n_rows
    # ordering: BFS over the netlist graph so connected cells land near each other
    by_net = {}
    for i, (_, _, pins) in enumerate(insts):
        for net in pins.values():
            by_net.setdefault(net, []).append(i)
    seen, order = set(), []
    for start in range(len(insts)):
        if start in seen:
            continue
        stack = [start]
        while stack:
            i = stack.pop()
            if i in seen:
                continue
            seen.add(i); order.append(i)
            for net in insts[i][2].values():
                stack.extend(j for j in by_net[net] if j not in seen)
    placed, x, filled, row = [], 0.0, 0.0, 0
    cap = total / n_rows                                    # cell width per row; gaps spread the utilization
    for i in order:
        t, name, pins = insts[i]
        if filled + widths[t] > cap * 1.001 and row < n_rows - 1:
            row += 1; x = 0.0; filled = 0.0
        x = round(x / stdcells.PITCH_UM) * stdcells.PITCH_UM
        placed.append((t, name, pins, x, row * stdcells.ROW_HEIGHT_UM))
        x += widths[t] / utilization; filled += widths[t]
    hpwl = 0.0
    for net, members in by_net.items():
        xs = [placed[order.index(i)][3] + widths[placed[order.index(i)][0]] / 2 for i in members]
        ys = [placed[order.index(i)][4] + stdcells.ROW_HEIGHT_UM / 2 for i in members]
        hpwl += (max(xs) - min(xs)) + (max(ys) - min(ys))
    return placed, {"cells": len(insts), "rows": n_rows, "core_w_um": row_w, "core_h_um": n_rows * stdcells.ROW_HEIGHT_UM,
                    "cell_area_um2": total * stdcells.ROW_HEIGHT_UM, "utilization": utilization, "hpwl_um": hpwl}


def write_outputs(placed, stats, out_dir: Path, design="dia4"):
    used = {t for t, *_ in placed}
    lib = {n: stdcells.cell_layout(n) for n in stdcells.CELLS if n in used}
    top = pdk0.Cell(design.upper() + "_PLACED")
    for t, name, pins, x, y in placed:
        top.ref(lib[t], x, y)
    top.box("ISO", -10, -10, stats["core_w_um"] + 10, -5)
    pdk0.write_gds(str(out_dir / f"{design}_placed.gds"), [top, *lib.values()], top.name)
    lines = ["VERSION 5.8 ;", f"DESIGN {design} ;", "UNITS DISTANCE MICRONS 1000 ;",
             f"DIEAREA ( 0 0 ) ( {int(stats['core_w_um'] * 1000)} {int(stats['core_h_um'] * 1000)} ) ;",
             f"COMPONENTS {len(placed)} ;"]
    for t, name, pins, x, y in placed:
        lines.append(f"  - {name} {t} + PLACED ( {int(x * 1000)} {int(y * 1000)} ) N ;")
    lines += ["END COMPONENTS", "END DESIGN"]
    (out_dir / f"{design}_placed.def").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    net = Path(sys.argv[1]) if len(sys.argv) > 1 else here / "dia4_netlist.v"
    insts = parse(net)
    placed, stats = place(insts)
    stdcells.write_lef(str(here / "adamas_ed.lef"))
    stdcells.write_liberty(str(here / "adamas_ed_timed.lib"))
    write_outputs(placed, stats, here)
    print({k: (round(v, 1) if isinstance(v, float) else v) for k, v in stats.items()})
