# ADAMAS expert audit (Phase 0)

**Status: findings only. Nothing in the code or chapters has been changed. Fixes wait for review at the Phase 0 gate.**
Audited: branch `claude/v0.26.0` (v0.24 on `main` plus the unreleased v0.25 and v0.26), October 2026.

## How the audit was done

Five reviewer roles each checked every claim in their area for four things: physics (equations, units, validity limits), agreement with the cited source (re-read), practicality (machines, cost, yield), and internal consistency across the README, chapters, code and paper.

| Panel | Roles | Scope | IDs |
|---|---|---|---|
| Materials and devices | Chemical vapor deposition (CVD) grower; wide-bandgap device physicist | Chapters 01–05, 12, 13, E9; `materials`, `doping`, `power`, `converter`, `thermal`, `wafer`, `logic` | G1–G24 |
| Quantum optics | Nitrogen-vacancy (NV) experimentalist | Chapters 06–08, E5, experiments; `nv`, `photophysics`, `gate_budget`, `coupling`, `register`, `action` | Q1–Q27 |
| Error correction, fab, consistency | Error-correction theorist; fab process engineer; consistency checker | Chapters 09–11, E1, E2, E6, E10, E11, traveler, validation, paper; `qec`, `circuit_qec`, `xzzx_native`, `resource`, `scaling`, `traveler` | E1–E29 |
| Software | Code review of the unreleased v0.26 | Equations in Action, desktop app, service worker, `adamas app` | S1–S15 |

