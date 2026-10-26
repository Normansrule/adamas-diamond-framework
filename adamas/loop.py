"""Equation in the loop: one registry of the live equation panels the labs show (Phase 0 proposal, docs/phase0).

Each panel pairs a lab with the equation that governs it. The registry holds what must be identical on the web, in the
desktop app, and in the documents: the equation (HTML with clickable symbols), every symbol's name, unit, range, and
origin, the assumptions under which the equation holds, the unit check, the Python function that is the reference
implementation, and the sources. The browser evaluates the same equations in web/assets/loop_models.js, and golden()
writes Python values at fixed inputs to web/tests/loop_golden.json for the node tests to compare (tolerance 1e-6
relative unless stated).

Panels: Qubit Lab (Rabi, Ramsey, mistimed echo), Photon Lab (measured contrast), Power Lab (hot switch), Addressing Lab
(crosstalk), Wafer Lab (critical field and strain-limited T2* versus dislocation density).
"""
from __future__ import annotations

S = lambda k, html: f'<button class="v" type="button" data-k="{k}">{html}</button>'   # noqa: E731  clickable symbol
FR = lambda a, b: f'<span class="fr"><span>{a}</span><span>{b}</span></span>'          # noqa: E731

PANELS = {
 "rabi": {
  "lab": "labs/qubit.html", "title": "Rabi oscillation", "python": "adamas.nv.rabi",
  "html": f"<i>P</i><sub>−1</sub> = {FR(S('Om', 'Ω') + '<sup>2</sup>', S('Om', 'Ω') + '<sup>2</sup> + ' + S('de', 'δ') + '<sup>2</sup>')} sin<sup>2</sup>(π√({S('Om', 'Ω')}<sup>2</sup> + {S('de', 'δ')}<sup>2</sup>) {S('t', 't')})",
  "result": {"sym": "P₋₁", "name": "probability of mₛ = −1 after the pulse", "unit": "", "digits": 3},
  "vars": {"Om": {"sym": "Ω", "name": "Rabi frequency", "unit": "MHz", "min": 1, "max": 20, "digits": 1, "src": "set by microwave power; the π pulse lasts 1/(2Ω)"},
           "de": {"sym": "δ", "name": "detuning", "unit": "MHz", "min": -4, "max": 4, "digits": 2, "src": "microwave frequency minus the ODMR line (experiment A1)"},
           "t": {"sym": "t", "name": "pulse length", "unit": "µs", "min": 0, "max": 2, "digits": 3, "src": "pulse generator (experiment B1)"}},
  "units": ["MHz × µs = 1: the phase is dimensionless"],
  "assumptions": [{"id": "rwa", "text": "rotating wave: Ω ≪ D = 2870 MHz"}, {"id": "nodecay", "text": "no decay: t ≪ T₂*"},
                  {"id": "twolevel", "text": "two levels: mₛ = 0 and −1 only"}],
  "refs": ["rabi1937", "jelezko2004a"], "derivation": ["Chapter 6", "docs/06_nv_center_physics.md"]},
 "ramsey": {
  "lab": "labs/qubit.html", "title": "Ramsey fringes", "python": "adamas.nv.ramsey",
  "html": f"<i>P</i><sub>−1</sub> = ½[1 + cos(2π{S('de', 'δ')}{S('tau', 'τ')}) e<sup>−({S('tau', 'τ')}/{S('t2s', 'T<sub>2</sub>*')})<sup>2</sup></sup>]",
  "result": {"sym": "P₋₁", "name": "probability of mₛ = −1 after π/2 – τ – π/2", "unit": "", "digits": 3},
  "vars": {"de": {"sym": "δ", "name": "detuning", "unit": "MHz", "min": -4, "max": 4, "digits": 2, "src": "microwave frequency minus the ODMR line"},
           "tau": {"sym": "τ", "name": "free time", "unit": "µs", "min": 0, "max": 6, "digits": 2, "src": "pulse generator"},
           "t2s": {"sym": "T₂*", "name": "dephasing time", "unit": "µs", "min": 0.1, "max": 6, "digits": 2, "src": "spread of static detunings; 1 to 100 µs in real diamond [balasubramanian2009]"}},
  "units": ["MHz × µs = 1", "τ / T₂* is dimensionless"],
  "assumptions": [{"id": "hard", "text": "hard pulses: π/(2Ω) ≪ τ"}, {"id": "gauss", "text": "quasi-static Gaussian detunings"}],
  "refs": ["ramsey1950", "degen2017"], "derivation": ["Chapter 6", "docs/06_nv_center_physics.md"]},
 "echo": {
  "lab": "labs/qubit.html", "title": "Hahn echo with a mistimed π pulse", "python": "adamas.nv.echo_mistimed",
  "html": f"<i>P</i><sub>−1</sub> = ½[1 − cos(2π{S('de', 'δ')}{S('eps', 'ε')}) e<sup>−({S('eps', 'ε')}/{S('t2s', 'T<sub>2</sub>*')})<sup>2</sup></sup>], &nbsp; ε = τ<sub>2</sub> − τ<sub>1</sub>",
  "result": {"sym": "P₋₁", "name": "probability of mₛ = −1 after π/2 – τ₁ – π – τ₂ – π/2", "unit": "", "digits": 3},
  "vars": {"de": {"sym": "δ", "name": "detuning", "unit": "MHz", "min": -4, "max": 4, "digits": 2, "src": "microwave frequency minus the ODMR line"},
           "eps": {"sym": "ε", "name": "π-pulse mistiming τ₂ − τ₁", "unit": "µs", "min": -2, "max": 2, "digits": 2, "src": "pulse placement; 0 for a centred echo"},
           "t2s": {"sym": "T₂*", "name": "dephasing time", "unit": "µs", "min": 0.1, "max": 6, "digits": 2, "src": "spread of static detunings"}},
  "units": ["MHz × µs = 1"],
  "assumptions": [{"id": "static", "text": "static noise only: real spins also lose T₂ (not modelled here)"}, {"id": "hard", "text": "hard pulses"}],
  "refs": ["hahn1950", "delange2010"], "derivation": ["Chapter 6", "docs/06_nv_center_physics.md"]},
 "contrast": {
  "lab": "labs/photon.html", "title": "Readout contrast you can measure", "python": "adamas.photophysics.measured_contrast",
  "html": f"<i>C</i> = 1 − {FR(S('P', '<i>P</i>') + ' <i>I</i><sub>1</sub> + (1 − ' + S('P', '<i>P</i>') + ') <i>I</i><sub>0</sub>', S('P', '<i>P</i>') + ' <i>I</i><sub>0</sub> + (1 − ' + S('P', '<i>P</i>') + ') <i>I</i><sub>1</sub>')}, &nbsp; <i>I</i><sub>m</sub> = ∫<sub>0</sub><sup>{S('win', 't<sub>w</sub>')}</sup> photons(mₛ = m), &nbsp; {S('P', '<i>P</i>')}({S('beta', 'β')}, {S('tpol', 't<sub>pol</sub>')})",
  "result": {"sym": "C", "name": "contrast with and without a π pulse, from the pumped state", "unit": "", "digits": 3},
  "vars": {"beta": {"sym": "β", "name": "pump rate over the radiative rate", "unit": "", "min": 0.1, "max": 3, "digits": 2, "src": "laser power; saturation near 1 [tetienne2012]"},
           "win": {"sym": "t_w", "name": "counting window", "unit": "µs", "min": 0.1, "max": 1, "digits": 2, "src": "photon-counter gate"},
           "tpol": {"sym": "t_pol", "name": "pumping time before the pulse", "unit": "µs", "min": 0.3, "max": 5, "digits": 1, "src": "laser pulse length"},
           "P": {"sym": "P", "name": "spin polarization (population of mₛ = 0)", "unit": "", "derived": True, "digits": 3, "src": "computed from the rate model after t_pol"}},
  "units": ["rates in 1/µs × times in µs: dimensionless"],
  "assumptions": [{"id": "zerofield", "text": "zero field: mₛ = ±1 lumped"}, {"id": "perfectpi", "text": "perfect π pulse"},
                  {"id": "window", "text": "window shorter than the singlet lifetime (≈ 0.5 µs)"}],
  "refs": ["tetienne2012", "gruber1997"], "derivation": ["Chapter 6", "docs/06_nv_center_physics.md"]},
 "hot_switch": {
  "lab": "labs/power.html", "title": "Why diamond wins only when hot", "python": "adamas.converter.ron_temperature_factor",
  "html": f"{FR('<i>R</i><sub>on</sub>(' + S('T', 'T') + ')', '<i>R</i><sub>ideal</sub>')} = ({FR(S('T', 'T'), '300 K')})<sup>{S('alpha', 'α')}</sup> · {FR('1', S('fion', '<i>f</i><sub>ion</sub>') + '(' + S('T', 'T') + ', ' + S('N', 'N') + ')')}",
  "result": {"sym": "R_on/R_ideal", "name": "on-resistance of a bulk boron-doped drift relative to its ideal limit", "unit": "×", "digits": 1},
  "vars": {"T": {"sym": "T", "name": "junction temperature", "unit": "K", "min": 300, "max": 650, "digits": 0, "src": "set by losses, cooling and ambient"},
           "alpha": {"sym": "α", "name": "lattice-mobility exponent", "unit": "", "min": 2.0, "max": 3.2, "digits": 1, "src": "about 2.8 for holes in diamond [pernot2010]"},
           "N": {"sym": "N", "name": "boron in the drift layer", "unit": "cm⁻³", "derived": True, "digits": 2, "src": "unipolar-limit design for the blocking voltage: ε E_c² / (2 q BV)"},
           "fion": {"sym": "f_ion", "name": "ionized fraction of the boron", "unit": "", "derived": True, "digits": 4, "src": "charge neutrality with E_A = 0.37 eV [lagrange1998]"}},
  "units": ["(K / K)^α is dimensionless", "f_ion is a fraction"],
  "assumptions": [{"id": "uncomp", "text": "uncompensated boron (compensation lowers f_ion)"}, {"id": "nofield", "text": "no field-assisted ionization"},
                  {"id": "sicceil", "text": "SiC package ceiling ≈ 523 K"}],
  "refs": ["pernot2010", "lagrange1998", "kawarada2014"], "derivation": ["E9.2", "docs/expert/E9_power_circuits_diamond_vs_gan_sic.md"]},
 "crosstalk": {
  "lab": "labs/addressing.html", "title": "Driving one NV without the other", "python": "adamas.addressing.crosstalk",
  "html": f"<i>X</i> = {FR(S('Om', 'Ω') + '<sup>2</sup>', S('Om', 'Ω') + '<sup>2</sup> + ' + S('Dl', 'Δ') + '<sup>2</sup>')}, &nbsp; resolved if {S('Dl', 'Δ')} &gt; {FR('1', 'π' + S('t2s', 'T<sub>2</sub>*'))}",
  "result": {"sym": "X", "name": "peak excitation of the other NV (crosstalk)", "unit": "", "digits": 4},
  "vars": {"Om": {"sym": "Ω", "name": "Rabi frequency of the drive", "unit": "MHz", "min": 0.1, "max": 20, "digits": 2, "src": "microwave power"},
           "Dl": {"sym": "Δ", "name": "separation of the two NVs' lines", "unit": "MHz", "derived": True, "digits": 2, "src": "orientation (spectral route) or field gradient"},
           "t2s": {"sym": "T₂*", "name": "dephasing time", "unit": "µs", "min": 0.2, "max": 50, "digits": 1, "src": "sets the line width 1/(πT₂*)"}},
  "units": ["MHz² / MHz²: dimensionless", "1/(µs) = MHz"],
  "assumptions": [{"id": "resolved", "text": "lines resolved: Δ above the line width"}, {"id": "nohf", "text": "¹⁴N hyperfine ignored (2.15 MHz triplet)"}],
  "refs": ["rabi1937", "dolde2013", "grinolds2011"], "derivation": ["Chapter 7", "docs/07_nv_fabrication_and_placement.md"]},
 "crystal": {
  "lab": "labs/wafer.html", "title": "Crystal quality sets the breakdown field", "python": "adamas.power.critical_field_mv_cm",
  "html": f"<i>E</i><sub>c</sub> = 7.7 − 1.88 log<sub>10</sub>({FR(S('D', 'D'), '10<sup>4</sup> cm<sup>−2</sup>')}) MV/cm, &nbsp; {S('t2', '<i>T</i><sub>2</sub>*')} ≤ {FR('1', 'π <i>k</i><sub>s</sub> ' + S('eps', 'ε') + '(' + S('D', 'D') + ')')}",
  "result": {"sym": "E_c", "name": "effective breakdown field (proposed fit, floored at 1 MV/cm)", "unit": "MV/cm", "digits": 2},
  "vars": {"D": {"sym": "D", "name": "threading-dislocation density", "unit": "cm⁻²", "min": 10, "max": 1e9, "log": True, "digits": 2, "src": "substrate class: HPHT ~10², CVD on HPHT ~10⁴, heteroepitaxial ~2×10⁷ [stehl2013]"},
           "eps": {"sym": "ε", "name": "strain at the mean dislocation distance, b/(2πr)", "unit": "", "derived": True, "digits": 2, "src": "Burgers vector 0.252 nm, r = 1/(2√D)"},
           "t2": {"sym": "T₂*", "name": "strain-limited dephasing time (upper bound)", "unit": "µs", "derived": True, "digits": 3, "src": "spin–strain coupling 10.9 GHz per unit strain [marshall2022]"}},
  "units": ["log of a ratio of densities", "GHz × strain × µs: dimensionless"],
  "assumptions": [{"id": "fit", "text": "E_c(D) is an engineering fit, not a law"}, {"id": "range", "text": "fit range 10⁴ to 10⁸ cm⁻²"}],
  "refs": ["volpe2010", "kwak2021", "weippert2022", "marshall2022", "stehl2013"], "derivation": ["Chapter 2", "docs/02_wafer_manufacturing.md"]},
}


