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
    data["power"] = power_data()
    from . import resource
    data["resource"] = resource.table()
    data["workloads"] = {k: list(v) for k, v in resource.WORKLOADS.items()}
    from . import traveler
    data["traveler"] = traveler.to_json()
    net = ROOT / "circuits" / "digital" / "dia4_netlist.v"
    if net.exists():
        sys.path.insert(0, str(ROOT / "circuits" / "digital"))
        import place
        placed, st = place.place(place.parse(net))
        data["dia4_layout"] = {"w": st["core_w_um"], "h": st["core_h_um"], "row": stdcells.ROW_HEIGHT_UM,
                               "cells": [{"n": n, "t": t, "x": round(x, 2), "y": round(y, 2), "w": stdcells.CELLS[t][3] * stdcells.PITCH_UM}
                                         for t, n, _, x, y in placed]}
    return data


def power_data(bv_table: float = 1200.0) -> dict:
    """Per-material inputs for the Power Lab, computed by adamas.converter so the browser uses the Python physics.
    R_on(T) tables are evaluated at a 1200 V class (the diamond ionization factor depends weakly on the drift doping)."""
    import numpy as np
    from . import converter, materials, power
    T = [float(t) for t in np.arange(300, 660, 10)]
    out = {}
    for key, name, measured in [("Si", "Silicon (ideal)", None), ("4H-SiC", "Silicon carbide (ideal)", None), ("GaN", "Gallium nitride (ideal)", None),
                                ("Diamond", "Diamond (ideal, holes)", None), ("Diamond", "Diamond (measured 2022 device)", "saha2022")]:
        m = materials.MATERIALS[key]
        if measured:
            pt = power.MEASURED_DIAMOND[measured]
            rsp = pt["ron_mohm_cm2"] * (1000.0 / pt["bv_v"]) ** 2
            F = [converter.ron_temperature_factor(key, t, bv_table, bulk_doped=False) for t in T]
        else:
            rsp = power.ron_sp_mohm_cm2(m, 1000.0, "p" if key == "Diamond" else "n")
            F = [converter.ron_temperature_factor(key, t, bv_table) for t in T]
        out[name] = {"key": key, "measured": measured, "rsp_1kv": rsp, "coss_1kv": converter.coss_sp_f_cm2(m, 1000.0),
                     "t_table": {"T": T, "F": F}, "tjmax_c": converter.TJ_MAX_C[key]}
    return out


