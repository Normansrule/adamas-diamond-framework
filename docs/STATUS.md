# What is skipped, deferred, or still an assumption, and why

This file lists everything in ADAMAS that is not finished, so nothing is skipped silently. Each item says whether it was fixed, why it waits, and what would close it. It is updated with every release; the audit's fix status is in [AUDIT.md §9](AUDIT.md#9-fix-status-in-v0270).

Last updated: v0.35.0 (2026-11-07).

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
| Photos | references/images.psv is empty: Wikimedia Commons could not be reached from the build container to check licenses | Check each candidate by hand and log it: S01 "Single-crystal CVD diamond disc"; S03 "CVD Reaction Chamber, GPN-2000-001466" (NASA; a CVD chamber, not a diamond reactor, and must be captioned so); S05 "JEOL Electron Beam Lithography (EBL)" (Flickr upload); S19 "TF78 60 – Wire bonding". Owner-made build photos for L0 (CC BY) are welcome |
| L3 control charts | No wafer has been measured; the page shows the traveler limits only, with no invented data | Log measured wafers |
| W7 placement yield | Uses illustrative inputs (5 nm spread per axis, 10 nm design spacing) with the sourced 1 % conversion [pezzagna2010] | Measured placement spread and conversion |
| W8 array gate | No sourced threshold for "good enough"; the page computes sites needed for a target the reader sets and gives no verdict | A decision in build phase P5 |
| Step times and costs for L2 and L3 | Not sourced, so not shown | Facility quotes |

## Open in v0.31.0: Quantum Device Library

The Quantum Device Library ([docs/devices/README.md](devices/README.md), `adamas/qdl.py`) lists 28 devices. What it does not have yet:

| Device | Item | Why it waits |
|---|---|---|
| QDL-07 | X07a p-i-n doped growth (boron and phosphorus layers) | Not in the process traveler (docs/process/TRAVELER.md) yet; the device page shows it as **missing** |
| QDL-09 | X09a Nanophotonic etch (nanopillars or waveguides) | Not in the process traveler (docs/process/TRAVELER.md) yet; the device page shows it as **missing** |
| QDL-10 | X10a Dark-spin chain placement | Not in the process traveler (docs/process/TRAVELER.md) yet; the device page shows it as **missing** |
| QDL-11 | X11a Nanophotonic etch (cavity) | Not in the process traveler (docs/process/TRAVELER.md) yet; the device page shows it as **missing** |
| QDL-13 | X13a Optomechanical resonator fabrication | Not in the process traveler (docs/process/TRAVELER.md) yet; the device page shows it as **missing** |
| QDL-14 | X14a Released diamond nanobeam | Not in the process traveler (docs/process/TRAVELER.md) yet; the device page shows it as **missing** |
| QDL-15 | X15a Ferromagnet strip deposition | Not in the process traveler (docs/process/TRAVELER.md) yet; the device page shows it as **missing** |
| QDL-17 | X17a Pillar tip etch and cantilever mount | Not in the process traveler (docs/process/TRAVELER.md) yet; the device page shows it as **missing** |
| QDL-20 | X20a Nanodiamond milling and surface treatment | Not in the process traveler (docs/process/TRAVELER.md) yet; the device page shows it as **missing** |
| QDL-25 | X25a Cavity assembly (sapphire or dielectric resonator) | Not in the process traveler (docs/process/TRAVELER.md) yet; the device page shows it as **missing** |
| QDL-27 | X27a CMOS die from a multi-project wafer (MPW) shuttle | Not in the process traveler (docs/process/TRAVELER.md) yet; the device page shows it as **missing** |
| QDL-02, 07, 09, 10, 13 to 16, 18, 22 to 26 | No simulated pass/fail check | The package has no model for these devices yet (nuclear decoupling, charge state, photonics, mechanics, NMR, maser, many-body); each page says which |
| All | Photos of build steps (Fab Journey, planned for v0.32.0) | Wikimedia Commons licenses could not be checked from the build container; diagrams only until each license is logged in references/images.psv with a test |
| QDL-05 | [dreau2013] metadata | Checked on arXiv (1210.6195); awaiting Crossref verification (`make verify`) |

Numbers that exist in the papers but are not yet confirmed from them (the device pages say "to confirm" instead of a value):

| Device | Figure of merit | To confirm |
|---|---|---|
| QDL-07 | NV⁻ fraction under readout | NV⁻ fraction under electrical control: confirm from the paper |
| QDL-09 | Collection gain over bulk | Photon-collection gain of diamond nanowires: confirm from the paper |
| QDL-12 | Sensitivity | Ensemble sensitivity records: confirm from the paper |
| QDL-17 | Spatial resolution | Tip spatial resolution: confirm from the paper |
| QDL-18 | Spectral resolution | Chemical-shift resolution: confirm from the paper |
| QDL-19 | Field sensitivity per pixel | Per-pixel sensitivity: confirm from the paper |
| QDL-21 | Sensitivity | Biomagnetic sensitivity: confirm from the paper |
| QDL-22 | Signal enhancement over thermal | Hyperpolarization enhancement: confirm from the paper |
| QDL-24 | Electric-field sensitivity | Electric-field sensitivity: confirm from the paper |

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
| Build program P5–P8 full write-ups and the Machines and Facilities Atlas (P0 to P4 are written) | Each of the roughly 60 Atlas entries needs a sourced price, facility need, and pass/fail criterion. Writing them without sources would break this project's rule that every number is sourced or computed. The outline is in [phase0/BUILD_PROGRAM_OUTLINE.md](phase0/BUILD_PROGRAM_OUTLINE.md). | One phase per release, each passing the same reference check. |
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
