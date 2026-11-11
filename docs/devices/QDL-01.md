# QDL-01 NV electron-spin qubit cell

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [rong2015] [balasubramanian2009] [doherty2013]

Superconducting qubits operate near 10 to 20 mK (dilution-refrigerator base below 20 mK, 14 mK under a 50-qubit load [krinner2019]). Nothing here implies parity with them.

**Analogy only:** a memory bit cell (analogy) — the real device is the NV electron-spin qubit cell. Fits: It holds one bit of state at one site and is written and read by wires and light. Breaks: It holds a quantum superposition, not a 0 or 1, it is read by averaging at room temperature, and it is not refreshed.

## What it should do

Hold one qubit in the electron spin of a nitrogen-vacancy (NV) center and rotate it with microwaves.

A nitrogen atom next to a missing carbon atom traps two electrons whose spin (S = 1) has three levels. Green light pumps it into mₛ = 0, microwaves near 2.87 GHz rotate it between mₛ = 0 and −1, and the red fluorescence is dimmer in mₛ = ±1 ([gruber1997]; contrast 0.31 in the rate model of adamas.photophysics), which reads it out. At room temperature the spin keeps its phase for milliseconds under a Hahn echo in ¹²C-enriched diamond. It is the qubit every other register device in this library serves.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Single-qubit rotations (X, Y, arbitrary axis) | demonstrated | [rong2015] | average fidelity 0.999952 by randomized benchmarking |
| Hahn echo and dynamical decoupling | demonstrated | [hahn1950] [balasubramanian2009] |  |

## Entanglement

| What | Label | Sources | Note |
|---|---|---|---|
| None alone; see the conditional gate (QDL-03) and the dipolar coupler (QDL-04) | demonstrated | [rong2015] |  |

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Processor qubit in a small room-temperature register | demonstrated | [rong2015] [waldherr2014] |  |
| Single-spin sensor (see QDL-17) | demonstrated | [degen2017] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| Single-qubit gate fidelity | 1 | demonstrated: room temperature, randomized benchmarking [rong2015] | 0.9999 | ADAMAS design threshold (proposed): stay below 10⁻⁴ error so two-qubit gates dominate the budget |
| Electron Hahn-echo T₂ | 1.8 ms | demonstrated: ¹²C-enriched diamond, room temperature [balasubramanian2009] | 0.4753 ms | T₂ a 0.99 two-NV gate at 10 nm needs (single-spin exponential bound, as r_max) (`adamas.qdl.required_t2_10nm_ms`) |

## How to build it

Traveler variant: `qubit` (docs/process/TRAVELER.md). Extension steps are written in the traveler's extension section; steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S03 | **Homoepitaxial buffer growth (MPCVD).** Grow with ¹²CH₄ (isotopically enriched) so ¹³C spins do not shorten T₂. | 950 | Safety: Hydrogen and methane are flammable: leak-checked lines, gas detectors, interlocked exhaust. Microwave leakage check after any maintenance. |
| S04 | **Post-growth clean and inspection.** Growth leaves a hydrogen-terminated, possibly graphitic surface; a second oxidizing clean restores the oxygen-terminated reference state for lithography. | 200 | Safety: As S02. |
| S05 | **Etched alignment marks.** Every later mask, including the nanoscale nitrogen apertures, aligns to these. They must be etched into diamond because the NV anneal (S07) exceeds gold's melting point (1064 °C). | 120 | Safety: Plasma tools: standard interlocks; chlorine-free recipes only. |
| S06 | **Nitrogen implantation through apertures.** Implant single ¹⁵N⁺ per aperture at 2.5 to 10 keV (about 4 to 15 nm deep by the rule of thumb in adamas.coupling). | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S13 | **Atomic-layer-deposited Al₂O₃ gate insulator and passivation.** Al₂O₃ is both the gate insulator and the cap that stabilizes the hole gas. Deposition temperature sets the trade-off: hot ALD survives high-temperature operation; cold ALD keeps NO₂. | 450 | Safety: Trimethylaluminium is pyrophoric: sealed source, trained operators, never open to air. |
| S16 | **Mask 6 (METAL2): interconnect and pads.** Connects transistors into cells and brings every node to probe pads; the photocurrent electrodes and microwave line for qubits (QELEC) are drawn here too. | 120 | Safety: As S14. |
| S18 | **Quantum test (NV windows).** Find the NV, measure ODMR, Rabi, Ramsey and echo (experiments B1 and C1). | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |
| S19 | **Dicing and high-temperature packaging.** Diamond's advantage is operating hot; the package must not become the limit. | 350 | Safety: Laser dicing fumes: local extraction. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M01 Microwave plasma chemical vapor deposition (MPCVD) reactor; M10 Wet bench: tri-acid and piranha cleans, HF; M12 Electron-beam lithography; M20 Low-energy ion implanter (¹⁵N); M21 Aperture masks (PMMA, AFM-tip) or focused ion beam; M22 High-vacuum annealing furnace (800–1200 °C); M47 High numerical-aperture objective; M49 Two single-photon avalanche diodes (SPADs); M51 Arbitrary waveform generator (AWG); M52 Electronic-grade, low-nitrogen, optionally ¹²C-enriched CVD diamond

## Pass/fail checks (simulated)

| Check | Nominal (documented seed) | Degraded twin | Fault | Threshold source | Pass rate |
|---|---|---|---|---|---|
| Echo long enough for a 0.99 gate at 10 nm: fitted T₂ − k·σ ≥ 475 µs (0.99 gate at 10 nm) | 1795 µs, **pass** | 97.96 µs, **fail** | Natural-abundance carbon and surface spins cut T₂ to 100 µs | adamas.qdl.required_t2_us (52 MHz nm³/r³ and the single-spin bound) | 1.00 ± 0.00 (200 seeds) |

## Failure modes

- Charge state flips to NV⁰ under light
- Surface spins shorten T₂ for shallow NVs
- Strain splits and broadens the lines

## Open problems

- Single-shot electron readout at room temperature does not exist yet (see QDL-05).

## Links

Labs: labs/qubit.html, labs/photon.html. Chapters: [06_nv_center_physics.md](../06_nv_center_physics.md). Experiments: B1, C1. Equation panels: rabi, ramsey, echo.
