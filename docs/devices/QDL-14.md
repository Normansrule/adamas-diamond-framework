# QDL-14 Phonon (strain) bus through a diamond nanobeam

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: proposed** (On paper only: theory, a proposal, or an ADAMAS design idea). Operating temperature: about 300 K. [rabl2010] [ovartchaiyapong2014] [teissier2014]

Spin-strain coupling demonstrated; spin-spin link proposed.

## What it should do

Couple distant NVs through the vibrations of a diamond beam they sit in.

Strain changes the NV's levels, so a vibrating beam can drive the spin; this coupling is demonstrated. Using one mechanical mode to entangle two NVs is a proposal; thermal phonons at 300 K are the obstacle.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Spin driven by a mechanical mode | demonstrated | [ovartchaiyapong2014] [teissier2014] |  |
| Spin-spin gate through a phonon | proposed | [rabl2010] |  |

## Entanglement

| What | Label | Sources | Note |
|---|---|---|---|
| NV-NV via a shared mode | proposed | [rabl2010] |  |

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| On-chip room-temperature link | proposed | [rabl2010] |  |

## Figures of merit (current versus target)

None quantified yet.

## How to build it

Traveler variant: `qubit` (docs/process/TRAVELER.md). Extension steps are written in the traveler's extension section; steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S03 | **Homoepitaxial buffer growth (MPCVD).** Buries polishing damage and substrate impurities under fresh, controlled diamond; for qubits a ¹²C-enriched cap removes the nuclear-spin bath. | 950 | Safety: Hydrogen and methane are flammable: leak-checked lines, gas detectors, interlocked exhaust. Microwave leakage check after any maintenance. |
| S05 | **Etched alignment marks.** Every later mask, including the nanoscale nitrogen apertures, aligns to these. They must be etched into diamond because the NV anneal (S07) exceeds gold's melting point (1064 °C). | 120 | Safety: Plasma tools: standard interlocks; chlorine-free recipes only. |
| S06 | **Nitrogen implantation through apertures.** Places nitrogen where qubits are wanted (layer QIMPLANT of PDK-0). Depth and dose set how many NV centers form and how close they sit to the surface. | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| X14a | **Released diamond nanobeam.** A free-standing diamond cantilever with an NV inside lets the spin feel the beam's strain, so the beam's motion can drive or read the spin at room temperature. | 450 | **extension step** (demonstrated, docs/process/TRAVELER.md) [burek2012] [ovartchaiyapong2012] [ovartchaiyapong2014] [tao2014] Safety: Chlorine plasma: toxic gas controls. HSQ bonding uses HF later for removal: HF training. |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M12 Electron-beam lithography; M16 Inductively coupled plasma reactive-ion etching (ICP-RIE)

## Pass/fail checks (simulated)

No mechanical model in the package.

## Failure modes

- Thermal phonon occupation at 300 K

## Open problems

- High-Q beams and strong single-phonon coupling

## Links

Labs: —. Chapters: [08_quantum_processor_architecture.md](../08_quantum_processor_architecture.md). Experiments: —. Equation panels: —.
