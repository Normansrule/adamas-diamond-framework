# Developing ADAMAS from an Ubuntu terminal

Works on Ubuntu 24.04 and 26.04, natively or under Windows Subsystem for Linux 2 (WSL2). Commands are grouped so you can paste one block at a time. Lines starting with `#` are comments.

## 0 · One-time system packages

```bash
sudo apt update
sudo apt install -y git make build-essential unzip curl \
    ngspice iverilog yosys gtkwave klayout
# ngspice  : circuit simulation           iverilog/gtkwave : Verilog simulation and waveforms
# yosys    : logic synthesis              klayout          : mask layout viewer/editor (needs a display; WSLg works)
ngspice --version | head -2 ; yosys -V ; iverilog -V | head -1
```

If a package is missing on your release, skip it: the Python package and tests do not need it (those tests skip automatically).

## 1 · Get the code into your home directory

From the zip this project was delivered as (WSL2: your Windows Downloads folder is under `/mnt/c`):

```bash
mkdir -p ~/projects && cd ~/projects
unzip /mnt/c/Users/$USER/Downloads/adamas-diamond-framework.zip     # adjust the path if needed
cd adamas-diamond-framework
git log --oneline | head -3
```

Keep the repository inside the Linux file system (`~/projects`), not under `/mnt/c`; builds and git are much faster there.

## 2 · Python environment (Miniforge / conda)

```bash
# install Miniforge only if "conda" is not found:
# curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
# bash Miniforge3-Linux-x86_64.sh -b -p ~/miniforge3 && ~/miniforge3/bin/conda init bash && exec bash

conda env create -f environment.yml        # creates the "adamas" environment and installs the package in editable mode
conda activate adamas
python -c "import adamas, sys; print('adamas', adamas.__version__, 'on python', sys.version.split()[0])"
```

## 3 · Verify everything

```bash
python -m pytest -q            # always "python -m pytest": a stray ~/.local/bin/pytest can shadow the environment's
make refs                      # rebuild the bibliography and check every [bibkey]
make figures                   # regenerate all 37 figures
make spice                     # ngspice: inverter + ring oscillator (prints the oscillation period)
make rtl                       # DIA-4 behavioral simulation  -> PASS
make synth                     # Yosys synthesis + gate-level simulation -> cell counts, PASS
```

Expected: 47 tests pass; `make synth` reports 190 to 220 cells (varies with Yosys version) (13 DFF, 34 INV, 49 NAND2, 100 NOR2, 24 NOR3).

## 4 · Publish to GitHub

Create an empty repository named `adamas-diamond-framework` on GitHub first (no README, no license). Then, using the SSH host alias for the account:

```bash
git config user.name  "Aleksander Norman"
git config user.email "YOUR_GITHUB_NOREPLY_EMAIL"
git commit --amend --reset-author --no-edit          # only if you want your identity on the delivered commits
git remote add origin git@github-normansrule:Normansrule/adamas-diamond-framework.git
ssh -T git@github-normansrule                        # should greet you as Normansrule
git push -u origin main
git tag -a v0.2.0 -m "ADAMAS v0.2.0: expert track" && git push origin v0.2.0
```

Pushing over SSH avoids the token-scope problem that blocks `.github/workflows/` files over HTTPS.

## 5 · Daily development loop

```bash
cd ~/projects/adamas-diamond-framework && conda activate adamas
git switch -c feature/my-change                      # one branch per change
# ... edit ...
python -m pytest -q && make refs                     # tests + citation check must pass
git add -A && git commit -m "Describe the change"
git push -u origin feature/my-change                 # then open a pull request on GitHub
```

### Add a reference

```bash
echo 'smith2027 | Smith, J. | 2027 | Title here | Journal Name | 12, 345 | lit | K' >> references/refs_c.psv
make refs
```

### Verify the reference list against Crossref (needs internet; resumable)

```bash
make verify MAILTO=you@school.edu          # a real address puts you in Crossref's faster "polite pool"
python tools/verify_refs.py --retry-checks --mailto you@school.edu     # redo rows that were CHECK or ERROR
python tools/show_checks.py                # readable list of everything still needing review
make apply-verify                          # stores DOIs in references/dois.psv, promotes PASS rows to verified
```

The run backs off automatically on HTTP 429 (rate limit). A `CHECK` row is a request for human review, not a verdict: fix the `.psv` line if the reference is wrong, or record your decision in `references/verification_overrides.psv` (for example `NOT-INDEXED` for a thesis or technical memo).

### Add a figure

```bash
# 1. write fig_something(out) in adamas/figures_expert.py, ending with  return _finish(fig, out, "figNN_name.png", "[bibkeys]")
# 2. append it to ALL in that file
make figures && git add docs/img/figNN_name.png
```

### Work on the circuits

```bash
cd circuits/spice   && ngspice ed_inverter.cir                 # interactive: plots the transfer curve
cd ../digital       && iverilog -o /tmp/dia4 dia4.v dia4_tb.v && vvp /tmp/dia4
yosys -p "read_verilog dia4.v; synth -top dia4 -flatten; dfflegalize -cell \$_DFF_P_ 01; opt; \
          dfflibmap -liberty adamas_ed.lib; abc -liberty adamas_ed.lib; stat -liberty adamas_ed.lib"
```

### Optional: place-and-route tools for project P-2

```bash
# OpenROAD and OpenLane are easiest through Docker (Docker Desktop with WSL integration, or docker.io on native Ubuntu)
docker pull openroad/orfs:latest
# follow docs/expert/E2_process_integration_and_pdk.md, project P-2, for the technology files you need to write first
```

## 6 · Suggested order of work

Follow `docs/expert/E8_projects_and_thesis_topics.md`. The laptop-only path is: S-1 (step 3 above) → D-1 (extend DIA-4) → P-3 (fit SPICE models) → Q-1 (non-Markovian gate model) → X-1 (surface-code simulator).
