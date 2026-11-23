"""Qubits on the Bloch sphere: the theory behind every Bloch-sphere picture in ADAMAS (v0.53.0).

A qubit's state is rho = (I + r . sigma) / 2 with r = (<X>, <Y>, <Z>) in the unit ball [nielsen2010]: pure states sit on the
surface, mixed states inside, and the purity is Tr rho^2 = (1 + |r|^2) / 2. For the nitrogen-vacancy (NV) electron spin the
north pole |0> is m_s = 0 (bright) and the south pole |1> is m_s = -1 (about 30 % dimmer) [doherty2013].

1. Bloch equations [bloch1946] in the frame rotating with the drive (time in microseconds, frequencies in MHz):
       dr/dt = 2 pi W x r - ( x / T2, y / T2, (z - z_eq) / T1 ),   W = (Omega cos phi, Omega sin phi, delta)
   Omega is the Rabi frequency, phi the drive phase, delta the detuning. `evolve` solves them exactly with the matrix
   exponential of the 4 x 4 affine generator; tests check it against the Lindblad master equation [lindblad1976] built
   with adamas.opensys.liouvillian (relaxation both ways at rates (1 +/- z_eq) / (2 T1), pure dephasing for the rest of 1/T2).
2. Gates are rotations: any single-qubit gate is, up to a global phase, R_n(theta) = exp(-i theta n . sigma / 2), a turn of
   the arrow by theta about the axis n [nielsen2010]. `axis_angle` reads n and theta from the 2 x 2 matrix.
   X, Y, Z: pi about x, y, z. H: pi about (x + z) / sqrt 2. S: pi/2 about z. T: pi/4 about z.
3. Entanglement shrinks the arrow: in the pure two-qubit state cos t |00> + sin t |11> each qubit on its own has
   r = (0, 0, cos 2t) and the pair's concurrence is C = |sin 2t| [wootters1998]. For every pure two-qubit state
   |r_A|^2 + C^2 = 1, so a maximally entangled qubit, seen alone, sits at the center: it has no direction of its own.
4. Room-temperature NV numbers (the same as adamas.opensys and adamas.qdl): T1 = 6 ms [jarmola2012]; Hahn-echo
   T2 = 1.8 ms in 12C-enriched diamond [balasubramanian2009]. Thermal equilibrium in the (m_s = 0, -1) pair is
   z_eq = tanh(h D / (2 k T)) with D the zero-field splitting [doherty2013] (adamas.nv): about 2e-4 at 300 K, so in the
   dark the arrow relaxes to the center, not to the north pole. Optical pumping puts it near the top (Device Library QDL-06);
   `reset_z` maps the pumped m_s = 0 population of adamas.photophysics onto the (0, -1) pair, assuming m_s = +1 and -1
   are equally populated.

Every Bloch-sphere animation on the website is computed by the browser twin web/assets/sim/bloch.js, checked against
the golden values `write_golden` writes (web/tests/bloch_golden.json).
"""
from __future__ import annotations

import math

import numpy as np
from scipy.linalg import expm

I2 = np.eye(2, dtype=complex)
SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI = (SX, SY, SZ)

T1_ROOM_US = 6000.0          # [jarmola2012], as adamas.opensys.cz_gate_fidelity(t1_ms=6.0)
T2_ROOM_US = 1800.0          # [balasubramanian2009], as adamas.qdl.T2_ROOM_MS
PUMP_PER_US = 0.5            # green-light pumping rate in the Qubit Lab: illustrative (v0.54.0)

GATES = {                    # name -> 2 x 2 unitary [nielsen2010]
    "X": SX, "Y": SY, "Z": SZ,
    "H": np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2),
    "S": np.diag([1, 1j]).astype(complex),
    "T": np.diag([1, np.exp(1j * math.pi / 4)]).astype(complex),
}


