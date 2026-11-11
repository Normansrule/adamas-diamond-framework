# QDL-06 Optical reset (initialization)

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [gruber1997] [tetienne2012] [waldherr2014]

**Analogy only:** a pull-down resistor (analogy) — the real device is the Optical reset (initialization). Fits: It drains the state to a known value every cycle. Breaks: It works by optical pumping through a metastable level, not by dissipation in a resistor, and stops short of 100 % (0.82 in the rate model).

## What it should do

Pump the electron into mₛ = 0 with green light before every operation.

Under green light, mₛ = ±1 crosses more often into a metastable singlet that returns mostly to mₛ = 0, so after about a microsecond the spin sits in mₛ = 0 with high but not perfect probability. Nuclear spins are then initialized by swapping or by repeated measurement.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Reset of the electron to mₛ = 0 | demonstrated | [gruber1997] |  |
| Nuclear-spin initialization | demonstrated | [waldherr2014] |  |

## Entanglement

None.

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Every register and sensor cycle | demonstrated | [gruber1997] [barry2020] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| Electron polarization after pumping | 0.8179 | simulated: rate model, β = 1, 3 µs (adamas.photophysics) | — |  |

## How to build it

Traveler variant: `qubit` (docs/process/TRAVELER.md). Extension steps are written in the traveler's extension section; steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S18 | **Quantum test (NV windows).** Laser pulses gated by an acousto-optic modulator (M39). | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M38 532 nm laser, tens of mW; M39 Acousto-optic modulator (AOM); M42 Pulse timing: FPGA board or pulse generator; M46 Optical breadboard, mounts, laser goggles and interlock

## Pass/fail checks (simulated)

| Check | Nominal (documented seed) | Degraded twin | Fault | Threshold source | Pass rate |
|---|---|---|---|---|---|
| Pump reaches its steady state: polarization ≥ 0.99 × steady state (0.818) | 0.8179, **pass** | 0.765, **fail** | Laser pulse too short (0.1 µs) | ADAMAS design threshold: 0.99 of the steady state | 1.00 ± 0.00 (200 seeds) |

## Failure modes

- Too much power ionizes NV⁻ to NV⁰
- Pulse too short

## Open problems

- Electron polarization stops short of 100 % (0.82 in the rate model of adamas.photophysics); repeated measurement is needed for more.

## Links

Labs: labs/photon.html. Chapters: [06_nv_center_physics.md](../06_nv_center_physics.md). Experiments: B1. Equation panels: contrast.
