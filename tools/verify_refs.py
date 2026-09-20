"""Verify every reference against the public Crossref API and fetch its DOI.

Usage:  python tools/verify_refs.py [--only K] [--limit 50] [--fresh] [--mailto you@example.org]

For each article the script asks Crossref for the three best bibliographic matches, keeps the one whose title is
closest, and compares title (fuzzy), year, first-author family name, and volume. It appends one row per reference to
references/verification_report.csv as it goes, so an interrupted run loses nothing and a re-run resumes where it
stopped (use --fresh to start over). Nothing in the database is changed automatically; a human reviews every CHECK row.
Needs internet access and only the Python standard library.
"""
from __future__ import annotations
import argparse
import csv
import difflib
import html
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from refs_common import ROOT, load

API = "https://api.crossref.org/works"
HEADER = ["key", "result", "doi", "title_similarity", "problems", "crossref_match"]


def _norm(text: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", "", text or ""))
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).strip()


def _year(hit: dict) -> int | None:
    for field in ("published-print", "published-online", "issued", "published"):
        parts = (hit.get(field) or {}).get("date-parts") or [[None]]
        if parts and parts[0] and parts[0][0]:
            try:
                return int(parts[0][0])
            except (TypeError, ValueError):
                continue
    return None


def compare(ref, hit: dict) -> tuple[bool, float, list[str]]:
    """Pure function (no network): returns (ok, title similarity, list of problems)."""
    problems: list[str] = []
    sim = difflib.SequenceMatcher(None, _norm(ref.title), _norm((hit.get("title") or [""])[0])).ratio()
    if sim <= 0.85:
        problems.append("title differs")
    year = _year(hit)
    if year is None:
        problems.append("Crossref has no year")
    elif abs(year - int(ref.year)) > 1:
        problems.append(f"year {ref.year} vs Crossref {year}")
    family = _norm((hit.get("author") or [{}])[0].get("family", ""))
    if not family or family[:4] not in _norm(ref.authors):
        problems.append(f"first author vs Crossref '{family}'")
    ours = re.match(r"\s*(\d+)", ref.locator)
    theirs = str(hit.get("volume") or "")
    if ours and theirs and ours.group(1) != theirs:
        problems.append(f"volume {ours.group(1)} vs Crossref {theirs}")
    return (not problems, sim, problems)


def query(ref, mailto: str) -> list[dict]:
    q = urllib.parse.urlencode({"query.bibliographic": f"{ref.title} {ref.authors.split(';')[0]} {ref.year}",
                                "rows": 3, "mailto": mailto,
                                "select": "DOI,title,author,issued,published-print,published-online,volume,page,container-title"})
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": f"adamas-verify/0.2 (mailto:{mailto})"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["message"]["items"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["K", "V"], help="check only references with this status")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--fresh", action="store_true", help="ignore an existing report and start over")
    ap.add_argument("--mailto", default="set-your-email@example.org", help="contact address for Crossref's polite pool")
    args = ap.parse_args()
    refs = [r for r in load() if r.locator not in ("book", "report") and "ind" not in r.tags
            and "book" not in r.locator and "conference" not in r.locator]
    if args.only:
        refs = [r for r in refs if r.status == args.only]
    out = ROOT / "references" / "verification_report.csv"
    done: set[str] = set()
    if out.exists() and not args.fresh:
        with out.open(encoding="utf-8") as fh:
            done = {row[0] for row in csv.reader(fh) if row and row[1] != "ERROR"} - {"key"}
        kept = [row for row in csv.reader(out.open(encoding="utf-8")) if row and row[0] in done]
        with out.open("w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerows([HEADER, *kept])
    else:
        with out.open("w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerow(HEADER)
    todo = [r for r in refs if r.key not in done]
    if args.limit:
        todo = todo[: args.limit]
    counts = {"PASS": 0, "CHECK": 0, "ERROR": 0}
    for i, r in enumerate(todo, 1):
        try:
            hits = query(r, args.mailto)
            if not hits:
                row = [r.key, "CHECK", "", "", "no Crossref match", ""]
            else:
                scored = [(compare(r, h), h) for h in hits]
                (ok, sim, problems), hit = max(scored, key=lambda s: (s[0][0], s[0][1]))
                who = (hit.get("author") or [{}])[0].get("family", "")
                desc = f"{who} {_year(hit)}: {(hit.get('title') or [''])[0]} | {(hit.get('container-title') or [''])[0]} " \
                       f"{hit.get('volume', '')}, {hit.get('page', '')}"
                row = [r.key, "PASS" if ok else "CHECK", hit.get("DOI", ""), f"{sim:.2f}", "; ".join(problems), desc]
        except Exception as exc:  # a bad record or a network hiccup must never kill a long run
            row = [r.key, "ERROR", "", "", f"{type(exc).__name__}: {exc}", ""]
        counts[row[1]] += 1
        with out.open("a", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerow(row)
        print(f"[{i}/{len(todo)}] {r.key}: {row[1]}" + (f"  ({row[4]})" if row[1] != "PASS" else ""), flush=True)
        time.sleep(0.2)  # be polite to the free API
    print(f"wrote {out}  |  this run: {counts}  |  previously done: {len(done)}")


if __name__ == "__main__":
    main()
