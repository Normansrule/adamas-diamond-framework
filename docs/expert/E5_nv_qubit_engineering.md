# E5 · NV qubit engineering: open-system models, baths, and control

**Plain-language summary.** Chapters 6 to 8 described the NV qubit with simple formulas. Real qubits lose information to their surroundings, and engineering them means modeling that loss, then designing pulse sequences that fight it. This chapter adds three research-grade tools to the repository (a master-equation gate simulator, a nuclear-spin bath model, and a dynamical-decoupling calculator) and checks each against a published number.

Code: `adamas.opensys`. Foundations of the pulse methods: [rabi1937], [ramsey1950], [hahn1950], [carr1954], [meiboom1958].

## E5.1 Master-equation model of the NV–NV gate

Markovian open-system dynamics ([lindblad1976], [gorini1976]; the formalism implemented by QuTiP [johansson2012]):

$$\dot\rho = -i[H,\rho] + \sum_k \left( c_k\rho c_k^\dagger - \tfrac12\{c_k^\dagger c_k,\rho\}\right)$$

Two electron-spin qubits with $H = 2\pi\nu_{dd}|11\rangle\langle 11|$, $\nu_{dd} = 52\ \mathrm{MHz\,nm^3}/r^3$ ([neumann2010natphys], [dolde2013]); on each spin, dephasing $c = \sqrt{\gamma_\phi/2}\,\sigma_z$ and symmetric relaxation at $1/(2T_1)$ each way, with $1/T_2 = 1/(2T_1) + \gamma_\phi$. Evolving $|{+}{+}\rangle$ for $t_g = 1/(2\nu_{dd})$ should give the maximally entangled state $\mathrm{CZ}|{+}{+}\rangle$.

| Spacing | Simple bound ([Chapter 7](../07_nv_fabrication_and_placement.md)) | Lindblad, $T_2$ = 1.8 ms, $T_1$ = 6 ms |
|---|---|---|
| 10 nm | 0.997 | 0.994 |
| 15 nm | 0.991 | 0.981 |
| 25 nm | 0.960 | 0.916 |
| 30 nm | 0.933 | 0.861 |

![Lindblad gate simulation](../img/fig22_lindblad_gate.png)

**Reading the result.** Both spins dephase, so the true ceiling is lower than the earlier bound. The measured 0.67 [dolde2013] and 0.824 [dolde2014] at 25 nm lie below even this curve; plausible contributors that this model omits are the shorter coherence of that sample, imperfect spin initialization, and accumulated pulse error over a long sequence. Charge-state errors are not among them for the 2013 value, which was normalized to charge-preselected runs (Section E5.1c). Under this memoryless-noise assumption, 99 percent needs spacing at or below about 12 nm in ¹²C material. Section E5.1b shows that assumption is pessimistic for an echoed gate. Coherence inputs: [balasubramanian2009], [herbschleb2019], [jarmola2012]. The current room-temperature record is a two-qubit fidelity of 96.0 ± 2.5 % for NVs 9.5 nm apart, with 594 nm charge-state pre-selection [joas2025] (demonstrated).

**Addressing.** At these spacings both NVs sit inside one diffraction-limited laser spot (about 250 nm), so they cannot be driven or read out optically one by one. Every room-temperature pair so far was told apart spectrally, using NVs on different crystal axes whose lines sit about 30 MHz apart, and read out jointly ([dolde2013], [joas2025]). Field gradients ([grinolds2011], [zhang2017addr]) and the dark-spin bus of [Chapter 8](../08_quantum_processor_architecture.md) are proposed routes to larger arrays; none yet gives individual coherent control below 30 nm at room temperature.

### E5.1b Beyond the Markov approximation: an error budget (project Q-1, done)

