"""ADAMAS-PDK-0: layer map, lambda design rules, and a generator for the process-control-monitor die (project P-1).

Process: hydrogen-terminated diamond p-channel MOSFET flow of chapters 3 and E2 [kawarada2014], [kitabayashi2017],
[saha2021], two threshold flavors [liu2017]. Rules use the scalable-lambda convention [meadconway1980] with lambda = 1 um.
Test structures: transfer-length ladder and van der Pauw cross [sze2006]; MOS capacitor [matsumoto2016]; transistor W/L
array for mismatch [pelgrom1989]; serpentine and comb for defect density [stapper1983]; ring oscillators [liu2017];
NV witness window kept oxygen-terminated [hauf2011].

Output is GDSII written by a small self-contained writer (rectangles, text, references), readable by KLayout, Magic, or
any layout tool. Coordinates in micrometers; database unit 1 nm.
"""
from __future__ import annotations
import struct
from dataclasses import dataclass, field

LAMBDA_UM = 1.0

LAYERS = {  # name: (gds layer, datatype, purpose, polarity)
    "OHMIC": (1, 0, "Gold source/drain; protects C-H termination", "dark"),
    "ISO": (2, 0, "Oxygen-plasma isolation (drawn where C-O is wanted)", "dark"),
    "ENH": (3, 0, "Partial channel oxidation: enhancement-mode devices", "dark"),
    "GATE": (4, 0, "Gate metal on ALD Al2O3", "dark"),
    "VIA": (5, 0, "Openings in Al2O3", "clear"),
    "METAL2": (6, 0, "Interconnect and pads", "dark"),
    "QIMPLANT": (7, 0, "Nitrogen implant apertures (electron beam)", "clear"),
    "QELEC": (8, 0, "Photocurrent electrodes and microwave line", "dark"),
    "TEXT": (63, 0, "Labels", "n/a"),
}

RULES = {  # in lambda; every rule cites its reason in chapter E2
    "min_width": 2, "min_space": 2, "gate_overhang_active": 2, "via_enclosure": 1, "via_size": 3, "pad": 100, "pad_space": 50,
    "gate_length_min": 2, "ohmic_to_gate": 2, "iso_enclosure_of_device": 3, "qimplant_min": 0.02, "nv_window_to_channel": 5,
}


# ---------------- minimal GDSII writer ----------------
def _real8(x: float) -> bytes:
    if x == 0:
        return b"\x00" * 8
    sign = 0
    if x < 0:
        sign, x = 0x80, -x
    exp = 0
    while x >= 1.0:
        x /= 16.0; exp += 1
    while x < 1.0 / 16.0:
        x *= 16.0; exp -= 1
    mant = int(x * (1 << 56))
    return bytes([sign | (exp + 64)]) + mant.to_bytes(7, "big")


def _rec(code: int, data: bytes = b"") -> bytes:
    return struct.pack(">HH", 4 + len(data), code) + data


def _str(s: str) -> bytes:
    b = s.encode("ascii")
    return b + (b"\x00" if len(b) % 2 else b"")


@dataclass
class Cell:
    name: str
    boxes: list = field(default_factory=list)     # (layer, x0, y0, x1, y1) in um
    texts: list = field(default_factory=list)     # (layer, x, y, string)
    refs: list = field(default_factory=list)      # (cellname, x, y)

    def box(self, layer: str, x0: float, y0: float, x1: float, y1: float) -> None:
        self.boxes.append((layer, min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))

    def text(self, x: float, y: float, s: str) -> None:
        self.texts.append(("TEXT", x, y, s))

    def ref(self, cell: "Cell", x: float, y: float) -> None:
        self.refs.append((cell.name, x, y))


