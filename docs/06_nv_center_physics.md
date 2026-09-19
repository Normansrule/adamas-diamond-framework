# 06 · Physics of the nitrogen-vacancy (NV) center

**Plain-language summary.** The NV center is an atom-sized compass needle trapped in diamond. Green light points it "up," microwaves rotate it to any angle, and the brightness of its red glow reveals which way it points. Because the diamond cage is so stiff and magnetically quiet, the needle keeps its quantum state for milliseconds at room temperature, and a neighboring atomic nucleus can store it for seconds.

## 6.1 Structure and history

A substitutional nitrogen atom next to a carbon vacancy, in its negative charge state (NV⁻), has six electrons forming a spin triplet ($S = 1$) ground state of symmetry ³A₂ ([davies1976], [loubser1978], [doherty2011], [maze2011], [gali2008], [gali2019]). Single centers were first imaged and their magnetic resonance detected optically in 1997 [gruber1997]; coherent oscillations of one electron spin and of one nuclear spin followed in 2004 ([jelezko2004a], [jelezko2004b]). Standard review: [doherty2013].

## 6.2 Ground-state Hamiltonian

In frequency units [doherty2013]:

$$\frac{H}{h} = D\left(S_z^{2} - \tfrac{2}{3}\right) + E\left(S_x^{2} - S_y^{2}\right) + \gamma_e\,\mathbf{B}\cdot\mathbf{S} + \mathbf{S}\cdot\mathbf{A}\cdot\mathbf{I} + P I_z^{2}$$

| Symbol | Meaning | Value | Source |
|---|---|---|---|
| $D$ | Zero-field splitting between $m_s = 0$ and $m_s = \pm 1$ | 2.870 GHz at 300 K | [loubser1978], [doherty2013] |
| $dD/dT$ | Temperature shift | −74.2 kHz/K | [acosta2010], [toyli2012] |
| $\gamma_e$ | Electron gyromagnetic ratio | 28.03 GHz/T | [doherty2013] |
| $E$ | Strain and electric-field splitting | sample dependent, kHz to MHz | [dolde2011] |
| $A_\parallel$ (¹⁴N) | Hyperfine coupling to the host nitrogen nucleus | −2.16 MHz (¹⁴N), 3.03 MHz (¹⁵N) | [felton2009] |
| $P$ | ¹⁴N quadrupole splitting | −4.95 MHz | [felton2009] |
| $A$ (¹³C) | Hyperfine coupling to nearby carbon-13 | up to about 130 MHz, site dependent | [smeltzer2011], [childress2006] |

For a field $B_\parallel$ along the NV axis the two resonances are $f_\pm = D \pm \gamma_e B_\parallel$. `adamas.nv.transition_frequencies_mhz(1.0)` returns 2841.97 and 2898.03 MHz at 1 mT.

![Simulated optically detected magnetic resonance spectra](img/fig08_odmr.png)

The four possible ⟨111⟩ orientations of the NV axis give up to eight lines in an ensemble, which turns a diamond chip into a vector magnetometer ([rondin2014], [barry2020], [schirhagl2014]).

## 6.3 The optical cycle: initialization and readout

![NV energy levels](img/fig07_nv_levels.png)

Green excitation (typically 532 nm) drives the ³A₂ → ³E transition; the zero-phonon line is at 637 nm and most emission falls in a phonon sideband from 640 to 800 nm ([davies1976], [doherty2013]). From the excited state, $m_s = \pm 1$ has a much higher probability than $m_s = 0$ of crossing into the singlet states (¹A₁ → ¹E, infrared line at 1042 nm), which return preferentially to $m_s = 0$ ([manson2006], [goldman2015], [robledo2011njp], [tetienne2012]). Two results follow:

- **Spin polarization** above about 80 percent into $m_s = 0$ after a microsecond of green light.
- **Spin-dependent fluorescence**: about 30 percent fewer photons from $m_s = \pm 1$ during the first few hundred nanoseconds.

The contrast is modest and only a fraction of a photon is detected per readout, so room-temperature optical readout of the electron spin is an averaging measurement, not single-shot ([hopper2018], [steiner2010]). Workarounds appear in [Chapter 8](08_quantum_processor_architecture.md).

**Charge state.** Green light also shuffles the defect between NV⁻ and neutral NV⁰; the steady-state NV⁻ population under 532 nm is about 70 to 75 percent ([aslam2013]). Electrical gating and surface chemistry control it ([grotz2012], [hauf2011], [doi2014]).

## 6.4 Coherent control

A resonant microwave field of Rabi frequency $\Omega$ rotates the spin [jelezko2004a]:

$$P_{|{-1}\rangle}(t) = \frac{\Omega^2}{\Omega^2 + \delta^2}\sin^2\left(\pi t\sqrt{\Omega^2 + \delta^2}\right)$$

Gates as fast as a nanosecond have been driven, beyond the rotating-wave regime [fuchs2009]. Ramsey fringes decay with $T_2^{*}$, Hahn echoes with $T_2$, and dynamical decoupling pushes toward the $T_1$ limit ([childress2006], [delange2010], [bargill2013], [zhao2012]):

![Rabi, Ramsey, and Hahn echo simulations](img/fig09_coherent_control.png)

## 6.5 Coherence at room temperature

| Quantity | Value | Condition | Source |
|---|---|---|---|
| $T_2^{*}$ | about 1 to 5 µs | natural carbon (1.1% ¹³C) | [childress2006], [mizuochi2009] |
| $T_2^{*}$ | tens to about 100 µs and beyond | ¹²C-enriched | [balasubramanian2009], [bauch2018] |
| $T_2$ (echo) | about 0.6 ms | natural carbon | [mizuochi2009] |
| $T_2$ (echo) | 1.8 ms | 99.7% ¹²C | [balasubramanian2009] |
| $T_2$ (echo) | 2.4 ms | phosphorus-doped n-type, ¹²C | [herbschleb2019] |
| $T_1$ | about 6 ms | phonon limited at 300 K | [jarmola2012], [cambria2023] |
| Nuclear memory | > 1 s | ¹³C with decoupling and laser dissipation | [maurer2012] |
| $T_2$ at 3.7 K, for contrast | about 1 s | dynamical decoupling | [abobeih2018] |

![Room-temperature coherence times](img/fig13_room_temp_coherence.png)

Decoherence sources and their scaling: carbon-13 bath ([mizuochi2009], [zhao2012]); substitutional nitrogen (P1) bath, $1/T_2 \propto [\mathrm{N}]$ ([vanwyk1997], [bauch2020]); surface noise for centers shallower than about 10 nm ([rosskopf2014], [myers2014], [romach2015], [sangtawesin2019], [oforiokai2012]).

## 6.6 Sensing: the application that already ships

Shot-noise-limited continuous-wave sensitivity for linewidth $\Delta\nu$, contrast $C$, and photon rate $R$ [dreau2011]:

$$\eta_{B} \approx \frac{4}{3\sqrt{3}}\,\frac{h}{g\mu_B}\,\frac{\Delta\nu}{C\sqrt{R}}$$

Magnetometry ([taylor2008], [maze2008], [balasubramanian2008], [wolf2015]), electric fields [dolde2011], temperature ([kucsko2013], [toyli2013]), nanoscale nuclear magnetic resonance ([glenn2018], [bucher2019]), wide-field imaging ([levine2019], [casola2018]), integrated-circuit current mapping [turner2020], and portable packages [stuerner2021]. General theory: [degen2017]. Sensing is both the near-term product and the diagnostic tool for every quantum-processor experiment in this framework.

Code: `adamas.nv`.
