"""Machines and Facilities Atlas: what each machine M00 to M59 (adamas.atlas) costs, where it lives, and how you get it.

Every entry has exactly one price kind, and the kind is printed next to the number:
  sourced    a number read from a published rate sheet or store page, with its reference key; the page and the date it
             was read are in references/refs_m.psv. Facility rates are per hour of tool time and depend on who you are
             (academic or industry), so both are given where the page gives both.
  estimate   the sum of part-price ranges from the experiment parts lists (adamas.experiments), which are reviewer
             estimates of 2026 street prices, not vendor quotes.
  included   priced inside another machine's estimate (named).
  unpriced   no published price was found; the reason says why and what would price it.
No prices are converted between currencies or summed across kinds, because no exchange rate or quote is sourced here.
Most shared-facility rates are hourly: the cost of a phase depends on hours of tool time, which this module does not
guess. adamas build docs writes docs/build/ATLAS.md from this module.
"""
from __future__ import annotations

from pathlib import Path

from .atlas import ATLAS

ROOT = Path(__file__).resolve().parents[1]
READ_ON = "10 November 2026"     # the date every sourced page below was read

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
    "application": "Application facility (test bench, shielded room, irradiation, vehicle)",
}
ACCESS = {"buy": "buy", "hourly": "hourly user rate", "service": "pay per design or per run", "partner": "partner or facility access"}

