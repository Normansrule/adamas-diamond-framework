"""Fab Journey: the build, step by step, at four scopes (planned in v0.31.0, built in v0.32.0).

    L0 Kitchen table   experiments A1 and A2 (no fabrication)                      10 steps
    L1 Teaching lab    experiments B1, B2 and B3                                   11 steps
    L2 Cleanroom       one qubit cell and a coupled NV pair (traveler, QDL-04)     12 steps
    L3 Wafer scale     placement arrays, process control and yield (D2, P5, P7)     8 steps

Nothing here is new data. Each step is assembled from the sources that already hold it: the experiment cards
(adamas.experiments), the process traveler (adamas.traveler), the device library (adamas.qdl) and the Machine Atlas
(adamas.atlas). Each step has one action, a parts tray with Atlas IDs, a code-drawn diagram (a beam-path setup for L0
and L1, a before/after cross-section for L2 and L3, schematic and not to scale), a photo slot, a checkpoint, safety
callouts that point to institutional training, time and cost where the experiment card gives them (estimates), and
troubleshooting where the traveler lists failure modes.

Checkpoints are computed where the package has a model: the build-program P1 and P2 fits (adamas.build_program) and the
device-library checks (adamas.qdl). Elsewhere the checkpoint lists the traveler's acceptance criteria, which are
measured on your own sample; the page says so instead of inventing a result.

Photos. Only public-domain, CC0, CC BY or CC BY-SA photos may appear, each logged in references/images.psv with its
author, source and license, and checked by tests/test_journey.py. No AI-generated image is ever shown as a photo. In
v0.32.0 the log is empty: the Wikimedia Commons candidates could not be license-checked from the build container, so
every step shows its diagram and says that no open photo is logged yet.
"""
from __future__ import annotations

import functools
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "references" / "images.psv"
LICENSES = ("public domain", "CC0", "CC BY", "CC BY-SA")
TRAINING = ("Hazardous steps need your institution's laser, chemical, cleanroom and high-voltage training before you "
            "start; these notes do not replace it.")

LEVELS = [
    {"id": "L0", "name": "Kitchen table", "scope": "Experiments A1 and A2: see the NV glow, hear it resonate, weigh a magnet. No fabrication.", "experiments": ["A1", "A2"]},
    {"id": "L1", "name": "Teaching lab", "scope": "Experiments B1 to B3: pulsed control, vector magnetometry, boron activation.", "experiments": ["B1", "B2", "B3"]},
    {"id": "L2", "name": "Cleanroom device", "scope": "One qubit cell and a coupled NV pair on the traveler's qubit variant (device QDL-04).", "device": "QDL-04"},
    {"id": "L3", "name": "Wafer scale", "scope": "Placement arrays, statistical process control and yield (experiment D2, build phases P5 and P7).", "experiments": ["D2"]},
]

# Machines each experiment uses (Machine Atlas, build-program phases P1 and P2).
EXP_ATLAS = {"A1": ["M30", "M31", "M32", "M33", "M34", "M35", "M36"], "A2": ["M37"],
             "B1": ["M38", "M39", "M40", "M41", "M42", "M46"], "B2": ["M43", "M52"], "B3": ["M44", "M45"]}

# Beam path or circuit drawn for each experiment (L0, L1), in signal order.
SETUP = {"A1": ["Green source", "NV diamond on antenna", "Red filter", "Photodiode", "Microcontroller"],
         "A2": ["Magnet on rail", "NV diamond", "A1 readout chain"],
         "B1": ["532 nm laser", "Acousto-optic modulator", "NV plate on microwave line", "Filter", "Photodiode", "Pulse timing"],
         "B2": ["Helmholtz coils", "NV plate", "B1 readout chain"],
         "B3": ["Source-measure unit", "Boron-doped diamond on hot stage", "Thermometer"]}

# Computed checkpoints: experiment step title -> (python, what it shows).
EXP_CHECK = {("A1", "Find the dip"): "p1_detection", ("A2", "Plot log-log"): "p1_magnetometer",
             ("B1", "Rabi"): "p2_rabi", ("B1", "Ramsey"): "p2_ramsey", ("B1", "Echo"): "p2_echo",
             ("B2", "Fit"): "p2_vector", ("B3", "Arrhenius plot"): "p2_arrhenius"}

