# Validation matrix

_Generated from `adamas/validation.py` (`make validation`). Interactive version: [validation.html](https://normansrule.github.io/adamas-diamond-framework/validation.html)._

**18 checks: 17 pass, 1 known discrepancy (explained), 0 fail.** Evidence types: *literature* (reproduces a published result), *cross-tool* (two independent implementations agree), *analytic* (recovers a known or injected answer).

![Uncertainty](img/fig49_uncertainty.png)

| Area | Check | Type | Model | Reference | Tolerance | Status | Source | How |
|---|---|---|---|---|---|---|---|---|
| Error correction | Phenomenological surface-code threshold (equal data and readout error) | literature | 3.1 | 2.93 | ±10% | pass | [wang2003] | adamas.surface_sim with PyMatching, chapter E6 (Figure 27) |
| Qubits | Bell fidelity of the published NV pair: coherence-limited model (worst defensible case) vs measured 0.67 | literature | 0.7844 | 0.67 | ±5% | known discrepancy: model range 0.78 to 1.00 stays above the measurement; the authors name dephasing and pulse errors, which the model does not resolve (audit Q1 to Q3) | [dolde2013] [dolde2014] | adamas.gate_budget at q = 1 (the paper normalized out charge-state errors); echo exponent 1 to 3, one or two gate applications, with T1 |
| Qubits | Single-NV readout contrast from the polarized state, 300 ns window | literature | 0.3082 | 0.3 | ±20% | pass | [doherty2013] [gruber1997] | adamas.photophysics five-level model with measured rates [tetienne2012], starting from its own 82% polarization (audit Q18) |
| Power | Measured diamond MOSFETs lie between diamond's and silicon's one-dimensional limits | literature | 3 | 3 | exact | pass | [saha2021] [saha2022] [saha2023] [baliga1982] | no real device may beat its own material limit |
| Logic | Five-stage ring-oscillator period, browser model vs ngspice | cross-tool | 24.6 | 22.4 | ±15% | pass | circuits/spice/ring_oscillator.cir | web/tests/sim.test.mjs; the constant-capacitance node model explains the 10% gap |
| Logic | DIA-4 JavaScript emulator vs Icarus Verilog, random programs identical | cross-tool | 25 | 25 | exact | pass | circuits/digital/dia4.v | tests/test_web.py::test_dia4_emulator_matches_verilog_on_random_programs |
| Logic | Inverter transfer curve, JavaScript vs Python: fraction of points within 0.01 V | cross-tool | 1 | 1 | exact | pass | adamas.logic | web/tests/sim.test.mjs; largest difference 0.003 V at seven input voltages |
| Power | Power Lab switch loss, JavaScript vs adamas.converter | cross-tool | 1 | 1 | ±1% | pass | adamas.converter | tests/test_web.py::test_power_lab_javascript_matches_python (five switches, two temperatures) |
| Systems | Machine Builder runtime, JavaScript vs adamas.resource | cross-tool | 1 | 1 | ±1e-07% | pass | adamas.resource | tests/test_web.py::test_machine_builder_javascript_matches_python |
| Qubits | Photon Lab readout contrast, JavaScript vs Python | cross-tool | 1 | 1 | ±2% | pass | adamas.photophysics | tests/test_photophysics.py::test_photon_lab_matches_python |
| Error correction | Native XZZX circuit equals the standard code under depolarizing noise (ratio of logical errors) | cross-tool | 1.048 | 1 | ±20% | pass | [bonillaataides2021] | adamas.xzzx_native: Clifford-equivalent circuits must perform the same; 40,000 shots each |
| Systems | Sobol first-order index recovers the exact value 0.8 for Y = a + 2b (uniform inputs) | analytic | 0.8038 | 0.8 | ±3% | pass | [sobol2001] [jansen1999] | adamas.decision pick-freeze estimator, 8,000 samples |
| Hardware | ADF4351 registers R2 to R5 vs evaluation-board defaults | cross-tool | 4 | 4 | exact | pass | ADF4351 data sheet | adamas.hw.adf4351, tests/test_hardware.py |
| Thermal | Steady hot-spot ratio silicon/diamond equals the conductivity ratio | analytic | 14.67 | 14.67 | ±1% | pass | [carslaw1959] | web/assets/sim/heat.js steady solver (unit test to 1%) |
| Doping | Arrhenius analysis recovers the boron acceptor energy put into the model (eV) | analytic | 0.3661 | 0.37 | ±3% | pass | [lagrange1998] | adamas.experiments B3 with the density-of-states and mobility correction |
| Sensing | Dipole-law slope recovered from noisy A2 data | analytic | -3.014 | -3 | ±3% | pass | magnetostatics | adamas.experiments A2, 5% simulated noise |
| Analysis | Rabi fit recovers the simulated 5 MHz drive | analytic | 4.996 | 5 | ±1% | pass | adamas.fitting | docs/data/examples/rabi.csv |
| Analysis | g⁽²⁾ fit recovers the simulated g⁽²⁾(0) = 0.2 | analytic | 0.1797 | 0.2 | ±15% | pass | [kurtsiefer2000] | docs/data/examples/g2.csv |

## How sure are the headline numbers?

Figure 49 propagates documented parameter ranges through the headline results (`adamas.uncertainty`). The silicon-carbide-to-diamond EV-inverter loss ratio includes the incomplete ionization of a bulk boron-doped drift. At a 300 K junction it is 0.40 at the baseline and 0.36 at the median (P10 to P90 0.26 to 0.49): a bulk-doped diamond switch loses to silicon carbide. At a 523 K junction it is 1.9 at the baseline and 1.7 at the median (P10 to P90 1.2 to 2.4): diamond wins when hot. The room-temperature machine's runtime (RSA-2048, calibrated step count) is dominated by readout time: median 1.2 years, P10 to P90 0.4 to 5.3 years.
