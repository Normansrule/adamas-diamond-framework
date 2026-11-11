# QDL-03 Electron-nuclear conditional gate

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [xie2023] [rong2015]

Superconducting qubits operate near 10 to 20 mK (dilution-refrigerator base below 20 mK, 14 mK under a 50-qubit load [krinner2019]). Nothing here implies parity with them.

**Analogy only:** a transistor (analogy) — the real device is the Electron-nuclear conditional gate. Fits: One spin switches what happens to the other, as a gate voltage switches a channel. Breaks: It is reversible and coherent, it has no gain, and it acts on superpositions.

## What it should do

Flip the electron only if the nucleus is in one state (a CNOT), using a pulse that resolves the hyperfine line.

The ¹⁴N hyperfine coupling of about 2.16 MHz splits the electron line in three. A weak microwave pulse narrower than that splitting flips the electron for one nuclear state only: a controlled NOT. The same trick runs the other way with radio-frequency pulses. Noise filtering has pushed it to 0.9992 at room temperature.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| CNOT (electron target, nucleus control) | demonstrated | [xie2023] [rong2015] |  |
| Nuclear-controlled phase gates | demonstrated | [waldherr2014] |  |

## Entanglement

| What | Label | Sources | Note |
|---|---|---|---|
| Electron-nuclear Bell states, deterministic | demonstrated | [rong2015] [xie2023] |  |

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Two-qubit gate inside one register | demonstrated | [xie2023] |  |
| Error correction with nuclear ancillas | demonstrated | [waldherr2014] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| CNOT gate fidelity | 0.9992 ± 7e-05 | demonstrated: electron and ¹⁴N, room temperature, noise filtering [xie2023] | — |  |

## How to build it

Traveler variant: `qubit` (docs/process/TRAVELER.md). Extension steps are written in the traveler's extension section; steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S03 | **Homoepitaxial buffer growth (MPCVD).** Buries polishing damage and substrate impurities under fresh, controlled diamond; for qubits a ¹²C-enriched cap removes the nuclear-spin bath. | 950 | Safety: Hydrogen and methane are flammable: leak-checked lines, gas detectors, interlocked exhaust. Microwave leakage check after any maintenance. |
| S04 | **Post-growth clean and inspection.** Growth leaves a hydrogen-terminated, possibly graphitic surface; a second oxidizing clean restores the oxygen-terminated reference state for lithography. | 200 | Safety: As S02. |
| S05 | **Etched alignment marks.** Every later mask, including the nanoscale nitrogen apertures, aligns to these. They must be etched into diamond because the NV anneal (S07) exceeds gold's melting point (1064 °C). | 120 | Safety: Plasma tools: standard interlocks; chlorine-free recipes only. |
| S06 | **Nitrogen implantation through apertures.** Places nitrogen where qubits are wanted (layer QIMPLANT of PDK-0). Depth and dose set how many NV centers form and how close they sit to the surface. | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S13 | **Atomic-layer-deposited Al₂O₃ gate insulator and passivation.** Al₂O₃ is both the gate insulator and the cap that stabilizes the hole gas. Deposition temperature sets the trade-off: hot ALD survives high-temperature operation; cold ALD keeps NO₂. | 450 | Safety: Trimethylaluminium is pyrophoric: sealed source, trained operators, never open to air. |
| S16 | **Mask 6 (METAL2): interconnect and pads.** Connects transistors into cells and brings every node to probe pads; the photocurrent electrodes and microwave line for qubits (QELEC) are drawn here too. | 120 | Safety: As S14. |
| S18 | **Quantum test (NV windows).** Calibrate the selective π pulse on one hyperfine line (Rabi frequency well below 2.16 MHz). | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |
| S19 | **Dicing and high-temperature packaging.** Diamond's advantage is operating hot; the package must not become the limit. | 350 | Safety: Laser dicing fumes: local extraction. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M20 Low-energy ion implanter (¹⁵N); M22 High-vacuum annealing furnace (800–1200 °C); M47 High numerical-aperture objective; M51 Arbitrary waveform generator (AWG); M53 RF source for nuclear spins (MHz range)

## Pass/fail checks (simulated)

| Check | Nominal (documented seed) | Degraded twin | Fault | Threshold source | Pass rate |
|---|---|---|---|---|---|
| Bell state from the selective CNOT stays above 0.99: Bell-state fidelity after the selective CNOT ≥ 0.99 (a Bell fidelity, not a gate fidelity) | 0.9957, **pass** | 0.9719, **fail** | Drive too strong: the pulse also rotates the neighboring hyperfine line | ADAMAS design threshold 0.99 on the Bell-state fidelity | 1.00 ± 0.00 (200 seeds) |

## Failure modes

- Drive strong enough to excite the neighboring hyperfine line
- Field drift detunes the selective pulse

## Open problems

- Gates between nuclei of different NVs still go through the electrons (QDL-04).

## Links

Labs: labs/qubit.html, labs/addressing.html. Chapters: [08_quantum_processor_architecture.md](../08_quantum_processor_architecture.md). Experiments: C2. Equation panels: rabi, crosstalk.
