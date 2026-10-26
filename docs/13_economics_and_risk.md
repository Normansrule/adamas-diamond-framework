# 13 · Economics, risk, and the path to products

**Plain-language summary.** New semiconductor materials succeed by first winning a niche where nothing else works, then using that revenue to grow wafers and cut costs. Silicon carbide took about thirty years to go from 1-inch wafers to electric-car inverters. Diamond is near the start of the same curve.

## 13.1 The silicon carbide precedent

Silicon carbide wafers went from 25 mm in the early 1990s to 200 mm in the 2020s ([kimoto2014], `adamas.wafer.WAFER_HISTORY`). At each step the dominant products were small-die discretes, because yield falls exponentially with die area when defect density is high ([murphy1964], [stapper1983]; Figure 16 in [Chapter 2](02_wafer_manufacturing.md)). Diamond's 2026 status is 51 mm (2-inch) heteroepitaxial wafers in the peer-reviewed literature ([kim2021], [qu2024]), plus an industry announcement of a reproducible 76 mm process with 100 mm in development that is reported, not peer-reviewed [e6orbray2026]. By diameter alone this resembles silicon carbide around 1997 to 2001 or silicon around 1964 to 1972 (`adamas.wafer.WAFER_HISTORY`). By defect density diamond is far behind: wafer-scale heteroepitaxial material carries about 2×10⁷ dislocations per cm² ([stehl2013], [Chapter 2](02_wafer_manufacturing.md)).

## 13.2 Product sequence ADAMAS expects

| Horizon | Product | Why diamond wins | Die size | Evidence |
|---|---|---|---|---|
| Now | Heat spreaders, detectors, quantum sensors | Already commercial | n/a | [francis2010], [pernegger2005], [stuerner2021] |
| Near | Radiation-hard and high-temperature discretes and small circuits | Nothing else survives | ≤ 1 mm² | [ookuma2026], [kawarada2014] |
| Near | Few-qubit room-temperature quantum accelerators and quantum memories | No cryostat; edge deployment | ≤ 1 mm² diamond on CMOS | [olcf2025], [qbpawsey2023], [li2024] |
| Medium | Multi-kilovolt power switches | Figure of merit, cooling | 1 to 10 mm² | [saha2021], [donato2020], [umezawa2018] |
| Long | Monolithic complementary logic; clustered NV processors with error correction | Requires n-type and placement breakthroughs | > 10 mm² | [liao2024], [yao2012] |

## 13.3 Cost logic for quantum chiplets

A quantum chiplet needs very little diamond. A 1 mm² chiplet from a 51 mm (2-inch) wafer yields about 1,900 gross dies by `adamas.wafer.dies_per_wafer(51, 1.0)`; the announced 76 mm process would give about 4,400, if it delivers usable quality. Only the top few micrometers need quantum-grade ¹²C material ([Chapter 2](02_wafer_manufacturing.md)), so isotope cost per die is negligible. The dominant costs are characterization (every NV site must be mapped) and bonding. This is why detect-and-repair (experiment C-5) and electrical readout (C-6, F-1) are the economically decisive experiments: they convert a microscopy-limited craft into a wafer-probe-style test flow.

## 13.4 Risk register

| Risk | Likelihood | Impact | Mitigation | Sources |
|---|---|---|---|---|
| n-type doping stays impractical | High | Blocks monolithic complementary logic | Heterogeneous integration with silicon; p-only logic for interface roles | [kalish1999], [liao2024], [li2024] |
| NV placement yield stalls below 50 percent | Medium | Blocks direct-coupled arrays | Detect-and-repair; clusters plus bus; laser writing | [chen2019], [luhmann2019], [yao2012] |
| NV-NV gate fidelity stays below 0.99 at room temperature (gate G-2) | Medium | Limits processors to few-qubit cells | ¹²C material, optimal control, closer spacing, charge pre-selection; accept accelerator niche | [dolde2014], [joas2025], [herbschleb2019] |
| Wafer scaling stalls at 2 to 3 inch | Medium | Cost floor stays high | Small-die products remain viable | [schreck2017], [kim2021], [e6orbray2026] (reported) |
| Dislocations limit breakdown and coherence on heteroepitaxial wafers | **High** | Measured breakdown field falls from ≥ 7.7 MV/cm on small-area homoepitaxial diamond to about 1.1 to 1.5 MV/cm on wafer-scale heteroepitaxial material (about 10⁷ cm⁻²) ([volpe2010], [kwak2021], [weippert2022]); single-NV $T_2$ is about 5 µs on heteroepitaxial diamond [nelz2019]. Roadmap target F-3 is therefore restated as a $T_2$ distribution against etch-pit density | Thick buffer growth (density falls with thickness [stehl2013]), dislocation filtering, offcut substrates; small dies; homoepitaxial layers for qubits | [kim2021], [gaukroger2008], [friel2009], [stehl2013], [kwak2021], [weippert2022], [nelz2019] |
| Hole-gas surface instability | Low to medium | Reliability | ALD passivation, oxide acceptors, boron nitride gates | [kawarada2017], [crawford2021], [sasama2022] |
| Competing platforms (superconducting, trapped-ion, neutral-atom, silicon spin) reach fault tolerance first | High | Reduces the general-purpose computing case | Focus on what only room-temperature operation offers: embedded, mobile, and sensing-coupled processing | [preskill2018], [ladd2010], [kane1998] |
| Vendor claims outrun peer review | Present | Credibility of the field | This repository's evidence labels | [saxonq2026], [tqi2026] |

## 13.5 What would change this assessment

1. A shallow n-type dopant or stable n-type transfer doping in diamond.
2. Single-shot electron-spin readout at room temperature with fidelity above 90 percent.
3. A demonstrated room-temperature NV-NV link beyond 50 nm.
4. 150 mm single-crystal wafers with dislocation density below 10⁴ cm⁻².

Any one of these moves a row in [Chapter 12](12_silicon_vs_diamond_scorecard.md) and should trigger a revision of this framework.
