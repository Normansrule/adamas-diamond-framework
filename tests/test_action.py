"""Equations in action, the desktop app, and the installable web app."""
import json
import math
import shutil
import sys
from pathlib import Path

import pytest

from adamas import __version__, action

ROOT = Path(__file__).resolve().parents[1]


def _close(a, b):
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(_close(x, y) for x, y in zip(a, b))
    if isinstance(a, float) or isinstance(b, float):
        return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)
    return a == b


def test_golden_values_are_current():
    """web/tests/action_golden.json (what the JavaScript is tested against) must equal the package's values."""
    stored = json.loads((ROOT / "web" / "tests" / "action_golden.json").read_text())
    fresh = json.loads(json.dumps(action.golden()))
    assert stored.keys() == fresh.keys()
    for k in fresh:
        assert _close(stored[k], fresh[k]), f"{k}: run make action-golden"


def test_scenes_are_complete_and_sourced():
    sys.path.insert(0, str(ROOT / "tools"))
    from refs_common import load
    keys = {r.key for r in load()}
    from adamas.experiments import EXPERIMENTS
    ids = {e["id"] for e in EXPERIMENTS}
    assert len(action.SCENES) == 14 and len({s["id"] for s in action.SCENES}) == 14
    assert {s["exp"] for s in action.SCENES if s["exp"]} == ids            # every experiment has its equation
    for s in action.SCENES:
        assert s["group"] in action.GROUPS and set(s["levels"]) == {"k", "s", "r"}
        assert all(r in keys for r in s["refs"]), s["id"]
        vkeys = [v["key"] for v in s["vars"]]
        assert s["auto"] in vkeys and f'data-v="{s["auto"]}"' in s["html"], s["id"]
        for v in s["vars"]:
            if "choices" in v:
                assert v["value"] in [c[1] for c in v["choices"]]
            else:
                assert v["min"] <= v["value"] <= v["max"] and v["step"] > 0, (s["id"], v["key"])
        assert (ROOT / "web" / s["lab"].split("#")[0]).exists() or s["lab"].startswith("explorer"), s["lab"]


def test_equations_doc_is_current():
    assert (ROOT / "docs" / "EQUATIONS_IN_ACTION.md").read_text(encoding="utf-8") == action.to_markdown(), "run adamas build docs"


def test_site_data_carries_scenes_with_experiment_steps():
    d = action.to_json()
    a1 = next(s for s in d["scenes"] if s["id"] == "odmr")
    assert a1["experiment"]["id"] == "A1" and len(a1["experiment"]["steps"]) >= 4
    assert set(d["materials"]) >= {"Si", "4H-SiC", "GaN", "Diamond"} and d["materials"]["Diamond"]["carrier"] == "holes"


def test_app_versions_and_manifest():
    pkg = json.loads((ROOT / "desktop" / "package.json").read_text())
    assert pkg["version"] == __version__, "bump desktop/package.json with the release"
    names = [pkg["build"][t]["artifactName"] for t in ("nsis", "portable", "dmg", "appImage", "deb")]
    page = (ROOT / "web" / "download.html").read_text(encoding="utf-8")
    for n in names:                                  # the download page links the exact file names the builder writes
        stem = n.split("${arch}")[0]
        assert stem in page, stem
    man = json.loads((ROOT / "web" / "manifest.webmanifest").read_text())
    assert man["display"] == "standalone" and any(i.get("purpose") == "maskable" for i in man["icons"])
    assert "__ADAMAS_VERSION__" in (ROOT / "web" / "sw.js").read_text()


def test_icons_draw():
    pytest.importorskip("PIL")
    from adamas import icons
    im = icons.draw(64)
    assert im.size == (64, 64) and im.getpixel((32, 30))[2] > 200      # the gem is drawn in the middle


def test_site_build_installable_and_offline(tmp_path):
    from adamas import site
    out = site.build(tmp_path / "s")
    idx = (out / "index.html").read_text(encoding="utf-8")
    assert 'rel="manifest"' in idx and (out / "assets" / "icons" / "icon-512.png").exists()
    assert __version__ in (out / "sw.js").read_text()
    lab = (out / "labs" / "qubit.html").read_text(encoding="utf-8")
    assert 'href="../manifest.webmanifest"' in lab
    if not (ROOT / "web" / "node_modules" / "plotly.js-dist-min").exists():
        pytest.skip("offline build needs: cd web && npm ci")
    files = site.vendor(out)
    assert "vendor/three/three.module.js" in files and any(f.endswith(".woff2") for f in files)
    for p in list(out.rglob("*.html")) + [out / "assets" / "style.css"]:
        if "vendor" not in p.parts:
            t = p.read_text(encoding="utf-8")
            assert "cdn.jsdelivr.net" not in t and "cdn.plot.ly" not in t and "fonts.googleapis.com" not in t, p
    shutil.rmtree(out)
