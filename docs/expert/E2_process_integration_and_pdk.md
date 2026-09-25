# E2 · From patterns to real circuits: process integration and a process design kit (PDK)

**Plain-language summary.** A factory process becomes useful to circuit designers only when it is frozen into a rulebook: which layers exist, how small and how close shapes may be, and how the resulting transistors behave in a simulator. Silicon foundries call that rulebook a process design kit. Diamond has none. This chapter specifies a first one, "ADAMAS-PDK-0," small enough for a university cleanroom.

## E2.1 Layer stack and masks

Process basis: hydrogen-terminated diamond MOSFET flow of [Chapter 3](../03_process_flow_vs_cmos.md) ([kawarada2014], [kitabayashi2017], [saha2021]), two threshold flavors as in [liu2017].

| Mask | Layer | Purpose | Minimum feature (proposed) | Tool ([E1](E1_lithography_from_euv_to_electron_beam.md)) |
|---|---|---|---|---|
| 1 | `OHMIC` | Gold source/drain; also protects the hydrogen termination | 2 µm | i-line |
| 2 | `ISO` | Oxygen-plasma isolation outside active areas | 2 µm | i-line |
| 3 | `ENH` | Partial oxidation of the channel for enhancement-mode devices [kitabayashi2017] | 2 µm | i-line |
| 4 | `GATE` | Gate metal on atomic-layer-deposited Al₂O₃ | 2 µm (0.5 µm option) | i-line / electron beam |
| 5 | `VIA` | Openings in Al₂O₃ | 3 µm | i-line |
| 6 | `METAL2` | Interconnect and pads | 3 µm | i-line |
| Q1 (optional) | `QIMPLANT` | Nitrogen implant apertures in oxygen-terminated regions | 20 nm | electron beam |
| Q2 (optional) | `QELEC` | Photocurrent electrodes and microwave line | 1 µm | i-line |

```mermaid
flowchart LR
    m1[OHMIC] --> m2[ISO] --> m3[ENH] --> ald[ALD Al₂O₃] --> m4[GATE] --> m5[VIA] --> m6[METAL2]
    m2 -. quantum option .-> q1[QIMPLANT + anneal] --> q2[QELEC]
```

Design rules follow the scalable lambda convention of [meadconway1980] with λ = 1 µm: minimum width 2λ, spacing 2λ, gate overlap of active 2λ, via enclosure 1λ. Conservative rules trade density for yield, which is the right trade at this maturity ([Chapter 2](../02_wafer_manufacturing.md), yield model).

## E2.2 Process control monitors

Every die carries test structures, because in an immature process the monitors are worth more than the circuits.

| Structure | Extracts | Reference method |
|---|---|---|
| Transfer-length-method ladder | Contact resistance, sheet resistance | [sze2006] |
| Van der Pauw and Hall cross | Hole sheet density and mobility of the hole gas | [sasama2018], [kawarada2017] |
| Metal-oxide-semiconductor capacitor | Oxide capacitance, interface charge, flat-band voltage | [sze2006], [matsumoto2016] |
| Transistor array, W and L sweep | Threshold, transconductance parameter, channel-length modulation, **mismatch coefficient** $A_{VT}$ | [pelgrom1989] |
| Ring oscillators, 5 to 51 stages | Gate delay, static current | [liu2017]; `circuits/spice/ring_oscillator.cir` |
| Serpentine and comb | Metal opens and shorts, defect density $D_0$ for the yield model | [stapper1983] |
| Isolation leakage pair | Oxygen-termination isolation quality | [kawarada2014] |
| NV witness region | Charge-state fraction and $T_2$ next to active circuits | [hauf2011], [grotz2012] |

## E2.3 Compact model ladder

| Level | Model | Use | Status |
|---|---|---|---|
| 0 | Square law (SPICE level 1 [nagel1973], [sze2006]) | Hand analysis, this repository | Done: `circuits/spice/diamond_pfet.lib`, tested |
| 1 | Charge-based all-region model (EKV [enz1995], [tsividis2011]) | Analog design with gm/I_D [silveira1996] | Proposed (S-5) |
| 2 | Verilog-A surface-potential model including hole-gas density versus gate bias, temperature-activated contact resistance, and self-heating | Power and radio-frequency design | Proposed |
| 3 | Statistical corners from the monitor data | Yield-aware design | Requires fabricated lots |

The Python and SPICE level-0 models agree: a 5-stage ring oscillator gives 2.2 ns per stage in ngspice and 3.3 ns in the first-order formula of `adamas.digital`. The hand formula is pessimistic by about 1.5 times, which is normal for first-order delay estimates [rabaey2003].

