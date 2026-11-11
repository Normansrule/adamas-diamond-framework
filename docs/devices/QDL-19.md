# QDL-19 Quantum diamond microscope

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [levine2019] [turner2020] [lesage2013]

## What it should do

Image magnetic fields over millimeters with a camera looking at an NV layer.

A thin NV ensemble layer under the sample is imaged onto a camera; each pixel is a magnetometer. Used on rocks, cells and working chips.

## Gates it can hold

None.

## Entanglement

None.

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Failure analysis of integrated circuits | demonstrated | [turner2020] |  |
| Imaging magnetotactic bacteria | demonstrated | [lesage2013] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| Field sensitivity per pixel | to confirm | Per-pixel sensitivity: confirm from the paper [levine2019] | — |  |

## How to build it

Traveler variant: `sensor` (docs/process/TRAVELER.md). Extension steps are written in the traveler's extension section; steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S06 | **Nitrogen implantation through apertures.** Shallow dense ensemble layer. | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M20 Low-energy ion implanter (¹⁵N); M22 High-vacuum annealing furnace (800–1200 °C); M38 532 nm laser, tens of mW; M43 Helmholtz coil set and current supplies

## Pass/fail checks (simulated)

| Check | Nominal (documented seed) | Degraded twin | Fault | Threshold source | Pass rate |
|---|---|---|---|---|---|
| Per-pixel dip is detected: dip depth / σ ≥ 5 at 2870 MHz (five-sigma detection) | 43.24 σ, **pass** | 3.061 σ, **fail** | Green background reaches the camera: twenty times less contrast | five-sigma convention (build program P1) | 1.00 ± 0.00 (200 seeds) |

## Failure modes

- Strain gradients across the field

## Open problems

- Sensitivity per pixel at video rate

## Links

Labs: —. Chapters: [10_current_experiments_and_industry.md](../10_current_experiments_and_industry.md). Experiments: A1. Equation panels: odmr.
