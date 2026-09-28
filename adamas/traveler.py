"""ADAMAS process traveler T1: hydrogen-terminated diamond transistors (PDK-0) with optional NV-qubit windows.

A step-by-step run sheet for a university or pilot cleanroom. It is the single source for docs/process/TRAVELER.md,
the interactive web traveler (process.html), and Figures 41 to 43. Every step lists purpose, equipment, parameters
with literature anchors, in-line checks with pass criteria, safety, failure modes, and what silicon does instead.

How to read the numbers. Parameters are STARTING POINTS drawn from the cited literature, not a qualified recipe: every
tool differs, and each value must be tuned on your line with the test structures of the PDK-0 monitor die (chapter E2).
Pass criteria marked "ADAMAS" are this repository's engineering targets, derived from its models; those with a key come
from the cited paper. Safety notes summarize hazards; they do not replace your facility's training and procedures.
"""
from __future__ import annotations

VARIANTS = {
    "power": {"name": "Power switch (EV, grid, data center)", "skip": ["S06", "S07", "S18"],
              "note": "High-temperature ALD (option B) for 400 °C and kilovolt operation, or NO₂ + low-temperature ALD (option A) for the highest current."},
    "rf": {"name": "RF power amplifier (5G, radar, space)", "skip": ["S06", "S07", "S18"],
           "note": "NO₂ doping + thin low-temperature ALD (option A); gate length 0.1 to 1 µm by electron-beam lithography."},
    "hot_logic": {"name": "High-temperature / radiation-hard logic", "skip": ["S06", "S07", "S12", "S18"],
                  "note": "No NO₂ (it desorbs when hot); high-temperature ALD (option B); E/D logic cells of PDK-0."},
    "sensor": {"name": "NV quantum sensor (magnetometer)", "skip": ["S08", "S09", "S10", "S11", "S12", "S13", "S14", "S15", "S16", "S17"],
               "note": "Material and NV steps only: dense ensemble implant, oxygen surface, optical and microwave test."},
    "qubit": {"name": "Room-temperature qubit register chip", "skip": ["S12"],
              "note": "Full flow with ¹²C cap, aperture implant, photocurrent electrodes on the QELEC layer; no NO₂ near qubits."},
}

MODULES = [("M0", "Incoming", "#8b98a5"), ("M1", "Clean and grow", "#ffc46b"), ("M2", "Quantum option", "#ff5d6c"),
           ("M3", "Transistor front end", "#2de2e6"), ("M4", "Back end", "#9d7bff"), ("M5", "Test and ship", "#48e5a3")]

