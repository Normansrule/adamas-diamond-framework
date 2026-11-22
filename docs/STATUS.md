# What is skipped, deferred, or still an assumption, and why

This file lists everything in ADAMAS that is not finished, so nothing is skipped silently. Each item says whether it was fixed, why it waits, and what would close it. It is updated with every release; the audit's fix status is in [AUDIT.md §9](AUDIT.md#9-fix-status-in-v0270).

Last updated: v0.52.0 (2026-11-22).

## Open in v0.52.0: small drifts in the pilot line

[P7](build/P7_pilot_line.md) now compares CUSUM [page1954] and EWMA [roberts1959] charts with the Shewhart chart at equal false-alarm rate. What is still open:

| Item | Why it waits | What would close it |
|---|---|---|
| k = 0.5σ, λ = 0.2 and the 1σ drift | ADAMAS design choices and an illustrative drift | Tune them to the smallest drift that matters for a product, from P4 and P7 data |
| Several parameters at once | Only contact resistance is charted | A chart for each traveler check, or a multivariate chart, with the false-alarm rate shared across them |
| Verification of page1954 and roberts1959 | Entered by hand from their Crossref records | `make verify` |

## Open in v0.51.0: clustered killer defects

[P7](build/P7_pilot_line.md) now fits Stapper's negative-binomial yield [stapper1983] with a cluster parameter measured from the defect-monitor counts. What is still open:

| Item | Why it waits | What would close it |
|---|---|---|
| The cluster parameter α = 0.5 and the 10 mm product die | Illustrative; no diamond inspection data give α | α fitted to counts from real defect-monitor wafers |
| Where clusters sit on the wafer | Clustering enters only as die-to-die spread of density | A spatial wafer-map model (for example correlated density fields) fitted to inspection maps |
| The P7 gate itself | Still judges the monitor die with Murphy's model, where the models differ by 2.2 percentage points | Choose the model from the fitted α once real counts exist |

## Open in v0.50.0: error correction against both error types

`adamas.qec` adds the phase-flip code and the nine-qubit code [shor1995] (Figure 64, [P6](build/P6_integration.md)). What is still open:

| Item | Why it waits | What would close it |
|---|---|---|
| Noise model | Bit and phase flips are taken as independent with equal probability on every qubit; a real register has a different relaxation time T₁ and coherence time T₂ for each qubit (electron and nuclei), so the two error types are not equally likely | Measured T₁ and T₂ of each register qubit in a biased-noise model |
| Errors during correction | The codes assume perfect encoding, syndrome measurement and correction gates | A circuit-level model like `adamas.circuit_qec` for the nine-qubit code |
| Nine qubits in hardware | One P6 cell has three register qubits; nine need linked cells, which are not modeled | A cell-to-cell link model (see Open in v0.37.0) |

## Open in v0.49.0: Fab Journey photos

`adamas.photos` reads each candidate photo's license from Wikimedia Commons and logs only openly licensed ones ([references/images.psv](../references/images.psv)). What is still open:

| Item | Why it waits | What would close it |
|---|---|---|
| The photos themselves | Wikimedia Commons is blocked by the build container's network policy, so the four candidates (W1, S03, S05, S19) have not been fetched or license-checked yet | Run `make photos` (the v0.49.0 apply script does), or allow commons.wikimedia.org and upload.wikimedia.org in the build environment |
| Steps with no candidate | No openly licensed photo was found for an ion implanter, a tube furnace, a wet bench or a nitrogen-vacancy (NV) fluorescence setup; Commons category pages could not be read | Search the Commons categories (Ion implantation, Vacuum furnaces, Cleanroom equipment, Nitrogen-vacancy center in diamond) from a machine that can reach them; owner-made photos (CC BY) are welcome |
| Captions | Each caption is written here from the search result and the step; the Commons description was not readable, so the W1 link to [schreck2017] is hedged | Read each kept file's description and adjust its caption |

## Open in v0.48.0: every Atlas machine has a published price

The five machines that had no price now carry the published figures that exist, each with what it does not cover ([ATLAS.md](build/ATLAS.md)): 38 sourced, 20 estimated, 1 included, 1 at no cost, 0 unpriced. What is still open:

| Item | Why it waits | What would close it |
|---|---|---|
| M01 growth reactor and M02 HPHT plates come from marketplace listings | The suppliers are not named, the reactor listing does not say which model its range is for, and one plate listing contradicts itself (high-pressure high-temperature (HPHT) title, chemical vapor deposition (CVD) attribute); no maker publishes a price | A maker's quote |
| M03 is priced by a substrate, not the heteroepitaxy stack | Diamond Foundry's 18 mm substrate does not state its growth method; no iridium template or heteroepitaxial wafer price was found | A quote from a heteroepitaxy supplier |
| M25 is priced by general femtosecond laser time | Neither facility mentions diamond or color centers | A laser-writing collaboration or service |
| M59 covers the magnetometer rental only | The test vehicle and survey flights are not priced; no contractor rate card was found | A survey contractor's rate |
| Verification of the 9 new pages | Read on 18 November 2026; marketplace pages change without notice | Re-read before buying |

