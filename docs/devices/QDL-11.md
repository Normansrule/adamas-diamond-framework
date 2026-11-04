# QDL-11 Photonic link node (cryogenic)

_Generated from `adamas/qdl.py` (`adamas build docs`); do not edit by hand. Every number has a source key or is computed by the package._

**Status: cryogenic** (Demonstrated only when cooled to a few kelvin; not a room-temperature device today). Operating temperature: about 4 K. [bernien2013] [hensen2015] [pompili2021] [faraon2011]

Demonstrated only at cryogenic temperature (about 4 K). Superconducting qubits operate near 10 to 20 mK (dilution-refrigerator base below 20 mK, 14 mK under a 50-qubit load [krinner2019]). Nothing here implies parity with them.

## What it should do

Entangle distant NVs by interfering their photons.

Two NVs each emit a photon entangled with their spin; a beam splitter and detectors herald entanglement between them. It works only at a few kelvin, where the zero-phonon line is narrow; at room temperature only about 3 % of the light is in that line and it is broad. It is kept in the library as the reference link.

## Gates it can hold

| What | Label | Sources | Note |
|---|---|---|---|
| Heralded remote entanglement | cryogenic | [bernien2013] [pompili2021] |  |

## Entanglement

| What | Label | Sources | Note |
|---|---|---|---|
| Spin-spin entanglement over distance | cryogenic | [bernien2013] [hensen2015] |  |
| Three-node network | cryogenic | [pompili2021] |  |

## Use cases

| What | Label | Sources | Note |
|---|---|---|---|
| Quantum network and repeater | cryogenic | [pompili2021] [hermans2022] |  |

## Figures of merit (current versus target)

| Figure of merit | Current | Label and conditions | Target | Basis |
|---|---|---|---|---|
| Zero-phonon fraction of the emission | 0.03 | demonstrated: room-temperature emission; cavities raise it more than tenfold below 10 K [faraon2011] | — |  |

## How to build it

Traveler variant: `qubit` (docs/process/TRAVELER.md). Steps marked **missing** are not in the traveler yet (docs/STATUS.md).

| Step | What | Max °C | Notes |
|---|---|---|---|
| S01 | **Incoming substrate inspection.** Every later step inherits the substrate's defects: dislocations become leakage paths, polishing damage roughens the channel, nitrogen and silicon impurities add unwanted color centers. | 25 | Safety: Handle with plastic or diamond-safe tweezers; edges chip. |
| S02 | **Oxidizing acid clean.** Removes graphitic (non-diamond) carbon, metals, and organics, and leaves an oxygen-terminated reference surface. | 200 | Safety: Perchloric acid only in a perchloric-rated hood with wash-down; perchlorate residues are explosive. Hot concentrated acids: face shield, acid apron, heavy gloves; never add organics. Never boil a perchloric mixture to dryness: hot sulfuric acid can dehydrate HClO₄ to explosive anhydrous perchloric acid; top up or stop well before the volume falls. |
| S03 | **Homoepitaxial buffer growth (MPCVD).** Buries polishing damage and substrate impurities under fresh, controlled diamond; for qubits a ¹²C-enriched cap removes the nuclear-spin bath. | 950 | Safety: Hydrogen and methane are flammable: leak-checked lines, gas detectors, interlocked exhaust. Microwave leakage check after any maintenance. |
| S05 | **Etched alignment marks.** Every later mask, including the nanoscale nitrogen apertures, aligns to these. They must be etched into diamond because the NV anneal (S07) exceeds gold's melting point (1064 °C). | 120 | Safety: Plasma tools: standard interlocks; chlorine-free recipes only. |
| S06 | **Nitrogen implantation through apertures.** Places nitrogen where qubits are wanted (layer QIMPLANT of PDK-0). Depth and dose set how many NV centers form and how close they sit to the surface. | 25 | Safety: Ion implanter: radiation (X-ray) interlocks and high voltage. |
| S07 | **Vacancy anneal and oxygen re-termination.** Heating makes vacancies mobile; when one meets an implanted nitrogen it forms an NV center. The oxidizing clean then stabilizes the negative charge state that is the qubit. | 1100 | Safety: Furnace hot-zone burns; vacuum implosion shielding. |
| X11a | **Nanophotonic etch (cavity).** As QDL-09, with a cavity. | — | **missing** (cryogenic) [faraon2011] |
| S18 | **Quantum test (NV windows).** Measures the numbers that decide whether qubits work: resonance contrast, coherence, and charge-state stability. They feed the gate budget of chapter E5. | 25 | Safety: Class 3B/4 laser: interlocked enclosure, wavelength-rated eyewear. |

Hazardous steps need your institution's cleanroom, chemical, laser and high-voltage training before you start; the notes above do not replace it.

Machines (Atlas): M47 High numerical-aperture objective; M49 Two single-photon avalanche diodes (SPADs); M50 Time tagger (picosecond correlator)

## Pass/fail checks (simulated)

| Check | Nominal (documented seed) | Degraded twin | Fault | Threshold source | Pass rate |
|---|---|---|---|---|---|
| The link uses one emitter: g⁽²⁾(0) + 2σ < 0.5 [kurtsiefer2000] | 0.1919, **pass** | 0.6593, **fail** | Three NVs in the spot instead of one | 0.5 criterion [kurtsiefer2000] | 1.00 ± 0.00 (200 seeds) |

## Failure modes

- Spectral diffusion broadens the line
- Low photon rate

## Open problems

- A room-temperature photonic interface (unsolved); see QDL-13 to QDL-16.

## Links

Labs: labs/photon.html. Chapters: [08_quantum_processor_architecture.md](../08_quantum_processor_architecture.md). Experiments: C1. Equation panels: —.
