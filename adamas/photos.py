"""Openly licensed photographs for the Fab Journey, fetched from Wikimedia Commons with their license read from Commons.

The build container that writes this package cannot reach Wikimedia Commons, so no photo is checked or stored by hand.
Instead each candidate below names a Commons file and the Fab Journey step it illustrates, and

    python -m adamas.photos            (or: make photos, which also rebuilds the docs)

asks the Commons API for each file's license, author and source, keeps only public-domain, CC0, CC BY and CC BY-SA
files with no stated restriction, saves a 1024-pixel JPEG or PNG copy under docs/img/photos/, and writes one row per
kept file to references/images.psv. A file whose license is anything else, whose author is not stated, or whose page
cannot be read is skipped and reported; nothing is guessed. If the network fails, the log is left as it was and the
command exits with an error. Photos keep their own licenses; they are not covered by the repository's MIT license.

The candidate titles were found by web search on 18 November 2026; their licenses are read only by this script.
"""
from __future__ import annotations

import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHOTOS = ROOT / "docs" / "img" / "photos"
IMAGES = ROOT / "references" / "images.psv"
API = "https://commons.wikimedia.org/w/api.php"
SOURCE_PREFIX = "https://commons.wikimedia.org/wiki/File:"
COPY_PREFIX = "https://upload.wikimedia.org/"
WIDTH = 1024
FIELDS = ("file", "title", "author", "source", "license", "credit", "step", "note", "license_url")
HEADER = """# ADAMAS photo log. One row per photo shown anywhere in the project, written by `python -m adamas.photos` from the
# Wikimedia Commons API (license, author and source are copied from Commons, never typed by hand):
# file (under docs/img/photos/) | title | author | source URL | license | credit line | Fab Journey step ID | note | license URL
# Allowed licenses: public domain, CC0, CC BY, CC BY-SA (any version). tests/test_journey.py checks every row and that the file exists.
# Each photo keeps its own license (not the repository's MIT license); the files are 1024-pixel copies of the originals.
# Never log an AI-generated image as a photo.
"""


def _ua() -> str:
    from . import __version__
    return f"ADAMAS-photo-fetch/{__version__} (open-source teaching documentation build)"


# (Fab Journey step, Commons file title, what the caption must add so the photo is not read as more than it shows)
CANDIDATES = [
    ("W1", "File:Single-crystal CVD diamond disc.jpg",
     "A single-crystal diamond grown by heteroepitaxy, the method of this step; the image appears to be the crystal "
     "shown in [schreck2017] (check the Commons description)."),
    ("S03", "File:CVD Reaction Chamber - GPN-2000-001466.jpg",
     "A chemical vapor deposition chamber, not a diamond reactor: shown only as an example of the kind of tool."),
    ("S05", "File:JEOL Electron Beam Lithography (EBL) (48539692216).jpg",
     "An electron-beam lithography tool of the kind that writes the masks of this step and of S06."),
    ("S19", "File:TF78 60 - Wire bonding.jpg",
     "Wire bonding, shown as an example of the kind of tool; not a diamond device."),
]


def license_ok(name: str) -> str | None:
    """The allowed license this Commons short name stands for, or None. Accepts any version of CC BY and CC BY-SA;
    rejects non-commercial, no-derivatives, ported, GNU Free Documentation License and country-specific public-domain tags."""
    n = " ".join(name.replace("_", " ").split())
    if re.fullmatch(r"(?i)public domain|pd-usgov(-[a-z]+)*", n):
        return "public domain"
    if re.fullmatch(r"(?i)cc0( 1\.0)?", n):
        return "CC0"
    m = re.fullmatch(r"(?i)cc[ -]by(-sa)?( \d(\.\d)?)?", n)
    if m:
        return ("CC BY-SA" if m.group(1) else "CC BY") + (m.group(2) or "")
    return None