# L2: cross-section after each step (top layer first). Before = the previous step's after.
SUB = "Electronic-grade diamond plate"
L2_AFTER = {
    "S01": [SUB], "S02": ["Oxygen-terminated surface", SUB], "S03": ["¹²C epitaxial cap", SUB], "S04": ["¹²C cap, oxygen-terminated", SUB],
    "S05": ["¹²C cap with etched alignment marks", SUB], "S06": ["PMMA mask with apertures", "Implanted ¹⁵N (depth below)", "¹²C cap", SUB],
    "S06a": ["Vacancies around each implanted ¹⁵N", "¹²C cap", SUB], "S07": ["NV pair in the ¹²C cap", SUB],
    "S13": ["Al₂O₃ (atomic layer deposition)", "NV pair", SUB], "S16": ["Gold coplanar waveguide and electrodes", "Al₂O₃", "NV pair", SUB],
    "S18": ["Gold coplanar waveguide and electrodes", "Al₂O₃", "NV pair (tested)", SUB], "S19": ["Package and gold wire bonds", "Chip", "Carrier"],
}
L2_EXTRA = {"S06a": {"title": "Vacancy creation", "label": "reported", "refs": ["chen2019"], "atlas": ["M25"],
                     "text": "Strip the PMMA mask. The implant itself makes the vacancies the anneal needs; laser writing can add vacancies at chosen sites [chen2019]. Optional; not a traveler step yet."}}
L2_CHECK = {"S18": [("QDL-01", 0), ("QDL-04", 0), ("QDL-05", 0)], "S06a": []}
IMPLANT_KEV = 5.0          # inside the traveler's 2.5 to 10 keV window [pezzagna2010]; illustrative choice

# L3: wafer-scale steps (D2, P5, P7). Cross-sections are schematic.
WAFER = "Silicon (or sapphire) wafer"
L3_STEPS = [
    {"id": "W1", "title": "Heteroepitaxial growth on iridium", "atlas": ["M03", "M01"], "label": "reported",
     "text": "Grow diamond on an iridium buffer by bias-enhanced nucleation (iridium on yttria-stabilized zirconia (YSZ) over silicon, or directly on sapphire), then thicken it by microwave plasma chemical vapor deposition (MPCVD). Heteroepitaxial films carry many dislocations, which limit NV coherence (adamas.nv dislocation model).",
     "after": ["Diamond film", "Iridium buffer", "YSZ (silicon route only)", WAFER], "refs": ["schreck2014", "schreck2017"]},
    {"id": "W2", "title": "Polish and map", "atlas": ["M05", "M06", "M07", "M08", "M09"], "label": "reported",
     "text": "Polish, then map stress (Raman), crystal quality (X-ray diffraction), photoluminescence and birefringence over the whole wafer.",
     "after": ["Polished diamond film (mapped)", "Iridium buffer", "YSZ (silicon route only)", WAFER], "refs": ["schreck2017"]},
    {"id": "W3", "title": "Implant a placement array", "atlas": ["M12", "M20", "M21"], "label": "proposed",
     "text": "Write an aperture array and implant ¹⁵N through it, as in L2 step S06 but over the wafer. Two-site cells about 10 nm apart need apertures and placement finer than the traveler's 20 to 50 nm PMMA apertures (tip-based masks or a focused ion beam, M21); this is a proposal.",
     "after": ["PMMA aperture array", "Implanted ¹⁵N array", "Diamond film", "Iridium buffer", "YSZ (silicon route only)", WAFER], "refs": ["pezzagna2010"]},
    {"id": "W4", "title": "Anneal", "atlas": ["M22"], "label": "reported",
     "text": "Vacuum anneal to form NV centers, then an oxidizing clean (traveler step S07).",
     "after": ["NV array (random conversion)", "Diamond film", "Iridium buffer", "YSZ (silicon route only)", WAFER], "refs": ["pezzagna2010"]},
    {"id": "W5", "title": "Map, then repair empty sites", "atlas": ["M47", "M48", "M25"], "label": "proposed",
     "text": "Map every site confocally, then laser-write NVs at the empty ones with local laser annealing and fluorescence feedback, as demonstrated for single NVs in bulk [chen2019]; repairing an implanted array this way is a proposal. A furnace re-anneal would act on the whole wafer and could change working sites, and repair cannot fix sites that hold two or more NVs.",
     "after": ["NV array (repaired sites)", "Diamond film", "Iridium buffer", "YSZ (silicon route only)", WAFER], "refs": ["chen2019"]},
    {"id": "W6", "title": "Statistical process control", "atlas": ["M00", "M17"], "label": "proposed", "chart": "spc",
     "text": "Track every traveler check on every wafer as a control chart against its acceptance limits (experiment D2).", "refs": []},
    {"id": "W7", "title": "Placement yield", "atlas": ["M00"], "label": "simulated", "chart": "yield",
     "text": "Probability that a two-site cell holds exactly one NV per site, closer than the coupling horizon (adamas.coupling.pair_yield).", "refs": ["pezzagna2010"]},
    {"id": "W8", "title": "Gate: plan arrays?", "atlas": ["M00"], "label": "proposed", "chart": "gate",
     "text": "Build-program P5 question: is placement yield good enough to plan arrays? Set how many working cells the array needs; the page computes how many two-site cells (and sites) that takes.", "refs": []},
]