# check: (name, unit, low, high, source); low/high None = open bound; unit "" with low=high=None = pass/fail checkbox
STEPS = [
 {"id": "S01", "short": "Inspect", "module": "M0", "title": "Incoming substrate inspection", "t_max_c": 25,
  "why": "Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers.",
  "equipment": ["Optical microscope with differential interference contrast", "Cross-polarized imaging (birefringence)", "Raman spectrometer (532 nm)", "Atomic force microscope"],
  "params": [("Orientation", "(100), miscut under 3°", "[friel2009]"), ("Grade", "Electronic-grade CVD (N < 5 ppb) for qubits; heteroepitaxial or HPHT acceptable for power", "[friel2009] [schreck2017]"),
             ("Size", "3 × 3 mm plates up to 3-inch wafers", "[e6orbray2026]")],
  "checks": [("Raman 1332 cm⁻¹ line width", "cm⁻¹", None, 3.0, "ADAMAS"), ("Surface roughness Ra (AFM, 5 × 5 µm)", "nm", None, 1.0, "ADAMAS"),
             ("No scratches or pits visible at 50×", "", None, None, "ADAMAS")],
  "safety": ["Handle with plastic or diamond-safe tweezers; edges chip."],
  "failures": [("Broad Raman line or strong birefringence", "High dislocation or strain density", "Reject for devices; use for process development only")],
  "silicon": "Silicon wafers arrive with sub-nanometer roughness and near-zero dislocations; inspection is statistical, not per piece."},
 {"id": "S02", "short": "Acid clean", "module": "M1", "title": "Oxidizing acid clean", "t_max_c": 200,
  "why": "Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface.",
  "equipment": ["Dedicated wet bench for hot oxidizing acids", "Quartz beaker and hot plate", "Ultrasonic solvent bath"],
  "params": [("Acid mixture", "Boiling H₂SO₄ : HNO₃ : HClO₄ (1:1:1, 'tri-acid') or H₂SO₄ : HNO₃ (3:1) where perchloric use is not permitted", "[sangtawesin2019]"),
             ("Temperature and time", "About 170 to 200 °C, 30 min to several hours", "[sangtawesin2019]"),
             ("Follow-up", "DI water rinse, acetone and isopropanol ultrasonic 10 min each, N₂ dry", "")],
  "checks": [("Water contact angle (oxygen-terminated: hydrophilic)", "°", None, 30.0, "ADAMAS"), ("No residue under dark-field microscopy", "", None, None, "ADAMAS")],
  "safety": ["Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive.", "Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics."],
  "failures": [("Hydrophobic patches remain", "Incomplete oxidation or organic film", "Repeat clean; extend time")],
  "silicon": "Silicon uses the RCA clean and a dilute-HF dip to strip native oxide; diamond has no native oxide to strip."},
 {"id": "S03", "short": "Epi growth", "module": "M1", "title": "Homoepitaxial buffer growth (MPCVD)", "t_max_c": 950,
  "why": "Buries polishing damage and substrate impurities under fresh, controlled diamond; for qubits a ¹²C-enriched cap removes the nuclear-spin bath.",
  "equipment": ["Microwave plasma CVD reactor (2.45 GHz)", "Pyrometer", "Mass-flow controllers for H₂, CH₄ (¹²CH₄ for qubits)"],
  "params": [("Pre-growth H₂ plasma etch", "10 to 30 min to remove subsurface damage", "[tallaire2013]"),
             ("Gas", "CH₄/H₂ about 0.5 to 4%; residual nitrogen below 1 ppm (electronic grade below 200 ppb)", "[lu2013] [bolshakov2020] [teraji2015]"),
             ("Pressure, temperature", "About 100 to 300 Torr, 800 to 1000 °C substrate", "[lu2013] [bolshakov2020]"),
             ("Thickness", "1 to 5 µm for devices; 50 to 100 nm ¹²C cap for qubits", "[teraji2015] [balasubramanian2009]")],
  "checks": [("Hillock density (DIC microscope)", "cm⁻²", None, 1000.0, "ADAMAS"), ("PL: no SiV (737 nm) or strong NV (637 nm) signal from the layer", "", None, None, "ADAMAS"),
             ("Layer thickness", "µm", 1.0, 5.0, "ADAMAS")],
  "safety": ["Hydrogen and methane are flammable: leak-checked lines, gas detectors, interlocked exhaust.", "Microwave leakage check after any maintenance."],
  "failures": [("Unepitaxial crystallites / hillocks", "Too much CH₄ or dirty substrate", "Lower CH₄, longer H₂ etch, better clean"),
               ("Strong NV or SiV photoluminescence", "Nitrogen leak or silicon from quartz window", "Leak-check, purify gas, shield quartz")],
  "silicon": "Silicon epitaxy (CVD from silane or trichlorosilane) is routine at 300 mm; diamond growth is slow and small."},
 {"id": "S04", "short": "Re-clean", "module": "M1", "title": "Post-growth clean and inspection", "t_max_c": 200,
  "why": "Growth leaves a hydrogen-terminated, possibly graphitic surface; a second oxidizing clean restores the oxygen-terminated reference state for lithography.",
  "equipment": ["As S02"], "params": [("Recipe", "Repeat S02", "[sangtawesin2019]")],
  "checks": [("Water contact angle", "°", None, 30.0, "ADAMAS")], "safety": ["As S02."],
  "failures": [("Film delaminates in acid", "Stress from growth", "Anneal or regrow thinner")],
  "silicon": "No equivalent: silicon's native oxide makes the surface state predictable."},
 {"id": "S05", "short": "Marks", "module": "M1", "title": "Etched alignment marks", "t_max_c": 120,
  "why": "Every later mask, including the nanoscale nitrogen apertures, aligns to these. They must be etched into diamond because the NV anneal (S07) exceeds gold's melting point (1064 °C).",
  "equipment": ["Optical or electron-beam lithography", "Hard mask evaporator (Al or SiO₂)", "Inductively coupled O₂/Ar plasma etcher"],
  "params": [("Mask", "Al or SiO₂ hard mask, lift-off", ""), ("Etch", "O₂/Ar inductively coupled plasma, 200 to 500 nm deep", "[hauf2011]"), ("Strip", "Mask wet etch, then S02 clean", "")],
  "checks": [("Mark depth (profilometer)", "nm", 150.0, 600.0, "ADAMAS"), ("Marks visible in the electron-beam tool", "", None, None, "ADAMAS")],
  "safety": ["Plasma tools: standard interlocks; chlorine-free recipes only."],
  "failures": [("Micromasking pillars in the etched field", "Sputtered mask material", "Lower bias power; cleaner mask")],
  "silicon": "Silicon uses the same idea (zero-level marks), usually etched into the wafer."},
 {"id": "S06", "short": "N implant", "module": "M2", "title": "Nitrogen implantation through apertures", "t_max_c": 25,
  "why": "Places nitrogen where qubits are wanted (layer QIMPLANT of PDK-0). Depth and dose set how many NV centers form and how close they sit to the surface.",
  "equipment": ["Electron-beam lithography (PMMA apertures, 20 to 50 nm)", "Low-energy ion implanter with ¹⁵N⁺ source", "SRIM for depth planning"],
  "params": [("Isotope", "¹⁵N⁺ (distinguishes implanted from native ¹⁴N)", "[pezzagna2010]"),
             ("Energy", "2.5 to 10 keV → about 5 to 15 nm mean depth", "[pezzagna2010] [ziegler2010]"),
             ("Dose", "10⁸ to 10¹¹ cm⁻² for single centers; up to 10¹³ cm⁻² for sensing ensembles", "[pezzagna2010]")],
  "checks": [("Aperture diameter (SEM of test field)", "nm", 10.0, 60.0, "ADAMAS"), ("Implant dose logged", "", None, None, "ADAMAS")],
  "safety": ["Ion implanter: radiation (X-ray) interlocks and high voltage."],
  "failures": [("Too few or too many NV per site", "Dose or aperture size", "Calibrate conversion yield on the witness array; adjust dose")],
  "silicon": "Silicon implants dopants the same way, but at 10¹⁴ to 10¹⁵ cm⁻² and for electrical, not quantum, purposes."},
 {"id": "S07", "short": "NV anneal", "module": "M2", "title": "Vacancy anneal and oxygen re-termination", "t_max_c": 1100,
  "why": "Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit.",
  "equipment": ["High-vacuum furnace (below 10⁻⁶ mbar) or forming-gas furnace", "Tri-acid bench (S02)"],
  "params": [("Anneal", "800 to 1100 °C, 1 to 3 h, high vacuum (prevents surface etching)", "[pezzagna2010]"),
             ("Yield to expect", "About 1% at 2.5 to 5 keV, rising with energy", "[pezzagna2010]"),
             ("Re-termination", "Tri-acid clean (S02) → oxygen surface; NV⁻ stable near the surface", "[hauf2011] [sangtawesin2019]")],
  "checks": [("NV conversion yield (confocal count ÷ implanted N)", "%", 0.5, None, "[pezzagna2010]"),
             ("Echo T₂ of shallow NV (depth about 10 nm)", "µs", 10.0, None, "ADAMAS"), ("NV⁻ fraction under green light", "", 0.7, None, "[aslam2013]")],
  "safety": ["Furnace hot-zone burns; vacuum implosion shielding."],
  "failures": [("Low yield, dark surface layer", "Residual oxygen etched the surface during anneal", "Better vacuum; lower temperature; forming gas"),
               ("Short T₂", "Surface spins or implant damage", "Higher anneal temperature, oxygen annealing, deeper NV")],
  "silicon": "Silicon's implant anneal activates dopants (rapid thermal anneal around 1000 °C); here the anneal manufactures a defect on purpose."},
 {"id": "S08", "short": "H₂ plasma", "module": "M3", "title": "Hydrogen termination (H₂ plasma)", "t_max_c": 800,
  "why": "Creates the C–H surface whose negative electron affinity lets adsorbed acceptors pull electrons out, leaving the two-dimensional hole gas that is the transistor channel. No dopant atoms are involved.",
  "equipment": ["MPCVD reactor in pure H₂"],
  "params": [("Plasma", "Pure H₂, about 600 to 800 °C, 5 to 30 min", "[kawarada2023]"), ("Cool-down", "In H₂ to below about 300 °C before venting", "[kawarada2023]")],
  "checks": [("Water contact angle (hydrophobic)", "°", 75.0, None, "ADAMAS"), ("Sheet resistance in air (Van der Pauw)", "kΩ/sq", 3.0, 30.0, "ADAMAS")],
  "safety": ["As S03 (hydrogen plasma)."],
  "failures": [("High sheet resistance", "Incomplete termination or exposure to oxidizers", "Repeat plasma; store in clean N₂; proceed to S09 within hours")],
  "silicon": "No equivalent. Silicon channels form by inversion under the gate, not by surface chemistry."},
 {"id": "S09", "short": "Gold", "module": "M3", "title": "Blanket gold deposition", "t_max_c": 80,
  "why": "Gold forms a low-resistance contact to the hole gas and protects the fragile C–H surface from every later resist and solvent.",
  "equipment": ["Electron-beam evaporator"],
  "params": [("Film", "About 100 nm Au directly on C–H, no adhesion layer", "[kawarada2023]")],
  "checks": [("Au thickness (crystal monitor)", "nm", 80.0, 120.0, "ADAMAS")],
  "safety": ["Evaporator high voltage and X-rays; standard training."],
  "failures": [("Gold peels during lift-off or tape test", "Contaminated surface", "Shorten time between S08 and S09; gentler resist strip")],
  "silicon": "Silicon forms contacts by silicidation (Ni, Co, Ti) after doping the source and drain."},
 {"id": "S10", "short": "Mask 1 isolate", "module": "M3", "title": "Mask 1 (OHMIC + ISO): gold pattern and oxygen-plasma isolation", "t_max_c": 120,
  "why": "Gold is removed everywhere except the device areas; the uncovered C–H is converted to C–O by an oxygen plasma, which kills the hole gas. One mask isolates every transistor and returns the NV windows to an oxygen surface.",
  "equipment": ["Mask aligner or laser writer (PDK-0 layers OHMIC and ISO)", "KI/I₂ gold etchant", "O₂ plasma asher or UV-ozone"],
  "params": [("Gold etch", "KI/I₂ at room temperature until clear", "[kawarada2023]"), ("Isolation", "Low-power O₂ plasma or UV-ozone, a few minutes", "[kawarada2014]")],
  "checks": [("Leakage between isolated pads at 20 V", "nA", None, 1.0, "ADAMAS"), ("NV windows oxygen-terminated (contact angle below 30°)", "", None, None, "ADAMAS")],
  "safety": ["Iodine-based etchant stains and irritates: gloves, goggles."],
  "failures": [("Pads short together", "Incomplete oxidation or gold residue", "Extend plasma; inspect at 100×")],
  "silicon": "Silicon isolates devices with shallow-trench isolation: etch, oxide fill, and chemical-mechanical polish."},
 {"id": "S11", "short": "Mask 2 gate gap", "module": "M3", "title": "Mask 2 (GATE opening): self-aligned channel", "t_max_c": 120,
  "why": "Opening a gap in the gold defines the channel length; the gold on either side becomes source and drain, self-aligned to the channel.",
  "equipment": ["Optical lithography (gaps above 1 µm) or electron-beam lithography (0.1 to 1 µm)", "KI/I₂"],
  "params": [("Gap", "2 µm (PDK-0 rule) for logic; 0.1 to 1 µm for RF", "[kawarada2023]")],
  "checks": [("Channel length (SEM)", "µm", 0.1, 10.0, "ADAMAS"), ("No gold residue in the gap", "", None, None, "ADAMAS")],
  "safety": ["As S10."],
  "failures": [("Undercut widens the gap", "Over-etch", "Time the etch; calibrate on test gaps")],
  "silicon": "Silicon uses a self-aligned polysilicon or metal gate, with implants aligned to it."},
 {"id": "S12", "short": "NO₂", "module": "M3", "title": "NO₂ exposure (option A, high-current devices)", "t_max_c": 25,
  "why": "NO₂ is a strong surface acceptor: it raises the hole density toward 10¹⁴ cm⁻², lowering on-resistance. It must be locked in immediately by the ALD cap (S13).",
  "equipment": ["Sealed exposure chamber with 2% NO₂ in N₂", "Gas cabinet with NO₂ detector"],
  "params": [("Gas", "2% NO₂ in N₂, room temperature", "[kasu2012] [hirama2012]"), ("Saturation", "Hole density saturates near 9 × 10¹³ cm⁻² above about 300 ppm", "[sato2013]"),
             ("Duration", "Until the sheet resistance of a test structure saturates", "[kubovic2009]")],
  "checks": [("Sheet resistance after exposure (from the saturated hole density of [sato2013] and a typical mobility)", "kΩ/sq", 0.5, 5.0, "ADAMAS")],
  "safety": ["NO₂ is highly toxic: gas cabinet, continuous monitoring, exhausted enclosure, buddy system."],
  "failures": [("Resistance recovers after exposure", "NO₂ desorbs before capping", "Minimize delay to ALD; low-temperature ALD first cycles")],
  "silicon": "No equivalent. Silicon doping is by implantation and anneal."},
 {"id": "S13", "short": "ALD Al₂O₃", "module": "M3", "title": "Atomic-layer-deposited Al₂O₃ gate insulator and passivation", "t_max_c": 450,
  "why": "Al₂O₃ is both the gate insulator and the cap that stabilizes the hole gas. Deposition temperature sets the trade-off: hot ALD survives high-temperature operation; cold ALD keeps NO₂.",
  "equipment": ["Thermal ALD (trimethylaluminium + H₂O)", "Ellipsometer and silicon witness piece"],
  "params": [("Option A (with NO₂)", "≤ 150 °C, about 10 nm", "[kasu2012] [hirama2012]"),
             ("Option B (high temperature, high voltage)", "About 450 °C, 100 to 200 nm; enables 400 °C operation and about 2 kV", "[kawarada2014] [kawarada2017]")],
  "checks": [("Thickness on witness (ellipsometry)", "nm", 8.0, 220.0, "ADAMAS"), ("C–V hysteresis on MOS capacitor", "V", None, 0.5, "ADAMAS")],
  "safety": ["Trimethylaluminium is pyrophoric: sealed source, trained operators, never open to air."],
  "failures": [("Large C–V hysteresis", "Traps at the interface or in the oxide", "Adjust temperature; post-deposition anneal within the thermal budget")],
  "silicon": "Silicon also uses ALD high-κ oxides (HfO₂) at advanced nodes, over a thin SiO₂ interface layer."},
 {"id": "S14", "short": "Mask 3 gate", "module": "M4", "title": "Mask 3 (GATE metal)", "t_max_c": 120,
  "why": "The gate electrode sits on Al₂O₃ over the channel and must overlap the gap on both sides so the whole channel is controlled.",
  "equipment": ["Lithography", "Evaporator", "Lift-off bath"],
  "params": [("Metal", "Al, Au, or Ti/Au (for example 10/80 nm)", "[kasu2012] [kawarada2023]"), ("Overlap", "At least 2 λ beyond the gap (PDK-0 rule)", "")],
  "checks": [("Gate leakage at maximum gate voltage", "µA/mm", None, 1.0, "ADAMAS")],
  "safety": ["Solvents for lift-off: fume hood."],
  "failures": [("Gate shorts to source or drain", "ALD pinholes or misalignment", "Thicker ALD; check overlay")],
  "silicon": "Similar: metal gate definition, but silicon uses gate-last replacement flows at advanced nodes."},
 {"id": "S15", "short": "Mask 4 vias", "module": "M4", "title": "Mask 4 (VIA): open Al₂O₃ over contacts", "t_max_c": 25,
  "why": "Contacts need bare gold; the oxide is removed only where pads and probes land.",
  "equipment": ["Lithography", "Buffered oxide etch (HF-based)"],
  "params": [("Etch", "10:1 buffered oxide etch, timed to the ALD thickness", "")],
  "checks": [("Via resistance (Kelvin structure)", "Ω", None, 1.0, "ADAMAS")],
  "safety": ["Hydrofluoric acid: HF-specific training, calcium gluconate gel at hand, never work alone."],
  "failures": [("Open vias", "Under-etch", "Extend etch; check with a probe on a test pad")],
  "silicon": "Silicon opens contacts through a thick dielectric by plasma etch, then fills tungsten plugs."},
 {"id": "S16", "short": "Mask 5 metal", "module": "M4", "title": "Mask 5 (METAL2): interconnect and pads", "t_max_c": 120,
  "why": "Connects transistors into cells and brings every node to probe pads; the photocurrent electrodes and microwave line for qubits (QELEC) are drawn here too.",
  "equipment": ["Lithography", "Evaporator", "Lift-off"],
  "params": [("Metal", "Ti/Au, for example 20/130 nm", "")],
  "checks": [("Line resistance on the serpentine monitor", "Ω/sq", None, 0.5, "ADAMAS"), ("Comb-to-serpentine leakage", "nA", None, 1.0, "[stapper1983]")],
  "safety": ["As S14."],
  "failures": [("Opens on the serpentine", "Particles or lift-off tearing", "Clean room discipline; bilayer resist")],
  "silicon": "Silicon uses a copper damascene stack with ten or more layers."},
 {"id": "S17", "short": "Parametric test", "module": "M5", "title": "Parametric test (PDK-0 monitor die)", "t_max_c": 400,
  "why": "Turns the wafer into numbers that calibrate every ADAMAS model: contact resistance, sheet resistance, threshold voltages, mismatch, defect density, and gate delay.",
  "equipment": ["Probe station with hot chuck (to 400 °C)", "Semiconductor parameter analyzer", "C–V meter", "Oscilloscope for ring oscillators"],
  "params": [("Structures", "TLM, van der Pauw, MOS capacitor, FET array (W/L × 4), serpentine-comb, ring oscillators", "[liu2017]"),
             ("Temperatures", "25, 200, and 300 °C (to 400 °C for option B)", "[kawarada2014]")],
  "checks": [("Contact resistance (TLM)", "Ω·mm", None, 10.0, "ADAMAS"), ("On/off current ratio", "", 1e6, None, "ADAMAS"),
             ("Ring-oscillator period vs ADAMAS model", "ratio", 0.5, 2.0, "ADAMAS"), ("Threshold spread σ(V_T) on 4-device groups", "mV", None, 200.0, "[pelgrom1989]")],
  "safety": ["Hot chuck burns; high-voltage breakdown tests only behind shields."],
  "failures": [("Threshold drift during hot test", "Mobile charge or NO₂ desorption", "Use option B oxide for hot operation")],
  "silicon": "Same idea: process-control monitors in the scribe lines of every wafer."},
 {"id": "S18", "short": "Quantum test", "module": "M5", "title": "Quantum test (NV windows)", "t_max_c": 25,
  "why": "Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5.",
  "equipment": ["Confocal microscope (532 nm excitation, 650 to 800 nm detection)", "Microwave source and stripline", "Photocurrent amplifier (optional)"],
  "params": [("Sequence", "ODMR, Rabi, Hahn echo, charge-state PL spectrum (575 nm NV⁰, 637 nm NV⁻ zero-phonon lines)", "[doherty2013] [aslam2013]")],
  "checks": [("ODMR contrast (single NV)", "%", 15.0, None, "[gruber1997]"), ("Echo T₂", "µs", 10.0, None, "ADAMAS"), ("NV⁻ fraction", "", 0.7, None, "[aslam2013]")],
  "safety": ["Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear."],
  "failures": [("Low NV⁻ fraction", "Residual C–H or surface band bending near windows", "Re-oxidize windows; keep QIMPLANT at least 5 µm from channels (PDK rule)")],
  "silicon": "No equivalent in silicon CMOS."},
 {"id": "S19", "short": "Dice, package", "module": "M5", "title": "Dicing and high-temperature packaging", "t_max_c": 350,
  "why": "Diamond's advantage is operating hot; the package must not become the limit.",
  "equipment": ["Laser dicing", "Die bonder", "Wire bonder (Au)"],
  "params": [("Dicing", "Laser scribing (diamond cannot be sawn economically)", ""), ("Die attach", "Au–Sn eutectic or sintered silver for above 200 °C", "[lutz2018]")],
  "checks": [("Post-dicing chipping at edges", "µm", None, 20.0, "ADAMAS"), ("Wire-bond pull strength", "gf", 3.0, None, "ADAMAS")],
  "safety": ["Laser dicing fumes: local extraction."],
  "failures": [("Die attach voids", "Poor wetting on diamond", "Metallize back side (Ti/Pt/Au)")],
  "silicon": "Silicon is sawn with blades and packaged with organic die-attach limited to about 150 to 175 °C."},
]

