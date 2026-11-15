"""Machines and Facilities Atlas: what each machine M00 to M59 (adamas.atlas) costs, where it lives, and how you get it.

Every entry has exactly one price kind, and the kind is printed next to the number:
  sourced    a number read from a published rate sheet or store page, with its reference key; the page and the date it
             was read are in references/refs_m.psv. Facility rates are per hour of tool time and depend on who you are
             (academic or industry), so both are given where the page gives both.
  estimate   the sum of part-price ranges from the experiment parts lists (adamas.experiments), which are reviewer
             estimates of 2026 street prices, not vendor quotes.
  included   priced inside another machine's estimate (named).
  unpriced   no published price was found; the reason says why and what would price it.
A sourced row can price only part of a machine (PARTIAL names what is left out), or the closest published tool (SUBSTITUTE).
No prices are converted between currencies or summed across kinds, because no exchange rate or quote is sourced here.
Most shared-facility rates are hourly: the cost of a phase depends on hours of tool time, which this module does not
guess. adamas build docs writes docs/build/ATLAS.md from this module.
"""
from __future__ import annotations

from pathlib import Path

from .atlas import ATLAS

ROOT = Path(__file__).resolve().parents[1]
READ_ON = "10 November 2026"     # the date the v0.40.0 pages were read
READ_ON_2 = "15 November 2026"   # the date the v0.43.0 pages were read (and the extra lines of ccmr2026 and wnf2026)

# Where the machine lives and how a group gets time on it.
FACILITY = {
    "computer": "Any computer",
    "desk": "Desk or kitchen table (tier A experiments)",
    "teaching": "Teaching laboratory (tier B)",
    "research": "Research laboratory (tier C)",
    "cleanroom": "University cleanroom, hourly tool rates",
    "characterization": "Shared characterization facility, hourly rates",
    "ion beam": "Ion-beam facility, hourly rates",
    "shuttle": "Multi-project wafer (MPW) shuttle service",
    "growth": "Diamond growth and wafering laboratory or fab",
    "application": "Application facility (test bench; shielded room; irradiation; vehicle)",
}
ACCESS = {"buy": "buy", "hourly": "hourly user rate", "service": "pay per design or per run", "partner": "partner or facility access"}

