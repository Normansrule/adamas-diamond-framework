"""ADAMAS: a design framework for diamond-wafer electronics, from classical devices to room-temperature
nitrogen-vacancy (NV) quantum processors.

Every formula in this package carries a ``[bibkey]`` that resolves in references/REFERENCES.md.
"""
__version__ = "0.25.0"
from . import constants, materials, doping, thermal, wafer, power, logic, nv, coupling, register  # noqa: F401
from . import litho, digital, analog, opensys, qec, gate_budget, surface_sim, converter, scaling, pdk0, stdcells, explorer, poster, orfs_platform, circuit_qec, resource, course, photophysics, traveler, experiments, fitting, glossary, paper, uncertainty, validation, decision  # noqa: F401,E402
