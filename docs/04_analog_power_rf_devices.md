# 04 · Analog, power, and radio-frequency (RF) devices

**Plain-language summary.** The first useful diamond circuits are not computers. They are switches that block thousands of volts, amplifiers that push radio power, and sensors that survive heat and radiation. These are analog parts, and they are where diamond's advantage over silicon is largest.

## 4.1 The power-switch limit

For a one-sided abrupt junction that must block a voltage $BV$, the drift region needs thickness $W = 2BV/E_c$ and doping $N = \varepsilon E_c^2 / (2 q BV)$. Its resistance per unit area is [baliga1982]:

$$R_{on,sp} = \frac{W}{q \mu N} = \frac{4\,BV^{2}}{\varepsilon \mu E_c^{3}}$$

![Specific on-resistance versus breakdown voltage](img/fig03_ron_vs_bv.png)

At 2608 V, `adamas.power` gives an ideal hole-conduction diamond limit of 0.014 mΩ·cm² and a silicon limit of about 695 mΩ·cm². The measured diamond MOSFET sits at 19.74 mΩ·cm² [saha2021]: already about 35 times better than the silicon limit, and about 1000 times above its own limit. The gap is the research opportunity, and it comes mostly from incomplete ionization, contact resistance, and lateral (not vertical) geometry ([donato2020], [umezawa2018], [geis2018]).

## 4.2 Device families demonstrated so far

| Device | Key result | Sources |
|---|---|---|
| Schottky barrier diode | Multi-kilovolt blocking; >6 kV reported on thick intrinsic layers | [butler2003], [twitchen2004], [traore2014], [volpe2010] |
| Schottky-pn diode | High forward current density with fast switching | [makino2009] |
| pn and p-i-n junctions | Ultraviolet emission at 235 nm from a diamond pn junction | [koizumi2001] |
| Hydrogen-terminated Field-Effect Transistor (FET) | First enhancement-mode device, 1994; operation to 400 °C; normally-off variants | [kawarada1994], [kawarada2014], [kitabayashi2017], [kawarada2017] |
| NO₂-doped MOSFET on heteroepitaxial wafer | 2608 V, 345 MW/cm² Baliga figure of merit | [saha2021], [saha2020] |
| Inversion-channel MOSFET | First on n-type diamond, 2016 | [matsumoto2016] |
| n-channel MOSFET | Electron mobility about 150 cm²/(V·s) at 573 K, 2024 | [liao2024] |
| p-channel MOSFET on n-type body | 2024 | [zhao2024] |
| Junction FET | Operation at elevated temperature with low leakage | [iwasaki2013jfet] |
| Bipolar junction transistor | Current gain demonstrated with phosphorus-doped base | [kato2012bjt] |
| Hexagonal-boron-nitride-gated FET | High channel mobility without surface acceptors | [sasama2018], [sasama2022] |

Reviews: [aleksov2003], [wort2008], [umezawa2018], [geis2018], [donato2020], [koizumi2018book].

## 4.3 Radio-frequency (RF) amplifiers

A transistor's current-gain cutoff frequency is bounded by carrier transit under the gate [sze2006]:

$$f_T \approx \frac{v_{sat}}{2\pi L_g}$$

With the hole-gas saturation velocity near 10⁷ cm/s, a 100 nm gate gives $f_T$ of tens of gigahertz, as measured: 70 GHz class cutoff frequencies and power densities of 2 W/mm at 1 GHz and 3.8 W/mm with ALD Al₂O₃ ([kasu2005], [ueda2006], [russell2012], [yu2018], [imanishi2019], [kasu2017]). Gallium nitride is far ahead in output power today ([mishra2008]); diamond's near-term RF role is as the heat spreader under gallium nitride ([francis2010], [pomeroy2014]).

## 4.4 Analog building blocks: what can be designed today

| Block | Feasible with p-channel-only diamond? | Note |
|---|---|---|
| Common-source amplifier | Yes | Depletion-mode load or resistor load; gain limited by output conductance ([liu2017]) |
| Differential pair | Yes | Needs matched transistors; matching data do not yet exist in the literature |
| Current mirror | Yes (p-type) | Sourcing mirrors only |
| Operational amplifier | Partly | No complementary output stage until n-channel matures ([liao2024]) |
| Voltage reference | Open problem | No bandgap-reference analog; Schottky or threshold-difference references proposed in [Chapter 11](11_proposed_experiments_and_roadmap.md) |
| High-side power switch + driver | Yes | The natural first integrated circuit |
| Radiation and particle detector | Yes, commercial | [pernegger2005]; betavoltaic cells [bormashov2018] |

Silicon carbide shows the precedent: simple junction-FET logic and amplifiers ran for weeks at Venus surface conditions of 460 °C [neudeck2016]. Diamond's wider gap extends the same logic upward in temperature ([neudeck2002]).

## 4.5 Exotic but relevant

Diamond's conduction band has six valleys whose populations can be polarized and transported, a "valleytronic" degree of freedom with no silicon-industry equivalent [isberg2013]. Electrically driven single-photon emission from NV centers in a diamond p-i-n diode ties this chapter to the quantum chapters ([mizuochi2012], [lohrmann2011]).

Code: `adamas.power`, `adamas.thermal`, `circuits/spice/`.
