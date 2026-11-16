"""Retrofit Map: real processes, tools, services and products that a group can use today, or retrofit from silicon,
silicon carbide (SiC) or gallium nitride (GaN) manufacturing, for each step of the ADAMAS build.

Every route names a real process or product, the numbers its source states, and its maturity:
  in production      sold or deployed today for diamond (a product, a tool for sale, or a paid service that lists diamond)
  on diamond         demonstrated on diamond in a paper or by a company, not sold as a process
  retrofit           a mature process proven on silicon, SiC, GaN or another material; using it on diamond is this
                     repository's proposal, so the claim is labeled proposed until someone runs it on diamond
  proposed           no demonstration
Maturity is about the process, not about ADAMAS: a sensor sold today does not make the ADAMAS processor real. Products
are listed against the Quantum Device Library device (adamas.qdl) they show is possible, never as parity with
superconducting or other qubits. Company claims without a paper are marked "company statement".
adamas build docs writes docs/process/RETROFIT.md; the Process and Devices pages show the same data.
"""
from __future__ import annotations

from pathlib import Path

from .traveler import STEPS

ROOT = Path(__file__).resolve().parents[1]

LEVELS = ("in production", "on diamond", "retrofit", "proposed")
LEVEL_TEXT = {"in production": "In production for diamond today", "on diamond": "Demonstrated on diamond",
              "retrofit": "Retrofit from silicon, SiC or GaN (proposed for diamond)", "proposed": "Proposed"}
COLORS = {"in production": "#2fbf71", "on diamond": "#4aa8ff", "retrofit": "#ffc46b", "proposed": "#ff5d6c"}

# Build stages in order, with the traveler steps (adamas.traveler) each one covers. "W" stages come before S01.
STAGES = [("W1", "Wafers", []), ("W2", "Growth reactors", ["S03"]), ("W3", "Slicing and lift-off", []),
          ("W4", "Polishing", ["S01", "S04"]), ("P1", "Etching and marks", ["S05", "S10"]),
          ("P2", "Nitrogen and NV creation", ["S06", "S07"]), ("P3", "Surface, gate oxide and transistors", ["S08", "S11", "S12", "S13"]),
          ("P4", "Bonding and integration", ["S19"]), ("P5", "Packaging and heat", ["S19"]),
          ("P6", "Lithography and metal", ["S09", "S14", "S15", "S16"])]

# The traveler steps each route actually performs. A route counts for a step's maturity only if it is listed here, so a
# stage-wide route (for example a heat spreader in the packaging stage) does not raise the level of a step it does not do.
ROUTE_STEPS = {"R07": ["S03"], "R08": ["S03"], "R16": ["S06"], "R17": ["S06"], "R18": ["S06"], "R19": ["S06", "S07"],
               "R20": ["S06"], "R21": ["S05", "S10"], "R22": ["S05", "S10"], "R23": ["S08", "S13"], "R27": ["S19"],
               "R28": ["S19"], "R31": ["S09", "S14", "S15", "S16"]}