# Sourced: id -> list of quotes (reference key, tool as the page names it, currency, unit, {user category: price}, note)
SOURCED: dict[str, list[tuple[str, str, str, str, dict, str]]] = {
    "M06": [("maf2023", "Raman", "USD", "hour", {"academic": 34, "outside academic": 40, "industry": 126}, ""),
            ("ccmr2026", "WITec Alpha300R / Renishaw InVia Raman", "USD", "hour", {"Cornell internal": 49.95}, "")],
    "M07": [("maf2023", "XRD", "USD", "hour", {"academic": 55, "outside academic": 64, "industry": 200}, ""),
            ("ccmr2026", "Rigaku SmartLab XRD", "USD", "hour", {"Cornell internal": 51.00}, "")],
    "M10": [("wnf2026", "Wet Bench / Solvent Bench", "USD", "hour", {"academic (UW and non-UW)": 13, "industry": 38}, "")],
    "M11": [("wnf2026", "Contact Aligner", "USD", "hour", {"academic (UW and non-UW)": 63, "industry": 189}, ""),
            ("wnf2026", "Heidelberg Direct Write", "USD", "hour", {"academic (UW and non-UW)": 38, "industry": 114}, "maskless laser writer")],
    "M12": [("wnf2026", "E-beam Lithography", "USD", "hour", {"academic (UW and non-UW)": 158, "industry": 569}, "the facility applies a separate yearly cap to e-beam hours")],
    "M13": [("wnf2026", "E-beam Evaporator", "USD", "hour", {"academic (UW and non-UW)": 89, "industry": 267}, "")],
    "M14": [("wnf2026", "ALD", "USD", "hour", {"academic (UW and non-UW)": 38, "industry": 114}, "")],
    "M15": [("wnf2026", "Plasma Asher", "USD", "hour", {"academic (UW and non-UW)": 63, "industry": 189}, "")],
    "M16": [("wnf2026", "DRIE/RIE/ICP", "USD", "hour", {"academic (UW and non-UW)": 89, "industry": 267}, "")],
    "M17": [("wnf2026", "Probe Station", "USD", "hour", {"academic (UW and non-UW)": 38, "industry": 114}, "the rate sheet lists no separate parameter analyzer or hot chuck")],
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
SUBSTITUTE = {"M17", "M20", "M22", "M23", "M26"}

# Effective date of each sourced page as the page states it (all were read on READ_ON).
EFFECTIVE = {"wnf2026": "effective 1 March 2026", "maf2023": "effective 1 September 2023", "ccmr2026": "fiscal year 2027, from 1 July 2026",
             "mibl2024": "from 1 September 2024", "tinytapeout2026": "no date shown", "europractice2026": "2026 schedule",
             "e6cvd2026": "no date shown", "lattispec2026": "no date shown"}

NO_COST = {"M00": "a computer the user already has; every listed tool is open source"}
INCLUDED = {"M39": ("M38", "the B1 laser line item includes an acousto-optic modulator or direct modulation")}

UNPRICED = {
    "M01": "no MPCVD reactor maker publishes a price; the D2 experiment's line item for several reactors is an estimate, not a per-reactor price",
    "M02": "no HPHT press price is published; type Ib plates are sold (e6cvd.com) but the page does not state the growth method",
    "M03": "heteroepitaxy stacks (iridium on YSZ, bias-enhanced nucleation) are made in research groups; no service price is published",
    "M04": "no published service rate for laser cutting of diamond was found",
    "M05": "no published service rate for diamond polishing was found",
    "M08": "no published hourly rate for photoluminescence or NV-density mapping was found",
    "M09": "birefringence imaging and etch-pit counting use a polarizing microscope and a furnace; no rate was sourced",
    "M18": "no published hourly rate for a high-voltage curve tracer was found",
    "M25": "laser writing of vacancies is done in a few research groups; no service price exists",
    "M53": "not in any experiment parts list; a MHz signal generator and coil, to be quoted",
    "M54": "not in any experiment parts list; an orange or red laser line, to be quoted",
    "M55": "not in any experiment parts list; electrodes are made on M11 to M13, the lock-in and amplifier need quotes",
    "M56": "application test bench; P8 lists it without a sourced price",
    "M57": "irradiation time at licensed facilities; P8 lists it without a sourced price",
    "M58": "magnetically shielded room; P8 lists it without a sourced price",
    "M59": "vehicle and magnetic-anomaly map; P8 lists it without a sourced price",
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
        quotes = [{"key": k, "effective": EFFECTIVE[k], "listed_as": t, "currency": c, "unit": u, "prices": p, "note": n} for k, t, c, u, p, n in SOURCED[atlas_id]]
        row.update(kind="sourced", quotes=quotes, substitute=atlas_id in SUBSTITUTE)
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
    return f"{rng} per {u}, {t}{near} [{k}]{extra} ([Atlas](ATLAS.md))"


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
        return ("**Closest listed tool, not the same:** " if x["substitute"] else "") + "; ".join(out)
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
    srcs = "\n".join(f"- [{k}]: {EFFECTIVE[k]}" for k in s["keys"])
    return f"""# Machines and Facilities Atlas

*Generated by `adamas build docs` from `adamas/atlas_prices.py`; do not edit by hand.*

Every machine the build program names (M00 to M59, from the outline), where it lives, how a group gets it, which phases
use it, and what it costs. Each price carries its kind:

- **sourced**: read from a published rate sheet or store page on {READ_ON} (the reference gives the page). Rates
  change every fiscal year; check the page before you budget.
- **estimate**: the sum of part-price ranges from the experiment parts lists (`adamas.experiments`), which are
  reviewer estimates of 2026 street prices, not quotes.
- **included**: priced inside another machine's line.
- **no cost**: nothing to buy (open-source software on a computer you have).
- **unpriced**: no published price was found; the reason says why.

Of {s['machines']} machines: {s['sourced']} sourced, {s['estimate']} estimate, {s['included']} included, {s['no cost']} no cost, {s['unpriced']} unpriced.
{len(SUBSTITUTE)} of the sourced rows ({', '.join(sorted(SUBSTITUTE))}) are priced by the closest published tool, which is not the
same tool; their notes say how it differs.
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

- **Growth (M01 to M05):** quotes from reactor makers and diamond polishing services; none publish prices.
- **Characterization gaps (M08, M09, M18):** a facility rate sheet that lists photoluminescence mapping, birefringence
  imaging and high-voltage curve tracing.
- **Application facilities (M56 to M59):** test-bench, shielded-room and irradiation-time quotes (see P8).
- **Lab optics and detectors:** vendor list prices (objectives, single-photon detectors, time taggers) to replace the
  estimates; the vendors checked either do not publish prices or did not show them to an automated reader.

## Sources and the dates they state

{srcs}

All were read on {READ_ON}.

Sources: {' '.join(f'[{k}]' for k in s['keys'])}
"""


def write(path: str = "docs/build/ATLAS.md") -> str:
    p = ROOT / path; p.write_text(to_markdown(), encoding="utf-8"); return str(p)


def to_json() -> dict:
    return {"rows": rows(), "summary": summary(), "kinds": KINDS, "effective": EFFECTIVE, "facility": FACILITY, "access": ACCESS, "read_on": READ_ON,
            "access_fees": [{"key": k, "listed_as": t, "currency": c, "unit": u, "prices": p} for k, t, c, u, p in ACCESS_FEES]}