**Lead re-check.** Every critical finding was re-checked by hand: the code was rerun, or the primary source was re-read. Those rows are marked ✔. Sources were re-read from arXiv and publisher pages. Crossref, doi.org and PubMed Central were blocked in this environment. Rows that rely on memory or a summary page say so in the evidence. Labels follow the rigor rules: **demonstrated** (peer-reviewed), **reported** (industry, preprint or press release), **proposed here** (this repository's model or idea).

**Totals.** 80 findings: 8 critical, 33 major, 31 minor, and 8 checked correct. A further 15 code findings in the unreleased v0.26 are listed separately.

---

## 1. What changes the headline story

These eight critical findings change numbers that appear in the README key findings, the preprint abstract, or the build plan. Fixing them will regenerate those numbers. The v0.25 "what to measure next" analysis must be rerun after G6/G7 and E9, because it was computed on the flawed models.

| # | Claim today | What the audit found | Effect after the fix |
|---|---|---|---|
| **G6, G7** ✔ | "Diamond's EV-inverter (electric vehicle) loss advantage over silicon carbide (SiC) is a median 3.8×" | The model assumes every boron acceptor in the drift layer is ionized. At the 1.31×10¹⁷ cm⁻³ a 1200 V drift needs, the package's own solver gives **0.50 % ionized at 300 K** (21.7 % at 573 K). Resistance ∝ 1/f_ion and loss ∝ √R, so the ratio falls by about 14×. The temperature factor is also normalized to 300 K instead of to full ionization. | A bulk-doped diamond switch **loses to SiC by about 4× at 300 K** (ratio ≈ 0.27). It wins only when hot (150–300 °C junction) with good mobility, where it roughly matches ideal gallium nitride (GaN). Lateral hole-gas devices (Saha) avoid ionization and need their own model. |
| **G4** | All wafer-scale power claims use a 10 MV/cm critical field | The 10 MV/cm figure is theoretical. Small-area homoepitaxial diamond reaches about 7.7 MV/cm. Wafer-scale heteroepitaxial diamond (about 10⁷ dislocations per cm²) measures **1–2 MV/cm**, with leakage at threading dislocations [kwak2021, weippert2022, saha2021]. | The critical field, and so the Baliga figure of merit (BFOM), must depend on dislocation density. On today's heteroepitaxial wafers BFOM is about 10² × silicon, not 49,000×. |
| **G1** | "Reproducible 3-inch single-crystal diamond was reported in 2026" | The only source is a Semiconductor Today news item [e6orbray2026], with no substrate, dislocation density, X-ray rocking curve, yield or price. Peer-reviewed record: one 92 mm plate (2017) [schreck2017], and 2-inch wafers at about 2×10⁷ cm⁻² [kim2021, qu2024]. | Relabel as an industry claim, keep the source, and drop it as support for cost or quality. |
| **E1** ✔ | RSA-2048 at 1 ms readout: "about a year" (README E10 row, E10.2) versus "6.0 years" (key findings, E10.5, paper) | Two different models, each arithmetically right (section 2). | One statement naming both models. |
| **E22** | Traveler step S08: hydrogen plasma at 600–800 °C, after the NV centers are created | Hydrogen plasma at 700–1000 °C passivates NV centers into non-luminescent NVH deep into the crystal, and annealing does not restore them [stacey2012] (only the arXiv version was read). The qubit variant of the flow would erase its own qubits. | Hard-mask the qubit windows during S08, or move hydrogen termination before implantation, or use low-temperature atomic hydrogen. Add an automated thermal-budget rule. |
| **Q1** ✔ | "The measured 0.67 means the NV⁻ charge state was ready only 0.75 of the time: preparation, not coherence, is the bottleneck" | Dolde 2013's supplement says the tomography was "normalize[d] … to a charge state preselected scheme" and that "a NV initialization close to unity is assumed" (re-read, arXiv 1212.2804). Charge state was normalized out, so it cannot explain the 0.67. Dolde 2014 names coherence time and imperfect initialization. | Withdraw the headline. The validation row becomes a known discrepancy (18/19 → 17/19). The two-qubit gate budget needs a real error model (Q2, Q3). |
| **Q4** | "Qubits must sit within about 15 to 30 nm" (README §5, chapters 7, 8) | A diffraction-limited spot is about 250 nm, so both NVs sit in one spot. Every room-temperature pair so far was addressed **spectrally** (different crystal orientations, lines about 30 MHz apart) and read out jointly. Chapter 7 even recommends aligning all NVs, which removes that route (Q5). | Add the addressing problem and the solution table (section 2) to §5, chapter 7 and chapter 8. |

The reviewers also flag two major findings that weaken v0.24–v0.25 results:
- **E9:** the XZZX threshold of 1.59 % and the 67 M-qubit machine assume bias-preserving CNOT gates, which two-level spins cannot have. The robust XZZX advantage is idle and readout dephasing.
- **E5:** the machine's die area assumes a 1 µm cell pitch while its gates assume 25 nm, so no link between cells is defined.

---

## 2. The three known issues, resolved

### 2a. RSA-2048 runtime (E1, E2, E4) ✔

| Model | Where | Assumptions | Result at 1 ms |
|---|---|---|---|
| Scaled 2021 layout (`adamas.scaling`) | README:473, E10.2 | Gidney and Ekerå's published 8 h (20 M qubits, distance 27, 10⁻³ gate error, 1 µs cycle, 10 µs reaction time) scaled linearly by cycle time; assumes the reaction time scales too | **≈ 0.9 years** |
| Circuit-level (`adamas.resource`) | Key findings, E10.5, paper | 6,000 logical qubits; 3×10⁹ logical steps run in series at d rounds each; Λ = 3.56 fitted at d ≤ 7 with a 0.3 % link error (not demonstrated); 1,105 µs round | **6.0 years**, distance 57, 78 M qubits |
| Circuit-level, calibrated so it reproduces the published 8 h at the published parameters | proposed | Effective step count about 1.07×10⁹ instead of 3×10⁹ | **≈ 2.1 years**, distance 55, 73 M qubits |

The 6.57× gap between the first two rows comes from three factors: distance (2.11×), round length (1.105×), and the serial schedule (2.81×). The 3×10⁹ figure is a Toffoli-gate count used as a serial step count. At the paper's own parameters, that overstates the published runtime 3.2×.

**Proposed single statement:** "At 1 ms NV readout an RSA-2048 job takes roughly 1 to 6 years: about 1 year by scaling the published 2021 estimate to the slower cycle, and 6 years from this repository's circuit-level model (about 2 years when calibrated to the published schedule). Area and power are not the limits; readout speed and link fidelity are." Also state the uncertainty as a median of 3.6 years (P10–P90: 1.2–15.5 years) instead of hanging the range on the 6.0-year baseline (E19).

### 2b. Wafers: industry claim versus peer-reviewed, and what dislocations do (G1–G5)

| Material class | Largest | Dislocation density (cm⁻²) | Measured breakdown | NV coherence | Label |
|---|---|---|---|---|---|
| High-pressure high-temperature (HPHT) plate | about 10–15 mm (unsourced) | about 10¹–10³ | — | Low-strain plates: T₂* ≈ 1.3 µs (strain plus charge, ensemble) [blinder2024] | demonstrated |
| CVD on HPHT (homoepitaxial) | about 10 mm; mosaics larger, with tile boundaries | about 10²–10⁵ [sumiya2012, friel2009] | ≥ 7.7 MV/cm, small area [volpe2010] | T₂ up to 1.8–2.4 ms in ¹²C-enriched layers [balasubramanian2009, herbschleb2019] | demonstrated |
| Heteroepitaxial on Ir/YSZ/Si or sapphire | 92 mm one-off plate [schreck2017]; 2-inch wafers [kim2021, qu2024] | ≈ 2×10⁷ at the growth surface; 10⁷–10⁹ in thin layers [stehl2013] | 1.1–2 MV/cm [kwak2021, weippert2022, saha2021] | Single NV T₂ = 5 µs [nelz2019]; T₂ 98–539 µs over laterally overgrown regions [oshnik2025, preprint] | demonstrated / reported |
| "Reproducible 3-inch", 2026 | 76 mm | not reported | not reported | not reported | **reported (industry)** |

**Proposed models.** All fitted forms are labeled proposed here.
- *Breakdown:* E_BR ≈ 7.7 − 2.1·log₁₀(D/10⁴) MV/cm for 10⁴ ≤ D ≤ 10⁷ cm⁻². This is a fit to the points above. Add a killer-defect survival factor exp(−A·f_k·D), where f_k, the fraction of dislocations that kill a device, is a measured unknown.
- *Coherence:* static strain ε ≈ b/(2πr) at mean dislocation distance r = 1/(2√D), with Burgers vector b = 0.252 nm and spin-strain coupling ≈ 10.9 GHz per unit strain [marshall2022]. Ensemble T₂* ≈ 1.2 µs at D = 10⁷, 37 µs at 10⁴, and 0.12 ms at 10³. The echo removes static strain, so T₂ is set by noise along the dislocations. This reproduces the measured order of magnitude.
- *Consequence:* the roadmap target F-3, "wafer-mapped T₂ > 1 ms on a 2- to 3-inch heteroepitaxial wafer", is unsupported today. The best heteroepitaxial T₂ is about 0.5 ms (preprint).

### 2c. Addressing NVs 15–30 nm apart (Q4, Q5, Q8, Q9)

| Method | Best result | Individual coherent control at < 30 nm, room temperature? |
|---|---|---|
| Spectral: different NV orientations, joint readout in one spot | 9.8 nm, coherent coupling [neumann2010natphys]; 25 nm, F = 0.67 [dolde2013]; F = 0.824 [dolde2014]; **9.5 nm, two-qubit fidelity 96.0 ± 2.5 % with 594 nm charge pre-selection** [joas2025] | **Yes: the only route demonstrated** |
| Spectral: optical zero-phonon line and strain | 3 NVs in one sub-diffraction cluster, crosstalk < 4 %, at 4 K [bersin2019] | Single-qubit only, cryogenic |
| Magnetic-field gradient | 1 G/nm, separate Rabi drive on NVs 135 nm apart [grinolds2011]; 0.11 G/nm microcoil, 96 nm, 97 % selectivity [zhang2017addr] | Not yet. 0.1 G/nm gives about 4 MHz at 15 nm, but readout is still joint |
| Sub-diffraction optics (STED, spin-RESOLFT, charge-state depletion, STORM) | Imaging to about 4–6 nm; spin control of NVs 100–150 nm apart [rittweger2009, maurer2010, chen2015csd, pfender2014] | Imaging yes; control at < 30 nm no |
| Dark-spin chain bus | Theory: chain spins 16–20 nm apart, 5–20 per link; assumes NV T₁ of 100–250 ms, about 250 K cooling, a donut readout beam and a field gradient [yao2012] | No (proposed) |
| Photoelectric readout | Single NV [siyushev2019], still focused light; NN-unmixed pair readout at about 10 nm [joliffe2024, preprint] | No |

Text to add to README §5: "At 15–30 nm both NVs sit inside one laser spot (about 250 nm), so they cannot be addressed or read out optically one by one. Every room-temperature demonstration so far tells them apart spectrally, using NVs on different crystal axes whose lines sit about 30 MHz apart, and reads them out together [dolde2013], [joas2025]. Field gradients, sub-diffraction optics, and the dark-spin bus of Chapter 8 are the proposed routes to larger arrays."

---

## 3. All findings, by severity

Columns: **Claim** (short) · **Where** · **Verdict** (correct, needs qualification, wrong, unsupported) · **Evidence** · **Fix** · **Label**.

### Critical (8)

| ID | Claim | Where | Verdict | Evidence | Fix | Label |
|---|---|---|---|---|---|---|
| G6 ✔ | EV inverter loss advantage over SiC: median 3.8× (2.5–5.5×) | README:33,297; uncertainty.py:40-46; VALIDATION.md | wrong | Assumes full ionization; drift f_ion = 0.50 % at 300 K (code). Corrected ratio ≈ 0.27 (P10–P90 0.18–0.39) | Divide R_on by f_ion(T,N); add junction temperature as an input; report 300 K and 573 K; mobility μ(N_A) | proposed here |
| G7 | `ron_temperature_factor` divides by f_ion(T)/f_ion(300 K); E9.2 table | converter.py:37-44; E9:27-52 | wrong | Gives below-ideal R_on when hot (implies over 100 % ionization). Correct form: R_ideal·(T/300)^m / f_ion(T). Per switch (800 V, 300 A, 20 kHz, μ = 3800): 54 W at 300 K, 20 W at 573 K; ideal SiC is 30 W at 300 K; ideal GaN is 21 W | Fix the formula; replace the 3.8 W row | proposed here |
| G4 | 10 MV/cm used for wafer-scale material; dislocation risk "Medium" | materials.py:39; uncertainty.py:25; ch13:31 | wrong | Heteroepitaxial: 1.1–2 MV/cm measured [kwak2021, weippert2022, saha2021]; leakage hot spots [alvarez2014] | E_BR(D) and killer-defect survival; risk to High | demonstrated / proposed |
| G1 | "Reproducible 3-inch single-crystal wafer (2026)" | README:386; ch00:43; ch02:46,66; ch10:11; ch11:61; ch12:11,64; ch13:7,30; paper:21; wafer.py; materials.py; traveler.py | unsupported as peer-reviewed | News item only; no quality data | Section 2b wording; tag reported; stop using it for cost (ch12:64) or quality (F-3) | reported |
| E1 ✔ | RSA-2048 "about a year" vs "6.0 years" | README:473 vs README:37; E10:28 vs E10:80; paper | needs qualification | Two models (section 2a) | Single statement naming both | proposed here |
| E22 | Hydrogen plasma 600–800 °C (S08) after NV creation (S06–S07) | TRAVELER:225; traveler.py:241 | wrong | Hydrogen passivates NV centers deep into the crystal at 700–1000 °C [stacey2012] (arXiv read; volume and page from memory) | Mask qubit windows or reorder; add a rule to `thermal_violations()` | reported (physics) / proposed (fix) |
| Q1 ✔ | 0.67 = charge state ready 0.75 of the time; preparation is the bottleneck | README:35; paper:17,41; E5:54,72; action.py; experiments.py; validation.py:46-51 | wrong | Dolde 2013 normalized the data to charge-preselected and assumed near-unity initialization (re-read) | Withdraw; validation row → known discrepancy | demonstrated (source) |
| Q4 | Qubits within 15–30 nm, with no word on addressing | README:416; ch07:3; ch08 §8.3 | needs qualification | Section 2c | Add the paragraph and table | demonstrated / proposed |

### Major (33)

| ID | Claim | Where | Verdict | Evidence | Fix | Label |
|---|---|---|---|---|---|---|
| G2 | Wafer history 92 → 51 → 76 mm; "production 50–76 mm" | wafer.py:16-19; materials.py:39; ch02:66; ch12:11 | needs qualification | Mixes a one-off plate, a pilot and an announcement | Two series ("peer-reviewed largest", "announced") with labels | demonstrated / reported |
| G3 | Heteroepitaxial dislocations "10⁶–10⁸"; scorecard "10³ to 10⁷" | ch02:46,67; ch12:12 | needs qualification | Wafer-scale ≈ 2×10⁷; 10⁶ only locally; density falls with thickness [stehl2013] | `dislocation_cm2` per substrate class | demonstrated |
| G5 | F-3 "wafer-mapped T₂ > 1 ms" on heteroepitaxial | ch11:61; ch13:31 | unsupported | Section 2b | Strain model in `adamas.nv`; restate F-3 as a T₂ distribution versus etch-pit density | demonstrated / proposed |
| G8 | Hole mobility 3800 cm²/V·s baseline | ch01:14; materials.py:39; uncertainty.py:26 | needs qualification | Time-of-flight record never reproduced [isberg2002]; ab initio ≈ 1970 [sanders2021]; Hall ≈ 1870 [volpe2009]; falls with doping [pernot2010] | Baseline ≈ 2000; μ(N_A) in drift layers; label 3800 a record | demonstrated |
| G9 | Critical field "10 MV/cm, 33× silicon"; "10–20 kV single dies plausible" | README:97,121; ch01:12; E9:60 | needs qualification | Theoretical; measured ≥ 7.7 (homoepitaxial), 1–2 (heteroepitaxial) | State all three | demonstrated |
| G10 | BFOM "48,976×" silicon | README:33,180,365; ch01:48; paper:21 | needs qualification | Arithmetic right but compares diamond holes with silicon electrons; 5-digit false precision. 7.7 MV/cm and μ 2000 give about 12,000×; heteroepitaxial gives about 165× | Report a range and the carriers compared | proposed here |
| G11 | "Under 1 % of boron ionized at 300 K" | README:123,180,380; ch01:64; paper:21 | needs qualification | 0.57 % at 10¹⁷ but 1.6 % at 10¹⁶, about 5 % at 10¹⁵; compensation lowers it | State the doping range; nonzero compensation by default | demonstrated |
| G14 | 2608 / 3659 V; "beats silicon's limit by about 90×" | README:370; ch04:13-19; power.py; paper:28 | correct arithmetic, needs qualification | [saha2021] and [saha2022] confirmed; 3659 V on-resistance not verified (IEEE blocked). Lateral devices compared with vertical one-dimensional limits; silicon at fixed 0.3 MV/cm | Note lateral versus vertical; flag the derived value | demonstrated |
| G15 | "A vertical diamond MOSFET at even 1 % of the ideal limit would match GaN"; W-5 "1 mΩ·cm² (1 % of ideal)" | E9:55,75,87 | wrong | Loss ∝ √R: at 100× ideal it is 38 W versus 21 W for GaN; matching GaN needs ≤ 30× ideal; 1 mΩ·cm² at 3 kV is 1.9 % of ideal | Correct; state the junction temperature | proposed here |
| G16 | "Diamond 400 °C demonstrated" used as the converter ceiling; 400 °C logic | converter.py:18-19,30; E9:33,59; ch12:24; README:439-440 | needs qualification | One hydrogen-terminated FET, short-term [kawarada2014]; no diamond logic shown at 400 °C in the cited set | "400 °C, single device, short-term"; "high-temperature logic: not demonstrated" | demonstrated / proposed |
| E2 | Workload "6,000 logical, 3×10⁹ steps" | resource.py:27; paper:53 | needs qualification | 3×10⁹ is a Toffoli count, not serial steps; overstates the published runtime 3.2× | Label as upper bound or calibrate | proposed here |
| E4 | Superconducting "8 hours" (E10.1) versus "4 days" (E10.5b) | E10:11 vs 78-81 | needs qualification | 4 days uses today's measured Λ = 2.14 [google2025]: distance 95, 217 M qubits; 8 h assumes Λ ≈ 10 | Label the columns | demonstrated / proposed |
| E5 | Die "5.7 mm" at 1 µm pitch while every CNOT is a 25 µs dipolar link | E10:34,53; resource.py:136; E1:72-74; ch09 §9.3 | wrong (internally) | Coupling at 1 µm is about 0.05 Hz; four different pitches used | Name the inter-cell link (bus or photonic) with its time and error, or price a 25 nm pitch with spectral addressing | proposed here |
| E6 | Reference machine "5×10⁶ cells, 2×10⁷ qubits" | E10:59 | needs qualification | From the 2021 layout; the same chapter's model needs 67–142 M | Resize or label | proposed here |
| E7 | Requirement "link error below 1.3 %" | E10:63; README:469; E6:56 | needs qualification | 1.3 % is phenomenological break-even; circuit-level threshold ≈ 1 %; the machine assumes 0.3 %; best NV–NV is 4 % error [joas2025] | "≤ 0.3 % (as assumed); threshold ≈ 1 %" | proposed here |
| E8 | Gate G-2 "NV–NV fidelity > 0.95" | ch11:90 | wrong (too lax) | 5 % error is about 5× above threshold | G-2 ≥ 0.99, target 0.997 | proposed here |
| E9 | XZZX threshold 1.59 % versus 0.63 % at bias 100 | README:36; E6:106-107; paper:46; poster:38 | needs qualification | Repository's own numbers. Bias on CX/XCX needs bias-preserving CNOTs, impossible for two-level qubits [guillaud2019, puri2020]; two-level circuit-level study: 0.66–1.27 % [etxezarreta2025, preprint] | Call it an upper bound; rerun with bias only on CZ and η ≈ 5 on CX; keep the idle-dephasing result | proposed here |
| E10 | "399 M versus 67 M"; "about six times as many qubits" | README:37,285; E10:97-103 | needs qualification | Compares across noise models; same model gives 165 → 399 M (2.4×) and 142 → 67 M; 399/78 = 5.1 | Within-model ratios | proposed here |
| E23 | "Six-mask PDK-0" | README:465; E2:9-17,116; ch11:44; TRAVELER | wrong (inconsistent) | Traveler has 5 masks and no enhancement (ENH) step; the E/D logic variant needs it | Add ENH (partial channel oxidation [kitabayashi2017]); one mask count | proposed here |
| Q2 | "Coherence would allow 0.998" | README:35; E5:67-72; gate_budget.py | needs qualification | Assumes one gate with an e^-(t/T₂)³ envelope; Dolde applies two gates and names dephasing; p = 1 gives about 0.83–0.90; T₁ = 1.12 ms ignored | Range over p = 1–3, two gates, include T₁ | proposed here |
| Q3 | q = charge state × spin polarization | E5:36; paper:41 | wrong (internally) | With the package's own 82 % polarization, q ≈ 0.59, so F ≈ 0.55 < 0.67 | Redefine or remove | proposed here |
| Q5 | (111) alignment "removes a four-fold loss in addressability" | ch07:40; nv.py:22 | needs qualification | Every room-temperature pair relied on different orientations | State the trade-off: alignment helps sensing, hurts close pairs | demonstrated |
| Q6 | "Best room-temperature NV–NV fidelity is 0.82"; "below 15 nm for 99 %" | ch08:69 | wrong (outdated) | 96.0 ± 2.5 % at 9.5 nm [joas2025, already in references] | Update; reconcile with E5.1b | demonstrated |
| Q7 | C-8 "nuclear–nuclear entanglement across two NVs at 300 K", not yet reported | README:441; ch11:51,53 | wrong label | Dolde 2014 transferred entanglement to two nuclear spins about 25 nm apart | Relabel; keep the new parts (direct Bell tomography, ¹⁴N memories) as proposed | demonstrated |
| Q8 | Dark-spin bus "room (proposed)" | ch08:49,56 | needs qualification | Yao's assumptions (T₁ 100–250 ms, about 250 K, donut beam, gradient) | List them | proposed (theory) |
| Q9 | Photoelectric readout "needs no objective lens"; default interface | ch08:65; F-1 | needs qualification | Single-NV PDMR uses focused two-photon ionization, so it is still diffraction limited | Say so | demonstrated / proposed |
| Q18 | Contrast "about 30 %" versus model 45 % | README:126,182; ch06:38; photophysics.py; VALIDATION | inconsistent | From the model's own 82 % polarization the contrast is ≈ 0.31, matching the literature | Compute contrast from the polarized state | proposed here |
| Q23 | D1 teaches "why charge-state preparation limits fidelity"; "0.67 at q ≈ 0.75" | experiments.py:168-176; EXPERIMENTS.md:264,282 | unsupported | No addressing or readout plan for two NVs in one spot | Add a plan (different orientations, joint readout, 594 nm pre-selection); state the charge idea as a hypothesis | proposed here |
| E16 | Circuit threshold "about 1.2 %" next to "falls from 0.95 %" | E6:70; paper:46 | needs qualification | Two noise models; published matching-decoder values 0.57–1 % | State both; add a published circuit-level validation row | proposed here |
| E19 | "6.0 years (1.2 to 15.5)" | README:37 | needs qualification | Median 3.6 years; 1 ms sits at about P65 | Quote the median | proposed here |
| E20 | Baseline ratio 6.7× versus 7.8× versus "8×" | VALIDATION:33; paper:17,63; README:470 | inconsistent | √(R·C) metric versus the inverter model | Name the metric each time (superseded by G6) | proposed here |
| G19 | SiC field 2.5 (materials) versus 3.0 (uncertainty) | materials.py:33; uncertainty.py:28 | inconsistent | Two parameter sources | One source | proposed here |
| E29 | Experiment IDs collide (B3, C1, C2, D1 versus B-3, C-1, C-2); "gates above the fault-tolerance threshold" | E10; ch11; README:441 | needs qualification | Two ID sets; rong2015 is electron–nuclear | Separate prefixes; reword | demonstrated |

### Minor (31)

| ID | Claim | Where | Fix |
|---|---|---|---|
| G12 | Boron 0.37 eV; metallic above 3×10²⁰ | ch01:64,73 | N-dependent E_A; quote ≈ 4.5×10²⁰ [klein2007] |
| G13 | κ = 22, "5× copper" | ch01:78; README:122 | 5.5×; add κ(T); note the uniform-flux hot spot is 1.27× higher |
| G17 | First n-channel MOSFET 2024 | README:180,440; ch04:34 | "first, per the authors; phosphorus-doped channel; mobility at 300 °C" |
| G18 | p-channel on n-type body, 2024 [zhao2024] | ch04:35; ch05:14 | State what is new versus [matsumoto2016] |
| G20 | "Boron implantation is poor" | ch03:95; ch12:14 | "Immature" (1651 V implanted diode [saha2023sbd]) |
| G21 | "Like SiC around 2001 or silicon around 1972" | ch13:7; README:386 | "By diameter; far behind by defect density" |
| G22 | Lateral R_on scaled as BV²; vertical C_oss for a lateral device | converter.py:73-74; E9:53 | Fixed contact term; note the approximation |
| G24 | HPHT plates "up to roughly 10 mm"; mosaic "2 inch" | ch02:30,45 | Mosaic is not single-crystal; source the HPHT size |
| E3 | "20 million, 8 hours at 1 µs" | E10:11; scaling.py:4 | Note the reaction-time assumption |
| E11 | "E10 still uses the standard code, so it is conservative" | E6:113 | Stale; point to E10.5c/d |
| E12 | p_L ≈ 0.1(p/p_th)^((d+1)/2) attributed to [fowler2012] | E6:19; qec.py; README:129 | Fowler 2012 is 0.03(p/0.57 %)^d_e; cite the rule-of-thumb source |
| E13 | 2d² − 1 qubits [fowler2012] | E6:13; qec.py | Cite a rotated-layout source |
| E14 ✔ | Distance table d = 17 and 23 | E6:25-26; qec.py | Floating-point boundary (0.1·0.1⁸ = 1.0000000000000005e-9): exact answers d = 15 and 21 |
| E15 | 3.1 % versus 2.93 % [wang2003] | E6:41; VALIDATION; paper | Add "matching-decoder value" (correct otherwise) |
| E17 | Readout "below a tenth of T₂" versus "below about 1 %" | paper:17 vs E6:73-75 | State both criteria |
| E18 | Λ 4.03 / 3.56 / 2.64 | numbers.tex; paper:46 | "Extrapolated from d ≤ 7" |
| E21 | "< 1 % of one 76 mm wafer" | E10:38 | "< 2 %" at 10 % yield |
| E24 | 0.1–1 µm RF gaps by wet gold etch | TRAVELER:301 | E-beam lift-off or ion milling below 1 µm |
| E25 | Tri-acid clean | TRAVELER:61-72 | Add: never boil to dryness (anhydrous perchloric acid is explosive); no organics on the bench |
| E26 | ¹⁵N 2.5–10 keV; anneal; ALD option B "about 2 kV" | TRAVELER S06, S07, S13 | Verify the 2 kV value in kawarada2017 |
| E27 | High-NA "26 × 33 mm field" | E1:43 | High-NA EUV uses a 26 × 16.5 mm half field |
| E28 | "52 figures" | ch11:18; DEVELOPMENT_UBUNTU:48; E8:14 | 53; generate from the figure list |
| Q10 | neumann2010natphys listed as "two NVs entangled" | ch08:48 | Coherent coupling only |
| Q12 | Pair yield 10⁻⁴; "20 nm apertures" | ch07:30-31,69; experiments.py:173 | Demonstrated pairs used MeV ions (Neumann 21 %; Dolde about 2 %) |
| Q15 | A∥(¹⁴N) = −2.16, P = −4.95 MHz [felton2009] | ch06:21-22; nv.py:15 | Felton gives −2.147 and −5.016; re-cite or change |
| Q16 | T₂ 1.8 / 2.4 ms | ch06:58-62 | Add the T₂* ≈ 1.5 ms record [herbschleb2019] |
| Q21 | "Tens of thousands of gate operations" | README:410; ch08:13 | True for electron–nuclear; NV–NV gives T₂/t_g of about 10–400 |
| Q22 | Ω = A/√3 selective pulse, 0.99999 | ch08:38; register.py | ¹⁴N (I = 1): a third line leaves ≈ 2.7 % excitation |
| Q24 | A1: < 1 mW 532 nm module, red filter foil | experiments.py:33-41 | Add infrared-block and shortpass filters; check power with a meter |
| Q25 | B1 US$3,000–10,000 | experiments.py:86 | Re-source; likely US$5–12k (reviewer's estimate) |
| Q27 | "mₛ = 0 is about 30 % brighter" | README:126; action.py:36 | "±1 is about 30 % dimmer" |
| G23, Q11, Q13, Q14, Q17, Q19, Q20, Q26 | — | — | Checked correct (section 4) |

---

## 4. Checked and correct

- **NV constants:** D = 2870 MHz, dD/dT = −74.2 kHz/K, γₑ = 28.03 GHz/T [doherty2013, acosta2010].
- **Dipolar coupling:** 52 MHz·nm³/r³; [joas2025]'s 119.8 kHz at ≤ 9.54 nm matches 2 × 52/r³.
- **Stored Dolde 2013 pair parameters:** 25 ± 2 nm, 4.93 kHz, T₂ 150/514 µs, F = 0.67 ± 0.04, and 0.824 in 2014.
- **Charge state:** NV⁻ fraction 70–75 % under green light [aslam2013].
- **Room-temperature results:** error correction [waldherr2014]; gates 99.995 % and 99.2 % [rong2015]; T₂ of 1.8 ms and 2.4 ms.
- **Saha devices:** 2608 V / 19.74 mΩ·cm² and 2568 V / 7.54 mΩ·cm² [saha2021, saha2022].
- **Literature anchors:** Gidney–Ekerå assumptions; Google 2025 Λ = 2.14 ± 0.02, 1.1 µs, 0.143 % per cycle; Wang 2003 2.93 %.
- **Lithography:** every number in E1 recomputed exactly.
- **Logic:** E/D inverter current about 1 mA.
- **Reproducibility:** every runtime, die size and Λ reproduces from the code. TRAVELER.md is byte-identical to its generator, and all 127 tests collect.

## 5. Strongest and weakest links

**Strongest**
1. **Reproducibility.** Every number the audit recomputed matches the code, and the generated documents match their generators.
2. **Single-qubit physics.** NV constants, coherence records, and room-temperature error correction are accurate and well cited.
3. **Honest framing in many places.** Chapter 7's pair-yield bound, "no single-shot electron readout at 300 K", and the 0.3 % versus 0.82 gap stated openly.
4. **Device arithmetic.** Baliga limits, Saha's figures, and the ionization solver are correct.

**Weakest**
1. **The power headline (G6, G7, G4).** It leaves out the material's own deep-dopant physics and treats heteroepitaxial wafers as if they were HPHT-grade. Diamond's real case is hot operation and lateral hole-gas devices, not a 300 K bulk-doped switch.
2. **The two-qubit gate story (Q1–Q3, Q6).** The "preparation is the bottleneck" headline contradicts its source, and the state of the art is two years out of date.
3. **The machine has no defined link between cells (E5–E8).** Geometry, link error and decision gates do not agree with each other or with demonstrated fidelities.
4. **Addressing (Q4, Q5).** It is missing everywhere, and one recommendation removes the only working route.
5. **The qubit fab variant cannot be built as written (E22, E23).**

## 6. Proposed fix plan (after your approval)

| Batch | Contents | Regenerates |
|---|---|---|
| **F1 Physics models** | G6/G7 ionization-aware R_on(T); μ(N_A); E_BR(D) and killer-defect survival; strain-limited T₂*(D); compensation default; E14 tolerance; Q18 contrast from the polarized state; gate budget with p = 1–3, two gates, T₁ (Q2, Q3) | Power Lab, Equations in Action, uncertainty, Sobol, validation, figures 28–30 and 49–52, numbers.tex |
| **F2 Machine model** | E1/E2 calibrated schedule; E5 explicit link and pitch; E9 bias only on CZ, η ≈ 5 on CX; within-model ratios (E10); G-2 ≥ 0.99 | Resource tables (about 6 min), figures 33, 50–52, Machine Builder, E10 |
| **F3 Text and labels** | G1–G3, G8–G11, G14–G17, Q1, Q4–Q10, Q15–Q16, Q21–Q27, E3–E4, E6–E8, E11–E13, E15–E21, E27–E29; demonstrated, reported and proposed labels; README §5 addressing; one runtime statement | README, chapters, paper, talk, poster |
| **F4 Process** | E22 hydrogen-plasma rule and step order; E23 ENH step and one mask count; E24–E26 | Traveler, process page, PDK-0 |
| **F5 v0.26 software** | S1–S15 (below) | Site, desktop app |
| **F6 References** | About 40 new entries (status K) from this audit; run `make verify` | Bibliography |

Each batch ends with tests, `adamas build docs`, `make figures site`, and a gate summary.

---

## 7. Unreleased v0.26 code review (S1–S15)

| ID | Severity | Finding | Fix |
|---|---|---|---|
| S1 | medium | Echo scene says "300× longer than T₂*", should be 1200× (`action_scenes.js:301`) | `S.t2 / 0.5` |
| S2 | medium | Plugged-in numbers can go stale after a fast drag (90 ms throttle without a trailing update) | Trailing update |
| S3 | medium | Play/Tour resets the yield and g2 scenes every frame (the auto variable is in their reset key) | Leave it out of the key, or pick another auto variable |
| S4 | medium | `adamas app` can fail and leave `site/` empty when only some web libraries are installed | Check every vendor source, or fall back to online |
| S5 | medium | `adamas app --out DIR` can delete a non-site folder | Refuse a non-empty folder without a marker |
| S6 | medium | The service worker serves new HTML with old cached scripts after a deploy | Network-first for same-origin scripts and styles, or hashed file names |
| S7 | low | Arrhenius scene: N_D > N_A shows 4×10⁴⁵ Ω·cm | Clamp, or label it n-type |
| S8 | low | Surface scene: p_L > 1 at p = 2 % and d = 25 | Clamp and label as saturated |
| S9 | low | Murphy yield loses precision at tiny A·D₀ (JavaScript and Python) | `-expm1(-x)/x` |
| S10 | low | "cos 90° = 1.8×10⁻¹⁶ mT" | Round to 0 |
| S11 | low | Markers and curves leave three charts (heat, dipole, FET) | Fit the axes |
| S12 | low | Desktop window icon not packaged | Add it to `files` |
| S13 | low | Download page picks arm64 for Intel Macs and offers the AppImage to Android | Detect better |
| S14 | low | Desktop pull-request check misses changes under `adamas/` | Widen the path filter |
| S15 | low | `adamas app` request logging; Electron permission requests not denied | Subclass the handler; `setPermissionRequestHandler` deny |

Checked sound: the `app://` path-traversal guard, sandbox and context isolation, the Content-Security-Policy, the CI artifact layout, and the 14 scenes at every slider extreme (no exceptions, no NaN).

## 8. Sources the reviewers could not open

IEEE Xplore (the [saha2023] abstract), HAL ([volpe2010]), nature.com full text ([schreck2017]), PubMed Central, Crossref, and doi.org. Values taken from memory or summary pages are marked in the reviewer notes and must be checked before they ship (rule: never invent).
