# Build program

_Generated from `adamas/build_program.py` (`adamas build docs`); every number below is computed by the package._

A ladder from a laptop to a pilot line. Each phase ends at a decision gate. P0 and P1 are written in full, with their gates evaluated by code; P2 to P8 are outlined in [phase0/BUILD_PROGRAM_OUTLINE.md](../phase0/BUILD_PROGRAM_OUTLINE.md) and are written one per release as their sources come in ([STATUS.md](../STATUS.md)).

| Phase | Name | Budget | Goal | Gate question | Status |
|---|---|---|---|---|---|
| P0 | Simulation | US$0 | Every later step is runnable in the app and calibrated against published data. | Do the models agree with published data well enough to plan hardware? | [written](P0_simulation.md) |
| P1 | Proof of concept | computed from the A1, A2, and A3 part lists | An ensemble ODMR magnetometer and thermometer from the A1 kit. | Is the signal-to-noise good enough to move to pulsed control? | [written](P1_proof_of_concept.md) |
| P2 | Teaching lab | US$1,000 to 12,000 (B tier) | Pulsed control (Rabi, Ramsey, echo), T1 and T2, vector magnetometry, boron activation energy. | Can we hold a spin coherent and measure deep dopants reliably? | outline |
| P3 | Single NV | US$10,000 to 100,000 (C tier) | Confocal microscope, antibunching, single-spin control, nuclear-spin register. | Do we have single, addressable registers? | outline |
| P4 | Devices | university cleanroom | Hydrogen-terminated FETs with Al2O3; I-V, breakdown, and temperature tests. | Do our devices match the models, run to run? | outline |
| P5 | Placement | shared facility | Implant through masks, anneal, conversion statistics, NV pairs closer than 30 nm. | Is placement yield good enough to plan arrays? | outline |
| P6 | Integration | packaging line or MPW partner | Diamond chiplets bonded to silicon CMOS control; multi-cell arrays. | Does integration keep coherence and yield? | outline |
| P7 | Pilot line and products | fab | Wafer-scale flow, statistical process control, first products. | Which product line pays for the line? | outline |
| P8 | Frontier and humanity | application-specific | Grid and EV efficiency, space electronics, medical magnetometry, navigation. | Where does diamond beat the incumbent, with evidence? | outline |
