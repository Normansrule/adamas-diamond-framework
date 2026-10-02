import json
import re
from pathlib import Path

import pytest

from adamas import cli, readme, site

ROOT = Path(__file__).resolve().parents[1]


def test_cli_commands_run(capsys):
    assert cli.main(["info"]) == 0 and "ADAMAS" in capsys.readouterr().out
    assert cli.main(["estimate", "--workload", "materials", "--readout-us", "100"]) == 0
    assert "code distance" in capsys.readouterr().out
    assert cli.main(["fit", "rabi", str(ROOT / "docs/data/examples/rabi.csv")]) == 0
    capsys.readouterr()
    assert cli.main(["findings"]) == 0
    F = json.loads(capsys.readouterr().out)
    assert float(F["UncPowerPfifty"]) < float(F["BFOMratio"].replace(",", ""))
    assert cli.main(["validate"]) == 0
    cli.main(["doctor"])                     # exit code depends on the machine; must not crash


def test_readme_findings_block_is_current():
    s = (ROOT / "README.md").read_text(encoding="utf-8")
    a, b = s.index(readme.START), s.index(readme.END) + len(readme.END)
    assert s[a:b] == readme.block(), "run: adamas build docs"


def test_navigation_and_search_cover_every_page():
    nav = (ROOT / "web/assets/site.js").read_text(encoding="utf-8")
    hrefs = set(re.findall(r"'((?:labs/|course/|paper/)?[\w-]+\.(?:html|pdf))'", nav.split("export const LINKS")[0]))
    built = {"explorer.html", "gallery.html", "glossary.html", "course/index.html"} | {f"paper/{p.name}" for p in (ROOT / "paper").glob("*.pdf")}
    for h in hrefs:
        assert (ROOT / "web" / h).exists() or h in built, h
    idx = site.search_index(); kinds = {i["kind"] for i in idx}
    assert {"page", "lab", "term", "figure", "experiment", "step", "lesson"} <= kinds
    assert {h for h in hrefs} <= {i["href"] for i in idx} | {"explorer.html", "gallery.html", "glossary.html", "course/index.html"}


@pytest.mark.skipif(not (ROOT / "CHANGELOG.md").exists(), reason="no changelog")
def test_changelog_lists_this_version():
    from adamas import __version__
    assert f"| {__version__} |" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
