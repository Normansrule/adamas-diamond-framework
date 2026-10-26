import re
from pathlib import Path

from adamas import paper

ROOT = Path(__file__).resolve().parents[1]


import pytest


@pytest.mark.parametrize("doc", ["adamas.tex", "talk.tex", "poster.tex"])
def test_every_macro_in_the_documents_is_generated(doc):
    n = paper.numbers()
    used = set(re.findall(r"\\([A-Z][A-Za-z]+)", (ROOT / "paper" / doc).read_text(encoding="utf-8")))
    known_latex = {"LaTeX", "Lambda", "Omega", "Huge", "Large", "Rightarrow"}   # LaTeX and Greek macros
    assert used - known_latex <= set(n), sorted(used - set(n) - known_latex)


def test_headline_numbers_match_the_models():
    n = paper.numbers()
    assert n["FcohPublished"] == "0.998" and float(n["FcohLow"]) < 0.67 + 0.2 and float(n["FcohLow"]) > 0.67   # 0.67 is below the range
    assert float(n["LossGaN"]) < float(n["LossSiC"]) < float(n["LossDiamond"]) < float(n["LossSi"])
    assert float(n["LossDiamondHot"]) < float(n["LossSiCHot"]) and float(n["PowerRatioRoom"]) < 1 < float(n["PowerRatioHot"])
    assert int(n["RSADistance"]) > 40


def test_every_citation_resolves():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from refs_common import load
    keys = {r.key for r in load()}
    cites = set(k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", (ROOT / "paper" / "adamas.tex").read_text()) for k in c.split(","))
    assert cites <= keys, sorted(cites - keys)