# Sourced: id -> list of quotes (reference key, tool as the page names it, currency, unit, {user category: price}, note)
SOURCED: dict[str, list[tuple[str, str, str, str, dict, str]]] = {
    "M06": [("maf2023", "Raman", "USD", "hour", {"academic": 34, "outside academic": 40, "industry": 126}, ""),
            ("ccmr2026", "WITec Alpha300R / Renishaw InVia Raman", "USD", "hour", {"Cornell internal": 49.95}, "")],
    "M07": [("maf2023", "XRD", "USD", "hour", {"academic": 55, "outside academic": 64, "industry": 200}, ""),
            ("ccmr2026", "Rigaku SmartLab XRD", "USD", "hour", {"Cornell internal": 51.00}, "")],
    "M04": [("gatechims2025", "Laser Machining Lab, class 1, 2 and 3 tools", "USD", "hour",
             {"Georgia Tech and US academic, class 1": 28, "Georgia Tech and US academic, class 2": 39, "Georgia Tech and US academic, class 3": 50,
              "foreign academic and industry, class 1": 47, "foreign academic and industry, class 2": 53, "foreign academic and industry, class 3": 51},
             "femtosecond laser machining of glass, sapphire and metal; the page does not say which tool is in which class and does not mention diamond")],
    "M05": [("ccmr2026", "Allied Multiprep Polishers", "USD", "hour", {"Cornell internal": 33.99}, "metallographic polisher"),
            ("ccmr2026", "Struers Rotopol", "USD", "hour", {"Cornell internal": 36.40}, "metallographic polisher"),
            ("aggiefab2025", "G&P CMP", "USD", "hour", {"Texas A&M": 55}, "chemical-mechanical polisher; outside academic users pay 150 % and industry 300 % of the listed rate (the page prints no dollar figure for them)")],
    "M08": [("cunyasrc2024", "FLS1000 Photoluminescence Lifetime Spectrometer; Micro-Photoluminescence Setup", "USD", "hour",
             {"CUNY": 20, "outside academic": 30, "start-up": 60, "industrial": 120}, "the same rate for each tool; no photoluminescence mapping tool is listed"),
            ("ccmr2026", "Edinburgh FLS1000 Fluorescence and Lifetime Spectrometer", "USD", "hour", {"Cornell internal": 41.70}, "US$10.50 minimum charge")],
    "M09": [("wnf2026", "Microscopes", "USD", "hour", {"academic (UW and non-UW)": 13, "industry": 38}, "the sheet does not say whether polarizing optics are fitted")],
    "M10": [("wnf2026", "Wet Bench / Solvent Bench", "USD", "hour", {"academic (UW and non-UW)": 13, "industry": 38}, "")],
    "M11": [("wnf2026", "Contact Aligner", "USD", "hour", {"academic (UW and non-UW)": 63, "industry": 189}, ""),
            ("wnf2026", "Heidelberg Direct Write", "USD", "hour", {"academic (UW and non-UW)": 38, "industry": 114}, "maskless laser writer")],
    "M12": [("wnf2026", "E-beam Lithography", "USD", "hour", {"academic (UW and non-UW)": 158, "industry": 569}, "the facility applies a separate yearly cap to e-beam hours")],
    "M13": [("wnf2026", "E-beam Evaporator", "USD", "hour", {"academic (UW and non-UW)": 89, "industry": 267}, "")],
    "M14": [("wnf2026", "ALD", "USD", "hour", {"academic (UW and non-UW)": 38, "industry": 114}, "")],
    "M15": [("wnf2026", "Plasma Asher", "USD", "hour", {"academic (UW and non-UW)": 63, "industry": 189}, "")],
    "M16": [("wnf2026", "DRIE/RIE/ICP", "USD", "hour", {"academic (UW and non-UW)": 89, "industry": 267}, "")],
    "M17": [("wnf2026", "Probe Station", "USD", "hour", {"academic (UW and non-UW)": 38, "industry": 114}, "the rate sheet lists no separate parameter analyzer or hot chuck")],
    "M18": [("asuaep2026", "Keysight B1505A Power Device Analyzer/Curve Tracer", "USD", "hour", {"ASU": 44, "nonprofit and academic": 55},
             "listed for packaged discrete devices; the rate page states no voltage range")],
    "M19": [("wnf2026", "Stylus / Optical Profilometer", "USD", "hour", {"academic (UW and non-UW)": 63, "industry": 189}, "profilometer only"),
            ("maf2023", "Profilometer", "USD", "hour", {"academic": 22, "outside academic": 26, "industry": 126}, "")],
    "M20": [("mibl2024", "BLUE 400 kV implanter", "USD", "hour", {"University of Michigan": 51, "other universities": 102, "businesses": 204},
             "set-up is charged at the same rate, with a 4 hour minimum per ion beam and experiment; a research implanter, not a dedicated low-energy ¹⁵N tool")],
    "M21": [("maf2023", "FIB", "USD", "hour", {"academic": 55, "outside academic": 64, "industry": 200}, "focused ion beam only; aperture masks are made with M12"),
            ("ccmr2026", "Thermo Helios G4 UX FIB", "USD", "hour", {"Cornell internal": 116.35}, "")],
    "M22": [("wnf2026", "RTA", "USD", "hour", {"academic (UW and non-UW)": 63, "industry": 189}, "closest listed tool: rapid thermal anneal, not a high-vacuum 1200 °C furnace")],
    "M23": [("maf2023", "ToF-SIMS", "USD", "hour", {"academic": 90, "outside academic": 100, "industry": 225},
             "time-of-flight SIMS; depth profiles of implanted nitrogen are often done on dynamic SIMS, which is not priced here")],
    "M24": [("maf2023", "AFM", "USD", "hour", {"academic": 22, "outside academic": 26, "industry": 126}, ""),
            ("ccmr2026", "Asylum MFP3D AFM", "USD", "hour", {"Cornell internal": 49.40}, "")],
    "M26": [("wnf2026", "Wafer Bonder", "USD", "hour", {"academic (UW and non-UW)": 89, "industry": 267}, "wafer bonder; no die or flip-chip bonder rate was found")],
    "M27": [("wnf2026", "Dicing Saw", "USD", "hour", {"academic (UW and non-UW)": 63, "industry": 189}, "saw only; laser dicing is not priced")],
    "M28": [("wnf2026", "Wire Bonder", "USD", "hour", {"academic (UW and non-UW)": 63, "industry": 189}, "packages not included")],
    "M29": [("tinytapeout2026", "sky130A tile", "EUR", "tile", {"per tile": 70}, "analog designs need at least two tiles (140 EUR) plus 40 EUR per analog pin for the first two and 100 EUR per pin after that; "
             "covers inclusion on the shuttle only, not the chip, board or shipping"),
            ("europractice2026", "X-FAB XH018 0.18 µm, 4 metal layers, E-FLASH", "EUR", "mm²", {"discounted (eligible EUROPRACTICE members)": 1080, "standard": 1126},
             "basic offering, optional modules cost extra; minimum charge equivalent to 10 mm² (XH018_MIN_MM2); area rounded up to the next mm²; VAT treatment not stated on the page")],
    "M31": [("lattispec2026", "High NV content plate, 3.2 × 2.4 × 1.2 mm, HPHT type Ib", "USD", "plate", {"list": 510}, "")],
    "M52": [("e6cvd2026", "EL SC plate 2.0 × 2.0 × 0.5 mm (145-500-0385)", "USD", "plate", {"regular": 865, "special (sale)": 565}, "electronic grade; isotope content not stated on the page"),
            ("e6cvd2026", "EL SC plate 4.0 × 4.0 × 0.5 mm (145-500-0389)", "USD", "plate", {"regular": 2545, "special (sale)": 1730}, "¹²C-enriched plates are not priced on the page")],
    "M53": [("srs2026", "DS345 30 MHz function generator", "USD", "instrument", {"base price": 2595}, "the page prints 'from'; options cost extra"),
            ("rigolna2026", "DG1022Z 25 MHz two-channel function generator", "USD", "instrument", {"price shown": 389}, "")],
    "M54": [("edmundoptics2026", "594 nm yellow HeNe laser, 1.3 mW, linearly polarized (#28-062)", "GBP", "laser", {"list, excluding VAT": 4234}, "UK store"),
            ("edmundoptics2026", "635 nm 4 mW circular laser diode (#57-106)", "GBP", "diode", {"list, excluding VAT": 212}, "UK store; diode module only")],
    "M55": [("srs2026", "SR860 500 kHz lock-in amplifier", "USD", "instrument", {"base price": 6495}, "the page prints 'from'"),
            ("srs2026", "SR570 low-noise current preamplifier", "USD", "instrument", {"base price": 3395}, "transimpedance amplifier; the page prints 'from'")],
    "M56": [("transcat2026", "GW Instek GPM-8213G digital AC power meter with GPIB", "USD", "instrument", {"price shown": 1156}, "reseller; a power meter, not a multichannel power analyzer; tariff surcharges may apply"),
            ("infraredcameras2026", "FLIR E8 Pro thermal camera", "USD", "camera", {"regular price": 3249}, "reseller; shown sold out when read"),
            ("element14sg2026", "Infineon EVALDCLINKDPTTOBO1 800 V double-pulse test board", "SGD", "board", {"excluding GST": 661.05}, "reseller; the device-under-test board only, not a complete tester")],
    "M57": [("osurc2023", "Gamma Irradiator Use (Cobalt-60)", "USD", "run", {"OSU internal": 179, "external": 188}, "includes staff time; sheet for 1 July 2023 to 30 June 2024, no newer sheet was found"),
            ("umdrad2025", "Irradiator", "USD", "hour", {"listed rate": 550}, "2 hour minimum, 150 % off hours; university and government discounts not printed; the facility describes a panoramic cobalt-60 irradiator")],
    "M58": [("aalto2025", "DC (shielded room in Magnet House 4th floor)", "EUR", "hour", {"all users, VAT 0 %": 40}, "a magnetically shielded room for hourly use"),
            ("twinleaf2026", "MS-1L four-layer magnetic shield", "USD", "shield", {"price shown": 7996}, "benchtop shield, 30 mm bore; not a room"),
            ("twinleaf2026", "MS-2 four-layer magnetic shield", "USD", "shield", {"price shown": 14390}, "benchtop shield, 46 mm bore; not a room"),
            ("quspin2026", "QZFM Gen-3 zero-field optically pumped magnetometer", "USD", "sensor",
             {"1 to 3 sensors, each": 10000, "4 to 7, each": 8500, "8 to 15, each": 8000, "16 to 32, each": 7700}, "for a gradiometer, two or more sensors; triaxial option US$1,250 more per sensor")],
}

