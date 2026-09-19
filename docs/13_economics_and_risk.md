# 13 · Economics, risk, and the path to products

**Plain-language summary.** New semiconductor materials succeed by first winning a niche where nothing else works, then using that revenue to grow wafers and cut costs. Silicon carbide took about thirty years to go from 1-inch wafers to electric-car inverters. Diamond is near the start of the same curve.

## 13.1 The silicon carbide precedent

Silicon carbide wafers went from 25 mm in the early 1990s to 200 mm in the 2020s ([kimoto2014], `adamas.wafer.WAFER_HISTORY`). At each step the dominant products were small-die discretes, because yield falls exponentially with die area when defect density is high ([murphy1964], [stapper1983]; Figure 16 in [Chapter 2](02_wafer_manufacturing.md)). Diamond's 2026 status, reproducible 76 mm wafers with 100 mm in development [e6orbray2026], corresponds to silicon carbide around 2001 or silicon around 1972.

## 13.2 Product sequence ADAMAS expects

| Horizon | Product | Why diamond wins | Die size | Evidence |
|---|---|---|---|---|
| Now | Heat spreaders, detectors, quantum sensors | Already commercial | n/a | [francis2010], [pernegger2005], [stuerner2021] |
| Near | Radiation-hard and high-temperature discretes and small circuits | Nothing else survives | ≤ 1 mm² | [ookuma2026], [kawarada2014] |
| Near | Few-qubit room-temperature quantum accelerators and quantum memories | No cryostat; edge deployment | ≤ 1 mm² diamond on CMOS | [olcf2025], [qbpawsey2023], [li2024] |
| Medium | Multi-kilovolt power switches | Figure of merit, cooling | 1 to 10 mm² | [saha2021], [donato2020], [umezawa2018] |
| Long | Monolithic complementary logic; clustered NV processors with error correction | Requires n-type and placement breakthroughs | > 10 mm² | [liao2024], [yao2012] |

## 13.3 Cost logic for quantum chiplets

A quantum chiplet needs very little diamond. A 1 mm² chiplet from a 76 mm wafer yields about 4,400 gross dies by `adamas.wafer.dies_per_wafer(76, 1.0)`. Only the top few micrometers need quantum-grade ¹²C material ([Chapter 2](02_wafer_manufacturing.md)), so isotope cost per die is negligible. The dominant costs are characterization (every NV site must be mapped) and bonding. This is why detect-and-repair (experiment C-5) and electrical readout (C-6, F-1) are the economically decisive experiments: they convert a microscopy-limited craft into a wafer-probe-style test flow.

## 13.4 Risk register

| Risk | Likelihood | Impact | Mitigation | Sources |
|---|---|---|---|---|
| n-type doping stays impractical | High | Blocks monolithic complementary logic | Heterogeneous integration with silicon; p-only logic for interface roles | [kalish1999], [liao2024], [li2024] |
| NV placement yield stalls below 50 percent | Medium | Blocks direct-coupled arrays | Detect-and-repair; clusters plus bus; laser writing | [chen2019], [luhmann2019], [yao2012] |
| Inter-cell gate fidelity stays below 0.95 at room temperature | Medium | Limits processors to few-qubit cells | ¹²C material, optimal control, closer spacing; accept accelerator niche | [dolde2014], [herbschleb2019] |
| Wafer scaling stalls at 3 to 4 inch | Medium | Cost floor stays high | Small-die products remain viable | [e6orbray2026], [schreck2017] |
| Dislocations limit breakdown and coherence on heteroepitaxial wafers | Medium | Performance gap between HPHT and wafer-scale material | Thick buffer growth, dislocation filtering, offcut substrates | [kim2021], [gaukroger2008], [friel2009] |
| Hole-gas surface instability | Low to medium | Reliability | ALD passivation, oxide acceptors, boron nitride gates | [kawarada2017], [crawford2021], [sasama2022] |
| Competing platforms (superconducting, trapped-ion, neutral-atom, silicon spin) reach fault tolerance first | High | Reduces the general-purpose computing case | Focus on what only room-temperature operation offers: embedded, mobile, and sensing-coupled processing | [preskill2018], [ladd2010], [kane1998] |
| Vendor claims outrun peer review | Present | Credibility of the field | This repository's evidence labels | [saxonq2026], [tqi2026] |

## 13.5 What would change this assessment

1. A shallow n-type dopant or stable n-type transfer doping in diamond.
2. Single-shot electron-spin readout at room temperature with fidelity above 90 percent.
3. A demonstrated room-temperature NV-NV link beyond 50 nm.
4. 150 mm single-crystal wafers with dislocation density below 10⁴ cm⁻².

Any one of these moves a row in [Chapter 12](12_silicon_vs_diamond_scorecard.md) and should trigger a revision of this framework.
