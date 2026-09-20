"""Verify every reference against the public Crossref API and fetch its DOI.

Usage:  python tools/verify_refs.py [--retry-checks] [--pause 1.0] [--only K] [--limit 50] [--fresh] [--mailto you@example.org]
        python tools/apply_verification.py      (afterwards: stores DOIs, promotes PASS rows to verified)

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
import urllib.error
import urllib.parse
import urllib.request
from refs_common import ROOT, load

API = "https://api.crossref.org/works"
HEADER = ["key", "result", "doi", "title_similarity", "problems", "crossref_match"]


def _norm(text: str) -> str:
    """Lower-case ASCII words. Crossref titles often arrive spread over several indented lines with
    <sub>/<sup>/<i> markup ("NO\n   <sub>2</sub>\n   hole"), so markup is removed and whitespace collapsed."""
    text = html.unescape(re.sub(r"\s*<[^>]+>\s*", "", text or ""))
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


def _squash(text: str) -> str:
    """Letters and digits only, so "NO 2" equals "NO2" and "(5-nanometer)^3" equals "(5-Nanometer)3"."""
    return _norm(text).replace(" ", "")


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
    theirs_title = (hit.get("title") or [""])[0]
    sim = max(difflib.SequenceMatcher(None, _norm(ref.title), _norm(theirs_title)).ratio(),
              difflib.SequenceMatcher(None, _squash(ref.title), _squash(theirs_title)).ratio())
    a, b = _norm(ref.title), _norm(theirs_title)
    shorter, longer = sorted((a, b), key=len)
    if len(shorter.split()) >= 3 and longer.startswith(shorter):
        sim = max(sim, 0.90)                 # publishers often deposit the main title without its subtitle
    if sim <= 0.85:
        problems.append("title differs")
    year = _year(hit)
    if year is None:
        problems.append("Crossref has no year")
    elif abs(year - int(ref.year)) > 1:
        problems.append(f"year {ref.year} vs Crossref {year}")
    family = _norm((hit.get("author") or [{}])[0].get("family", ""))
    ours_auth = _norm(ref.authors)
    folded = ours_auth.replace("ue", "u").replace("oe", "o").replace("ae", "a")     # Stuerner == Stürner
    if not family:
        if sim < 0.95:                       # some publishers deposit no author list; a near-exact title is enough
            problems.append("Crossref record has no authors")
    elif not any(tok[:4] in ours_auth or tok[:4] in folded for tok in family.split() if len(tok) > 2):
        # every word of the deposited family name is tried, because some records read "K Kanaya"
        problems.append(f"first author vs Crossref '{family}'")
    ours = re.match(r"\s*(\d+)", ref.locator)
    theirs = re.match(r"\s*(\d+)", str(hit.get("volume") or ""))                 # "92U" -> 92, "27-28" -> 27
    if ours and theirs and ours.group(1) != theirs.group(1):
        problems.append(f"volume {ours.group(1)} vs Crossref {theirs.group(1)}")
    return (not problems, sim, problems)


SELECT = "DOI,title,author,issued,published-print,published-online,volume,page,container-title"


def _get(params: dict, mailto: str, tries: int = 6) -> list[dict]:
    """One Crossref request with exponential backoff on HTTP 429 (rate limit) and 5xx."""
    if "@" in mailto and "example.org" not in mailto:
        params = dict(params, mailto=mailto)                    # only a real address joins the polite pool
    req = urllib.request.Request(f"{API}?{urllib.parse.urlencode(params)}",
                                 headers={"User-Agent": f"adamas-verify/0.3 (mailto:{mailto})"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)["message"]["items"]
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == tries - 1:
                raise
            wait = float(exc.headers.get("Retry-After") or 0) or 2.0 * 2 ** attempt
            print(f"    rate limited (HTTP {exc.code}); waiting {wait:.0f} s", flush=True)
            time.sleep(wait)
    return []


def query(ref, mailto: str, strategy: int = 0) -> list[dict]:
    first = ref.authors.split(";")[0].split(",")[0].strip()
    if strategy == 0:
        params = {"query.bibliographic": f"{ref.title} {first} {ref.year}", "rows": 5, "select": SELECT}
    else:                                                       # fallback: title and author as separate fields
        params = {"query.title": ref.title, "query.author": first, "rows": 5, "select": SELECT}
    return _get(params, mailto)


def load_overrides() -> dict[str, tuple[str, str]]:
    """references/verification_overrides.psv: key | verdict | note  (human decisions that outrank Crossref)."""
    path = ROOT / "references" / "verification_overrides.psv"
    out: dict[str, tuple[str, str]] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                key, verdict, note = [x.strip() for x in line.split("|", 2)]
                out[key] = (verdict, note)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["K", "V"], help="check only references with this status")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--fresh", action="store_true", help="ignore an existing report and start over")
    ap.add_argument("--pause", type=float, default=1.0, help="seconds between requests (raise it if you see rate limiting)")
    ap.add_argument("--retry-checks", action="store_true", help="also redo rows that were CHECK last time")
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
            redo = {"ERROR", "CHECK"} if args.retry_checks else {"ERROR"}
            done = {row[0] for row in csv.reader(fh) if row and row[1] not in redo} - {"key"}
        kept = [row for row in csv.reader(out.open(encoding="utf-8")) if row and row[0] in done]
        with out.open("w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerows([HEADER, *kept])
    else:
        with out.open("w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerow(HEADER)
    todo = [r for r in refs if r.key not in done]
    if args.limit:
        todo = todo[: args.limit]
    counts = {"PASS": 0, "CHECK": 0, "ERROR": 0, "REVIEWED": 0}
    overrides = load_overrides()
    for i, r in enumerate(todo, 1):
        try:
            if r.key in overrides:
                verdict, note = overrides[r.key]
                hits, row = None, [r.key, "REVIEWED", "", "", f"{verdict}: {note}", ""]
            else:
                hits = query(r, args.mailto)
                if not any(compare(r, h)[0] for h in hits):
                    time.sleep(args.pause)
                    hits = hits + query(r, args.mailto, strategy=1)
            if hits is None:
                pass
            elif not hits:
                row = [r.key, "CHECK", "", "", "no Crossref match", ""]
            else:
                scored = [(compare(r, h), h) for h in hits]
                (ok, sim, problems), hit = max(scored, key=lambda s: (s[0][0], s[0][1]))
                who = (hit.get("author") or [{}])[0].get("family", "")
                clean = " ".join(html.unescape(re.sub(r"<[^>]+>", "", (hit.get("title") or [""])[0])).split())
                desc = f"{who} {_year(hit)}: {clean} | {(hit.get('container-title') or [''])[0]} " \
                       f"{hit.get('volume', '')}, {hit.get('page', '')}"
                row = [r.key, "PASS" if ok else "CHECK", hit.get("DOI", ""), f"{sim:.2f}", "; ".join(problems), desc]
        except Exception as exc:  # a bad record or a network hiccup must never kill a long run
            row = [r.key, "ERROR", "", "", f"{type(exc).__name__}: {exc}", ""]
        counts[row[1]] += 1
        with out.open("a", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerow(row)
        print(f"[{i}/{len(todo)}] {r.key}: {row[1]}" + (f"  ({row[4]})" if row[1] != "PASS" else ""), flush=True)
        time.sleep(args.pause)  # be polite to the free API
    print(f"wrote {out}  |  this run: {counts}  |  previously done: {len(done)}")


if __name__ == "__main__":
    main()