# ---------------------------------------------------------------------------------------------- checkpoints
def _bp():
    from . import build_program
    return build_program


@functools.lru_cache(maxsize=None)
def _p2():
    return _bp().p2_gate()


def checkpoint(name: str) -> dict:
    """Run one computed checkpoint; returns {what, value, pass, python}. Deterministic (fixed seeds)."""
    B = _bp()
    if name == "p1_detection":
        r = B.p1_detection()
        return {"what": "Dip found with signal-to-noise ≥ 5 and its center within half a line width of 2870 MHz", "value": f"{r['center_mhz']:.2f} ± {r['center_err_mhz']:.2f} MHz, signal-to-noise {r['snr']:.0f}",
                "pass": r["pass"], "python": "adamas.build_program.p1_detection"}
    if name == "p1_magnetometer":
        r = B.p1_magnetometer()
        return {"what": "Log-log slope of splitting against distance is −3 (dipole law) within two standard errors", "value": f"{r['slope']:.3f} ± {r['slope_err']:.3f}",
                "pass": r["pass"], "python": "adamas.build_program.p1_magnetometer"}
    if name in ("p2_rabi", "p2_ramsey", "p2_echo"):
        pu = _p2()["pulsed"]
        if name == "p2_rabi":
            return {"what": "Fitted Rabi frequency matches the value put in", "value": f"{pu['rabi_mhz']:.3f} ± {pu['rabi_err']:.3f} MHz (π pulse {pu['pi_ns']:.1f} ns)",
                    "pass": pu["rabi_pass"], "python": "adamas.build_program.p2_pulsed"}
        if name == "p2_ramsey":
            return {"what": "Fitted T₂* matches the value put in", "value": f"{pu['t2star_us']:.3f} ± {pu['t2star_err']:.3f} µs", "pass": pu["t2star_pass"], "python": "adamas.build_program.p2_pulsed"}
        return {"what": "Fitted T₂ matches, and the echo outlives T₂* more than tenfold", "value": f"{pu['t2_us']:.0f} ± {pu['t2_err']:.0f} µs, T₂/T₂* = {pu['echo_gain']:.0f}",
                "pass": pu["t2_pass"] and pu["echo_pass"], "python": "adamas.build_program.p2_pulsed"}
    if name == "p2_vector":
        v = _p2()["vector"]
        return {"what": "|B| from the four NV orientations matches the coil field", "value": f"{v['b_mt']:.3f} ± {v['b_err']:.3f} mT", "pass": v["pass"], "python": "adamas.build_program.p2_vector"}
    if name == "p2_arrhenius":
        a = _p2()["arrhenius"]
        return {"what": "Boron activation energy recovered", "value": f"{a['ea_ev']:.3f} ± {a['ea_err']:.3f} eV", "pass": a["pass"], "python": "adamas.build_program.p2_arrhenius"}
    raise KeyError(name)


def qdl_checkpoint(dev: str, i: int) -> dict:
    from . import qdl
    r = qdl.run_check(dev, i); c = qdl.BY_ID[dev]["checks"][i]
    v = r["value"]
    return {"what": f"{dev}: {c['title']} ({r['what']})", "value": f"{v:.4g} {r['unit']}".strip(), "pass": r["pass"], "python": f"adamas.qdl.run_check('{dev}', {i})"}


def implant_depth_nm(energy_kev: float = IMPLANT_KEV) -> tuple[float, float]:
    from .coupling import implant_rule_of_thumb
    return implant_rule_of_thumb(energy_kev)


def placement_yield(ions_per_site: int, conv: float = 0.01, sigma_nm: float = 5.0, target_nm: float = 10.0) -> float:
    """adamas.coupling.pair_yield at the library's coupling horizon r_max (0.99 bound, adamas.qdl). conv = 0.01 is the
    about-1-percent keV conversion [pezzagna2010]; sigma 5 nm per axis and the 10 nm target are illustrative inputs."""
    from .coupling import pair_yield
    from .qdl import r_max_nm
    return pair_yield(target_nm, sigma_nm, conv, ions_per_site=ions_per_site, r_max_nm=r_max_nm())


