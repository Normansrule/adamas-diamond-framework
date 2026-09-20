# DIA-4: a processor sized for p-channel-only diamond logic

Instruction set (opcode, operand): `1` LDI · `2` ADD · `3` SUB · `4` AND · `5` OR · `6` XOR · `7` JNZ · `8` JMP · `9` OUT · `A` CALL · `B` RET · others NOP. The shortcut `make rtl synth` runs everything below.

| File | Purpose |
|---|---|
| `dia4.v` | 4-bit accumulator processor, 9 instructions, synchronous reset |
| `dia4_tb.v` | Testbench: counts down from 5 on the output port, prints PASS |
| `dia4_call_tb.v` | Testbench: nested `CALL`/`RET` through the four-entry return stack, prints PASS |
| `adamas_ed.lib` | Liberty logic view of enhancement/depletion cells; `area` = transistor count |
| `cells_sim.v` | Behavioral cell models for gate-level simulation |
| `synth.ys` | Yosys script [wolf2013] mapping the design onto the cell library |

```bash
iverilog -o /tmp/dia4 dia4.v dia4_tb.v && vvp /tmp/dia4          # behavioral simulation
yosys -q -l synth.log synth.ys && grep -A8 "Number of cells" synth.log | tail -9
iverilog -o /tmp/dia4g dia4_netlist.v cells_sim.v dia4_tb.v && vvp /tmp/dia4g   # gate-level simulation
```

**Tested result (Yosys 0.33, Icarus Verilog):** both simulations print PASS. Synthesis gives 190 to 220 cells (varies with Yosys version)
(13 DFF, 34 INV, 49 NAND2, 100 NOR2, 24 NOR3) = **830 to 900 transistors**, about 40 percent of an Intel 4004 [faggin1996].
Feeding the gate count to `adamas.digital.processor_estimate` gives the clock and power estimates in
`docs/expert/E3_digital_and_cpu_design.md`. Timing in the Liberty file is intentionally absent: no measured
diamond cell delays exist yet (experiment D-2).

**v0.2.1:** with `CALL`/`RET` the design grows to 31 flip-flops and about 1,700 transistors (Yosys 0.33), still below the 4004's 2,300. See `docs/expert/E3_digital_and_cpu_design.md`.
