# Routing DIA-4 with OpenROAD (project P-2)

`python circuits/digital/place.py` writes the standard-cell LEF (`adamas_ed.lef`), a timed Liberty (`adamas_ed_timed.lib`),
a placed DEF, and a placed GDS. The placement is a simple row placer with no routing; for a real route and timing
report use OpenROAD-flow-scripts [ajayi2019] through Docker:

```bash
git clone --depth 1 https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts ~/orfs
make place                                                   # writes the LEF and timed Liberty
mkdir -p ~/orfs/flow/designs/adamas/dia4 ~/orfs/flow/platforms/adamas_pdk0
cp circuits/digital/dia4.v circuits/digital/openroad/{config.mk,constraint.sdc} ~/orfs/flow/designs/adamas/dia4/
cp circuits/digital/{adamas_ed.lef,adamas_ed_timed.lib} circuits/digital/openroad/platform/config.mk ~/orfs/flow/platforms/adamas_pdk0/
docker pull openroad/orfs
docker run -it --rm -v ~/orfs/flow:/OpenROAD-flow-scripts/flow openroad/orfs \
  bash -c "cd /OpenROAD-flow-scripts/flow && make DESIGN_CONFIG=designs/adamas/dia4/config.mk 2>&1 | tail -60"
```

The host directory `~/orfs/flow` is mounted into the container, so create files on the host, never inside the container.

The two-layer stack (GATE vertical, METAL2 horizontal) is thin; expect the router to need a low utilization or a third
metal. That is itself a result: PDK-0 as drawn routes only small blocks, which is consistent with the 10⁴-gate ceiling
of chapter E3. Timing in the Liberty is the calibrated first-order model of `adamas.digital`, not measured data (D-2).