def cells_to_write(cells: int, yield_per_cell: float) -> float:
    """Two-site cells to write so that `cells` working cells are expected (expected value only); each cell is two
    implant sites, so the site count is twice this."""
    return math.inf if yield_per_cell <= 0 else cells / yield_per_cell


# --------------------------------------------------------------------------------------------------- photos
def images() -> list[dict]:
    """Rows of references/images.psv: file | title | author | source | license | credit (comments start with #)."""
    rows = []
    if IMAGES.exists():
        for line in IMAGES.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                f = [x.strip() for x in line.split("|")]
                rows.append(dict(zip(("file", "title", "author", "source", "license", "credit", "step"), f)))
    return rows


def _photo(step_id: str) -> dict:
    for r in images():
        if r.get("step") == step_id:
            return {"status": "photo", **r}
    return {"status": "none", "note": "No openly licensed photo is logged for this step yet; the diagram is code-drawn and schematic."}


# ---------------------------------------------------------------------------------------------------- steps
def _exp_steps(eid: str) -> list[dict]:
    from .atlas import ATLAS
    from .experiments import EXPERIMENTS
    e = next(x for x in EXPERIMENTS if x["id"] == eid)
    out = []
    for k, (title, text, scene) in enumerate(e["steps"], 1):
        sid = f"{eid}.{k}"
        ck = EXP_CHECK.get((eid, title))
        out.append({"id": sid, "title": title, "action": text, "label": "reported", "experiment": eid,
                    "parts": [{"id": a, "name": ATLAS[a][0]} for a in EXP_ATLAS.get(eid, [])] if k == 1 else [],
                    "uses": list(scene), "diagram": {"kind": "setup", "chain": SETUP.get(eid, []), "active": k},
                    "photo": _photo(sid), "checkpoints": [checkpoint(ck)] if ck else [], "criteria": [],
                    "safety": list(e["safety"]), "time": e["time"] if k == 1 else None,
                    "cost": list(e["cost"]) if k == 1 else None, "troubleshoot": [], "refs": list(e["refs"]) if k == 1 else []})
    return out


def _l2_steps() -> list[dict]:
    from . import qdl, traveler
    from .atlas import ATLAS
    dev = qdl.BY_ID["QDL-04"]
    T = {s["id"]: s for s in traveler.STEPS}
    order = []
    for sid in dev["route"]["steps"]:
        order.append(sid)
        if sid == "S06":
            order.append("S06a")
    out, before = [], [SUB]
    depth, straggle = implant_depth_nm()
    for sid in order:
        after = [x.replace("(depth below)", f"(about {depth:.1f} ± {straggle:.1f} nm at {IMPLANT_KEV:g} keV)") for x in L2_AFTER[sid]]
        if sid in L2_EXTRA:
            x = L2_EXTRA[sid]
            st = {"id": sid, "title": x["title"], "action": x["text"], "label": x["label"], "traveler": False,
                  "parts": [{"id": a, "name": ATLAS[a][0]} for a in x["atlas"]], "criteria": [], "safety": ["Class 4 pulsed laser: interlocked enclosure."],
                  "troubleshoot": [], "refs": x["refs"], "t_max_c": None}
        else:
            s = T[sid]
            params = "; ".join(f"{p[0]}: {p[1]}" for p in s["params"])
            st = {"id": sid, "title": s["title"], "action": dev["route"]["overrides"].get(sid, params or s["title"]), "why": s["why"], "label": "reported", "traveler": True,
                  "parts": [{"id": a, "name": ATLAS[a][0]} for a in _l2_atlas(sid)], "equipment": list(s["equipment"]),
                  "criteria": [{"check": c[0], "unit": c[1], "min": c[2], "max": c[3], "src": c[4]} for c in s["checks"]],
                  "safety": _safety(s, T), "troubleshoot": [{"symptom": f[0], "cause": f[1], "fix": f[2]} for f in s["failures"]],
                  "refs": sorted({k for p in s["params"] for k in re.findall(r"\[([^\]]+)\]", p[2])}), "t_max_c": s["t_max_c"]}
        st.update({"diagram": {"kind": "section", "before": before, "after": after}, "photo": _photo(sid), "time": None, "cost": None,
                   "checkpoints": [qdl_checkpoint(d, i) for d, i in L2_CHECK.get(sid, [])]})
        out.append(st); before = after
    return out


