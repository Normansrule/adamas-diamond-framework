# Speaker notes: "Diamond chips, from wafer to qubit"

A 12-slide, 12 to 15 minute talk ([paper/talk.pdf](../paper/talk.pdf)) for seminars, PhD interviews, and lab visits, with an A0 poster ([paper/poster.pdf](../paper/poster.pdf)) and the preprint ([paper/adamas.pdf](../paper/adamas.pdf)). All three are built by `make talk poster paper`, and every number on them comes from the package, so they always match the code. Roughly one minute per slide.

| # | Slide | What to say | Likely question and a good answer |
|---|---|---|---|
| 1 | Title | One line: an open framework that follows diamond from the wafer to a quantum processor, where every number is computed and tested. | "Is this experimental work?" It is a modeling and tooling framework, validated against published measurements, with experiments designed to calibrate it. |
| 2 | Why diamond at all? | The power figure of merit and heat conduction are extreme, and the NV center is a room-temperature qubit. Then the catch: deep dopants, small wafers, p-channel-only logic. | "Why not just use SiC or GaN?" They are mature and good; the question is where diamond's margin pays for its immaturity: high voltage, high temperature, and quantum sensing. |
| 3 | What ADAMAS is | The chain from materials to experiments; validation and reproducibility are part of the design, not an afterthought. | "How do you know the models are right?" Point to the validation matrix: literature, cross-tool, and analytic checks. |
| 4 | Power switches | Real devices already beat silicon's theoretical limit by about two orders of magnitude; the inverter table puts it in watts. | "Why lateral devices?" Hydrogen-terminated hole-gas devices are the most mature diamond transistors; vertical devices need better doping. |
| 5 | Uncertainty | The textbook figure is the optimistic end; with honest ranges the advantage over SiC is a median of about 3.8×. Mobility and critical field dominate. | "Why should I trust your ranges?" They are from the published spread and stated in the code; the tornado shows what to measure first. |
| 6 | How you would build it | Surface chemistry makes the channel; gold goes on first; one oxygen plasma isolates; heat before metal. | "Has this flow been run?" It follows published process papers step by step; the traveler lists sources, pass criteria, and failure modes. |
| 7 | A processor on diamond | A small process design kit and a placed 4-bit processor about 1 mm² in size; emulator and Verilog agree. | "Why a 4-bit CPU?" It is the smallest complete test of a logic process, like the 4004 was for silicon. |
| 8 | Two-qubit bottleneck | Coherence would allow 0.998; the measured 0.67 is explained by the charge state being ready only 75% of the time. | "Isn't that just a fit?" It uses the paper's own parameters with one free parameter, which matches the independently measured NV⁻ fraction. |
| 9 | Slow readout | Data qubits wait during millisecond readout; scaling stops near 100 ms for a 1 s memory; the XZZX code buys about 10×. | "Why is XZZX better here?" Nuclear memories mostly dephase; XZZX spreads that biased noise across both logical sectors. |
| 10 | How big, how slow | Small die, years of runtime; readout and gate time are the levers, not area. | "So is this useless?" For factoring, yes today; for sensing, networking, and embedded quantum memory, room temperature matters more than speed. |
| 11 | Experiments | Anyone can start with a US$150 ODMR kit; firmware and fitter are in the repository. | "Have you built it?" State honestly what you have and have not built yet. |
| 12 | Takeaways | Four sentences: bounded power advantage, preparation bottleneck, small but slow, all open and regenerable. | Close by inviting collaboration on the calibration experiments. |

**Tips.** Practice slide 5 and slide 8; they are the two "honest science" moments that tend to impress. If time is short, skip slides 6 and 7. Keep the poster's QR code visible; it opens the interactive site.
