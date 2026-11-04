# QDL-02 Nuclear-spin memory

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: reported** (Published, with a bound or special conditions stated next to the number). Operating temperature: about 300 K. [maurer2012] [waldherr2014]

The second-scale memory time needs isotopically purified diamond, decoupling and laser dissipation [maurer2012].

**Analogy only:** a storage capacitor (analogy) — the real device is the Nuclear-spin memory. Fits: It holds state for a long time next to the active device. Breaks: It stores a quantum state, it does not leak charge, and reading it is not destructive in the same way.

## What it should do

Store a qubit for seconds in a nuclear spin (¹⁴N, ¹⁵N, or a nearby ¹³C) next to the NV.

Nuclear spins have a magnetic moment about a thousand times smaller than the electron's, so they hardly feel the noise that dephases the electron. The NV's own nitrogen nucleus is always there; ¹³C nuclei sit at random sites. The electron writes and reads them through the hyperfine interaction (QDL-03).

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Nuclear rotations by radio-frequency pulses | demonstrated | [waldherr2014] |  |
| Electron-nuclear swap (store and retrieve) | demonstrated | [maurer2012] |  |

## Entanglement

| What | Label | Sources | Note |
|---|---|---|---|
| Electron-nuclear Bell states; three nuclear spins entangled | demonstrated | [waldherr2014] | fidelity above 0.85 for the three-nuclear-spin state |

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Long memory for a room-temperature register | reported | [maurer2012] |  |
| Ancilla for room-temperature error correction | demonstrated | [waldherr2014] |  |
| Readout amplifier by repetitive mapping (QDL-05) | demonstrated | [neumann2010science] [dreau2013] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| Memory time | >1 s | reported: ¹³C, isotopically purified, decoupling plus laser dissipation, room temperature [maurer2012] | — | Set by the link time it must bridge; no link exists at room temperature yet (QDL-13 to QDL-16) |

## How to build it

Traveler variant: `qubit` (docs/process/TRAVELER.md). Steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S03 | **Homoepitaxial buffer growth (MPCVD).** Buries polishing damage and substrate impurities under fresh, controlled diamond; for qubits a ¹²C-enriched cap removes the nuclear-spin bath. | 950 | Safety: Hydrogen and methane are flammable: leak-checked lines, gas detectors, interlocked exhaust. Microwave leakage check after any maintenance. |
| S04 | **Post-growth clean and inspection.** Growth leaves a hydrogen-terminated, possibly graphitic surface; a second oxidizing clean restores the oxygen-terminated reference state for lithography. | 200 | Safety: As S02. |
| S05 | **Etched alignment marks.** Every later mask, including the nanoscale nitrogen apertures, aligns to these. They must be etched into diamond because the NV anneal (S07) exceeds gold's melting point (1064 °C). | 120 | Safety: Plasma tools: standard interlocks; chlorine-free recipes only. |
| S06 | **Nitrogen implantation through apertures.** Use ¹⁵N⁺ to tell implanted from native nitrogen; the ¹⁵N nucleus is the deterministic memory. | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S13 | **Atomic-layer-deposited Al₂O₃ gate insulator and passivation.** Al₂O₃ is both the gate insulator and the cap that stabilizes the hole gas. Deposition temperature sets the trade-off: hot ALD survives high-temperature operation; cold ALD keeps NO₂. | 450 | Safety: Trimethylaluminium is pyrophoric: sealed source, trained operators, never open to air. |
| S16 | **Mask 6 (METAL2): interconnect and pads.** Connects transistors into cells and brings every node to probe pads; the photocurrent electrodes and microwave line for qubits (QELEC) are drawn here too. | 120 | Safety: As S14. |
| S18 | **Quantum test (NV windows).** Add a radio-frequency source and find the nuclear transitions (Atlas M53). | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |
| S19 | **Dicing and high-temperature packaging.** Diamond's advantage is operating hot; the package must not become the limit. | 350 | Safety: Laser dicing fumes: local extraction. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M20 Low-energy ion implanter (¹⁵N); M22 High-vacuum annealing furnace (800–1200 °C); M53 RF source for nuclear spins (MHz range); M52 Electronic-grade, low-nitrogen, optionally ¹²C-enriched CVD diamond; M47 High numerical-aperture objective; M51 Arbitrary waveform generator (AWG)

## Pass/fail checks (simulated)

No nuclear decoupling model in the package yet; listed in docs/STATUS.md.

## Failure modes

- Laser light during electron readout dephases the nucleus
- ¹³C sites are random, so registers differ chip to chip

## Open problems

- A memory is only useful if a link can fill it; no room-temperature link exists yet.

## Links

Labs: labs/qubit.html. Chapters: [08_quantum_processor_architecture.md](../08_quantum_processor_architecture.md). Experiments: C2. Equation panels: —.
