# SPICE starting point

| File | Purpose |
|---|---|
| `diamond_pfet.lib` | Level-1 models of enhancement- and depletion-mode hydrogen-terminated diamond p-channel transistors |
| `ed_inverter.cir` | Enhancement/depletion inverter with a DC sweep |

**Honest status:** these netlists were written without access to a simulator and have **not been run**. They mirror the Python model in `adamas/logic.py`, which *is* tested. Run with `ngspice ed_inverter.cir` and compare with `docs/img/fig12_inverter_vtc.png`; note that the SPICE deck uses true negative rails while the Python figure plots magnitudes. Fitting the model cards to published curves ([liu2014], [liu2017], [kawarada2014]) is proposed experiment S-5 in `docs/11_proposed_experiments_and_roadmap.md`.