The master equation above assumes memoryless noise, which gives exponential decay. NV dephasing is dominated by a *slow* nuclear bath: coherence falls as $e^{-(t/T_2^*)^2}$ in free evolution and as $e^{-(t/T_2)^3}$ under an echo ([delange2010], [maze2008prb], [dobrovitski2008]). That changes the design conclusions, so `adamas.gate_budget` models the gate the way it is run in practice.

**Echoed gate.** Write $|11\rangle\langle11| = (1 - Z_1 - Z_2 + Z_1Z_2)/4$. A simultaneous π pulse on both spins at half time [hahn1950] reverses every single-spin $Z$ term, including quasi-static detuning, and leaves $Z_1Z_2$ untouched. The result equals a controlled-phase gate up to local rotations, in the same time $t_g = 1/(2\nu_{dd})$.

**Closed form.** For independent diagonal noise with single-spin coherence factors $w_1, w_2$, the fidelity of $\mathrm{CZ}|{+}{+}\rangle$ is exactly

$$F_{coh} = \frac{(1+w_1)(1+w_2)}{4}$$

(the test suite checks this against the Lindblad solver to six digits). Each spin's factor over the total entangling time $t = N_g t_g$ ($N_g$ = 1 or 2 gate applications) is

$$w = e^{-t/T_1}\, e^{-(t/T_2)^p}$$

with echo exponent $p = 3$ for a slow ¹³C bath and $p \approx 1$ for fast noise ([delange2010], [dobrovitski2008]). Assumptions: independent, diagonal noise on the two spins; the $T_1$ factor is optional. Adding a per-NV preparation probability $q$ and an error $\epsilon$ on each of $n$ pulses:

$$F = q^2 (1-\epsilon)^n F_{coh} + \frac{1-q^2}{4}$$

Here $q$ is the probability that an NV enters the gate in the state the tomography assumes, after any post-selection; a failed preparation is taken as a fully mixed state. It is a lumped parameter of this model (proposed here), not the product of the NV⁻ fraction and the spin polarization. That product, 0.70 to 0.75 [aslam2013] times the package's own 82 % polarization (`adamas.photophysics.polarization()`), is 0.57 to 0.61 and would give $F$ = 0.50 to 0.53 for the published pair, below the measured 0.67. For charge-preselected data, $q$ = 1 for the charge part.

**Double-quantum encoding.** Using $|{+1}\rangle, |{-1}\rangle$ as the qubit on both centers quadruples the coupling and doubles the magnetic-noise sensitivity, a technique used in NV–NV coupling experiments ([neumann2010natphys], [dolde2013]).

![Gate error budget](../img/fig26_gate_error_budget.png)

| Echo $T_2$ needed for fidelity ($p$ = 3, one gate application, no $T_1$) | 0.90 | 0.99 | 0.999 |
|---|---|---|---|
| 10 nm spacing | 20 µs | 44 µs | 96 µs |
| 15 nm | 68 µs | 150 µs | 324 µs |
| 25 nm | 315 µs | 695 µs | 1.5 ms |
| 25 nm, double quantum | 125 µs | 276 µs | 595 µs |

**What this changes.**

1. The Markov model is a pessimistic bound if the bath is slow. With an echoed gate and $p$ = 3, natural-abundance coherence (0.6 ms [mizuochi2009]) permits 0.98 at 25 nm, and ¹²C material (1.8 ms [balasubramanian2009]) permits 0.999. Under that assumption the spacing rule relaxes from "12 nm" to "25 nm is enough for coherence." The relief depends on $p$: with $p$ = 1 or two gate applications the limit falls well below these values (Section E5.1c), so the exponent must be measured on the sample (proposed here).
2. **Preparation is a hypothesis, not a finding.** Under green illumination the NV⁻ fraction is about 0.70 to 0.75 [aslam2013]. In runs that are *not* pre-selected, $q$ = 0.75 would by itself cap this model near 0.67. The published 0.67, however, was already normalized to charge-preselected runs [dolde2013], so this does not explain it (Section E5.1c). The right panel maps $(q, \epsilon)$ pairs for un-preselected data only.
3. Engineering priority: **charge-state pre-selection or deterministic initialization** ([hopper2018], [shields2015], [doi2014], [joas2025]), robust pulses ([khaneja2005], [dolde2014]), and a measured dephasing model for the gate sequence.

