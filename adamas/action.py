"""Equations in action: every experiment paired with the equation that governs it, as an animated, live web page.

Each scene names the experiment it explains (adamas.experiments), the governing equation in two forms (LaTeX for the
README, documents, and figures; HTML with tagged symbols for the web page, where a symbol glows when its slider moves),
the symbols and their meanings, the slider ranges, a three-level explanation, and its sources. The web page
(web/action.html) animates the mechanism, plugs the slider values into the equation, and draws the curve the experiment
should measure. The browser physics lives in web/assets/sim/action.js and is checked against this package: golden()
evaluates the Python models at fixed inputs, `make action-golden` writes them to web/tests/action_golden.json, and the
node tests compare the JavaScript with them.

Fourteen scenes: twelve follow the ten experiments (B1 gives three: Rabi, Ramsey, echo) and two are the framework's
headline equations (the Baliga power-device limit and surface-code scaling).
"""
from __future__ import annotations
import math

QQ = r",\qquad"
GROUPS = {"Materials": "#48e5a3", "Devices": "#ffc46b", "Quantum": "#2de2e6", "Scale": "#9d7bff"}

V = lambda key, html: f'<var data-v="{key}">{html}</var>'                     # noqa: E731  slider-linked symbol
FR = lambda a, b: f'<span class="fr"><span>{a}</span><span>{b}</span></span>'  # noqa: E731  stacked fraction

