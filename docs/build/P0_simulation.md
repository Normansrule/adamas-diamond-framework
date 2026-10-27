# P0 · Simulation

_Generated from `adamas/build_program.py` (`adamas build docs`); every number below is computed by the package._

**Status: written in full.** Budget: US$0 (open-source tools on a laptop, Atlas item M00). Gate verdict today: **go**.

## Goal

Make every later step runnable in the app first, and calibrate each model against published data, a second independent implementation, or a known answer. Hardware is planned only from models that pass this phase.

## Physics and equations

The 14 equations in action, one per experiment plus the power and error-correction limits (assumptions and validity ranges on each scene, [Equations in Action](../EQUATIONS_IN_ACTION.md)):

| Scene | ID | Sources |
|---|---|---|
| A spin you can see: optically detected magnetic resonance | `odmr` | [gruber1997], [doherty2013], [dreau2011], [stegemann2023] |
| Weigh a magnet with light: the inverse-cube law | `dipole` | [rondin2014], [doherty2013] |
| Heat-spreader race: why hot chips sit on diamond | `heat` | [carslaw1959], [wei1993], [francis2010] |
| Rabi oscillation: rotating a qubit with a microwave pulse | `rabi` | [rabi1937], [jelezko2004a], [childress2006] |
| Ramsey fringes: a clock that runs out of step | `ramsey` | [ramsey1950], [childress2006], [degen2017] |
| Spin echo: turning the runners around | `echo` | [hahn1950], [delange2010], [balasubramanian2009] |
| A compass with four needles: vector magnetometry | `vector` | [rondin2014], [barry2020], [doherty2013] |
| Watch boron wake up: incomplete ionization | `arrhenius` | [lagrange1998], [pernot2010], [sze2006] |
| One photon at a time: antibunching proves a single qubit | `g2` | [kurtsiefer2000], [jelezko2004a], [doherty2013] |
| The diamond transistor: a hole gas under hydrogen | `fet` | [kawarada2023], [kasu2012], [sze2006] |
| Two qubits talk: the dipolar gate and its error budget | `gate` | [dolde2013], [joas2025], [neumann2010natphys], [aslam2013] |
| Defects on a wafer: yield and good dies | `yield` | [murphy1964], [stapper1983], [plummer2000] |
| The power-device limit: Baliga's figure of merit | `bfom` | [baliga1982], [isberg2002], [kimoto2014] |
| Error correction: the surface-code threshold | `surface` | [fowler2012], [dennis2002], [kitaev2003] |

The equation-in-the-loop panels the labs carry, each with its reference implementation (assumption checks run live in the lab):

| Panel | Reference implementation | Lab |
|---|---|---|
| Rabi oscillation | `adamas.nv.rabi` | qubit.html |
| Ramsey fringes | `adamas.nv.ramsey` | qubit.html |
| Hahn echo with a mistimed π pulse | `adamas.nv.echo_mistimed` | qubit.html |
| Readout contrast you can measure | `adamas.photophysics.measured_contrast` | photon.html |
| Why diamond wins only when hot | `adamas.converter.ron_temperature_factor` | power.html |
| Driving one NV without the other | `adamas.addressing.crosstalk` | addressing.html |
| Crystal quality sets the breakdown field | `adamas.power.critical_field_mv_cm` | wafer.html |
| Where the magnetic-resonance lines sit | `adamas.nv.lines_perturbative_mhz` | lattice.html |
| How long the hot spot takes to settle | `adamas.thermal.slowest_mode_time_s` | heat.html |
| A hand estimate of the ring oscillator | `adamas.logic.ring_period_estimate_s` | transistor.html |
| How fast a bigger code wins | `adamas.qec.surface_code_logical_error` | qec.html |
| The failure budget that sets the code distance | `adamas.resource.failure_probability` | machine.html |
| What bias leaves the gate | `adamas.gatebias.output_bias` | bias.html |

Larger simulations: circuit-level surface and XZZX codes in Stim with PyMatching decoding (`adamas.circuit_qec`, `adamas.xzzx_native`), the Lindblad and echo gate budget (`adamas.gate_budget`, `adamas.opensys`), yield models (`adamas.wafer`), and the converter loss model (`adamas.converter`).

## Machines and facility

M00: a workstation with Python 3.10 or newer, Node.js, and the open tools in [DEVELOPMENT_UBUNTU.md](../DEVELOPMENT_UBUNTU.md) (Stim, PyMatching, ngspice, Icarus Verilog, Yosys, KLayout, OpenROAD). No laboratory, no safety training.

## Procedure

```bash
pip install -e ".[dev]" && (cd web && npm ci)
python -m pytest -q -rs          # every model test; -rs prints why anything skipped
(cd web && npm test)              # browser physics against Python golden values
make validation                   # the validation matrix below
make serve                        # run every lab locally
```

## Expected results and pass/fail

The validation matrix ([VALIDATION.md](../VALIDATION.md)) has **18 checks**: 4 against published results, 8 between two independent implementations, and 6 against known or injected answers.

| Criterion | Result | Pass? |
|---|---|---|
| No check fails | 0 fail | yes |
| Checks within tolerance | 17 of 18 | yes |
| Known discrepancies, explained and carried forward | 1 | listed below |

Known discrepancies (each says why, in the matrix):

- Bell fidelity of the published NV pair: coherence-limited model (worst defensible case) vs measured 0.67

## Failure modes

- A model can pass its one calibration point and still be wrong elsewhere. Each scene and panel states its validity range, and the labs flag states outside it.
- A cross-tool check catches a coding error but not a shared wrong assumption. The literature checks are the ones that test physics.
- Unmeasured inputs (the NV two-qubit gate bias, the inter-cell link) are assumptions, listed in [STATUS.md](../STATUS.md); P0 cannot validate them.

## Decision gate

*Do the models agree with published data well enough to plan hardware?* **Go**: no check fails. The 1 known discrepancy (or discrepancies) move forward to the phase that can measure them; the Bell-fidelity one goes to P5, where two-NV entanglement is measured.

Sources: see each scene and panel; validation sources in [VALIDATION.md](../VALIDATION.md).