# Cross-section model: (name, x0, x1, y_top, height, color, first_step, last_step_exclusive or None, label)
XS = [
 ("sub", 40, 860, 250, 100, "#1a3b55", "S01", None, "diamond substrate (100)"),
 ("epi", 40, 860, 232, 18, "#24607a", "S03", None, "homoepitaxial layer"),
 ("mark1", 55, 85, 232, 12, "#05070d", "S05", None, "etched mark"), ("mark2", 815, 845, 232, 12, "#05070d", "S05", None, ""),
 ("CO0", 40, 860, 229, 3, "#ffc46b", "S02", "S08", "C–O surface"),
 ("N", 700, 760, 238, 6, "#ffa45b", "S06", "S07", "implanted ¹⁵N"),
 ("NV", 700, 760, 238, 6, "#ff5d6c", "S07", None, "NV centers"),
 ("CH", 40, 860, 229, 3, "#6ff3ff", "S08", "S10", "C–H surface"),
 ("holes", 40, 860, 234, 3, "holes", "S08", "S10", "2-D hole gas"),
 ("CHdev", 140, 600, 229, 3, "#6ff3ff", "S10", None, "C–H (device)"),
 ("holesdev", 140, 600, 234, 3, "holes", "S10", None, "2-D hole gas"),
 ("COl", 40, 140, 229, 3, "#ffc46b", "S10", None, "C–O (isolation)"), ("COr", 600, 860, 229, 3, "#ffc46b", "S10", None, "C–O (isolation + NV window)"),
 ("Aub", 40, 860, 196, 33, "gold", "S09", "S10", "Au (100 nm)"),
 ("Aud", 140, 600, 196, 33, "gold", "S10", "S11", "Au"),
 ("AuS", 140, 330, 196, 33, "gold", "S11", None, "source"), ("AuD", 410, 600, 196, 33, "gold", "S11", None, "drain"),
 ("NO2", 330, 410, 222, 7, "no2", "S12", None, "NO₂"),
 ("ox1", 40, 860, 180, 16, "#9d7bff", "S13", None, "Al₂O₃ (ALD)"), ("ox2", 330, 410, 196, 33, "#9d7bff", "S13", None, ""),
 ("gate", 345, 395, 124, 56, "#b9c4d0", "S14", None, "gate"),
 ("via1", 205, 255, 180, 16, "#0b1320", "S15", None, "via"), ("via2", 485, 535, 180, 16, "#0b1320", "S15", None, ""),
 ("pad1", 190, 270, 110, 86, "#48e5a3", "S16", None, "Ti/Au pad"), ("pad2", 470, 550, 110, 86, "#48e5a3", "S16", None, ""),
 ("probe1", 225, 235, 20, 90, "#e8f1f8", "S17", "S18", "probe"), ("probe2", 505, 515, 20, 90, "#e8f1f8", "S17", "S18", ""),
 ("laser", 715, 745, 20, 210, "#48e5a3", "S18", "S19", "532 nm"),
 ("cut1", 30, 36, 20, 330, "#ff5d8f", "S19", None, "laser scribe"), ("cut2", 864, 870, 20, 330, "#ff5d8f", "S19", None, ""),
]

