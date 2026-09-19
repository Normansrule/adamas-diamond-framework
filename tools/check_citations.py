"""Fail if any [bibkey] cited in docs, README, or code is missing from the reference database."""
from __future__ import annotations
import re
import sys
from refs_common import ROOT, load

CITE = re.compile(r"\[([a-z][a-z0-9]+(?:\d{4})[a-z0-9]*)\]")


def main() -> int:
    keys = {r.key for r in load()}
    files = [ROOT / "README.md", *ROOT.glob("docs/*.md"), *ROOT.glob("adamas/*.py"),
             *ROOT.glob("circuits/**/*.*"), *ROOT.glob("examples/*.py")]
    cited: set[str] = set()
    missing: list[tuple[str, str]] = []
    for f in files:
        for m in CITE.finditer(f.read_text(encoding="utf-8")):
            cited.add(m.group(1))
            if m.group(1) not in keys:
                missing.append((f.relative_to(ROOT).as_posix(), m.group(1)))
    for f, k in missing:
        print(f"MISSING: [{k}] cited in {f}")
    print(f"{len(cited)} distinct keys cited, {len(keys)} in database, {len(keys - cited)} never cited")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
