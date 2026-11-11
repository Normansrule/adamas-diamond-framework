# Quantum Device Library

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

The room-temperature diamond devices ADAMAS describes, with what each should do, the gates and entanglement it can hold, its use cases, its figures of merit with sources, and its build route on the process traveler. Analogies to silicon parts (transistor, memory cell, resistor) are analogies only and always appear next to the real name.

Superconducting qubits operate near 10 to 20 mK (dilution-refrigerator base below 20 mK, 14 mK under a 50-qubit load [krinner2019]). Nothing here implies parity with them.

Bell-state fidelity and gate fidelity are different metrics; they sit in different columns and are not ranked against each other.

## Status labels

- **demonstrated**: Demonstrated near room temperature, with a cited paper
- **reported**: Published, with a bound or special conditions stated next to the number
- **simulated**: Computed by this package, not measured
- **proposed**: On paper only: theory, a proposal, or an ADAMAS design idea
- **cryogenic**: Demonstrated only when cooled to a few kelvin; not a room-temperature device today

## Quantum register (computing)

| Device | Status | What it does | Checks |
|---|---|---|---|
| [QDL-01 NV electron-spin qubit cell](QDL-01.md) | demonstrated | Hold one qubit in the electron spin of a nitrogen-vacancy (NV) center and rotate it with microwaves. | pass (1.00) |
| [QDL-02 Nuclear-spin memory](QDL-02.md) | reported | Store a qubit for seconds in a nuclear spin (¹⁴N, ¹⁵N, or a nearby ¹³C) next to the NV. | — |
| [QDL-03 Electron-nuclear conditional gate](QDL-03.md) | demonstrated | Flip the electron only if the nucleus is in one state (a CNOT), using a pulse that resolves the hyperfine line. | pass (1.00) |
| [QDL-04 NV-NV dipolar coupler](QDL-04.md) | demonstrated | Entangle two NV electron spins through their magnetic dipole coupling, ν = 52 MHz nm³ / r³. | pass (1.00) |
| [QDL-05 Spin readout (four routes)](QDL-05.md) | demonstrated | Turn the spin state into a measurable signal: photons, photocurrent, or a charge state. | pass (1.00) |
| [QDL-06 Optical reset (initialization)](QDL-06.md) | demonstrated | Pump the electron into mₛ = 0 with green light before every operation. | pass (1.00) |
| [QDL-07 Charge-control electrodes](QDL-07.md) | reported | Hold the NV in its negative charge state (NV⁻) with a gate voltage or a doped junction. | — |
| [QDL-08 Microwave drive line (coplanar waveguide)](QDL-08.md) | demonstrated | Carry microwave pulses to the NVs as an oscillating magnetic field. | pass (1.00) |
| [QDL-09 Optical waveguide and photon collector](QDL-09.md) | reported | Collect more of the NV's red light with nanowires, solid-immersion lenses or waveguides. | — |

## Links between registers

| Device | Status | What it does | Checks |
|---|---|---|---|
| [QDL-10 Dark-spin chain bus](QDL-10.md) | proposed | Move a qubit between NV registers 100 nm or more apart through a chain of optically dark nitrogen spins. | — |
| [QDL-11 Photonic link node (cryogenic)](QDL-11.md) | cryogenic | Entangle distant NVs by interfering their photons. | pass (1.00) |
| [QDL-13 Optomechanical repeater node](QDL-13.md) | proposed | Link registers at room temperature by converting spin states through a mechanical resonator to light. | — |
| [QDL-14 Phonon (strain) bus through a diamond nanobeam](QDL-14.md) | proposed | Couple distant NVs through the vibrations of a diamond beam they sit in. | — |
| [QDL-15 Ferromagnet-mediated coupler](QDL-15.md) | proposed | Couple NVs microns apart through spin waves in a ferromagnetic strip. | — |
| [QDL-16 Nuclear-spin-mediated coupler](QDL-16.md) | proposed | Use nuclear spins between NVs to relay their interaction. | — |

## Sensing (physics and engineering)

| Device | Status | What it does | Checks |
|---|---|---|---|
| [QDL-12 Ensemble magnetometer](QDL-12.md) | demonstrated | Measure magnetic fields with millions of NVs at once, by the shift of their optically detected magnetic resonance (ODMR) lines. | pass (1.00) |
| [QDL-17 Scanning-probe magnetometer tip](QDL-17.md) | demonstrated | Image magnetic fields at the nanoscale with one NV in a diamond tip scanned over a sample. | pass (1.00) |
| [QDL-19 Quantum diamond microscope](QDL-19.md) | demonstrated | Image magnetic fields over millimeters with a camera looking at an NV layer. | pass (1.00) |

## Chemistry and materials analysis

