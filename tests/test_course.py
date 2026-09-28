import re
from pathlib import Path

import pytest

from adamas.course import LESSONS

ROOT = Path(__file__).resolve().parents[1]


def test_lessons_are_well_formed():
    assert [L["id"] for L in LESSONS] == list(range(1, len(LESSONS) + 1))
    for L in LESSONS:
        assert len(L["quiz"]) == 4 and all(0 <= q["a"] < len(q["o"]) for q in L["quiz"])
        for _, p in L["read"]:
            assert (ROOT / p).exists(), p
        assert (ROOT / "web" / L["lab"][0].split("#")[0]).exists() or L["lab"][0].startswith("explorer")
        assert all(re.search(r"\[[a-z]+\d{4}[a-z]*\]", q["why"]) or "chapter" in q["why"].lower() for q in L["quiz"]), L["title"]


def test_lesson_code_runs():
    import contextlib
    import io
    for L in LESSONS:
        ns = {}
        with contextlib.redirect_stdout(io.StringIO()):
            for cell in L["code"]:
                exec(cell, ns)


def test_notebooks_match_course_and_execute():
    nbformat = pytest.importorskip("nbformat")
    nbclient = pytest.importorskip("nbclient")
    pytest.importorskip("ipykernel")
    from adamas.course import notebook
    for L in LESSONS:
        path = ROOT / "notebooks" / f"lesson_{L['id']}.ipynb"
        nb = nbformat.read(str(path), as_version=4)
        assert [c.source for c in nb.cells] == [c.source for c in notebook(L).cells], f"{path.name} is stale: run make notebooks"
    nb = nbformat.read(str(ROOT / "notebooks" / "lesson_5.ipynb"), as_version=4)
    nbclient.NotebookClient(nb, timeout=120, kernel_name="python3").execute()
