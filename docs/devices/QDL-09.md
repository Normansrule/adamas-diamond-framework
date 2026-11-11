# QDL-09 Optical waveguide and photon collector

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: reported** (Published, with a bound or special conditions stated next to the number). Operating temperature: about 300 K. [babinec2010] [hadden2010] [riedel2017]

Collection gains are reported at room temperature; the exact factor for each structure is to be confirmed.

**Analogy only:** a interconnect for light (analogy) — the real device is the Optical waveguide and photon collector. Fits: It routes signals (photons) to where they are measured. Breaks: It only improves collection; at room temperature it does not make photons indistinguishable.

## What it should do

Collect more of the NV's red light with nanowires, solid-immersion lenses or waveguides.

Diamond's high refractive index traps most of the light inside. Etched nanopillars, solid-immersion lenses and waveguides guide it out, which shortens every readout. This raises the photons-per-repetition input of the readout check (QDL-05).

## Gates it can hold

None.

## Entanglement

None.

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Faster readout in registers and sensors | reported | [babinec2010] [hadden2010] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| Collection gain over bulk | to confirm | Photon-collection gain of diamond nanowires: confirm from the paper [babinec2010] | — |  |

## How to build it

Traveler variant: `qubit` (docs/process/TRAVELER.md). Extension steps are written in the traveler's extension section; steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S03 | **Homoepitaxial buffer growth (MPCVD).** Buries polishing damage and substrate impurities under fresh, controlled diamond; for qubits a ¹²C-enriched cap removes the nuclear-spin bath. | 950 | Safety: Hydrogen and methane are flammable: leak-checked lines, gas detectors, interlocked exhaust. Microwave leakage check after any maintenance. |
| S05 | **Etched alignment marks.** Every later mask, including the nanoscale nitrogen apertures, aligns to these. They must be etched into diamond because the NV anneal (S07) exceeds gold's melting point (1064 °C). | 120 | Safety: Plasma tools: standard interlocks; chlorine-free recipes only. |
| S06 | **Nitrogen implantation through apertures.** Places nitrogen where qubits are wanted (layer QIMPLANT of PDK-0). Depth and dose set how many NV centers form and how close they sit to the surface. | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| X09a | **Nanophotonic etch (nanopillars or waveguides).** A pillar or waveguide around an NV center guides its light out of the high-index diamond, so more photons reach the detector at lower laser power. | 200 | **extension step** (demonstrated, docs/process/TRAVELER.md) [babinec2010] [burek2012] [hausmann2010] Safety: HF: calcium gluconate gel at hand and HF-specific training. Chlorine is toxic and corrosive: interlocked gas cabinet. Hot tri-acid: face shield, acid hood. |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M12 Electron-beam lithography; M16 Inductively coupled plasma reactive-ion etching (ICP-RIE); M47 High numerical-aperture objective

## Pass/fail checks (simulated)

No optical (photonic) model in the package yet; its effect enters QDL-05's readout check.

## Failure modes

- Etch damage near the NV
- Surface charge in the pillar

## Open problems

- Indistinguishable photons need cryogenics (see QDL-11).

## Links

Labs: labs/photon.html. Chapters: [08_quantum_processor_architecture.md](../08_quantum_processor_architecture.md). Experiments: —. Equation panels: —.