# Sourced rows that price only part of the machine: id -> what is not priced.
PARTIAL = {
    "M09": "the furnace or etch for etch-pit counting",
    "M53": "the RF amplifier and the coil",
    "M54": "the laser-diode driver, mounts and optics",
    "M55": "the bias electrodes, which are made on M11 to M13 and priced there",
    "M56": "a complete double-pulse tester (none with a published price was found)",
    "M57": "proton beam time (the facilities checked quote it on request)",
}

XH018_MIN_MM2 = 10          # EUROPRACTICE minimum charge for X-FAB XH018, in mm² [europractice2026]

# Facility access fees from the same rate sheet; they come on top of hourly tool rates.
ACCESS_FEES = [("wnf2026", "Monthly access fee", "USD", "month", {"academic (UW and non-UW)": 127, "industry (full)": 127, "industry (fixed)": 6325}),
               ("wnf2026", "Academic monthly cap on equipment use and access fees", "USD", "month", {"academic": 2500})]
WNF_NOTCH_USD = 5000        # above this monthly charge, WNF tools are billed at WNF_ABOVE_NOTCH_PCT of the hourly rate [wnf2026]
WNF_ABOVE_NOTCH_PCT = 33

WNF_OVERHEAD_PCT = 15.6     # overhead on WNF rates for users outside the University of Washington [wnf2026]