## Open in v0.47.0: open items closed from the sources

v0.47.0 re-read the sources behind the open items of v0.41.0 to v0.46.0. Closed: the last two open device numbers (QDL-07 NV⁻ fraction under bias, 0.55 to 0.6 [meniailava2025]; QDL-19 per-pixel sensitivity, 12.8 nT/√Hz with 0.54 µm pixels [oh2023]); published versions of three preprints (mccloskey2024, qu2024b, broadway2018) and the volume of liu2018; the microchiplet array's temperature (below 4 K, so R26 is cryogenic); the microdisk etch conditions [mitchell2019]; a maser irradiation dose [day2024]; the nanodiamond supplier's sizes [adamasfnd2026]; the NV quality-control service's accepted samples; and a second news report that names NV centers in the SBQuantum magnetometer. What is still open:

| Item | Why it waits | What would close it |
|---|---|---|
| QDL-07 and QDL-19 values are from preprints | Both are labeled reported, not demonstrated | The published versions |
| Maser anneal temperature and time (X25a) | Neither [breeze2018] nor [day2024] states them | Element Six's process or another paper |
| Etch times of the microdisk undercut (X13a) | [mitchell2019] gives powers, gases and 250 °C but no times; [khanaliloo2015] could not be read | The original paper |
| Laser-slicing kerf, thickness and wafer size (R11) | The releases of [sakamoto2023] give none; its volume is not confirmed | The full paper |
| Kerf of the commercial cutter (R55) and numbers for the NV quality-control service (R33) | Not published | A test order |
| Implantation energy for diamond (R16) | Diamond is listed only as a substrate | Ask the service |
| Element Six DNV grades, QuantumDiamonds QD m.0, SBQuantum sensitivity | No absolute NV density, field of view or sensitivity published | Datasheets |
| Verification of the 6 new papers, the corrected ones and 3 new web pages | Entered by hand from the pages read; the mccloskey2024 article number, the oh2023 title and the wan2019 co-authors were read from listings | `make verify` |

## Open in v0.46.0: Step Services

Every traveler step now has a route that performs it ([RETROFIT.md](process/RETROFIT.md), Figure 63). What is still open:

| Item | Why it waits | What would close it |
|---|---|---|
| Steps demonstrated but not offered for diamond | S02, S07, S08, S09, S11, S11E, S12 to S17: only papers perform them; no vendor found that offers tri-acid cleaning, vacancy annealing, hydrogen termination, NO₂ doping or ALD on customer diamond | A service quote, or running them in a shared cleanroom |
| Company statements without numbers | Kwan-tek NV quality control (R33) and Diamond Materials gold metallization (R50) give no numbers or stack; Coherent's cutter (R55) gives no kerf | Datasheets or a test order |
| Whether the NV quality-control service accepts patterned chips (R33) | The page describes diamonds, not finished chips | Ask the service |
| Gold directly on hydrogen-terminated diamond from a service (R50) | S09 needs gold without an adhesion metal; the service does not state its stack, so R50 does not count for S09 | Ask for the stack |
| AuGe die attach (R57) above the S19 budget | AuGe melts at 356 °C; S19 allows 350 °C | Check the Al₂O₃ and termination limits before raising it |
| General tools not stated for diamond (R44 maskless aligner, R51 hot chuck) | Small pieces on these tools are this repository's proposal | Run one diamond plate on each |
| HPHT and preprint sources | Birefringence values are from HPHT diamond (R34); R37, R39, R46, R48, R54 are preprints in the sources read | CVD measurements; the published versions |
| Verification of the 12 new papers | Entered by hand from the pages read; two titles (qu2024b, yang2017) were read from listings | `make verify` |

## Open in v0.45.0: Retrofit Map

The [Retrofit Map](process/RETROFIT.md) (`adamas.retrofit`) lists real processes for every build stage. What it does not have yet:

