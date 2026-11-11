# QDL-13 Optomechanical repeater node

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: proposed** (On paper only: theory, a proposal, or an ADAMAS design idea). Operating temperature: about 300 K. [ji2022]

Proposal; nothing built.

## What it should do

Link registers at room temperature by converting spin states through a mechanical resonator to light.

A proposal for a room-temperature quantum repeater that uses optomechanics instead of the cryogenic zero-phonon line. On paper only.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Heralded remote entanglement | proposed | [ji2022] |  |

## Entanglement

| What | Label | Sources | Note |
|---|---|---|---|
| Spin-spin over distance | proposed | [ji2022] |  |

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Room-temperature quantum network | proposed | [ji2022] |  |

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
| X13a | **Optomechanical resonator fabrication.** The proposal couples an NV spin to a mechanical oscillator through a magnetic tip, and the oscillator to telecom light in a cavity, to build a room-temperature quantum repeater. | — | **extension step** (proposed, docs/process/TRAVELER.md) [ji2022] Safety: High-power lasers in the cavity: Class 3B or 4 controls. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M12 Electron-beam lithography; M16 Inductively coupled plasma reactive-ion etching (ICP-RIE)

## Pass/fail checks (simulated)

Proposal; no model in the package.

## Failure modes

- Thermal phonons at 300 K

## Open problems

- Any experimental demonstration

## Links

Labs: —. Chapters: [08_quantum_processor_architecture.md](../08_quantum_processor_architecture.md). Experiments: —. Equation panels: —.
