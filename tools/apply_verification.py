"""Fold a finished Crossref verification run back into the database.

For every PASS row of references/verification_report.csv this script
  1. records the DOI in references/dois.psv (key | doi), which IS committed, and
  2. changes that reference's status from K (from knowledge) to V (verified) in the .psv files.
CHECK, ERROR, and REVIEWED rows are left untouched for a human. Then run:  make refs
"""
from __future__ import annotations
import csv
from refs_common import REF_FILES, ROOT


def main() -> None:
    report = ROOT / "references" / "verification_report.csv"
    if not report.exists():
        raise SystemExit("no verification_report.csv; run tools/verify_refs.py first")
    with report.open(encoding="utf-8") as fh:
        passed = {row["key"]: row["doi"] for row in csv.DictReader(fh) if row["result"] == "PASS"}
    doi_path = ROOT / "references" / "dois.psv"
    dois: dict[str, str] = {}
    if doi_path.exists():
        for line in doi_path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                k, d = [x.strip() for x in line.split("|", 1)]
                dois[k] = d
    dois.update({k: d for k, d in passed.items() if d})
    doi_path.write_text("# key | doi   (written by tools/apply_verification.py from Crossref matches; do not type DOIs by hand)\n"
                        + "".join(f"{k} | {d}\n" for k, d in sorted(dois.items())), encoding="utf-8")
    promoted = 0
    for path in REF_FILES:
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            parts = line.split("|")
            if len(parts) == 8 and not line.startswith("#") and parts[0].strip() in passed and parts[7].strip() == "K":
                parts[7] = " V"
                lines[i] = "|".join(parts)
                promoted += 1
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(passed)} PASS rows: {len(dois)} DOIs stored in {doi_path.name}, {promoted} references promoted K -> V")


if __name__ == "__main__":
    main()