# Estimate: id -> [(experiment id, part name)]; the ranges are read from adamas.experiments at run time.
ESTIMATE = {
    "M30": [("A1", "Green source")], "M31": [("A1", "NV-rich diamond")], "M32": [("A1", "Red filter")], "M33": [("A1", "Photodetector")],
    "M34": [("A1", "Microwave source")], "M35": [("A1", "Antenna")], "M36": [("A1", "Controller")],
    "M37": [("A1", "Mechanics"), ("A3", "Heater"), ("A3", "Temperature sensors")],
    "M38": [("B1", "532 nm laser")], "M40": [("B1", "Photodetector")], "M41": [("B1", "Microwave chain")], "M42": [("B1", "Pulse timing")],
    "M43": [("B2", "Helmholtz coil set"), ("B2", "Current supplies")], "M44": [("B3", "Hot stage")],
    "M45": [("B3", "Source-measure unit or precision source + meter")], "M46": [("B1", "Optics")],
    "M47": [("C1", "Oil or air objective")], "M48": [("C1", "Scanning")], "M49": [("C1", "Single-photon detectors")], "M50": [("C1", "Time tagger")],
    "M51": [("C1", "Microwave and control")], "M52": [("C1", "Electronic-grade diamond")],
}
# Machines priced by a published tool that is not the same as the Atlas tool; the note on the quote says how it differs.
SUBSTITUTE = {"M04", "M05", "M08", "M09", "M17", "M20", "M22", "M23", "M26"}

# Effective date of each sourced page as the page states it, and the date it was read.
EFFECTIVE = {"wnf2026": "effective 1 March 2026", "maf2023": "effective 1 September 2023", "ccmr2026": "fiscal year 2027, from 1 July 2026",
             "mibl2024": "from 1 September 2024", "tinytapeout2026": "no date shown", "europractice2026": "2026 schedule",
             "e6cvd2026": "no date shown", "lattispec2026": "no date shown",
             "gatechims2025": "effective 1 September 2025", "aggiefab2025": "effective 1 October 2025", "cunyasrc2024": "effective 1 July 2024",
             "asuaep2026": "no date shown", "osurc2023": "1 July 2023 to 30 June 2024", "umdrad2025": "effective 1 July 2025 (2026-2027 fee schedule)",
             "aalto2025": "page updated 8 January 2025", "srs2026": "no date shown", "rigolna2026": "no date shown", "edmundoptics2026": "no date shown",
             "transcat2026": "no date shown", "infraredcameras2026": "no date shown", "element14sg2026": "no date shown", "twinleaf2026": "no date shown",
             "quspin2026": "no date shown"}