def _text(v: str) -> str:
    """Plain text from a Commons extmetadata HTML value."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", v or "")).split())


def parse(api_json: dict, title: str) -> dict:
    """One file's facts from an API reply (action=query, prop=imageinfo, iiprop=url|extmetadata|mime): either
    {"ok": True, license, license_url, author, source, thumb, ext} or {"ok": False, "why": ...}."""
    pages = (api_json.get("query") or {}).get("pages") or {}
    page = next(iter(pages.values()), None)
    if not page or "missing" in page or not page.get("imageinfo"):
        return {"ok": False, "why": f"{title}: no such file on Commons"}
    ii = page["imageinfo"][0]
    meta = {k: (v or {}).get("value", "") for k, v in (ii.get("extmetadata") or {}).items()}
    raw = _text(meta.get("LicenseShortName", ""))
    lic = license_ok(raw)
    if not lic:
        return {"ok": False, "why": f"{title}: license {raw or 'not stated'} is not allowed"}
    if _text(meta.get("Restrictions", "")):
        return {"ok": False, "why": f"{title}: restriction stated ({_text(meta['Restrictions'])})"}
    author = _text(meta.get("Artist", ""))
    if lic == "public domain" and not author:
        author = _text(meta.get("Credit", ""))
    if not author or author.lower() in ("unknown", "unknown author", "anonymous"):
        return {"ok": False, "why": f"{title}: no author stated"}
    source, thumb = ii.get("descriptionurl", ""), ii.get("thumburl") or ii.get("url", "")
    if not source.startswith(SOURCE_PREFIX) or not thumb.startswith(COPY_PREFIX):
        return {"ok": False, "why": f"{title}: unexpected source or file address"}
    ext = urllib.parse.urlparse(thumb).path.rsplit(".", 1)[-1].lower()
    ext = {"jpeg": "jpg"}.get(ext, ext)
    if ext not in ("jpg", "png"):
        return {"ok": False, "why": f"{title}: copy is .{ext}, not JPEG or PNG"}
    lic_url = _text(meta.get("LicenseUrl", ""))
    return {"ok": True, "license": lic, "license_as_stated": raw, "license_url": lic_url if lic_url.startswith("https://") else "",
            "author": author, "source": source, "thumb": thumb, "ext": ext}


def file_name(step: str, title: str, ext: str = "jpg") -> str:
    stem = re.sub(r"[^a-z0-9]+", "-", title.split(":", 1)[-1].rsplit(".", 1)[0].lower()).strip("-")[:60]
    return f"{step.lower().replace('.', '-')}-{stem}.{ext}"


def row(step: str, title: str, facts: dict, note: str) -> str:
    name = title.split(":", 1)[-1].rsplit(".", 1)[0]
    credit = f"{name}, by {facts['author']}, {facts['license']}, via Wikimedia Commons (resized)"
    cells = [file_name(step, title, facts["ext"]), name, facts["author"], facts["source"], facts["license"], credit, step, note,
             facts["license_url"]]
    return " | ".join(c.replace("|", "/") for c in cells)


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _ua()})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def fetch(out=sys.stdout) -> int:
    """Fetch every candidate; write the photos and references/images.psv. Returns the number of photos kept.
    Raises SystemExit (and leaves the log unchanged) when Commons cannot be read."""
    got = []
    for step, title, note in CANDIDATES:
        q = {"action": "query", "format": "json", "prop": "imageinfo", "iiprop": "url|extmetadata|mime", "redirects": "1",
             "iiurlwidth": str(WIDTH), "titles": title}
        try:
            facts = parse(json.loads(_get(API + "?" + urllib.parse.urlencode(q))), title)
            data = _get(facts["thumb"]) if facts["ok"] else None
        except (OSError, ValueError) as e:
            raise SystemExit(f"could not read Wikimedia Commons ({title}: {e}); references/images.psv is unchanged")
        got.append((step, title, note, facts, data))
    PHOTOS.mkdir(parents=True, exist_ok=True)
    rows, keep = [], set()
    for step, title, note, facts, data in got:
        if facts["ok"]:
            name = file_name(step, title, facts["ext"])
            (PHOTOS / name).write_bytes(data)
            keep.add(name)
            rows.append(row(step, title, facts, note))
            print(f"kept    {step}: {title} ({facts['license_as_stated']}, {facts['author']})", file=out)
        else:
            print(f"skipped {step}: {facts['why']}", file=out)
    for p in PHOTOS.iterdir():                 # never publish a file that has no row in the log
        if p.is_file() and p.name not in keep:
            p.unlink()
    IMAGES.write_text(HEADER + "".join(r + "\n" for r in rows), encoding="utf-8")
    print(f"{len(rows)} of {len(CANDIDATES)} photos kept; now run: python -m adamas build docs", file=out)
    return len(rows)


if __name__ == "__main__":
    fetch()
