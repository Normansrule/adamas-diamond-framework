# ADAMAS developer shortcuts. Run inside the conda environment:  conda activate adamas
PY := python
.PHONY: all test figures animations loop-gif trailer notebooks traveler experiments examples glossary validation paper talk poster explorer orfs site serve web-test refs verify apply-verify spice rtl synth layout place action-golden app desktop desktop-check clean

all: refs test figures

test:            ## unit tests plus citation check (use "python -m pytest", not a bare pytest on PATH)
	$(PY) -m pytest -q

figures:         ## regenerate all 53 figures and the equations animation into docs/img/
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

place:           ## LEF, timed Liberty, and a placed DIA-4 (GDS + DEF) on PDK-0
	$(PY) circuits/digital/place.py

animations:      ## every animated GIF in docs/img (about a minute)
	$(PY) -c "from adamas.animations import make_all; make_all('docs/img')"

loop-gif:        ## record the equation-in-the-loop GIF for the README from an offline site build (needs Playwright: npm i -g playwright)
	$(PY) -m adamas.site /tmp/adamas-loop-site --offline && rm -rf /tmp/adamas-loop-frames && mkdir -p /tmp/adamas-loop-frames
	($(PY) -m http.server -d /tmp/adamas-loop-site 8765 >/dev/null 2>&1 & echo $$! > /tmp/adamas-loop.pid); sleep 1
	NODE_PATH=$$(npm root -g) node tools/record_loop.mjs http://localhost:8765 /tmp/adamas-loop-frames; s=$$?; kill $$(cat /tmp/adamas-loop.pid); exit $$s
	$(PY) tools/make_loop_gif.py /tmp/adamas-loop-frames docs/img/anim_equation_loop.gif

explorer:        ## rebuild docs/index.html (interactive explorer) and the poster
	$(PY) -c "from adamas.explorer import write; write('docs/index.html')" && $(PY) -c "from adamas.poster import write; write()"

orfs:            ## install the PDK-0 platform + DIA-4 into ~/orfs and run OpenROAD in Docker (host shell, not inside a container)
	bash circuits/digital/openroad/run_orfs.sh

site:            ## build the website (landing page, every lab, explorer) into site/
	$(PY) -m adamas.site site

serve: site      ## build and serve the website at http://localhost:8000
	$(PY) -m http.server -d site 8000

web-test: site   ## JavaScript unit tests and headless smoke test of every page (needs: cd web && npm install)
	cd web && npm test && npm run smoke

trailer:         ## render the 20-second trailer video docs/img/trailer.mp4 (needs ffmpeg, about 45 s)
	$(PY) -m adamas.trailer docs/img/trailer.mp4

notebooks:       ## regenerate the six course notebooks from adamas/course.py
	$(PY) -c "from adamas.course import write_notebooks; write_notebooks()"

traveler:        ## regenerate docs/process/TRAVELER.md from adamas/traveler.py
	$(PY) -c "from adamas.traveler import write; write()"

experiments:     ## regenerate docs/experiments/EXPERIMENTS.md from adamas/experiments.py
	$(PY) -c "from adamas.experiments import write; write()"

examples:        ## regenerate the practice datasets in docs/data/examples
	$(PY) -c "from adamas.fitting import example_datasets; example_datasets()"

glossary:        ## regenerate docs/GLOSSARY.md
	$(PY) -c "from adamas.glossary import write; write()"

paper:           ## numbers from the package, then the preprint PDF (needs pdflatex, latexmk)
	$(PY) -m adamas.paper && cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error adamas.tex && latexmk -c

validation:      ## regenerate docs/VALIDATION.md (validation matrix and uncertainty summary)
	$(PY) -c "from adamas.validation import write; write()"

talk:            ## 12-slide Beamer talk, numbers from the package (paper/talk.pdf)
	$(PY) -m adamas.paper && cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error talk.tex && latexmk -c talk.tex && rm -f talk.nav talk.snm

poster:          ## A0 conference poster with QR code (paper/poster.pdf)
	$(PY) -m adamas.paper && cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error poster.tex && latexmk -c poster.tex

xzzx:            ## rerun the native XZZX study (about three minutes) into docs/data/xzzx_native.json
	rm -f docs/data/xzzx_native.json && $(PY) -c "from adamas.xzzx_native import cached_study; cached_study()"

docs:            ## regenerate traveler, experiments, glossary, validation, and the README key-findings block
	$(PY) -m adamas build docs

resource-biased: ## rebuild the biased-noise resource tables for both codes (about 2 minutes)
	$(PY) -c "from adamas import resource as R; [R.table_for(m, refresh=True) for m in ('css_biased', 'xzzx_biased')]"

resource-bias:   ## rebuild the native-circuit tables at bias 0.5 and 10 for both codes (about 4 minutes)
	$(PY) -c "from adamas import resource as R; [R.table_eta(c, e, refresh=True) for c in ('css', 'xzzx') for e in (0.5, 10.0)]"

action-golden:   ## Python values the browser physics of Equations in Action is tested against (web/tests/action_golden.json)
	$(PY) -c "from adamas.action import write_golden; write_golden()"

app:             ## open the website as a local app (native window with pip install -e ".[app]")
	$(PY) -m adamas app

desktop:         ## build the desktop app for this system into desktop/dist (needs: cd web && npm ci)
	$(PY) -m adamas.site desktop/site --offline && $(PY) -m adamas.icons desktop/build/icon.png 1024
	cd desktop && npm ci && npx electron-builder --publish never

desktop-check:   ## open every page in the desktop app and fail on any script error (Linux needs xvfb)
	$(PY) -m adamas.site desktop/site --offline && cd desktop && npm ci && xvfb-run -a npx electron . --check --no-sandbox

clean:
	rm -rf .pytest_cache build dist *.egg-info circuits/digital/synth.log
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
