# QDL-26 Many-body quantum simulator (dense ensemble)

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [choi2017] [zu2021]

The surface-spin version is proposed [cai2013].

## What it should do

Study interacting spin physics with dense NV ensembles whose dipolar coupling is strong.

Dense NV ensembles show discrete time-crystalline order and emergent hydrodynamics at room temperature. A surface-spin simulator is proposed.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Global Floquet driving of the ensemble | demonstrated | [choi2017] |  |

## Entanglement

| What | Label | Sources | Note |
|---|---|---|---|
| Many-body correlations (not individually addressed) | demonstrated | [choi2017] [zu2021] |  |
| Patterned surface-spin lattice | proposed | [cai2013] |  |

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Time crystals and hydrodynamics | demonstrated | [choi2017] [zu2021] |  |

## Figures of merit (current versus target)

None quantified yet.

## How to build it

Traveler variant: `sensor` (docs/process/TRAVELER.md). Steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S06 | **Nitrogen implantation through apertures.** High dose for a dense ensemble. | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M20 Low-energy ion implanter (¹⁵N); M22 High-vacuum annealing furnace (800–1200 °C); M51 Arbitrary waveform generator (AWG)

## Pass/fail checks (simulated)

No many-body model in the package.

## Failure modes

- Disorder from P1 centers

## Open problems

- Single-site control

## Links

Labs: —. Chapters: [11_proposed_experiments_and_roadmap.md](../11_proposed_experiments_and_roadmap.md). Experiments: —. Equation panels: —.
