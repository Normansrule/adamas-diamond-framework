# Routing DIA-4 with OpenROAD (project P-2)

`adamas.orfs_platform` writes a complete OpenROAD-flow-scripts (ORFS) platform for ADAMAS-PDK-0 [ajayi2019]:
technology and cell LEF, timed Liberty (with tie and filler cells), cell GDS, parasitic estimates (`setRC.tcl`), power grid
(`pdn.tcl`: a core ring plus follow-pin rails, because vertical power stripes on the two-layer stack would short to
transistor gates), routing tracks, and a KLayout technology file. One command installs it and runs the flow in Docker:

```bash
bash circuits/digital/openroad/run_orfs.sh            # uses ~/orfs; clones it if missing; log in last_run.log
```

Run it from WSL, not from inside the container. The script mounts `~/orfs/flow` into the `openroad/orfs` image, so every
file is created on the host.

**What to expect.** PDK-0 has two routing layers (gate metal vertical, gold METAL2 horizontal) at a 4 um pitch. Routing
congestion is the likely limit; the design configuration uses 30% core utilization for that reason. If global or detailed
routing fails, that is a PDK result, not a bug: it quantifies the case for a third metal in PDK-1 (chapter E2). Timing
in the Liberty is the calibrated first-order model of `adamas.digital`, and wire parasitics are order-of-magnitude
placeholders until the monitor die is measured.