# Routes: id, stage, process, who or where, maturity, what the source states, refs, what is left for ADAMAS.
ROUTES = [
    ("R01", "W1", "Electronic-grade CVD single-crystal plates", "Element Six online store", "in production",
     "2.0 × 2.0 × 0.5 mm and 4.0 × 4.0 × 0.5 mm electronic-grade plates sold with list prices", ["e6cvd2026"],
     "Plates, not wafers: every cleanroom step runs on small pieces until wafers are used"),
    ("R02", "W1", "Heteroepitaxial wafers on iridium/sapphire (KENZAN Diamond)", "Orbray", "in production",
     "'Two-inch diamond substrate is available', with four-inch as the next stage (company statement); peer-reviewed two-inch "
     "(001) growth on misoriented sapphire by step flow", ["orbray2026", "kim2021"],
     "NV coherence on these wafers is to be measured"),
    ("R03", "W1", "Three-inch wafer process and volume two-inch supply", "Element Six with Orbray", "on diamond",
     "Industry announcement of a reproducible three-inch process, with two-inch prepared for volume production (company statement)",
     ["e6orbray2026"], "No paper yet; wafer specifications to be published"),
    ("R04", "W1", "Heteroepitaxy on iridium/yttria-stabilized zirconia (YSZ)/silicon with bias-enhanced nucleation", "University of Augsburg", "on diamond",
     "One single crystal about 90 mm across and 155 carats, 1.6 ± 0.25 mm thick; dislocation density about 4 × 10⁷ cm⁻² after "
     "1.5 mm of growth", ["schreck2017"], "Electronic-grade purity and NV coherence on such wafers are to be shown"),
    ("R05", "W1", "Mosaic wafer tiled from lift-off plates", "AIST (National Institute of Advanced Industrial Science and Technology, Japan)",
     "on diamond", "Two-inch mosaic (40 × 60 mm²) made from 24 plates of 10 × 10 mm²", ["yamada2014"],
     "Proposed: place dies away from the tile boundaries"),
    ("R06", "W1", "100 mm and 200 mm single-crystal diamond", "Diamond Foundry", "on diamond",
     "'a single crystal of diamond 100mm in diameter' weighing 110 carats (2023); a 200 mm single crystal shown in November 2026 "
     "(company statements, no paper or process)", ["diamondfoundry2023", "diamondfoundry2026"],
     "No published growth process, purity or defect data"),
    ("R07", "W2", "Microwave plasma chemical vapor deposition (MPCVD) reactor for single-crystal growth (SDS6K)", "Seki Diamond Systems, sold by Cornes Technologies", "in production",
     "6 kW at 2.45 GHz, standard 50 mm (2-inch) holder, 10 to 220 Torr", ["cornes2025"],
     "Buy or use one; the traveler's S03 recipe sets the gas and temperature"),
    ("R08", "W2", "915 MHz and 2.45 GHz microwave generators for single-crystal diamond", "MKS Instruments", "in production",
     "Generators for electronic-grade single-crystal growth at pressures above 160 Torr (company statement)", ["mks2026"],
     "Generators only; the reactor body comes from another maker or a laboratory design"),
    ("R09", "W2", "High-rate single-crystal growth and the direct-wafer process", "AIST", "on diamond",
     "2.45 GHz, 5 kW reactor; CH₄/H₂ at 60 and 500 sccm, 21 kPa, about 1100 to 1200 °C; seed ion-implanted to make a "
     "graphitizing layer so the grown plate lifts off", ["chayahara2011"],
     "The quantum layer is grown separately with the S03 recipe"),
    ("R10", "W3", "Lift-off by MeV ion implantation", "Research (Parikh and co-workers)", "on diamond",
     "4 to 5 MeV carbon or oxygen ions make a buried damaged layer (oxygen at 3 × 10¹⁷ cm⁻² or more); after annealing it is "
     "etched in acid or in oxygen at 550 to 600 °C, releasing the plate", ["parikh1992"],
     "Needs a MeV implanter (HZDR offers up to 6 MV, route R17)"),
    ("R11", "W3", "Laser slicing at the {100} plane", "Chiba University with Orbray", "on diamond",
     "An irradiation sequence that stops cracks running along {111} planes slices diamond at {100}", ["sakamoto2023"],
     "Kerf and thickness not given in the parts read"),
    ("R12", "W3", "KABRA laser slicing (silicon carbide)", "DISCO", "retrofit",
     "Slices ingots larger than 50 mm into wafers 100 µm thick or less (silicon carbide)", ["disco2024"],
     "Not shown on diamond; proposed here as the volume route once diamond boules exist"),
    ("R13", "W4", "Plasma-assisted polishing", "Research (Liu, Yamamura and co-workers)", "on diamond",
     "Sq 0.361 nm over 5 µm on a 21 × 19 mm mosaic, removal 13.3 µm/h, argon-oxygen plasma at 13.56 MHz and 100 W, 0.8 kPa, "
     "reported damage-free", ["liu2020"], "A research tool; no commercial version was found"),
    ("R14", "W4", "Chemical-mechanical polishing (CMP)", "Cardiff University; Fraunhofer USA CMW as a service", "on diamond",
     "Nanocrystalline diamond film from 18.3 to 1.7 nm root-mean-square (rms) roughness in 4 h with colloidal silica (0.42 nm rms locally); "
     "the Fraunhofer USA service states sub-nanometer roughness over large-area diamond wafers (company statement)",
     ["thomas2014", "fraunhofercmw2026"], "The paper used polycrystalline film; the service does not state the crystal type"),
    ("R15", "W4", "Grinding, polishing, laser cutting, plasma etching and metallization as a service", "Diamond Materials GmbH",
     "in production", "Lists these services for customer diamond (company statement, no specifications)", ["diamondmaterials2026"],
     "Ask for roughness and thickness tolerances"),
    ("R16", "P2", "Ion implantation service that lists diamond", "Ion Beam Services (IBS), France", "in production",
     "Lists diamond among implanted substrates; samples up to 12-inch wafers; for SiC, 5 to 400 keV with nitrogen among the species",
     ["ibs2026"], "Ask for ¹⁵N at the S06 energy and dose; the diamond energy range is not stated"),
    ("R17", "P2", "Ion implantation from 10 kV to 6 MV", "HZDR Innovation (Helmholtz-Zentrum Dresden-Rossendorf), Germany", "in production",
     "Species from hydrogen to gold, small samples up to 200 mm wafers", ["hzdr2026"],
     "Also the MeV source for lift-off (R10)"),
    ("R18", "P2", "Nitrogen delta-doping during growth", "Research (Awschalom group)", "on diamond",
     "Nitrogen layers at depths of 5 to 100 nm; T₂ above 100 µs at 5 nm and above 600 µs at 50 nm or deeper", ["ohno2012"],
     "An alternative to S06: no implant damage, but no lateral placement"),
    ("R19", "P2", "Laser writing of single NV centers", "Research (Oxford and Warwick)", "on diamond",
     "Single NV centers with up to 45 % success per site, within about 200 nm of the target; anneal 3 h at 1000 °C", ["chen2017"],
     "The detect-and-repair route of build phase P5 (Atlas M25)"),
    ("R20", "P2", "NV arrays through masks", "Research (Awschalom and Schenkel groups)", "on diamond",
     "Nanofabrication of single NV centers on sub-100 nm length scales across a chip", ["toyli2010"],
     "Yield is statistical (Poisson); see build phase P5"),
    ("R21", "P1", "Deep inductively coupled plasma etch with near-zero micromasking", "University College London", "on diamond",
     "45.1 nm/min in argon-oxygen (20 % O₂, 200 W) with a 20 s argon-chlorine clean every 2 min; 16.9 : 1 selectivity to an "
     "aluminium mask; 0.47 nm surface roughness; deeper than 10 µm", ["hicks2019"], "Use for marks (S05) and isolation (S10)"),
    ("R22", "P1", "Plasma etch tools for quantum diamond", "Oxford Instruments (PlasmaPro 100 Cobra inductively coupled plasma (ICP) and reactive ion etching (RIE))", "in production",
     "Surface roughness Ra below 0.3 nm on diamond for NV work (company statement)", ["oxinst2026"],
     "Tool for sale; the same class is on shared cleanroom rate sheets (Atlas M16)"),
    ("R23", "P3", "Hydrogen-terminated field-effect transistors (FETs) with atomic-layer-deposited Al₂O₃", "Waseda University (Kawarada group)", "on diamond",
     "Al₂O₃ deposited at 450 °C, 200 nm gate insulator; breakdown 1700 V at room temperature and 1200 V at 300 and 400 °C; "
     "drain current within 30 % from room temperature to 400 °C", ["kawarada2017", "kawarada2014"],
     "No foundry offering was found"),
    ("R24", "P4", "Room-temperature Au/Au atomic diffusion bonding to silicon", "AIST", "on diamond",
     "Ti/Au 5/12 nm layers bond single-crystal diamond to silicon in air; the silicon broke before the bond in shear tests",
     ["matsumae2018"], "The route to put a diamond die on a complementary metal-oxide-semiconductor (CMOS) chip (X27a)"),
    ("R25", "P4", "Surface-activated bonding of GaN to diamond", "Research (Liang and co-workers)", "on diamond",
     "Interface stable when heated to 1000 °C", ["liang2021"], "For GaN-on-diamond power and radio-frequency devices"),
    ("R26", "P4", "Quantum microchiplets on a photonic chip", "Research (Wan and co-workers)", "on diamond",
     "A 128-channel defect-free array of germanium- and silicon-vacancy diamond microchiplets on an aluminium nitride photonic "
     "circuit (color centers other than NV)", ["wan2020"], "Proposed here for NV chiplets; not shown with NV"),
    ("R27", "P5", "High-temperature reliability of diamond power devices", "AIST", "on diamond",
     "No change over 1500 hours at 400 °C; operation at 250 °C in a 1 A class device", ["shikata2013"],
     "The package itself is listed as a research item there"),
    ("R28", "P5", "Pressureless silver sintering (power-module die attach)", "Research on a non-diamond Schottky diode", "retrofit",
     "Sintered at 290 °C for 40 min without pressure", ["dai2023"],
     "Not shown on diamond; proposed for S19 because it stays below the 500 °C hydrogen limit"),
    ("R29", "P5", "Diamond heat spreaders", "Element Six", "in production",
     "Thermal conductivity from 1000 to 2200 W/(m·K), for radio-frequency power amplifiers and laser diodes", ["e6thermal2026"],
     "Passive diamond in production today"),
    ("R30", "P5", "GaN-on-diamond amplifiers in orbit", "Akash Systems", "in production",
     "5 W continuous wave at 8.4 GHz on Pixxel's Firefly satellites; described as the first GaN-on-diamond device in space",
     ["akash2026"], "Diamond as a heat sink, not as a semiconductor"),
    ("R31", "P6", "Shared university cleanroom: aligners, direct-write lithography, electron-beam evaporation", "University cleanrooms (for example the Washington Nanofabrication Facility)",
     "retrofit", "Hourly rates published for contact aligners, maskless direct writers and electron-beam evaporators (silicon tools)",
     ["wnf2026"], "The diamond recipes are in the traveler steps; small diamond pieces on silicon-sized tools are this repository's proposal"),
]