SCENES = [
 {"id": "odmr", "group": "Quantum", "exp": "A1", "title": "A spin you can see: optically detected magnetic resonance",
  "tagline": "Sweep a microwave through 2.87 GHz and the red glow dips; a magnet splits the dip in two.",
  "tex": r"f_\pm = D \pm \gamma_e B_\parallel,\qquad B_\parallel = B\cos\theta",
  "html": f"f<sub>±</sub> = <span class=k>D</span> ± <span class=k>γ<sub>e</sub></span>{V('B', 'B')} cos {V('theta', 'θ')}",
  "symbols": [("D", "zero-field splitting, 2870 MHz at room temperature"), ("γₑ", "electron gyromagnetic ratio, 28.03 MHz per mT"),
              ("B", "magnetic field"), ("θ", "angle between the field and the NV axis"), ("Γ", "line width (full width at half maximum)"), ("C", "fluorescence contrast of a dip")],
  "vars": [{"key": "B", "label": "Field B", "unit": "mT", "min": 0, "max": 10, "step": 0.1, "value": 3},
           {"key": "theta", "label": "Angle θ", "unit": "°", "min": 0, "max": 90, "step": 1, "value": 0},
           {"key": "width", "label": "Line width Γ", "unit": "MHz", "min": 1, "max": 12, "step": 0.5, "value": 6},
           {"key": "contrast", "label": "Contrast C", "unit": "%", "min": 0.5, "max": 3, "step": 0.1, "value": 1.2}],
  "auto": "B",
  "levels": {"k": "Inside the diamond are tiny magnets that glow red when you shine green light on them. A radio wave at exactly the right pitch flips them, and flipped ones glow a little less. Bring a real magnet close and the right pitch splits into two: one higher, one lower.",
             "s": "Green light pumps the NV ground state into mₛ = 0, which fluoresces about 30% more than mₛ = ±1. A microwave at a transition frequency moves population into ±1 and the fluorescence dips. The ±1 levels shift by ±γₑB∥ (Zeeman effect), so the single 2870 MHz dip splits by 2γₑB∥.",
             "r": "Lines are the exact eigenvalue differences of H/h = D S_z² + γₑ B·S for spin 1 with B in the x–z plane (the web page diagonalizes the 3×3 Hamiltonian in closed form); a transverse field adds the second-order shift 3γₑ²B⊥²/2D. Lorentzian line shape of full width Γ; the ensemble case sums four ⟨111⟩ orientations. Same model as adamas.nv."},
  "refs": ["gruber1997", "doherty2013", "dreau2011", "stegemann2023"], "lab": "labs/lattice.html"},

 {"id": "dipole", "group": "Quantum", "exp": "A2", "title": "Weigh a magnet with light: the inverse-cube law",
  "tagline": "Move the magnet back and the splitting collapses as 1/r³: a dipole field, measured by a qubit.",
  "tex": r"B(r) = \frac{\mu_0}{4\pi}\,\frac{2m}{r^3},\qquad \Delta f = 2\gamma_e B",
  "html": f"B = {FR('<span class=k>μ<sub>0</sub></span>', '<span class=k>4π</span>')} {FR('2' + V('m', 'm'), V('r', 'r') + '<sup>3</sup>')} &nbsp;⟹&nbsp; Δf = 2<span class=k>γ<sub>e</sub></span>B",
  "symbols": [("μ₀", "vacuum permeability, 4π × 10⁻⁷ T·m/A"), ("m", "magnetic dipole moment of the magnet"), ("r", "distance from the magnet to the diamond"), ("Δf", "splitting between the outer pair of lines")],
  "vars": [{"key": "r", "label": "Distance r", "unit": "cm", "min": 2, "max": 12, "step": 0.1, "value": 4},
           {"key": "m", "label": "Dipole moment m", "unit": "A·m²", "min": 0.2, "max": 3, "step": 0.05, "value": 1.2}],
  "auto": "r",
  "levels": {"k": "A magnet's pull fades fast when you move it away: twice as far means eight times weaker. The diamond's two red-glow dips tell you exactly how strong the field is, so you can watch the field fade.",
             "s": "On the axis of a small magnet the field is B = (μ₀/4π)(2m/r³). Each NV line pair splits by 2γₑB∥, so the splitting falls as r⁻³: a straight line of slope −3 on log–log axes. The intercept gives m; a 10 mm N52 cube is about 1.2 A·m².",
             "r": "Point-dipole approximation, valid when r is a few magnet sizes; closer in, use the finite-cube field. The experiment fits the outer line pair, whose axis makes the smallest angle with the field (projection factor about 0.85 in the A2 data)."},
  "refs": ["rondin2014", "doherty2013"], "lab": "labs/lattice.html"},

 {"id": "heat", "group": "Materials", "exp": "A3", "title": "Heat-spreader race: why hot chips sit on diamond",
  "tagline": "Same heater, four plates. The diamond plate pulls the heat away fastest and stays coolest.",
  "tex": r"\Delta T(t) = P\,R_{th}\left(1 - e^{-t/\tau}\right),\qquad R_{th} = \frac{1}{4\kappa a} + R_{paste} + R_{sink}",
  "html": f"ΔT = {V('P', 'P')} R<sub>th</sub>(1 − e<sup>−{V('t', 't')}/τ</sup>), &nbsp; R<sub>th</sub> = {FR('1', '4' + V('kappa', 'κ') + '<span class=k>a</span>')} + <span class=k>R<sub>paste</sub></span> + <span class=k>R<sub>sink</sub></span>",
  "symbols": [("P", "heater power"), ("κ", "thermal conductivity of the plate"), ("a", "heater contact radius, 1 mm"), ("R_paste, R_sink", "thermal paste and heat sink, 3.0 and 1.5 K/W"), ("τ", "settling time constant")],
  "vars": [{"key": "kappa", "label": "Plate", "unit": "W/(cm·K)", "choices": [["Diamond", 20.0], ["Copper", 4.0], ["Aluminium", 2.37], ["Silicon", 1.5]], "value": 20.0},
           {"key": "P", "label": "Power P", "unit": "W", "min": 0.5, "max": 3, "step": 0.1, "value": 1.5},
           {"key": "t", "label": "Time t", "unit": "s", "min": 0, "max": 180, "step": 1, "value": 60}],
  "auto": "t",
  "levels": {"k": "Heat is like a crowd leaving a stadium. Diamond has the widest exits, so the crowd (the heat) leaves fastest and the heater stays coolest.",
             "s": "A small hot spot on a thick plate sees a spreading resistance 1/(4κa); in series with the paste and sink it sets the steady temperature rise P·R_th. Diamond's κ is about five times copper's, so its spreading term almost vanishes and the paste dominates.",
             "r": "Isothermal disk on a half-space [carslaw1959]; the lumped first-order response with τ = 12 + 30/κ s is a fit to the A3 geometry, not a derivation. The animated map is an explicit 2-D diffusion solve with each material's diffusivity κ/ρc (diamond about 11 cm²/s, copper 1.2)."},
  "refs": ["carslaw1959", "wei1993", "francis2010"], "lab": "labs/heat.html"},

 {"id": "rabi", "group": "Quantum", "exp": "B1", "title": "Rabi oscillation: rotating a qubit with a microwave pulse",
  "tagline": "Hold the microwave on longer and the spin rolls from bright to dark and back: a qubit gate.",
  "tex": r"P_{-1}(\tau) = \frac{\Omega^2}{\Omega^2+\delta^2}\,\sin^2\!\left(\pi\sqrt{\Omega^2+\delta^2}\;\tau\right)",
  "html": f"P<sub>−1</sub> = {FR(V('Om', 'Ω') + '<sup>2</sup>', V('Om', 'Ω') + '<sup>2</sup> + ' + V('de', 'δ') + '<sup>2</sup>')} sin<sup>2</sup>(π<span class=sq>√<span>{V('Om', 'Ω')}<sup>2</sup> + {V('de', 'δ')}<sup>2</sup></span></span> {V('tau', 'τ')})",
  "symbols": [("Ω", "Rabi frequency, set by the microwave power"), ("δ", "detuning of the microwave from the line"), ("τ", "pulse length"), ("P₋₁", "probability of ending in mₛ = −1 (dimmer)")],
  "vars": [{"key": "Om", "label": "Rabi frequency Ω", "unit": "MHz", "min": 1, "max": 20, "step": 0.5, "value": 5},
           {"key": "de", "label": "Detuning δ", "unit": "MHz", "min": -10, "max": 10, "step": 0.5, "value": 0},
           {"key": "tau", "label": "Pulse length τ", "unit": "µs", "min": 0, "max": 1, "step": 0.005, "value": 0.1}],
  "auto": "tau",
  "levels": {"k": "The spin is an arrow on a ball. A microwave pushes it around the ball; leave it on just long enough and the arrow points down: that is a flip, the qubit's NOT gate.",
             "s": "In the rotating frame the drive rotates the Bloch vector about (Ω, 0, δ). On resonance it swings fully from |0⟩ to |−1⟩ every 1/(2Ω): the π pulse. Detuning tilts the axis, so the swing never reaches the bottom and gets faster.",
             "r": "Two-level reduction of the spin-1 (mₛ = 0, −1 subspace), rotating-wave approximation, frequencies in MHz and times in µs so Ω is the Rabi frequency in cycles per µs. Same expression as adamas.nv.rabi without decay; the pulse diagram is the B1 sequence (3 µs initialize, τ, 300 ns readout)."},
  "refs": ["rabi1937", "jelezko2004a", "childress2006"], "lab": "labs/qubit.html"},

 {"id": "ramsey", "group": "Quantum", "exp": "B1", "title": "Ramsey fringes: a clock that runs out of step",
  "tagline": "Two π/2 pulses with a wait between them: the spins fan out and the fringes fade with T₂*.",
  "tex": r"P_0(\tau) = \tfrac12\left[1 + \cos(2\pi\delta\tau)\,e^{-(\tau/T_2^*)^2}\right]",
  "html": f"P<sub>0</sub> = ½[1 + cos(2π{V('de', 'δ')}{V('tau', 'τ')}) e<sup>−({V('tau', 'τ')}/{V('t2s', 'T<sub>2</sub>*')})<sup>2</sup></sup>]",
  "symbols": [("δ", "detuning: how fast the spin precesses in the rotating frame"), ("τ", "free evolution time"), ("T₂*", "dephasing time from the static spread of fields"), ("P₀", "probability of returning to mₛ = 0")],
  "vars": [{"key": "de", "label": "Detuning δ", "unit": "MHz", "min": 0.5, "max": 5, "step": 0.1, "value": 2},
           {"key": "t2s", "label": "Dephasing T₂*", "unit": "µs", "min": 0.2, "max": 3, "step": 0.05, "value": 1},
           {"key": "tau", "label": "Free time τ", "unit": "µs", "min": 0, "max": 3, "step": 0.01, "value": 0.5}],
  "auto": "tau",
  "levels": {"k": "Start a hundred runners together. Each runs at a slightly different speed, so after a while they are spread all around the track and you can no longer tell where the group is.",
             "s": "A π/2 pulse tips the spin onto the equator; it precesses at δ during τ; a second π/2 pulse maps the phase onto population, giving fringes at δ. Every NV in the ensemble sees a slightly different static field, so the phases spread and the fringes decay as exp(−(τ/T₂*)²).",
             "r": "Quasi-static Gaussian detuning distribution with σ = √2/(2πT₂*) gives the Gaussian envelope (exponent p = 2); the animation draws spins sampled from that distribution, so the mean vector's length is the envelope. Same as adamas.nv.ramsey."},
  "refs": ["ramsey1950", "childress2006", "degen2017"], "lab": "labs/qubit.html"},

 {"id": "echo", "group": "Quantum", "exp": "B1", "title": "Spin echo: turning the runners around",
  "tagline": "Flip every spin halfway through and the static spread cancels; only slow noise remains (T₂).",
  "tex": r"C(\tau) = e^{-(\tau/T_2)^{p}},\qquad p \approx 3",
  "html": f"C = e<sup>−({V('tau', 'τ')}/{V('t2', 'T<sub>2</sub>')})<sup>{V('p', 'p')}</sup></sup>",
  "symbols": [("τ", "total free time, with a π pulse at τ/2"), ("T₂", "echo coherence time"), ("p", "stretch exponent; about 3 for a slowly changing carbon-13 bath"), ("C", "echo contrast")],
  "vars": [{"key": "t2", "label": "Echo time T₂", "unit": "µs", "min": 50, "max": 2000, "step": 10, "value": 600},
           {"key": "p", "label": "Exponent p", "unit": "", "min": 1, "max": 4, "step": 0.1, "value": 3},
           {"key": "tau", "label": "Free time τ", "unit": "µs", "min": 0, "max": 2000, "step": 5, "value": 300}],
  "auto": "tau",
  "levels": {"k": "Halfway through the race, everyone turns around and runs back at the same speed. The fast runners had gone further, but they come back faster, so everyone arrives at the start line together.",
             "s": "A π pulse at τ/2 reverses each spin's accumulated phase, so any field that stays constant during the sequence cancels exactly. Only fields that change during τ survive; they set T₂, which is hundreds of times longer than T₂* (milliseconds in isotopically pure diamond at room temperature).",
             "r": "Hahn echo with a slow (Ornstein–Uhlenbeck-like) bath gives exp(−(τ/T₂)³); fast or many-spin baths give smaller p. Room-temperature record 1.8 ms in ¹²C-enriched diamond [balasubramanian2009]. Same as adamas.nv.hahn_echo."},
  "refs": ["hahn1950", "delange2010", "balasubramanian2009"], "lab": "labs/qubit.html"},

 {"id": "vector", "group": "Quantum", "exp": "B2", "title": "A compass with four needles: vector magnetometry",
  "tagline": "Four NV orientations each measure one projection of the field; together they give the whole vector.",
  "tex": r"\Delta f_i = 2\gamma_e\,|\mathbf{B}\cdot\hat{\mathbf n}_i|,\qquad |\mathbf B| = \sqrt{\tfrac34\textstyle\sum_{i=1}^{4}\left(\Delta f_i/2\gamma_e\right)^2}",
  "html": f"Δf<sub>i</sub> = 2<span class=k>γ<sub>e</sub></span>|<b>B</b>·<b>n̂</b><sub>i</sub>|, &nbsp; <b>B</b> = ({V('B', '|B|')}, {V('theta', 'θ')}, {V('phi', 'φ')}) &nbsp;⟹&nbsp; |<b>B</b>| = √(¾ Σ<sub>i</sub> (Δf<sub>i</sub>/2<span class=k>γ<sub>e</sub></span>)<sup>2</sup>)",
  "symbols": [("n̂ᵢ", "the four ⟨111⟩ NV axes, at 109.5° to each other"), ("Δfᵢ", "splitting of the line pair of orientation i"), ("B, θ, φ", "field magnitude, polar and azimuthal angles")],
  "vars": [{"key": "B", "label": "Field |B|", "unit": "mT", "min": 0, "max": 5, "step": 0.05, "value": 2.5},
           {"key": "theta", "label": "Polar angle θ", "unit": "°", "min": 0, "max": 180, "step": 1, "value": 60},
           {"key": "phi", "label": "Azimuth φ", "unit": "°", "min": 0, "max": 360, "step": 1, "value": 30}],
  "auto": "phi",
  "levels": {"k": "The diamond has compass needles pointing four different ways. Each one feels only the part of the magnet's pull along its direction. Read all four and you know exactly which way, and how hard, the magnet pulls.",
             "s": "Each orientation's line pair splits by 2γₑ|B·n̂ᵢ|. Because the four tetrahedral axes satisfy Σ n̂ᵢn̂ᵢᵀ = (4/3)I, the squared projections add up to (4/3)|B|² for any direction: the magnitude comes straight out, and the signs follow from a least-squares fit.",
             "r": "Weak-field (first-order) projections; the sign ambiguity of |B·n̂ᵢ| is resolved by the calibration coils in B2. Off-axis fields add the second-order shift 3γₑ²B⊥²/2D, included in the Lattice Lab spectrum but not in this identity."},
  "refs": ["rondin2014", "barry2020", "doherty2013"], "lab": "labs/lattice.html"},

 {"id": "arrhenius", "group": "Materials", "exp": "B3", "title": "Watch boron wake up: incomplete ionization",
  "tagline": "Boron's holes are bound 0.37 eV deep; heat sets them free and the resistance falls by orders of magnitude.",
  "tex": r"\frac{p\,(p+N_D)}{N_A - N_D - p} = \frac{N_V}{g}\,e^{-E_A/kT},\qquad \rho = \frac{1}{q\,p\,\mu(T)}",
  "html": f"{FR('p(p + ' + V('Nd', 'N<sub>D</sub>') + ')', V('Na', 'N<sub>A</sub>') + ' − ' + V('Nd', 'N<sub>D</sub>') + ' − p')} = {FR('N<sub>V</sub>', '<span class=k>g</span>')} e<sup>−{V('Ea', 'E<sub>A</sub>')}/k{V('T', 'T')}</sup>, &nbsp; ρ = {FR('1', 'q p μ(' + V('T', 'T') + ')')}",
  "symbols": [("p", "free hole density"), ("N_A, N_D", "boron (acceptor) and compensating nitrogen (donor) densities"), ("N_V", "valence-band effective density of states, ∝ T^1.5"),
              ("g", "acceptor degeneracy, 4"), ("E_A", "boron activation energy, 0.37 eV"), ("μ(T)", "hole mobility, 1500 (T/300 K)^−2.2 cm²/V·s")],
  "vars": [{"key": "T", "label": "Temperature T", "unit": "K", "min": 250, "max": 800, "step": 5, "value": 300},
           {"key": "Ea", "label": "Activation E_A", "unit": "eV", "min": 0.05, "max": 0.6, "step": 0.01, "value": 0.37},
           {"key": "Na", "label": "Boron N_A", "unit": "cm⁻³", "min": 16, "max": 19, "step": 0.05, "value": 17.5, "log": True},
           {"key": "Nd", "label": "Nitrogen N_D", "unit": "cm⁻³", "min": 14, "max": 17, "step": 0.05, "value": 16.7, "log": True}],
  "auto": "T",
  "levels": {"k": "In silicon the extra charges are loose at room temperature. In diamond, boron holds on to them tightly; you have to heat the diamond before most of them let go. That is why diamond chips work better when hot.",
             "s": "Charge neutrality with one acceptor level gives a quadratic for p. With E_A = 0.37 eV only a fraction of a percent of boron is ionized at 300 K; heating frees more holes, so the resistivity drops steeply until lattice scattering (μ ∝ T^−2.2) takes over. Silicon's 0.045 eV dopants are fully ionized: slide E_A down to see.",
             "r": "Closed-form root of the single-level neutrality equation [sze2006] with m*_dos = 0.9 m₀ and g = 4 (adamas.doping); in the compensated regime the corrected Arrhenius slope of ln(ρT^−0.7) gives E_A, without compensation about E_A/2 (B3 analysis)."},
  "refs": ["lagrange1998", "pernot2010", "sze2006"], "lab": "explorer.html#ion"},

 {"id": "g2", "group": "Quantum", "exp": "C1", "title": "One photon at a time: antibunching proves a single qubit",
  "tagline": "Split the light onto two detectors: a single NV can never click both at once.",
  "tex": r"g^{(2)}(\tau) = 1 - \rho^2\,e^{-|\tau|/\tau_1},\qquad \rho = \frac{S}{S+B}",
  "html": f"g<sup>(2)</sup>(τ) = 1 − {V('rho', 'ρ')}<sup>2</sup> e<sup>−|τ|/{V('tau1', 'τ<sub>1</sub>')}</sup>, &nbsp; ρ = {FR('S', 'S + B')}",
  "symbols": [("g⁽²⁾(τ)", "normalized rate of photon pairs separated by τ"), ("ρ", "fraction of light from the NV (signal over signal plus background)"), ("τ₁", "antibunching time, about the excited-state lifetime at low power"), ("g⁽²⁾(0) < 0.5", "proof of a single emitter")],
  "vars": [{"key": "rho", "label": "Signal fraction ρ", "unit": "", "min": 0.3, "max": 1, "step": 0.01, "value": 0.9},
           {"key": "tau1", "label": "Time τ₁", "unit": "ns", "min": 5, "max": 30, "step": 0.5, "value": 12}],
  "auto": "rho",
  "levels": {"k": "A single NV center is like a sprinkler that shoots one drop at a time and needs a moment to refill. Put two buckets side by side: they never catch a drop at exactly the same moment.",
             "s": "After emitting, the NV is in its ground state and must be re-excited before it can emit again, so photon pairs at zero delay are missing: a dip in g⁽²⁾(0). Uncorrelated background fills the dip to 1 − ρ²; a dip below 0.5 proves one emitter.",
             "r": "Hanbury Brown–Twiss correlation with a two-level-like recovery e^(−|τ|/τ₁) (bunching from the metastable singlet appears at high power and longer τ). The animation is a stochastic emitter (exponential re-excitation) plus Poisson background on a 50:50 beam splitter; the histogram converges to the formula."},
  "refs": ["kurtsiefer2000", "jelezko2004a", "doherty2013"], "lab": "labs/photon.html"},

 {"id": "fet", "group": "Devices", "exp": "C2", "title": "The diamond transistor: a hole gas under hydrogen",
  "tagline": "Hydrogen-terminated diamond carries a sheet of holes; the gate squeezes it, the drain pulls it.",
  "tex": r"I_D = k\left[(V_{GS}-V_{th})V_{DS} - \tfrac12 V_{DS}^2\right]\ \text{(linear)},\quad I_D = \tfrac{k}{2}(V_{GS}-V_{th})^2\ \text{(saturation)},\quad k = \frac{\mu C_{ox} W}{L}",
  "html": f"I<sub>D</sub> = k[({V('vgs', 'V<sub>GS</sub>')} − <span class=k>V<sub>th</sub></span>){V('vds', 'V<sub>DS</sub>')} − ½{V('vds', 'V<sub>DS</sub>')}<sup>2</sup>] &nbsp;→&nbsp; {FR('k', '2')}({V('vgs', 'V<sub>GS</sub>')} − <span class=k>V<sub>th</sub></span>)<sup>2</sup>, &nbsp; k = {FR(V('mu', 'μ') + '<span class=k>C<sub>ox</sub>W</span>', '<span class=k>L</span>')}",
  "symbols": [("V_GS, V_DS", "gate and drain voltage magnitudes (the p-channel rails are negative in the lab)"), ("V_th", "threshold, 1.5 V"), ("μ", "channel hole mobility"),
              ("C_ox", "gate capacitance per area: 30 nm aluminium oxide"), ("W/L", "100 µm / 2 µm")],
  "vars": [{"key": "vgs", "label": "|V_GS|", "unit": "V", "min": 0, "max": 10, "step": 0.1, "value": 6},
           {"key": "vds", "label": "|V_DS|", "unit": "V", "min": 0, "max": 20, "step": 0.1, "value": 8},
           {"key": "mu", "label": "Mobility μ", "unit": "cm²/V·s", "min": 30, "max": 300, "step": 5, "value": 150}],
  "auto": "vds",
  "levels": {"k": "A transistor is a tap. The gate is the handle: open it more and more charge flows. Push harder with the drain and the flow rises, until the channel pinches and the flow stops growing.",
             "s": "Hydrogen termination plus air or oxide acceptors pull electrons out of diamond, leaving a two-dimensional hole gas a few nanometres under the surface. The square-law model gives a linear region for V_DS < V_GS − V_th and saturation beyond, where the channel pinches off at the drain.",
             "r": "Long-channel square-law model with constant mobility (adamas.logic.Fet, used by the ngspice deck and the DIA-4 cell library); real devices add series resistance, velocity saturation, and surface-acceptor drift. Parameters are those of the C2 expected curves."},
  "refs": ["kawarada2023", "kasu2012", "sze2006"], "lab": "labs/transistor.html"},

 {"id": "gate", "group": "Scale", "exp": "D1", "title": "Two qubits talk: the dipolar gate and its error budget",
  "tagline": "Two NVs 25 nm apart feel each other's field; the gate is slow, so coherence, pulses and charge state all cost fidelity.",
  "tex": r"\nu = \frac{52\ \mathrm{MHz\,nm^3}}{r^3},\quad t_g = \frac{1}{2\nu},\quad F = q^2\left(\frac{1+e^{-(t_g/T_2)^3}}{2}\right)^2 + \frac{1-q^2}{4}",
  "html": f"ν = {FR('<span class=k>52 MHz·nm³</span>', V('r', 'r') + '<sup>3</sup>')}, t<sub>g</sub> = {FR('1', '2ν')}, F = {V('q', 'q')}<sup>2</sup>({FR('1 + e<sup>−(t<sub>g</sub>/' + V('t2', 'T<sub>2</sub>') + ')<sup>3</sup></sup>', '2')})<sup>2</sup> + {FR('1 − ' + V('q', 'q') + '<sup>2</sup>', '4')}",
  "symbols": [("ν", "dipolar coupling (perpendicular geometry)"), ("r", "NV–NV distance"), ("t_g", "controlled-phase gate time"), ("T₂", "echo coherence time of each spin"),
              ("q", "probability that each NV is in the negative charge state and polarized"), ("F", "Bell-state fidelity")],
  "vars": [{"key": "r", "label": "Distance r", "unit": "nm", "min": 8, "max": 40, "step": 0.5, "value": 25},
           {"key": "t2", "label": "Echo T₂", "unit": "µs", "min": 100, "max": 3000, "step": 10, "value": 600},
           {"key": "q", "label": "Preparation q", "unit": "", "min": 0.5, "max": 1, "step": 0.01, "value": 0.75}],
  "auto": "q",
  "levels": {"k": "Two tiny magnets close together can feel each other, very gently. To make them work as a team they need to be close, stay calm long enough, and both be switched on. If one is 'off' a quarter of the time and nobody checks first, the teamwork falls apart.",
             "s": "Magnetic dipole coupling falls as 1/r³: 3.3 kHz at 25 nm, so a gate takes about 150 µs. Echo coherence must survive that long. Even with perfect coherence, if each NV is in the right charge state only with probability q and runs are not pre-selected, the fidelity is capped near q². The 2013 experiment's 0.67 was already normalized to charge-preselected runs, so it is not explained by q; the 2025 record of 96% pre-selects the charge state with a 594 nm laser [joas2025].",
             "r": "Echoed controlled-phase gate, F_coh = (1 + w)²/4 with w = exp(−(t_g/T₂)³), unprepared runs modeled as fully mixed (fidelity ¼). Single-quantum coupling at θ = 90°; the published pair [dolde2013] used double-quantum encoding (4× coupling). The echo exponent 3 assumes a slow ¹³C bath; with p = 1 or two gate applications the coherence limit for that pair drops to about 0.8 (adamas.gate_budget.coherence_limited_range). Addressing: both NVs sit in one laser spot and are told apart by their crystal orientation (audit Q4)."},
  "refs": ["dolde2013", "joas2025", "neumann2010natphys", "aslam2013"], "lab": "explorer.html#gate"},

 {"id": "yield", "group": "Scale", "exp": "D2", "title": "Defects on a wafer: yield and good dies",
  "tagline": "Every killer defect ruins the die it lands on. Bigger dies catch more of them.",
  "tex": r"Y_P = e^{-A D_0},\quad Y_M = \left(\frac{1-e^{-A D_0}}{A D_0}\right)^2,\quad N = \frac{\pi (d/2)^2}{A} - \frac{\pi d}{\sqrt{2A}}",
  "html": f"Y<sub>Murphy</sub> = ({FR('1 − e<sup>−' + V('A', 'A') + V('D0', 'D<sub>0</sub>') + '</sup>', V('A', 'A') + V('D0', 'D<sub>0</sub>'))})<sup>2</sup>, &nbsp; good dies = N·Y, &nbsp; N = {FR('π(' + V('d', 'd') + '/2)<sup>2</sup>', V('A', 'A'))} − {FR('π' + V('d', 'd'), '√(2' + V('A', 'A') + ')')}",
  "symbols": [("A", "die area"), ("D₀", "killer defect density"), ("d", "wafer diameter"), ("Y_P, Y_M", "Poisson and Murphy yield models"), ("N", "gross dies per wafer, with edge loss")],
  "vars": [{"key": "D0", "label": "Defects D₀", "unit": "/cm²", "min": -1, "max": 1.3, "step": 0.02, "value": 0.3, "log": True},
           {"key": "A", "label": "Die area A", "unit": "mm²", "min": 4, "max": 100, "step": 1, "value": 25},
           {"key": "d", "label": "Wafer d", "unit": "mm", "choices": [["2-inch (50 mm)", 50], ["3-inch (76 mm)", 76], ["4-inch (100 mm)", 100]], "value": 76}],
  "auto": "D0",
  "levels": {"k": "Throw sand at a chessboard. Every square hit by a grain is ruined. Small squares often escape; big squares almost always get hit.",
             "s": "Random point defects give the Poisson yield e^(−AD₀); clustering is better described by Murphy's model. Diamond wafers today carry far more killer defects than silicon (about 0.1 per cm² in mature silicon fabs), which is why small dies and power products come first.",
             "r": "Gross dies use the standard edge-loss approximation [plummer2000]; good dies = N·Y_M as in adamas.wafer.good_dies. The animation drops defects uniformly on the usable disk (exactly the Poisson model) and counts the dies hit."},
  "refs": ["murphy1964", "stapper1983", "plummer2000"], "lab": "labs/wafer.html"},

 {"id": "bfom", "group": "Devices", "exp": None, "title": "The power-device limit: Baliga's figure of merit",
  "tagline": "To block more volts a switch needs a thicker, lighter-doped layer; diamond's field strength makes that layer tiny.",
  "tex": r"R_{on,sp} = \frac{4V_B^2}{\varepsilon\,\mu\,E_c^3},\qquad \mathrm{BFOM} = \varepsilon\,\mu\,E_c^3",
  "html": f"R<sub>on,sp</sub> = {FR('4' + V('VB', 'V<sub>B</sub>') + '<sup>2</sup>', V('mat', 'ε μ E<sub>c</sub><sup>3</sup>'))}, &nbsp; W = {FR('2' + V('VB', 'V<sub>B</sub>'), V('mat', 'E<sub>c</sub>'))}",
  "symbols": [("V_B", "breakdown voltage the switch must block"), ("ε", "permittivity"), ("μ", "carrier mobility (holes for diamond today)"), ("E_c", "critical field"), ("W", "drift-layer thickness")],
  "vars": [{"key": "VB", "label": "Blocking V_B", "unit": "V", "min": 2, "max": 4, "step": 0.02, "value": 3.08, "log": True},
           {"key": "mat", "label": "Material", "unit": "", "choices": [["Diamond", "Diamond"], ["Gallium oxide", "Ga2O3"], ["Gallium nitride", "GaN"], ["Silicon carbide", "4H-SiC"], ["Silicon", "Si"]], "value": "Diamond"}],
  "auto": "VB",
  "levels": {"k": "A power switch is a wall that must hold back high voltage when off, and be a wide-open door when on. Diamond can be a very thin wall, and a thin wall is easy to walk through.",
             "s": "The drift layer of a unipolar switch must hold V_B at a peak field E_c: thickness W = 2V_B/E_c and doping ∝ εE_c²/V_B. Its resistance is then 4V_B²/(εμE_c³). E_c enters cubed, so diamond's 10 MV/cm beats silicon's 0.3 MV/cm by a factor of about 37,000 from the field alone.",
             "r": "Ideal one-dimensional punch-through-free drift layer with full ionization [baliga1982] (adamas.power.ron_sp_mohm_cm2). Diamond with holes today; incomplete ionization of boron raises the real value at room temperature (see the B3 scene and the Power Lab)."},
  "refs": ["baliga1982", "isberg2002", "kimoto2014"], "lab": "labs/power.html"},

 {"id": "surface", "group": "Scale", "exp": None, "title": "Error correction: the surface-code threshold",
  "tagline": "Below threshold, every step up in code distance multiplies the protection.",
  "tex": r"p_L \approx 0.1\left(\frac{p}{p_{th}}\right)^{(d+1)/2},\qquad n = 2d^2 - 1",
  "html": f"p<sub>L</sub> ≈ 0.1({FR(V('p', 'p'), '<span class=k>p<sub>th</sub></span>')})<sup>({V('d', 'd')} + 1)/2</sup>, &nbsp; n = 2{V('d', 'd')}<sup>2</sup> − 1",
  "symbols": [("p", "physical error rate per operation"), ("p_th", "threshold, about 1%"), ("d", "code distance (odd)"), ("p_L", "logical error per round"), ("n", "physical qubits per logical qubit")],
  "vars": [{"key": "p", "label": "Physical error p", "unit": "", "min": -4, "max": -1.7, "step": 0.02, "value": -2.7, "log": True},
           {"key": "d", "label": "Distance d", "unit": "", "min": 3, "max": 25, "step": 2, "value": 7}],
  "auto": "p",
  "levels": {"k": "Copy a secret onto many noisy notes and take a careful vote. If each note is only rarely wrong, adding more notes makes the vote almost never wrong. If notes are wrong too often, more notes just add more mistakes.",
             "s": "A distance-d surface code fails only when about (d+1)/2 errors line up across the lattice. Below threshold (p < p_th ≈ 1%) each increase of d by 2 multiplies the suppression by p_th/p, at a cost of 2d² − 1 qubits.",
             "r": "Heuristic scaling [fowler2012] with prefactor 0.1 (adamas.qec); the framework's circuit-level Stim and PyMatching tables (adamas.resource) replace it for the machine estimate, including the native XZZX code under biased noise."},
  "refs": ["fowler2012", "dennis2002", "kitaev2003"], "lab": "labs/qec.html"},
]


