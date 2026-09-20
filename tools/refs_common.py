"""Shared loader for the pipe-separated reference database in references/."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF_FILES = [ROOT / "references" / "refs_a.psv", ROOT / "references" / "refs_b.psv",
             ROOT / "references" / "refs_c.psv"]

TAG_NAMES = {
    "mat": "Materials physics and figures of merit",
    "waf": "Diamond growth and wafers",
    "si": "Silicon baseline",
    "dop": "Doping, surfaces, and processing",
    "dev": "Devices and circuits",
    "thm": "Thermal management and diamond-on-chip integration",
    "nv": "Nitrogen-vacancy (NV) center physics",
    "sens": "Quantum sensing",
    "fab": "NV center fabrication and placement",
    "qc": "Quantum computing with diamond spins",
    "net": "Photonics, other color centers, and quantum networks",
    "ind": "Industry and news (2025-2026)",
    "edu": "Teaching laboratories",
    "lit": "Lithography and nanofabrication",
    "eda": "Digital design, processors, and design automation",
    "ana": "Analog design and compact models",
    "ctl": "Quantum control, open systems, and error correction",
    "bey": "Beyond: adjacent platforms and frontier applications",
}


@dataclass(frozen=True)
class Ref:
    key: str
    authors: str
    year: str
    title: str
    venue: str
    locator: str
    tags: tuple[str, ...]
    status: str

    def apa(self) -> str:
        loc = f", {self.locator}" if self.locator not in ("book", "report") else ""
        return f"{self.authors} ({self.year}). {self.title}. *{self.venue}*{loc}."


def load() -> list[Ref]:
    refs: list[Ref] = []
    seen: set[str] = set()
    for path in REF_FILES:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip() or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) != 8:
                raise ValueError(f"{path.name}:{n}: expected 8 fields, got {len(parts)}")
            key = parts[0]
            if key in seen:
                raise ValueError(f"duplicate key {key}")
            seen.add(key)
            refs.append(Ref(key, parts[1], parts[2], parts[3], parts[4], parts[5],
                            tuple(parts[6].split(",")), parts[7]))
    return refs