def to_json() -> dict:
    return PANELS


# ---------------- Python values at fixed inputs, for the JavaScript cross-check -----------------------------------
def golden() -> dict:
    from . import addressing, converter, gatebias, materials, nv, photophysics, power
    out: dict = {}
    out["rabi"] = [[om, de, t, float(nv.rabi(t, om, de))] for om in (2.0, 7.5) for de in (0.0, 1.5) for t in (0.03, 0.21)]
    out["ramsey"] = [[de, tau, t2s, float(nv.ramsey(tau, de, t2s))] for de in (0.5, 2.0) for tau in (0.3, 1.7) for t2s in (0.8, 3.0)]
    out["echo"] = [[de, e, t2s, float(nv.echo_mistimed(e, de, t2s))] for de in (0.5, 2.0) for e in (0.0, 0.4, -1.1) for t2s in (0.8, 3.0)]
    out["polarization"] = [[b, t, photophysics.polarization(b, t)] for b in (0.5, 1.0, 2.0) for t in (0.5, 3.0)]
    out["contrast"] = [[b, w, t, photophysics.measured_contrast(b, w, t)] for b in (0.5, 1.0) for w in (0.3, 0.6) for t in (1.0, 3.0)]
    d = materials.MATERIALS["Diamond"]
    out["hot"] = [[bv, t, converter.drift_ionized_fraction(d, bv, t), converter.ron_temperature_factor("Diamond", t, bv)]
                  for bv in (650.0, 1200.0, 3300.0) for t in (300.0, 400.0, 523.0, 650.0)]
    out["crystal"] = [[D, power.critical_field_mv_cm(D), nv.dislocation_strain(D), nv.t2star_from_dislocations_us(D), power.killer_survival(25.0, D, 1e-3)]
                      for D in (1e2, 1e4, 3e5, 2e7, 1e9)]
    out["spot"] = [[lam, na, addressing.spot_fwhm_nm(lam, na)] for lam in (532.0, 637.0) for na in (0.7, 0.95, 1.3)]
    axes = [list(map(float, a)) for a in nv.NV_AXES]
    out["lines"] = [[b, th, ph, k, list(addressing.lines_on_axis(b, th, ph, axes[k]))] for b in (1.0, 5.0) for th, ph in ((0, 0), (54.7356, 45), (30, 10), (90, 0)) for k in range(4)]
    out["gradient"] = [[g, dx, addressing.gradient_shift_mhz(g, dx)] for g in (0.01, 0.1, 1.0) for dx in (10.0, 25.0)]
    out["crosstalk"] = [[om, dl, addressing.crosstalk(om, dl)] for om in (0.5, 5.0) for dl in (1.0, 30.0)]
    out["bias"] = [[k, eta, h, {str(q): v for q, v in gatebias.output_distribution(k, eta, h)["per_qubit"].items()},
                    gatebias.output_distribution(k, eta, h)["spread"]] for k in ("cz", "cnot") for eta in (0.5, 10.0, 100.0) for h in (0.002, 0.2)]
    out["propagate"] = [[q, p, gatebias.propagate({q: p}, [("CZ", (0, 1)), ("H", (1,))])] for q in (0, 1) for p in "XYZ"]
    return out


def write_golden(path: str = "web/tests/loop_golden.json") -> str:
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / path
    p.write_text(json.dumps(golden(), indent=1) + "\n", encoding="utf-8"); return str(p)


def write() -> str:
    """Golden values plus the registry itself (the node tests check that every panel and assumption has a JS model)."""
    import json
    from pathlib import Path
    reg = Path(__file__).resolve().parents[1] / "web" / "tests" / "loop_registry.json"
    reg.write_text(json.dumps(PANELS, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return write_golden() + " and " + str(reg)
