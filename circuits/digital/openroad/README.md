# Routing DIA-4 with OpenROAD (project P-2)

`python circuits/digital/place.py` writes the standard-cell LEF (`adamas_ed.lef`), a timed Liberty (`adamas_ed_timed.lib`),
a placed DEF, and a placed GDS. The placement is a simple row placer with no routing; for a real route and timing
report use OpenROAD-flow-scripts [ajayi2019] through Docker:

```bash
git clone --depth 1 https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts ~/orfs
mkdir -p ~/orfs/flow/designs/adamas/dia4 ~/orfs/flow/platforms/adamas_pdk0
cp circuits/digital/{dia4.v,adamas_ed.lef,adamas_ed_timed.lib} circuits/digital/openroad/{config.mk,constraint.sdc} ~/orfs/flow/designs/adamas/dia4/
cd ~/orfs && ./build_openroad.sh --docker    # or use the prebuilt image: docker pull openroad/orfs
cd flow && make DESIGN_CONFIG=designs/adamas/dia4/config.mk
```

The two-layer stack (GATE vertical, METAL2 horizontal) is thin; expect the router to need a low utilization or a third
metal. That is itself a result: PDK-0 as drawn routes only small blocks, which is consistent with the 10⁴-gate ceiling
of chapter E3. Timing in the Liberty is the calibrated first-order model of `adamas.digital`, not measured data (D-2).