def build_course(out: Path, head: str) -> None:
    """Generate web/course pages from adamas.course (single source for pages and notebooks)."""
    import html as H
    from .course import LESSONS, REPO
    d = out / "course"; d.mkdir(exist_ok=True)
    head = head.replace("../assets/", "../assets/")
    cards = "".join(f'''<a class="card reveal" href="lesson-{L["id"]}.html"><span class="tag">Lesson {L["id"]} · {L["minutes"]} min</span><h3>{H.escape(L["title"])}</h3>
      <p>{H.escape(L["objectives"][0])}.</p><span class="go">Start → <span id="badge{L["id"]}" style="color:var(--mute);font-weight:400;margin-left:8px"></span></span></a>''' for L in LESSONS)
    ids = [L["id"] for L in LESSONS]
    (d / "index.html").write_text(f'''<!doctype html><html lang="en" data-base=".."><head>{head}<title>Course · ADAMAS</title></head><body><main class="wrap">
<section class="block" style="padding:60px 0 10px"><span class="eyebrow">Course</span><h1 style="font-size:clamp(34px,5vw,60px)">Diamond chips, <span class="grad">in seven lessons</span></h1>
<p class="lead">From "why diamond?" to "how big is the machine?". Each lesson has objectives, readings, a lab task, a notebook you can run in your browser, and a four-question check. About six hours in total; suitable for self-study or a one-month module.</p>
<div id="progress" class="card" style="margin-top:20px"></div></section>
<div class="bento" style="grid-template-columns:repeat(3,1fr)">{cards}</div>
<section class="block"><div class="card"><h3>For instructors</h3><p>Notebooks live in <a href="{REPO}/tree/main/notebooks">notebooks/</a> and open in Google Colab or GitHub Codespaces. Every quiz answer cites a source in the repository's reference database; the lesson content is one Python file, <a href="{REPO}/blob/main/adamas/course.py">adamas/course.py</a>, so it is easy to fork and adapt.</p></div></section>
</main><script type="module">import {{ boot }} from '../assets/site.js'; import {{ progressBar }} from '../assets/course.js'; boot('Course'); progressBar(document.getElementById('progress'), {json.dumps(ids)});</script></body></html>''', encoding="utf-8")
    for L in LESSONS:
        colab = f"https://colab.research.google.com/github/Normansrule/adamas-diamond-framework/blob/main/notebooks/lesson_{L['id']}.ipynb"
        prev = f'<a class="btn" href="lesson-{L["id"] - 1}.html">← Lesson {L["id"] - 1}</a>' if L["id"] > 1 else '<a class="btn" href="index.html">← Course</a>'
        nxt = f'<a class="btn primary" href="lesson-{L["id"] + 1}.html">Lesson {L["id"] + 1} →</a>' if L["id"] < len(LESSONS) else '<a class="btn primary" href="index.html">Finish ✓</a>'
        reads = "".join(f'<li><a href="{REPO}/blob/main/{p}">{H.escape(t)}</a></li>' for t, p in L["read"])
        code = H.escape("\n\n".join(L["code"]))
        (d / f"lesson-{L['id']}.html").write_text(f'''<!doctype html><html lang="en" data-base=".."><head>{head}<title>Lesson {L["id"]}: {H.escape(L["title"])} · ADAMAS</title></head><body><main class="wrap" style="max-width:920px">
<section class="block" style="padding:50px 0 10px"><span class="eyebrow">Lesson {L["id"]} of {len(LESSONS)} · {L["minutes"]} minutes</span><h1 style="font-size:clamp(32px,4.5vw,54px)">{H.escape(L["title"])}</h1>
<canvas class="mini" data-mini="{ {1: "lattice", 2: "power", 3: "ring", 4: "rabi", 5: "stack", 6: "machine", 7: "fab"}.get(L["id"], "lattice") }" style="height:110px;margin:6px 0 14px"></canvas>
<div class="card"><h3>You will be able to</h3><ul>{"".join(f"<li>{H.escape(o)}</li>" for o in L["objectives"])}</ul></div></section>
<div class="card" style="margin:14px 0"><span class="tag gold">1 · Read</span><ul>{reads}</ul></div>
<div class="card" style="margin:14px 0"><span class="tag">2 · Play</span><p style="color:var(--ink)">{H.escape(L["lab"][1])}</p><a class="btn primary" href="../{L["lab"][0]}">Open the lab →</a></div>
<div class="card" style="margin:14px 0"><span class="tag violet">3 · Compute</span><p>The same physics in Python. Run it in your browser with Colab, or locally after <code>pip install -e .</code></p>
<div class="term" style="margin:10px 0"><pre>{code}</pre></div><a class="btn" href="{colab}">Open notebook in Colab</a></div>
<div class="card" style="margin:14px 0"><span class="tag red">4 · Check</span><div id="quiz"></div></div>
<div style="display:flex;justify-content:space-between;margin:24px 0 60px">{prev}{nxt}</div>
</main><script type="module">import {{ boot }} from '../assets/site.js'; import {{ quiz }} from '../assets/course.js'; import {{ minis }} from '../assets/minis.js'; boot('Course'); minis();
quiz(document.getElementById('quiz'), {L["id"]}, {json.dumps(L["quiz"], ensure_ascii=False)});</script></body></html>''', encoding="utf-8")


def gallery_items() -> list[dict]:
    """Every figure and animation with the first line of the function that draws it as its caption."""
    import ast
    import re
    caps = {}
    for f in ["figures.py", "figures_expert.py", "figures_apps.py", "animations.py"]:
        src = (ROOT / "adamas" / f).read_text(encoding="utf-8")
        for node in ast.parse(src).body:
            if isinstance(node, ast.FunctionDef):
                m = re.search(r'"((?:fig\d\d|anim)_\w+\.(?:png|gif))"', ast.get_source_segment(src, node) or "")
                if m:
                    caps[m.group(1)] = (ast.get_docstring(node) or "").split("\n")[0]
    items = []
    for p in sorted((ROOT / "docs" / "img").glob("fig*.png")) + sorted((ROOT / "docs" / "img").glob("anim_*.gif")):
        pretty = p.stem.split("_", 1)[1].replace("_", " ").capitalize()
        cap = caps.get(p.name) or pretty
        items.append({"src": f"img/{p.name}", "kind": "animation" if p.suffix == ".gif" else "figure", "caption": cap, "title": pretty})
    return items


