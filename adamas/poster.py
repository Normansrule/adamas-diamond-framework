"""One-page SVG infographic of the whole framework, generated from the package's own numbers, so it never goes stale.
Numbers: [sze2006] [wort2008] [baliga1982] [saha2022] [balasubramanian2009] [dolde2013] [e6orbray2026] [kim2021] [liu2017] [fowler2012] [joas2025]."""
from __future__ import annotations
from pathlib import Path
from . import converter, materials, power

W, H = 1400, 1000
INK, TEAL, RED, GOLD, GREY = "#1d2733", "#0fa3b1", "#e63946", "#f4a261", "#7a8793"


def _card(x, y, w, h, title, big, sub, color=TEAL, src=""):
    return f'''<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#fff" stroke="#dde3e8"/>
<text x="{x+18}" y="{y+30}" font-size="15" font-weight="700" fill="{INK}">{title}</text>
<text x="{x+18}" y="{y+82}" font-size="44" font-weight="800" fill="{color}">{big}</text>
<text x="{x+18}" y="{y+108}" font-size="13.5" fill="#4a5a6a">{sub}</text>
<text x="{x+18}" y="{y+h-12}" font-size="10.5" fill="#8a97a3">{src}</text></g>'''


def build_svg() -> str:
    f = materials.normalized_foms()["Diamond"]["BFOM"]
    si, c = materials.MATERIALS["Si"], materials.MATERIALS["Diamond"]
    m = power.MEASURED_DIAMOND["saha2022"]
    ratio = power.ron_sp_mohm_cm2(si, m["bv_v"]) / m["ron_mohm_cm2"]
    ev = converter.material_switch("4H-SiC", 1200, 800, 300, 20e3, t_k=523.0).p_total_w / converter.material_switch("Diamond", 1200, 800, 300, 20e3, t_k=523.0).p_total_w
    fion = 100 * converter.drift_ionized_fraction(c, 1200.0, 300.0)
    from . import gate_budget, resource
    lo, hi = gate_budget.coherence_limited_range()
    n, st = resource.WORKLOADS[resource.RSA_JOB]
    est = resource.estimate(n, st, 1000.0, 1000.0); yrs = est.runtime_hours / 8766
    nref = len(__import__("re").findall(r"^@", (Path(__file__).resolve().parents[1] / "references" / "references.bib").read_text(encoding="utf-8"), __import__("re").M))
    cards = [
        (30, 130, 320, 150, "Same crystal, tighter bonds", "3.567 Å", f"lattice constant vs silicon {si.a_angstrom} Å; bandgap {c.eg_ev} vs {si.eg_ev} eV", TEAL, "[sze2006] [wort2008]"),
        (370, 130, 320, 150, "Power-switch scorecard", f"{f:,.0f}×", "Baliga figure of merit relative to silicon (holes)", TEAL, "[baliga1982]"),
        (710, 130, 320, 150, "Heat removal", f"{c.kappa_w_cmk / si.kappa_w_cmk:.0f}×", f"thermal conductivity, {c.kappa_w_cmk} vs {si.kappa_w_cmk} W/(cm·K)", TEAL, "[wei1993]"),
        (1050, 130, 320, 150, "Wafers today", "51 mm", "largest peer-reviewed single crystal; 76 mm announced", GOLD, "[kim2021] [e6orbray2026]"),
        (30, 300, 320, 150, "Real diamond switch", f"{ratio:.0f}×", "below silicon's vertical limit (lateral, 2568 V, 7.54 mΩ·cm²)", TEAL, "[saha2022]"),
        (370, 300, 320, 150, "Traction inverter, hot", f"{ev:.1f}×", "less loss than SiC at a 250 °C junction; loses at 300 K", TEAL, "[erickson2020] chapter E9"),
        (710, 300, 320, 150, "Dopant activation, 300 K", f"{fion:.1f}%", "of boron ionized in a 1.2 kV diamond drift", RED, "[lagrange1998]"),
        (1050, 300, 320, 150, "Logic today", "p-only", "n-channel MOSFET reported 2024; DIA-4 placed in about 1 mm²", GOLD, "[liao2024] [liu2017]"),
        (30, 470, 320, 150, "Qubit at room temperature", "1.8 ms", "electron coherence, ¹²C diamond; nuclear memory &gt; 1 s", TEAL, "[balasubramanian2009] [maurer2012]"),
        (370, 470, 320, 150, "Two qubits entangled", "25 nm", f"apart, fidelity 0.67; coherence allows {lo:.2f} to {hi:.3f}", TEAL, "[dolde2013] chapter E5"),
        (710, 470, 320, 150, "Addressing", "250 nm", "laser spot, but qubits sit 10 to 30 nm apart", RED, "[dolde2013] [joas2025] chapter 8"),
        (1050, 470, 320, 150, "Link error to scale", "≤ 0.3%", "assumed per inter-cell link; threshold about 1%", GOLD, "[fowler2012] chapter E6"),
        (30, 640, 320, 150, "Machine area", f"{est.die_side_mm:.1f} mm", f"die side for RSA-2048: {est.physical_qubits / 1e6:.0f} M qubits at 1 µm pitch", TEAL, "chapter E10"),
        (370, 640, 320, 150, "Machine time", f"{yrs:.1f} yr", "RSA-2048 at 1 ms readout, calibrated to the 8 h estimate", RED, "[gidney2021] chapter E10"),
        (710, 640, 320, 150, "First products", "sensors", "quantum magnetometers, detectors, heat spreaders ship now", TEAL, "chapter E11"),
        (1050, 640, 320, 150, "Evidence base", f"{nref} refs", "each equation and figure carries a citation key", GOLD, "references/REFERENCES.md"),
    ]
    body = "".join(_card(*cd) for cd in cards)
    flow = ""
    steps = ["Grow wafer", "Pattern", "Process", "Analog &amp; power", "Digital", "NV qubits", "Error correction", "Applications"]
    for i, s in enumerate(steps):
        x = 30 + i * 168
        flow += f'<rect x="{x}" y="835" width="150" height="46" rx="10" fill="#15405a" stroke="{TEAL}"/><text x="{x+75}" y="864" font-size="14" font-weight="700" fill="#fff" text-anchor="middle">{s}</text>'
        if i < len(steps) - 1:
            flow += f'<path d="M{x+152} 858 L{x+166} 858" stroke="{TEAL}" stroke-width="2.5"/><path d="M{x+162} 852 L{x+170} 858 L{x+162} 864 Z" fill="{TEAL}"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Helvetica,Arial,sans-serif">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1320"/><stop offset="1" stop-color="#12344a"/></linearGradient></defs>
