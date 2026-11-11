# QDL-20 Diamond thermometer (bulk and nanodiamond)

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [acosta2010] [kucsko2013] [toyli2013]

## What it should do

Measure temperature through the shift of the zero-field splitting D with temperature.

D falls by about 74 kHz per kelvin near room temperature. Nanodiamonds inside cells report local temperature.

## Gates it can hold

None.

## Entanglement

None.

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Temperature inside living cells | demonstrated | [kucsko2013] |  |
| Hot-spot mapping in chips | proposed | [turner2020] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| dD/dT | -74.2 ± 0.7 kHz/K | demonstrated: weighted average of four samples near 300 K [acosta2010] | — |  |

## How to build it

Traveler variant: `sensor` (docs/process/TRAVELER.md). Extension steps are written in the traveler's extension section; steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S06 | **Nitrogen implantation through apertures.** Places nitrogen where qubits are wanted (layer QIMPLANT of PDK-0). Depth and dose set how many NV centers form and how close they sit to the surface. | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| X20a | **Nanodiamond milling and surface treatment.** Nanodiamonds with many NV centers go where a plate cannot, such as inside a living cell, and read out temperature optically. | — | **extension step** (demonstrated, docs/process/TRAVELER.md) [kucsko2013] Safety: Nanoparticle powders: avoid inhalation; handle in suspension. Biological samples: the institution's biosafety rules. |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M31 NV-rich diamond (irradiated and annealed HPHT); M37 Permanent magnets and a non-magnetic rail; thermistor and heater for dD/dT; M44 Hot stage (to about 500 °C)

## Pass/fail checks (simulated)

| Check | Nominal (documented seed) | Degraded twin | Fault | Threshold source | Pass rate |
|---|---|---|---|---|---|
| dD/dT agrees with −74.2(7) kHz/K: |dD/dT − (−74.2)| ≤ 5.4 kHz/K | -79.5 kHz/K, **pass** | -65.39 kHz/K, **fail** | Poor thermal contact: the diamond sees 80 % of the change | ±k combined σ around [acosta2010] (98.98 % coverage) | 0.99 ± 0.01 (200 seeds) |

## Failure modes

- Laser heating
- Strain shifts D

## Open problems

- Calibration in biological media

## Links

Labs: labs/heat.html. Chapters: [06_nv_center_physics.md](../06_nv_center_physics.md). Experiments: A3. Equation panels: odmr.