| Device | Status | What it does | Checks |
|---|---|---|---|
| [QDL-18 Nanoscale nuclear magnetic resonance (NMR) sensor](QDL-18.md) | demonstrated | Record nuclear magnetic resonance from zeptoliter to picoliter volumes on the diamond surface. | — |
| [QDL-24 Electric-field and stress sensor](QDL-24.md) | demonstrated | Measure electric fields and stress through the NV's strain and Stark shifts. | — |

## Biology and medicine

| Device | Status | What it does | Checks |
|---|---|---|---|
| [QDL-20 Diamond thermometer (bulk and nanodiamond)](QDL-20.md) | demonstrated | Measure temperature through the shift of the zero-field splitting D with temperature. | pass (0.99) |
| [QDL-21 Biomagnetic sensor (neuron action potentials)](QDL-21.md) | demonstrated | Detect the magnetic field of a firing nerve without touching it. | pass (1.00) |
| [QDL-22 Optical hyperpolarizer](QDL-22.md) | demonstrated | Transfer the NV's optical spin polarization to ¹³C nuclei to boost magnetic resonance signals. | — |

## Navigation

| Device | Status | What it does | Checks |
|---|---|---|---|
| [QDL-23 Diamond gyroscope](QDL-23.md) | proposed | Sense rotation through the geometric phase of NV or ¹⁴N nuclear spins. | — |

## Communications and microwave

| Device | Status | What it does | Checks |
|---|---|---|---|
| [QDL-25 Room-temperature maser](QDL-25.md) | demonstrated | Amplify or emit microwaves near 9 GHz with optically pumped NVs in a cavity. | — |

## Quantum simulation

| Device | Status | What it does | Checks |
|---|---|---|---|
| [QDL-26 Many-body quantum simulator (dense ensemble)](QDL-26.md) | demonstrated | Study interacting spin physics with dense NV ensembles whose dipolar coupling is strong. | — |

## Design and integration

| Device | Status | What it does | Checks |
|---|---|---|---|
| [QDL-27 CMOS control and readout chiplet](QDL-27.md) | demonstrated | Generate the microwaves and read the photons or photocurrent with a silicon chip bonded to the diamond. | pass (1.00) |
| [QDL-28 Packaged sensor module](QDL-28.md) | demonstrated | Put the diamond, light source, filter, detector and antenna in one portable package. | pass (1.00) |

## Extension steps

Device-specific steps written as step sheets in the extension section of [docs/process/TRAVELER.md](../process/TRAVELER.md), with the evidence label of the step itself.

| Device | Step | Title | Evidence |
|---|---|---|---|
| QDL-07 | X07a | p-i-n doped growth (boron and phosphorus layers) | demonstrated |
| QDL-09 | X09a | Nanophotonic etch (nanopillars or waveguides) | demonstrated |
| QDL-10 | X10a | Dark-spin chain placement | proposed |
| QDL-11 | X11a | Nanophotonic etch (cavity) | cryogenic |
| QDL-13 | X13a | Optomechanical resonator fabrication | proposed |
| QDL-14 | X14a | Released diamond nanobeam | demonstrated |
| QDL-15 | X15a | Ferromagnet strip deposition | proposed · cryogenic |
| QDL-17 | X17a | Pillar tip etch and cantilever mount | demonstrated |
| QDL-20 | X20a | Nanodiamond milling and surface treatment | demonstrated |
| QDL-25 | X25a | Cavity assembly (sapphire or dielectric resonator) | demonstrated |
| QDL-27 | X27a | CMOS die from a multi-project wafer (MPW) shuttle | demonstrated |

## Build steps the traveler does not have yet

None: every device's build steps are in the traveler or its extension section.

## Numbers to confirm from the papers

| Device | Figure of merit | To confirm |
|---|---|---|
| QDL-07 | NV⁻ fraction under readout | NV⁻ fraction under electrical control: confirm from the paper |
| QDL-09 | Collection gain over bulk | Photon-collection gain of diamond nanowires: confirm from the paper |
| QDL-12 | Sensitivity | Ensemble sensitivity records: confirm from the paper |
| QDL-17 | Spatial resolution | Tip spatial resolution: confirm from the paper |
| QDL-18 | Spectral resolution | Chemical-shift resolution: confirm from the paper |
| QDL-19 | Field sensitivity per pixel | Per-pixel sensitivity: confirm from the paper |
| QDL-21 | Sensitivity | Biomagnetic sensitivity: confirm from the paper |
| QDL-22 | Signal enhancement over thermal | Hyperpolarization enhancement: confirm from the paper |
| QDL-24 | Electric-field sensitivity | Electric-field sensitivity: confirm from the paper |

## How pass/fail is computed

Each check simulates a measurement with a fixed seed, analyzes it with adamas.fitting where a fit applies, and compares it with a sourced threshold or an ADAMAS design threshold stated as such. Each has a degraded twin with one physical fault, which must fail. The pass rate column is the fraction of 200 independent seeds on which the nominal check passes.
