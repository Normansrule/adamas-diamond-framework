# QDL-17 Scanning-probe magnetometer tip

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [casola2018] [rondin2014]

## What it should do

Image magnetic fields at the nanoscale with one NV in a diamond tip scanned over a sample.

One shallow NV at the apex of a diamond pillar on an atomic force microscope (AFM) cantilever maps stray fields of magnets, currents and superconductors.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Single-qubit sensing sequences | demonstrated | [degen2017] |  |

## Entanglement

None.

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Condensed-matter and data-storage imaging | demonstrated | [casola2018] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| Spatial resolution | to confirm | Tip spatial resolution: confirm from the paper [casola2018] | — |  |

## How to build it

Traveler variant: `sensor` (docs/process/TRAVELER.md). Steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S06 | **Nitrogen implantation through apertures.** Shallow single NVs (2.5 keV). | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| X17a | **Pillar tip etch and cantilever mount.** Etch a pillar around the NV and attach it to a cantilever. | — | **missing** (reported) [casola2018] |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M24 Atomic force microscopy (AFM); M47 High numerical-aperture objective; M49 Two single-photon avalanche diodes (SPADs)

## Pass/fail checks (simulated)

| Check | Nominal (documented seed) | Degraded twin | Fault | Threshold source | Pass rate |
|---|---|---|---|---|---|
| Single-NV dip is detected: dip depth / σ ≥ 5 at 2870 MHz (five-sigma detection) | 25.55 σ, **pass** | 3.806 σ, **fail** | Background light swamps the single NV | five-sigma convention (build program P1) | 1.00 ± 0.00 (200 seeds) |

## Failure modes

- Tip-sample distance drifts
- Shallow-NV coherence loss

## Open problems

- Coherence of NVs within 10 nm of the surface

## Links

Labs: —. Chapters: [06_nv_center_physics.md](../06_nv_center_physics.md). Experiments: C1. Equation panels: odmr.