def bloch_vector(rho: np.ndarray) -> np.ndarray:
    """r = (Tr rho X, Tr rho Y, Tr rho Z)."""
    return np.array([float(np.real(np.trace(rho @ s))) for s in PAULI])


def density_matrix(r) -> np.ndarray:
    """rho = (I + r . sigma) / 2."""
    x, y, z = r
    return 0.5 * (I2 + x * SX + y * SY + z * SZ)


def purity(r) -> float:
    """Tr rho^2 = (1 + |r|^2) / 2: 1 on the surface, 1/2 at the center."""
    return 0.5 * (1.0 + float(np.dot(r, r)))


def p_minus1(r) -> float:
    """Probability of reading m_s = -1 (the south pole): (1 - z) / 2."""
    return 0.5 * (1.0 - float(r[2]))


def _rate(t_us: float) -> float:
    return 0.0 if t_us is None or not math.isfinite(t_us) or t_us <= 0 else 1.0 / t_us


def generator(rabi_mhz=0.0, detuning_mhz=0.0, phase=0.0, t1_us=math.inf, t2_us=math.inf, z_eq=0.0,
              pump_per_us=0.0, z_pump=1.0) -> np.ndarray:
    """4 x 4 matrix A with d/dt (x, y, z, 1) = A (x, y, z, 1): the Bloch equations [bloch1946].
    Green light (v0.54.0) adds a pumping rate pump_per_us that drives z toward z_pump and, because the optical cycle
    destroys the phase, removes x and y at the same rate (a schematic model; the rate is an illustrative input)."""
    w = 2 * math.pi * np.array([rabi_mhz * math.cos(phase), rabi_mhz * math.sin(phase), detuning_mhz])
    g1, g2, gp = _rate(t1_us), _rate(t2_us), max(0.0, pump_per_us)
    a = np.zeros((4, 4))
    a[:3, :3] = [[-g2 - gp, -w[2], w[1]], [w[2], -g2 - gp, -w[0]], [-w[1], w[0], -g1 - gp]]
    a[2, 3] = g1 * z_eq + gp * z_pump
    return a


def evolve(r0, t_us: float, **p) -> np.ndarray:
    """Bloch vector after t_us microseconds of the Bloch equations (exact)."""
    v = expm(generator(**p) * t_us) @ np.array([*r0, 1.0])
    return v[:3]


def trajectory(r0, t_us: float, steps: int = 200, **p) -> np.ndarray:
    """(steps + 1) x 3 points of the exact solution from 0 to t_us."""
    step = expm(generator(**p) * (t_us / steps))
    v, out = np.array([*r0, 1.0]), []
    for _ in range(steps + 1):
        out.append(v[:3].copy()); v = step @ v
    return np.array(out)


def lindblad_evolve(r0, t_us: float, rabi_mhz=0.0, detuning_mhz=0.0, phase=0.0, t1_us=math.inf, t2_us=math.inf, z_eq=0.0,
                    pump_per_us=0.0, z_pump=1.0):
    """The same evolution from the Lindblad master equation [lindblad1976] (adamas.opensys.liouvillian), as a check."""
    from .opensys import liouvillian
    w = 2 * math.pi * np.array([rabi_mhz * math.cos(phase), rabi_mhz * math.sin(phase), detuning_mhz])
    h = 0.5 * (w[0] * SX + w[1] * SY + w[2] * SZ)
    g1, g2 = _rate(t1_us), _rate(t2_us)
    gphi = g2 - g1 / 2
    if gphi < -1e-15:
        raise ValueError("T2 cannot exceed 2 T1")
    c = []
    if g1:
        c += [math.sqrt(g1 * (1 + z_eq) / 2) * np.array([[0, 1], [0, 0]], dtype=complex),     # |1> -> |0>, toward +z
              math.sqrt(g1 * (1 - z_eq) / 2) * np.array([[0, 0], [1, 0]], dtype=complex)]     # |0> -> |1>
    if gphi > 0:
        c.append(math.sqrt(gphi / 2) * SZ)
    if pump_per_us > 0:                       # pumping both ways toward z_pump, plus dephasing so x, y also decay at the pump rate
        gp = pump_per_us
        c += [math.sqrt(gp * (1 + z_pump) / 2) * np.array([[0, 1], [0, 0]], dtype=complex),
              math.sqrt(gp * (1 - z_pump) / 2) * np.array([[0, 0], [1, 0]], dtype=complex), math.sqrt(gp / 4) * SZ]
    rho = density_matrix(r0)
    v = expm(liouvillian(h, c) * t_us) @ rho.reshape(-1, order="F")
    return bloch_vector(v.reshape(2, 2, order="F"))