## E2.4 Open-source design flow

```mermaid
flowchart LR
    rtl[Verilog] --> yosys["Yosys synthesis [wolf2013]<br/>adamas_ed.lib"] --> pnr["Place and route<br/>OpenROAD [ajayi2019], OpenLane [shalan2020]"] --> gds[Layout] --> drc["Design-rule and layout-versus-schematic checks<br/>(KLayout, Magic, Netgen)"] --> fab[Mask tape-out]
    spice["ngspice [nagel1973]<br/>diamond_pfet.lib"] --> yosys
    gds --> pex[Parasitic extraction] --> spice
```

The synthesis step already runs in this repository (`circuits/digital/`). Place and route needs a technology file (layer map, LEF abstract views of the cells), which is project P-2 below. The open 130 nm silicon flow of [shalan2020] is the template.

## E2.4b The monitor die exists (project P-1, done)

`adamas.pdk0` holds the layer map, the lambda rules, and a generator that writes the monitor die as GDSII with a self-contained writer (no layout library needed). `python circuits/layout/make_pdk0_monitor.py` produces `circuits/layout/pdk0_monitor.gds` (16 cells, about 340 rectangles), which KLayout reads back with the correct 3 × 3 mm extent; `pdk0.lyp` colors the layers and `pdk0_drc.lydrc` is a first design-rule deck (width, space, gate-to-ohmic, via enclosure, and "every NV aperture must sit in an oxygen-terminated window").

![PDK-0 monitor die](../img/fig35_pdk0_monitor_die.png)

Contents: transfer-length ladder (2 to 32 µm), van der Pauw cross, 200 µm MOS capacitor, serpentine-plus-comb defect monitor, ten transistor geometries × 4 copies for mismatch statistics ([pelgrom1989]), an NV witness window with a 10 × 10 array of 50 nm implant apertures on a 0.5 µm pitch with photocurrent electrodes ([siyushev2019]), and an 8-pad frame. The die is deliberately sparse: at this maturity every square millimeter of diamond should carry monitors, not product.

```bash
python circuits/layout/make_pdk0_monitor.py && klayout circuits/layout/pdk0_monitor.gds -l circuits/layout/pdk0.lyp
```

## E2.4c Standard cells, LEF, timing, and a placed processor (project P-2, done)

`adamas.stdcells` turns the six logic cells into placeable layouts on a 30 µm row, writes the Library Exchange Format (LEF) abstracts that place-and-route tools read [weste2011], and writes a **timed** Liberty file whose 3 × 3 delay tables come from the first-order model of `adamas.digital` [rabaey2003], calibrated by the ngspice ring oscillator of [E3](E3_digital_and_cpu_design.md). Yosys reads the timed library and re-synthesizes DIA-4 against it.

`circuits/digital/place.py` then places the synthesized DIA-4: a connectivity-ordered row placer (no routing) that writes a placed GDS, a Design Exchange Format (DEF) file OpenROAD can route, and the statistics below. KLayout reads both files back.

![Placed DIA-4](../img/fig37_dia4_placed.png)

| Quantity | Value (Yosys 0.33 netlist, 374 cells) |
|---|---|
| Cell area | 0.28 mm² |
| Core at 60% utilization | 672 × 690 µm, 23 rows |
| Half-perimeter wirelength | about 140 mm |
| Die with pads | about 1 mm² |

A 4004-class processor therefore occupies about one square millimeter in PDK-0 at 2 µm gates, which is the chiplet size that [Chapter 13](../13_economics_and_risk.md) argued yields well on today's wafers. `circuits/digital/openroad/` carries the OpenROAD-flow-scripts configuration for a real route and a timing report ([ajayi2019], [shalan2020]); the two-layer stack of PDK-0 is thin, and routing the whole block may need a third metal, which is a PDK-1 item.

## E2.5 Projects

| ID | Project | Deliverable |
|---|---|---|
| P-1 | Draw the PDK-0 monitor die with the rules above | **Done in v0.6.0**: `circuits/layout/pdk0_monitor.gds`, `.lyp`, `.lydrc` |
| P-2 | LEF, timed Liberty, placement of DIA-4; OpenROAD configuration | **Done in v0.7.0** (Section E2.4c); a routed result with OpenROAD is the remaining step |
| P-3 | Fit level-0 and EKV parameters to digitized curves of [liu2017] and [kawarada2014] | Model cards with fit error |
| P-4 | Fabricate the monitor die (4 masks) on a 3 to 5 mm plate | Measured parameter table that replaces every placeholder in this repository |
