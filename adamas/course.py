"""ADAMAS course: six lessons from "why diamond?" to "how big is the machine?", for self-study or a semester module.

Each lesson has objectives, readings in this repository, a hands-on lab task, a runnable notebook, and a four-question
check with explanations. The website pages (web/course/) and the notebooks (notebooks/) are generated from this file,
so content lives in one place. Citation keys resolve in references/REFERENCES.md.
"""
from __future__ import annotations

REPO = "https://github.com/Normansrule/adamas-diamond-framework"
SITE = "https://normansrule.github.io/adamas-diamond-framework"

LESSONS = [
    {
        "id": 1, "title": "Why diamond?", "minutes": 45,
        "objectives": ["Explain why a larger bandgap and breakdown field matter for power and heat",
                       "Compute a figure of merit relative to silicon", "Explain why deep dopants limit diamond at room temperature"],
        "read": [("Chapter 1: Materials physics", "docs/01_materials_physics.md"),
                 ("Chapter 3: Process flow versus CMOS", "docs/03_process_flow_vs_cmos.md")],
        "lab": ("labs/lattice.html", "Switch between diamond and silicon at true scale. Then open the Heat Race and compare the peak temperature rise of silicon and diamond at steady state. Is the ratio close to 22 / 1.5?"),
        "code": ["from adamas import materials, doping",
                 "f = materials.normalized_foms()\nprint('Baliga figure of merit, diamond vs silicon:', round(f['Diamond']['BFOM']))",
                 "for key in ('Si:B', 'C:B', 'C:P'):\n    print(key, f\"{100 * doping.ionized_fraction(doping.DOPANTS[key], 1e17):.2f} % ionized at 300 K\")"],
        "quiz": [
            {"q": "Diamond's Baliga figure of merit is so large mainly because it scales as the cube of…", "o": ["the thermal conductivity", "the critical breakdown field", "the lattice constant", "the hole mobility"], "a": 1,
             "why": "BFOM = εμE_c³. Diamond's breakdown field (about 10 MV/cm) is about 30× silicon's, and it enters cubed [baliga1982]."},
            {"q": "At 300 K and 10¹⁷ cm⁻³, roughly what fraction of boron atoms in diamond are ionized?", "o": ["about 90%", "about 50%", "under 1%", "exactly 100%"], "a": 2,
             "why": "Boron sits 0.37 eV above the valence band, many kT deep, so most acceptors keep their holes [lagrange1998]."},
            {"q": "Why does diamond's hot spot run cooler than silicon's for the same power?", "o": ["Its bandgap is wider", "Its thermal conductivity is about 15× higher", "It is transparent", "Its atoms are heavier"], "a": 1,
             "why": "At steady state the peak temperature rise scales as 1/κ; κ is 22 versus 1.5 W/(cm·K) [wei1993]."},
            {"q": "Which statement about surface transfer doping is true?", "o": ["It needs phosphorus implants", "It creates a hole gas at a hydrogen-terminated surface with no dopant atoms", "It works only below 77 K", "It is how silicon CMOS is made"], "a": 1,
             "why": "Air-borne or deposited acceptors pull electrons from the C–H surface, leaving a 2-D hole gas [maier2000]."},
        ],
    },
    {
        "id": 2, "title": "Power switches", "minutes": 50,
        "objectives": ["Read an on-resistance versus breakdown-voltage chart", "Derive the loss-optimal die area of a hard-switched converter",
                       "Explain why bulk-doped diamond improves when hot"],
        "read": [("Chapter 4: Analog, power, and RF devices", "docs/04_analog_power_rf_devices.md"), ("E9: Power circuits, diamond vs GaN and SiC", "docs/expert/E9_power_circuits_diamond_vs_gan_sic.md")],
        "lab": ("labs/power.html", "Pick the EV traction inverter. Raise the junction temperature from 27 °C to 250 °C and watch which materials cross their temperature limit, and how the silicon-to-diamond loss ratio changes."),
        "code": ["from adamas import converter",
                 "for m in ('Si', '4H-SiC', 'GaN', 'Diamond'):\n    s = converter.material_switch(m, 1200, 800, 300, 20e3)\n    print(f'{m:8s} {s.p_total_w:7.1f} W per switch')",
                 "s = converter.material_switch('Diamond', 1200, 800, 300, 20e3, measured='saha2022')\nprint('measured 2022 diamond device, scaled:', round(s.p_total_w, 1), 'W')"],
        "quiz": [
            {"q": "At the loss-optimal die area of a hard-switched converter, conduction loss and switching loss are…", "o": ["zero and maximal", "equal", "in the ratio of the bus voltages", "independent of area"], "a": 1,
             "why": "P = I²R/A + ½CAV²f is minimized where the two terms are equal, giving P = 2IV√(fRC/2) [erickson2020]."},
            {"q": "The measured 2568 V diamond MOSFET beats silicon's theoretical limit by roughly…", "o": ["2×", "10×", "about 90×", "10,000×"], "a": 2,
             "why": "7.54 mΩ·cm² against silicon's one-dimensional limit at the same voltage [saha2022] [baliga1982]."},
            {"q": "Why can bulk-doped diamond's on-resistance fall as it heats up?", "o": ["Mobility rises with temperature", "More boron ionizes, adding holes faster than mobility drops", "The bandgap shrinks to zero", "Oxide charges anneal"], "a": 1,
             "why": "Ionization rises steeply with temperature for a 0.37 eV acceptor [pernot2010]; the hole-gas devices lack this gain."},
            {"q": "Which material merit sets the minimum switch loss in this model?", "o": ["√(R_on,sp · C_oss,sp)", "Thermal conductivity alone", "Bandgap alone", "Die cost"], "a": 0,
             "why": "The optimum loss scales as √(R·C); both terms improve with breakdown field [huang2004]."},
        ],
    },
    {
        "id": 3, "title": "Transistors, gates, and a diamond CPU", "minutes": 60,
        "objectives": ["Explain an enhancement/depletion inverter and its static power", "Relate stage delay to a ring-oscillator period",
                       "Trace a program through the DIA-4 processor"],
        "read": [("Chapter 5: Digital logic", "docs/05_digital_logic.md"), ("E3: Digital and CPU design", "docs/expert/E3_digital_and_cpu_design.md")],
        "lab": ("labs/transistor.html", "Lower the driver-to-load ratio until the ring oscillator stops. Then open the Diamond CPU, load 'subroutines', and step until the output port shows 10. Which instruction wrote it?"),
        "code": ["from adamas.logic import Fet, inverter_vtc, noise_margins",
                 "vin, vout = inverter_vtc(Fet(vth=1.5, w_um=200), Fet(vth=-2.0, w_um=25), vdd=10.0)\nprint(noise_margins(vin, vout))",
                 "from adamas import digital\nprint(round(digital.EDGate().t_pd_s * 1e9, 2), 'ns per stage (hand model)')"],
        "quiz": [
            {"q": "Why do p-channel-only diamond gates burn static power?", "o": ["Their gates leak through the oxide", "When the output is low, the driver and the always-on load conduct at once", "Holes recombine", "The clock never stops"], "a": 1,
             "why": "The depletion load is normally on, so a current path exists whenever the driver is on [liu2017]."},
            {"q": "A five-stage ring oscillator with a 24.6 ns period has a stage delay of about…", "o": ["24.6 ns", "4.9 ns", "2.5 ns", "0.5 ns"], "a": 2,
             "why": "Period = 2 × stages × delay, so 24.6 / 10 ≈ 2.5 ns [rabaey2003]."},
            {"q": "In DIA-4, what does JNZ do?", "o": ["Jumps if the accumulator is not zero", "Jumps if carry is set", "Always jumps", "Returns from a call"], "a": 0,
             "why": "JNZ branches on a non-zero accumulator, the loop primitive of the countdown example (chapter E3; the 4004 had the same idea [faggin1996])."},
            {"q": "Roughly how much diamond does the placed DIA-4 core need at 2 µm gates?", "o": ["1 µm²", "about 1 mm² with pads", "1 cm²", "a full 76 mm wafer"], "a": 1,
             "why": "About 0.25–0.28 mm² of cells at 60% utilization, about 1 mm² with pads (chapter E2)."},
        ],
    },
    {
        "id": 4, "title": "The NV qubit", "minutes": 50,
        "objectives": ["Read an ODMR spectrum and relate line splitting to magnetic field", "Distinguish Rabi, Ramsey, and echo experiments",
                       "Explain what T₂* and T₂ measure"],
        "read": [("Chapter 6: NV center physics", "docs/06_nv_center_physics.md"), ("E5: NV qubit engineering", "docs/expert/E5_nv_qubit_engineering.md")],
        "lab": ("labs/qubit.html", "Set T₂* to 2 µs. Run Ramsey and Echo with the same free time of 5 µs. Why does one keep its coherence and the other lose it?"),
        "code": ["import numpy as np\nfrom adamas import nv",
                 "f = np.linspace(2780, 2960, 7)\nprint(nv.odmr_spectrum(f, np.array([0, 0, 2.0]), hyperfine=False).round(4))",
                 "t = np.linspace(0, 1, 5)\nprint(nv.rabi(t, 2.0).round(3))"],
        "quiz": [
            {"q": "The NV zero-field splitting D is about…", "o": ["28 MHz", "2.87 GHz", "532 nm", "1.945 eV"], "a": 1,
             "why": "D ≈ 2.870 GHz between mₛ = 0 and mₛ = ±1 at room temperature [doherty2013]."},
            {"q": "A field of 1 mT along an NV axis splits its two lines by about…", "o": ["2.8 MHz", "28 MHz", "56 MHz", "2.87 GHz"], "a": 2,
             "why": "Each line moves by γB = 28 MHz/mT, in opposite directions, so the gap is 2γB [rondin2014]."},
            {"q": "Why does a spin echo recover coherence that a Ramsey experiment loses?", "o": ["It uses a stronger laser", "The π pulse reverses each spin's accumulated phase from static detunings", "It cools the diamond", "It removes the nitrogen"], "a": 1,
             "why": "Static field differences are refocused by the π pulse [hahn1950]; only changing noise remains, setting T₂."},
            {"q": "Which spin state fluoresces more brightly under green light?", "o": ["mₛ = 0", "mₛ = −1", "mₛ = +1", "they are equal"], "a": 0,
             "why": "mₛ = ±1 can cross into the singlet and skip photons, so mₛ = 0 is about 30% brighter [gruber1997]."},
        ],
    },
    {
        "id": 5, "title": "Two qubits and the real bottleneck", "minutes": 45,
        "objectives": ["Estimate dipolar coupling and gate time from spacing", "Build an error budget for an entangling gate",
                       "Explain why charge-state preparation dominates"],
        "read": [("Chapter 8: Quantum processor architecture", "docs/08_quantum_processor_architecture.md"), ("E5.1b and E5.1c: the gate budget and the published pair", "docs/expert/E5_nv_qubit_engineering.md")],
        "lab": ("explorer.html#gate", "In panel 5, set T₂ to 600 µs and preparation to 1.0, then lower preparation to 0.75. Compare with the measured 0.67 of the 2013 experiment."),
        "code": ["from adamas import gate_budget as gb",
                 "g = gb.published_check()\nprint('coherence-limited fidelity', round(g.f_coherent, 4))",
                 "for q in (0.75, 0.87, 1.0):\n    print(q, round(gb.published_check(q).fidelity, 3))"],
        "quiz": [
            {"q": "Dipolar coupling between two NV centers falls with distance r as…", "o": ["1/r", "1/r²", "1/r³", "e^(−r)"], "a": 2,
             "why": "Magnetic dipole–dipole coupling ≈ 52 MHz·nm³ / r³ [dolde2013]."},
            {"q": "With the published pair's parameters, coherence alone would allow a Bell fidelity of about…", "o": ["0.67", "0.82", "0.998", "0.5"], "a": 2,
             "why": "The measured coupling and T₂ times give 0.998; the gap to 0.67 is preparation (chapter E5.1c)."},
            {"q": "What preparation probability reproduces the measured 0.67 in this model?", "o": ["about 0.50", "about 0.75", "about 0.95", "exactly 1"], "a": 1,
             "why": "q ≈ 0.75 matches the NV⁻ charge-state fraction under green light [aslam2013]."},
            {"q": "Halving the spacing between two NV centers speeds their coupling by…", "o": ["2×", "4×", "8×", "it does not change"], "a": 2,
             "why": "Coupling ∝ 1/r³, so r → r/2 multiplies it by 8, shortening the gate eightfold [dolde2013]."},
        ],
    },
    {
        "id": 6, "title": "Error correction and the size of the machine", "minutes": 60,
        "objectives": ["Explain syndromes, matching, and threshold", "State the readout-time budget for NV hardware",
                       "Estimate qubits, die size, and runtime for a job"],
        "read": [("E6: Error correction and system architecture", "docs/expert/E6_error_correction_and_system_architecture.md"), ("E10: Scaling a room-temperature quantum computer", "docs/expert/E10_scaling_a_room_temperature_quantum_computer.md")],
        "lab": ("labs/machine.html", "Choose the materials-simulation job. Move readout from 1 ms to 0.1 ms, then lower the gate time from 25 µs to 3 µs. Which change saves more time, and why?"),
        "code": ["from adamas import resource as R",
                 "n, steps = R.WORKLOADS['Materials simulation (1,000 logical, 10⁹ steps)']\nfor tr in (100, 1000):\n    e = R.estimate(n, steps, tr)\n    print(tr, 'µs readout:', e.distance, f'{e.physical_qubits:.2e} qubits', round(e.runtime_hours / 24), 'days')"],
        "quiz": [
            {"q": "What does a lit check (syndrome) in a surface code tell you?", "o": ["Exactly which qubit flipped", "That an error chain ends next to it", "That the code has failed", "The measured value of the logical qubit"], "a": 1,
             "why": "Checks see only the endpoints of error chains; the decoder infers the chains by matching [dennis2002]."},
            {"q": "Below threshold, making the code distance larger…", "o": ["increases logical errors", "suppresses logical errors exponentially", "has no effect", "only costs time"], "a": 1,
             "why": "p_L ∝ Λ^(−(d+1)/2) with Λ > 1 below threshold [fowler2012] [google2025]."},
            {"q": "For NV cells with a 1 s nuclear memory, the standard code stops improving with distance at a readout time of about…", "o": ["1 µs", "1 ms", "100 ms", "10 s"], "a": 2,
             "why": "Circuit-level simulation: data idle while the ancilla is read, with break-even near 10% of the memory time (chapter E6.1c)."},
            {"q": "Why does the XZZX code help NV hardware?", "o": ["It needs fewer qubits per patch", "It exploits the dephasing bias of the nuclear memory", "It removes the need for readout", "It works without a decoder"], "a": 1,
             "why": "Bias-tailored codes turn Z-dominated noise into an advantage, about 10× more tolerable readout here [bonillaataides2021] (E6.1d)."},
        ],
    },
    {
        "id": 7, "title": "Building it: the process traveler", "minutes": 60,
        "objectives": ["Order a diamond process by its thermal budget", "Explain why gold goes on right after hydrogen termination",
                       "Choose NO₂ and ALD options for a target product"],
        "read": [("Process engineering overview", "docs/process/README.md"), ("Traveler T1, all 19 steps", "docs/process/TRAVELER.md"),
                 ("From process to product", "docs/process/APPLICATIONS.md")],
        "lab": ("process.html", "Select the 'Power switch' variant and walk from S01 to S19 with the arrow keys. Which steps are skipped, and which single step would you change to build the RF amplifier instead?"),
        "code": ["from adamas import traveler as T",
                 "print('thermal-budget violations:', T.thermal_violations())\nfor s in T.STEPS[:9]:\n    print(s['id'], s['short'], s['t_max_c'], '°C')",
                 "print(T.VARIANTS['rf']['name'], '→ skips', T.VARIANTS['rf']['skip'])"],
        "quiz": [
            {"q": "Why must the NV anneal (up to about 1100 °C) come before the first gold deposition?", "o": ["Gold blocks nitrogen", "Gold melts at 1064 °C and the hole gas and oxide cannot survive such heat", "The anneal needs gold as a catalyst", "It does not matter"], "a": 1,
             "why": "Heat is spent early: growth and the NV anneal precede all metal; after gold the flow stays below about 500 °C (Figure 42; [pezzagna2010])."},
            {"q": "What creates the transistor channel in hydrogen-terminated diamond?", "o": ["Boron implantation", "A two-dimensional hole gas from surface transfer doping at the C–H surface", "An inversion layer under the gate", "Phosphorus diffusion"], "a": 1,
             "why": "Acceptors on the C–H surface pull electrons out of the diamond, leaving holes a few nanometers deep [maier2000] [kawarada2023]."},
            {"q": "How are neighboring transistors isolated in this flow?", "o": ["Shallow-trench isolation", "An oxygen plasma turns exposed C–H into C–O, killing the hole gas", "Reverse-biased wells", "Etching mesas 1 µm deep"], "a": 1,
             "why": "One masked oxygen-plasma step isolates every device and also restores oxygen termination on the NV windows [kawarada2023] [hauf2011]."},
            {"q": "For a transistor that must run at 400 °C, which options fit best?", "o": ["NO₂ doping with ≤ 150 °C ALD", "No NO₂, about 450 °C ALD", "No ALD at all", "Any option works"], "a": 1,
             "why": "NO₂ desorbs when hot; high-temperature ALD Al₂O₃ enabled 400 °C operation [kawarada2014]."},
        ],
    },
]


