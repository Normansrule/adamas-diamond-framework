# QDL-07 Charge-control electrodes

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: reported** (Published, with a bound or special conditions stated next to the number). Operating temperature: about 300 K. [hauf2011] [grotz2012] [doi2014]

Electrical charge control is reported; holding NV⁻ near 100 % under readout light is not.

## What it should do

Hold the NV in its negative charge state (NV⁻) with a gate voltage or a doped junction.

Only NV⁻ is a qubit. Surface termination and nearby dopants set the Fermi level, and electrodes can move it. A p-i-n junction can also pump charge.

## Gates it can hold

None.

## Entanglement

None.

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Raise the probability that both NVs of a pair start in NV⁻ | proposed | [grotz2012] |  |
| Electrically driven single-photon source | demonstrated | [mizuochi2012] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| NV⁻ fraction under readout | to confirm | NV⁻ fraction under electrical control: confirm from the paper [grotz2012] | — | As high as the gate budget needs (Machine Builder) |

## How to build it

Traveler variant: `qubit` (docs/process/TRAVELER.md). Extension steps are written in the traveler's extension section; steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S03 | **Homoepitaxial buffer growth (MPCVD).** Buries polishing damage and substrate impurities under fresh, controlled diamond; for qubits a ¹²C-enriched cap removes the nuclear-spin bath. | 950 | Safety: Hydrogen and methane are flammable: leak-checked lines, gas detectors, interlocked exhaust. Microwave leakage check after any maintenance. |
| X07a | **p-i-n doped growth (boron and phosphorus layers).** An NV center inside the intrinsic layer of a diamond p-i-n diode can be driven electrically: injected electrons and holes recombine at the defect, which then emits single photons at room temperature. | — | **extension step** (demonstrated, docs/process/TRAVELER.md) [mizuochi2012] Safety: Phosphine and diborane are highly toxic and pyrophoric: gas cabinets, detectors and the facility's toxic-gas training are mandatory. |
| S06 | **Nitrogen implantation through apertures.** Places nitrogen where qubits are wanted (layer QIMPLANT of PDK-0). Depth and dose set how many NV centers form and how close they sit to the surface. | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| S13 | **Atomic-layer-deposited Al₂O₃ gate insulator and passivation.** Al₂O₃ is both the gate insulator and the cap that stabilizes the hole gas. Deposition temperature sets the trade-off: hot ALD survives high-temperature operation; cold ALD keeps NO₂. | 450 | Safety: Trimethylaluminium is pyrophoric: sealed source, trained operators, never open to air. |
| S14 | **Mask 4 (GATE metal).** Gate electrodes over the NV region on the QELEC layer. | 120 | Safety: Solvents for lift-off: fume hood. |
| S16 | **Mask 6 (METAL2): interconnect and pads.** Connects transistors into cells and brings every node to probe pads; the photocurrent electrodes and microwave line for qubits (QELEC) are drawn here too. | 120 | Safety: As S14. |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M01 Microwave plasma chemical vapor deposition (MPCVD) reactor; M13 Electron-beam evaporator (Ti/Pt/Au, Au); M14 Atomic layer deposition (ALD) of Al₂O₃; M55 Photoelectric readout chain (bias electrodes, lock-in, transimpedance)

## Pass/fail checks (simulated)

No charge-state model in the package yet; listed in docs/STATUS.md.

## Failure modes

- Surface conduction shorts the gate
- Ionization under light outruns the electrical restore

## Open problems

- Deterministic NV⁻ preparation at room temperature.

## Links

Labs: labs/bias.html. Chapters: [07_nv_fabrication_and_placement.md](../07_nv_fabrication_and_placement.md). Experiments: —. Equation panels: —.
