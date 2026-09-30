"""ADAMAS experiments: ten hands-on experiments in four price tiers, from a kitchen table to a pilot line.

Tier A, about US$100 to 500: see NV fluorescence, record an ODMR spectrum, weigh a magnet with light, race heat
spreaders. Tier B, about US$1,000 to 10,000: pulsed spin control (Rabi, Ramsey, echo), vector magnetometry, dopant
activation. Tier C, about US$10,000 to 100,000: single NV centers and photon antibunching; making and testing a diamond
transistor with a university cleanroom. Tier D, above US$100,000 up to tens of millions: a two-qubit register at room
temperature and a diamond pilot line.

Every experiment has a parts list with approximate 2026 US-dollar price ranges (street prices for generic parts; verify
with vendors), safety notes, numbered steps, the analysis to do, and simulated expected results computed from this
package's models so you know what a working setup should show. The 3-D scene descriptions drive the interactive
Experiments page. Designs for tier A follow published teaching setups [stegemann2023] [williams2026]; tier B follows
[sewani2020].
"""
from __future__ import annotations
import math

import numpy as np

TIERS = {
    "A": {"name": "Kitchen table", "range": "US$100 to 500", "color": "#48e5a3", "who": "high school, outreach, first-year labs, home"},
    "B": {"name": "Teaching lab", "range": "US$1,000 to 10,000", "color": "#2de2e6", "who": "upper-division undergraduate and master's labs"},
    "C": {"name": "Research lab", "range": "US$10,000 to 100,000", "color": "#9d7bff", "who": "graduate research groups, shared facilities"},
    "D": {"name": "Facility", "range": "US$100,000 to tens of millions", "color": "#ff5d6c", "who": "national labs, companies, consortia"},
}