<rect width="{W}" height="{H}" fill="#f4f7f9"/><rect width="{W}" height="110" fill="url(#g)"/>
<text x="30" y="62" font-size="46" font-weight="800" fill="#fff" letter-spacing="5">ADAMAS</text>
<text x="290" y="60" font-size="20" fill="#9fe8f2">Diamond wafers for classical and quantum circuits: the framework on one page</text>
<text x="290" y="88" font-size="14" fill="#c8d6e0">Sixteen numbers, each from a cited equation or measurement. Teal = advantage, red = obstacle, gold = status.</text>
{body}
<text x="30" y="820" font-size="16" font-weight="700" fill="{INK}">The path this repository follows, in order</text>{flow}
<text x="30" y="930" font-size="13" fill="#4a5a6a">Generated by adamas.poster from the package's own models. Bracketed keys resolve in references/REFERENCES.md; "chapter" points into docs/expert/.</text>
<text x="30" y="955" font-size="13" fill="#4a5a6a">Room-temperature diamond quantum machines will be memory-rich and slow: their case is embedded, sensing-coupled, and networked computing, not factoring.</text>
</svg>'''


def write(path: str | Path = "docs/img/poster.svg") -> Path:
    p = Path(path); p.write_text(build_svg(), encoding="utf-8"); return p
