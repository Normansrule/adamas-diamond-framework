# ADAMAS developer shortcuts. Run inside the conda environment:  conda activate adamas
PY := python
.PHONY: all test figures refs verify spice rtl synth clean

all: refs test figures

test:            ## unit tests plus citation check (use "python -m pytest", not a bare pytest on PATH)
	$(PY) -m pytest -q

figures:         ## regenerate all 25 figures into docs/img/
	$(PY) examples/make_all_figures.py

refs:            ## rebuild references.bib and REFERENCES.md, then check every [bibkey]
	cd tools && $(PY) build_refs.py && $(PY) check_citations.py

verify:          ## Crossref verification of the reference list (needs internet)
	cd tools && $(PY) verify_refs.py

spice:           ## inverter sweep and ring oscillator in ngspice
	cd circuits/spice && ngspice -b ed_inverter.cir > /dev/null && ngspice -b ring_oscillator.cir | grep -E "^(period|iavg)"

rtl:             ## behavioral simulation of the DIA-4 processor
	cd circuits/digital && iverilog -o /tmp/dia4 dia4.v dia4_tb.v && vvp /tmp/dia4

synth:           ## synthesize DIA-4 onto the diamond cell library, then gate-level simulation
	cd circuits/digital && yosys -q -l synth.log synth.ys && grep -A7 "Number of cells" synth.log | tail -8 \
	&& iverilog -o /tmp/dia4g dia4_netlist.v cells_sim.v dia4_tb.v && vvp /tmp/dia4g

clean:
	rm -rf .pytest_cache build dist *.egg-info circuits/digital/synth.log
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