# Atlas machines per traveler step (from the Atlas phase table and the traveler's equipment lists).
L2_ATLAS = {"S01": ["M06", "M08", "M09", "M19"], "S02": ["M10"], "S03": ["M01"], "S04": ["M10"], "S05": ["M11", "M12", "M16"],
            "S06": ["M12", "M20", "M21"], "S07": ["M22", "M10"], "S13": ["M14"], "S16": ["M11", "M13"],
            "S18": ["M47", "M49", "M51", "M54", "M55"], "S19": ["M27", "M28"]}


def _safety(s: dict, T: dict) -> list[str]:
    """The step's safety text with "As Sxx." resolved, plus the S02 acid-bench text when the step reuses that bench."""
    out = []
    for x in s["safety"]:
        m = re.fullmatch(r"As (S\d\d)\.", x.strip())
        out += list(T[m.group(1)]["safety"]) if m else [x]
    if s["id"] != "S02" and any("(S02)" in e for e in s["equipment"]):
        out += [x for x in T["S02"]["safety"] if x not in out]
    return out


def _l2_atlas(sid: str) -> list[str]:
    return L2_ATLAS.get(sid, [])


def _l3_steps() -> list[dict]:
    from . import traveler
    from .atlas import ATLAS
    out, before = [], [WAFER]
    for w in L3_STEPS:
        st = {"id": w["id"], "title": w["title"], "action": w["text"], "label": w["label"], "parts": [{"id": a, "name": ATLAS[a][0]} for a in w["atlas"]],
              "photo": _photo(w["id"]), "checkpoints": [], "criteria": [], "safety": [], "time": None, "cost": None, "troubleshoot": [], "refs": w["refs"]}
        if "after" in w:
            st["diagram"] = {"kind": "section", "before": before, "after": w["after"]}; before = w["after"]
        elif w["chart"] == "spc":
            st["diagram"] = {"kind": "spc", "limits": [{"step": s["id"], "check": c[0], "unit": c[1], "min": c[2], "max": c[3], "src": c[4]}
                                                       for s in traveler.STEPS for c in s["checks"] if c[2] is not None or c[3] is not None]}
        elif w["chart"] == "yield":
            rows = [{"ions_per_site": n, "yield": placement_yield(n)} for n in (1, 50, 100, 200)]
            st["diagram"] = {"kind": "yield", "rows": rows, "conv": 0.01, "sigma_nm": 5.0, "target_nm": 10.0}
            best = max(rows, key=lambda r: r["yield"])
            st["checkpoints"] = [{"what": "Expected share of two-site cells that work (one NV per site, closer than r_max)", "value": f"{best['yield']:.4f} at {best['ions_per_site']} ions per site (best of the grid 1, 50, 100, 200; the peak is near 1/conversion)",
                                  "pass": None, "python": "adamas.journey.placement_yield"}]
        else:
            st["diagram"] = {"kind": "gate"}
        if w["id"] == "W2":
            st["safety"] = ["Raman and photoluminescence lasers: enclosed or interlocked beam, wavelength-rated eyewear. X-ray diffraction: radiation interlocks."]
        if w["id"] in ("W1", "W3", "W4", "W5"):
            st["safety"] = {"W1": ["Hydrogen and methane are flammable: leak-checked lines, gas detectors, interlocked exhaust."],
                            "W3": ["Ion implanter: radiation (X-ray) interlocks and high voltage."],
                            "W4": ["Furnace hot-zone burns; vacuum implosion shielding.", "Tri-acid clean: as traveler step S02 (perchloric-rated hood, face shield, acid apron)."],
                            "W5": ["Class 4 pulsed laser: interlocked enclosure."]}[w["id"]]
        out.append(st)
    return out


@functools.lru_cache(maxsize=None)
def steps(level: str) -> tuple:
    L = next(x for x in LEVELS if x["id"] == level)
    if level in ("L0", "L1"):
        return tuple(s for e in L["experiments"] for s in _exp_steps(e))
    return tuple(_l2_steps() if level == "L2" else _l3_steps())


def refs_used() -> set[str]:
    keys = set()
    for L in LEVELS:
        for s in steps(L["id"]):
            keys |= set(s["refs"])
    return keys


def to_json() -> dict:
    import copy
    return {"levels": [{**L, "steps": copy.deepcopy(list(steps(L["id"])))} for L in LEVELS], "training": TRAINING, "licenses": list(LICENSES)}


