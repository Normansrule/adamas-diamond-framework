# E6 · Error correction and system architecture

**Plain-language summary.** Every qubit makes mistakes. A useful quantum computer hides those mistakes by spreading each "logical" qubit across many physical ones. This chapter counts how many NV cells that takes, shows why better links matter more than more qubits, and lays out the full computing stack from algorithm to microwave pulse.

Code: `adamas.qec`.

## E6.1 Codes

| Code | Idea | Overhead | Needs | Source |
|---|---|---|---|---|
| Three-qubit repetition | Majority vote on one error type; $p_L = 3p^2 - 2p^3$ | 3 | Any three coupled spins | [shor1995]; room-temperature NV demonstration [waldherr2014] |
| Steane and other stabilizer codes | Parity checks on both error types | 7+ | All-to-all within a cell | [steane1996], [gottesman1997]; five-qubit code at 4 K [abobeih2022] |
| Surface code | Two-dimensional grid, nearest-neighbor checks, threshold near 1% | $2d^2 - 1$ | Planar nearest-neighbor links | [kitaev2003], [dennis2002], [fowler2012] |
| Quantum low-density parity-check codes | About 10× fewer qubits than surface code | lower | **Long-range links** | [bravyi2024] |
| Modular / networked cells | Small processors joined by noisy links plus purification | high, but tolerant of 10% link error | Heralded entanglement | [nickerson2014], [nemoto2014] |

Surface-code scaling [fowler2012]:

$$p_L \approx 0.1\left(\frac{p}{p_{th}}\right)^{(d+1)/2}, \qquad p_{th}\approx 10^{-2}$$

![Surface-code overhead in NV cells](../img/fig24_qec_overhead.png)

| Physical error | Target logical error | Distance | Physical qubits | NV cells (4 qubits each) |
|---|---|---|---|---|
| 10⁻³ | 10⁻⁹ | 17 | 577 | 145 |
| 10⁻³ | 10⁻¹² (×100 logical qubits) | 23 | 105,700 | 26,425 |
| 8 × 10⁻³ ([rong2015] two-qubit) | 10⁻⁹ | > 150 | impractical | impractical |

**The lesson.** Gates inside a cell already sit near or below threshold ([rong2015], [xie2023]). The code distance, and with it the machine size, is governed by the *worst* operation in the syndrome cycle, which is the inter-cell link ([E5](E5_nv_qubit_engineering.md)) and the readout. A factor of ten in link error is worth more than a factor of ten in qubit count.

## E6.2 Mapping codes onto NV hardware

```mermaid
flowchart TB
    subgraph cell["NV cell = 1 electron + 3 nuclear spins"]
        e((e⁻ : ancilla and bus))
        n1((¹⁴N : data))
        c1((¹³C : data))
        c2((¹³C : memory))
    end
    cell -- "dipolar link ≤ 12 nm" --- cell2["neighbor cell"]
    cell -- "dark-spin bus [yao2012]" --- cell3["distant cell"]
    e --> ro["photoelectric readout [siyushev2019]<br/>repeated via nuclear ancilla [neumann2010science]"]
```

Design choices this repository recommends (proposals):

1. **Electron as ancilla, nuclei as data.** Syndrome extraction needs repeated readout, and nuclear spins survive optical readout of the electron ([jiang2009], [neumann2010science], [maurer2012]).
2. **Syndrome cycle budget.** Nuclear gate 10 to 100 µs, electron gate 10 to 100 ns, repetitive readout 1 to 10 ms ([dutt2007], [vandersar2012], [neumann2010science]). The cycle is readout-limited at roughly 100 Hz to 1 kHz, five to six orders slower than superconducting hardware. Room-temperature NV machines will be memory-rich and slow, which suits sensing, networking, and embedded co-processing more than large-scale factoring ([shor1997]).
3. **Hierarchy.** Small code inside each cell (repetition or a 5-qubit code as in [abobeih2022]) concatenated with a surface or modular code between cells, so inter-cell links can be noisier ([nickerson2014]).

## E6.3 The full stack

```mermaid
flowchart TB
    a["Algorithm: search [grover1997], factoring [shor1997], variational [peruzzo2014]"] --> b["Logical circuit"]
    b --> c["Error-correction layer: code, decoder (silicon die)"]
    c --> d["Physical circuit on the cell graph: routing through electron buses"]
    d --> e["Pulse compiler: selective π pulses, decoupling, optimal control [khaneja2005]"]
    e --> f["Waveform generation: 2.87 GHz and 1 to 10 MHz (silicon die) [kim2019cmos]"]
    f --> g["Diamond die: NV cells, photocurrent electrodes, p-channel multiplexers, DIA-4-class sequencer (see E3)"]
    g --> h["Readout chain (see E4)"] --> c
```

Near-term machines skip the error-correction layer and run shallow circuits [preskill2018]; their figure of merit is quantum volume [cross2019], verified by randomized benchmarking ([knill2008], [magesan2011]).

## E6.4 Projects

| ID | Project | Deliverable |
|---|---|---|
| X-1 | Monte Carlo surface-code simulator with separate intra-cell, inter-cell, and readout error rates | Threshold surface in three error dimensions |
| X-2 | Compiler from a gate list to `adamas.register` pulse sequences for a 1-electron + 2-nuclei cell | Verified Deutsch–Jozsa [shi2010] and Grover [grover1997] on the simulator |
| X-3 | Architecture trade study: direct dipolar lattice versus dark-spin bus versus modular cells, using yields from `adamas.coupling.pair_yield` | Cells per logical qubit versus nitrogen-to-NV conversion yield |
| X-4 | Decoder latency budget on the silicon die | Decoder that keeps pace with a 1 kHz syndrome cycle (easy) and headroom analysis |