def build_gallery(out: Path) -> None:
    import html as H
    items = gallery_items()
    tiles = "".join(f'''<figure class="tile" data-kind="{i["kind"]}" data-text="{H.escape((i["title"] + " " + i["caption"]).lower())}">
      <img loading="lazy" src="{i["src"]}" alt="{H.escape(i["title"])}"><figcaption><b>{H.escape(i["title"])}</b><span>{H.escape(i["caption"])}</span></figcaption></figure>''' for i in items)
    n_fig = sum(i["kind"] == "figure" for i in items); n_anim = len(items) - n_fig
    (out / "gallery.html").write_text(f'''<!doctype html><html lang="en" data-base="."><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="assets/style.css"><title>Gallery · ADAMAS</title>
<style>.masonry{{columns:3 320px;column-gap:16px;margin-top:24px}}.tile{{break-inside:avoid;margin:0 0 16px;background:var(--glass);border:1px solid var(--line);border-radius:16px;overflow:hidden;cursor:zoom-in;transition:transform .25s,border-color .25s}}
.tile:hover{{transform:translateY(-3px);border-color:rgba(111,243,255,.4)}}.tile img{{width:100%;display:block;background:#fff}}.tile figcaption{{padding:10px 12px;font-size:13px;color:var(--mute)}}.tile figcaption b{{display:block;color:var(--ink);font-size:14px;margin-bottom:3px}}
.tile[hidden]{{display:none}}#lb{{position:fixed;inset:0;background:rgba(3,5,10,.92);display:none;align-items:center;justify-content:center;z-index:100;flex-direction:column;padding:24px}}#lb.on{{display:flex}}#lb img{{max-width:95vw;max-height:80vh;border-radius:10px;background:#fff}}#lb p{{color:var(--ink);max-width:900px;text-align:center}}</style></head><body>
<main class="wrap"><section class="block" style="padding:60px 0 10px"><span class="eyebrow">Gallery</span><h1 style="font-size:clamp(34px,5vw,60px)">Every figure, <span class="grad">every animation</span></h1>
<p class="lead">{n_fig} figures and {n_anim} animations, all regenerated from code by <code>make figures animations</code>. Click any tile to enlarge it; each caption names the model and sources.</p>
<div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center"><div class="seg" id="kind"><button class="on" data-k="all">All</button><button data-k="figure">Figures</button><button data-k="animation">Animations</button></div>
<input type="text" id="q" placeholder="Search: qubit, heat, wafer, surface code…" style="max-width:340px"></div></section>
<div class="masonry" id="grid">{tiles}</div></main><div id="lb"><img id="lbImg" alt=""><p id="lbCap"></p><p style="color:var(--mute);font-size:13px">Click anywhere or press Esc to close</p></div>
<script type="module">import {{ boot }} from './assets/site.js'; boot('Gallery');
const $ = id => document.getElementById(id); let kind = 'all';
function filter() {{ const q = $('q').value.toLowerCase().trim(); document.querySelectorAll('.tile').forEach(t => t.hidden = !((kind === 'all' || t.dataset.kind === kind) && (!q || t.dataset.text.includes(q)))); }}
$('kind').onclick = e => {{ const b = e.target.closest('button'); if (!b) return; kind = b.dataset.k; $('kind').querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b)); filter(); }};
$('q').oninput = filter;
document.querySelectorAll('.tile').forEach(t => t.onclick = () => {{ $('lbImg').src = t.querySelector('img').src; $('lbCap').textContent = t.querySelector('figcaption').innerText; $('lb').classList.add('on'); }});
$('lb').onclick = () => $('lb').classList.remove('on'); addEventListener('keydown', e => {{ if (e.key === 'Escape') $('lb').classList.remove('on'); }});
</script></body></html>''', encoding="utf-8")


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
    build_course(out, head)
    build_gallery(out)
    (out / ".nojekyll").write_text("")
    return out


if __name__ == "__main__":
    p = build(sys.argv[1] if len(sys.argv) > 1 else ROOT / "site")
    print("built", p, sum(1 for _ in p.rglob("*")), "files")
