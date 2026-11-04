# QDL-22 Optical hyperpolarizer

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [london2013] [king2015] [ajoy2018]

## What it should do

Transfer the NV's optical spin polarization to ¹³C nuclei to boost magnetic resonance signals.

Green light polarizes the NV; microwaves or level crossings pass that polarization to nuclear spins, in crystals and powders, at room temperature.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Polarization transfer (electron to nuclei) | demonstrated | [london2013] |  |

## Entanglement

None.

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Brighter agents for magnetic resonance imaging (MRI) and NMR | proposed | [ajoy2018] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| Signal enhancement over thermal | to confirm | Hyperpolarization enhancement: confirm from the paper [king2015] | — |  |

## How to build it

Traveler variant: `sensor` (docs/process/TRAVELER.md). Steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S06 | **Nitrogen implantation through apertures.** Places nitrogen where qubits are wanted (layer QIMPLANT of PDK-0). Depth and dose set how many NV centers form and how close they sit to the surface. | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M31 NV-rich diamond (irradiated and annealed HPHT); M38 532 nm laser, tens of mW; M53 RF source for nuclear spins (MHz range)

## Pass/fail checks (simulated)

No polarization-transfer model in the package.

## Failure modes

- Spin diffusion barrier near the NV

## Open problems

- Transferring polarization to molecules outside the diamond

## Links

Labs: —. Chapters: [10_current_experiments_and_industry.md](../10_current_experiments_and_industry.md). Experiments: —. Equation panels: —.
