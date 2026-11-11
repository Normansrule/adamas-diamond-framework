# QDL-10 Dark-spin chain bus

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: proposed** (On paper only: theory, a proposal, or an ADAMAS design idea). [yao2012]

Theory; chains not yet built.

**Analogy only:** a quantum wire (analogy) — the real device is the Dark-spin chain bus. Fits: It carries quantum information from one register to another. Breaks: It is a chain of nitrogen spins, and nobody has built one yet.

## What it should do

Move a qubit between NV registers 100 nm or more apart through a chain of optically dark nitrogen spins.

Yao and co-workers proposed chains of 5 to 20 nitrogen spins about 10 to 20 nm apart, swept by microwave pulses, to connect NV registers that can each be addressed optically. It assumes an NV T₁ of 100 to 250 ms, cooling to about 250 K, a donut-shaped readout beam and a field gradient.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| State transfer along the chain | proposed | [yao2012] |  |

## Entanglement

| What | Label | Sources | Note |
|---|---|---|---|
| Entanglement between distant registers | proposed | [yao2012] |  |

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Wiring a room-temperature processor | proposed | [yao2012] |  |

## Figures of merit (current versus target)

None quantified yet.

## How to build it

Traveler variant: `qubit` (docs/process/TRAVELER.md). Extension steps are written in the traveler's extension section; steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S03 | **Homoepitaxial buffer growth (MPCVD).** Buries polishing damage and substrate impurities under fresh, controlled diamond; for qubits a ¹²C-enriched cap removes the nuclear-spin bath. | 950 | Safety: Hydrogen and methane are flammable: leak-checked lines, gas detectors, interlocked exhaust. Microwave leakage check after any maintenance. |
| S06 | **Nitrogen implantation through apertures.** Places nitrogen where qubits are wanted (layer QIMPLANT of PDK-0). Depth and dose set how many NV centers form and how close they sit to the surface. | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| X10a | **Dark-spin chain placement.** A chain of optically dark nitrogen spins between two NV registers carries quantum information over hundreds of nanometres without photons. | — | **extension step** (proposed, docs/process/TRAVELER.md) [yao2012] Safety: Ion implanters: radiation and high-voltage interlocks; facility training. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M20 Low-energy ion implanter (¹⁵N); M21 Aperture masks (PMMA, AFM-tip) or focused ion beam; M22 High-vacuum annealing furnace (800–1200 °C)

## Pass/fail checks (simulated)

Theory only; no simulation in the package.

## Failure modes

- Nitrogen spins in the chain are missing or misplaced

## Open problems

- Building chains with the needed spacing
- Holding T₁ long enough

## Links

Labs: labs/machine.html. Chapters: [08_quantum_processor_architecture.md](../08_quantum_processor_architecture.md). Experiments: —. Equation panels: —.
