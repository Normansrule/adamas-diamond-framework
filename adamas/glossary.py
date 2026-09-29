"""Glossary: every acronym and specialist term used in the framework, spelled out and explained in one sentence.
Generates docs/GLOSSARY.md and data/glossary.json, from which web/assets/glossary.js adds hover definitions to the
first use of each term on every page of the website."""
from __future__ import annotations

TERMS = {
    "NV": ("nitrogen-vacancy center", "A nitrogen atom next to a missing carbon atom in diamond; its electron spin is a qubit that works at room temperature."),
    "ODMR": ("optically detected magnetic resonance", "Reading a spin with light: the NV glow dims when a microwave field is tuned to its resonance."),
    "ZPL": ("zero-phonon line", "The sharp optical line of a color center without lattice vibrations: 637 nm for NV⁻, 575 nm for NV⁰."),
    "T1": ("longitudinal relaxation time", "How long a spin keeps its population (up or down) before relaxing."),
    "T2": ("coherence time (spin echo)", "How long a spin keeps its phase when static field noise is refocused by an echo."),
    "T2*": ("inhomogeneous dephasing time", "How long phase survives without an echo; limited by static field differences."),
    "CVD": ("chemical vapor deposition", "Growing a solid from reactive gases; diamond grows from methane and hydrogen."),
    "MPCVD": ("microwave plasma chemical vapor deposition", "CVD in which a microwave-driven plasma cracks methane and hydrogen to grow diamond."),
    "HPHT": ("high-pressure, high-temperature", "Growing diamond at several gigapascals and over 1,300 °C, like the conditions in Earth's mantle."),
    "ALD": ("atomic layer deposition", "Depositing a film one atomic layer at a time from alternating precursors; used for the Al₂O₃ gate insulator."),
    "TMA": ("trimethylaluminium", "The pyrophoric aluminium precursor for ALD Al₂O₃."),
    "2DHG": ("two-dimensional hole gas", "A sheet of mobile holes a few nanometers under a hydrogen-terminated diamond surface: the transistor channel."),
    "MOSFET": ("metal-oxide-semiconductor field-effect transistor", "A transistor whose channel is controlled by a gate across a thin insulator."),
    "FET": ("field-effect transistor", "A transistor controlled by an electric field from its gate."),
    "E/D": ("enhancement/depletion", "Logic built from normally-off (enhancement) drivers and normally-on (depletion) loads, used when only one transistor polarity exists."),
    "CMOS": ("complementary metal-oxide-semiconductor", "Logic that pairs n- and p-channel transistors so no current flows when idle."),
    "PDK": ("process design kit", "The rules, device models, and cell libraries that let designers use a manufacturing process."),
    "LEF": ("Library Exchange Format", "A file describing the outline, pins, and blockages of each standard cell for placement and routing."),
    "DEF": ("Design Exchange Format", "A file describing where cells and wires are placed in a chip layout."),
    "GDS": ("Graphic Data System (GDSII)", "The standard binary file format for chip layouts sent to mask makers."),
    "DRC": ("design rule check", "Automatic checking that a layout obeys the minimum widths and spacings of a process."),
    "SPICE": ("Simulation Program with Integrated Circuit Emphasis", "The classic circuit simulator; ngspice is its open-source descendant."),
    "RTL": ("register-transfer level", "Describing a digital circuit as registers and the logic between them, in Verilog or VHDL."),
    "ORFS": ("OpenROAD-flow-scripts", "An open-source flow that takes RTL to a routed chip layout."),
    "TLM": ("transfer length method", "Measuring contact resistance from resistors of increasing length."),
    "PCM": ("process control monitor", "Test structures on every wafer that measure the process itself."),
    "BOE": ("buffered oxide etch", "A buffered hydrofluoric-acid solution that etches oxides."),
    "EUV": ("extreme ultraviolet", "13.5 nm light used by the most advanced lithography tools."),
    "SiC": ("silicon carbide", "A wide-bandgap semiconductor used in today's electric-vehicle power switches."),
    "GaN": ("gallium nitride", "A wide-bandgap semiconductor used in fast chargers, radio amplifiers, and data-center supplies."),
    "BFOM": ("Baliga's figure of merit", "εμE_c³: how low a power switch's on-resistance can be for a given blocking voltage."),
    "QEC": ("quantum error correction", "Spreading one logical qubit over many physical qubits so errors can be detected and undone."),
    "CSS": ("Calderbank–Shor–Steane code", "A quantum code with separate checks for bit flips and phase flips; the standard surface code is one."),
    "XZZX": ("XZZX surface code", "A surface-code variant whose checks mix X and Z, which exploits noise dominated by one error type."),
    "MWPM": ("minimum-weight perfect matching", "The decoding algorithm that pairs syndrome defects with the shortest error chains."),
    "SRIM": ("Stopping and Range of Ions in Matter", "Software that predicts how deep implanted ions come to rest."),
    "SPAD": ("single-photon avalanche diode", "A detector that registers individual photons."),
    "APD": ("avalanche photodiode", "A photodiode with internal gain; in Geiger mode it counts single photons."),
    "AOM": ("acousto-optic modulator", "A crystal driven by sound waves that switches a laser beam on and off in nanoseconds."),
    "PLL": ("phase-locked loop", "A circuit that synthesizes a stable, tunable frequency from a reference clock."),
    "FPGA": ("field-programmable gate array", "A chip of reconfigurable logic; here it times laser and microwave pulses."),
    "AWG": ("arbitrary waveform generator", "An instrument that outputs any programmed voltage waveform, used for qubit control pulses."),
    "TIA": ("transimpedance amplifier", "An amplifier that turns a small photocurrent into a voltage."),
    "RF": ("radio frequency", "Electromagnetic signals from kilohertz to hundreds of gigahertz."),
    "EV": ("electric vehicle", "A car driven by electric motors; its inverter is a key market for wide-bandgap power switches."),
    "NA": ("numerical aperture", "How wide a cone of light a lens collects; high NA means brighter images of single emitters."),
    "DIA-4": ("DIA-4 processor", "This repository's 4-bit teaching processor, synthesized onto diamond logic cells."),
}


def to_json() -> dict:
    return {k: {"full": v[0], "def": v[1]} for k, v in TERMS.items()}


def to_markdown() -> str:
    L = ["# Glossary", "", "_Generated from `adamas/glossary.py`. On the website, hover the dotted underline on the first use of any term._", "",
         "| Term | Stands for | Meaning |", "|---|---|---|"]
    L += [f"| {k} | {v[0]} | {v[1]} |" for k, v in sorted(TERMS.items(), key=lambda kv: kv[0].lower())]
    return "\n".join(L) + "\n"


def write(path: str = "docs/GLOSSARY.md") -> str:
    from pathlib import Path
    Path(path).write_text(to_markdown(), encoding="utf-8"); return path
