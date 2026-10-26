"""Equation in the loop: one registry of the live equation panels the labs show (Phase 0 proposal, docs/phase0).

Each panel pairs a lab with the equation that governs it. The registry holds what must be identical on the web, in the
desktop app, and in the documents: the equation (HTML with clickable symbols), every symbol's name, unit, range, and
origin, the assumptions under which the equation holds, the unit check, the Python function that is the reference
implementation, and the sources. The browser evaluates the same equations in web/assets/loop_models.js, and golden()
writes Python values at fixed inputs to web/tests/loop_golden.json for the node tests to compare (tolerance 1e-6
relative unless stated).

Panels: Qubit Lab (Rabi, Ramsey, mistimed echo), Photon Lab (measured contrast), Power Lab (hot switch), Addressing Lab
(crosstalk), Wafer Lab (critical field and strain-limited T2* versus dislocation density), Lattice Lab (ODMR lines to
second order), Heat Race (slowest thermal mode), Transistor Lab (ring-oscillator hand estimate), Break the Code (logical
error scaling), Machine Builder (failure budget), Gate Bias Lab (output bias).
"""
from __future__ import annotations

import math

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
  "html": f"<i>X</i> = {FR(S('Om', 'Ω') + '<sup>2</sup>', S('Om', 'Ω') + '<sup>2</sup> + ' + S('Dl', 'Δ') + '<sup>2</sup>')}, &nbsp; resolved if {S('Dl', 'Δ')} &gt; {FR('2√ln 2', 'π' + S('t2s', 'T<sub>2</sub>*'))}",
  "result": {"sym": "X", "name": "peak excitation of the other NV (crosstalk)", "unit": "", "digits": 4},
  "vars": {"Om": {"sym": "Ω", "name": "Rabi frequency of the drive", "unit": "MHz", "min": 0.1, "max": 20, "digits": 2, "src": "microwave power"},
           "Dl": {"sym": "Δ", "name": "separation of the two NVs' lines", "unit": "MHz", "derived": True, "digits": 2, "src": "orientation (spectral route) or field gradient"},
           "t2s": {"sym": "T₂*", "name": "dephasing time", "unit": "µs", "min": 0.2, "max": 50, "digits": 1, "src": "sets the line width 2√ln2/(πT₂*) of a Gaussian free-induction decay"}},
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
 "odmr": {
  "lab": "labs/lattice.html", "title": "Where the magnetic-resonance lines sit", "python": "adamas.nv.lines_perturbative_mhz",
  "html": f"<i>f</i><sub>±</sub> = {S('D', '<i>D</i>')} + {FR('3<i>b</i><sub>⊥</sub><sup>2</sup>', '2' + S('D', '<i>D</i>'))} ± √(<i>b</i><sub>∥</sub><sup>2</sup> + ({FR('<i>b</i><sub>⊥</sub><sup>2</sup>', '2' + S('D', '<i>D</i>'))})<sup>2</sup>), &nbsp; <i>b</i><sub>∥</sub> = γ<sub>e</sub>{S('B', '<i>B</i>')} cos {S('th', 'θ')}, <i>b</i><sub>⊥</sub> = γ<sub>e</sub>{S('B', '<i>B</i>')} sin {S('th', 'θ')}",
  "result": {"sym": "Δf", "name": "splitting of the two lines of the NV along [111]", "unit": "MHz", "digits": 1},
  "vars": {"B": {"sym": "B", "name": "field magnitude", "unit": "mT", "min": 0, "max": 8, "digits": 2, "src": "the magnet (experiment A2: a magnet's dipole field)"},
           "th": {"sym": "θ", "name": "angle between the field and the [111] NV axis", "unit": "°", "derived": True, "digits": 1, "src": "set by the lab's field direction"},
           "D": {"sym": "D", "name": "zero-field splitting", "unit": "MHz", "min": 2860, "max": 2880, "digits": 1, "src": "2870 MHz at 300 K, −74.2 kHz/K [acosta2010] [doherty2013]"}},
  "units": ["γₑ = 28.03 MHz/mT, so γₑB is in MHz", "b²/D: MHz²/MHz = MHz"],
  "assumptions": [{"id": "weak", "text": "second order in B: γₑB ≪ D (the ±1 pair mixes near 90°)"}, {"id": "strainfree", "text": "no strain or electric field (E = 0)"}],
  "refs": ["doherty2013", "acosta2010"], "derivation": ["Chapter 6", "docs/06_nv_center_physics.md"]},
 "heat": {
  "lab": "labs/heat.html", "title": "How long the hot spot takes to settle", "python": "adamas.thermal.slowest_mode_time_s",
  "html": f"τ = {FR('4' + S('L', '<i>L</i>') + '<sup>2</sup>', 'π<sup>2</sup>' + S('al', 'α'))}, &nbsp; {S('al', 'α')} = {FR(S('k', 'κ'), S('rc', 'ρ<i>c</i>'))}, &nbsp; steady peak ∝ 1/{S('k', 'κ')}",
  "result": {"sym": "τ", "name": "time constant of the slowest thermal mode (95 % settled after 3τ)", "unit": "ms", "digits": 2},
  "vars": {"k": {"sym": "κ", "name": "thermal conductivity", "unit": "W/(cm·K)", "min": 1, "max": 25, "log": True, "digits": 2, "src": "diamond 22 [wei1993], SiC 4.9 [kimoto2014], GaN 2.3 [mishra2008], Si 1.5 [sze2006]; click a tile to load it"},
           "rc": {"sym": "ρc", "name": "volumetric heat capacity", "unit": "J/(cm³·K)", "min": 1, "max": 3.5, "digits": 2, "src": "density × specific heat: diamond 3.52 × 0.509, silicon 2.33 × 0.705 [haynes2016]"},
           "L": {"sym": "L", "name": "die thickness", "unit": "cm", "min": 0.02, "max": 0.5, "digits": 2, "src": "the lab's cross-section is 0.2 cm deep"},
           "al": {"sym": "α", "name": "thermal diffusivity", "unit": "cm²/s", "derived": True, "digits": 2, "src": "κ / (ρc)"}},
  "units": ["cm² / (cm²/s) = s, shown in ms", "W/(cm·K) ÷ J/(cm³·K) = cm²/s"],
  "assumptions": [{"id": "constk", "text": "constant κ (it falls as the die heats)"}, {"id": "settled", "text": "the lab has run for 3τ (steady state)"}],
  "refs": ["carslaw1959", "wei1993", "sze2006", "kimoto2014", "mishra2008", "haynes2016"], "derivation": ["Chapter 4", "docs/04_analog_power_rf_devices.md"]},
 "ring": {
  "lab": "labs/transistor.html", "title": "A hand estimate of the ring oscillator", "python": "adamas.logic.ring_period_estimate_s",
  "html": f"<i>T</i> = {S('N', '<i>N</i>')} ({FR(S('C', '<i>C</i>') + S('V', '<i>V</i><sub>DD</sub>'), '2' + S('IL', '<i>I</i><sub>L</sub>'))} + {FR(S('C', '<i>C</i>') + S('V', '<i>V</i><sub>DD</sub>'), '2(' + S('ID', '<i>I</i><sub>D</sub>') + ' − ' + S('IL', '<i>I</i><sub>L</sub>') + ')')}), &nbsp; <i>I</i> ∝ {S('mu', 'μ')}",
  "result": {"sym": "T", "name": "estimated period of the five-stage ring", "unit": "ns", "digits": 1},
  "vars": {"mu": {"sym": "μ", "name": "hole mobility in the channel", "unit": "cm²/(V·s)", "min": 20, "max": 600, "digits": 0, "src": "hydrogen-terminated diamond, 50 to 300 typical [kawarada2017]"},
           "V": {"sym": "V_DD", "name": "supply voltage", "unit": "V", "min": 4, "max": 20, "step": 1, "digits": 1, "src": "the lab's supply"},
           "N": {"sym": "N", "name": "number of stages", "unit": "", "derived": True, "digits": 0, "src": "five, as in the lab and the ngspice netlist"},
           "C": {"sym": "C", "name": "node capacitance (gate plus 20 fF wiring)", "unit": "fF", "derived": True, "digits": 1, "src": "C_ox W L of the next driver + wiring"},
           "IL": {"sym": "I_L", "name": "load current (depletion device, V_GS = 0)", "unit": "mA", "derived": True, "digits": 3, "src": "square law at saturation"},
           "ID": {"sym": "I_D", "name": "driver current at V_DS = V_DD/2", "unit": "mA", "derived": True, "digits": 3, "src": "square law, input at V_DD"}},
  "units": ["F × V / A = s, shown in ns"],
  "assumptions": [{"id": "vsim", "text": "the hand estimate agrees with the lab's transient simulation within 50 %"},
                  {"id": "longch", "text": "long channel: no velocity saturation"}],
  "refs": ["rabaey2003", "sze2006", "liu2017"], "derivation": ["E3", "docs/expert/E3_digital_and_cpu_design.md"]},
 "logical": {
  "lab": "labs/qec.html", "title": "How fast a bigger code wins", "python": "adamas.qec.surface_code_logical_error",
  "html": f"<i>p</i><sub>L</sub> ≈ {S('A', '<i>A</i>')} ({FR(S('p', '<i>p</i>'), S('pth', '<i>p</i><sub>th</sub>'))})<sup>({S('d', '<i>d</i>')} + 1)/2</sup>",
  "result": {"sym": "p_L", "name": "logical failure probability per decoding trial", "unit": "", "digits": 4},
  "vars": {"p": {"sym": "p", "name": "physical error rate", "unit": "", "min": 0.01, "max": 0.2, "step": 0.01, "digits": 3, "src": "the lab's slider: independent bit flips"},
           "d": {"sym": "d", "name": "code distance", "unit": "", "min": 3, "max": 9, "step": 2, "digits": 0, "src": "the lab's code size"},
           "pth": {"sym": "p_th", "name": "threshold", "unit": "", "min": 0.03, "max": 0.15, "digits": 3, "src": "10.3 % for code capacity with minimum-weight matching [wang2003]; this lab's greedy decoder is lower"},
           "A": {"sym": "A", "name": "prefactor", "unit": "", "min": 0.01, "max": 1, "log": True, "digits": 2, "src": "fitted to simulation (the lab fits it to its own threshold run); 0.1 is the round value used by [gidney2021]"}},
  "units": ["p / p_th is dimensionless"],
  "assumptions": [{"id": "below", "text": "below threshold: p < p_th"}, {"id": "lowp", "text": "leading order: valid well below threshold"},
                  {"id": "codecap", "text": "code capacity: perfect syndrome measurements"}],
  "refs": ["dennis2002", "wang2003", "fowler2012", "gidney2021"], "derivation": ["E6", "docs/expert/E6_error_correction_and_system_architecture.md"]},
 "budget": {
  "lab": "labs/machine.html", "title": "The failure budget that sets the code distance", "python": "adamas.resource.failure_probability",
  "html": f"<i>P</i><sub>fail</sub> = {S('n', '<i>n</i><sub>L</sub>')} · {S('st', '<i>S</i>')} · {S('d', '<i>d</i>')} · {S('A', '<i>A</i>')} {S('lam', 'Λ')}<sup>−({S('d', '<i>d</i>')} + 1)/2</sup> ≤ ε",
  "result": {"sym": "P_fail", "name": "probability that the whole computation fails", "unit": "", "digits": 4},
  "vars": {"n": {"sym": "n_L", "name": "logical qubits", "unit": "", "derived": True, "digits": 0, "src": "the chosen job"},
           "st": {"sym": "S", "name": "logical steps", "unit": "", "derived": True, "digits": 2, "src": "the chosen job (RSA-2048 calibrated to 1.07 × 10⁹)"},
           "d": {"sym": "d", "name": "code distance (smallest odd d meeting ε = 1 %)", "unit": "", "derived": True, "digits": 0, "src": "chosen by the lab"},
           "A": {"sym": "A", "name": "fit prefactor", "unit": "", "derived": True, "digits": 3, "src": "Stim circuit-level fit at this readout time and memory [gidney2021stim]"},
           "lam": {"sym": "Λ", "name": "error suppression per +2 distance", "unit": "", "derived": True, "digits": 2, "src": "same fit; 2.14 measured on superconducting hardware [google2025]"}},
  "units": ["a product of counts and probabilities: dimensionless"],
  "assumptions": [{"id": "below", "text": "below threshold: Λ > 1"}, {"id": "union", "text": "union bound: failures independent and rare"},
                  {"id": "link", "text": "the 0.3 % inter-cell link is proposed, not demonstrated"}],
  "refs": ["fowler2012", "litinski2019", "gidney2021stim", "google2025"], "derivation": ["E10", "docs/expert/E10_scaling_a_room_temperature_quantum_computer.md"]},
 "bias": {
  "lab": "labs/bias.html", "title": "What bias leaves the gate", "python": "adamas.gatebias.output_bias",
  "html": f"η<sub>out</sub> = {FR('<i>P</i><sub>Z</sub>', '<i>P</i><sub>X</sub> + <i>P</i><sub>Y</sub>')} on the target; CZ: η<sub>out</sub> = {S('eta', 'η')}, &nbsp; H·CZ·H: η<sub>out</sub> → {FR('1', '2' + S('eta', 'η') + ' + 1')} as {S('h', '<i>h</i>')} → 0",
  "result": {"sym": "η_out", "name": "bias of the target's errors leaving the H · CZ · H CNOT", "unit": "", "digits": 4},
  "vars": {"eta": {"sym": "η", "name": "bias going in, p_Z / (p_X + p_Y)", "unit": "", "min": 0.5, "max": 1000, "log": True, "digits": 2, "src": "NV dephasing dominates; the value for two-qubit gates is an assumption"},
           "h": {"sym": "h", "name": "Hadamard time over CZ time", "unit": "", "min": 0.001, "max": 0.5, "log": True, "digits": 3, "src": "lab slider; short pulses make h small"}},
  "units": ["a ratio of probabilities: dimensionless"],
  "assumptions": [{"id": "first", "text": "first order in the error rate"}, {"id": "endseg", "text": "errors at the end of each segment (spread is a lower bound)"},
                  {"id": "shorth", "text": "short Hadamards: h ≪ 1"}],
  "refs": ["guillaud2019", "etxezarreta2025", "gidney2021stim"], "derivation": ["E6.1e", "docs/expert/E6_error_correction_and_system_architecture.md"]},
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
    out["best"] = [[b, th, ph, *addressing.best_line(b, th, ph)] for b in (1.0, 5.0) for th, ph in ((0, 0), (54.7356, 45), (30, 10), (55, 45))]
    out["linewidth"] = [[t, addressing.linewidth_mhz(t)] for t in (0.3, 1.0, 10.0)]
    out["bias"] = [[k, eta, h, {str(q): v for q, v in gatebias.output_distribution(k, eta, h)["per_qubit"].items()},
                    gatebias.output_distribution(k, eta, h)["spread"]] for k in ("cz", "cnot") for eta in (0.5, 10.0, 100.0) for h in (0.002, 0.2)]
    out["propagate"] = [[q, p, gatebias.propagate({q: p}, [("CZ", (0, 1)), ("H", (1,))])] for q in (0, 1) for p in "XYZ"]
    from . import logic, qec, resource, thermal
    out["odmr2"] = [[b, th, list(nv.lines_perturbative_mhz(b, th)),
                     list(nv.transition_frequencies_mhz((b * math.sin(math.radians(th)), 0.0, b * math.cos(math.radians(th)))))]
                    for b in (0.5, 3.0, 8.0) for th in (0.0, 40.0, 90.0, 130.0)]
    out["heat"] = [[k, rc, L, thermal.slowest_mode_time_s(k, rc, L)] for k, rc in ((22.0, 3.52 * 0.509), (1.5, 2.33 * 0.705)) for L in (0.05, 0.2)]
    out["ring"] = [[mu, ve, vd, r, vdd, logic.ring_period_estimate_s(mu, ve, vd, r, vdd)] for mu, ve, vd, r, vdd in
                   ((150.0, 1.5, -2.0, 8.0, 10.0), (300.0, 1.0, -1.0, 4.0, 6.0), (60.0, 3.0, -4.0, 16.0, 15.0))]
    out["logical"] = [[p, d, pth, A, qec.surface_code_logical_error(p, d, pth, A)] for p in (0.02, 0.08) for d in (3, 7) for pth, A in ((0.103, 0.1), (0.05, 0.3))]
    out["budget"] = [[n, st, d, A, lam, resource.failure_probability(n, st, d, A, lam)] for n, st in ((100.0, 1e6), (1000.0, 1.07e9)) for d in (11, 27) for A, lam in ((0.03, 2.14), (0.1, 4.0))]
    out["outbias"] = [[k, eta, h, {str(q): v for q, v in gatebias.output_bias(k, eta, h).items()}] for k in ("cz", "cnot") for eta in (1.0, 100.0) for h in (0.001, 0.1)]
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