def projection_noise(p: float, shots: int) -> float:
    """Standard deviation of the measured fraction of m_s = -1 outcomes in `shots` ideal projective measurements:
    sqrt(p (1 - p) / shots), quantum projection noise [itano1993]."""
    return math.sqrt(max(0.0, p * (1 - p)) / shots)


def rotation(axis, angle: float) -> np.ndarray:
    """R_n(theta) = exp(-i theta n . sigma / 2)."""
    n = np.asarray(axis, dtype=float); n = n / np.linalg.norm(n)
    return math.cos(angle / 2) * I2 - 1j * math.sin(angle / 2) * (n[0] * SX + n[1] * SY + n[2] * SZ)


def axis_angle(u: np.ndarray) -> tuple[np.ndarray, float]:
    """Axis n and angle theta in [0, pi] with u = e^(i alpha) R_n(theta) [nielsen2010]."""
    v = u / np.sqrt(np.linalg.det(u))
    c = float(np.real(np.trace(v))) / 2
    if c < 0:
        v, c = -v, -c
    theta = 2 * math.acos(min(1.0, c))
    s = math.sin(theta / 2)
    if s < 1e-12:
        return np.array([0.0, 0.0, 1.0]), 0.0
    n = np.array([float(np.real(1j * np.trace(v @ p))) / (2 * s) for p in PAULI])
    n = n / np.linalg.norm(n)
    if abs(theta - math.pi) < 1e-9:          # a turn by pi about n equals one about -n: fix the sign (first nonzero > 0)
        k = next(i for i in range(3) if abs(n[i]) > 1e-9)
        if n[k] < 0:
            n = -n
    return np.round(n, 15) + 0.0, theta


def apply_gate(r, u: np.ndarray) -> np.ndarray:
    """Bloch vector of u rho u^dagger."""
    rho = density_matrix(r)
    return bloch_vector(u @ rho @ u.conj().T)


def reduced_bloch(psi: np.ndarray, qubit: int = 0) -> np.ndarray:
    """Bloch vector of one qubit of a two-qubit pure state (amplitudes in the order 00, 01, 10, 11)."""
    m = np.asarray(psi, dtype=complex).reshape(2, 2)
    rho = m @ m.conj().T if qubit == 0 else m.T @ m.conj()
    return bloch_vector(rho)


def concurrence(psi: np.ndarray) -> float:
    """Concurrence of a pure two-qubit state, |<psi| Y x Y |psi*>| [wootters1998]."""
    psi = np.asarray(psi, dtype=complex)
    return float(abs(psi.conj() @ np.kron(SY, SY) @ psi.conj()))


def partly_entangled(theta: float) -> np.ndarray:
    """cos theta |00> + sin theta |11>."""
    return np.array([math.cos(theta), 0, 0, math.sin(theta)], dtype=complex)


def thermal_z(t_k: float = 300.0) -> float:
    """Equilibrium z of the (m_s = 0, -1) pair at zero field: tanh(h D / (2 k T)), D from adamas.nv."""
    from .constants import H, KB
    from .nv import zero_field_splitting_mhz
    return math.tanh(H * zero_field_splitting_mhz(t_k) * 1e6 / (2 * KB * t_k))


