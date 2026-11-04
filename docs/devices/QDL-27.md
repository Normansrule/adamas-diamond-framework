# QDL-27 CMOS control and readout chiplet

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [kim2019cmos] [ibrahim2021]

## What it should do

Generate the microwaves and read the photons or photocurrent with a silicon chip bonded to the diamond.

Silicon CMOS can synthesize the microwave drive, filter the green light and detect red photons on one chip; diamond chiplets bonded on CMOS are demonstrated.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| On-chip microwave drive and optical detection for continuous-wave ODMR | demonstrated | [kim2019cmos] |  |
| Pulsed single-qubit gates from the chiplet | proposed | [ibrahim2021] |  |

## Entanglement

None.

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Chip-scale magnetometer | demonstrated | [kim2019cmos] [ibrahim2021] |  |
| Control plane for a register (build program P6) | proposed | [ibrahim2021] |  |

## Figures of merit (current versus target)

None quantified yet.

## How to build it

Traveler variant: `qubit` (docs/process/TRAVELER.md). Steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S19 | **Dicing and high-temperature packaging.** Flip-chip or wire-bond the diamond onto the CMOS die. | 350 | Safety: Laser dicing fumes: local extraction. |
| X27a | **CMOS die from a multi-project wafer (MPW) shuttle.** Design with open tools (M00) and order a shuttle. | — | **missing** (demonstrated) [kim2019cmos] |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M00 Workstation plus open tools (adamas, Stim, PyMatching, ngspice, Yosys, KLayout, OpenROAD); M26 Wafer or die bonder (thermocompression, hybrid); M29 CMOS control chip from a multi-project wafer (MPW) shuttle

## Pass/fail checks (simulated)

| Check | Nominal (documented seed) | Degraded twin | Fault | Threshold source | Pass rate |
|---|---|---|---|---|---|
| On-chip driver delivers the design Rabi frequency: |Ω_fit − 10 MHz| + k·σ ≤ 5 % | 10 MHz, **pass** | 4.999 MHz, **fail** | Driver gives half the current | ADAMAS design threshold: within 5 % of the design value, including k·σ | 1.00 ± 0.00 (200 seeds) |

## Failure modes

- Heating from the driver near the diamond
- Green light leaking through the filter

## Open problems

- Driving many qubits independently

## Links

Labs: labs/stack.html. Chapters: [09_cmos_control_integration.md](../09_cmos_control_integration.md). Experiments: —. Equation panels: rabi.
