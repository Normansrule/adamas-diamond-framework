# QDL-28 Packaged sensor module

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [stuerner2021] [webb2019]

## What it should do

Put the diamond, light source, filter, detector and antenna in one portable package.

Compact and portable NV magnetometers are built and sold; the A1 kit is the teaching version.

## Gates it can hold

None.

## Entanglement

None.

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Field magnetometry | demonstrated | [stuerner2021] |  |
| Teaching | demonstrated | [sewani2020] |  |

## Figures of merit (current versus target)

None quantified yet.

## How to build it

Traveler variant: `sensor` (docs/process/TRAVELER.md). Steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S19 | **Dicing and high-temperature packaging.** Assemble diamond, LED or laser, filter, photodiode and loop antenna. | 350 | Safety: Laser dicing fumes: local extraction. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M30 Green source: LED or under 1 mW 532 nm laser module; M31 NV-rich diamond (irradiated and annealed HPHT); M32 Longpass filter; M33 Silicon photodiode and transimpedance amplifier; M34 Phase-locked loop (PLL) microwave synthesizer, ADF4351 class; M35 Microstrip or loop antenna; M36 Microcontroller (Raspberry Pi Pico)

## Pass/fail checks (simulated)

| Check | Nominal (documented seed) | Degraded twin | Fault | Threshold source | Pass rate |
|---|---|---|---|---|---|
| The module sees the dip: dip depth / σ ≥ 5 at 2870 MHz (five-sigma detection) | 43.24 σ, **pass** | 3.061 σ, **fail** | Filter misaligned: twenty times less contrast | five-sigma convention (build program P1) | 1.00 ± 0.00 (200 seeds) |

## Failure modes

- Laser or LED drift

## Open problems

- Power and size for field use

## Links

Labs: —. Chapters: [10_current_experiments_and_industry.md](../10_current_experiments_and_industry.md). Experiments: A1. Equation panels: odmr.