def reset_z() -> float:
    """z after optical pumping, in the (0, -1) pair: (p0 - p_-1) / (p0 + p_-1) with p_+1 = p_-1 = (1 - p0) / 2,
    p0 from adamas.photophysics.polarization (simulated)."""
    from .photophysics import polarization
    p0 = float(polarization())
    pm = (1 - p0) / 2
    return (p0 - pm) / (p0 + pm)


def figure(out="docs/img"):
    """Figure 65: the qubit on the Bloch sphere. (a) relaxation with the room-temperature T1 and T2 of an NV spin;
    (b) gates as rotations; (c) entanglement shrinks each qubit's own arrow (simulated: exact formulas)."""
    from pathlib import Path
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(15, 6.4))

    def sphere(ax, title):
        u, v = np.linspace(0, 2 * np.pi, 40), np.linspace(0, np.pi, 20)
        ax.plot_wireframe(np.outer(np.cos(u), np.sin(v)), np.outer(np.sin(u), np.sin(v)), np.outer(np.ones_like(u), np.cos(v)),
                          color="#b8c4cc", lw=0.4, alpha=0.5)
        for d, lab in (((1.25, 0, 0), "x"), ((0, 1.25, 0), "y")):
            ax.plot([0, d[0]], [0, d[1]], [0, d[2]], color="#888888", lw=0.8); ax.text(*d, lab, color="#555555")
        ax.plot([0, 0], [0, 0], [-1.2, 1.2], color="#888888", lw=0.8)
        ax.text(0, 0, 1.3, "|0⟩  mₛ = 0", ha="center"); ax.text(0, 0, -1.45, "|1⟩  mₛ = −1", ha="center")
        ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_zlim(-1, 1); ax.set_box_aspect((1, 1, 1)); ax.set_axis_off()
        ax.view_init(elev=18, azim=-60); ax.set_title(title, fontsize=10.5)

    zq = thermal_z()
    ax = fig.add_subplot(1, 3, 1, projection="3d")
    sphere(ax, "(a) Relaxation, NV at room temperature\necho T₂ = 1.8 ms shrinks x, y; T₁ = 6 ms moves z to ≈ 0")
    tr = trajectory([1, 0, 0], 3 * T2_ROOM_US, 600, detuning_mhz=0.001, t1_us=T1_ROOM_US, t2_us=T2_ROOM_US, z_eq=zq)
    ax.plot(*tr.T, color="#00798c", lw=1.4, label="from +x: spirals in (echo-limited T₂; free precession decays faster, T₂*)")
    tr2 = trajectory([0, 0, -1], 3 * T1_ROOM_US, 200, t1_us=T1_ROOM_US, t2_us=T2_ROOM_US, z_eq=zq)
    ax.plot(*tr2.T, color="#d1495b", lw=2.2, label="from |1⟩: climbs to the center (T₁)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.02), fontsize=8.5, frameon=False)

    ax = fig.add_subplot(1, 3, 2, projection="3d")
    sphere(ax, "(b) Gates are rotations\n|0⟩ → H → S → T → X")
    r, cols = np.array([0.0, 0.0, 1.0]), {"H": "#00798c", "S": "#edae49", "T": "#9d7bff", "X": "#d1495b"}
    for g in ("H", "S", "T", "X"):
        n, th = axis_angle(GATES[g])
        pts = np.array([apply_gate(r, rotation(n, th * k / 40)) for k in range(41)])
        ax.plot(*pts.T, color=cols[g], lw=2.2, label=f"{g}: {_PI.get(round(th / math.pi, 6), f'{th:.3f} rad')} about ({n[0]:.2f}, {n[1]:.2f}, {n[2]:.2f})")
        r = pts[-1]
    ax.quiver(0, 0, 0, *r, color="#222222", lw=1.6, arrow_length_ratio=0.12)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.02), fontsize=8.5, frameon=False)

    ax = fig.add_subplot(1, 3, 3)
    th = np.linspace(0, math.pi / 2, 181)
    ax.plot(th / math.pi, [np.linalg.norm(reduced_bloch(partly_entangled(t))) for t in th], color="#00798c", lw=2.4,
            label="length of one qubit's own arrow |r|")
    ax.plot(th / math.pi, [concurrence(partly_entangled(t)) for t in th], color="#d1495b", lw=2.4, label="concurrence C [wootters1998]")
    ax.plot(th / math.pi, [purity(reduced_bloch(partly_entangled(t))) for t in th], color="#888888", lw=1.6, ls="--",
            label="purity of one qubit (1 + |r|²)/2")
    ax.set_xlabel("θ / π in  cos θ |00⟩ + sin θ |11⟩"); ax.set_ylim(0, 1.05)
    ax.set_title("(c) Entanglement shrinks each qubit's arrow:\n|r|² + C² = 1 for pure pairs", fontsize=10.5)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), fontsize=8.5, frameon=False)
    fig.suptitle("The qubit on the Bloch sphere (simulated: exact solutions; detuning 1 kHz in (a) is illustrative)", fontsize=12)
    fig.tight_layout()
    p = out / "fig65_bloch.png"; fig.savefig(p, dpi=150); plt.close(fig)
    return p