### E5.1c Check against the published pair (project Q-1b, done)

The entanglement experiment of [dolde2013] reports what the budget needs: two NV centers 25 ± 2 nm apart with different orientations, a single-quantum dipolar coupling of 4.93 ± 0.05 kHz (the isotropic 52/r³ rule gives 3.3 kHz; the angular factor supplies the rest), double-quantum echo times of 150 ± 18 µs and 514 ± 50 µs, a spin echo on both spins during the gate, and a Bell fidelity of 0.67 ± 0.04, raised to 0.824 on the same pair with optimal-control pulses [dolde2014], and $T_1$ = 1.12 ms. `adamas.gate_budget.DOLDE2013` stores these numbers; `published_check()` evaluates the model with them.

![Published-pair check](../img/fig36_published_gate_check.png)

| Quantity | Value |
|---|---|
| Gate time (double quantum, 19.7 kHz) | 25 µs (model) |
| Coherence-limited fidelity at $q$ = 1 | **0.784 to 0.998** over $p$ = 1 to 3, one or two gate applications, with and without $T_1$ = 1.12 ms (`adamas.gate_budget.coherence_limited_range()`; 0.998 is $p$ = 3, one application, no $T_1$) |
| Measured, normalized to charge-preselected runs | 0.67 ± 0.04 [dolde2013]; 0.824 with optimal control [dolde2014] (demonstrated) |
| Status | **Known discrepancy**: the measurement lies below the whole model range |

**Reading.** The supplement of [dolde2013] states that the tomography was normalized "to a charge state preselected scheme" and that "a NV initialization close to unity is assumed." Charge-state errors are therefore already removed from the 0.67, and the earlier reading of this section (the charge state ready only 0.75 of the time, so preparation rather than coherence is the bottleneck) is **withdrawn**. The model compares the measurement at $q$ = 1. Its coherence limit spans 0.784 to 0.998 depending on the echo exponent, on whether the gate is applied once or twice (create, then map back for readout), and on $T_1$; the measured value lies below all of it. [dolde2014] names coherence time and imperfect initialization as the limits. Closing the gap needs a full error model of the published sequence (dephasing in both gate applications, pulse errors, spin initialization), which is follow-up Q-1c. Caveat: the tomography pulse count (taken as 8) is an estimate.

## E5.2 The carbon-13 bath

Quasi-static, secular treatment ([maze2008prb], [dobrovitski2008], [zhao2012]): each ¹³C nucleus at position $\mathbf r_k$ shifts the electron by $\pm A_{zz,k}/2$ with

$$A_{zz} = \frac{\mu_0\gamma_e\gamma_n\hbar}{4\pi r^3}(1 - 3\cos^2\theta) \approx \frac{19.9\ \mathrm{kHz\,nm^3}}{r^3}(1-3\cos^2\theta), \qquad \sigma^2 = \tfrac14\sum_k A_{zz,k}^2, \qquad T_2^{*} = \frac{\sqrt2}{2\pi\sigma}$$

`t2star_us_c13` populates a real diamond lattice at random and returns the distribution over configurations. Nuclei coupled above 200 kHz are treated as resolved register qubits instead of noise (a simplification of this repository).

| ¹³C concentration | Median $T_2^{*}$ (model) | Experiment |
|---|---|---|
| 1.1% (natural) | 3.1 µs | 1 to 5 µs ([childress2006], [mizuochi2009]) |
| 0.3% | 8.4 µs | 1.8 ms **echo** $T_2$ at 0.3% in [balasubramanian2009] (different quantity) |
| 0.03% | 69 µs | tens to 100 µs class ([bauch2018]) |

![Bath and decoupling](../img/fig23_bath_and_decoupling.png)

