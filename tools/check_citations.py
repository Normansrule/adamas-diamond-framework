"""Fail if any [bibkey] cited in docs, README, or code is missing from the reference database."""
from __future__ import annotations
import re
import sys
from refs_common import ROOT, load

KEY = re.compile(r"[a-z][a-z0-9]+(?:\d{4})[a-z0-9]*")
GROUP = re.compile(r"\[([a-z][^\[\]\n]{3,160})\]")      # [key], [key1, key2], [key, preprint]


def cites(text: str):
    for m in GROUP.finditer(text):
        for part in m.group(1).split(","):
            part = part.strip()
            if KEY.fullmatch(part):
                yield part


def main() -> int:
    keys = {r.key for r in load()}
    files = [ROOT / "README.md", *ROOT.glob("docs/**/*.md"), *ROOT.glob("adamas/*.py"),
             *[p for p in ROOT.glob("circuits/**/*.*") if p.suffix not in (".gds", ".def", ".pyc")], *ROOT.glob("examples/*.py"), *ROOT.glob("web/*.html"), *ROOT.glob("web/labs/*.html"), *ROOT.glob("web/assets/**/*.js")]
    cited: set[str] = set()
    missing: list[tuple[str, str]] = []
    for f in files:
        for k in cites(f.read_text(encoding="utf-8")):
            cited.add(k)
            if k not in keys:
                missing.append((f.relative_to(ROOT).as_posix(), k))
    for f, k in missing:
        print(f"MISSING: [{k}] cited in {f}")
    print(f"{len(cited)} distinct keys cited, {len(keys)} in database, {len(keys - cited)} never cited")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
