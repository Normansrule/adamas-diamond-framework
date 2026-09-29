"""Fit your own experiment data (the analysis step of every experiment in adamas.experiments).

    python -m adamas.fit odmr my_sweep.csv          # two columns: frequency_MHz, signal
    python -m adamas.fit rabi rabi.csv              # time_us, contrast
    python -m adamas.fit ramsey | echo | arrhenius | iv | g2  file.csv

Each fit returns best values with one-standard-deviation uncertainties from the covariance matrix, the reduced
chi-square, the model curve, and a plain-language interpretation linked to the framework's physics (field from the
ODMR splitting [doherty2013], pi-pulse length from Rabi [jelezko2004a], T2* and T2 [hahn1950], the acceptor energy
from an Arrhenius plot [lagrange1998], transistor threshold and gain factor [sze2006], single-emitter test from
g2(0) [kurtsiefer2000]). The browser Data Lab (web/datalab.html) runs the same models in JavaScript.
"""
from __future__ import annotations
import csv
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks

GAMMA_MHZ_PER_MT = 28.025
KB_EV = 8.617333262e-5


@dataclass
class Fit:
    kind: str
    params: dict
    errors: dict
    chi2_red: float
    x: list
    model: list
    notes: list = field(default_factory=list)

    def summary(self) -> str:
        rows = [f"{k:>14s} = {v:.6g} ± {self.errors.get(k, float('nan')):.2g}" for k, v in self.params.items()]
        return "\n".join([f"[{self.kind}] reduced chi-square {self.chi2_red:.3g}"] + rows + [f"  → {n}" for n in self.notes])