ORDER = [s["id"] for s in STEPS]


def step_index(sid: str) -> int:
    return ORDER.index(sid)


def visible(shape, k: int) -> bool:
    a = step_index(shape[6]); b = step_index(shape[7]) if shape[7] else len(ORDER)
    return a <= k < b


def thermal_violations() -> list[str]:
    """Steps after gold deposition must stay below 500 °C (gold diffusion, hole-gas stability); growth and NV anneal
    must precede the first metal. Returns human-readable violations (empty list = consistent flow)."""
    out, first_metal = [], step_index("S09")
    for k, s in enumerate(STEPS):
        if k >= first_metal and s["t_max_c"] > 500:
            out.append(f"{s['id']} at {s['t_max_c']} °C after gold")
    return out


def to_json() -> dict:
    return {"steps": STEPS, "xs": XS, "variants": VARIANTS, "modules": MODULES, "order": ORDER}


def to_markdown() -> str:
    L = ["# Process traveler T1: diamond transistors with optional NV windows",
         "",
         "_Generated from `adamas/traveler.py` (`make traveler`); edit the Python, not this file. Interactive version: "
         "[process.html](https://normansrule.github.io/adamas-diamond-framework/process.html)._",
         "",
         "**Read this first.** Parameters are starting points from the cited literature, not a qualified recipe; tune each on your "
         "tools with the PDK-0 monitor die ([E2](../expert/E2_process_integration_and_pdk.md)). Pass criteria marked ADAMAS are this "
         "repository's targets. Safety notes summarize hazards and never replace your facility's training.",
         "",
         "![Process flow](../img/fig41_process_flow.png)",
         "",
         "## Variants",
         "",
         "| Variant | Steps skipped | Note |", "|---|---|---|"]
    L += [f"| {v['name']} | {', '.join(v['skip']) or '–'} | {v['note']} |" for v in VARIANTS.values()]
    L += ["", "![Thermal budget](../img/fig42_thermal_budget.png)", "", "![Cross-sections](../img/fig43_cross_sections.png)", ""]
    mod = {m[0]: m[1] for m in MODULES}
    for s in STEPS:
        L += [f"## {s['id']} · {s['title']}", "", f"*Module: {mod[s['module']]} · peak temperature {s['t_max_c']} °C*", "", f"**Why.** {s['why']}", "",
              "**Equipment.** " + "; ".join(s["equipment"]) + ".", "", "| Parameter | Starting point | Source |", "|---|---|---|"]
        L += [f"| {a} | {b} | {c or 'ADAMAS'} |" for a, b, c in s["params"]]
        L += ["", "| Check | Pass criterion | Source |", "|---|---|---|"]
        for name, unit, lo, hi, src in s["checks"]:
            crit = "pass / fail" if lo is None and hi is None else (f"≥ {lo:g} {unit}" if hi is None else f"≤ {hi:g} {unit}" if lo is None else f"{lo:g} to {hi:g} {unit}")
            L.append(f"| {name} | {crit.strip()} | {src} |")
        L += ["", "**Safety.** " + " ".join(s["safety"]), ""]
        L += ["| Symptom | Likely cause | Action |", "|---|---|---|"] + [f"| {a} | {b} | {c} |" for a, b, c in s["failures"]]
        L += ["", f"**Silicon, for comparison.** {s['silicon']}", ""]
    return "\n".join(L) + "\n"


def write(path: str = "docs/process/TRAVELER.md") -> str:
    from pathlib import Path
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(to_markdown(), encoding="utf-8"); return str(p)