# scene components: (name, kind, [x, y, z] in cm, size, color); kinds are drawn by web/experiments.html
EXPERIMENTS = [
 {"id": "A1", "tier": "A", "title": "See the qubit glow, then hear it resonate (ODMR)", "cost": (150, 400), "time": "one afternoon", "skill": "soldering, basic Python",
  "goal": "Watch NV centers glow red under green light, then sweep a microwave source through 2.87 GHz and see the glow dip: optically detected magnetic resonance.",
  "learn": ["Spin-dependent fluorescence (why mₛ = 0 is bright)", "The zero-field splitting D = 2.87 GHz", "Lock-free signal averaging"],
  "parts": [("NV-rich diamond", "Microdiamond powder or a small HPHT plate with high NV density (irradiated and annealed)", 50, 250),
            ("Green source", "High-power green LED (safer, visible) or a laser module under 1 mW at 532 nm", 10, 60),
            ("Red filter", "Longpass filter near 600 to 650 nm, or red filter foil", 5, 80),
            ("Photodetector", "Silicon photodiode with a JFET-input transimpedance amplifier (for example TL082)", 10, 40),
            ("Microwave source", "PLL synthesizer board covering 2.7 to 3.0 GHz (ADF4351-class)", 30, 60),
            ("Antenna", "Short microstrip line or a copper wire loop under the diamond", 5, 20),
            ("Controller", "Raspberry Pi Pico (or any microcontroller with SPI, ADC, and USB); ready-made firmware in hardware/a1_odmr", 5, 40),
            ("Mechanics", "3-D printed cube mounts or a breadboard; neodymium magnet", 10, 50)],
  "safety": ["Even a 1 mW green laser can damage eyes: never look into the beam; use a phone camera to align. The LED version avoids laser hazards.",
             "Microwave powers here are milliwatts; keep the antenna enclosed and away from the body anyway."],
  "steps": [("Mount the diamond on the antenna", "Glue the diamond (or a spot of powder) onto the microstrip or inside the loop; the microwave field must reach it.", ["diamond", "antenna"]),
            ("Illuminate", "Point the green source at the diamond from a few millimeters. Through the red filter you see red fluorescence: NV centers emitting.", ["source", "diamond", "filter"]),
            ("Detect", "Place the filter and photodiode to collect the red light; check that the amplifier output rises when the green light is on.", ["filter", "detector"]),
            ("Sweep", "Step the synthesizer from 2800 to 2940 MHz in 0.5 MHz steps, averaging the detector at each step. With the ADAMAS firmware: python hardware/a1_odmr/host.py --port <port>.", ["mw", "mcu"]),
            ("Find the dip", "Plot detector signal versus frequency. A dip of about 0.5 to 3% near 2870 MHz is ODMR. Average longer if it is buried in noise.", ["mcu"]),
            ("Split it", "Bring the magnet closer: the single dip splits into up to eight (four NV orientations × two), moving apart as the field grows.", ["magnet"])],
  "analysis": "Fit Lorentzians to the dips. The center is D ≈ 2870 MHz; each pair splits by 2γB∥ with γ = 28 MHz/mT. Compare with the Lattice Lab.",
  "expected": "odmr_ensemble", "lab": "labs/lattice.html", "refs": ["stegemann2023", "williams2026", "gruber1997", "doherty2013"],
  "scene": [("source", "led", [-12, 3, 0], 1.2, "#48e5a3"), ("diamond", "diamond", [0, 0.6, 0], 0.6, "#6ff3ff"), ("antenna", "loop", [0, 0.2, 0], 1.6, "#d98c3a"),
            ("pcb", "pcb", [0, 0, 0], 6, "#1d6b3a"), ("filter", "filter", [7, 2, 0], 1.6, "#ff5d6c"), ("detector", "box", [11, 2, 0], 1.6, "#8b98a5"),
            ("mw", "board", [-3, 0.2, -7], 3, "#2c6e8f"), ("mcu", "board", [6, 0.2, -7], 3, "#2a7a4b"), ("magnet", "magnet", [0, 1.2, 6], 1.2, "#c0c0c0")],
  "beams": {"green": [[-12, 3, 0], [0, 0.8, 0]], "red": [[0, 0.8, 0], [7, 2, 0], [11, 2, 0]]}},
 {"id": "A2", "tier": "A", "title": "Weigh a magnet with light", "cost": (0, 50), "time": "one hour (uses the A1 setup)", "skill": "A1 completed",
  "goal": "Measure how the ODMR splitting shrinks as a magnet moves away, and recover the inverse-cube law of a dipole field.",
  "learn": ["Zeeman splitting 2γB", "Dipole fields fall as 1/r³", "Calibrating a sensor"],
  "parts": [("Ruler or printed rail", "Millimeter scale along the magnet axis", 0, 10), ("Second magnet (optional)", "Different size to compare dipole moments", 0, 20),
            ("Non-magnetic stand", "Wood or plastic; no steel near the diamond", 0, 20)],
  "safety": ["Neodymium magnets pinch fingers and wipe cards; keep them apart from electronics and pacemakers."],
  "steps": [("Align the magnet", "Place the magnet on the rail, pointing at the diamond, starting 3 cm away.", ["magnet", "rail"]),
            ("Record a spectrum", "Sweep as in A1 and note the frequencies of the outermost dip pair.", ["diamond", "mcu"]),
            ("Step the distance", "Repeat at 3, 4, 5, 6, 8, and 10 cm.", ["magnet", "rail"]),
            ("Plot log-log", "Plot splitting against distance on log-log axes; fit a straight line.", ["mcu"])],
  "analysis": "The slope should be close to −3. The intercept gives the magnet's dipole moment; a 10 mm N52 cube is about 1.2 A·m².",
  "expected": "magnet_distance", "lab": "labs/lattice.html", "refs": ["rondin2014", "doherty2013"],
  "scene": [("diamond", "diamond", [0, 0.6, 0], 0.6, "#6ff3ff"), ("pcb", "pcb", [0, 0, 0], 6, "#1d6b3a"), ("rail", "rail", [0, 0.2, 10], 14, "#caa36a"),
            ("magnet", "magnet", [0, 1.2, 6], 1.2, "#c0c0c0"), ("mcu", "board", [6, 0.2, -7], 3, "#2a7a4b")],
  "beams": {}},
 {"id": "A3", "tier": "A", "title": "Heat-spreader race: diamond against copper, aluminium, and silicon", "cost": (100, 350), "time": "one afternoon", "skill": "basic electronics",
  "goal": "Put the same heater on plates of four materials and record how hot the heater gets. Diamond, with about five times copper's conductivity, keeps it coolest.",
  "learn": ["Thermal conductivity and spreading resistance", "Why GaN amplifiers sit on diamond", "Lumped thermal RC time constants"],
  "parts": [("CVD diamond heat-spreader plate", "About 10 × 10 × 0.5 mm, thermal grade", 50, 200), ("Copper, aluminium plates", "Same size", 5, 15),
            ("Silicon piece", "Broken wafer piece, same size", 0, 20), ("Heater", "Surface-mount power resistor (for example 1 Ω, 2 W) with a small contact area", 2, 10),
            ("Temperature sensors", "Thermocouples or thermistors, or a low-cost thermal camera", 10, 150), ("Supply", "Bench or USB-C supply with current reading", 20, 60),
            ("Heat sink", "Aluminium block under all plates", 5, 20)],
  "safety": ["The heater can exceed 100 °C: do not touch; limit power; never leave unattended."],
  "steps": [("Assemble", "Put each plate on the heat sink with thin thermal paste; bond the heater to the center of the plate.", ["plate", "sink", "heater"]),
            ("Instrument", "Attach a sensor to the heater and one to the plate edge.", ["sensor"]),
            ("Power on", "Apply the same power (for example 1.5 W) to each in turn; log temperature every second for 3 minutes.", ["supply"]),
            ("Compare", "Plot heater temperature rise against time for all four plates.", ["sensor"])],
  "analysis": "At steady state the heater's rise scales roughly as the inverse of the plate's conductivity (plus the paste and sink). Diamond gives the smallest rise and the fastest settling.",
  "expected": "heat_spreaders", "lab": "labs/heat.html", "refs": ["wei1993", "carslaw1959", "francis2010"],
  "scene": [("sink", "block", [0, -1, 0], 10, "#9aa6b2"), ("plate", "plate", [0, 0.1, 0], 4, "#6ff3ff"), ("heater", "box", [0, 0.5, 0], 0.8, "#ff9a3c"),
            ("sensor", "probe", [2, 1.5, 0], 0.3, "#ffd166"), ("supply", "box", [-8, 1, -5], 3, "#3b4656")],
  "beams": {}},
 {"id": "B1", "tier": "B", "title": "Pulsed control: Rabi oscillations, Ramsey fringes, and spin echo", "cost": (3000, 10000), "time": "two to four lab sessions", "skill": "RF, optics alignment, Python",
  "goal": "Drive the NV spin with timed microwave pulses and read it out with timed laser pulses, turning the spin into a qubit you can rotate and measure.",
  "learn": ["Rabi frequency and π pulses", "T₂* from Ramsey fringes", "T₂ from spin echo"],
  "parts": [("NV ensemble plate", "CVD or HPHT, 1 to 10 ppm NV", 300, 1500), ("532 nm laser", "Tens of mW, with an acousto-optic modulator or direct modulation", 500, 2500),
            ("Optics", "Lenses, mirrors, 600 nm longpass and 900 nm shortpass filters, kinematic mounts", 400, 1500),
            ("Photodetector", "Amplified silicon photodiode or avalanche photodiode", 150, 1000), ("Microwave chain", "Synthesizer, fast RF switch, 1 to 10 W amplifier, circulator or dump", 800, 3000),
            ("Pulse timing", "FPGA board (for example Red Pitaya) or a pulse generator with 10 ns resolution", 300, 1500), ("Coils", "Bias coils or a permanent magnet on a translation stage", 100, 500)],
  "safety": ["Class 3B laser: enclosed beam path, wavelength-rated goggles, interlock.", "Amplified microwaves at watts: terminate every output, never run an open amplifier."],
  "steps": [("Polarize and read", "Program: 3 µs laser pulse (initialize), wait, microwave pulse of length τ, 300 ns laser readout window.", ["laser", "fpga"]),
            ("Find resonance", "Run continuous ODMR (A1) to find a line; bias field so one NV class is separated.", ["mw", "coils"]),
            ("Rabi", "Sweep τ from 0 to 1 µs: the readout oscillates; half a period is the π pulse.", ["mw", "detector"]),
            ("Ramsey", "π/2, wait τ, π/2 with a small detuning: fringes that decay with T₂*.", ["mw", "detector"]),
            ("Echo", "π/2, τ/2, π, τ/2, π/2: the decay envelope gives T₂, far longer than T₂*.", ["mw", "detector"])],
  "analysis": "Fit a damped cosine to Rabi, a decaying cosine to Ramsey (T₂*), and exp(−(τ/T₂)ⁿ) to echo. Compare with the Qubit Lab.",
  "expected": "pulsed", "lab": "labs/qubit.html", "refs": ["sewani2020", "jelezko2004a", "hahn1950", "childress2006"],
  "scene": [("laser", "laser", [-14, 2, 0], 1.4, "#2d2d2d"), ("aom", "box", [-9, 2, 0], 1, "#6b7c8f"), ("lens", "lens", [-3, 2, 0], 1.4, "#bfe9ff"),
            ("diamond", "diamond", [0, 2, 0], 0.6, "#6ff3ff"), ("antenna", "loop", [0, 1.4, 0], 1.6, "#d98c3a"), ("dichroic", "dichroic", [-5.5, 2, 0], 1.6, "#9fd8ff"),
            ("filter", "filter", [-5.5, 2, 4], 1.4, "#ff5d6c"), ("detector", "box", [-5.5, 2, 8], 1.6, "#8b98a5"), ("mw", "box", [4, 0.5, -7], 2.4, "#2c6e8f"),
            ("fpga", "board", [-4, 0.2, -8], 3, "#8a3f2c"), ("coils", "coils", [0, 2, 0], 4.5, "#c77d2e")],
  "beams": {"green": [[-14, 2, 0], [0, 2, 0]], "red": [[0, 2, 0], [-5.5, 2, 0], [-5.5, 2, 8]]}},
 {"id": "B2", "tier": "B", "title": "Vector magnetometry with three-axis coils", "cost": (1000, 3000), "time": "two lab sessions", "skill": "B1 or A1 completed",
  "goal": "Apply known fields in three directions and recover the full field vector from the eight ODMR lines of the four NV orientations.",
  "learn": ["The four ⟨111⟩ NV axes", "Least-squares fitting of a vector", "Sensor calibration"],
  "parts": [("Helmholtz coil set", "Three orthogonal pairs, a few mT", 400, 1500), ("Current supplies", "Three channels, 0 to 3 A", 300, 1000), ("Single-crystal NV plate", "Known crystal orientation", 300, 800)],
  "safety": ["Coils heat up at high current: monitor temperature and limit duty cycle."],
  "steps": [("Calibrate each axis", "Apply current to one coil pair at a time; record the eight line positions.", ["coils"]),
            ("Unknown field", "Set an arbitrary combination of currents; record the spectrum.", ["coils", "detector"]),
            ("Fit", "Fit the field vector that best reproduces all eight lines; compare with the coil calibration.", ["mcu"])],
  "analysis": "The line pair of each orientation gives |B·n̂ᵢ|; four orientations over-determine the three components. Residuals test the model.",
  "expected": "vector", "lab": "labs/lattice.html", "refs": ["rondin2014", "barry2020", "doherty2013"],
  "scene": [("diamond", "diamond", [0, 2, 0], 0.6, "#6ff3ff"), ("coils", "coils3", [0, 2, 0], 6, "#c77d2e"), ("detector", "box", [0, 2, 9], 1.6, "#8b98a5"),
            ("mcu", "board", [7, 0.2, -6], 3, "#2a7a4b")],
  "beams": {"green": [[-12, 2, 0], [0, 2, 0]], "red": [[0, 2, 0], [0, 2, 9]]}},
 {"id": "B3", "tier": "B", "title": "Watch boron wake up: dopant activation in diamond", "cost": (1500, 6000), "time": "two lab sessions", "skill": "four-point measurement, hot stage",
  "goal": "Measure the resistance of lightly boron-doped single-crystal diamond from room temperature to about 500 °C and extract the 0.37 eV acceptor energy from an Arrhenius plot.",
  "learn": ["Deep dopants and incomplete ionization", "Arrhenius analysis", "Why diamond electronics improve when hot"],
  "parts": [("Boron-doped single-crystal diamond", "[B] about 10¹⁷ cm⁻³ with some compensating nitrogen (about 10¹⁶ to 10¹⁷ cm⁻³), four Ti/Pt/Au contacts", 800, 3500),
            ("Hot stage", "To about 500 °C, in air or nitrogen", 300, 1500), ("Source-measure unit or precision source + meter", "Nanoampere to milliampere", 300, 2000),
            ("Probes and wiring", "High-temperature probes", 100, 400)],
  "safety": ["Hot stage burns; use tongs and heat-resistant gloves.", "Heavily doped electrode-grade material behaves almost like a metal and will not show activation: use lightly doped samples."],
  "steps": [("Contact check", "Verify ohmic contacts with I–V at room temperature (straight line through zero).", ["probes"]),
            ("Heat in steps", "Step 25 to 500 °C in 25 °C steps; wait for stability; record resistance in both current directions.", ["stage", "smu"]),
            ("Arrhenius plot", "Plot ln(R) against 1000/T and fit the straight part.", ["smu"])],
  "analysis": "A raw Arrhenius slope underestimates the acceptor energy because the density of states grows as T^1.5 and the lattice mobility falls as about T^-2.2; fit ln(R·T^-0.7) instead. In the compensated regime the corrected slope gives E_A ≈ 0.37 eV (without compensation it approaches E_A/2). A Hall measurement separates density from mobility directly.",
  "expected": "arrhenius", "lab": "explorer.html#ion", "refs": ["lagrange1998", "sze2006", "pernot2010"],
  "scene": [("stage", "block", [0, -0.5, 0], 6, "#a64b2a"), ("sample", "plate", [0, 0.3, 0], 2, "#3f7fbf"), ("probes", "probe4", [0, 1.5, 0], 2, "#e8f1f8"),
            ("smu", "box", [-9, 1, -5], 3.5, "#3b4656")],
  "beams": {}},
 {"id": "C1", "tier": "C", "title": "One qubit at a time: single NV centers and photon antibunching", "cost": (30000, 100000), "time": "weeks to build, days per measurement", "skill": "confocal microscopy, photon counting",
  "goal": "Build a confocal microscope that sees individual NV centers, prove each is a single quantum emitter by photon antibunching, and measure its hyperfine-resolved resonance.",
  "learn": ["Confocal imaging", "Hanbury Brown–Twiss correlation g⁽²⁾(τ)", "Nuclear-spin hyperfine structure"],
  "parts": [("Oil or air objective", "Numerical aperture 0.9 to 1.4", 1500, 8000), ("Scanning", "Galvo mirrors or a piezo stage", 3000, 20000),
            ("Single-photon detectors", "Two silicon avalanche photodiodes in Geiger mode", 6000, 20000), ("Time tagger", "Picosecond-resolution correlator", 5000, 20000),
            ("Laser and optics", "532 nm, fiber coupling, pinhole, filters", 3000, 15000), ("Electronic-grade diamond", "Low-nitrogen CVD with sparse NV", 500, 3000),
            ("Microwave and control", "Arbitrary waveform generator, amplifier", 5000, 30000)],
  "safety": ["Class 3B/4 laser; fiber ends and objective focus are especially hazardous.", "Immersion oil: keep off optics other than the objective."],
  "steps": [("Scan", "Raster-scan a 20 × 20 µm field; isolated bright spots are NV candidates.", ["galvo", "objective"]),
            ("Correlate", "Park on a spot; split fluorescence onto two detectors; histogram photon-pair delays.", ["spad1", "spad2", "tagger"]),
            ("Check g⁽²⁾(0)", "A dip below 0.5 at zero delay proves a single emitter.", ["tagger"]),
            ("Resolve hyperfine", "Low-power ODMR on that NV shows three lines 2.16 MHz apart from the ¹⁴N nucleus.", ["mw"])],
  "analysis": "Fit g⁽²⁾(τ) = 1 − (1 − g₀) e^(−|τ|/τ₁); background lifts g₀ above zero. The hyperfine triplet is the nuclear memory used in chapter E5.",
  "expected": "single_nv", "lab": "labs/photon.html", "refs": ["kurtsiefer2000", "gruber1997", "jelezko2004a", "doherty2013"],
  "scene": [("laser", "laser", [-14, 4, 0], 1.4, "#2d2d2d"), ("galvo", "box", [-7, 4, 0], 1.4, "#6b7c8f"), ("dichroic", "dichroic", [-10, 4, 0], 1.6, "#9fd8ff"),
            ("objective", "objective", [0, 5.5, 0], 1.4, "#c9ced6"), ("diamond", "diamond", [0, 2.8, 0], 0.6, "#6ff3ff"), ("stage", "block", [0, 1.8, 0], 5, "#4d5a68"),
            ("spad1", "box", [-10, 4, 9], 1.3, "#8b98a5"), ("spad2", "box", [-6, 4, 12], 1.3, "#8b98a5"), ("tagger", "board", [-2, 0.2, 12], 3, "#35467a"), ("mw", "box", [7, 1, -6], 2.4, "#2c6e8f")],
  "beams": {"green": [[-14, 4, 0], [-10, 4, 0], [-7, 4, 0], [0, 7.5, 0], [0, 2.8, 0]], "red": [[0, 2.8, 0], [0, 7.5, 0], [-10, 4, 0], [-10, 4, 9]]}},
 {"id": "C2", "tier": "C", "title": "Make and test a diamond transistor (university cleanroom)", "cost": (10000, 50000), "time": "one to three months", "skill": "cleanroom training",
  "goal": "Run process traveler T1 (power variant) on one or two plates in a university cleanroom and measure transistor and ring-oscillator curves on a hot chuck.",
  "learn": ["Surface transfer doping in practice", "Transistor parameter extraction", "Why hot operation matters"],
  "parts": [("Single-crystal plates", "3 × 3 to 5 × 5 mm, (100)", 1000, 6000), ("Cleanroom access", "Tool-time fees for lithography, evaporation, ALD, plasma", 5000, 30000),
            ("Hydrogen plasma", "MPCVD time at a partner lab", 1000, 5000), ("Probe station and analyzer", "Often available in the department", 0, 10000)],
  "safety": ["All cleanroom hazards in the process traveler: perchloric and hydrofluoric acids, NO₂, trimethylaluminium, plasmas."],
  "steps": [("Plan the run", "Pick the variant in docs/process/APPLICATIONS.md; draw the PDK-0 monitor die (make layout).", ["plate"]),
            ("Run the traveler", "Follow S01 to S17 in process.html, logging every check.", ["fab"]),
            ("Test", "Measure TLM, MOS capacitor, transistor, and ring oscillator at 25 and 200 °C.", ["prober"]),
            ("Calibrate the models", "Enter the measured parameters into adamas.logic and the SPICE models (projects P-3, D-2).", ["prober"])],
  "analysis": "Extract threshold voltage, mobility, contact resistance, and ring-oscillator stage delay; compare with the Transistor Lab and the ngspice deck.",
  "expected": "fet_curves", "lab": "process.html", "refs": ["kawarada2023", "kasu2012", "liu2017"],
  "scene": [("fab", "reactor", [-6, 2, 0], 4, "#9aa6b2"), ("plate", "plate", [4, 0.5, 0], 2, "#6ff3ff"), ("prober", "prober", [4, 1.5, 0], 3, "#c9ced6")],
  "beams": {}},
 {"id": "D1", "tier": "D", "title": "Two entangled qubits at room temperature", "cost": (500000, 2000000), "time": "one to three years", "skill": "research group",
  "goal": "Implant NV pairs about 25 nm apart, find coupled pairs, and entangle them with echoed dipolar gates, reproducing and then improving on the 2013 result.",
  "learn": ["Nanoscale implantation", "Dipolar two-qubit gates", "Why charge-state preparation limits fidelity"],
  "parts": [("Implantation", "Aperture implantation or scanning-probe implantation of ¹⁵N", 100000, 800000), ("Confocal setups", "Two-color, with charge-state readout", 150000, 400000),
            ("Control electronics", "Multi-channel arbitrary waveform generators, amplifiers", 100000, 300000), ("Materials", "Isotopically purified ¹²C diamond", 20000, 100000)],
  "safety": ["Institutional laser, radiation (implanter), and high-voltage programs."],
  "steps": [("Place pairs", "Implant through 20 nm apertures; anneal; tri-acid clean (traveler S06, S07).", ["implanter"]),
            ("Find pairs", "Measure the dipolar splitting; keep pairs with 5 to 20 kHz coupling.", ["confocal"]),
            ("Entangle", "Echoed gate sequence; Bell-state tomography.", ["awg"]),
            ("Beat the budget", "Add charge-state verification before the gate; compare with the adamas.gate_budget prediction.", ["confocal"])],
  "analysis": "Fidelity against preparation probability q follows the chapter E5 budget: 0.67 at q ≈ 0.75, rising toward 0.998 as q → 1.",
  "expected": "bell_q", "lab": "explorer.html#gate", "refs": ["dolde2013", "dolde2014", "aslam2013", "pezzagna2010"],
  "scene": [("implanter", "implanter", [-8, 2, 0], 6, "#6b7c8f"), ("confocal", "prober", [5, 1.5, 0], 3, "#c9ced6"), ("awg", "rack", [10, 3, -5], 4, "#2a3446")],
  "beams": {}},
 {"id": "D2", "tier": "D", "title": "A diamond pilot line on 3-inch wafers", "cost": (5000000, 50000000), "time": "years", "skill": "company or consortium",
  "goal": "Run PDK-0 on 3-inch heteroepitaxial wafers with statistical process control, and measure how many working dies each wafer yields.",
  "learn": ["Yield and defect density", "Statistical process control", "Cost per good die"],
  "parts": [("MPCVD reactors", "Wafer-scale growth", 1000000, 10000000), ("Lithography and deposition", "Steppers, e-beam, evaporators, ALD, etchers", 2000000, 20000000),
            ("Metrology", "Defect inspection, Raman mapping, probe cards", 1000000, 10000000), ("Wafers", "3-inch single-crystal, per year", 500000, 5000000)],
  "safety": ["Full semiconductor-fab environmental health and safety program."],
  "steps": [("Baseline", "Run the monitor die on every wafer; track each check of the traveler as a control chart.", ["line"]),
            ("Yield learning", "Map killer defects; compare good dies with the Poisson and Murphy models.", ["wafer"]),
            ("Product", "Move to the product variant with the best economics (power or sensors first).", ["line"])],
  "analysis": "Good dies per wafer versus defect density and die size, as in the Wafer Lab; cost per good die sets which products are viable.",
  "expected": "good_dies", "lab": "labs/wafer.html", "refs": ["e6orbray2026", "murphy1964", "stapper1983", "kim2021"],
  "scene": [("line", "reactor", [-8, 2, 0], 4, "#9aa6b2"), ("wafer", "wafer", [3, 0.5, 0], 3.8, "#6ff3ff"), ("stepper", "rack", [9, 3, -4], 4, "#2a3446")],
  "beams": {}},
]


