# QDL-12 Ensemble magnetometer

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [barry2020] [wolf2015] [stuerner2021]

## What it should do

Measure magnetic fields with millions of NVs at once, by the shift of their optically detected magnetic resonance (ODMR) lines.

A field B shifts the ODMR lines by 28 MHz per mT along each NV axis. Four crystal orientations give a vector magnetometer. It is the device that already pays: commercial sensors and teaching kits exist.

## Gates it can hold

None.

## Entanglement

| What | Label | Sources | Note |
|---|---|---|---|
| None needed (classical ensemble average) | demonstrated | [barry2020] |  |

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Magnetic anomaly and current sensing | demonstrated | [barry2020] |  |
| Teaching lab (experiments A1, A2, B2) | demonstrated | [sewani2020] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| Line shift per field | 28.03 MHz/mT | reported: physical constant, g = 2.0028 (adamas.nv) [doherty2013] | — |  |
| Sensitivity | 0.9 pT/√Hz | demonstrated: NV ensemble of about 10¹¹ centres in 8.5 × 10⁻⁴ mm³, room temperature, photon-shot-noise limited [wolf2015] | — |  |

## How to build it

Traveler variant: `sensor` (docs/process/TRAVELER.md). Extension steps are written in the traveler's extension section; steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S06 | **Nitrogen implantation through apertures.** High dose for an ensemble layer (traveler S06 [pezzagna2010]), or buy irradiated high-pressure high-temperature (HPHT) diamond (M31). | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |
| S19 | **Dicing and high-temperature packaging.** Diamond's advantage is operating hot; the package must not become the limit. | 350 | Safety: Laser dicing fumes: local extraction. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M30 Green source: LED or under 1 mW 532 nm laser module; M31 NV-rich diamond (irradiated and annealed HPHT); M32 Longpass filter; M33 Silicon photodiode and transimpedance amplifier; M34 Phase-locked loop (PLL) microwave synthesizer, ADF4351 class; M35 Microstrip or loop antenna; M36 Microcontroller (Raspberry Pi Pico)

## Pass/fail checks (simulated)

| Check | Nominal (documented seed) | Degraded twin | Fault | Threshold source | Pass rate |
|---|---|---|---|---|---|
| The dip is detected: dip depth / σ ≥ 5 at 2870 MHz (five-sigma detection) | 43.24 σ, **pass** | 3.061 σ, **fail** | Contrast twenty times lower (misaligned filter lets green through) | five-sigma convention (build program P1) | 1.00 ± 0.00 (200 seeds) |

## Failure modes

- Laser intensity noise
- Strain broadening

## Open problems

- Reaching the shot-noise limit in a small package

## Links

Labs: labs/lattice.html. Chapters: [06_nv_center_physics.md](../06_nv_center_physics.md). Experiments: A1, A2, B2. Equation panels: odmr.