The spread between configurations is a manufacturing fact: two NV centers in the same crystal differ in $T_2^{*}$ by a factor of two or more, so every cell needs individual calibration. The echo time $T_2$ requires nuclear pair dynamics and the cluster-correlation expansion [yang2008]; that is simulation S-3.

## E5.3 Dynamical decoupling

Periodic π pulses average out slow noise ([viola1999], [carr1954], [meiboom1958]; compensated XY sequences [gullion1990]). For classical Gaussian noise with correlation $b^2 e^{-|\tau|/\tau_c}$, the coherence is $e^{-\chi}$ with

$$\chi(t) = \tfrac12\int_0^t\!\!\int_0^t y(t_1)\,y(t_2)\,b^2 e^{-|t_1-t_2|/\tau_c}\,dt_1 dt_2$$

where $y = \pm1$ flips at each pulse [cywinski2008]. With the bath parameters measured in [delange2010] ($b$ = 3.6 µs⁻¹, $\tau_c$ = 25 µs) `t2_under_cpmg_us` returns a Hahn-echo $T_2$ of 2.9 µs (they measured 2.8 µs) and reproduces the $N^{2/3}$ scaling until $T_2$ approaches $\tau_c$, where the curve bends over. The same scaling reaches 0.6 s at 77 K [bargill2013].

## E5.4 Control quality

| Tool | Purpose | Source |
|---|---|---|
| Gradient-ascent pulse engineering | Numerically optimized pulses; raised NV–NV entanglement from 0.67 to 0.824 | [khaneja2005], [dolde2014] |
| Derivative-removal shaping | Suppresses leakage to neighboring hyperfine lines | [motzoi2009] |
| Noise-filtering composite gates | 99.92 percent two-qubit gate (electron–nuclear) | [xie2023], [rong2015] |
| Geometric and holonomic gates | Robustness to amplitude error | [zu2014], [arroyo2014] |
| Randomized benchmarking | Gate error independent of preparation and readout | [knill2008], [magesan2011] |
| Quantum volume | System-level benchmark | [cross2019] |
| Algorithms on NV hardware | Deutsch–Jozsa at 300 K; programmable two-qubit processor; quantum Fourier transform | [shi2010], [wu2019], [vorobyov2021] |

## E5.5 Experiments and simulation projects

| ID | Item | Success metric |
|---|---|---|
| Q-1 | Non-Markovian error budget for the echoed gate | **Done in v0.3.0** (`adamas.gate_budget`, Section E5.1b) |
| Q-1b | Test the budget with the published pair's parameters | **Done in v0.6.0, revised after the audit** (Section E5.1c): at $q$ = 1 the coherence limit is 0.784 to 0.998, above the charge-normalized 0.67; known discrepancy |
| Q-1c | Full error model of the published sequence: dephasing in both gate applications, pulse errors, spin initialization, measured echo exponent | Reproduces 0.67 [dolde2013] and 0.824 [dolde2014] with parameters read from the papers |
| Q-2 | Cluster-correlation-expansion $T_2$ (pairs, then triples) | 0.6 ms natural, 1.8 ms at 0.3% within a factor of two ([mizuochi2009], [balasubramanian2009]) |
| Q-3 | Pulse optimization for the ¹⁴N-selective π pulse of `adamas.register` under 1 percent amplitude noise | Fidelity above 0.999 with amplitude robustness |
| Q-4 | Randomized benchmarking on a benchtop ensemble ([Chapter 11](../11_proposed_experiments_and_roadmap.md), B-5) | Error per Clifford gate with uncertainty |
| Q-5 | Map $T_2^{*}$ of 100 single NVs in one ¹²C-enriched sample | Distribution compared with `t2star_us_c13` |
| Q-6 | Electrical readout of a nuclear-spin register through the electron [gulka2021] on a PDK-0 die | Nuclear Rabi oscillation detected as photocurrent |