# ---------------- expected results (simulated from the package models) ----------------
def _rng(seed=4):
    return np.random.default_rng(seed)


def expected(kind: str) -> dict:
    from . import doping, gate_budget, nv, wafer
    r = _rng()
    if kind == "odmr_ensemble":
        f = np.linspace(2790, 2950, 321)
        clean0 = nv.odmr_spectrum(f, np.zeros(3), contrast=0.012, linewidth_mhz=6.0, hyperfine=False)
        clean1 = nv.odmr_spectrum(f, np.array([1.1, 0.9, 1.9]), contrast=0.012, linewidth_mhz=6.0, hyperfine=False)
        return {"x": f.tolist(), "series": {"no magnet": (clean0 + r.normal(0, 0.0012, f.size)).tolist(), "magnet near (offset −0.04 for clarity)": (clean1 + r.normal(0, 0.0012, f.size) - 0.04).tolist()},
                "model": {"magnet near": (clean1 - 0.04).tolist()}, "xlabel": "Microwave frequency (MHz)", "ylabel": "Red fluorescence (normalized)"}
    if kind == "magnet_distance":
        d = np.array([3, 4, 5, 6, 8, 10.0]); m = 1.2
        b_mt = 1e-7 * 2 * m / (d / 100) ** 3 * 1e3
        split = 2 * 28.025 * b_mt * 0.85
        meas = split * (1 + r.normal(0, 0.05, d.size))
        return {"x": d.tolist(), "series": {"measured": meas.tolist(), "dipole law": split.tolist()}, "xlabel": "Magnet distance (cm)", "ylabel": "Outer line splitting (MHz)", "log": True}
    if kind == "heat_spreaders":
        t = np.linspace(0, 180, 181); P = 1.5
        out = {}
        for name, k in [("aluminium", 2.37), ("copper", 4.0), ("silicon", 1.5), ("diamond", 20.0)]:
            r_th = 1 / (4 * k * 0.1) + 3.0 + 1.5                              # spreading (heater radius 1 mm) + paste + sink, K/W
            tau = 12 + 30 / k
            out[name] = (P * r_th * (1 - np.exp(-t / tau)) + r.normal(0, 0.05, t.size)).tolist()
        return {"x": t.tolist(), "series": out, "xlabel": "Time (s)", "ylabel": "Heater temperature rise (K)"}
    if kind == "pulsed":
        tr = np.linspace(0, 1.0, 101); tm = np.linspace(0, 3.0, 151); te = np.linspace(0, 600, 61)
        rabi = 0.5 * (1 - np.cos(2 * np.pi * 5 * tr) * np.exp(-tr / 0.8)) * 0.1 + r.normal(0, 0.004, tr.size)
        ram = 0.5 * (1 - np.cos(2 * np.pi * 3 * tm) * np.exp(-(tm / 0.6) ** 2)) * 0.1 + r.normal(0, 0.004, tm.size)
        echo = 0.1 * np.exp(-(te / 300) ** 1.5) + r.normal(0, 0.003, te.size)
        return {"panels": {"Rabi (µs)": [tr.tolist(), rabi.tolist()], "Ramsey (µs)": [tm.tolist(), ram.tolist()], "Echo (µs)": [te.tolist(), echo.tolist()]},
                "xlabel": "Pulse length or free time", "ylabel": "Contrast"}
    if kind == "vector":
        from .nv import NV_AXES
        B = np.array([1.2, -0.7, 2.1])
        proj = np.abs(NV_AXES @ B) * 28.025
        fit = proj * (1 + r.normal(0, 0.01, 4))
        return {"x": [1, 2, 3, 4], "series": {"applied": proj.tolist(), "fitted": fit.tolist()}, "xlabel": "NV orientation", "ylabel": "Half splitting γ|B·n| (MHz)", "bar": True, "B": B.tolist()}
    if kind == "arrhenius":
        T = np.linspace(300, 780, 25); d = doping.DOPANTS["C:B"]
        p = np.array([doping.free_carriers_cm3(d, 3e17, t, n_comp=5e16) for t in T])
        mu = 1500 * (T / 300) ** -2.2
        R = 1 / (1.602e-19 * p * mu) * (1 + r.normal(0, 0.03, T.size))
        x = 1000 / T
        raw = np.polyfit(x[:9], np.log(R[:9]), 1)[0] * 1000 * 8.617e-5
        # correct for the T^1.5 density of states and the T^-2.2 lattice mobility before fitting: R * T^-0.7
        corr = np.polyfit(x[:9], np.log(R[:9] * T[:9] ** -0.7), 1)[0] * 1000 * 8.617e-5
        return {"x": x.tolist(), "series": {"resistivity (Ω·cm)": R.tolist()}, "xlabel": "1000 / T (1/K)", "ylabel": "Resistivity (Ω·cm)", "logy": True,
                "ea_raw_ev": float(raw), "ea_fit_ev": float(corr)}
    if kind == "single_nv":
        tau = np.linspace(-80, 80, 161); g2 = 1 - 0.8 * np.exp(-np.abs(tau) / 12) + r.normal(0, 0.03, tau.size)
        f = np.linspace(2863, 2877, 281); spec = nv.odmr_spectrum(f, np.zeros(3), axes=np.array([[0, 0, 1.0]]), contrast=0.25, linewidth_mhz=0.4, hyperfine=True)
        return {"panels": {"g2": [tau.tolist(), g2.tolist()], "hyperfine": [f.tolist(), (spec + r.normal(0, 0.01, f.size)).tolist()]}, "xlabel": "", "ylabel": ""}
    if kind == "fet_curves":
        from .logic import Fet
        fet = Fet(mu_cm2_vs=150, vth=1.5, w_um=100)
        vds = np.linspace(0, 20, 81)
        return {"x": vds.tolist(), "series": {f"|V_GS| = {v} V": [fet.current(v, x) * 1e3 for x in vds] for v in (3, 5, 7, 9)}, "xlabel": "|V_DS| (V), W = 100 µm, L = 2 µm", "ylabel": "|I_D| (mA)"}
    if kind == "bell_q":
        q = np.linspace(0.5, 1.0, 51)
        return {"x": q.tolist(), "series": {"model (published pair)": [gate_budget.published_check(x).fidelity for x in q]}, "xlabel": "Charge-state preparation probability q",
                "ylabel": "Bell-state fidelity", "marks": [[0.75, 0.67, "2013"], [0.87, 0.82, "2014"]]}
    if kind == "good_dies":
        d0 = np.logspace(-1, 1.3, 40)
        return {"x": d0.tolist(), "series": {f"{a} mm² die": [wafer.good_dies(76, a, x) for x in d0] for a in (4, 25, 100)}, "xlabel": "Killer defects per cm²", "ylabel": "Good dies per 3-inch wafer", "log": True}
    raise KeyError(kind)


