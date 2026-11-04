# QDL-04 NV-NV dipolar coupler

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [dolde2013] [dolde2014] [joas2025]

Superconducting qubits operate near 10 to 20 mK (dilution-refrigerator base below 20 mK, 14 mK under a 50-qubit load [krinner2019]). Nothing here implies parity with them.

**Analogy only:** a transistor (analogy) — the real device is the NV-NV dipolar coupler. Fits: One NV's state controls the phase picked up by its neighbor. Breaks: The coupling is always on, falls as 1/r³, and only works for NVs about 10 to 25 nm apart.

## What it should do

Entangle two NV electron spins through their magnetic dipole coupling, ν = 52 MHz nm³ / r³.

Two electron spins a few nanometers apart feel each other's field. Echo pulses remove everything except the coupling, and waiting t = 1/(2ν) makes a controlled-phase gate. At 25 nm that takes about 0.15 ms, so coherence limits the spacing; at 10 nm placement is the hard part.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Controlled phase (CZ) by free evolution under echo | demonstrated | [dolde2013] [joas2025] |  |
| Optimal-control entangling gate | demonstrated | [dolde2014] |  |

## Entanglement

| What | Label | Sources | Note |
|---|---|---|---|
| Electron-electron Bell states between two NVs | demonstrated | [dolde2013] [dolde2014] | Bell-state fidelity, not gate fidelity |
| Gate fidelity measured on a 9.5 nm pair | demonstrated | [joas2025] | charge state pre-selected; a different metric from Bell fidelity |

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Two-qubit gate between registers | demonstrated | [joas2025] |  |
| Building block of the scalable architecture | proposed | [yao2012] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| Bell-state fidelity | 0.824 | demonstrated: two NVs about 25 nm apart, optimal control, room temperature [dolde2014] | 0.5 | Entanglement witness: above 0.5 proves entanglement (build program P5) |
| Two-qubit gate fidelity | 0.96 ± 0.025 | demonstrated: 9.5 nm pair, ambient conditions, charge state pre-selected [joas2025] | 0.99 | ADAMAS design target (proposed); the coherence bound allows it only for r ≤ r_max |
| Largest spacing for a 0.99 coherence-limited gate | — |  | 15.59 nm | From ν = 52 MHz nm³/r³ and T₂ = 1.8 ms [balasubramanian2009], single-spin exponential bound; the two-spin stretched-echo model (adamas.gate_budget) allows wider spacings (`adamas.qdl.r_max_nm`) |

## How to build it

Traveler variant: `qubit` (docs/process/TRAVELER.md). Steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S03 | **Homoepitaxial buffer growth (MPCVD).** Buries polishing damage and substrate impurities under fresh, controlled diamond; for qubits a ¹²C-enriched cap removes the nuclear-spin bath. | 950 | Safety: Hydrogen and methane are flammable: leak-checked lines, gas detectors, interlocked exhaust. Microwave leakage check after any maintenance. |
| S04 | **Post-growth clean and inspection.** Growth leaves a hydrogen-terminated, possibly graphitic surface; a second oxidizing clean restores the oxygen-terminated reference state for lithography. | 200 | Safety: As S02. |
| S05 | **Etched alignment marks.** Every later mask, including the nanoscale nitrogen apertures, aligns to these. They must be etched into diamond because the NV anneal (S07) exceeds gold's melting point (1064 °C). | 120 | Safety: Plasma tools: standard interlocks; chlorine-free recipes only. |
| S06 | **Nitrogen implantation through apertures.** One aperture with a dose that leaves about two NVs inside; their spacing is set by chance within the aperture and the implant straggle, so pairs inside the coupling horizon are found afterwards by double electron-electron resonance (S18). Separate sites 10 nm apart are below the traveler's 20 to 50 nm apertures (two-site model: Fab Journey W7, adamas.coupling.pair_yield). | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S13 | **Atomic-layer-deposited Al₂O₃ gate insulator and passivation.** Al₂O₃ is both the gate insulator and the cap that stabilizes the hole gas. Deposition temperature sets the trade-off: hot ALD survives high-temperature operation; cold ALD keeps NO₂. | 450 | Safety: Trimethylaluminium is pyrophoric: sealed source, trained operators, never open to air. |
| S16 | **Mask 6 (METAL2): interconnect and pads.** Connects transistors into cells and brings every node to probe pads; the photocurrent electrodes and microwave line for qubits (QELEC) are drawn here too. | 120 | Safety: As S14. |
| S18 | **Quantum test (NV windows).** Find a coupled pair by double electron-electron resonance (DEER) and measure ν. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |
| S19 | **Dicing and high-temperature packaging.** Diamond's advantage is operating hot; the package must not become the limit. | 350 | Safety: Laser dicing fumes: local extraction. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M12 Electron-beam lithography; M20 Low-energy ion implanter (¹⁵N); M21 Aperture masks (PMMA, AFM-tip) or focused ion beam; M22 High-vacuum annealing furnace (800–1200 °C); M24 Atomic force microscopy (AFM); M25 Laser writing of vacancies (detect-and-repair); M47 High numerical-aperture objective; M51 Arbitrary waveform generator (AWG)

## Pass/fail checks (simulated)

| Check | Nominal (documented seed) | Degraded twin | Fault | Threshold source | Pass rate |
|---|---|---|---|---|---|
| Coupling strong enough for a 0.99 gate: fitted coupling − k·σ ≥ 13.75 kHz (r ≤ 15.6 nm) | 52.07 kHz, **pass** | 1.929 kHz, **fail** | Placement error: the pair ends up 30 nm apart | r_max from ν = 52 MHz nm³/r³ and T₂ = 1.8 ms [balasubramanian2009] | 1.00 ± 0.00 (200 seeds) |

## Failure modes

- Pair too far apart (placement)
- One NV in the wrong charge state
- Cannot address two NVs closer than the diffraction limit

## Open problems

- Placing NVs 10 nm apart with high yield
- Addressing each NV of a close pair separately (Addressing Lab)

## Links

Labs: labs/addressing.html, labs/machine.html. Chapters: [07_nv_fabrication_and_placement.md](../07_nv_fabrication_and_placement.md), [08_quantum_processor_architecture.md](../08_quantum_processor_architecture.md). Experiments: C2. Equation panels: budget, crosstalk.
