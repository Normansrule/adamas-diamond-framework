# QDL-18 Nanoscale nuclear magnetic resonance (NMR) sensor

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [staudacher2013] [mamin2013] [aslam2017] [glenn2018] [lovchinsky2016]

## What it should do

Record nuclear magnetic resonance from zeptoliter to picoliter volumes on the diamond surface.

A shallow NV detects the oscillating field of nuclear spins in a sample on the surface; ensembles with synchronized readout resolve chemical shifts.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Dynamical-decoupling sensing sequences | demonstrated | [staudacher2013] [mamin2013] |  |

## Entanglement

None.

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Chemistry of tiny samples | demonstrated | [glenn2018] |  |
| Single-protein detection | demonstrated | [lovchinsky2016] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| Spectral resolution | to confirm | Chemical-shift resolution: confirm from the paper [glenn2018] | — |  |

## How to build it

Traveler variant: `sensor` (docs/process/TRAVELER.md). Extension steps are written in the traveler's extension section; steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S06 | **Nitrogen implantation through apertures.** Shallow NVs (2.5 keV, about 4 nm deep by adamas.coupling). | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M20 Low-energy ion implanter (¹⁵N); M22 High-vacuum annealing furnace (800–1200 °C); M47 High numerical-aperture objective; M51 Arbitrary waveform generator (AWG)

## Pass/fail checks (simulated)

No NMR model in the package yet.

## Failure modes

- Surface spins shorten coherence

## Open problems

- Robust shallow NVs

## Links

Labs: —. Chapters: [10_current_experiments_and_industry.md](../10_current_experiments_and_industry.md). Experiments: —. Equation panels: echo.
