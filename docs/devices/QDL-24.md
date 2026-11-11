# QDL-24 Electric-field and stress sensor

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [dolde2011] [hsieh2019]

## What it should do

Measure electric fields and stress through the NV's strain and Stark shifts.

The NV levels respond to electric fields and stress; NVs in a diamond-anvil cell image stress and magnetism at megabar pressure.

## Gates it can hold

None.

## Entanglement

None.

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Electric-field sensing with a single NV | demonstrated | [dolde2011] |  |
| Materials at megabar pressure | demonstrated | [hsieh2019] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| Electric-field sensitivity | to confirm | Electric-field sensitivity: confirm from the paper [dolde2011] | — |  |

## How to build it

Traveler variant: `sensor` (docs/process/TRAVELER.md). Extension steps are written in the traveler's extension section; steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S06 | **Nitrogen implantation through apertures.** Shallow NV layer in an anvil culet for pressure work. | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M20 Low-energy ion implanter (¹⁵N); M22 High-vacuum annealing furnace (800–1200 °C); M47 High numerical-aperture objective

## Pass/fail checks (simulated)

No Stark or stress model in the package beyond adamas.nv strain.

## Failure modes

- Field and strain mix in the signal

## Open problems

- Separating electric and strain contributions

## Links

Labs: labs/lattice.html. Chapters: [06_nv_center_physics.md](../06_nv_center_physics.md). Experiments: —. Equation panels: —.