# Products on the market or deployed that show a Quantum Device Library device is real (adamas.qdl ids).
PRODUCTS = [
    ("QDL-17", "Qnami ProteusQ scanning NV microscope", "in production",
     "Room-temperature operation; sensitivity better than 2 µT/√Hz in continuous-wave operation; samples up to 40 × 50 mm²", ["qnami2026"]),
    ("QDL-17", "Qnami Quantilever MX diamond tip", "in production",
     "NV depth down to 10 nm from the apex (simulated by the maker), T₂* above 1 µs typical, tip radius 100 nm", ["qnami2019"]),
    ("QDL-12", "Element Six DNV-B1 and DNV-B14 quantum-grade diamond (material)", "in production",
     "DNV-B1: uniform NV concentration with spin lifetimes of a microsecond (2020); DNV-B14: more than ten times the NV density of "
     "DNV-B1 (2021)", ["e6dnv2020", "e6dnv2021"]),
    ("QDL-19", "QuantumDiamonds QD m.0 for chip failure analysis", "in production",
     "Diamond quantum microscope to find faults in integrated circuits; first production run fully allocated (2024, news report)",
     ["quantumdiamonds2024"]),
    ("QDL-01", "Quantum Brilliance room-temperature diamond quantum accelerator", "in production",
     "Rack-mounted system commissioned at the Pawsey Supercomputing Centre (2022); each processing unit has two qubits and runs at "
     "room temperature", ["qb2022", "ornl2025"]),
    ("QDL-01", "CIQTEK Diamond Quantum Computer for education", "in production",
     "One-qubit NV teaching instrument that works at room temperature", ["ciqtek2026"]),
    ("QDL-20", "Adámas Nanotechnologies NV-rich diamond (material)", "in production",
     "NV-rich plates sold with a list price; the nanodiamonds of the cell-thermometry paper came from the same company", ["lattispec2026", "kucsko2013"]),
    ("QDL-12", "SBQuantum diamond magnetometer for the MagQuest challenge", "on diamond",
     "Quantum diamond magnetometer about the size of a quart of milk, for a space launch in the MagQuest challenge (news report, 27 March 2026; NV not named)", ["sbquantum2026"]),
    ("QDL-12", "Lockheed Martin Dark Ice NV magnetometer", "on diamond",
     "Prototype magnetometer using NV centers in a synthetic diamond the size of a salt crystal (news report, 2019)", ["lockheed2019"]),
]