READ = {k: (READ_ON_2 if k in {"gatechims2025", "aggiefab2025", "cunyasrc2024", "asuaep2026", "osurc2023", "umdrad2025", "aalto2025", "srs2026",
                               "rigolna2026", "edmundoptics2026", "transcat2026", "infraredcameras2026", "element14sg2026", "twinleaf2026", "quspin2026"}
            else READ_ON + (" and " + READ_ON_2 if k in {"ccmr2026", "wnf2026"} else "")) for k in EFFECTIVE}

NO_COST = {"M00": "a computer the user already has; every listed tool is open source"}
INCLUDED = {"M39": ("M38", "the B1 laser line item includes an acousto-optic modulator or direct modulation")}

UNPRICED = {
    "M01": "no MPCVD reactor maker publishes a price; the D2 experiment's line item for several reactors is an estimate, not a per-reactor price",
    "M02": "no HPHT press price is published; type Ib plates are sold (e6cvd.com) but the page does not state the growth method",
    "M03": "heteroepitaxy stacks (iridium on YSZ, bias-enhanced nucleation) are made in research groups; no service price is published",
    "M25": "laser writing of vacancies is done in a few research groups; no service price exists",
    "M59": "a test vehicle and a magnetic-anomaly map; no published rental or survey price was found",
}

PLACE = {**{f"M{i:02d}": ("desk", "buy") for i in range(30, 38)}, **{f"M{i:02d}": ("teaching", "buy") for i in range(38, 47)},
         **{f"M{i:02d}": ("research", "buy") for i in range(47, 56)},
         **{m: ("cleanroom", "hourly") for m in ("M10", "M11", "M12", "M13", "M14", "M15", "M16", "M17", "M18", "M19", "M22", "M26", "M27", "M28")},
         **{m: ("characterization", "hourly") for m in ("M06", "M07", "M08", "M09", "M21", "M23", "M24")},
         **{m: ("growth", "partner") for m in ("M01", "M02", "M03", "M04", "M05")},
         **{m: ("application", "partner") for m in ("M56", "M57", "M58", "M59")},
         "M00": ("computer", "buy"), "M20": ("ion beam", "hourly"), "M25": ("research", "partner"), "M29": ("shuttle", "service"),
         "M31": ("desk", "buy"), "M52": ("research", "buy")}


KINDS = ("sourced", "estimate", "included", "no cost", "unpriced")


def _part(exp: str, name: str) -> tuple[int, int]:
    from .experiments import EXPERIMENTS
    e = next(x for x in EXPERIMENTS if x["id"] == exp)
    p = next(p for p in e["parts"] if p[0] == name)        # StopIteration if a parts list was renamed
    return p[2], p[3]


def phases_using(atlas_id: str) -> list[str]:
    """Build phases that name this machine: the outline's phase column (adamas.atlas) and the P3 to P8 machine lists."""
    from . import build_program as B
    used = {p.strip() for p in ATLAS[atlas_id][1].replace(",", " ").split() if p.strip().startswith("P") and p.strip()[1:].isdigit()}
    for ph in ("P3", "P4", "P5", "P6", "P7", "P8"):
        if atlas_id in getattr(B, f"{ph}_MACHINES"):
            used.add(ph)
    return sorted(used, key=lambda s: int(s[1:]))


def entry(atlas_id: str) -> dict:
    """The Atlas row for one machine: facility, access, price kind, and the price itself."""
    fac, acc = PLACE[atlas_id]
    row = {"id": atlas_id, "tool": ATLAS[atlas_id][0], "facility": fac, "access": acc, "phases": phases_using(atlas_id)}
    if atlas_id in SOURCED:
        quotes = [{"key": k, "effective": EFFECTIVE[k], "read_on": READ[k], "listed_as": t, "currency": c, "unit": u, "prices": p, "note": n} for k, t, c, u, p, n in SOURCED[atlas_id]]
        row.update(kind="sourced", quotes=quotes, substitute=atlas_id in SUBSTITUTE, partial=PARTIAL.get(atlas_id, ""))
        if atlas_id in ESTIMATE:                            # a sourced price wins; the estimate stays visible for comparison
            row["estimate"] = _estimate(atlas_id)
    elif atlas_id in ESTIMATE:
        row.update(kind="estimate", estimate=_estimate(atlas_id))
    elif atlas_id in NO_COST:
        row.update(kind="no cost", reason=NO_COST[atlas_id])
    elif atlas_id in INCLUDED:
        row.update(kind="included", within=INCLUDED[atlas_id][0], reason=INCLUDED[atlas_id][1])
    else:
        row.update(kind="unpriced", reason=UNPRICED[atlas_id])
    return row


