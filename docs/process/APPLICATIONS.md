# From process to product: which flow builds what

Every product below uses the same traveler ([TRAVELER.md](TRAVELER.md)) with different options. The numbers to beat are published results; the ADAMAS column points to the model or lab in this repository that predicts the product-level effect.

## Decision table

| Product | Traveler variant | Key options | Numbers to beat (published) | ADAMAS model and lab |
|---|---|---|---|---|
| EV traction inverter, grid converter | Power | Option B ALD (about 450 °C, 100 to 200 nm) for hot and high-voltage operation; long gate-drain spacing; field plate | 2608 V and 19.7 mΩ·cm² ([saha2021]); 2568 V and 7.5 mΩ·cm² ([saha2022]); 3659 V ([saha2023]); 400 °C operation ([kawarada2014]) | `adamas.converter`, [Power Lab](https://normansrule.github.io/adamas-diamond-framework/labs/power.html), chapter [E9](../expert/E9_power_circuits_diamond_vs_gan_sic.md) |
| RF power amplifier (5G base station, radar, satellite) | RF | Option A: NO₂ + thin ALD (about 10 nm, ≤ 150 °C); 0.1 to 1 µm gates by electron-beam lithography | 1.3 A/mm drain current ([hirama2012]); hole density about 9 × 10¹³ cm⁻² at NO₂ saturation ([sato2013]) | chapter [4](../04_analog_power_rf_devices.md) |
| Control electronics for 300 °C and radiation (downhole, space, reactor decommissioning) | High-temperature logic | Option B ALD; no NO₂; enhancement/depletion cells of PDK-0 | 400 °C transistor operation ([kawarada2014]); diamond electronics plant for radiation-hard devices ([ookuma2026]) | `adamas.stdcells`, [Transistor Lab](https://normansrule.github.io/adamas-diamond-framework/labs/transistor.html), [Diamond CPU](https://normansrule.github.io/adamas-diamond-framework/labs/cpu.html) |
| Quantum magnetometer (medical, geophysics, battery inspection) | Sensor | Dense ¹⁵N implant or nitrogen-doped growth; oxygen surface; no transistor steps | Ensemble sensitivity and methods reviewed in ([barry2020]), single-spin imaging ([rondin2014]) | `adamas.nv`, [Lattice Lab](https://normansrule.github.io/adamas-diamond-framework/labs/lattice.html), [Photon Lab](https://normansrule.github.io/adamas-diamond-framework/labs/photon.html) |
| Room-temperature qubit register | Qubit | ¹²C cap; aperture implant at 20 to 50 nm; photocurrent electrodes (QELEC); no NO₂ | 25 nm entangled pair, fidelity 0.67 ([dolde2013]); electrical readout of single spins ([siyushev2019]); chiplets on CMOS ([li2024]) | `adamas.gate_budget`, `adamas.circuit_qec`, [Machine Builder](https://normansrule.github.io/adamas-diamond-framework/labs/machine.html), chapters [E5](../expert/E5_nv_qubit_engineering.md) and [E6](../expert/E6_error_correction_and_system_architecture.md) |
| Heat spreader under GaN amplifiers | (not this flow) | Polycrystalline diamond bonded or grown under GaN | 4-inch GaN-on-diamond ([francis2010]) | `adamas.thermal`, [Heat Race](https://normansrule.github.io/adamas-diamond-framework/labs/heat.html) |

## Product 1: a 1.2 kV power switch for an EV inverter

**What changes in the traveler.** Choose option B at S13 (hot ALD) so the device survives the junction temperatures where diamond's advantage appears. Draw a long gate-drain spacing and a field plate on METAL2 to spread the field; the breakdown voltage of lateral hole-gas devices scales with that spacing ([kawarada2017]).

**Acceptance tests.**
1. Off-state breakdown on sacrificial devices, behind a shield, at 25 °C and 200 °C. Target: at least 1.5 × the bus voltage.
2. Specific on-resistance from the linear region, normalized to the active area including the drift region.
3. Double-pulse switching test to measure switching energy; this is the measurement that replaces the output-capacitance model of `adamas.converter` (project W-2).
4. High-temperature gate bias for threshold stability.

**How it reaches the product.** Loss per switch sets the heat-sink size and the inverter efficiency; the Power Lab shows the chain from R_on·C_oss to kilowatts saved.

## Product 2: an RF power amplifier transistor

**What changes.** Option A (NO₂ + ≤ 150 °C ALD) for the highest hole density; electron-beam gates of 0.1 to 1 µm; T-shaped gates to lower gate resistance. Keep the ALD thin (about 10 nm) for transconductance ([kasu2012]).

**Acceptance tests.** S-parameters for current-gain and power-gain cutoff frequencies; load-pull output power density at the target band; thermal stability of the NO₂ doping under bias ([hirama2012]).

## Product 3: high-temperature control logic

**What changes.** No NO₂ (it desorbs when hot); option B ALD; PDK-0 enhancement/depletion cells with the partial-oxidation ENH layer for enhancement devices ([liu2017]).

**Acceptance tests.** Ring-oscillator period at 25, 200, 300, and 400 °C; noise margins of the inverter chain; the DIA-4 test program (countdown and CALL/RET) on a packaged die at temperature. The ring-oscillator period is compared with the ADAMAS model, and the ratio is logged in the run log (S17).

## Product 4: an NV magnetometer

**What changes.** Only S01 to S07 and S18. Use a high implant dose (about 10¹² to 10¹³ cm⁻²) or nitrogen-doped growth for ensembles; keep the surface oxygen-terminated for NV⁻ stability ([hauf2011]).

**Acceptance tests.** ODMR contrast and line width; sensitivity from the photon rate and line width ([barry2020]); the eight-line vector response to a calibrated coil field (compare with the Lattice Lab).

## Product 5: a qubit register chip

**What changes.** Full flow without NO₂. ¹²C-enriched cap at S03 ([balasubramanian2009]); 20 to 50 nm apertures at S06; photocurrent electrodes and a microwave line on QELEC at S16 ([siyushev2019]). Keep NV windows at least 5 µm from any hole-gas channel (PDK-0 rule).

**Acceptance tests.** Per-window NV count (target one), T₂, NV⁻ fraction, and a two-NV coupling measurement on the closest pairs. The measured charge-state fraction q enters `adamas.gate_budget` directly; chapter E5 shows it is the dominant term in the entangling-gate error.