def load_csv(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    xs, ys = [], []
    with open(path, newline="") as fh:
        for row in csv.reader(fh):
            try:
                xs.append(float(row[0])); ys.append(float(row[1]))
            except (ValueError, IndexError):
                continue                     # header or blank line
    if len(xs) < 5:
        raise ValueError("need at least five numeric rows with two columns")
    return np.array(xs), np.array(ys)


def _finish(kind, fn, x, y, p, cov, names, notes) -> Fit:
    err = np.sqrt(np.clip(np.diag(cov), 0, None)) if cov is not None and np.all(np.isfinite(cov)) else np.full(len(p), np.nan)
    resid = y - fn(x, *p); dof = max(1, len(x) - len(p))
    sigma = max(float(np.std(np.diff(y, 2)) / math.sqrt(6)), 1e-300)    # noise from second differences (insensitive to smooth trends)
    chi2 = float(np.sum(resid ** 2) / dof / sigma ** 2)
    xx = np.linspace(x.min(), x.max(), 400)
    return Fit(kind, dict(zip(names, map(float, p))), dict(zip(names, map(float, err))), chi2, xx.tolist(), fn(xx, *p).tolist(), notes)


def lorentz_sum(x, c0, *pars):
    y = np.full_like(x, c0, dtype=float)
    for a, x0, w in zip(pars[0::3], pars[1::3], pars[2::3]):
        y = y - a * w ** 2 / ((x - x0) ** 2 + w ** 2)
    return y


def fit_odmr(x, y, max_lines: int = 8) -> Fit:
    base = np.median(np.sort(y)[-max(5, len(y) // 4):]); depth = base - y
    noise = np.std(np.diff(y, 2)) / math.sqrt(6)
    win = max(1, len(x) // 60)                                   # detect on a lightly smoothed copy; fit the raw data
    sm = np.convolve(depth, np.ones(win) / win, mode="same")
    peaks, props = find_peaks(sm, prominence=max(4 * noise / math.sqrt(win), 1e-12), width=1, distance=max(1, win))
    if len(peaks) == 0:
        raise ValueError("no resonance dip found above the noise")
    order = np.argsort(props["prominences"])[::-1][:max_lines]; peaks = np.sort(peaks[order])
    step = float(np.median(np.diff(x)))
    p0 = [base]
    for k in peaks:
        p0 += [depth[k], x[k], 3 * abs(step) + 1.0]
    model = lambda xx, *q: lorentz_sum(xx, *q)  # noqa: E731
    p, cov = curve_fit(model, x, y, p0=p0, maxfev=40000)
    # prune lines narrower than the frequency step or not significant, then refit once
    perr = np.sqrt(np.clip(np.diag(cov), 0, None)) if np.all(np.isfinite(cov)) else np.full(len(p), np.inf)
    keep = [i for i in range(len(peaks)) if abs(p[3 + 3 * i]) > 0.5 * abs(step) and p[1 + 3 * i] > 2.5 * perr[1 + 3 * i]]
    if keep and len(keep) < len(peaks):
        p0 = [p[0]] + [v for i in keep for v in p[1 + 3 * i: 4 + 3 * i]]
        p, cov = curve_fit(model, x, y, p0=p0, maxfev=40000); peaks = peaks[keep]
    names = ["baseline"] + [f"{t}{i + 1}" for i in range(len(peaks)) for t in ("depth", "center", "hwhm")]
    centers = sorted(p[2::3])
    notes = [f"{len(peaks)} resonance line(s) found"]
    if len(centers) == 1:
        notes.append(f"single line at {centers[0]:.2f} MHz (zero-field splitting D ≈ 2870 MHz)")
    else:
        split = centers[-1] - centers[0]
        notes.append(f"outermost lines {split:.2f} MHz apart → |B∥| ≥ {split / (2 * GAMMA_MHZ_PER_MT):.3f} mT along the most aligned NV axis")
        notes.append(f"center of mass {np.mean(centers):.2f} MHz")
    notes.append(f"contrast of deepest line {100 * max(p[1::3]) / p[0]:.2f}%")
    return _finish("odmr", lambda xx, *q: lorentz_sum(xx, *q), x, y, p, cov, names, notes)


def fit_rabi(x, y) -> Fit:
    f = lambda t, a, om, tau, c: c + a * (1 - np.cos(2 * np.pi * om * t) * np.exp(-t / tau))  # noqa: E731
    spec = np.abs(np.fft.rfft(y - y.mean())); fr = np.fft.rfftfreq(len(x), x[1] - x[0]); om0 = fr[1 + np.argmax(spec[1:])]
    p, cov = curve_fit(f, x, y, p0=[(y.max() - y.min()) / 2, om0, x.max(), y.min()], maxfev=20000)
    return _finish("rabi", f, x, y, p, cov, ["amplitude", "rabi_MHz", "decay_us", "offset"],
                   [f"π pulse = {500 / p[1]:.1f} ns, π/2 pulse = {250 / p[1]:.1f} ns (units: time in µs, frequency in MHz)"])


def fit_ramsey(x, y) -> Fit:
    f = lambda t, a, df, t2s, c: c + a * (1 - np.cos(2 * np.pi * df * t) * np.exp(-(t / t2s) ** 2))  # noqa: E731
    spec = np.abs(np.fft.rfft(y - y.mean())); fr = np.fft.rfftfreq(len(x), x[1] - x[0]); d0 = fr[1 + np.argmax(spec[1:])]
    p, cov = curve_fit(f, x, y, p0=[(y.max() - y.min()) / 2, d0, x.max() / 4, y.min()], maxfev=20000)
    return _finish("ramsey", f, x, y, p, cov, ["amplitude", "detuning_MHz", "T2star_us", "offset"],
                   [f"T₂* = {abs(p[2]):.3g} µs: static field inhomogeneity (echo removes it)"])


def fit_echo(x, y) -> Fit:
    f = lambda t, a, t2, n, c: c + a * np.exp(-(t / t2) ** n)  # noqa: E731
    p, cov = curve_fit(f, x, y, p0=[y.max() - y.min(), x.max() / 2, 1.5, y.min()], bounds=([0, 1e-9, 0.5, -np.inf], [np.inf, np.inf, 4, np.inf]), maxfev=20000)
    return _finish("echo", f, x, y, p, cov, ["amplitude", "T2_us", "stretch_n", "offset"],
                   [f"T₂ = {p[1]:.3g} µs, stretch exponent {p[2]:.2f} (about 3 for a slow nuclear-spin bath, 1 for fast noise)"])


def fit_arrhenius(x_inv_kilo_k, resistance) -> Fit:
    """x = 1000/T (1/K), y = resistance or resistivity. Fits the straight low-temperature part after correcting for
    the T^1.5 density of states and the T^-2.2 lattice mobility (see experiment B3)."""
    T = 1000 / x_inv_kilo_k; order = np.argsort(T); T, R, x = T[order], resistance[order], x_inv_kilo_k[order]
    n = max(5, len(T) // 3); sel = slice(0, n)
    yc = np.log(R[sel] * T[sel] ** -0.7)
    (m, b), cov = np.polyfit(x[sel], yc, 1, cov=True)
    raw = np.polyfit(x[sel], np.log(R[sel]), 1)[0]
    f = lambda xx, mm, bb: np.exp(mm * xx + bb) * (1000 / xx) ** 0.7  # noqa: E731
    fit = _finish("arrhenius", f, x[sel], R[sel], [m, b], cov, ["slope_K", "intercept"],
                  [f"activation energy {m * 1000 * KB_EV:.3f} ± {math.sqrt(cov[0, 0]) * 1000 * KB_EV:.3f} eV (corrected); raw slope {raw * 1000 * KB_EV:.3f} eV",
                   "boron in diamond: 0.37 eV in compensated samples; about half that without compensation"])
    fit.params["E_A_eV"] = float(m * 1000 * KB_EV); fit.errors["E_A_eV"] = float(math.sqrt(cov[0, 0]) * 1000 * KB_EV)
    res = yc - (m * x[sel] + b); fit.chi2_red = 1.0 if len(res) < 4 else float(np.sum(res ** 2) / (len(res) - 2) / max(np.var(np.diff(res)) / 2, 1e-300))
    return fit


def fit_iv(vds, i_ma, vgs: float | None = None) -> Fit:
    """Output curve at one gate voltage: square law I = k[(Vov)V - V²/2] below saturation, kVov²/2 above."""
    def f(v, k, vov):
        v = np.asarray(v); return np.where(v < vov, k * (vov * v - v * v / 2), k * vov * vov / 2)
    p, cov = curve_fit(f, vds, i_ma, p0=[2 * i_ma.max() / max(vds.max() / 2, 1e-9) ** 2, vds.max() / 2], maxfev=20000)
    notes = [f"gain factor k = {p[0]:.3g} mA/V², overdrive {p[1]:.3g} V (saturation onset)"]
    if vgs is not None:
        notes.append(f"threshold voltage ≈ {vgs - p[1]:.3g} V")
    return _finish("iv", f, vds, i_ma, p, cov, ["k_mA_per_V2", "overdrive_V"], notes)


def fit_g2(tau, g) -> Fit:
    f = lambda t, g0, t1, c: c * (1 - (1 - g0) * np.exp(-np.abs(t) / t1))  # noqa: E731
    p, cov = curve_fit(f, tau, g, p0=[0.3, 10, 1], maxfev=20000)
    single = p[0] < 0.5
    return _finish("g2", f, tau, g, p, cov, ["g2_zero", "tau_ns", "norm"],
                   [f"g⁽²⁾(0) = {p[0]:.3f} → {'a single quantum emitter' if single else 'more than one emitter'} (threshold 0.5)"])


FITTERS = {"odmr": fit_odmr, "rabi": fit_rabi, "ramsey": fit_ramsey, "echo": fit_echo, "arrhenius": fit_arrhenius, "iv": fit_iv, "g2": fit_g2}


def fit(kind: str, x, y) -> Fit:
    return FITTERS[kind](np.asarray(x, float), np.asarray(y, float))


def example_datasets(out: str | Path = "docs/data/examples") -> list[Path]:
    """Write simulated datasets (from adamas.experiments) as CSV files to practice the analysis."""
    from . import experiments as X
    out = Path(out); out.mkdir(parents=True, exist_ok=True); paths = []
    def w(name, header, x, y):
        p = out / name
        with open(p, "w", newline="") as fh:
            wr = csv.writer(fh, lineterminator="\n"); wr.writerow(header); wr.writerows(zip(np.round(x, 6), np.round(y, 7)))
        paths.append(p)
    r = X.expected("odmr_ensemble"); s = r["series"]
    w("odmr_zero_field.csv", ["frequency_MHz", "signal"], r["x"], s["no magnet"])
    w("odmr_with_magnet.csv", ["frequency_MHz", "signal"], r["x"], np.array(s["magnet near (offset −0.04 for clarity)"]) + 0.04)
    P = X.expected("pulsed")["panels"]
    w("rabi.csv", ["time_us", "contrast"], *P["Rabi (µs)"]); w("ramsey.csv", ["time_us", "contrast"], *P["Ramsey (µs)"]); w("echo.csv", ["time_us", "contrast"], *P["Echo (µs)"])
    r = X.expected("arrhenius"); w("arrhenius.csv", ["inv_T_1000_per_K", "resistivity_ohm_cm"], r["x"], r["series"]["resistivity (Ω·cm)"])
    r = X.expected("fet_curves"); w("iv_vgs7.csv", ["vds_V", "id_mA"], r["x"], r["series"]["|V_GS| = 7 V"])
    P = X.expected("single_nv")["panels"]; w("g2.csv", ["tau_ns", "g2"], *P["g2"])
    return paths


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) < 2 or argv[0] not in FITTERS:
        print(__doc__); print("kinds:", ", ".join(FITTERS)); return 2
    x, y = load_csv(argv[1])
    res = fit(argv[0], x, y)
    print(res.summary())
    if "--json" in argv:
        print(json.dumps({"params": res.params, "errors": res.errors, "notes": res.notes}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
