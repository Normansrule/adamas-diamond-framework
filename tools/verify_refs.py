"""Verify every reference against the public Crossref API and fetch its DOI.

Usage:  python tools/verify_refs.py [--only K] [--limit 50]

For each article, the script asks Crossref for the best bibliographic match and compares the
title (fuzzy), the year, and the first author's family name. It writes references/verification_report.csv
with the matched DOI and a PASS / CHECK flag. Nothing in the database is changed automatically; a human
reviews every CHECK row. Needs internet access and only the Python standard library.
"""
from __future__ import annotations
import argparse
import csv
import difflib
import json
import time
import urllib.parse
import urllib.request
from refs_common import ROOT, load

API = "https://api.crossref.org/works"


def query(ref) -> dict | None:
    q = urllib.parse.urlencode({"query.bibliographic": f"{ref.title} {ref.authors.split(';')[0]} {ref.year}",
                                "rows": 1, "mailto": "set-your-email@example.org"})
    with urllib.request.urlopen(f"{API}?{q}", timeout=30) as resp:
        items = json.load(resp)["message"]["items"]
    return items[0] if items else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["K", "V"], help="check only references with this status")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    refs = [r for r in load() if r.locator not in ("book", "report") and "ind" not in r.tags]
    if args.only:
        refs = [r for r in refs if r.status == args.only]
    if args.limit:
        refs = refs[: args.limit]
    rows = []
    for i, r in enumerate(refs, 1):
        try:
            hit = query(r)
        except Exception as exc:  # network errors should not kill a long run
            rows.append([r.key, "ERROR", "", "", str(exc)])
            continue
        if not hit:
            rows.append([r.key, "CHECK", "", "", "no match"])
            continue
        title = (hit.get("title") or [""])[0]
        year = str((hit.get("issued", {}).get("date-parts") or [[None]])[0][0])
        family = (hit.get("author") or [{}])[0].get("family", "")
        sim = difflib.SequenceMatcher(None, r.title.lower(), title.lower()).ratio()
        ok = sim > 0.85 and abs(int(year or 0) - int(r.year)) <= 1 and family[:4].lower() in r.authors.lower()
        rows.append([r.key, "PASS" if ok else "CHECK", hit.get("DOI", ""), f"{sim:.2f}", f"{family} {year}: {title}"])
        print(f"[{i}/{len(refs)}] {r.key}: {'PASS' if ok else 'CHECK'}")
        time.sleep(0.2)  # be polite to the free API
    out = ROOT / "references" / "verification_report.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows([["key", "result", "doi", "title_similarity", "crossref_match"], *rows])
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
