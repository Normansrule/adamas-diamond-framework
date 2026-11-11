# QDL-16 Nuclear-spin-mediated coupler

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: proposed** (On paper only: theory, a proposal, or an ADAMAS design idea). Operating temperature: about 300 K. [bermudez2011]

Proposal.

## What it should do

Use nuclear spins between NVs to relay their interaction.

A proposal in which nuclear spins mediate coupling between electron spins, relaxing the spacing requirement of QDL-04.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Nuclear-mediated two-qubit gate | proposed | [bermudez2011] |  |

## Entanglement

| What | Label | Sources | Note |
|---|---|---|---|
| Electron-electron through nuclei | proposed | [bermudez2011] |  |

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Wiring registers | proposed | [bermudez2011] |  |

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
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M20 Low-energy ion implanter (¹⁵N); M22 High-vacuum annealing furnace (800–1200 °C); M53 RF source for nuclear spins (MHz range)

## Pass/fail checks (simulated)

Proposal; no model in the package.

## Failure modes

- Random nuclear positions

## Open problems

- Any demonstration

## Links

Labs: —. Chapters: [08_quantum_processor_architecture.md](../08_quantum_processor_architecture.md). Experiments: —. Equation panels: —.
