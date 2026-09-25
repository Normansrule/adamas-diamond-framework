import re
import shutil
import subprocess
import xml.dom.minidom

from adamas import explorer, poster


def test_explorer_html_builds_and_js_parses(tmp_path):
    html = explorer.build_html()
    assert html.count("<section") == 7 and "plotly" in html
    js = re.search(r"<script>(const MAT=.*)</script></body>", html, re.S).group(1)
    if shutil.which("node"):
        f = tmp_path / "x.js"; f.write_text(js)
        out = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
        assert out.returncode == 0, out.stderr


def test_explorer_javascript_matches_python_at_spot_values(tmp_path):
    if not shutil.which("node"):
        return
    from adamas import doping, materials, power
    html = explorer.build_html()
    js = re.search(r"<script>(const MAT=.*)</script></body>", html, re.S).group(1)
    stub = ("const store={fomCarrier:'p',ronT:'300',ionN:'17',odmrB:'3',odmrTh:'35',odmrLw:'1.5',gT2:'600',gQ:'1',gDQ:false,convApp:'ev',qCycle:'-3',qYield:'50',qPitch:'1'};"
            "global.document={querySelectorAll:()=>[],getElementById:id=>({value:store[id],checked:store[id]===true,set innerHTML(v){},set textContent(v){},dataset:{}})};"
            "global.Plotly={react:()=>{}};")
    probe = "console.log(JSON.stringify({b:fom(MAT.Diamond,'p').BFOM/fom(MAT.Si,'n').BFOM,r:ron(MAT.Diamond,2608,'p'),i:ionized(0.37,1e17,300)}));"
    f = tmp_path / "run.js"; f.write_text(stub + js + probe)
    out = subprocess.run(["node", str(f)], capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1]
    import json
    got = json.loads(out)
    assert abs(got["b"] / materials.normalized_foms()["Diamond"]["BFOM"] - 1) < 1e-6
    assert abs(got["r"] / power.ron_sp_mohm_cm2(materials.MATERIALS["Diamond"], 2608, "p") - 1) < 1e-6
    assert abs(got["i"] / doping.ionized_fraction(doping.DOPANTS["C:B"], 1e17) - 1) < 0.15      # effective-mass convention differs slightly


def test_poster_is_well_formed_svg():
    xml.dom.minidom.parseString(poster.build_svg())
