# P8 · Frontier: where diamond beats the incumbent, with evidence

_Generated from `adamas/build_program.py` (`adamas build docs`); every number below is computed by the package._

**Status: written in full.** Budget: **not priced** (application-specific test benches, shielded rooms and irradiation facilities; no sourced prices). Gate verdict: **go**.

P8 is not one experiment. It asks, application by application, whether diamond beats the device it would replace, and answers with an **evidence ledger** whose rules are evaluated by code, so an inflated claim fails the build the way a failed measurement fails the earlier phases. Claims and readiness levels are this repository's judgment; the rules check them against the evidence. Nothing here is a new measurement: comparisons are **computed** over sourced parameter ranges or **cited**, and every row is labeled with the evidence behind it.

## Goal

For each application in the outline (grid and electric-vehicle power, hot and harsh-environment electronics, radiation detection, medical and field magnetometry, navigation, room-temperature quantum registers): name the incumbent, compare where a comparison can be computed or is published, assign a technology readiness level (TRL) no higher than the evidence allows, and name the key unsolved problem. Terms in the ledger: EV, electric vehicle; SiC, silicon carbide; MOSFET, metal-oxide-semiconductor field-effect transistor (FET); 2DHG, two-dimensional hole gas; GaN, gallium nitride; RF, radio frequency; NV, nitrogen-vacancy center; SQUID, superconducting quantum interference device; GPS, Global Positioning System.

## Rules (evaluated by code)

- **R1 Claim follows evidence.** "Beats" or "does not beat" needs either a computed comparison that is decisive over a sourced parameter **range** (its 10th percentile above 1, or its 90th below 1; a single point value is never decisive) or a cited measured comparison, with both numbers and the source, pointing the same way. A claim may not contradict a decisive computed comparison: no hiding a loss, and no hiding a win. "Undecided" means no decisive comparison is sourced; "not compared" is used only where no comparison is attempted on purpose.
- **R2 Readiness follows evidence.** TRL follows the NASA scale [mankins1995]; the cap is set by the strongest cited evidence: proposed or simulated ≤ 2, demonstrated in a lab ≤ 4, a component in a relevant environment ≤ 5, a prototype in a relevant environment ≤ 6, commercial ≤ 9. A claim that rests on a computed comparison is capped at 3.
- **R3 Name the problem.** Every application states its key unsolved problem.

## Physics and equations

- **Power switch loss:** with conduction loss I²R_on,sp/A and hard-switching loss ½C_oss,sp·A·V²·f, the area A that minimizes their sum gives a loss proportional to √(R_on,sp · C_oss,sp), so the ratio of silicon carbide's loss to diamond's is √[(R·C)_SiC / (R·C)_diamond] for a 1200 V device (`adamas.converter.optimum_switch`, `adamas.uncertainty.power_ratio`). Assumes a linear output capacitance (fully depleted drift), hard switching, the same converter topology and thermal design, and ignores packaging, gate drive and reliability. R_on includes the lattice mobility at the junction temperature and, for diamond's idealized bulk boron-doped vertical drift, the ionized fraction of the (uncompensated) boron, which is small at room temperature and grows with temperature. The diamond hole-mobility range is that of intrinsic material, an upper bound for a doped drift. Parameter ranges (Latin-hypercube sampled, 2000 samples): Diamond critical field 5 to 10 MV/cm [wort2008] [donato2020]; Diamond hole mobility 1000 to 3800 cm²/V·s [sanders2021] [volpe2009] [isberg2002]; Diamond permittivity 5.6 to 5.8 [sze2006]; SiC critical field 2.2 to 3 MV/cm [kimoto2014]; SiC electron mobility 700 to 1000 cm²/V·s [kimoto2014].
- **Result:** at 300 K the ratio is 0.26 to 0.49 (10th to 90th percentile): this diamond switch **loses**. With both junctions at 523 K, silicon carbide's package-limited ceiling [she2017], it is 1.24 to 2.35: diamond **wins**; the median crosses 1 at 415 K and 90 % of the samples are above 1 from 472 K. That win needs silicon carbide forced to its ceiling: cooled to 373 K against diamond at 523 K, the ratio is 0.83 to 1.57, **undecided**. And it is for an idealized device: the best demonstrated diamond switch [saha2023], a lateral 2DHG device scaled to 1200 V, against ideal silicon carbide gives 0.15 at 300 K and 0.13 at 523 K (one device against an ideal limit, so unfavourable to diamond, but measured).
- **Heat spreading:** single-crystal thermal conductivity, diamond 4.5 times silicon carbide's (`adamas.materials`, point values). A point value is not decisive, and the transistor's channel temperature also depends on the GaN–diamond interface.
- **Readiness:** TRL 1 to 9 [mankins1995]: 1 basic principles observed; 2 concept formulated; 3 analytical and experimental proof of concept; 4 component validated in the lab; 5 component validated in a relevant environment; 6 prototype in a relevant environment; 7 prototype in an operational environment; 8 system complete and qualified; 9 system proven in operation.