# ------------------------------------------------------------------------------------------------ documents
GEN = "_Generated from `adamas/journey.py` (`adamas build docs`); do not edit by hand._"


def _layers(xs) -> str:
    return " / ".join(xs)


def _level_md(L: dict) -> str:
    S = steps(L["id"])
    out = [f"# Fab Journey {L['id']}: {L['name']}", "", GEN, "", L["scope"], "", f"> {TRAINING}", ""]
    for n, s in enumerate(S, 1):
        out += [f"## Step {n} · {s['id']} {s['title']}", "", f"**Label:** {s['label']}. " + s["action"], ""]
        if s.get("why"):
            out += [f"**Why:** {s['why']}", ""]
        if s["parts"]:
            out += ["**Parts and machines:** " + "; ".join(f"{p['id']} {p['name']}" for p in s["parts"]), ""]
        d = s["diagram"]
        if d["kind"] == "section":
            out += [f"**Cross-section (schematic, top first).** Before: {_layers(d['before'])}. After: {_layers(d['after'])}.", ""]
        elif d["kind"] == "setup":
            out += ["**Setup (signal order):** " + " → ".join(d["chain"]), ""]
        elif d["kind"] == "yield":
            out += ["**Placement yield (simulated; illustrative inputs: conversion 0.01 [pezzagna2010], 5 nm spread per axis, 10 nm target):** " +
                    "; ".join(f"{r['ions_per_site']} ions per site → {r['yield']:.4f}" for r in d["rows"]), ""]
        elif d["kind"] == "spc":
            out += [f"**Control limits ({len(d['limits'])} traveler checks with a limit):** " + "; ".join(
                f"{x['step']} {x['check']} {'≥ ' + str(x['min']) if x['min'] is not None else ''}{' ≤ ' + str(x['max']) if x['max'] is not None else ''} {x['unit']}".replace("  ", " ") for x in d["limits"]), ""]
        out += ["**Photo:** " + (f"{s['photo']['title']}, {s['photo']['author']}, {s['photo']['license']}" if s["photo"]["status"] == "photo" else s["photo"]["note"]), ""]
        for c in s["checkpoints"]:
            v = "pass" if c["pass"] else ("fail" if c["pass"] is False else "computed")
            out += [f"**Checkpoint (simulated, `{c['python']}`):** {c['what']}: {c['value']} → **{v}**", ""]
        if s["criteria"]:
            out += ["**Acceptance criteria (measure on your sample; ADAMAS = limit chosen by this project, proposed):** " + "; ".join(
                f"{c['check']}{' ≥ ' + str(c['min']) if c['min'] is not None else ''}{' ≤ ' + str(c['max']) if c['max'] is not None else ''} {c['unit']} ({c['src']})".replace("  ", " ") for c in s["criteria"]), ""]
        if s["safety"]:
            out += ["**Safety:** " + " ".join(s["safety"]) + " " + TRAINING, ""]
        if s["time"] or s["cost"]:
            out += [f"**Time and cost (whole experiment, estimates from the experiment card):** {s['time']}; US${s['cost'][0]:,} to {s['cost'][1]:,}", ""]
        if s["troubleshoot"]:
            out += ["**Troubleshooting:**", ""] + [f"- {t['symptom']}: {t['cause']} → {t['fix']}" for t in s["troubleshoot"]] + [""]
        if s["refs"]:
            out += ["Sources: " + " ".join(f"[{k}]" for k in s["refs"]), ""]
    return "\n".join(out)


def _index_md() -> str:
    out = ["# Fab Journey", "", GEN, "", "The build, step by step, at four scopes. Diagrams are code-drawn and schematic; photos appear only when an openly licensed one is logged in references/images.psv (none yet).", "",
           "| Level | Name | Steps | Scope |", "|---|---|---|---|"]
    out += [f"| [{L['id']}]({L['id']}.md) | {L['name']} | {len(steps(L['id']))} | {L['scope']} |" for L in LEVELS]
    return "\n".join(out + [""])


def documents() -> dict[str, str]:
    d = {"README.md": _index_md()}
    d.update({f"{L['id']}.md": _level_md(L) for L in LEVELS})
    return d


def write(folder: str = "docs/journey") -> list[str]:
    d = ROOT / folder; d.mkdir(parents=True, exist_ok=True)
    out = []
    for name, text in documents().items():
        (d / name).write_text(text, encoding="utf-8"); out.append(str(d / name))
    return out