| Item | Why it waits | What would close it |
|---|---|---|
| Retrofit routes R12, R28, R31 | Laser slicing (silicon carbide), silver sintering (a non-diamond diode) and silicon cleanroom tools are proven, but not on diamond in the sources read | Run each on a diamond piece and record the result |
| Company statements without papers | Three-inch (Element Six with Orbray) and 100 and 200 mm (Diamond Foundry) single crystals, CMP roughness (Fraunhofer USA), plasma tool roughness (Oxford Instruments) | Published specifications or papers |
| Product specifications | Several product pages give no numbers (QuantumDiamonds QD m.0, SBQuantum, Element Six DNV grades' absolute NV density) | Datasheets |
| Operating temperature of the microchiplet array (R26) | Not restated from [wan2020] | Read the paper's methods |
| Laser-slicing kerf and thickness for diamond (R11) | Not in the parts of [sakamoto2023] that could be read | The full paper |
| Steps without a production route | 16 of 20 traveler steps have no route that performs them in production; S15 and S16 rest on silicon cleanroom tools only | A service or paper that runs each step on diamond |
| Diamond energy range at the implantation service (R16) | The page lists diamond but gives energies only for silicon carbide | Ask the service for ¹⁵N at the S06 energy |
| Verification of the nine new papers | Entered by hand from the pages read | `make verify` |

## Open in v0.44.0: traveler parameters read from the sources

| Item | Why it waits | What would close it |
|---|---|---|
| X07a layer thicknesses, growth temperature, gas mix, substrate orientation | The paper [mizuochi2012] and its supplement are paywalled and blocked from the container; the author's review [mizuochi2014] gives the doping, substrate and contacts but not these | The full paper |
| X13a membrane process | The proposal [ji2022] fabricates no device; the demonstrated diamond microdisk route [mitchell2016] is listed as an alternative, not as the proposal's membrane | A fabricated membrane with a magnetic tip |
| Etch powers, times and the undercut temperature for the microdisk route | Not stated in [mitchell2016]; [khanaliloo2015] could not be read from the container | Read [khanaliloo2015] |
| Verification of mizuochi2014 and mitchell2016 | Entered by hand from the documents read (mizuochi2014 is in Japanese, read from annex.jsap.or.jp) | `make verify` |

## Open in v0.43.0: Atlas prices for most of the rest

Eleven more machines are priced from published pages read on 15 November 2026 (see [build/ATLAS.md](build/ATLAS.md)); 33 of 60 are now sourced. What is left:

| Item | Why it waits | What would close it |
|---|---|---|
| Unpriced machines (5): M01 MPCVD reactor, M02 HPHT press, M03 heteroepitaxy, M25 laser writing of vacancies, M59 navigation test vehicle | No maker or service publishes a price | Quotes |
| Closest-tool rows M04, M05, M08, M09, M18 | The rate sheets found price laser machining of glass and sapphire, sample polishers and a chemical-mechanical polisher not stated for diamond, photoluminescence spectrometers and a general microscope, and a curve tracer listed for packaged discrete devices, not the diamond tools | A rate sheet or service price for diamond laser cutting, scaife polishing, photoluminescence mapping and a polarizing microscope |
| Partly priced rows M09, M53 to M57 | Each row names what is not priced: the etch-pit furnace, the radio-frequency amplifier and coil, the laser driver and optics, the bias electrodes (priced on M11 to M13), a power analyzer and a complete double-pulse tester, proton beam time | Quotes for the named parts; the proton facilities checked (Texas A&M, Berkeley 88-Inch, TRIUMF, PSI) quote on request |
| Old or undated pages | The Oregon State gamma rate is for 2023 to 2024; several store pages show no date; the UW Molecular Analysis Facility page no longer shows its 2023 date and lists new rates from 1 January 2027 | Re-read the pages each year; switch maf2023 to the 2027 table when it takes effect |
| Reseller prices | The power meter, thermal camera and double-pulse board prices come from resellers, and the camera was sold out when read | Maker list prices or quotes |
| Aalto shielded room | The page does not say whether the room is magnetically or radio-frequency shielded | Ask the facility |
| Thorlabs list prices | Thorlabs pages do not render for an automated reader | Read by a person |

## Open in v0.42.0: device numbers confirmed from the papers

Seven of the nine device figures of merit that said "confirm from the paper" now carry values read from the papers, with conditions: nanowire flux gain 10× [babinec2010], ensemble sensitivity 0.9 pT/√Hz [wolf2015], tip resolution about 20 nm [maletinsky2012], NMR spectral resolution 3 Hz [glenn2018], biomagnetic sensitivity 15 pT/√Hz [barry2016], hyperpolarization enhancement about 170,000 [king2015], electric-field sensitivity about 140 V/cm/√Hz [dolde2011]. Two stay open:

| Item | Why it waits | What would close it |
|---|---|---|
| QDL-07 NV⁻ fraction under electrical control | [grotz2012] reports a shift from NV⁰ to NV⁻ over a ±0.5 V gate but no fraction | A paper that states the fraction |
| QDL-19 per-pixel sensitivity | The review [levine2019] gives no per-pixel number in the parts read | A measured quantum diamond microscope sensitivity with its pixel size |
| Verification of ovartchaiyapong2012 | Entered by hand from the arXiv page (which links its DOI) | `make verify` |

## Open in v0.41.0: extension steps X07a to X27a

The eleven device-specific build steps are written as step sheets ([process/TRAVELER.md](process/TRAVELER.md), `adamas.traveler_ext`). Each parameter is read from its paper or marked *to source*. What they do not have yet:

| Item | Why it waits | What would close it |
|---|---|---|
| X07a doping levels, layer thicknesses and growth temperature | Doping closed in v0.44.0 from the author's review; thicknesses and growth conditions are in "Open in v0.44.0" | — |
| X10a, X13a, X15a are proposals | No fabricated device: deterministic spin-chain placement, a room-temperature membrane at the assumed quality factor, and a ferromagnet bus (which the proposal runs at 0.1 K) | A demonstration of each |
| X11a works only cryogenically | The cavity enhancement was measured below 10 K [faraon2011] | A room-temperature use case, or keep it labeled cryogenic |
| X20a nanodiamond size and milling | The arXiv version of [kucsko2013] has no separate supplement and states no size or treatment; the supplier is now named | The supplier's specification for the nanodiamonds used |
| X25a irradiation and anneal | The paper and its arXiv version say Element Six did these steps and give no energy, dose or anneal [breeze2018] | Element Six's process, or another maser paper that states it |
| Monolithic microdisk route (khanaliloo2015) | Partly closed in v0.44.0: the same group's later paper [mitchell2016] gives the process and results, added to X13a | Read [khanaliloo2015] for etch powers and times |
| Verification of maletinsky2012 | Entered by hand (published title and pages read from the university repository); its DOI is added by `make apply-verify`, not by hand | `make verify` |

## Open in v0.40.0: Machines and Facilities Atlas

The [Atlas](build/ATLAS.md) (`adamas.atlas_prices`) prices the 60 machines with published rate sheets and store pages, each read on 10 November 2026, and labels everything else. What it does not have yet:

| Item | Why it waits | What would close it |
|---|---|---|
| Unpriced machines (16) | Closed for 11 in v0.43.0; see "Open in v0.43.0" for the 5 left | — |
| Lab optics and detectors are estimates | Thorlabs pages did not render for an automated reader; single-photon detector and time-tagger makers do not publish prices | List prices read by a person, or quotes |
| Phase totals from hourly rates | Cleanroom and characterization prices are per hour, and the tool hours per phase are not modelled | An hours estimate per traveler step |
| Currency and fiscal year | Prices stay in their own currency (US$ or EUR) and year; no exchange rate is sourced, and rate sheets change every year | A dated exchange rate, and re-reading the pages each year |
| Per-machine acceptance tests | The Atlas links each machine to the phases (and so the gates) that use it; it does not give a buy-time acceptance test per tool | Acceptance criteria from vendor specifications |
| One facility per tool class | Most hourly rates come from one university (UW) and one internal rate sheet (Cornell); rates elsewhere differ | More rate sheets, to give ranges |

## Open in v0.39.0: build phase P8 (frontier)

[P8](build/P8_frontier.md) is written as an evidence ledger whose rules are evaluated by code (`adamas.build_program.p8_gate`). What it does not have yet:

| Item | Why it waits | What would close it |
|---|---|---|
| Incumbent numbers for magnetometry, RF and navigation | No sourced femtotesla medical requirement, fluxgate or optically pumped sensitivity, GaN RF power density at matched conditions, or navigation requirement | Sources for each, then a computed or cited comparison in the ledger |
| Radiation-hardness numbers | Only the review [tapper2000] is cited | Dose-to-failure data for diamond and silicon devices |
| Measured power comparison | The 523 K win is computed for an idealized bulk-doped vertical drift that is not demonstrated, with an intrinsic-material mobility range (an upper bound) and uncompensated boron | A vertical diamond switch measured on a converter bench (M56) at 250 °C, against cooled silicon carbide |
| Value of running hot | The loss model does not price the smaller cooling system a hot switch allows | A system cost model with sourced cooling costs |
| Claims and readiness levels | They are this repository's judgment; the rules check consistency with the evidence, not the judgment itself | Review by people working in each application |
| Prices of benches, shielded rooms and irradiation time | Not sourced | Quotes or facility rates |
| Verification of mankins1995 | Entered by hand; Crossref is not reachable from the build container | `make verify` |

## Open in v0.38.0: build phase P7 (pilot line)

[P7](build/P7_pilot_line.md) is written in full, with its gate evaluated by code (`adamas.build_program.p7_gate`). What it does not have yet:

| Item | Why it waits | What would close it |
|---|---|---|
| Illustrative inputs | The wafer-to-wafer spread of contact resistance, the killer-defect density (2 cm⁻²), the edge exclusion and both faults are chosen, not measured. The 2-inch wafer size [kim2021] and the 3 mm monitor die are the only fixed inputs; P4's contact resistance is itself illustrative | Values from a pilot-line run |
| Cost per good die and the product decision | No sourced wafer, test or product price; D2's part list is a planning estimate | Quotes and product prices |
| Clustered defects | Partly closed in v0.51.0: a negative-binomial yield with a fitted cluster parameter [stapper1983]; spatial cluster maps are still open (Open in v0.51.0) | A spatial wafer-map model fitted to inspection data |
| Small drifts and several parameters | Small drifts partly closed in v0.52.0 (CUSUM and EWMA on contact resistance); still one parameter only | Charts over every traveler check |
| Defect density to leakage and coherence | No model links dislocation density to leakage current or T₂ | Measured leakage and T₂ against etch-pit density |
| Product qualification | No sourced reliability criteria per product | Qualification standards for each product line |
| Verification of shewhart1931 | Entered by hand; Crossref is not reachable from the build container | `make verify` |

## Open in v0.37.0: build phase P6 (integration)

[P6](build/P6_integration.md) is written in full, with its gate evaluated by code (`adamas.build_program.p6_gate`). What it does not have yet:

| Item | Why it waits | What would close it |
|---|---|---|
| Illustrative inputs | T2, the stretch exponent and the noise reuse experiment B1's model; the T2 limit (0.8), the encoding fidelity f0 = 0.9 and the fidelity noise are chosen, not measured. The 10 MHz design and its 5 % tolerance come from QDL-27 | Values from a P6 run |
| Die or flip-chip bonder price, and the P6 total (M26 to M29) | Partly closed in v0.40.0: the [Atlas](build/ATLAS.md) has published hourly rates for wafer bonding, dicing and wire bonding [wnf2026] and shuttle prices [tinytapeout2026] [europractice2026]. No die or flip-chip bonder rate is sourced, and no total is given because the die area and tool hours are not modelled | A bonder rate, and an hours and area estimate for the P6 run |
| Multi-cell arrays | No model links two cells yet | A cell-to-cell link model (photonic or dipolar) driven by P5's pair yield |
| Photoelectric readout through the chiplet (M55) | No noise model of the readout chain | A photocurrent noise model checked against a measurement |
| Heating and green-light leakage (QDL-27 failure modes) | No thermal or optical model of the assembly | A thermal model of the driver and a filter-leakage measurement |
| Phase errors in the repetition code | Closed for independent flips with perfect gates in v0.50.0 (circuit-level and hardware items are in Open in v0.50.0): `adamas.qec` adds the phase-flip code and the nine-qubit code [shor1995], checked by exhaustive decoding | — |

## Open in v0.36.0: build phase P5 (placement)

[P5](build/P5_placement.md) is written in full, with its gate evaluated by code (`adamas.build_program.p5_gate`). What it does not have yet:

| Item | Why it waits | What would close it |
|---|---|---|
| Illustrative inputs | Aperture counts, ions per aperture, the 20 nm aperture, and the noise of the population and parity measurements are chosen to look like a typical run, not measured. The yield (1 %, limit 0.5 %) and the fidelity put in (0.67) are sourced | Values from a P5 run |
| Yield at high local fluence | 50 ions through a 20 nm aperture is about 1.6×10¹³ cm⁻², above S06's single-center range; the about 1 % yield [pezzagna2010] is extrapolated to it | The witness-array yield at the chosen fluence |
| Ion stopping | Depth and straggle use the rule of thumb of `adamas.coupling` (0.4 x depth), not a SRIM calculation | A SRIM run [ziegler2010] at the chosen energy, checked by SIMS |
| Coupling geometry | Both NVs are taken as quantized along [111]; pairs on different axes have a different angular factor | The full secular dipolar tensor for two NV axes |
| Coherence, charge state and addressing in the Bell check | The fidelity is put in as the published value; T₂ near the surface, charge-state preparation and same-axis pairs are not simulated | The `adamas.gate_budget` model driven by measured T₂, q and coupling |
| High-vacuum furnace (M22) and dynamic SIMS (M23) rates | Partly closed in v0.40.0: the [Atlas](build/ATLAS.md) gives the closest published rates, a rapid thermal anneal [wnf2026] and time-of-flight SIMS [maf2023], which are not the same tools | Rates for a high-vacuum 1200 °C furnace and for dynamic SIMS depth profiling |

## Open in v0.35.0: Entanglement Lab

The [Entanglement Lab](../web/labs/entangle.html) and [ENTANGLEMENT.md](ENTANGLEMENT.md) answer one question: can entanglement alone, with no physical connection, carry a message? It cannot (a theorem, checked numerically). What remains open:

| Item | Why it waits | What would close it |
|---|---|---|
| Six classic references in refs_m.psv (ghirardi1980, clauser1969, cirelson1980, ekert1991, bennett1992, wootters1982) | Entered by hand; Crossref was not reachable from the build machine | `make verify` then `make apply-verify` |
| Distributing entanglement between room-temperature NV devices | Every NV network result cited is cryogenic; no room-temperature NV-to-NV entanglement over a photonic link is reported | A sourced room-temperature mechanism, or keep it out of scope |
| Pre-shared entanglement stored in room-temperature ¹³C memories | Proposed only: the more-than-1-s memory [maurer2012] is one local spin, not half of a remote pair | A demonstration, then a model with storage decoherence |
| Photon loss, heralding rate and memory decay in the lab | The lab models the pair only as a Werner state | Rates from [humphreys2018] and [stolk2024] in a link model |

## Open in v0.34.0: build phase P4 (devices)

[P4](build/P4_devices.md) is written in full, with its gate evaluated by code (`adamas.build_program.p4_gate`). What it does not have yet:

| Item | Why it waits | What would close it |
|---|---|---|
| Illustrative inputs | Sheet resistance (10 kΩ/sq), contact resistance (3 Ω·mm), threshold spread (60 mV), noise levels, and the PDK-0 FET values of `adamas.logic` (150 cm²/V·s, 1.0 V, 30 nm Al₂O₃ with relative permittivity 9) are chosen inside published ranges, not measured | Measured values from a P4 run, entered into `adamas.logic` and the SPICE models |
| Pass limits marked ADAMAS | The 10 Ω·mm contact limit and the 3 to 30 kΩ/sq sheet window are this project's engineering targets (traveler S17, S08), not literature values | Sourced typical values, or a decision after the first run |
| Hot operation, breakdown, on/off ratio, ring oscillators | No temperature-dependent FET model, no off-current or oscillator noise model, and no simulated breakdown structure (the breakdown fit in `adamas.power` is proposed) | Models with sources, then a criterion each |
| Prices of the curve tracer (M18) and the photoelectric readout chain (M55) | No sourced price | Quotes or sourced street prices |

## Open in v0.33.0: build phase P3 (single NV)

[P3](build/P3_single_nv.md) is written in full, with its gate evaluated by code (`adamas.build_program.p3_gate`). What it does not have yet:

| Item | Why it waits | What would close it |
|---|---|---|
| Illustrative inputs | The background fraction (ρ² = 0.8), antibunching time (12 ns), bias field (1 mT), line width (0.4 MHz), nuclear Rabi frequency (10 kHz) and all noise levels are chosen to look like a typical confocal setup; none is measured or sourced. Only the ¹⁴N hyperfine constant (2.147 MHz [felton2009]) is sourced | Measured values from a P3 setup, or sourced typical values |
| Uncertainty of the ¹⁴N hyperfine constant | 2.147 MHz [felton2009] is used without its published uncertainty, and other papers report values a little higher; so the P3 hyperfine test checks that the triplet is resolved, not the value | Record the published uncertainty (and other measurements) from the papers, then add a value test with the combined uncertainty, as P1 does for dD/dT |
| Field for nuclear polarization | The procedure says "near the excited-state level anticrossing" [jacques2009] without a number, because the field value is not yet recorded from the paper | Confirm the field from [jacques2009] |
| Price of the nuclear-spin RF source (M53) and the charge-state laser (M54) | No sourced price; the C1 part list does not include them | A quote or a sourced street price |
| Single-shot nuclear readout, charge state (M54), electron–nuclear gate | No model in the package for repetitive readout or NV⁻/NV⁰ dynamics; the register's CNOT is computed as a Bell-state fidelity, not a gate fidelity | Models with sources, then a criterion each |

## Open in v0.32.0: Fab Journey

The Fab Journey ([docs/journey/README.md](journey/README.md), `adamas/journey.py`) shows code-drawn diagrams only. What it does not have yet:

| Item | Why it waits | What would close it |
|---|---|---|
| Photos | references/images.psv is empty: Wikimedia Commons could not be reached from the build container to check licenses (v0.49.0: `make photos` checks them on a machine that can reach Commons) | Run `make photos` on a machine that can reach Commons; it logs only allowed licenses. Candidates: W1 "Single-crystal CVD diamond disc" (chemical vapor deposition, CVD); S03 "CVD Reaction Chamber, GPN-2000-001466" (NASA; a CVD chamber, not a diamond reactor, and must be captioned so); S05 "JEOL Electron Beam Lithography (EBL)" (Flickr upload); S19 "TF78 60 – Wire bonding". Owner-made build photos for L0 (CC BY) are welcome |
| L3 control charts | No wafer has been measured; the page shows the traveler limits only, with no invented data | Log measured wafers |
| W7 placement yield | Uses illustrative inputs (5 nm spread per axis, 10 nm design spacing) with the sourced 1 % conversion [pezzagna2010] | Measured placement spread and conversion |
| W8 array gate | No sourced threshold for "good enough"; the page computes sites needed for a target the reader sets and gives no verdict | A decision in build phase P5 |
| Step times and costs for L2 and L3 | Not sourced, so not shown | Facility quotes |

## Open in v0.31.0: Quantum Device Library

The Quantum Device Library ([docs/devices/README.md](devices/README.md), `adamas/qdl.py`) lists 28 devices. What it does not have yet:

| Device | Item | Why it waits |
|---|---|---|
| QDL-07, 09, 10, 11, 13, 14, 15, 17, 20, 25, 27 | Build steps X07a to X27a | Closed in v0.41.0: written as extension steps in [process/TRAVELER.md](process/TRAVELER.md) (`adamas.traveler_ext`); open parameters inside them are listed under "Open in v0.41.0" |
| QDL-02, 07, 09, 10, 13 to 16, 18, 22 to 26 | No simulated pass/fail check | The package has no model for these devices yet (nuclear decoupling, charge state, photonics, mechanics, NMR, maser, many-body); each page says which |
| All | Photos of build steps (Fab Journey, planned for v0.32.0) | Wikimedia Commons licenses could not be checked from the build container; diagrams only until each license is logged in references/images.psv with a test |
| QDL-05 | [dreau2013] metadata | Checked on arXiv (1210.6195); awaiting Crossref verification (`make verify`) |

Numbers that exist in the papers but are not yet confirmed from them (the device pages say "to confirm" instead of a value):

| Device | Figure of merit | To confirm |
|---|---|---|
| QDL-07 | NV⁻ fraction under readout | NV⁻ fraction under electrical control: [grotz2012] shifts an ensemble from NV⁰ to NV⁻ over a ±0.5 V electrolytic gate but states no fraction; needs another source |
| QDL-19 | Field sensitivity per pixel | Per-pixel sensitivity: the review [levine2019] defines a volume-normalized sensitivity but no per-pixel number was found in the parts read; needs a measured value |
| QDL-09, 12, 17, 18, 21, 22, 24 | Seven figures of merit | Closed in v0.42.0: values read from the papers with their conditions (all seven measured at room temperature or ambient conditions) |

## Fixed in v0.30.0

| Item | Was | Now |
|---|---|---|
| Build program phase P2 (teaching lab) | Outline | Written in full ([docs/build/P2_teaching_lab.md](build/P2_teaching_lab.md)); its gate is evaluated from simulated B1, B2, and B3 data fitted with the Data Lab's code; each test is set so a correct setup passes the whole gate 95 % of the time, checked over 1000 simulated setups |

## Fixed in v0.29.0

| Item | Was | Now |
|---|---|---|
| Build program phases P0 and P1 | Outline only | Written in full in [docs/build](build/README.md), generated by `adamas.build_program`; both gates are evaluated by code (P0 from the validation matrix, P1 from a simulated A1 kit fitted with the Data Lab's code); a [Build Program page](https://normansrule.github.io/adamas-diamond-framework/build.html) re-runs P1 in the browser |
| One electron gyromagnetic ratio everywhere | The fitting code, the expected-data generator, and two browser modules used 28.025 MHz/mT; the rest used 28.03 (g = 2.0028) | All use `adamas.nv.GAMMA_MHZ_PER_MT` (Python) or `GAMMA` in `web/assets/sim/action.js` (browser) [doherty2013] |
| Continuous integration | Failing since v0.28 on Python 3.10 (golden values compared exactly; numpy and scipy versions change the last digits); `docs/build` hidden by `.gitignore` | Golden values compared to 1e-9 relative; `docs/build` committed; passing on Python 3.10 and 3.12 |
| Equation in the loop | Five labs | Eleven labs, thirteen panels; the Break the Code panel is fitted to the lab's own threshold run |

## Fixed in v0.28.0 (were open in v0.27.0)

| Item | Was | Now |
|---|---|---|
| Copper's thermal conductivity (README, chapter 00) | Unsourced "5.5× copper" | 4.0 W/(cm·K) at 300 K from the NBS compilation [ho1972] |
| High-pressure (HPHT) plate size (chapter 02, audit table) | Unsourced | Sourced to a measured HPHT plate [stoupin2016] |
| Sub-diffraction addressing claims (chapter 07) | Some rows cited the wrong paper | Rows re-cited after reading each source; spot size from [born1999]; implantation conversion numbers corrected (21 % at 18 MeV, about 2 % simulated at 1 MeV) |
| Photon Lab contrast | The lab showed the pure-state contrast (0.445) | It shows the contrast from the pumped state (0.308), the number a measurement sees; both are labeled |
| Echo with a timing error | Only the ideal echo was modeled | `adamas.nv.echo_mistimed` and the Qubit Lab show how a mistimed π pulse lets static detuning back in |
| Addressing two NVs 15–30 nm apart (audit issue 3) | Text only | `adamas.addressing` plus the Addressing Lab: spot size, axis and gradient routes, crosstalk; tested |
| Gate bias (XZZX) | Stated in text | `adamas.gatebias` plus the Gate Bias Lab: Pauli propagation through CZ and H · CZ · H, checked against Stim |
| Equation in the loop (Phase 0 outline) | Proposed | Seven live panels in five labs, one Python registry (`adamas.loop`), browser arithmetic golden-tested |
| Desktop app dependency advisory | `npm audit` reported Electron advisories | Electron updated, `npm audit` reports 0 vulnerabilities |

## Deferred, with the reason

| Item | Why it waits | What closes it |
|---|---|---|
| Renaming experiment IDs in E29 | The roadmap IDs are cross-referenced in the README, E2, E8, the notebooks, and the decision analysis's keys. Renaming them breaks published links and saved course progress for no change in content. The two ID lists are explained in the chapter instead. | Nothing; kept by decision. |
| Tauri desktop shell with a Python engine | The Electron build is released (installers for Windows, macOS, and Linux built in CI), passes its per-page self-test in CI, and runs the same web code. A port is roadmap step 5 in [phase0/APP_ARCHITECTURE.md](phase0/APP_ARCHITECTURE.md). Porting before the content is complete would double the release work. | Port after the build program write-ups; keep Electron until Tauri passes the same self-test. |
| Machines and Facilities Atlas prices | Mostly closed in v0.40.0: [build/ATLAS.md](build/ATLAS.md) gives every machine a facility, an access mode and a price kind (sourced, estimate, included or unpriced with a reason); see "Open in v0.40.0" for what is left | Quotes or facility rates for the unpriced entries |
| GitHub Actions major versions (checkout, setup-node, setup-python, artifacts, pages) | GitHub warns that these target Node.js 20; it already runs them on Node.js 24, and every workflow passes. Newer majors exist (up to v7 and v8) and some change artifact behaviour, so each bump needs its release notes read and a test run. | Bump one workflow at a time and confirm the desktop release still uploads its installers. |
| Crossref verification of the newest references (part K) | Verification queries Crossref from the network; the build machine for releases cannot reach it. Metadata was checked by hand on publisher, arXiv, or institutional pages. | On a machine with internet, from the repository folder: `make verify MAILTO=you@example.com`, then `make apply-verify`. |

## Still assumptions (labeled as such wherever they appear)

| Assumption | Where | Why it is not measured |
|---|---|---|
| Bias of NV two-qubit gates (full bias on CZ, at most 5 on CNOT) | E6, `adamas.xzzx_native`, Gate Bias Lab | No published measurement of the Pauli bias of an NV-NV gate exists that we could find. The decision analysis shows the code choice is robust to it (value of information about 3 % of the machine). |
| Inter-cell photonic link parameters | `adamas.resource.LINK` | Proposed, not demonstrated at the needed rate; labeled proposed. |
| T₁ (longitudinal relaxation) in phase P2 | docs/build/P2_teaching_lab.md | The package has no T₁ model yet, so P2 has no T₁ pass/fail criterion; adding one needs a sourced phonon-limited T₁ at room temperature. |
| Density and specific heat of SiC and GaN in the Heat Race | `web/assets/sim/heat.js` | Textbook values not yet tied to a cited source; silicon and diamond are cited [haynes2016]. They change only the settling time, not the steady-state ratio, which depends on κ alone. |
| A1 kit filter prices (US$5 to 80) | EXPERIMENTS.md, `adamas.experiments` | Retail prices vary by vendor and month; given as a range, labeled an estimate. |
| Tier B and higher experiment totals | EXPERIMENTS.md | Labeled "a reviewer's estimate, not a vendor quote". |

## Tests that skip, and why

Every skip is environmental: the test needs a tool that is not installed. None skips because it fails.

| Skips without | Tests | Install on Ubuntu |
|---|---|---|
| Icarus Verilog | DIA-4 Verilog testbench, Verilog against the JavaScript emulator | `sudo apt install -y iverilog` |
| ngspice | Ring oscillator against the JavaScript transistor model | `sudo apt install -y ngspice` |
| Node.js or `web/node_modules` | Browser physics, equation-in-the-loop golden values, page smoke tests | `sudo apt install -y nodejs npm && cd web && npm ci` |
| Stim and PyMatching | Circuit-level error correction, XZZX, Pauli propagation check | `pip install stim pymatching` |
| ffmpeg | Rendering the trailer video | `sudo apt install -y ffmpeg` |
| nbclient and ipykernel | Executing the course notebooks | `pip install nbclient ipykernel` |

The preprint, talk, and poster need LaTeX: `sudo apt install -y texlive-latex-recommended texlive-latex-extra texlive-pictures latexmk`, then `make paper talk poster`.
