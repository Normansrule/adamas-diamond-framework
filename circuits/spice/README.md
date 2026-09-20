# SPICE decks (tested with ngspice 42)

| File | Purpose | Result |
|---|---|---|
| `diamond_pfet.lib` | Level-1 models [nagel1973] of enhancement- and depletion-mode hydrogen-terminated diamond p-channel transistors | placeholder parameters matching `adamas.logic` |
| `ed_inverter.cir` | Enhancement/depletion inverter, DC sweep | switching point near −2.2 V, low level −35 mV |
| `ring_oscillator.cir` | 5-stage ring oscillator, transient | see the period printed by `.measure`; compare with `adamas.digital.EDGate(fanout=1)` |

```bash
sudo apt install -y ngspice
ngspice -b ed_inverter.cir
ngspice -b ring_oscillator.cir | grep -E "^(period|iavg)"
```

Rails are negative, as in the laboratory, while the Python figures plot magnitudes. The model cards are **not fits to measured devices**; fitting them to published curves ([liu2014], [liu2017], [kawarada2014]) is experiment S-5 and the first task of the process design kit in `docs/expert/E2_process_integration_and_pdk.md`.