def _step_refs(sid: str) -> list[str]:
    s = next(x for x in STEPS if x["id"] == sid)
    keys = []
    for p in s["params"]:
        for tok in (p[2] or "").replace("]", " ").replace("[", " ").split():
            if tok not in keys:
                keys.append(tok)
    return keys


def routes(stage: str | None = None) -> list[dict]:
    keys = ("id", "stage", "process", "who", "level", "fact", "refs", "left")
    return [dict(zip(keys, r), steps=ROUTE_STEPS.get(r[0], [])) for r in ROUTES if stage in (None, r[1])]


def stage_level(stage: str) -> str:
    """The most mature level among a stage's routes (in production beats on diamond, and so on)."""
    lv = [r["level"] for r in routes(stage)]
    return min(lv, key=LEVELS.index) if lv else "proposed"


def step_view(sid: str) -> dict:
    """Routes for one traveler step, plus the diamond papers the step itself already cites."""
    rs = [r for r in routes() if sid in r["steps"]]
    cites = _step_refs(sid)
    level = min([r["level"] for r in rs] + (["on diamond"] if cites else []), key=LEVELS.index, default="proposed")
    return {"step": sid, "routes": [r["id"] for r in rs], "traveler_refs": cites, "level": level}


def products(device: str | None = None) -> list[dict]:
    keys = ("device", "name", "level", "fact", "refs")
    return [dict(zip(keys, p), material=p[1].endswith("(material)")) for p in PRODUCTS if device in (None, p[0])]