def write_gds(path: str, cells: list[Cell], top: str) -> None:
    dbu = 1e-3                                   # 1 nm database unit expressed in um
    out = [_rec(0x0002, struct.pack(">h", 600)), _rec(0x0102, b"\x00" * 24), _rec(0x0206, _str("ADAMAS_PDK0")),
           _rec(0x0305, _real8(dbu) + _real8(dbu * 1e-6))]
    order = sorted(cells, key=lambda c: c.name == top)   # leaves first, top last
    for c in order:
        out += [_rec(0x0502, b"\x00" * 24), _rec(0x0606, _str(c.name))]
        for layer, x0, y0, x1, y1 in c.boxes:
            l, d = LAYERS[layer][:2]
            pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
            xy = b"".join(struct.pack(">ii", round(x / dbu), round(y / dbu)) for x, y in pts)
            out += [_rec(0x0800), _rec(0x0D02, struct.pack(">h", l)), _rec(0x0E02, struct.pack(">h", d)), _rec(0x1003, xy), _rec(0x1100)]
        for layer, x, y, s in c.texts:
            l, d = LAYERS[layer][:2]
            out += [_rec(0x0C00), _rec(0x0D02, struct.pack(">h", l)), _rec(0x1602, struct.pack(">h", d)),
                    _rec(0x1003, struct.pack(">ii", round(x / dbu), round(y / dbu))), _rec(0x1906, _str(s)), _rec(0x1100)]
        for name, x, y in c.refs:
            out += [_rec(0x0A00), _rec(0x1206, _str(name)), _rec(0x1003, struct.pack(">ii", round(x / dbu), round(y / dbu))), _rec(0x1100)]
        out.append(_rec(0x0700))
    out.append(_rec(0x0400))
    with open(path, "wb") as fh:
        fh.write(b"".join(out))


# ---------------- devices and monitors ----------------
def pfet(name: str, w: float, l: float, enhancement: bool) -> Cell:
    """Hydrogen-terminated p-FET: gold ohmics, gate of length l over a channel of width w, C-O isolation around."""
    c = Cell(name)
    lam, g = LAMBDA_UM, RULES["ohmic_to_gate"] * LAMBDA_UM
    ox = 6 * lam
    c.box("OHMIC", -l / 2 - g - ox, -w / 2, -l / 2 - g, w / 2)
    c.box("OHMIC", l / 2 + g, -w / 2, l / 2 + g + ox, w / 2)
    c.box("GATE", -l / 2, -w / 2 - RULES["gate_overhang_active"] * lam, l / 2, w / 2 + RULES["gate_overhang_active"] * lam)
    if enhancement:
        c.box("ENH", -l / 2, -w / 2, l / 2, w / 2)
    e = RULES["iso_enclosure_of_device"] * lam
    x0, x1 = -l / 2 - g - ox - e, l / 2 + g + ox + e
    y0, y1 = -w / 2 - e, w / 2 + e
    # ISO is drawn as a frame around the device (the interior stays hydrogen-terminated)
    c.box("ISO", x0 - 2 * lam, y0 - 2 * lam, x1 + 2 * lam, y0)
    c.box("ISO", x0 - 2 * lam, y1, x1 + 2 * lam, y1 + 2 * lam)
    c.box("ISO", x0 - 2 * lam, y0, x0, y1)
    c.box("ISO", x1, y0, x1 + 2 * lam, y1)
    return c


def pad_frame(c: Cell, x: float, y: float, label: str) -> None:
    p = RULES["pad"] * LAMBDA_UM
    c.box("METAL2", x, y, x + p, y + p)
    c.box("VIA", x + 10, y + 10, x + p - 10, y + p - 10)
    c.text(x + p / 2, y + p / 2, label)


def tlm_ladder(spacings=(2, 4, 8, 16, 32)) -> Cell:
    c = Cell("TLM"); x = 0.0
    for s in spacings:
        c.box("OHMIC", x, 0, x + 20, 100); x += 20 + s
    c.box("OHMIC", x, 0, x + 20, 100)
    c.box("ISO", -5, -5, x + 25, 0); c.box("ISO", -5, 100, x + 25, 105)
    c.text(x / 2, 110, "TLM spacings 2..32 um")
    return c


