# QDL-08 Microwave drive line (coplanar waveguide)

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [fuchs2009] [kim2019cmos]

Classical device.

**Analogy only:** a word line with 50 Ω termination (resistor) (analogy) — the real device is the Microwave drive line (coplanar waveguide). Fits: It carries the control signal to many cells and is terminated so it does not reflect. Breaks: It is a classical wire: it drives qubits but carries no quantum information (the quantum wire is QDL-10).

## What it should do

Carry microwave pulses to the NVs as an oscillating magnetic field.

A gold coplanar waveguide (CPW) on the diamond carries microwave current near the 2.87 GHz resonance. The current makes a magnetic field at the NV whose strength sets the Rabi frequency. A 50 Ω termination keeps reflections from heating the chip unevenly. It is classical: noise on it is control error, not decoherence of a quantum bus.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Delivers the single-qubit gates of QDL-01 | demonstrated | [fuchs2009] |  |

## Entanglement

None.

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Every pulsed experiment | demonstrated | [fuchs2009] |  |

## Figures of merit (current versus target)

None quantified yet.

## How to build it

Traveler variant: `qubit` (docs/process/TRAVELER.md). Steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S13 | **Atomic-layer-deposited Al₂O₃ gate insulator and passivation.** Al₂O₃ is both the gate insulator and the cap that stabilizes the hole gas. Deposition temperature sets the trade-off: hot ALD survives high-temperature operation; cold ALD keeps NO₂. | 450 | Safety: Trimethylaluminium is pyrophoric: sealed source, trained operators, never open to air. |
| S14 | **Mask 4 (GATE metal).** The gate electrode sits on Al₂O₃ over the channel and must overlap the gap on both sides so the whole channel is controlled. | 120 | Safety: Solvents for lift-off: fume hood. |
| S15 | **Mask 5 (VIA): open Al₂O₃ over contacts.** Contacts need bare gold; the oxide is removed only where pads and probes land. | 25 | Safety: Hydrofluoric acid: HF-specific training, calcium gluconate gel at hand, never work alone. |
| S16 | **Mask 6 (METAL2): interconnect and pads.** METAL2 layer: CPW with ground planes, 50 Ω characteristic impedance, wire-bonded to a terminated board. | 120 | Safety: As S14. |
| S19 | **Dicing and high-temperature packaging.** Diamond's advantage is operating hot; the package must not become the limit. | 350 | Safety: Laser dicing fumes: local extraction. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M11 Optical lithography (mask aligner or laser writer); M13 Electron-beam evaporator (Ti/Pt/Au, Au); M28 Wire bonder and package; M41 Fast RF switch and 1–10 W microwave amplifier; M51 Arbitrary waveform generator (AWG)

## Pass/fail checks (simulated)

| Check | Nominal (documented seed) | Degraded twin | Fault | Threshold source | Pass rate |
|---|---|---|---|---|---|
| Line delivers the designed Rabi frequency: |Ω_fit − 10 MHz| + k·σ ≤ 5 % | 10 MHz, **pass** | 4.999 MHz, **fail** | 6 dB of extra loss (bad bond or mismatch) halves the field | ADAMAS design threshold: within 5 % of the design value, including k·σ | 1.00 ± 0.00 (200 seeds) |

## Failure modes

- Heating from high power
- Reflections from a poor termination

## Open problems

- Driving one NV of a close pair without the other (frequency or gradient addressing).

## Links

Labs: labs/qubit.html, labs/addressing.html. Chapters: [09_cmos_control_integration.md](../09_cmos_control_integration.md). Experiments: B1. Equation panels: rabi.