def _estimate(atlas_id: str) -> dict:
    parts = [(e, n, *_part(e, n)) for e, n in ESTIMATE[atlas_id]]
    return {"usd_low": sum(p[2] for p in parts), "usd_high": sum(p[3] for p in parts), "from": [f"{e}: {n}" for e, n, _, _ in parts]}


def short_price(atlas_id: str) -> str:
    """One-cell price for the phase pages: the first sourced quote's range with its key, or 'not priced'."""
    if atlas_id not in SOURCED:
        return "not priced (no source yet; see the [Atlas](ATLAS.md))"
    k, t, c, u, p, _ = SOURCED[atlas_id][0]; lo, hi = min(p.values()), max(p.values())
    rng = _money(c, lo) if lo == hi else f"{_money(c, lo)} to {_money(c, hi).replace('US$', '')}"
    near = " (closest listed tool, not the same)" if atlas_id in SUBSTITUTE else ""
    extra = f"; users outside the University of Washington add {WNF_OVERHEAD_PCT} %" if k == "wnf2026" else ""
    part = f"; not priced: {PARTIAL[atlas_id]}" if atlas_id in PARTIAL else ""
    return f"{rng} per {u}, {t}{near} [{k}]{extra}{part} ([Atlas](ATLAS.md))"


def mpw_prices() -> str:
    """The M29 shuttle prices as one phrase, for the P6 page."""
    (k1, _, c1, _, p1, _), (k2, t2, c2, u2, p2, _) = SOURCED["M29"]
    lo, hi = min(p2.values()), max(p2.values())
    return (f"{p1['per tile']} {c1} per Tiny Tapeout tile [{k1}]; {lo:,} to {hi:,} {c2}/{u2} for {t2} "
            f"through EUROPRACTICE, minimum {XH018_MIN_MM2} mm² [{k2}]")


def rows() -> list[dict]:
    return [entry(i) for i in ATLAS]


def summary() -> dict:
    r = rows(); kinds = KINDS
    by_phase = {}
    for ph in [f"P{i}" for i in range(9)]:
        ids = [x for x in r if ph in x["phases"]]
        by_phase[ph] = {k: sum(x["kind"] == k for x in ids) for k in kinds} | {"machines": len(ids)}
    return {"machines": len(r), **{k: sum(x["kind"] == k for x in r) for k in kinds}, "by_phase": by_phase,
            "keys": sorted({q["key"] for x in r for q in x.get("quotes", [])} | {f[0] for f in ACCESS_FEES})}


def _money(cur: str, v: float) -> str:
    s = f"{v:,.2f}" if v != int(v) else f"{int(v):,}"
    return f"US${s}" if cur == "USD" else f"{s} {cur}"


def _price_cell(x: dict) -> str:
    if x["kind"] == "sourced":
        out = []
        for q in x["quotes"]:
            p = ", ".join(f"{_money(q['currency'], v)} {k}" for k, v in q["prices"].items())
            out.append(f"{q['listed_as']}: {p} per {q['unit']} [{q['key']}]" + (f" ({q['note']})" if q["note"] else ""))
        return (("**Closest listed tool, not the same:** " if x["substitute"] else "") + "; ".join(out)
                + (f". **Not priced:** {x['partial']}" if x["partial"] else ""))
    if x["kind"] == "estimate":
        e = x["estimate"]; return f"US${e['usd_low']:,} to {e['usd_high']:,}, estimate from {', '.join(e['from'])}"
    if x["kind"] == "included":
        return f"in {x['within']}: {x['reason']}"
    if x["kind"] == "no cost":
        return f"no cost: {x['reason']}"
    return f"unpriced: {x['reason']}"