FIT_KIND = {"odmr_ensemble": "odmr", "magnet_distance": "odmr", "pulsed": "rabi", "vector": "odmr", "arrhenius": "arrhenius", "single_nv": "g2", "fet_curves": "iv"}


def to_json() -> dict:
    return {"tiers": TIERS, "experiments": [{**e, "result": expected(e["expected"])} for e in EXPERIMENTS]}


def to_markdown() -> str:
    L = ["# Experiments: from a kitchen table to a pilot line", "",
         "_Generated from `adamas/experiments.py` (`make experiments`). Interactive 3-D version: "
         "[experiments.html](https://normansrule.github.io/adamas-diamond-framework/experiments.html)._", "",
         "Ten experiments in four price tiers. Prices are approximate 2026 US-dollar street prices for generic parts and change with "
         "vendors and exchange rates; check before buying. Safety notes summarize hazards and never replace your institution's training.", "",
         "![Cost versus capability](../img/fig47_experiment_ladder.png)", "", "| Tier | Budget | For |", "|---|---|---|"]
    L += [f"| {k} · {t['name']} | {t['range']} | {t['who']} |" for k, t in TIERS.items()]
    L += ["", "![Expected results, tier A](../img/fig44_expected_tier_a.png)", "", "![Expected results, tier B](../img/fig45_expected_tier_b.png)", "",
          "![Expected results, tiers C and D](../img/fig46_expected_tier_cd.png)", ""]
    for e in EXPERIMENTS:
        lo, hi = e["cost"]
        L += [f"## {e['id']} · {e['title']}", "", f"*Tier {e['tier']} ({TIERS[e['tier']]['name']}) · about US${lo:,} to {hi:,} · {e['time']} · needs: {e['skill']}*", "",
              f"**Goal.** {e['goal']}", "", "**You will learn.** " + "; ".join(e["learn"]) + ".", "",
              "| Part | Specification | Approx. cost (US$) |", "|---|---|---|"]
        L += [f"| {a} | {b} | {c:,} to {d:,} |" for a, b, c, d in e["parts"]]
        L += ["", "**Safety.** " + " ".join(e["safety"]), "", "**Steps.**", ""]
        L += [f"{i + 1}. **{t}.** {d}" for i, (t, d, _) in enumerate(e["steps"])]
        fk = FIT_KIND.get(e["expected"])
        fitline = f" Fit your data with `python -m adamas.fit {fk} data.csv` or drop the CSV into the [Data Lab](https://normansrule.github.io/adamas-diamond-framework/datalab.html)." if fk else ""
        L += ["", f"**Analysis.** {e['analysis']}{fitline}", "", f"**Try it first in the browser:** [{e['lab']}](https://normansrule.github.io/adamas-diamond-framework/{e['lab']}). "
              f"Sources: {' '.join(f'[{k}]' for k in e['refs'])}.", ""]
    return "\n".join(L) + "\n"


def write(path: str = "docs/experiments/EXPERIMENTS.md") -> str:
    from pathlib import Path
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(to_markdown(), encoding="utf-8"); return str(p)