def notebook(lesson: dict):
    import nbformat
    from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
    colab = f"https://colab.research.google.com/github/Normansrule/adamas-diamond-framework/blob/main/notebooks/lesson_{lesson['id']}.ipynb"
    cells = [new_markdown_cell(f"# Lesson {lesson['id']}: {lesson['title']}\n\n[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)]({colab})\n\n"
                               "**Objectives**\n\n" + "\n".join(f"- {o}" for o in lesson["objectives"]) +
                               f"\n\nLab: [{lesson['lab'][0]}]({SITE}/{lesson['lab'][0]}). {lesson['lab'][1]}"),
             new_code_cell("# In Colab, install the package first (skipped when it is already installed)\n"
                           "import importlib.util, subprocess, sys\n"
                           "if importlib.util.find_spec('adamas') is None:\n"
                           f"    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'git+{REPO}'], check=True)")]
    cells += [new_code_cell(c) for c in lesson["code"]]
    cells.append(new_markdown_cell("**Check yourself.** Take the four-question check on the [lesson page]"
                                   f"({SITE}/course/lesson-{lesson['id']}.html)."))
    nb = new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    return nb


def write_notebooks(out: str = "notebooks") -> list[str]:
    import nbformat
    from pathlib import Path
    d = Path(out); d.mkdir(exist_ok=True)
    paths = []
    for L in LESSONS:
        p = d / f"lesson_{L['id']}.ipynb"; nbformat.write(notebook(L), str(p)); paths.append(str(p))
    return paths