## Evidence ledger

| Application | Incumbent | Metric | Comparison (above 1 favours diamond) | Claim | Evidence | TRL | Rules pass? |
|---|---|---|---|---|---|---|---|
| EV traction inverter switch, 300 K junction | silicon carbide MOSFET [reimers2019] | switch loss at the area optimum (idealized bulk-doped diamond drift) | 0.26 to 0.49 (median 0.36) | **does not beat** (simulated) | demonstrated: 3.66 kV NO₂-doped lateral diamond MOSFETs on heteroepitaxial wafers [saha2023] | 3 (cap 3) | yes |
| Hot power switch, both junctions at 250 °C | silicon carbide MOSFET at its package ceiling [she2017] | switch loss at the area optimum (idealized bulk-doped diamond drift) | 1.24 to 2.35 (median 1.71) | **beats** (simulated) | simulated: model only: the bulk-doped vertical drift is not demonstrated; the demonstrated hot devices are lateral FETs at 400 °C [kawarada2014] | 2 (cap 2) | yes |
| Hot diamond (250 °C) against cooled silicon carbide (100 °C) | silicon carbide MOSFET with more cooling | switch loss at the area optimum (idealized bulk-doped diamond drift) | 0.83 to 1.57 (median 1.14) | **undecided** | simulated: model only | 2 (cap 2) | yes |
| Heat spreader under GaN transistors | silicon carbide substrate | substrate thermal conductivity (single-crystal point values; the channel temperature also depends on the interface) | 4.49 (point values; not decisive) | **undecided** | demonstrated: 4-inch GaN-on-diamond substrates [francis2010] | 4 (cap 4) | yes |
| Radiation detector and beam monitor | silicon detector | radiation hardness (dose to failure) | none sourced | **undecided** | relevant environment: diamond detectors for particle physics, including beam tests and irradiation studies, reviewed in [tapper2000] | 5 (cap 5) | yes |
| RF power amplifier | GaN transistor | output power density at matched frequency and efficiency | none sourced | **undecided** | demonstrated: 3.8 W/mm RF power density from an Al₂O₃-gated diamond MOSFET [imanishi2019] | 4 (cap 4) | yes |
| NV magnetometer (field, medical, geophysical) | fluxgate, optically pumped or SQUID magnetometers | sensitivity at room temperature | none sourced | **undecided** | demonstrated: compact nanotesla-sensitivity NV magnetometer [webb2019]; sensitivity limits reviewed in [barry2020] | 4 (cap 4) | yes |
| High-temperature logic | silicon carbide and silicon-on-insulator logic [watson2015] | gates working at temperature | none sourced | **undecided** | demonstrated: logic gates from hydrogen-terminated diamond FETs [liu2017] | 3 (cap 4) | yes |
| GPS-free navigation by magnetic-anomaly maps | inertial navigation with fluxgate or optically pumped magnetometers | position error over time | none sourced | **undecided** | proposed: no diamond navigation result is sourced here | 2 (cap 2) | yes |
| Room-temperature few-qubit register | none: no comparison with superconducting or trapped-ion processors is made, and none is implied | none | none sourced | **not compared** | demonstrated: two-NV entanglement at room temperature [dolde2013] | 3 (cap 4) | yes |

## Machines and facility

Atlas machines for this phase: M56 Converter test bench (double-pulse tester, power analyzer, thermal camera), M57 Irradiation access (gamma, proton), M58 Magnetically shielded room or gradiometer setup, M59 Navigation test platform with a magnetic-anomaly map. Each application needs its own facility: a converter test bench, a magnetically shielded room, an irradiation facility, a vehicle with a magnetic-anomaly map.

## Facility and safety

High-voltage converter tests run behind interlocked shields; irradiation is done only at licensed facilities under their radiation-safety program; lasers for NV magnetometers are Class 3B or 4. Each needs your institution's specific training and sign-off before first use; this page does not replace that training.

## Procedure

1. **For each application,** find the incumbent's number for the metric that matters, from a source.
2. **Compute** the comparison where a model exists, over sourced parameter ranges, or **cite** a measured one with both numbers.
3. **Assign** the TRL from the strongest evidence, not from the hope.
4. **Run the rules** (`adamas build docs` does it); fix the claim, not the rule, when one fails.
5. **Test** the leading application on its bench (M56 for power) to turn a computed comparison into a measured one.