# ---------------- Python evaluations of every browser function, for the cross-check -------------------------------
def golden() -> dict:
    """Python model values at fixed inputs; the node tests require the JavaScript to match them."""
    from . import coupling, doping, gate_budget, nv, qec, wafer
    from .logic import Fet
    from .materials import MATERIALS
    from .power import ron_sp_mohm_cm2
    out: dict = {}
    out["odmr"] = [[b, th, list(nv.transition_frequencies_mhz((b * math.sin(math.radians(th)), 0.0, b * math.cos(math.radians(th)))))]
                   for b in (0.0, 1.0, 3.0, 10.0) for th in (0, 30, 90)]
    out["rabi"] = [[om, de, t, float(nv.rabi(t, om, de))] for om in (2.0, 5.0) for de in (0.0, 3.0) for t in (0.05, 0.1, 0.37)]
    out["ramsey"] = [[de, t2s, t, float(nv.ramsey(t, de, t2s))] for de in (1.0, 2.0) for t2s in (0.5, 1.0) for t in (0.2, 0.9)]
    out["echo"] = [[t2, p, t, float(nv.hahn_echo(t, t2, p))] for t2 in (300.0, 600.0) for p in (2.0, 3.0) for t in (100.0, 500.0)]
    out["doping"] = [[ea, na, nd, T, doping.free_carriers_cm3(doping.Dopant("x", "C", "acceptor", ea, 4, 0.9, ()), na, T, nd)]
                     for ea in (0.045, 0.37) for na, nd in ((1e17, 0.0), (3e17, 5e16)) for T in (300.0, 500.0, 750.0)]
    fet = [Fet(mu_cm2_vs=mu, vth=1.5, w_um=100) for mu in (150.0, 60.0)]
    out["fet"] = [[f.mu_cm2_vs, vgs, vds, f.current(vgs, vds)] for f in fet for vgs in (1.0, 5.0, 9.0) for vds in (1.0, 6.0, 15.0)]
    out["gate"] = [[r, t2, q, gate_budget.GateBudget(r_nm=r, t2star_us=1e9, t2_us=t2, echo=True, q_prep=q).fidelity, float(coupling.dipolar_coupling_khz(r))]
                   for r in (15.0, 25.0) for t2 in (300.0, 1800.0) for q in (0.75, 1.0)]
    out["yield"] = [[d, a, d0, wafer.dies_per_wafer(d, a), wafer.poisson_yield(a, d0), wafer.murphy_yield(a, d0), wafer.good_dies(d, a, d0)]
                    for d in (50.0, 76.0) for a in (4.0, 25.0, 100.0) for d0 in (0.1, 2.0)]
    out["bfom"] = [[k, vb, ron_sp_mohm_cm2(MATERIALS[k], vb, "p" if k == "Diamond" else "n")] for k in ("Si", "4H-SiC", "Diamond") for vb in (600.0, 3300.0)]
    out["surface"] = [[p, d, qec.surface_code_logical_error(p, d), qec.surface_code_qubits(d)] for p in (1e-3, 5e-3) for d in (3, 7, 11)]
    out["gamma_mhz_per_mt"] = nv.GAMMA_MHZ_PER_MT
    out["dipolar_mhz_nm3"] = float(coupling.DIPOLAR_MHZ_NM3)
    return out


