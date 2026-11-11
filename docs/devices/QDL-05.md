# QDL-05 Spin readout (four routes)

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [dreau2013] [shields2015] [siyushev2019] [hopper2018]

Single-shot readout at room temperature is demonstrated for nuclear spins only.

**Analogy only:** a sense amplifier (analogy) — the real device is the Spin readout (four routes). Fits: It turns a tiny state difference into a signal a circuit can use. Breaks: At room temperature the electron cannot yet be read in one shot; nuclear spins can.

## What it should do

Turn the spin state into a measurable signal: photons, photocurrent, or a charge state.

Route 1, optical: count red photons; only a fraction of a photon per shot is detected, so the electron readout is averaged. Route 2, spin-to-charge conversion (SCC): a timed laser sequence ionizes one spin state, and the charge state is then read with many photons. Route 3, photoelectric detection of magnetic resonance (PDMR): read the electrons the ionization frees as a current through electrodes. Route 4, nuclear single-shot: map the nucleus onto the electron thousands of times and add up the photons.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Projective measurement of the nucleus (single shot) | demonstrated | [neumann2010science] [dreau2013] |  |
| Averaged measurement of the electron | demonstrated | [hopper2018] |  |

## Entanglement

| What | Label | Sources | Note |
|---|---|---|---|
| None made; readout verifies the entanglement of QDL-03 and QDL-04 | demonstrated | [dolde2013] |  |

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Register readout | demonstrated | [dreau2013] |  |
| Electrical readout for chip-scale integration | demonstrated | [siyushev2019] [bourgeois2015] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| Nuclear single-shot readout fidelity | 0.96 ± 0.012 | demonstrated: ¹³C nucleus, 120 ms per readout, room temperature [dreau2013] | 0.96 | Reproduce the demonstrated value (check below) [dreau2013] |
| SCC readout noise relative to the projection limit | 2.76 × | demonstrated: room temperature; conventional optical readout 10.6× on the same NV [shields2015] | 1 × | Projection-noise limit (single-shot) |
| Optical readout contrast after pumping | 0.3082 | simulated: rate model of adamas.photophysics, β = 1, 0.3 µs window | — |  |

## How to build it

Traveler variant: `qubit` (docs/process/TRAVELER.md). Extension steps are written in the traveler's extension section; steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S03 | **Homoepitaxial buffer growth (MPCVD).** Buries polishing damage and substrate impurities under fresh, controlled diamond; for qubits a ¹²C-enriched cap removes the nuclear-spin bath. | 950 | Safety: Hydrogen and methane are flammable: leak-checked lines, gas detectors, interlocked exhaust. Microwave leakage check after any maintenance. |
| S04 | **Post-growth clean and inspection.** Growth leaves a hydrogen-terminated, possibly graphitic surface; a second oxidizing clean restores the oxygen-terminated reference state for lithography. | 200 | Safety: As S02. |
| S05 | **Etched alignment marks.** Every later mask, including the nanoscale nitrogen apertures, aligns to these. They must be etched into diamond because the NV anneal (S07) exceeds gold's melting point (1064 °C). | 120 | Safety: Plasma tools: standard interlocks; chlorine-free recipes only. |
| S06 | **Nitrogen implantation through apertures.** Places nitrogen where qubits are wanted (layer QIMPLANT of PDK-0). Depth and dose set how many NV centers form and how close they sit to the surface. | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S13 | **Atomic-layer-deposited Al₂O₃ gate insulator and passivation.** Al₂O₃ is both the gate insulator and the cap that stabilizes the hole gas. Deposition temperature sets the trade-off: hot ALD survives high-temperature operation; cold ALD keeps NO₂. | 450 | Safety: Trimethylaluminium is pyrophoric: sealed source, trained operators, never open to air. |
| S14 | **Mask 4 (GATE metal).** Photocurrent electrodes on the QELEC layer for route 3 (photoelectric). | 120 | Safety: Solvents for lift-off: fume hood. |
| S16 | **Mask 6 (METAL2): interconnect and pads.** Connects transistors into cells and brings every node to probe pads; the photocurrent electrodes and microwave line for qubits (QELEC) are drawn here too. | 120 | Safety: As S14. |
| S18 | **Quantum test (NV windows).** Add the orange/red charge-readout laser (Atlas M54) for SCC and the photocurrent chain (M55). | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |
| S19 | **Dicing and high-temperature packaging.** Diamond's advantage is operating hot; the package must not become the limit. | 350 | Safety: Laser dicing fumes: local extraction. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M47 High numerical-aperture objective; M49 Two single-photon avalanche diodes (SPADs); M50 Time tagger (picosecond correlator); M54 Two-color excitation for charge-state readout (orange or red laser); M55 Photoelectric readout chain (bias electrodes, lock-in, transimpedance); M13 Electron-beam evaporator (Ti/Pt/Au, Au)

## Pass/fail checks (simulated)

| Check | Nominal (documented seed) | Degraded twin | Fault | Threshold source | Pass rate |
|---|---|---|---|---|---|
| Repetitive nuclear readout reaches 0.96: readout fidelity ≥ 0.96 [dreau2013], no nuclear flips modeled | 0.9765, **pass** | 0.845, **fail** | Collection efficiency four times lower (no solid-immersion lens or waveguide) | 0.96 demonstrated [dreau2013] | 1.00 ± 0.00 (200 seeds) |

## Failure modes

- Nuclear spin flips during long readout
- Background light lowers contrast
- Photocurrent leakage from surface conduction

## Open problems

- Single-shot electron readout at room temperature
- Photoelectric readout of one NV among close neighbors

## Links

Labs: labs/photon.html. Chapters: [08_quantum_processor_architecture.md](../08_quantum_processor_architecture.md). Experiments: C1. Equation panels: contrast.
