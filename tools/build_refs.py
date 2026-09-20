"""Generate references/references.bib and references/REFERENCES.md from the .psv database."""
from __future__ import annotations
from refs_common import ROOT, TAG_NAMES, load


def load_dois() -> dict[str, str]:
    path = ROOT / "references" / "dois.psv"
    out: dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                k, d = [x.strip() for x in line.split("|", 1)]
                out[k] = d
    return out


DOIS = load_dois()


def bibtex(r) -> str:
    kind = "book" if r.locator == "book" else ("techreport" if r.locator == "report" else
           ("misc" if "ind" in r.tags or "arXiv" in r.venue else "article"))
    authors = " and ".join(a.strip() for a in r.authors.replace("et al.", "others").split(";"))
    fields = {"author": authors, "title": "{" + r.title + "}", "year": r.year}
    if kind == "article":
        fields["journal"] = r.venue
        if "," in r.locator and "TODO" not in r.locator:
            vol, page = [s.strip() for s in r.locator.split(",", 1)]
            fields["volume"], fields["pages"] = vol, page
        else:
            fields["note"] = r.locator
    elif kind == "book":
        fields["publisher"] = r.venue
    else:
        fields["howpublished"] = r.venue
        fields["note"] = r.locator
    if r.key in DOIS:
        fields["doi"] = DOIS[r.key]
    fields["keywords"] = ", ".join(r.tags) + f"; status={r.status}"
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields.items())
    return f"@{kind}{{{r.key},\n{body}\n}}\n"


def main() -> None:
    refs = load()
    (ROOT / "references" / "references.bib").write_text("\n".join(bibtex(r) for r in refs), encoding="utf-8")
    verified = sum(r.status == "V" for r in refs)
    out = ["# References", "",
           f"**{len(refs)} references.** {verified} are verified (marked ✅): matched against Crossref on title, year, "
           f"first author, and volume by `tools/verify_refs.py`, or checked against an online source while the "
           f"repository was built. {len(DOIS)} carry a Digital Object Identifier (DOI) fetched from Crossref; none "
           "is typed by hand, so a mistyped DOI can never point at the wrong paper. Entries marked 📚 are books, "
           "reports, conference papers, or items still awaiting review; human decisions about those are recorded in "
           "`references/verification_overrides.psv`.", "",
           "Cite in the docs and code as `[key]`. `python tools/check_citations.py` fails if a key is missing here.", ""]
    for tag, name in TAG_NAMES.items():
        group = sorted((r for r in refs if r.tags[0] == tag), key=lambda r: (r.year, r.key))
        if not group:
            continue
        out += [f"## {name} ({len(group)})", ""]
        for r in group:
            mark = "✅" if r.status == "V" else "📚"
            doi = f" [doi:{DOIS[r.key]}](https://doi.org/{DOIS[r.key]})" if r.key in DOIS else ""
            out.append(f"- {mark} **`[{r.key}]`** {r.apa()}{doi}")
        out.append("")
    (ROOT / "references" / "REFERENCES.md").write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {len(refs)} references ({verified} verified)")


if __name__ == "__main__":
    main()
