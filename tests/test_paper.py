import re
from pathlib import Path

from adamas import paper

ROOT = Path(__file__).resolve().parents[1]


def test_every_macro_in_the_manuscript_is_generated():
    n = paper.numbers()
    used = set(re.findall(r"\\([A-Z][A-Za-z]+)", (ROOT / "paper" / "adamas.tex").read_text(encoding="utf-8")))
    generated = set(n)
    known_latex = {"LaTeX", "Lambda", "Omega"}      # Greek letters in math mode
    assert used - known_latex <= generated, sorted(used - generated - known_latex)


def test_headline_numbers_match_the_models():
    n = paper.numbers()
    assert n["FcohPublished"] == "0.998" and n["qForSixtySeven"] == "0.75"
    assert float(n["LossDiamond"]) < float(n["LossGaN"]) < float(n["LossSiC"]) < float(n["LossSi"])
    assert int(n["RSADistance"]) > 40


def test_every_citation_resolves():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from refs_common import load
    keys = {r.key for r in load()}
    cites = set(k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", (ROOT / "paper" / "adamas.tex").read_text()) for k in c.split(","))
    assert cites <= keys, sorted(cites - keys)
