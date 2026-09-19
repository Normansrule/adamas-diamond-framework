"""NV center resonance lines, coupling versus distance, and the two-qubit register. Sources: adamas.nv, .coupling, .register."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adamas import coupling, nv, register  # noqa: E402

for b in (0.0, 1.0, 5.0):
    lo, hi = nv.transition_frequencies_mhz([0, 0, b])
    print(f"B = {b:3.1f} mT along the NV axis: lines at {lo:8.2f} and {hi:8.2f} MHz")

print("\nNV-NV dipolar link (T2 = 1.8 ms [balasubramanian2009]):")
for r in (5, 10, 15, 20, 25, 30, 40):
    print(f"  r = {r:2d} nm  coupling = {coupling.dipolar_coupling_khz(r):8.2f} kHz  "
          f"gate = {coupling.gate_time_us(r):7.1f} us  fidelity bound = {coupling.gate_fidelity_bound(r):.4f}")

print("\nPair yield, 15 nm target spacing, 5 nm blur:")
for y in (0.01, 0.1, 0.5, 0.75):
    print(f"  conversion yield {y:4.0%} -> working pairs {coupling.pair_yield(15, 5, y):.4f}")

print("\nElectron + nitrogen-14 Bell state, pulse-limited fidelity:")
print("  Rabi = A/sqrt(3):", round(register.bell_fidelity(2.16), 5))
print("  Rabi = 2 MHz    :", round(register.bell_fidelity(2.16, 2.0), 5))
