# Process traveler T1: diamond transistors with optional NV windows

_Generated from `adamas/traveler.py` (`make traveler`); edit the Python, not this file. Interactive version: [process.html](https://normansrule.github.io/adamas-diamond-framework/process.html)._

**Read this first.** Parameters are starting points from the cited literature, not a qualified recipe; tune each on your tools with the PDK-0 monitor die ([E2](../expert/E2_process_integration_and_pdk.md)). Pass criteria marked ADAMAS are this repository's targets. Safety notes summarize hazards and never replace your facility's training.

![Process flow](../img/fig41_process_flow.png)

## Variants

| Variant | Steps skipped | Note |
|---|---|---|
| Power switch (EV, grid, data center) | S06, S07, S18 | High-temperature ALD (option B) for 400 °C and kilovolt operation, or NO₂ + low-temperature ALD (option A) for the highest current. |
| RF power amplifier (5G, radar, space) | S06, S07, S18 | NO₂ doping + thin low-temperature ALD (option A); gate length 0.1 to 1 µm by electron-beam lithography. |
| High-temperature / radiation-hard logic | S06, S07, S12, S18 | No NO₂ (it desorbs when hot); high-temperature ALD (option B); E/D logic cells of PDK-0. |
| NV quantum sensor (magnetometer) | S08, S09, S10, S11, S12, S13, S14, S15, S16, S17 | Material and NV steps only: dense ensemble implant, oxygen surface, optical and microwave test. |
| Room-temperature qubit register chip | S12 | Full flow with ¹²C cap, aperture implant, photocurrent electrodes on the QELEC layer; no NO₂ near qubits. |

![Thermal budget](../img/fig42_thermal_budget.png)

![Cross-sections](../img/fig43_cross_sections.png)

## S01 · Incoming substrate inspection

*Module: Incoming · peak temperature 25 °C*

**Why.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers.

**Equipment.** Optical microscope with differential interference contrast; Cross-polarized imaging (birefringence); Raman spectrometer (532 nm); Atomic force microscope.

| Parameter | Starting point | Source |
|---|---|---|
| Orientation | (100), miscut under 3° | [friel2009] |
| Grade | Electronic-grade CVD (N < 5 ppb) for qubits; heteroepitaxial or HPHT acceptable for power | [friel2009] [schreck2017] |
| Size | 3 × 3 mm plates up to 3-inch wafers | [e6orbray2026] |

| Check | Pass criterion | Source |
|---|---|---|
| Raman 1332 cm⁻¹ line width | ≤ 3 cm⁻¹ | ADAMAS |
| Surface roughness Ra (AFM, 5 × 5 µm) | ≤ 1 nm | ADAMAS |
| No scratches or pits visible at 50× | pass / fail | ADAMAS |

**Safety.** Handle with plastic or diamond-safe tweezers; edges chip.

| Symptom | Likely cause | Action |
|---|---|---|
| Broad Raman line or strong birefringence | High dislocation or strain density | Reject for devices; use for process development only |

**Silicon, for comparison.** Silicon wafers arrive with sub-nanometer roughness and near-zero dislocations; inspection is statistical, not per piece.

## S02 · Oxidizing acid clean

*Module: Clean and grow · peak temperature 200 °C*

**Why.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface.

**Equipment.** Dedicated wet bench for hot oxidizing acids; Quartz beaker and hot plate; Ultrasonic solvent bath.

| Parameter | Starting point | Source |
|---|---|---|
| Acid mixture | Boiling H₂SO₄ : HNO₃ : HClO₄ (1:1:1, 'tri-acid') or H₂SO₄ : HNO₃ (3:1) where perchloric use is not permitted | [sangtawesin2019] |
| Temperature and time | About 170 to 200 °C, 30 min to several hours | [sangtawesin2019] |
| Follow-up | DI water rinse, acetone and isopropanol ultrasonic 10 min each, N₂ dry | ADAMAS |

| Check | Pass criterion | Source |
|---|---|---|
| Water contact angle (oxygen-terminated: hydrophilic) | ≤ 30 ° | ADAMAS |
| No residue under dark-field microscopy | pass / fail | ADAMAS |

**Safety.** Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics.

| Symptom | Likely cause | Action |
|---|---|---|
| Hydrophobic patches remain | Incomplete oxidation or organic film | Repeat clean; extend time |

**Silicon, for comparison.** Silicon uses the RCA clean and a dilute-HF dip to strip native oxide; diamond has no native oxide to strip.

## S03 · Homoepitaxial buffer growth (MPCVD)

*Module: Clean and grow · peak temperature 950 °C*

**Why.** Buries polishing damage and substrate impurities under fresh, controlled diamond; for qubits a ¹²C-enriched cap removes the nuclear-spin bath.

**Equipment.** Microwave plasma CVD reactor (2.45 GHz); Pyrometer; Mass-flow controllers for H₂, CH₄ (¹²CH₄ for qubits).

| Parameter | Starting point | Source |
|---|---|---|
| Pre-growth H₂ plasma etch | 10 to 30 min to remove subsurface damage | [tallaire2013] |
| Gas | CH₄/H₂ about 0.5 to 4%; residual nitrogen below 1 ppm (electronic grade below 200 ppb) | [lu2013] [bolshakov2020] [teraji2015] |
| Pressure, temperature | About 100 to 300 Torr, 800 to 1000 °C substrate | [lu2013] [bolshakov2020] |
| Thickness | 1 to 5 µm for devices; 50 to 100 nm ¹²C cap for qubits | [teraji2015] [balasubramanian2009] |

| Check | Pass criterion | Source |
|---|---|---|
| Hillock density (DIC microscope) | ≤ 1000 cm⁻² | ADAMAS |
| PL: no SiV (737 nm) or strong NV (637 nm) signal from the layer | pass / fail | ADAMAS |
| Layer thickness | 1 to 5 µm | ADAMAS |

**Safety.** Hydrogen and methane are flammable: leak-checked lines, gas detectors, interlocked exhaust. Microwave leakage check after any maintenance.

| Symptom | Likely cause | Action |
|---|---|---|
| Unepitaxial crystallites / hillocks | Too much CH₄ or dirty substrate | Lower CH₄, longer H₂ etch, better clean |
| Strong NV or SiV photoluminescence | Nitrogen leak or silicon from quartz window | Leak-check, purify gas, shield quartz |

**Silicon, for comparison.** Silicon epitaxy (CVD from silane or trichlorosilane) is routine at 300 mm; diamond growth is slow and small.

## S04 · Post-growth clean and inspection

*Module: Clean and grow · peak temperature 200 °C*

**Why.** Growth leaves a hydrogen-terminated, possibly graphitic surface; a second oxidizing clean restores the oxygen-terminated reference state for lithography.

**Equipment.** As S02.

| Parameter | Starting point | Source |
|---|---|---|
| Recipe | Repeat S02 | [sangtawesin2019] |

| Check | Pass criterion | Source |
|---|---|---|
| Water contact angle | ≤ 30 ° | ADAMAS |

**Safety.** As S02.

| Symptom | Likely cause | Action |
|---|---|---|
| Film delaminates in acid | Stress from growth | Anneal or regrow thinner |

**Silicon, for comparison.** No equivalent: silicon's native oxide makes the surface state predictable.

## S05 · Etched alignment marks

*Module: Clean and grow · peak temperature 120 °C*

**Why.** Every later mask, including the nanoscale nitrogen apertures, aligns to these. They must be etched into diamond because the NV anneal (S07) exceeds gold's melting point (1064 °C).

**Equipment.** Optical or electron-beam lithography; Hard mask evaporator (Al or SiO₂); Inductively coupled O₂/Ar plasma etcher.

| Parameter | Starting point | Source |
|---|---|---|
| Mask | Al or SiO₂ hard mask, lift-off | ADAMAS |
| Etch | O₂/Ar inductively coupled plasma, 200 to 500 nm deep | [hauf2011] |
| Strip | Mask wet etch, then S02 clean | ADAMAS |

| Check | Pass criterion | Source |
|---|---|---|
| Mark depth (profilometer) | 150 to 600 nm | ADAMAS |
| Marks visible in the electron-beam tool | pass / fail | ADAMAS |

**Safety.** Plasma tools: standard interlocks; chlorine-free recipes only.

| Symptom | Likely cause | Action |
|---|---|---|
| Micromasking pillars in the etched field | Sputtered mask material | Lower bias power; cleaner mask |

**Silicon, for comparison.** Silicon uses the same idea (zero-level marks), usually etched into the wafer.

## S06 · Nitrogen implantation through apertures

*Module: Quantum option · peak temperature 25 °C*

**Why.** Places nitrogen where qubits are wanted (layer QIMPLANT of PDK-0). Depth and dose set how many NV centers form and how close they sit to the surface.

**Equipment.** Electron-beam lithography (PMMA apertures, 20 to 50 nm); Low-energy ion implanter with ¹⁵N⁺ source; SRIM for depth planning.

| Parameter | Starting point | Source |
|---|---|---|
| Isotope | ¹⁵N⁺ (distinguishes implanted from native ¹⁴N) | [pezzagna2010] |
| Energy | 2.5 to 10 keV → about 5 to 15 nm mean depth | [pezzagna2010] [ziegler2010] |
| Dose | 10⁸ to 10¹¹ cm⁻² for single centers; up to 10¹³ cm⁻² for sensing ensembles | [pezzagna2010] |

| Check | Pass criterion | Source |
|---|---|---|
| Aperture diameter (SEM of test field) | 10 to 60 nm | ADAMAS |
| Implant dose logged | pass / fail | ADAMAS |

**Safety.** Ion implanter: radiation (X-ray) interlocks and high voltage.

| Symptom | Likely cause | Action |
|---|---|---|
| Too few or too many NV per site | Dose or aperture size | Calibrate conversion yield on the witness array; adjust dose |

**Silicon, for comparison.** Silicon implants dopants the same way, but at 10¹⁴ to 10¹⁵ cm⁻² and for electrical, not quantum, purposes.

## S07 · Vacancy anneal and oxygen re-termination

*Module: Quantum option · peak temperature 1100 °C*

**Why.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit.

**Equipment.** High-vacuum furnace (below 10⁻⁶ mbar) or forming-gas furnace; Tri-acid bench (S02).

| Parameter | Starting point | Source |
|---|---|---|
| Anneal | 800 to 1100 °C, 1 to 3 h, high vacuum (prevents surface etching) | [pezzagna2010] |
| Yield to expect | About 1% at 2.5 to 5 keV, rising with energy | [pezzagna2010] |
| Re-termination | Tri-acid clean (S02) → oxygen surface; NV⁻ stable near the surface | [hauf2011] [sangtawesin2019] |

| Check | Pass criterion | Source |
|---|---|---|
| NV conversion yield (confocal count ÷ implanted N) | ≥ 0.5 % | [pezzagna2010] |
| Echo T₂ of shallow NV (depth about 10 nm) | ≥ 10 µs | ADAMAS |
| NV⁻ fraction under green light | ≥ 0.7 | [aslam2013] |

**Safety.** Furnace hot-zone burns; vacuum implosion shielding.

| Symptom | Likely cause | Action |
|---|---|---|
| Low yield, dark surface layer | Residual oxygen etched the surface during anneal | Better vacuum; lower temperature; forming gas |
| Short T₂ | Surface spins or implant damage | Higher anneal temperature, oxygen annealing, deeper NV |

**Silicon, for comparison.** Silicon's implant anneal activates dopants (rapid thermal anneal around 1000 °C); here the anneal manufactures a defect on purpose.

## S08 · Hydrogen termination (H₂ plasma)

*Module: Transistor front end · peak temperature 800 °C*

**Why.** Creates the C–H surface whose negative electron affinity lets adsorbed acceptors pull electrons out, leaving the two-dimensional hole gas that is the transistor channel. No dopant atoms are involved.

**Equipment.** MPCVD reactor in pure H₂.

| Parameter | Starting point | Source |
|---|---|---|
| Plasma | Pure H₂, about 600 to 800 °C, 5 to 30 min | [kawarada2023] |
| Cool-down | In H₂ to below about 300 °C before venting | [kawarada2023] |

| Check | Pass criterion | Source |
|---|---|---|
| Water contact angle (hydrophobic) | ≥ 75 ° | ADAMAS |
| Sheet resistance in air (Van der Pauw) | 3 to 30 kΩ/sq | ADAMAS |

**Safety.** As S03 (hydrogen plasma).

| Symptom | Likely cause | Action |
|---|---|---|
| High sheet resistance | Incomplete termination or exposure to oxidizers | Repeat plasma; store in clean N₂; proceed to S09 within hours |

**Silicon, for comparison.** No equivalent. Silicon channels form by inversion under the gate, not by surface chemistry.

## S09 · Blanket gold deposition

*Module: Transistor front end · peak temperature 80 °C*

**Why.** Gold forms a low-resistance contact to the hole gas and protects the fragile C–H surface from every later resist and solvent.

**Equipment.** Electron-beam evaporator.

| Parameter | Starting point | Source |
|---|---|---|
| Film | About 100 nm Au directly on C–H, no adhesion layer | [kawarada2023] |

| Check | Pass criterion | Source |
|---|---|---|
| Au thickness (crystal monitor) | 80 to 120 nm | ADAMAS |

**Safety.** Evaporator high voltage and X-rays; standard training.

| Symptom | Likely cause | Action |
|---|---|---|
| Gold peels during lift-off or tape test | Contaminated surface | Shorten time between S08 and S09; gentler resist strip |

**Silicon, for comparison.** Silicon forms contacts by silicidation (Ni, Co, Ti) after doping the source and drain.

## S10 · Mask 1 (OHMIC + ISO): gold pattern and oxygen-plasma isolation

*Module: Transistor front end · peak temperature 120 °C*

**Why.** Gold is removed everywhere except the device areas; the uncovered C–H is converted to C–O by an oxygen plasma, which kills the hole gas. One mask isolates every transistor and returns the NV windows to an oxygen surface.

**Equipment.** Mask aligner or laser writer (PDK-0 layers OHMIC and ISO); KI/I₂ gold etchant; O₂ plasma asher or UV-ozone.

| Parameter | Starting point | Source |
|---|---|---|
| Gold etch | KI/I₂ at room temperature until clear | [kawarada2023] |
| Isolation | Low-power O₂ plasma or UV-ozone, a few minutes | [kawarada2014] |

| Check | Pass criterion | Source |
|---|---|---|
| Leakage between isolated pads at 20 V | ≤ 1 nA | ADAMAS |
| NV windows oxygen-terminated (contact angle below 30°) | pass / fail | ADAMAS |

**Safety.** Iodine-based etchant stains and irritates: gloves, goggles.

| Symptom | Likely cause | Action |
|---|---|---|
| Pads short together | Incomplete oxidation or gold residue | Extend plasma; inspect at 100× |

**Silicon, for comparison.** Silicon isolates devices with shallow-trench isolation: etch, oxide fill, and chemical-mechanical polish.

## S11 · Mask 2 (GATE opening): self-aligned channel

*Module: Transistor front end · peak temperature 120 °C*

**Why.** Opening a gap in the gold defines the channel length; the gold on either side becomes source and drain, self-aligned to the channel.

**Equipment.** Optical lithography (gaps above 1 µm) or electron-beam lithography (0.1 to 1 µm); KI/I₂.

| Parameter | Starting point | Source |
|---|---|---|
| Gap | 2 µm (PDK-0 rule) for logic; 0.1 to 1 µm for RF | [kawarada2023] |

| Check | Pass criterion | Source |
|---|---|---|
| Channel length (SEM) | 0.1 to 10 µm | ADAMAS |
| No gold residue in the gap | pass / fail | ADAMAS |

**Safety.** As S10.

| Symptom | Likely cause | Action |
|---|---|---|
| Undercut widens the gap | Over-etch | Time the etch; calibrate on test gaps |

**Silicon, for comparison.** Silicon uses a self-aligned polysilicon or metal gate, with implants aligned to it.

## S12 · NO₂ exposure (option A, high-current devices)

*Module: Transistor front end · peak temperature 25 °C*

**Why.** NO₂ is a strong surface acceptor: it raises the hole density toward 10¹⁴ cm⁻², lowering on-resistance. It must be locked in immediately by the ALD cap (S13).

**Equipment.** Sealed exposure chamber with 2% NO₂ in N₂; Gas cabinet with NO₂ detector.

| Parameter | Starting point | Source |
|---|---|---|
| Gas | 2% NO₂ in N₂, room temperature | [kasu2012] [hirama2012] |
| Saturation | Hole density saturates near 9 × 10¹³ cm⁻² above about 300 ppm | [sato2013] |
| Duration | Until the sheet resistance of a test structure saturates | [kubovic2009] |

| Check | Pass criterion | Source |
|---|---|---|
| Sheet resistance after exposure (from the saturated hole density of [sato2013] and a typical mobility) | 0.5 to 5 kΩ/sq | ADAMAS |

**Safety.** NO₂ is highly toxic: gas cabinet, continuous monitoring, exhausted enclosure, buddy system.

| Symptom | Likely cause | Action |
|---|---|---|
| Resistance recovers after exposure | NO₂ desorbs before capping | Minimize delay to ALD; low-temperature ALD first cycles |

**Silicon, for comparison.** No equivalent. Silicon doping is by implantation and anneal.

## S13 · Atomic-layer-deposited Al₂O₃ gate insulator and passivation

*Module: Transistor front end · peak temperature 450 °C*

**Why.** Al₂O₃ is both the gate insulator and the cap that stabilizes the hole gas. Deposition temperature sets the trade-off: hot ALD survives high-temperature operation; cold ALD keeps NO₂.

**Equipment.** Thermal ALD (trimethylaluminium + H₂O); Ellipsometer and silicon witness piece.

| Parameter | Starting point | Source |
|---|---|---|
| Option A (with NO₂) | ≤ 150 °C, about 10 nm | [kasu2012] [hirama2012] |
| Option B (high temperature, high voltage) | About 450 °C, 100 to 200 nm; enables 400 °C operation and about 2 kV | [kawarada2014] [kawarada2017] |

| Check | Pass criterion | Source |
|---|---|---|
| Thickness on witness (ellipsometry) | 8 to 220 nm | ADAMAS |
| C–V hysteresis on MOS capacitor | ≤ 0.5 V | ADAMAS |

**Safety.** Trimethylaluminium is pyrophoric: sealed source, trained operators, never open to air.

| Symptom | Likely cause | Action |
|---|---|---|
| Large C–V hysteresis | Traps at the interface or in the oxide | Adjust temperature; post-deposition anneal within the thermal budget |

**Silicon, for comparison.** Silicon also uses ALD high-κ oxides (HfO₂) at advanced nodes, over a thin SiO₂ interface layer.

## S14 · Mask 3 (GATE metal)

*Module: Back end · peak temperature 120 °C*

**Why.** The gate electrode sits on Al₂O₃ over the channel and must overlap the gap on both sides so the whole channel is controlled.

**Equipment.** Lithography; Evaporator; Lift-off bath.

| Parameter | Starting point | Source |
|---|---|---|
| Metal | Al, Au, or Ti/Au (for example 10/80 nm) | [kasu2012] [kawarada2023] |
| Overlap | At least 2 λ beyond the gap (PDK-0 rule) | ADAMAS |

| Check | Pass criterion | Source |
|---|---|---|
| Gate leakage at maximum gate voltage | ≤ 1 µA/mm | ADAMAS |

**Safety.** Solvents for lift-off: fume hood.

| Symptom | Likely cause | Action |
|---|---|---|
| Gate shorts to source or drain | ALD pinholes or misalignment | Thicker ALD; check overlay |

**Silicon, for comparison.** Similar: metal gate definition, but silicon uses gate-last replacement flows at advanced nodes.

## S15 · Mask 4 (VIA): open Al₂O₃ over contacts

*Module: Back end · peak temperature 25 °C*

**Why.** Contacts need bare gold; the oxide is removed only where pads and probes land.

**Equipment.** Lithography; Buffered oxide etch (HF-based).

| Parameter | Starting point | Source |
|---|---|---|
| Etch | 10:1 buffered oxide etch, timed to the ALD thickness | ADAMAS |

| Check | Pass criterion | Source |
|---|---|---|
| Via resistance (Kelvin structure) | ≤ 1 Ω | ADAMAS |

**Safety.** Hydrofluoric acid: HF-specific training, calcium gluconate gel at hand, never work alone.

| Symptom | Likely cause | Action |
|---|---|---|
| Open vias | Under-etch | Extend etch; check with a probe on a test pad |

**Silicon, for comparison.** Silicon opens contacts through a thick dielectric by plasma etch, then fills tungsten plugs.

## S16 · Mask 5 (METAL2): interconnect and pads

*Module: Back end · peak temperature 120 °C*

**Why.** Connects transistors into cells and brings every node to probe pads; the photocurrent electrodes and microwave line for qubits (QELEC) are drawn here too.

**Equipment.** Lithography; Evaporator; Lift-off.

| Parameter | Starting point | Source |
|---|---|---|
| Metal | Ti/Au, for example 20/130 nm | ADAMAS |

| Check | Pass criterion | Source |
|---|---|---|
| Line resistance on the serpentine monitor | ≤ 0.5 Ω/sq | ADAMAS |
| Comb-to-serpentine leakage | ≤ 1 nA | [stapper1983] |

**Safety.** As S14.

| Symptom | Likely cause | Action |
|---|---|---|
| Opens on the serpentine | Particles or lift-off tearing | Clean room discipline; bilayer resist |

**Silicon, for comparison.** Silicon uses a copper damascene stack with ten or more layers.

## S17 · Parametric test (PDK-0 monitor die)

*Module: Test and ship · peak temperature 400 °C*

**Why.** Turns the wafer into numbers that calibrate every ADAMAS model: contact resistance, sheet resistance, threshold voltages, mismatch, defect density, and gate delay.

**Equipment.** Probe station with hot chuck (to 400 °C); Semiconductor parameter analyzer; C–V meter; Oscilloscope for ring oscillators.

| Parameter | Starting point | Source |
|---|---|---|
| Structures | TLM, van der Pauw, MOS capacitor, FET array (W/L × 4), serpentine-comb, ring oscillators | [liu2017] |
| Temperatures | 25, 200, and 300 °C (to 400 °C for option B) | [kawarada2014] |

| Check | Pass criterion | Source |
|---|---|---|
| Contact resistance (TLM) | ≤ 10 Ω·mm | ADAMAS |
| On/off current ratio | ≥ 1e+06 | ADAMAS |
| Ring-oscillator period vs ADAMAS model | 0.5 to 2 ratio | ADAMAS |
| Threshold spread σ(V_T) on 4-device groups | ≤ 200 mV | [pelgrom1989] |

**Safety.** Hot chuck burns; high-voltage breakdown tests only behind shields.

| Symptom | Likely cause | Action |
|---|---|---|
| Threshold drift during hot test | Mobile charge or NO₂ desorption | Use option B oxide for hot operation |

**Silicon, for comparison.** Same idea: process-control monitors in the scribe lines of every wafer.

## S18 · Quantum test (NV windows)

*Module: Test and ship · peak temperature 25 °C*

**Why.** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5.

**Equipment.** Confocal microscope (532 nm excitation, 650 to 800 nm detection); Microwave source and stripline; Photocurrent amplifier (optional).

| Parameter | Starting point | Source |
|---|---|---|
| Sequence | ODMR, Rabi, Hahn echo, charge-state PL spectrum (575 nm NV⁰, 637 nm NV⁻ zero-phonon lines) | [doherty2013] [aslam2013] |

| Check | Pass criterion | Source |
|---|---|---|
| ODMR contrast (single NV) | ≥ 15 % | [gruber1997] |
| Echo T₂ | ≥ 10 µs | ADAMAS |
| NV⁻ fraction | ≥ 0.7 | [aslam2013] |

**Safety.** Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear.

| Symptom | Likely cause | Action |
|---|---|---|
| Low NV⁻ fraction | Residual C–H or surface band bending near windows | Re-oxidize windows; keep QIMPLANT at least 5 µm from channels (PDK rule) |

**Silicon, for comparison.** No equivalent in silicon CMOS.

## S19 · Dicing and high-temperature packaging

*Module: Test and ship · peak temperature 350 °C*

**Why.** Diamond's advantage is operating hot; the package must not become the limit.

**Equipment.** Laser dicing; Die bonder; Wire bonder (Au).

| Parameter | Starting point | Source |
|---|---|---|
| Dicing | Laser scribing (diamond cannot be sawn economically) | ADAMAS |
| Die attach | Au–Sn eutectic or sintered silver for above 200 °C | [lutz2018] |

| Check | Pass criterion | Source |
|---|---|---|
| Post-dicing chipping at edges | ≤ 20 µm | ADAMAS |
| Wire-bond pull strength | ≥ 3 gf | ADAMAS |

**Safety.** Laser dicing fumes: local extraction.

| Symptom | Likely cause | Action |
|---|---|---|
| Die attach voids | Poor wetting on diamond | Metallize back side (Ti/Pt/Au) |

**Silicon, for comparison.** Silicon is sawn with blades and packaged with organic die-attach limited to about 150 to 175 °C.

