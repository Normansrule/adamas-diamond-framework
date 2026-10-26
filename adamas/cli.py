"""One command for the whole framework:  adamas <command>  (or  python -m adamas <command>).

    adamas info                         version, contents, and the key findings
    adamas doctor                       which optional tools are installed, with install hints
    adamas fit KIND data.csv            fit experiment data (odmr, rabi, ramsey, echo, arrhenius, iv, g2)
    adamas estimate [--workload W] [--readout-us T] [--memory-ms M] [--gate-us G]
                                        size a room-temperature NV quantum computer
    adamas validate                     print the validation matrix
    adamas uncertainty [power|quantum]  Monte Carlo percentiles and the tornado ranking
    adamas findings                     headline numbers as JSON (the same ones the website and preprint use)
    adamas build [docs|site|figures]    regenerate generated documents, the website, or all figures
    adamas app [--browser] [--port N]   the website as a local app: native window with pywebview, else your browser
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TOOLS = [  # (name, how to detect, what it enables, install hint)
    ("stim + pymatching", "py:stim", "circuit-level error correction, native XZZX", "pip install stim pymatching"),
    ("klayout", "py:klayout", "GDS layout and design-rule checks", "pip install klayout"),
    ("ngspice", "bin:ngspice", "SPICE checks of the logic cells", "sudo apt install ngspice"),
    ("iverilog", "bin:iverilog", "Verilog simulation of DIA-4", "sudo apt install iverilog"),
    ("yosys", "bin:yosys", "logic synthesis", "sudo apt install yosys"),
    ("node", "bin:node", "website tests", "install Node.js 20 or newer"),
    ("pdflatex + latexmk", "bin:latexmk", "preprint, talk, poster", "sudo apt install texlive-latex-recommended texlive-latex-extra latexmk"),
    ("docker", "bin:docker", "OpenROAD place and route", "install Docker Engine"),
    ("mpremote", "bin:mpremote", "flash the A1 ODMR kit", "pip install mpremote pyserial"),
]


def _has(spec: str) -> bool:
    kind, name = spec.split(":")
    if kind == "bin":
        return shutil.which(name) is not None
    try:
        __import__(name); return True
    except ImportError:
        return False


def cmd_info(a) -> int:
    from . import __version__
    figs = len(list((ROOT / "docs" / "img").glob("fig*.png")))
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from refs_common import load
        refs = load(); nref, nver = len(refs), sum(r.status == "V" for r in refs)
    except Exception:            # noqa: BLE001  (installed without the repository)
        nref = nver = "?"
    print(f"ADAMAS {__version__}: diamond electronics and room-temperature NV quantum processors")
    print(f"  references {nref} ({nver} verified) · figures {figs} · modules {len(list((ROOT / 'adamas').glob('*.py')))}")
    try:
        from .site import findings
        F = findings()
        print(f"  power: ideal figure of merit {F['BFOMratio']}× silicon; SiC ÷ diamond inverter loss {F['PowerRatioRoom']}× at 300 K (bulk-doped drift), {F['PowerRatioHot']}× at 523 K")
        print(f"  qubits: coherence-limited Bell fidelity {F['FcohLow']} to {F['FcohHigh']}; measured 0.67 is below it (known discrepancy)")
        print(f"  error correction: native XZZX threshold {F['ThrXZZXBias']}% vs standard {F['ThrCSSBias']}% at bias 100 on CZ (CNOT ≤ {F['EtaCnot']})")
        print(f"  validation: {F['ValPass']} of {F['ValChecks']} checks pass")
    except Exception as e:     # noqa: BLE001
        print(f"  (findings unavailable: {e})")
    return 0


def cmd_doctor(a) -> int:
    ok = True
    print(f"Python {sys.version.split()[0]}")
    for name, spec, use, hint in TOOLS:
        has = _has(spec); ok &= has or name in ("docker", "mpremote")
        print(f"  {'✓' if has else '✗'} {name:20s} {use}" + ("" if has else f"   →  {hint}"))
    return 0 if ok else 1


def cmd_fit(a) -> int:
    from .fitting import main
    return main([a.kind, a.file] + (["--json"] if a.json else []))


def cmd_estimate(a) -> int:
    from . import resource
    names = list(resource.WORKLOADS)
    w = next((n for n in names if a.workload.lower() in n.lower()), None)
    if w is None:
        print("workloads:", "; ".join(names)); return 2
    n, st = resource.WORKLOADS[w]
    e = resource.estimate(n, st, a.readout_us, a.memory_ms, gate_us=a.gate_us)
    if e is None:
        print(f"{w}: no code distance reaches the target at {a.readout_us} µs readout (the code no longer scales)"); return 1
    print(f"{w} at {a.readout_us:g} µs readout, {a.memory_ms:g} ms memory, {a.gate_us:g} µs gates:")
    print(f"  code distance {e.distance} · {e.physical_qubits / 1e6:.1f} million physical qubits · die {e.die_side_mm:.1f} mm · runtime {e.runtime_hours / 24:.1f} days")
    return 0


def cmd_validate(a) -> int:
    from . import validation
    for r in validation.rows():
        print(f"  {'✓' if r.status == 'pass' else '!' if r.status != 'FAIL' else '✗'} [{r.kind:10s}] {r.check}: model {r.model:.4g}, reference {r.reference:.4g}")
    s = validation.summary(); print(f"{s['pass']} pass, {s['known discrepancy']} known discrepancy, {s['FAIL']} fail")
    return 1 if s["FAIL"] else 0


def cmd_uncertainty(a) -> int:
    from . import uncertainty as U
    mc = U.monte_carlo(a.study, a.samples)
    print(f"{mc['label']}: P10 {mc['p10']:.2f}, P50 {mc['p50']:.2f}, P90 {mc['p90']:.2f} (baseline {mc['baseline']:.2f})")
    for r in U.tornado(a.study):
        print(f"  {r['name']:26s} {r['y_low']:.3g} → {r['y_high']:.3g}")
    return 0


def cmd_findings(a) -> int:
    from .site import findings
    print(json.dumps(findings(), indent=2, ensure_ascii=False)); return 0


def cmd_build(a) -> int:
    if a.what == "docs":
        from . import action, experiments, glossary, loop, readme, traveler, validation
        print("wrote", action.write_golden())
        print("wrote", loop.write())
        for m in (traveler, experiments, glossary, validation, action, readme):
            print("wrote", m.write())
        return 0
    if a.what == "site":
        from .site import build
        print("built", build(a.out, offline=a.offline)); return 0
    return subprocess.call([sys.executable, str(ROOT / "examples" / "make_all_figures.py")])


def cmd_app(a) -> int:
    """Build the site once (rebuilt when the package version changes), serve it on localhost, open a window."""
    import functools
    import http.server
    import threading
    import webbrowser
    from . import __version__
    from .site import build
    out = Path(a.out) if a.out else ROOT / "site"
    stamp = out / "data" / "app_version.txt"
    if a.rebuild or not (out / "index.html").exists() or not stamp.exists() or stamp.read_text().strip() != __version__:
        from .site import VENDOR
        offline = not a.online and all((ROOT / "web" / "node_modules" / src).exists() for _, src, _, _ in VENDOR)
        if not a.online and not offline:
            print("web libraries not installed (cd web && npm ci); building with CDN links instead")
        print(f"building the site into {out}{' (offline libraries)' if offline else ''} ...", flush=True)
        build(out, offline=offline); stamp.write_text(__version__)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):        # keep the terminal clean
            pass
    handler = functools.partial(Quiet, directory=str(out))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", a.port), handler)
    url = f"http://127.0.0.1:{srv.server_address[1]}/{a.page}"
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"ADAMAS {__version__} at {url}  (Ctrl+C to stop)", flush=True)
    try:
        if not a.browser:
            try:
                import webview
                webview.create_window("ADAMAS", url, width=1440, height=920, background_color="#05070d")
                webview.start(); return 0
            except ImportError:
                print("tip: pip install pywebview  (or pip install -e \".[app]\") for a native window; opening your browser instead")
        webbrowser.open(url)
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        srv.shutdown()
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="adamas", description="ADAMAS: diamond electronics and room-temperature quantum processors",
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__.split("\n", 2)[2])
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("info").set_defaults(fn=cmd_info)
    sub.add_parser("doctor").set_defaults(fn=cmd_doctor)
    f = sub.add_parser("fit"); f.add_argument("kind"); f.add_argument("file"); f.add_argument("--json", action="store_true"); f.set_defaults(fn=cmd_fit)
    e = sub.add_parser("estimate"); e.add_argument("--workload", default="RSA"); e.add_argument("--readout-us", type=float, default=1000.0)
    e.add_argument("--memory-ms", type=float, default=1000.0, choices=[100.0, 1000.0]); e.add_argument("--gate-us", type=float, default=25.0); e.set_defaults(fn=cmd_estimate)
    sub.add_parser("validate").set_defaults(fn=cmd_validate)
    u = sub.add_parser("uncertainty"); u.add_argument("study", nargs="?", default="power", choices=["power", "quantum"]); u.add_argument("--samples", type=int, default=2000); u.set_defaults(fn=cmd_uncertainty)
    sub.add_parser("findings").set_defaults(fn=cmd_findings)
    b = sub.add_parser("build"); b.add_argument("what", nargs="?", default="docs", choices=["docs", "site", "figures"]); b.add_argument("--out", default="site")
    b.add_argument("--offline", action="store_true", help="site: bundle three.js, GSAP, Plotly, and fonts (needs npm ci in web/)"); b.set_defaults(fn=cmd_build)
    ap = sub.add_parser("app", help="open the website as a local app"); ap.add_argument("--browser", action="store_true", help="use the browser even if pywebview is installed")
    ap.add_argument("--port", type=int, default=0, help="port (default: any free port)"); ap.add_argument("--page", default="index.html", help="first page, for example action.html")
    ap.add_argument("--out", default="", help="where to build the site (default: site/ in the checkout)"); ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--online", action="store_true", help="load libraries from CDNs instead of bundling them"); ap.set_defaults(fn=cmd_app)
    a = p.parse_args(argv)
    if not getattr(a, "fn", None):
        p.print_help(); return 0
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
