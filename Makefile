# ADAMAS developer shortcuts. Run inside the conda environment:  conda activate adamas
PY := python
.PHONY: all test figures refs verify apply-verify spice rtl synth layout clean

all: refs test figures

test:            ## unit tests plus citation check (use "python -m pytest", not a bare pytest on PATH)
	$(PY) -m pytest -q

figures:         ## regenerate all 36 figures into docs/img/
	$(PY) examples/make_all_figures.py

refs:            ## rebuild references.bib and REFERENCES.md, then check every [bibkey]
	cd tools && $(PY) build_refs.py && $(PY) check_citations.py

verify:          ## Crossref verification (needs internet; resumable). Pass your address: make verify MAILTO=you@school.edu
	cd tools && $(PY) verify_refs.py --mailto $(or $(MAILTO),set-your-email@example.org)

apply-verify:    ## store DOIs of PASS rows, promote them to verified, rebuild the bibliography
	cd tools && $(PY) apply_verification.py && $(PY) build_refs.py && $(PY) check_citations.py

spice:           ## inverter sweep and ring oscillator in ngspice
	cd circuits/spice && ngspice -b ed_inverter.cir > /dev/null && ngspice -b ring_oscillator.cir | grep -E "^(period|iavg)"

rtl:             ## behavioral simulation of the DIA-4 processor (countdown program, then nested CALL/RET)
	cd circuits/digital && for tb in dia4_tb dia4_call_tb; do iverilog -o /tmp/dia4 dia4.v $$tb.v && vvp /tmp/dia4 | grep -E "PASS|FAIL"; done

synth:           ## synthesize DIA-4 onto the diamond cell library, then gate-level simulation
	cd circuits/digital && yosys -q -l synth.log synth.ys && grep -A7 "Number of cells" synth.log | tail -8 \
	&& for tb in dia4_tb dia4_call_tb; do iverilog -o /tmp/dia4g dia4_netlist.v cells_sim.v $$tb.v && vvp /tmp/dia4g | grep -E "PASS|FAIL"; done

layout:          ## write the PDK-0 monitor die GDS
	$(PY) circuits/layout/make_pdk0_monitor.py

clean:
	rm -rf .pytest_cache build dist *.egg-info circuits/digital/synth.log
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