## Expected results

![P8 comparison and ledger](../img/fig61_build_p8.png)

## Pass/fail

The gate passes when every ledger row passes R1 to R3. The rules are deterministic, so there is no pass rate; instead each rule is tested on a **degraded twin**: an inflated claim that it must reject.

| Twin | Fault | Why it must fail | Rule | Passes? |
|---|---|---|---|---|
| Hide a loss | claims the 300 K inverter switch **beats** SiC | computed ratio 0.26 to 0.49, decisively below 1 | R1 | no |
| Inflate readiness | gives the NV magnetometer TRL 6 | its evidence is a lab demonstration, cap 4 | R2 | no |
| Unsupported win | claims the RF amplifier **beats** GaN | no computed or cited comparison | R1 | no |
| Point value as proof | claims the heat spreader **beats** SiC from two conductivities | a point value is not decisive | R1 | no |
| Citation the wrong way | claims the detector **beats** silicon with a citation whose numbers favour silicon | the cited direction contradicts the claim | R1 | no |

## Key unsolved problems

- **EV traction inverter switch, 300 K junction:** boron is only partly ionized at room temperature, so a bulk-doped vertical drift has a high resistance; surface-doped lateral devices avoid it but are not demonstrated at traction-inverter current.
- **Hot power switch, both junctions at 250 °C:** the win needs silicon carbide forced to its ceiling; a vertical bulk-doped diamond switch, and a package and gate insulator that last years at 250 °C, do not exist yet.
- **Hot diamond (250 °C) against cooled silicon carbide (100 °C):** the value of running hot is a smaller cooling system, which this loss model does not price.
- **Heat spreader under GaN transistors:** the thermal boundary resistance at the GaN–diamond interface and polycrystalline diamond's lower conductivity can erase the gain; no sourced channel-temperature comparison.
- **Radiation detector and beam monitor:** no sourced dose-to-failure numbers for diamond and silicon here; charge-collection distance of polycrystalline material and the cost of single-crystal plates.
- **RF power amplifier:** no GaN number at matched conditions is sourced here; surface-conductivity stability under RF drive.
- **NV magnetometer (field, medical, geophysical):** medical use (brain and heart signals) needs femtotesla-level sensitivity; no sourced requirement or incumbent number is in this repository yet.
- **High-temperature logic:** only p-type FETs are mature, so complementary logic and its static power are open.
- **GPS-free navigation by magnetic-anomaly maps:** a vector magnetometer with sourced sensitivity, drift and vehicle-noise rejection; anomaly-map resolution.
- **Room-temperature few-qubit register:** coupling more than a few spins with high fidelity; readout time (P3 to P6 of this program).

## Not yet sourced

- Incumbent numbers for magnetometry (femtotesla-level medical requirements, fluxgate and optically pumped sensitivities) and for GaN RF power density at matched conditions.
- Any diamond navigation result, and a magnetic-anomaly navigation requirement.
- Radiation-hardness numbers (dose to failure) for diamond and silicon devices.
- A channel-temperature comparison of GaN on diamond and on silicon carbide.
- Prices of the test benches, shielded rooms and irradiation time, and of the cooling that a hot switch would save.

## Failure modes

- **A model comparison taken for a measurement:** the loss ratio is simulated; only a bench measurement (M56) at matched junction temperature makes it evidence of the next level.
- **Unfair comparisons:** an incumbent at a worse operating point (forced hot instead of cooled), a different topology, or a cherry-picked parameter; the ranges here are sourced and sampled, and the cooled case is shown.
- **Readiness drift:** levels raised by enthusiasm; rule R2 stops that in this repository.

## Decision gate

*Where does diamond beat the incumbent, with evidence?* With the evidence in this repository, the rows that claim a win and pass the rules are: Hot power switch, both junctions at 250 °C. That win is computed for an idealized device and needs silicon carbide at its ceiling; the demonstrated diamond device still loses there, and against cooled silicon carbide the comparison is undecided. Everywhere else the honest answer is "does not beat", "undecided" or "not compared", and the key problem above says what would change it. Building a vertical diamond switch and measuring it hot on the converter bench is the experiment that would move the power rows.

Sources: [mankins1995] [wort2008] [donato2020] [sanders2021] [volpe2009] [isberg2002] [sze2006] [kimoto2014] [she2017] [saha2023] [reimers2019] [kawarada2014] [francis2010] [tapper2000] [imanishi2019] [webb2019] [barry2020] [watson2015] [liu2017] [dolde2013]
