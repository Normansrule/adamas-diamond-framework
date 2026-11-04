# QDL-23 Diamond gyroscope

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: proposed** (On paper only: theory, a proposal, or an ADAMAS design idea). Operating temperature: about 300 K. [ledbetter2012] [ajoy2012]

Proposal.

## What it should do

Sense rotation through the geometric phase of NV or ¹⁴N nuclear spins.

Proposals use the nuclear spin as a rotation sensor, for navigation without satellite positioning (GPS) together with the magnetometer.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Nuclear Ramsey sequence | proposed | [ledbetter2012] |  |

## Entanglement

None.

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Navigation without GPS | proposed | [ledbetter2012] |  |

## Figures of merit (current versus target)

None quantified yet.

## How to build it

Traveler variant: `sensor` (docs/process/TRAVELER.md). Steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S06 | **Nitrogen implantation through apertures.** Places nitrogen where qubits are wanted (layer QIMPLANT of PDK-0). Depth and dose set how many NV centers form and how close they sit to the surface. | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |
| S19 | **Dicing and high-temperature packaging.** Diamond's advantage is operating hot; the package must not become the limit. | 350 | Safety: Laser dicing fumes: local extraction. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M53 RF source for nuclear spins (MHz range); M59 Navigation test platform with a magnetic-anomaly map

## Pass/fail checks (simulated)

Proposal; no model in the package.

## Failure modes

- Magnetic field drift mimics rotation

## Open problems

- Competitive bias stability

## Links

Labs: labs/globe.html. Chapters: [11_proposed_experiments_and_roadmap.md](../11_proposed_experiments_and_roadmap.md). Experiments: —. Equation panels: —.
