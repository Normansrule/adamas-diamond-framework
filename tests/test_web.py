"""Web front end: JavaScript simulation modules (node --test), DIA-4 emulator versus Verilog, and page/id consistency."""
import json
import random
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
NODE = shutil.which("node")


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_javascript_simulation_modules():
    out = subprocess.run([NODE, "--test", "tests/sim.test.mjs"], cwd=WEB, capture_output=True, text=True)
    assert out.returncode == 0, out.stdout[-2000:]


@pytest.mark.skipif(NODE is None or shutil.which("iverilog") is None, reason="node or iverilog missing")
def test_dia4_emulator_matches_verilog_on_random_programs(tmp_path):
    d = ROOT / "circuits" / "digital"
    exe = tmp_path / "trace"
    subprocess.run(["iverilog", "-o", str(exe), str(d / "dia4.v"), str(d / "dia4_trace_tb.v")], check=True)
    rng = random.Random(4)
    js = tmp_path / "run.mjs"
    js.write_text(f"import * as c from '{(WEB / 'assets/sim/dia4.js').as_uri()}';\n"
                  "const rom = JSON.parse(process.argv[2]); let s = c.reset();\n"
                  "for (let k = 0; k < 40; k++) { s = c.step(s, rom); console.log(`${s.pc} ${s.acc} ${s.out} ${s.carry}`); }\n")
    for trial in range(25):
        rom = [rng.randrange(256) if rng.random() < 0.8 else (rng.choice([0x70, 0x80, 0xA0, 0xB0]) | rng.randrange(16)) for _ in range(16)]
        (tmp_path / "rom.hex").write_text("\n".join(f"{b:02x}" for b in rom) + "\n")
        hw = subprocess.run(["vvp", str(exe)], cwd=tmp_path, capture_output=True, text=True, check=True).stdout.split("\n")
        hw = [l for l in hw if re.fullmatch(r"\d+ \d+ \d+ [01x]", l.strip())]
        sw = subprocess.run([NODE, str(js), json.dumps(rom)], capture_output=True, text=True, check=True).stdout.split("\n")[:40]
        # the return stack is uninitialized in hardware (x) until written, so compare only while hardware is fully defined
        for k, (h, s) in enumerate(zip(hw, sw)):
            if "x" in h:
                break
            assert h.strip() == s.strip(), f"trial {trial} cycle {k}: verilog {h} vs js {s}, rom {rom}"


def test_every_element_id_used_by_page_scripts_exists():
    for page in list(WEB.glob("*.html")) + list(WEB.glob("labs/*.html")):
        html = page.read_text(encoding="utf-8")
        ids = set(re.findall(r'id="([^"]+)"', html))
        used = set(re.findall(r"""\$\(['"]([\w-]+)['"]\)""", html)) | set(re.findall(r"""getElementById\(['"]([\w-]+)['"]\)""", html))
        missing = used - ids
        assert not missing, f"{page.name}: script uses missing ids {sorted(missing)}"


def test_site_builds(tmp_path):
    from adamas import site
    out = site.build(tmp_path / "site")
    for need in ("index.html", "explorer.html", "labs/qubit.html", "labs/heat.html", "labs/cpu.html", "labs/qec.html",
                 "labs/lattice.html", "labs/fab.html", "labs/globe.html", "labs/stack.html", "labs/photon.html", "labs/wafer.html", "gallery.html", "course/lesson-6.html", "og.png", "data/site.json", "assets/style.css"):
        assert (out / need).exists(), need
    data = json.loads((out / "data" / "site.json").read_text())
    assert data["numbers"]["references"] >= 500 and len(data["references"]) >= 30


@pytest.mark.skipif(NODE is None or not (WEB / "node_modules" / "jsdom").exists(), reason="run: cd web && npm install")
def test_every_page_runs_headless_without_errors(tmp_path):
    from adamas import site
    out = site.build(tmp_path / "site")
    r = subprocess.run([NODE, "tests/smoke_all.mjs", str(out)], cwd=WEB, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_power_lab_javascript_matches_python(tmp_path):
    from adamas import converter, site
    data = site.power_data()
    (tmp_path / "p.json").write_text(json.dumps(data))
    js = tmp_path / "run.mjs"
    js.write_text(f"import * as C from '{(WEB / 'assets/sim/converter.js').as_uri()}'; import fs from 'node:fs';\n"
                  f"const D = JSON.parse(fs.readFileSync('{tmp_path / 'p.json'}','utf8')); const out = {{}};\n"
                  "for (const [n, m] of Object.entries(D)) out[n] = [300, 450].map(t => C.switchLoss(m, { bv: 1200, v: 800, i: 300, f: 2e4, tK: t }).pTotal);\n"
                  "console.log(JSON.stringify(out));")
    got = json.loads(subprocess.run([NODE, str(js)], capture_output=True, text=True, check=True).stdout)
    for name, m in data.items():
        for k, t in enumerate((300.0, 450.0)):
            ref = converter.material_switch(m["key"], 1200, 800, 300, 2e4, t_k=t, measured=m["measured"]).p_total_w
            assert abs(got[name][k] / ref - 1) < 0.01, (name, t, got[name][k], ref)


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_machine_builder_javascript_matches_python(tmp_path):
    from adamas import resource
    t = resource.table()
    (tmp_path / "t.json").write_text(json.dumps(t))
    cases = [(100, 1e6, 100.0, 1000.0), (1000, 1e9, 1000.0, 1000.0), (6000, 3e9, 3000.0, 100.0), (6000, 3e9, 450.0, 1000.0)]
    js = tmp_path / "run.mjs"
    js.write_text(f"import * as R from '{(WEB / 'assets/sim/resource.js').as_uri()}'; import fs from 'node:fs';\n"
                  f"const T = JSON.parse(fs.readFileSync('{tmp_path / 't.json'}','utf8'));\n"
                  f"console.log(JSON.stringify({json.dumps(cases)}.map(([n,s,tr,t2]) => R.estimate(T, {{nLogical:n, steps:s, tReadUs:tr, t2MemMs:t2}}))));")
    got = json.loads(subprocess.run([NODE, str(js)], capture_output=True, text=True, check=True).stdout)
    for (n, s, tr, t2), g in zip(cases, got):
        e = resource.estimate(n, s, tr, t2, t=t)
        assert g["distance"] == e.distance and abs(g["runtimeHours"] / e.runtime_hours - 1) < 1e-9 and abs(g["lam"] - e.lam) < 1e-9
