"""Print every reference that is not PASS or REVIEWED, one readable block each (the CSV is awkward in a pager)."""
import csv
from refs_common import ROOT, load

refs = {r.key: r for r in load()}
with (ROOT / "references" / "verification_report.csv").open(encoding="utf-8") as fh:
    rows = [r for r in csv.DictReader(fh) if r["result"] not in ("PASS", "REVIEWED")]
for r in rows:
    ours = refs[r["key"]]
    print(f"{r['key']}  [{r['result']}]  similarity {r['title_similarity']}  doi {r['doi']}")
    print(f"   problems : {r['problems']}")
    print(f"   ours     : {ours.authors.split(';')[0]} {ours.year}: {ours.title} | {ours.venue} {ours.locator}")
    print(f"   crossref : {' '.join(r['crossref_match'].split())}\n")
print(f"{len(rows)} rows need review")