_PI = {1.0: "π", 0.5: "π/2", 0.25: "π/4"}


def golden() -> dict:
    """Values the browser twin (web/assets/sim/bloch.js) must reproduce."""
    cases = [
        ([0, 0, 1], 0.1, dict(rabi_mhz=5.0)),
        ([0, 0, 1], 0.37, dict(rabi_mhz=3.0, detuning_mhz=1.5, phase=0.7)),
        ([1, 0, 0], 2.0, dict(detuning_mhz=0.4, t1_us=50.0, t2_us=8.0, z_eq=0.2)),
        ([0.3, -0.5, 0.6], 1.3, dict(rabi_mhz=2.0, detuning_mhz=-0.8, phase=-1.1, t1_us=7.0, t2_us=3.0, z_eq=-0.4)),
        ([0, 0, -1], 9000.0, dict(t1_us=T1_ROOM_US, t2_us=T2_ROOM_US, z_eq=thermal_z())),
        ([0.4, 0.5, -0.6], 2.5, dict(rabi_mhz=1.5, detuning_mhz=0.2, t1_us=30.0, t2_us=6.0, pump_per_us=0.5, z_pump=0.8)),
    ]
    evo = [{"r0": list(map(float, r0)), "t": t, "p": p, "r": evolve(r0, t, **p).tolist()} for r0, t, p in cases]
    gates = {}
    for g, u in GATES.items():
        n, th = axis_angle(u)
        gates[g] = {"axis": n.tolist(), "angle": th,
                    "images": [apply_gate(r, u).tolist() for r in ([0, 0, 1], [1, 0, 0], [0, 1, 0], [0.2, -0.3, 0.5])]}
    ent = [[t, reduced_bloch(partly_entangled(t)).tolist(), concurrence(partly_entangled(t))] for t in (0, 0.2, math.pi / 8, 0.6, math.pi / 4, 1.3)]
    noise = [[p, n, projection_noise(p, n)] for p, n in ((0.5, 100), (0.1, 1000), (0.93, 37))]
    return {"evolve": evo, "gates": gates, "entangled": ent, "noise": noise, "pump_per_us": PUMP_PER_US, "thermal_z": thermal_z(), "reset_z": reset_z(),
            "t1_us": T1_ROOM_US, "t2_us": T2_ROOM_US}


def to_json() -> dict:
    """What the website's Bloch scenes need from Python."""
    return {"t1_us": T1_ROOM_US, "t2_us": T2_ROOM_US, "thermal_z": thermal_z(), "reset_z": reset_z()}


def write_golden(path: str = "web/tests/bloch_golden.json") -> str:
    import json
    from pathlib import Path
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(golden(), indent=1) + "\n", encoding="utf-8")
    return str(p)