def summary() -> dict:
    r = routes()
    steps = [step_view(s["id"]) for s in STEPS]
    return {"routes": len(r), **{lv: sum(x["level"] == lv for x in r) for lv in LEVELS},
            "products": len(PRODUCTS), "devices_on_market": sorted({p["device"] for p in products() if p["level"] == "in production" and not p["material"]}),
            "materials_on_market": sorted({p["device"] for p in products() if p["level"] == "in production" and p["material"]}),
            "steps": len(steps), "steps_with_route": sum(bool(v["routes"]) for v in steps),
            "steps_by_level": {lv: sum(v["level"] == lv for v in steps) for lv in LEVELS}, "step_levels": {v["step"]: v["level"] for v in steps},
            "keys": sorted({k for x in ROUTES for k in x[6]} | {k for p in PRODUCTS for k in p[4]})}


def to_json() -> dict:
    return {"levels": LEVELS, "level_text": LEVEL_TEXT, "colors": COLORS, "stages": [list(s) for s in STAGES], "routes": routes(),
            "products": products(), "steps": {s["id"]: step_view(s["id"]) for s in STEPS}, "summary": summary()}


def _cite(keys, text: str = "") -> str:
    """Brackets for the keys that the text does not already cite inline."""
    return " ".join(f"[{k}]" for k in keys if f"[{k}]" not in text)


def to_markdown() -> str:
    s = summary()
    out = ["# Retrofit Map: real processes for every build stage", "",
           "*Generated by `adamas build docs` from `adamas/retrofit.py`; do not edit by hand.*", "",
           "This page answers one question for each stage of the build: **what real process, tool, service or product exists "
           "today that a group can use, or retrofit from silicon, silicon carbide (SiC) or gallium nitride (GaN) "
           "manufacturing?** Each route gives the numbers its source states and what is still left to do. Maturity levels:", ""]
    out += [f"- **{lv}**: {LEVEL_TEXT[lv]}." for lv in LEVELS]
    out += ["", "A retrofit route is a proposal of this repository until someone runs it on diamond. Products show that a device "
            "type is real; they do not make the ADAMAS processor real, and none is compared with superconducting or other qubits.", "",
            f"Of {s['routes']} routes: {s['in production']} in production, {s['on diamond']} demonstrated on diamond, "
            f"{s['retrofit']} retrofit, {s['proposed']} proposed. {s['products']} products or deployments cover "
            f"{len(s['devices_on_market'])} device types sold today as devices ({', '.join(s['devices_on_market'])}) and "
            f"{len(s['materials_on_market'])} whose NV diamond material is sold ({', '.join(s['materials_on_market'])}). "
            f"Of the {s['steps']} traveler steps, {s['steps_by_level']['in production']} have a route in production and "
            f"{s['steps_by_level']['on diamond']} more cite a diamond demonstration; the other {s['steps_by_level']['retrofit'] + s['steps_by_level']['proposed']} "
            f"({', '.join(sorted(k for k, v in s['step_levels'].items() if v in ('retrofit', 'proposed')))}) are standard lithography and "
            "metal steps on shared cleanroom tools (Atlas M11 to M13). A route counts for a step only if it performs that step "
            "(the 'Routes' column below); a step with no such route is 'on diamond' when its own parameters cite a diamond paper.", "",
            "![Retrofit Map](../img/fig62_retrofit_map.png)", ""]
    for k, name, steps in STAGES:
        out += [f"## {k} · {name} (best: {stage_level(k)})", ""]
        if steps:
            out += [f"Traveler steps: {', '.join(steps)} ([TRAVELER.md](TRAVELER.md)).", ""]
        out += ["| Route | Process | Who | Maturity | What the source states | What is left |", "|---|---|---|---|---|---|"]
        out += [f"| {r['id']} | {r['process']} | {r['who']} | **{r['level']}** | {r['fact']} {_cite(r['refs'], r['fact'])} | {r['left']} |" for r in routes(k)]
        out += [""]
    out += ["## Traveler steps and their best route", "", "| Step | Title | Routes | Diamond papers the step cites | Best level |", "|---|---|---|---|---|"]
    for st in STEPS:
        v = step_view(st["id"])
        out += [f"| {st['id']} | {st['title']} | {', '.join(v['routes']) or '—'} | {_cite(v['traveler_refs']) or '—'} | {v['level']} |"]
    out += ["", "## On the market: NV devices sold or deployed today", "",
            "| Device | Product | Maturity | What the source states |", "|---|---|---|---|"]
    out += [f"| {p['device']} | {p['name']} | **{p['level']}** | {p['fact']} {_cite(p['refs'], p['fact'])} |" for p in products()]
    out += ["", "## What a group can do this year", "",
            "1. Buy electronic-grade plates (R01) or a two-inch heteroepitaxial wafer (R02), and polish by plasma-assisted polishing "
            "or a CMP service (R13 to R15).",
            "2. Grow the quantum layer in a commercial 2.45 GHz reactor (R07) with the S03 recipe.",
            "3. Send pieces to an implantation service that lists diamond (R16, R17) for the S06 nitrogen implant, or grow a "
            "delta-doped layer instead (R18).",
            "4. Etch and pattern on shared cleanroom tools of the class the Atlas prices (R21, R22; Atlas M11 to M16).",
            "5. Build hydrogen-terminated FETs with ALD Al₂O₃ as published (R23), and bond dies to silicon at room temperature (R24).",
            "6. Benchmark against products already sold (scanning NV microscopes, quantum-grade diamond, teaching instruments).", "",
            f"Sources: {_cite(s['keys'])}", ""]
    return "\n".join(out)


