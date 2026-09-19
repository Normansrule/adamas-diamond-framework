"""Print the figure-of-merit table and the dopant ionization table. Sources: see adamas.materials and adamas.doping."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adamas import doping, materials, power  # noqa: E402

print(f"{'Material':10s} {'BFOM':>10s} {'BHFFOM':>10s} {'JFOM':>10s} {'KFOM':>8s}   (relative to silicon)")
for key, f in materials.normalized_foms().items():
    print(f"{key:10s} {f['BFOM']:10.0f} {f['BHFFOM']:10.0f} {f['JFOM']:10.0f} {f['KFOM']:8.2f}")

print("\nIonized dopant fraction at 300 K, 1e17 cm^-3:")
for key, d in doping.DOPANTS.items():
    print(f"  {key:5s} Ea = {d.ea_ev:5.3f} eV  ->  {doping.ionized_fraction(d, 1e17):.3e}")

bv = 2608.0
print(f"\nIdeal specific on-resistance at {bv:.0f} V (milliohm cm^2):")
for key, m in materials.MATERIALS.items():
    print(f"  {key:8s} {power.ron_sp_mohm_cm2(m, bv, 'p' if key == 'Diamond' else 'n'):10.4f}")
print("  measured diamond MOSFET [saha2021]:", power.MEASURED_DIAMOND["saha2021"]["ron_mohm_cm2"])
