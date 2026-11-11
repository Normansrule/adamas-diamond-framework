# QDL-25 Room-temperature maser

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: demonstrated** (Demonstrated near room temperature, with a cited paper). Operating temperature: about 300 K. [breeze2018]

## What it should do

Amplify or emit microwaves near 9 GHz with optically pumped NVs in a cavity.

Optical pumping inverts the NV population; in a high-Q microwave cavity this gives continuous-wave maser action without cryogenics.

## Gates it can hold

None.

## Entanglement

None.

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Low-noise microwave amplifier | proposed | [breeze2018] |  |
| Maser-assisted ensemble readout (ADAMAS idea) | proposed | [breeze2018] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| Operating frequency (about) | 9 GHz | demonstrated: continuous wave, room temperature, in a cavity [breeze2018] | — |  |

## How to build it

Traveler variant: `sensor` (docs/process/TRAVELER.md). Extension steps are written in the traveler's extension section; steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S06 | **Nitrogen implantation through apertures.** High-density NV ensemble (or irradiated HPHT). | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| X25a | **Cavity assembly (sapphire or dielectric resonator).** Optically pumped NV centers in a high-quality microwave resonator amplify microwaves: a continuous-wave maser at room temperature. | — | **extension step** (demonstrated, docs/process/TRAVELER.md) [breeze2018] Safety: Class 4 laser (hundreds of mW): interlocked enclosure and laser training. Strong magnet: pacemakers, tools and pinch hazards. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M31 NV-rich diamond (irradiated and annealed HPHT); M38 532 nm laser, tens of mW; M41 Fast RF switch and 1–10 W microwave amplifier; M43 Helmholtz coil set and current supplies

## Pass/fail checks (simulated)

No maser model in the package.

## Failure modes

- Pump heating

## Open problems

- Compact pumping

## Links

Labs: —. Chapters: [10_current_experiments_and_industry.md](../10_current_experiments_and_industry.md). Experiments: —. Equation panels: —.