def write(path: str = "docs/process/RETROFIT.md") -> str:
    p = ROOT / path; p.write_text(to_markdown(), encoding="utf-8"); return str(p)


def figure(out: str | Path = "docs/img") -> Path:
    """Figure 62: the Retrofit Map, one row per build stage, one dot per route colored by maturity, plus the products."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(15, 6.4), gridspec_kw={"width_ratios": [2.0, 1.3]})
    names = [f"{k} {n}" for k, n, _ in STAGES][::-1]
    for i, (k, _, _) in enumerate(STAGES[::-1]):
        rs = routes(k)
        best = stage_level(k)
        ax.barh(i, len(rs), color=COLORS[best], alpha=0.18, height=0.8)
        for j, r in enumerate(sorted(rs, key=lambda r: LEVELS.index(r["level"]))):
            ax.scatter(j + 0.5, i, s=230, color=COLORS[r["level"]], edgecolor="black", linewidth=0.6, zorder=3)
            ax.text(j + 0.5, i, r["id"][1:], ha="center", va="center", fontsize=6.5, zorder=4)
    ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel("routes (number = route id in RETROFIT.md)"); ax.set_xlim(0, max(len(routes(k)) for k, _, _ in STAGES) + 3.2)
    ax.set_title("Real processes for each build stage, by maturity")
    for lv in LEVELS:
        ax.scatter([], [], s=80, color=COLORS[lv], edgecolor="black", label=LEVEL_TEXT[lv])
    ax.legend(loc="lower right", fontsize=8, frameon=True)
    ps = products()[::-1]
    for i, p in enumerate(ps):
        bx.scatter(0.04, i, s=160, color=COLORS[p["level"]], edgecolor="black", linewidth=0.6, clip_on=False)
        bx.text(0.09, i, f"{p['device']}  {p['name']}", va="center", fontsize=8)
    bx.set_xlim(0, 1); bx.set_ylim(-0.7, len(ps) - 0.3); bx.axis("off")
    bx.set_title("NV devices sold or deployed today (by device type)")
    fig.text(0.01, 0.01, "Sources: docs/process/RETROFIT.md (adamas.retrofit); company statements are marked there. "
             "Retrofit = proven on silicon, SiC or GaN, proposed for diamond.", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    p = out / "fig62_retrofit_map.png"; fig.savefig(p, dpi=150); plt.close(fig)
    return p
