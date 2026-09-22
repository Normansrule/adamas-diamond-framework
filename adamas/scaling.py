"""How big would a room-temperature NV quantum computer have to be? Sizing arithmetic (project X-2 preview).

Workloads (physical-qubit counts published for surface-code machines with 1e-3 physical error):
    RSA-2048 factoring: 20 million qubits, 8 hours at a 1 us cycle [gidney2021]; < 1 million qubits [gidney2025]
    FeMoco nitrogenase chemistry: about 1 million qubits, days [reiher2017], [babbush2018]
Lattice-surgery layouts: [litinski2019], [fowler2012]. Cycle times of other platforms: superconducting ~1 us
[google2023], [google2025], [arute2019]; neutral atoms and ions ~ms [bluvstein2024], [monroe2013].

NV cell (this repository's architecture, chapters 8 and E6): one electron plus about 3 nuclear spins per cell, cells on
an optical-addressing pitch (about 0.5 to 1 um, diffraction) or an electrode pitch (1 to 2 um) [siyushev2019], [li2024].
Syndrome cycle time is set by repetitive electron readout, 0.1 to 10 ms [neumann2010science], [hopper2018].

Control power: superconducting machines pay a cryostat ([krinner2019], [reilly2015], [vandersypen2017]); NV machines pay
microwaves and light per cell (about 1 mW per cell driven; laser 0.1 to 1 mW per site under illumination).
"""
from __future__ import annotations
import math

WORKLOADS = {
    "RSA-2048, 2021 layout": {"physical_qubits": 20e6, "hours_at_1us": 8.0, "ref": "gidney2021"},
    "RSA-2048, 2025 layout": {"physical_qubits": 1e6, "hours_at_1us": 24 * 7.0, "ref": "gidney2025"},
    "FeMoco energy (chemistry)": {"physical_qubits": 1e6, "hours_at_1us": 24 * 4.0, "ref": "babbush2018"},
    "100 logical qubits, d = 17": {"physical_qubits": 100 * (2 * 17 ** 2 - 1), "hours_at_1us": 1.0, "ref": "fowler2012"},
}
PLATFORM_CYCLE_S = {"superconducting": 1e-6, "neutral atoms": 1e-3, "trapped ions": 1e-3,
                    "NV, optical repetitive readout": 1e-3, "NV, electrical readout (proposed)": 1e-4}


def wall_clock_hours(workload: str, cycle_s: float) -> float:
    w = WORKLOADS[workload]
    return w["hours_at_1us"] * cycle_s / 1e-6


def cells_needed(physical_qubits: float, qubits_per_cell: int = 4) -> int:
    return math.ceil(physical_qubits / qubits_per_cell)


def wafers_needed(cells: int, pitch_um: float = 1.0, wafer_mm: float = 76.0, cell_yield: float = 0.5, fill: float = 0.6) -> float:
    """Number of wafers whose working cells cover the demand; fill = fraction of wafer area given to cells."""
    area_um2 = math.pi * (wafer_mm * 1e3 / 2) ** 2 * fill
    return cells / (area_um2 / pitch_um ** 2 * cell_yield)


def die_side_mm(cells: int, pitch_um: float = 1.0, fill: float = 0.6) -> float:
    return math.sqrt(cells * pitch_um ** 2 / fill) * 1e-3


def control_power_w(cells: int, duty: float = 0.1, mw_per_cell_w: float = 1e-3, laser_per_cell_w: float = 3e-4) -> float:
    return cells * duty * (mw_per_cell_w + laser_per_cell_w)


def summary(workload: str, cycle_s: float = 1e-3, qubits_per_cell: int = 4, pitch_um: float = 1.0, cell_yield: float = 0.5) -> dict:
    w = WORKLOADS[workload]
    cells = cells_needed(w["physical_qubits"], qubits_per_cell)
    return {"physical_qubits": w["physical_qubits"], "nv_cells": cells, "wall_clock_hours": wall_clock_hours(workload, cycle_s),
            "die_side_mm": die_side_mm(cells, pitch_um), "wafers_76mm": wafers_needed(cells, pitch_um, 76.0, cell_yield),
            "control_power_w": control_power_w(cells)}