def van_der_pauw(size=100.0) -> Cell:
    c = Cell("VDP"); a = size / 4
    c.box("ISO", -size, -size, size, -size / 2); c.box("ISO", -size, size / 2, size, size)
    c.box("ISO", -size, -size / 2, -size / 2, size / 2); c.box("ISO", size / 2, -size / 2, size, size / 2)
    for x, y in [(-size / 2, -size / 2), (size / 2 - a, -size / 2), (-size / 2, size / 2 - a), (size / 2 - a, size / 2 - a)]:
        c.box("OHMIC", x, y, x + a, y + a)
    c.text(0, 0, "van der Pauw")
    return c


def moscap(side=200.0) -> Cell:
    c = Cell("MOSCAP")
    c.box("GATE", -side / 2, -side / 2, side / 2, side / 2)
    c.box("OHMIC", side / 2 + 5, -side / 2, side / 2 + 40, side / 2)
    c.text(0, 0, "MOS capacitor")
    return c


def serpentine_comb(width=2.0, space=2.0, n=40, length=400.0) -> Cell:
    c = Cell("SERPCOMB")
    for i in range(n):
        y = i * (width + space) * 2
        c.box("METAL2", 0, y, length, y + width)
        c.box("METAL2", 0 if i % 2 else length - width, y, width if i % 2 else length, y + 2 * width + space)
        c.box("METAL2", 0, y + width + space, length, y + 2 * width + space)   # comb finger (interleaved, separate net)
    c.text(length / 2, -10, "serpentine + comb")
    return c


def nv_window(side=50.0, pitch=0.5, n=10) -> Cell:
    """Oxygen-terminated witness window with an n x n array of nitrogen implant apertures."""
    c = Cell("NVWIN")
    c.box("ISO", -side / 2, -side / 2, side / 2, side / 2)
    a = 0.05
    for i in range(n):
        for j in range(n):
            x, y = (i - n / 2 + 0.5) * pitch, (j - n / 2 + 0.5) * pitch
            c.box("QIMPLANT", x - a / 2, y - a / 2, x + a / 2, y + a / 2)
    c.box("QELEC", -side / 2 + 2, -8, side / 2 - 2, -5); c.box("QELEC", -side / 2 + 2, 5, side / 2 - 2, 8)
    c.text(0, side / 2 + 5, "NV witness, 50 nm apertures")
    return c


def monitor_die(die_mm: float = 3.0) -> list[Cell]:
    """Full PDK-0 monitor die: returns [top, subcells...]. Layout in micrometers, origin at the lower left."""
    top = Cell("PDK0_MONITOR"); d = die_mm * 1e3
    top.box("ISO", 0, 0, d, 60); top.box("ISO", 0, d - 60, d, d); top.box("ISO", 0, 0, 60, d); top.box("ISO", d - 60, 0, d, d)
    cells = [tlm_ladder(), van_der_pauw(), moscap(), serpentine_comb(), nv_window()]
    fets = []
    for k, (w, l, enh) in enumerate([(4, 2, True), (8, 2, True), (16, 2, True), (32, 2, True), (16, 4, True), (16, 8, True),
                                      (4, 2, False), (16, 2, False), (16, 8, False), (64, 2, False)]):
        f = pfet(f"PFET_W{w}_L{l}_{'E' if enh else 'D'}", float(w), float(l), enh)
        fets.append(f)
    cells += fets
    top.ref(cells[0], 200, 200); top.ref(cells[1], 700, 300); top.ref(cells[2], 1100, 300); top.ref(cells[3], 200, 600)
    top.ref(cells[4], 2500, 2500)
    for k, f in enumerate(fets):
        for m in range(4):                                                          # 4 copies each for mismatch statistics
            top.ref(f, 200 + k * 250, 1000 + m * 200)
    for k, lab in enumerate(["VSS", "GATE", "DRAIN", "SOURCE", "SUB", "RO_OUT", "NV_A", "NV_B"]):
        pad_frame(top, 100 + k * 150 * LAMBDA_UM, d - 200, lab)
    top.text(d / 2, d - 300, "ADAMAS PDK-0 monitor die v0.6.0")
    return [top] + cells


def summarize(cells: list[Cell]) -> dict:
    n_box = sum(len(c.boxes) for c in cells)
    n_ref = sum(len(c.refs) for c in cells)
    return {"cells": len(cells), "rectangles": n_box, "references": n_ref}