def materials_json() -> dict:
    """Constants for the power scene: relative permittivity, the carrier mobility used (holes for diamond), Ec."""
    from .materials import MATERIALS
    return {k: {"name": m.name, "eps_r": m.eps_r, "mu": m.mu_p if k == "Diamond" else m.mu_n, "ec_mv_cm": m.ec_mv_cm, "carrier": "holes" if k == "Diamond" else "electrons"}
            for k, m in MATERIALS.items()}


def to_json() -> dict:
    from .experiments import EXPERIMENTS, TIERS
    ex = {e["id"]: e for e in EXPERIMENTS}
    scenes = []
    for s in SCENES:
        e = ex.get(s["exp"])
        extra = {"experiment": {"id": e["id"], "tier": e["tier"], "tier_name": TIERS[e["tier"]]["name"], "color": TIERS[e["tier"]]["color"], "title": e["title"],
                                "cost": list(e["cost"]), "steps": [[t, d] for t, d, _ in e["steps"]], "result": e["expected"]}} if e else {}
        scenes.append({**s, "symbols": [list(x) for x in s["symbols"]], **extra})
    return {"groups": GROUPS, "scenes": scenes, "materials": materials_json()}


def to_markdown() -> str:
    from .experiments import EXPERIMENTS, TIERS
    ex = {e["id"]: e for e in EXPERIMENTS}
    site = "https://normansrule.github.io/adamas-diamond-framework"
    L = ["# Equations in action", "",
         "_Generated from `adamas/action.py` (`adamas build docs`). Interactive version with animations and live sliders: "
         f"[action.html]({site}/action.html)._", "",
         "Fourteen equations that run the framework, each paired with the experiment that measures it. On the web page every symbol is a "
         "slider: move it and the symbol glows, the numbers are plugged in, the animation changes, and the curve redraws. Press **Play** and the "
         "page sweeps the variable for you.", "", "![Fourteen equations in action](../img/fig53_equations_in_action.png)", "",
         "| # | Scene | Equation | Experiment | Try it |", "|---|---|---|---|---|"]
    for i, s in enumerate(SCENES, 1):
        e = ex.get(s["exp"])
        exp = f"{e['id']} · tier {e['tier']} ({TIERS[e['tier']]['name']})" if e else "framework"
        head = s["tex"].split(QQ)[0].split(r",\quad")[0].replace("|", r"\vert ")
        L.append(f"| {i} | {s['title']} | ${head}$ | {exp} | [open]({site}/action.html#{s['id']}) |")
    L.append("")
    for i, s in enumerate(SCENES, 1):
        e = ex.get(s["exp"])
        L += [f"## {i}. {s['title']}", "", f"*{s['tagline']}*", "", "$$", s["tex"], "$$", "",
              "| Symbol | Meaning |", "|---|---|"] + [f"| {a} | {b} |" for a, b in s["symbols"]] + [""]
        L += [f"**In plain words.** {s['levels']['k']}", "", f"**How it works.** {s['levels']['s']}", "", f"**Model details.** {s['levels']['r']}", ""]
        if e:
            lo, hi = e["cost"]
            L += [f"**Measure it yourself:** experiment {e['id']}, *{e['title']}* (tier {e['tier']}, about US${lo:,} to {hi:,}); "
                  f"steps in [EXPERIMENTS.md](../experiments/EXPERIMENTS.md#{e['id'].lower()}--{_anchor(e['title'])}).", ""]
        L += [f"**Interactive:** [{site}/action.html#{s['id']}]({site}/action.html#{s['id']}) · related lab: [{s['lab']}]({site}/{s['lab']}) · "
              f"sources: {' '.join(f'[{k}]' for k in s['refs'])}", ""]
    return "\n".join(L) + "\n"


def _anchor(title: str) -> str:
    import re
    return re.sub(r"[^a-z0-9 -]", "", title.lower()).replace(" ", "-")


def write(path: str = "docs/EQUATIONS_IN_ACTION.md") -> str:
    from pathlib import Path
    p = Path(path); p.write_text(to_markdown(), encoding="utf-8"); return str(p)


def write_golden(path: str = "web/tests/action_golden.json") -> str:
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / path
    p.write_text(json.dumps(golden(), indent=1) + "\n", encoding="utf-8"); return str(p)
