# Equations in action

_Generated from `adamas/action.py` (`adamas build docs`). Interactive version with animations and live sliders: [action.html](https://normansrule.github.io/adamas-diamond-framework/action.html)._

Fourteen equations that run the framework, each paired with the experiment that measures it. On the web page every symbol is a slider: move it and the symbol glows, the numbers are plugged in, the animation changes, and the curve redraws. Press **Play** and the page sweeps the variable for you.

![Fourteen equations in action](../img/fig53_equations_in_action.png)

| # | Scene | Equation | Experiment | Try it |
|---|---|---|---|---|
| 1 | A spin you can see: optically detected magnetic resonance | $f_\pm = D \pm \gamma_e B_\parallel$ | A1 · tier A (Kitchen table) | [open](https://normansrule.github.io/adamas-diamond-framework/action.html#odmr) |
| 2 | Weigh a magnet with light: the inverse-cube law | $B(r) = \frac{\mu_0}{4\pi}\,\frac{2m}{r^3}$ | A2 · tier A (Kitchen table) | [open](https://normansrule.github.io/adamas-diamond-framework/action.html#dipole) |
| 3 | Heat-spreader race: why hot chips sit on diamond | $\Delta T(t) = P\,R_{th}\left(1 - e^{-t/\tau}\right)$ | A3 · tier A (Kitchen table) | [open](https://normansrule.github.io/adamas-diamond-framework/action.html#heat) |
| 4 | Rabi oscillation: rotating a qubit with a microwave pulse | $P_{-1}(\tau) = \frac{\Omega^2}{\Omega^2+\delta^2}\,\sin^2\!\left(\pi\sqrt{\Omega^2+\delta^2}\;\tau\right)$ | B1 · tier B (Teaching lab) | [open](https://normansrule.github.io/adamas-diamond-framework/action.html#rabi) |
| 5 | Ramsey fringes: a clock that runs out of step | $P_0(\tau) = \tfrac12\left[1 + \cos(2\pi\delta\tau)\,e^{-(\tau/T_2^*)^2}\right]$ | B1 · tier B (Teaching lab) | [open](https://normansrule.github.io/adamas-diamond-framework/action.html#ramsey) |
| 6 | Spin echo: turning the runners around | $C(\tau) = e^{-(\tau/T_2)^{p}}$ | B1 · tier B (Teaching lab) | [open](https://normansrule.github.io/adamas-diamond-framework/action.html#echo) |
| 7 | A compass with four needles: vector magnetometry | $\Delta f_i = 2\gamma_e\,\vert \mathbf{B}\cdot\hat{\mathbf n}_i\vert $ | B2 · tier B (Teaching lab) | [open](https://normansrule.github.io/adamas-diamond-framework/action.html#vector) |
| 8 | Watch boron wake up: incomplete ionization | $\frac{p\,(p+N_D)}{N_A - N_D - p} = \frac{N_V}{g}\,e^{-E_A/kT}$ | B3 · tier B (Teaching lab) | [open](https://normansrule.github.io/adamas-diamond-framework/action.html#arrhenius) |
| 9 | One photon at a time: antibunching proves a single qubit | $g^{(2)}(\tau) = 1 - \rho^2\,e^{-\vert \tau\vert /\tau_1}$ | C1 · tier C (Research lab) | [open](https://normansrule.github.io/adamas-diamond-framework/action.html#g2) |
| 10 | The diamond transistor: a hole gas under hydrogen | $I_D = k\left[(V_{GS}-V_{th})V_{DS} - \tfrac12 V_{DS}^2\right]\ \text{(linear)}$ | C2 · tier C (Research lab) | [open](https://normansrule.github.io/adamas-diamond-framework/action.html#fet) |
| 11 | Two qubits talk: the dipolar gate and its error budget | $\nu = \frac{52\ \mathrm{MHz\,nm^3}}{r^3}$ | D1 · tier D (Facility) | [open](https://normansrule.github.io/adamas-diamond-framework/action.html#gate) |
| 12 | Defects on a wafer: yield and good dies | $Y_P = e^{-A D_0}$ | D2 · tier D (Facility) | [open](https://normansrule.github.io/adamas-diamond-framework/action.html#yield) |
| 13 | The power-device limit: Baliga's figure of merit | $R_{on,sp} = \frac{4V_B^2}{\varepsilon\,\mu\,E_c^3}$ | framework | [open](https://normansrule.github.io/adamas-diamond-framework/action.html#bfom) |
| 14 | Error correction: the surface-code threshold | $p_L \approx 0.1\left(\frac{p}{p_{th}}\right)^{(d+1)/2}$ | framework | [open](https://normansrule.github.io/adamas-diamond-framework/action.html#surface) |

## 1. A spin you can see: optically detected magnetic resonance

*Sweep a microwave through 2.87 GHz and the red glow dips; a magnet splits the dip in two.*

$$
f_\pm = D \pm \gamma_e B_\parallel,\qquad B_\parallel = B\cos\theta
$$

| Symbol | Meaning |
|---|---|
| D | zero-field splitting, 2870 MHz at room temperature |
| γₑ | electron gyromagnetic ratio, 28.03 MHz per mT |
| B | magnetic field |
| θ | angle between the field and the NV axis |
| Γ | line width (full width at half maximum) |
| C | fluorescence contrast of a dip |

**In plain words.** Inside the diamond are tiny magnets that glow red when you shine green light on them. A radio wave at exactly the right pitch flips them, and flipped ones glow a little less. Bring a real magnet close and the right pitch splits into two: one higher, one lower.

**How it works.** Green light pumps the NV ground state into mₛ = 0, which fluoresces about 30% more than mₛ = ±1. A microwave at a transition frequency moves population into ±1 and the fluorescence dips. The ±1 levels shift by ±γₑB∥ (Zeeman effect), so the single 2870 MHz dip splits by 2γₑB∥.

**Model details.** Lines are the exact eigenvalue differences of H/h = D S_z² + γₑ B·S for spin 1 with B in the x–z plane (the web page diagonalizes the 3×3 Hamiltonian in closed form); a transverse field adds the second-order shift 3γₑ²B⊥²/2D. Lorentzian line shape of full width Γ; the ensemble case sums four ⟨111⟩ orientations. Same model as adamas.nv.

**Measure it yourself:** experiment A1, *See the qubit glow, then hear it resonate (ODMR)* (tier A, about US$150 to 400); steps in [EXPERIMENTS.md](../experiments/EXPERIMENTS.md#a1--see-the-qubit-glow-then-hear-it-resonate-odmr).

**Interactive:** [https://normansrule.github.io/adamas-diamond-framework/action.html#odmr](https://normansrule.github.io/adamas-diamond-framework/action.html#odmr) · related lab: [labs/lattice.html](https://normansrule.github.io/adamas-diamond-framework/labs/lattice.html) · sources: [gruber1997] [doherty2013] [dreau2011] [stegemann2023]

## 2. Weigh a magnet with light: the inverse-cube law

*Move the magnet back and the splitting collapses as 1/r³: a dipole field, measured by a qubit.*

$$
B(r) = \frac{\mu_0}{4\pi}\,\frac{2m}{r^3},\qquad \Delta f = 2\gamma_e B
$$

| Symbol | Meaning |
|---|---|
| μ₀ | vacuum permeability, 4π × 10⁻⁷ T·m/A |
| m | magnetic dipole moment of the magnet |
| r | distance from the magnet to the diamond |
| Δf | splitting between the outer pair of lines |

**In plain words.** A magnet's pull fades fast when you move it away: twice as far means eight times weaker. The diamond's two red-glow dips tell you exactly how strong the field is, so you can watch the field fade.

**How it works.** On the axis of a small magnet the field is B = (μ₀/4π)(2m/r³). Each NV line pair splits by 2γₑB∥, so the splitting falls as r⁻³: a straight line of slope −3 on log–log axes. The intercept gives m; a 10 mm N52 cube is about 1.2 A·m².

**Model details.** Point-dipole approximation, valid when r is a few magnet sizes; closer in, use the finite-cube field. The experiment fits the outer line pair, whose axis makes the smallest angle with the field (projection factor about 0.85 in the A2 data).

**Measure it yourself:** experiment A2, *Weigh a magnet with light* (tier A, about US$0 to 50); steps in [EXPERIMENTS.md](../experiments/EXPERIMENTS.md#a2--weigh-a-magnet-with-light).

**Interactive:** [https://normansrule.github.io/adamas-diamond-framework/action.html#dipole](https://normansrule.github.io/adamas-diamond-framework/action.html#dipole) · related lab: [labs/lattice.html](https://normansrule.github.io/adamas-diamond-framework/labs/lattice.html) · sources: [rondin2014] [doherty2013]

## 3. Heat-spreader race: why hot chips sit on diamond

*Same heater, four plates. The diamond plate pulls the heat away fastest and stays coolest.*

$$
\Delta T(t) = P\,R_{th}\left(1 - e^{-t/\tau}\right),\qquad R_{th} = \frac{1}{4\kappa a} + R_{paste} + R_{sink}
$$

| Symbol | Meaning |
|---|---|
| P | heater power |
| κ | thermal conductivity of the plate |
| a | heater contact radius, 1 mm |
| R_paste, R_sink | thermal paste and heat sink, 3.0 and 1.5 K/W |
| τ | settling time constant |

**In plain words.** Heat is like a crowd leaving a stadium. Diamond has the widest exits, so the crowd (the heat) leaves fastest and the heater stays coolest.

**How it works.** A small hot spot on a thick plate sees a spreading resistance 1/(4κa); in series with the paste and sink it sets the steady temperature rise P·R_th. Diamond's κ is about five times copper's, so its spreading term almost vanishes and the paste dominates.

**Model details.** Isothermal disk on a half-space [carslaw1959]; the lumped first-order response with τ = 12 + 30/κ s is a fit to the A3 geometry, not a derivation. The animated map is an explicit 2-D diffusion solve with each material's diffusivity κ/ρc (diamond about 11 cm²/s, copper 1.2).

**Measure it yourself:** experiment A3, *Heat-spreader race: diamond against copper, aluminium, and silicon* (tier A, about US$100 to 350); steps in [EXPERIMENTS.md](../experiments/EXPERIMENTS.md#a3--heat-spreader-race-diamond-against-copper-aluminium-and-silicon).

**Interactive:** [https://normansrule.github.io/adamas-diamond-framework/action.html#heat](https://normansrule.github.io/adamas-diamond-framework/action.html#heat) · related lab: [labs/heat.html](https://normansrule.github.io/adamas-diamond-framework/labs/heat.html) · sources: [carslaw1959] [wei1993] [francis2010]

## 4. Rabi oscillation: rotating a qubit with a microwave pulse

*Hold the microwave on longer and the spin rolls from bright to dark and back: a qubit gate.*

$$
P_{-1}(\tau) = \frac{\Omega^2}{\Omega^2+\delta^2}\,\sin^2\!\left(\pi\sqrt{\Omega^2+\delta^2}\;\tau\right)
$$

| Symbol | Meaning |
|---|---|
| Ω | Rabi frequency, set by the microwave power |
| δ | detuning of the microwave from the line |
| τ | pulse length |
| P₋₁ | probability of ending in mₛ = −1 (dimmer) |

**In plain words.** The spin is an arrow on a ball. A microwave pushes it around the ball; leave it on just long enough and the arrow points down: that is a flip, the qubit's NOT gate.

**How it works.** In the rotating frame the drive rotates the Bloch vector about (Ω, 0, δ). On resonance it swings fully from |0⟩ to |−1⟩ every 1/(2Ω): the π pulse. Detuning tilts the axis, so the swing never reaches the bottom and gets faster.

**Model details.** Two-level reduction of the spin-1 (mₛ = 0, −1 subspace), rotating-wave approximation, frequencies in MHz and times in µs so Ω is the Rabi frequency in cycles per µs. Same expression as adamas.nv.rabi without decay; the pulse diagram is the B1 sequence (3 µs initialize, τ, 300 ns readout).

**Measure it yourself:** experiment B1, *Pulsed control: Rabi oscillations, Ramsey fringes, and spin echo* (tier B, about US$3,000 to 10,000); steps in [EXPERIMENTS.md](../experiments/EXPERIMENTS.md#b1--pulsed-control-rabi-oscillations-ramsey-fringes-and-spin-echo).

**Interactive:** [https://normansrule.github.io/adamas-diamond-framework/action.html#rabi](https://normansrule.github.io/adamas-diamond-framework/action.html#rabi) · related lab: [labs/qubit.html](https://normansrule.github.io/adamas-diamond-framework/labs/qubit.html) · sources: [rabi1937] [jelezko2004a] [childress2006]

## 5. Ramsey fringes: a clock that runs out of step

*Two π/2 pulses with a wait between them: the spins fan out and the fringes fade with T₂*.*

$$
P_0(\tau) = \tfrac12\left[1 + \cos(2\pi\delta\tau)\,e^{-(\tau/T_2^*)^2}\right]
$$

| Symbol | Meaning |
|---|---|
| δ | detuning: how fast the spin precesses in the rotating frame |
| τ | free evolution time |
| T₂* | dephasing time from the static spread of fields |
| P₀ | probability of returning to mₛ = 0 |

**In plain words.** Start a hundred runners together. Each runs at a slightly different speed, so after a while they are spread all around the track and you can no longer tell where the group is.

**How it works.** A π/2 pulse tips the spin onto the equator; it precesses at δ during τ; a second π/2 pulse maps the phase onto population, giving fringes at δ. Every NV in the ensemble sees a slightly different static field, so the phases spread and the fringes decay as exp(−(τ/T₂*)²).

**Model details.** Quasi-static Gaussian detuning distribution with σ = √2/(2πT₂*) gives the Gaussian envelope (exponent p = 2); the animation draws spins sampled from that distribution, so the mean vector's length is the envelope. Same as adamas.nv.ramsey.

**Measure it yourself:** experiment B1, *Pulsed control: Rabi oscillations, Ramsey fringes, and spin echo* (tier B, about US$3,000 to 10,000); steps in [EXPERIMENTS.md](../experiments/EXPERIMENTS.md#b1--pulsed-control-rabi-oscillations-ramsey-fringes-and-spin-echo).

**Interactive:** [https://normansrule.github.io/adamas-diamond-framework/action.html#ramsey](https://normansrule.github.io/adamas-diamond-framework/action.html#ramsey) · related lab: [labs/qubit.html](https://normansrule.github.io/adamas-diamond-framework/labs/qubit.html) · sources: [ramsey1950] [childress2006] [degen2017]

## 6. Spin echo: turning the runners around

*Flip every spin halfway through and the static spread cancels; only slow noise remains (T₂).*

$$
C(\tau) = e^{-(\tau/T_2)^{p}},\qquad p \approx 3
$$

| Symbol | Meaning |
|---|---|
| τ | total free time, with a π pulse at τ/2 |
| T₂ | echo coherence time |
| p | stretch exponent; about 3 for a slowly changing carbon-13 bath |
| C | echo contrast |

**In plain words.** Halfway through the race, everyone turns around and runs back at the same speed. The fast runners had gone further, but they come back faster, so everyone arrives at the start line together.

**How it works.** A π pulse at τ/2 reverses each spin's accumulated phase, so any field that stays constant during the sequence cancels exactly. Only fields that change during τ survive; they set T₂, which is hundreds of times longer than T₂* (milliseconds in isotopically pure diamond at room temperature).

**Model details.** Hahn echo with a slow (Ornstein–Uhlenbeck-like) bath gives exp(−(τ/T₂)³); fast or many-spin baths give smaller p. Room-temperature record 1.8 ms in ¹²C-enriched diamond [balasubramanian2009]. Same as adamas.nv.hahn_echo.

**Measure it yourself:** experiment B1, *Pulsed control: Rabi oscillations, Ramsey fringes, and spin echo* (tier B, about US$3,000 to 10,000); steps in [EXPERIMENTS.md](../experiments/EXPERIMENTS.md#b1--pulsed-control-rabi-oscillations-ramsey-fringes-and-spin-echo).

**Interactive:** [https://normansrule.github.io/adamas-diamond-framework/action.html#echo](https://normansrule.github.io/adamas-diamond-framework/action.html#echo) · related lab: [labs/qubit.html](https://normansrule.github.io/adamas-diamond-framework/labs/qubit.html) · sources: [hahn1950] [delange2010] [balasubramanian2009]

## 7. A compass with four needles: vector magnetometry

*Four NV orientations each measure one projection of the field; together they give the whole vector.*

$$
\Delta f_i = 2\gamma_e\,|\mathbf{B}\cdot\hat{\mathbf n}_i|,\qquad |\mathbf B| = \sqrt{\tfrac34\textstyle\sum_{i=1}^{4}\left(\Delta f_i/2\gamma_e\right)^2}
$$

| Symbol | Meaning |
|---|---|
| n̂ᵢ | the four ⟨111⟩ NV axes, at 109.5° to each other |
| Δfᵢ | splitting of the line pair of orientation i |
| B, θ, φ | field magnitude, polar and azimuthal angles |

**In plain words.** The diamond has compass needles pointing four different ways. Each one feels only the part of the magnet's pull along its direction. Read all four and you know exactly which way, and how hard, the magnet pulls.

**How it works.** Each orientation's line pair splits by 2γₑ|B·n̂ᵢ|. Because the four tetrahedral axes satisfy Σ n̂ᵢn̂ᵢᵀ = (4/3)I, the squared projections add up to (4/3)|B|² for any direction: the magnitude comes straight out, and the signs follow from a least-squares fit.

**Model details.** Weak-field (first-order) projections; the sign ambiguity of |B·n̂ᵢ| is resolved by the calibration coils in B2. Off-axis fields add the second-order shift 3γₑ²B⊥²/2D, included in the Lattice Lab spectrum but not in this identity.

**Measure it yourself:** experiment B2, *Vector magnetometry with three-axis coils* (tier B, about US$1,000 to 3,000); steps in [EXPERIMENTS.md](../experiments/EXPERIMENTS.md#b2--vector-magnetometry-with-three-axis-coils).

**Interactive:** [https://normansrule.github.io/adamas-diamond-framework/action.html#vector](https://normansrule.github.io/adamas-diamond-framework/action.html#vector) · related lab: [labs/lattice.html](https://normansrule.github.io/adamas-diamond-framework/labs/lattice.html) · sources: [rondin2014] [barry2020] [doherty2013]

## 8. Watch boron wake up: incomplete ionization

*Boron's holes are bound 0.37 eV deep; heat sets them free and the resistance falls by orders of magnitude.*

$$
\frac{p\,(p+N_D)}{N_A - N_D - p} = \frac{N_V}{g}\,e^{-E_A/kT},\qquad \rho = \frac{1}{q\,p\,\mu(T)}
$$

| Symbol | Meaning |
|---|---|
| p | free hole density |
| N_A, N_D | boron (acceptor) and compensating nitrogen (donor) densities |
| N_V | valence-band effective density of states, ∝ T^1.5 |
| g | acceptor degeneracy, 4 |
| E_A | boron activation energy, 0.37 eV |
| μ(T) | hole mobility, 1500 (T/300 K)^−2.2 cm²/V·s |

**In plain words.** In silicon the extra charges are loose at room temperature. In diamond, boron holds on to them tightly; you have to heat the diamond before most of them let go. That is why diamond chips work better when hot.

**How it works.** Charge neutrality with one acceptor level gives a quadratic for p. With E_A = 0.37 eV only a fraction of a percent of boron is ionized at 300 K; heating frees more holes, so the resistivity drops steeply until lattice scattering (μ ∝ T^−2.2) takes over. Silicon's 0.045 eV dopants are fully ionized: slide E_A down to see.

**Model details.** Closed-form root of the single-level neutrality equation [sze2006] with m*_dos = 0.9 m₀ and g = 4 (adamas.doping); in the compensated regime the corrected Arrhenius slope of ln(ρT^−0.7) gives E_A, without compensation about E_A/2 (B3 analysis).

**Measure it yourself:** experiment B3, *Watch boron wake up: dopant activation in diamond* (tier B, about US$1,500 to 6,000); steps in [EXPERIMENTS.md](../experiments/EXPERIMENTS.md#b3--watch-boron-wake-up-dopant-activation-in-diamond).

**Interactive:** [https://normansrule.github.io/adamas-diamond-framework/action.html#arrhenius](https://normansrule.github.io/adamas-diamond-framework/action.html#arrhenius) · related lab: [explorer.html#ion](https://normansrule.github.io/adamas-diamond-framework/explorer.html#ion) · sources: [lagrange1998] [pernot2010] [sze2006]

## 9. One photon at a time: antibunching proves a single qubit

*Split the light onto two detectors: a single NV can never click both at once.*

$$
g^{(2)}(\tau) = 1 - \rho^2\,e^{-|\tau|/\tau_1},\qquad \rho = \frac{S}{S+B}
$$

| Symbol | Meaning |
|---|---|
| g⁽²⁾(τ) | normalized rate of photon pairs separated by τ |
| ρ | fraction of light from the NV (signal over signal plus background) |
| τ₁ | antibunching time, about the excited-state lifetime at low power |
| g⁽²⁾(0) < 0.5 | proof of a single emitter |

**In plain words.** A single NV center is like a sprinkler that shoots one drop at a time and needs a moment to refill. Put two buckets side by side: they never catch a drop at exactly the same moment.

**How it works.** After emitting, the NV is in its ground state and must be re-excited before it can emit again, so photon pairs at zero delay are missing: a dip in g⁽²⁾(0). Uncorrelated background fills the dip to 1 − ρ²; a dip below 0.5 proves one emitter.

**Model details.** Hanbury Brown–Twiss correlation with a two-level-like recovery e^(−|τ|/τ₁) (bunching from the metastable singlet appears at high power and longer τ). The animation is a stochastic emitter (exponential re-excitation) plus Poisson background on a 50:50 beam splitter; the histogram converges to the formula.

**Measure it yourself:** experiment C1, *One qubit at a time: single NV centers and photon antibunching* (tier C, about US$30,000 to 100,000); steps in [EXPERIMENTS.md](../experiments/EXPERIMENTS.md#c1--one-qubit-at-a-time-single-nv-centers-and-photon-antibunching).

**Interactive:** [https://normansrule.github.io/adamas-diamond-framework/action.html#g2](https://normansrule.github.io/adamas-diamond-framework/action.html#g2) · related lab: [labs/photon.html](https://normansrule.github.io/adamas-diamond-framework/labs/photon.html) · sources: [kurtsiefer2000] [jelezko2004a] [doherty2013]

## 10. The diamond transistor: a hole gas under hydrogen

*Hydrogen-terminated diamond carries a sheet of holes; the gate squeezes it, the drain pulls it.*

$$
I_D = k\left[(V_{GS}-V_{th})V_{DS} - \tfrac12 V_{DS}^2\right]\ \text{(linear)},\quad I_D = \tfrac{k}{2}(V_{GS}-V_{th})^2\ \text{(saturation)},\quad k = \frac{\mu C_{ox} W}{L}
$$

| Symbol | Meaning |
|---|---|
| V_GS, V_DS | gate and drain voltage magnitudes (the p-channel rails are negative in the lab) |
| V_th | threshold, 1.5 V |
| μ | channel hole mobility |
| C_ox | gate capacitance per area: 30 nm aluminium oxide |
| W/L | 100 µm / 2 µm |

**In plain words.** A transistor is a tap. The gate is the handle: open it more and more charge flows. Push harder with the drain and the flow rises, until the channel pinches and the flow stops growing.

**How it works.** Hydrogen termination plus air or oxide acceptors pull electrons out of diamond, leaving a two-dimensional hole gas a few nanometres under the surface. The square-law model gives a linear region for V_DS < V_GS − V_th and saturation beyond, where the channel pinches off at the drain.

**Model details.** Long-channel square-law model with constant mobility (adamas.logic.Fet, used by the ngspice deck and the DIA-4 cell library); real devices add series resistance, velocity saturation, and surface-acceptor drift. Parameters are those of the C2 expected curves.

**Measure it yourself:** experiment C2, *Make and test a diamond transistor (university cleanroom)* (tier C, about US$10,000 to 50,000); steps in [EXPERIMENTS.md](../experiments/EXPERIMENTS.md#c2--make-and-test-a-diamond-transistor-university-cleanroom).

**Interactive:** [https://normansrule.github.io/adamas-diamond-framework/action.html#fet](https://normansrule.github.io/adamas-diamond-framework/action.html#fet) · related lab: [labs/transistor.html](https://normansrule.github.io/adamas-diamond-framework/labs/transistor.html) · sources: [kawarada2023] [kasu2012] [sze2006]

## 11. Two qubits talk: the dipolar gate and its error budget

*Two NVs 25 nm apart feel each other's field; the gate is slow, so coherence and charge state decide the fidelity.*

$$
\nu = \frac{52\ \mathrm{MHz\,nm^3}}{r^3},\quad t_g = \frac{1}{2\nu},\quad F = q^2\left(\frac{1+e^{-(t_g/T_2)^3}}{2}\right)^2 + \frac{1-q^2}{4}
$$

| Symbol | Meaning |
|---|---|
| ν | dipolar coupling (perpendicular geometry) |
| r | NV–NV distance |
| t_g | controlled-phase gate time |
| T₂ | echo coherence time of each spin |
| q | probability that each NV is in the negative charge state and polarized |
| F | Bell-state fidelity |

**In plain words.** Two tiny magnets close together can feel each other, very gently. To make them work as a team they need to be close, stay calm long enough, and both be switched on. If one is 'off' a quarter of the time, the teamwork falls apart.

**How it works.** Magnetic dipole coupling falls as 1/r³: 3.3 kHz at 25 nm, so a gate takes about 150 µs. Echo coherence must survive that long. Even with perfect coherence, if each NV is in the right charge state only with probability q, the fidelity is capped near q²; at q ≈ 0.75 that explains the measured 0.67.

**Model details.** Echoed controlled-phase gate, F_coh = (1 + w)²/4 with w = exp(−(t_g/T₂)³), unprepared runs modeled as fully mixed (fidelity ¼). Single-quantum coupling at θ = 90°; the published pair [dolde2013] used double-quantum encoding (4× coupling). Same as adamas.gate_budget.GateBudget.

**Measure it yourself:** experiment D1, *Two entangled qubits at room temperature* (tier D, about US$500,000 to 2,000,000); steps in [EXPERIMENTS.md](../experiments/EXPERIMENTS.md#d1--two-entangled-qubits-at-room-temperature).

**Interactive:** [https://normansrule.github.io/adamas-diamond-framework/action.html#gate](https://normansrule.github.io/adamas-diamond-framework/action.html#gate) · related lab: [explorer.html#gate](https://normansrule.github.io/adamas-diamond-framework/explorer.html#gate) · sources: [dolde2013] [neumann2010natphys] [aslam2013]

## 12. Defects on a wafer: yield and good dies

*Every killer defect ruins the die it lands on. Bigger dies catch more of them.*

$$
Y_P = e^{-A D_0},\quad Y_M = \left(\frac{1-e^{-A D_0}}{A D_0}\right)^2,\quad N = \frac{\pi (d/2)^2}{A} - \frac{\pi d}{\sqrt{2A}}
$$

| Symbol | Meaning |
|---|---|
| A | die area |
| D₀ | killer defect density |
| d | wafer diameter |
| Y_P, Y_M | Poisson and Murphy yield models |
| N | gross dies per wafer, with edge loss |

**In plain words.** Throw sand at a chessboard. Every square hit by a grain is ruined. Small squares often escape; big squares almost always get hit.

**How it works.** Random point defects give the Poisson yield e^(−AD₀); clustering is better described by Murphy's model. Diamond wafers today carry far more killer defects than silicon (about 0.1 per cm² in mature silicon fabs), which is why small dies and power products come first.

**Model details.** Gross dies use the standard edge-loss approximation [plummer2000]; good dies = N·Y_M as in adamas.wafer.good_dies. The animation drops defects uniformly on the usable disk (exactly the Poisson model) and counts the dies hit.

**Measure it yourself:** experiment D2, *A diamond pilot line on 3-inch wafers* (tier D, about US$5,000,000 to 50,000,000); steps in [EXPERIMENTS.md](../experiments/EXPERIMENTS.md#d2--a-diamond-pilot-line-on-3-inch-wafers).

**Interactive:** [https://normansrule.github.io/adamas-diamond-framework/action.html#yield](https://normansrule.github.io/adamas-diamond-framework/action.html#yield) · related lab: [labs/wafer.html](https://normansrule.github.io/adamas-diamond-framework/labs/wafer.html) · sources: [murphy1964] [stapper1983] [plummer2000]

## 13. The power-device limit: Baliga's figure of merit

*To block more volts a switch needs a thicker, lighter-doped layer; diamond's field strength makes that layer tiny.*

$$
R_{on,sp} = \frac{4V_B^2}{\varepsilon\,\mu\,E_c^3},\qquad \mathrm{BFOM} = \varepsilon\,\mu\,E_c^3
$$

| Symbol | Meaning |
|---|---|
| V_B | breakdown voltage the switch must block |
| ε | permittivity |
| μ | carrier mobility (holes for diamond today) |
| E_c | critical field |
| W | drift-layer thickness |

**In plain words.** A power switch is a wall that must hold back high voltage when off, and be a wide-open door when on. Diamond can be a very thin wall, and a thin wall is easy to walk through.

**How it works.** The drift layer of a unipolar switch must hold V_B at a peak field E_c: thickness W = 2V_B/E_c and doping ∝ εE_c²/V_B. Its resistance is then 4V_B²/(εμE_c³). E_c enters cubed, so diamond's 10 MV/cm beats silicon's 0.3 MV/cm by a factor of about 37,000 from the field alone.

**Model details.** Ideal one-dimensional punch-through-free drift layer with full ionization [baliga1982] (adamas.power.ron_sp_mohm_cm2). Diamond with holes today; incomplete ionization of boron raises the real value at room temperature (see the B3 scene and the Power Lab).

**Interactive:** [https://normansrule.github.io/adamas-diamond-framework/action.html#bfom](https://normansrule.github.io/adamas-diamond-framework/action.html#bfom) · related lab: [labs/power.html](https://normansrule.github.io/adamas-diamond-framework/labs/power.html) · sources: [baliga1982] [isberg2002] [kimoto2014]

## 14. Error correction: the surface-code threshold

*Below threshold, every step up in code distance multiplies the protection.*

$$
p_L \approx 0.1\left(\frac{p}{p_{th}}\right)^{(d+1)/2},\qquad n = 2d^2 - 1
$$

| Symbol | Meaning |
|---|---|
| p | physical error rate per operation |
| p_th | threshold, about 1% |
| d | code distance (odd) |
| p_L | logical error per round |
| n | physical qubits per logical qubit |

**In plain words.** Copy a secret onto many noisy notes and take a careful vote. If each note is only rarely wrong, adding more notes makes the vote almost never wrong. If notes are wrong too often, more notes just add more mistakes.

**How it works.** A distance-d surface code fails only when about (d+1)/2 errors line up across the lattice. Below threshold (p < p_th ≈ 1%) each increase of d by 2 multiplies the suppression by p_th/p, at a cost of 2d² − 1 qubits.

**Model details.** Heuristic scaling [fowler2012] with prefactor 0.1 (adamas.qec); the framework's circuit-level Stim and PyMatching tables (adamas.resource) replace it for the machine estimate, including the native XZZX code under biased noise.

**Interactive:** [https://normansrule.github.io/adamas-diamond-framework/action.html#surface](https://normansrule.github.io/adamas-diamond-framework/action.html#surface) · related lab: [labs/qec.html](https://normansrule.github.io/adamas-diamond-framework/labs/qec.html) · sources: [fowler2012] [dennis2002] [kitaev2003]