def to_markdown() -> str:
    s = summary(); r = rows()
    table = "\n".join(f"| {x['id']} | {x['tool']} | {FACILITY[x['facility']].split(',')[0]} | {ACCESS[x['access']]} | {', '.join(x['phases']) or '—'} | **{x['kind']}** | {_price_cell(x)} |" for x in r)
    fees = "\n".join(f"- {t}: " + ", ".join(f"{_money(c, v)} {k}" for k, v in p.items()) + f" per {u} [{key}]" for key, t, c, u, p in ACCESS_FEES)
    phase = "\n".join(f"| {ph} | {v['machines']} | " + " | ".join(str(v[k]) for k in KINDS) + " |" for ph, v in s["by_phase"].items())
    srcs = "\n".join(f"- [{k}]: {EFFECTIVE[k]}; read on {READ[k]}" for k in s["keys"])
    return f"""# Machines and Facilities Atlas

*Generated by `adamas build docs` from `adamas/atlas_prices.py`; do not edit by hand.*

Every machine the build program names (M00 to M59, from the outline), where it lives, how a group gets it, which phases
use it, and what it costs. Each price carries its kind:

- **sourced**: read from a published rate sheet or store page on the date listed under Sources (the reference gives
  the page). Rates and list prices change; check the page before you budget. Store prices exclude tax and shipping
  unless the row says otherwise.
- **estimate**: the sum of part-price ranges from the experiment parts lists (`adamas.experiments`), which are
  reviewer estimates of 2026 street prices, not quotes.
- **included**: priced inside another machine's line.
- **no cost**: nothing to buy (open-source software on a computer you have).
- **unpriced**: no published price was found; the reason says why.

Of {s['machines']} machines: {s['sourced']} sourced, {s['estimate']} estimate, {s['included']} included, {s['no cost']} no cost, {s['unpriced']} unpriced.
{len(SUBSTITUTE)} of the sourced rows ({', '.join(sorted(SUBSTITUTE))}) are priced by the closest published tool, which is not the
same tool; their notes say how it differs. {len(PARTIAL)} ({', '.join(sorted(PARTIAL))}) price only part of the machine and say what
is left out.
Prices are not converted between currencies and not summed: most cleanroom and characterization prices are **per hour
of tool time**, and the hours a phase needs are not modelled here. Hourly rates differ several-fold between academic and
industry users, and between facilities (compare the two characterization sources below).

## Access fees

Shared cleanrooms also charge for access, on top of tool hours:

{fees}

The same sheet adds {WNF_OVERHEAD_PCT} % overhead to the listed rates for users outside the University of Washington, and
above a monthly charge of US${WNF_NOTCH_USD:,} bills tools at {WNF_ABOVE_NOTCH_PCT} % of the hourly rate [wnf2026].

## Coverage by phase

| Phase | Machines | Sourced | Estimate | Included | No cost | Unpriced |
|---|---|---|---|---|---|---|
{phase}

## Atlas

| ID | Machine | Facility | Access | Phases | Kind | Price |
|---|---|---|---|---|---|---|
{table}

## What would price the rest

- **Growth (M01 to M03):** quotes from reactor and press makers, and a heteroepitaxy partner; none publish prices.
- **Laser writing of vacancies (M25):** a research-group collaboration; no service exists.
- **Navigation platform (M59):** a vehicle and a magnetic-anomaly survey, to be quoted.
- **Closest-tool rows (M04, M05, M08, M09):** a rate sheet that names the diamond tool itself: laser cutting of
  diamond, scaife or diamond polishing, photoluminescence mapping, a polarizing microscope.
- **Partly priced rows:** the parts named in each row (for example proton beam time for M57).
- **Lab optics and detectors:** vendor list prices (objectives, single-photon detectors, time taggers) to replace the
  estimates; the vendors checked either do not publish prices or did not show them to an automated reader.

## Sources and the dates they state

{srcs}

Sources: {' '.join(f'[{k}]' for k in s['keys'])}
"""


def write(path: str = "docs/build/ATLAS.md") -> str:
    p = ROOT / path; p.write_text(to_markdown(), encoding="utf-8"); return str(p)


def to_json() -> dict:
    return {"rows": rows(), "summary": summary(), "kinds": KINDS, "effective": EFFECTIVE, "facility": FACILITY, "access": ACCESS, "read_on": READ,
            "access_fees": [{"key": k, "listed_as": t, "currency": c, "unit": u, "prices": p} for k, t, c, u, p in ACCESS_FEES]}