def document() -> str:
    """docs/BLOCH.md: the qubit on the Bloch sphere, with every number computed here."""
    zq, rz = thermal_z(), reset_z()
    gl = []
    for g, u in GATES.items():
        n, th = axis_angle(u)
        gl.append(f"| {g} | {_PI.get(round(th / math.pi, 6), f'{th:.3f} rad')} | ({n[0]:.3f}, {n[1]:.3f}, {n[2]:.3f}) |")
    el = []
    for t in (0, math.pi / 12, math.pi / 8, math.pi / 6, math.pi / 4):
        r, c = reduced_bloch(partly_entangled(t)), concurrence(partly_entangled(t))
        el.append(f"| {t / math.pi:.4f} π | {np.linalg.norm(r):.3f} | {c:.3f} | {purity(r):.3f} |")
    end = evolve([1, 0, 0], 3 * T2_ROOM_US, detuning_mhz=0.001, t1_us=T1_ROOM_US, t2_us=T2_ROOM_US, z_eq=zq)
    return f"""# The qubit on the Bloch sphere

*Generated by `adamas.bloch` (`python -m adamas.cli build docs`); do not edit by hand. Figure 65: [docs/img/fig65_bloch.png](img/fig65_bloch.png).*

Every Bloch-sphere picture in ADAMAS (the [Qubit Lab](https://normansrule.github.io/adamas-diamond-framework/labs/qubit.html),
the Device Library, the Fab Journey and the Entanglement Lab) is computed from the formulas below. The browser twin
`web/assets/sim/bloch.js` is checked against this module by `web/tests/bloch.test.mjs`. All of it is **simulated**: exact
solutions of textbook equations with the room-temperature times cited below, not measurements.

## The state is an arrow

A qubit's state is ρ = (I + r·σ)/2 with r = (⟨X⟩, ⟨Y⟩, ⟨Z⟩) inside the unit ball [nielsen2010]. Pure states sit on the surface and
mixed states inside; the purity is Tr ρ² = (1 + |r|²)/2. For the nitrogen-vacancy (NV) electron spin, the north pole |0⟩ is
mₛ = 0, which fluoresces brighter, and the south pole |1⟩ is mₛ = −1, about 30 % dimmer [doherty2013] [gruber1997].
A measurement does not read the arrow: it returns mₛ = −1 with probability (1 − z)/2.

## Motion: the Bloch equations

In the frame rotating with the microwave drive [bloch1946]:

    dr/dt = 2π W × r − ( x/T₂, y/T₂, (z − z_eq)/T₁ ),   W = (Ω cos φ, Ω sin φ, δ)

Ω is the Rabi frequency, φ the drive phase and δ the detuning. A pulse turns the arrow about W (Rabi [rabi1937]); free time
turns it about z at δ (Ramsey [ramsey1950]); a π pulse in the middle of the free time undoes a static spread of δ (echo
[hahn1950]). `adamas.bloch.evolve` solves the equations exactly and the tests check it against the Lindblad master equation
[lindblad1976] of `adamas.opensys`.

Room-temperature NV numbers used everywhere in ADAMAS: T₁ = {T1_ROOM_US / 1000:g} ms [jarmola2012] and Hahn-echo
T₂ = {T2_ROOM_US / 1000:g} ms in carbon-12-enriched diamond [balasubramanian2009]. The thermal equilibrium of the
(mₛ = 0, −1) pair is z_eq = tanh(hD / 2kT) = {zq:.1e} at 300 K (D from `adamas.nv`), so **in the dark the arrow relaxes to the
center, not to the top**: started on the equator, it has length {np.linalg.norm(end):.3f} after 3 T₂ (Figure 65a). That decay uses
the Hahn-echo T₂, as if each spin's static detuning were refocused; an arrow precessing freely decays faster, with T₂*. Green light
pumps it up: the simulated optical pumping of `adamas.photophysics` gives z = {rz:.2f} in the (0, −1) pair, taking mₛ = ±1 as
equally populated.

## Light and shots in the Qubit Lab (v0.54.0)

With T₁ or T₂ set, every spin of the Qubit Lab's ensemble follows these equations exactly, each with its own static
detuning. The echo then shows what it can and cannot do: it undoes the static spread (T₂*) but still decays as e^(−τ/T₂).
Green light adds a pumping rate γ_p that drives z toward the optical-reset value above and removes x and y at the same rate,
because the optical cycle destroys the phase. This is a schematic model with an illustrative γ_p = {PUMP_PER_US:g} per µs, checked
against the Lindblad equation with pumping both ways plus dephasing. A shot is an ideal projective measurement: the fraction
of mₛ = −1 outcomes in n shots scatters by √(p(1 − p)/n), the quantum projection noise [itano1993]; for p = 0.5 and
100 shots that is {projection_noise(0.5, 100):.2f}. Real room-temperature readout adds photon shot noise on top (Device
Library QDL-05).

## Gates are turns

Every single-qubit gate is, up to a global phase, a rotation R_n(θ) = exp(−iθ n·σ/2) of the arrow [nielsen2010]
(`adamas.bloch.axis_angle` reads n and θ from the matrix):

| Gate | Turn θ | Axis n |
|---|---|---|
{chr(10).join(gl)}

## Entanglement shrinks each qubit's arrow

In the pure two-qubit state cos θ |00⟩ + sin θ |11⟩, each qubit seen alone has r = (0, 0, cos 2θ), and the pair's
concurrence is C = |sin 2θ| [wootters1998]. For every pure two-qubit state |r|² + C² = 1 (the tests check random states):

| θ | Length of one qubit's arrow | Concurrence C | Purity of one qubit |
|---|---|---|---|
{chr(10).join(el)}

A Bell pair leaves both arrows at the center. Nothing Alice does to her qubit changes Bob's arrow, whatever its length
[ghirardi1980]; for a Bell pair that arrow is the center, so in the Entanglement Lab Bob sees 50/50 whatever she does.

## Where the scenes appear

| Scene | What it shows | Where |
|---|---|---|
| Rabi | a resonant pulse turns \\|0⟩ to \\|1⟩ | Device Library QDL-08, QDL-27; Fab Journey B1.3 |
| Finding the dip | off resonance the arrow never reaches the bottom (pulsed picture of the dip) | Fab Journey A1.5, B1.2 |
| Ramsey | free precession turns a field into a phase | electron-spin sensing devices (QDL-12, 17, 19, 20, 21, 24); Fab Journey B1.4 |
| Echo | the π pulse refocuses the fan of spins | QDL-18; Fab Journey B1.5 |
| Gates | X, Y, Z, H, S, T as turns, with buttons | QDL-01 |
| Relaxation | T₂ shrinks the arrow on the equator; T₁ brings an arrow from \\|1⟩ to the center | QDL-01 |
| Reset | green light pumps the arrow up | QDL-06; Fab Journey B1.1 |
| Readout | the arrow is projected to a pole | QDL-05 |
| Entanglement | each qubit's own arrow shrinks | coupler and link devices (QDL-03, 04, 10, 11, 13 to 16); Fab Journey S18 (what the measured coupling would enable); Entanglement Lab |

Pulse lengths, Rabi frequencies, detunings and ensemble spreads inside the scenes are illustrative and labeled so; only
T₁, T₂, z_eq and the pumped z come from the cited sources or simulations above. Devices whose qubit is a nuclear spin or an
ensemble with other times (for example the nuclear Ramsey gyroscope, QDL-23) show no scene rather than an electron-spin one. These pictures show one qubit or one pair;
they say nothing about how a diamond processor compares with superconducting qubits.
"""


def write(path: str = "docs/BLOCH.md") -> str:
    from pathlib import Path
    Path(path).write_text(document(), encoding="utf-8")
    write_golden()
    return path
