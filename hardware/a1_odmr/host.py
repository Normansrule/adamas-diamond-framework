"""Run an ODMR sweep on the A1 kit and fit it.

    pip install pyserial
    python hardware/a1_odmr/host.py --port /dev/ttyACM0 --start 2800 --stop 2940 --step 0.5 --avg 64 --out sweep.csv
    (Windows: --port COM5; WSL2 needs usbipd to attach the Pico)

Writes a two-column CSV (frequency_MHz, adc_volts), then runs the same fit as  python -m adamas.fit odmr sweep.csv.
"""
import argparse
import csv
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True); ap.add_argument("--start", type=float, default=2800); ap.add_argument("--stop", type=float, default=2940)
    ap.add_argument("--step", type=float, default=0.5); ap.add_argument("--avg", type=int, default=64); ap.add_argument("--out", default="sweep.csv")
    ap.add_argument("--no-fit", action="store_true")
    a = ap.parse_args()
    import serial
    with serial.Serial(a.port, 115200, timeout=10) as s:
        time.sleep(0.5); s.reset_input_buffer()
        s.write(f"SWEEP {a.start} {a.stop} {a.step} {a.avg}\n".encode())
        rows = []
        while True:
            line = s.readline().decode(errors="ignore").strip()
            if not line:
                sys.exit("timeout: no data from the Pico (check the port and that main.py is running)")
            if line == "END":
                break
            f, v = line.split(","); rows.append((float(f), float(v)))
            print(f"\r{len(rows)} points, {f} MHz", end="")
    with open(a.out, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(["frequency_MHz", "adc_volts"]); w.writerows(rows)
    print(f"\nwrote {a.out}")
    if not a.no_fit:
        from adamas.fitting import fit, load_csv
        print(fit("odmr", *load_csv(a.out)).summary())


if __name__ == "__main__":
    main()
