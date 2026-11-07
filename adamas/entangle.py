"""Entanglement Lab: what shared entanglement can do, and the one thing it cannot do (send a message on its own).

Everything here is computed with small density matrices (numpy), so each claim is checked by code and tests:

* No-signaling (no-communication theorem [ghirardi1980]): whatever Alice does to her half of an entangled pair
  (nothing, a measurement in any basis, any unitary), Bob's reduced state, and therefore every statistic he can measure,
  is unchanged. `no_signaling_check` tests this on random states and random operations; `signaling_game` plays the
  natural attempt (Alice picks her measurement basis to encode a bit) and shows Bob guesses at exactly 50 %.
* Teleportation [bennett1993]: a shared pair plus Alice's two classical bits moves an unknown qubit to Bob with
  fidelity 1. Without the bits Bob holds I/2 (fidelity 1/2 for every input); a classical strategy without
  entanglement (measure in Z, send the result, re-prepare) reaches 2/3 on average, computed here.
* Bell test (CHSH [clauser1969]): local hidden variables give |S| <= 2; quantum mechanics reaches 2 sqrt(2)
  [cirelson1980]; a Werner state of visibility v gives S = 2 sqrt(2) v, so a violation needs v > 1/sqrt(2).
* Light-time: the classical bits travel no faster than light, so teleportation over a distance L takes at least L / c.

Labels: no-signaling and the CHSH bounds are theorems; teleportation and Bell violations between NV centers are
demonstrated, at cryogenic temperature only [bernien2013] [hensen2015] [pompili2021] [hermans2022]; storing pre-shared
entanglement in room-temperature nuclear memories for later use is proposed (TIMELINE).
"""
from __future__ import annotations

import math

import numpy as np

C_M_S = 299_792_458.0                       # speed of light in vacuum, m/s (exact, SI definition)

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)


# ------------------------------------------------------------------ states and operations ---------------------------
def ket(*bits: int) -> np.ndarray:
    v = np.zeros(2 ** len(bits), dtype=complex); v[int("".join(map(str, bits)), 2)] = 1.0
    return v


def bell(name: str = "phi+") -> np.ndarray:
    """The four Bell states as vectors on qubits (A, B)."""
    s = 1 / math.sqrt(2)
    return {"phi+": s * (ket(0, 0) + ket(1, 1)), "phi-": s * (ket(0, 0) - ket(1, 1)),
            "psi+": s * (ket(0, 1) + ket(1, 0)), "psi-": s * (ket(0, 1) - ket(1, 0))}[name]


def dm(v: np.ndarray) -> np.ndarray:
    return np.outer(v, v.conj())


def werner(v: float) -> np.ndarray:
    """v |Phi+><Phi+| + (1 - v) I/4: a Bell pair mixed with white noise (visibility v)."""
    return v * dm(bell("phi+")) + (1 - v) * np.eye(4) / 4


def ptrace_a(rho: np.ndarray) -> np.ndarray:
    """Bob's reduced state: trace out qubit A of a two-qubit density matrix."""
    return np.einsum("abad->bd", rho.reshape(2, 2, 2, 2))


def haar_unitary(rng: np.random.Generator) -> np.ndarray:
    z = (rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))) / math.sqrt(2)
    q, r = np.linalg.qr(z); d = np.diag(r)
    return q * (d / np.abs(d))


def random_state(rng: np.random.Generator, rank: int = 4) -> np.ndarray:
    """Random two-qubit density matrix (entangled with high probability)."""
    g = rng.normal(size=(4, rank)) + 1j * rng.normal(size=(4, rank)); rho = g @ g.conj().T
    return rho / np.trace(rho).real


def random_qubit(rng: np.random.Generator) -> np.ndarray:
    return haar_unitary(rng) @ np.array([1, 0], dtype=complex)


def alice_measures(rho: np.ndarray, u: np.ndarray) -> list[tuple[float, np.ndarray]]:
    """Alice measures her qubit in the basis {U|0>, U|1>}. Returns (probability, Bob's conditional state) per outcome."""
    out = []
    for k in range(2):
        e = u[:, k]; p = np.kron(np.outer(e, e.conj()), I2)
        post = p @ rho @ p; pr = float(np.trace(post).real)
        out.append((pr, ptrace_a(post) / pr if pr > 1e-15 else np.zeros((2, 2), complex)))
    return out


def trace_distance(a: np.ndarray, b: np.ndarray) -> float:
    return 0.5 * float(np.sum(np.abs(np.linalg.eigvalsh(a - b))))


# ------------------------------------------------------------------ no-signaling ------------------------------------
def bob_view(rho: np.ndarray, action: str, u: np.ndarray | None = None) -> np.ndarray:
    """Bob's reduced state after Alice's action, averaged over her outcomes (he does not know them):
    'nothing', 'measure' in basis u, or 'unitary' u on her qubit."""
    if action == "nothing":
        return ptrace_a(rho)
    if action == "measure":
        return sum(p * s for p, s in alice_measures(rho, u))
    if action == "unitary":
        w = np.kron(u, I2); return ptrace_a(w @ rho @ w.conj().T)
    raise ValueError(action)


def no_signaling_check(trials: int = 200, seed: int = 0) -> dict:
    """Largest trace distance between Bob's state with Alice idle and after a random measurement or unitary, over
    random states. The theorem says 0; the result is floating-point round-off. For comparison, the largest change of
    Bob's CONDITIONAL state (if he were told Alice's outcome) is order 1: the correlations are real, but invisible to
    Bob until a classical message arrives."""
    r = np.random.default_rng(seed); worst = 0.0; cond = 0.0
    for _ in range(trials):
        rho = random_state(r); base = bob_view(rho, "nothing"); u = haar_unitary(r)
        worst = max(worst, trace_distance(base, bob_view(rho, "measure", u)), trace_distance(base, bob_view(rho, "unitary", u)))
        cond = max(cond, max(trace_distance(base, s) for _, s in alice_measures(rho, u)))
    return {"trials": trials, "max_change": worst, "max_conditional_change": cond}


def signaling_game(rounds: int = 10_000, seed: int = 1) -> dict:
    """Alice tries to send bit b through a Bell pair alone: she measures in Z for b = 0 and in X for b = 1. Bob
    measures in Z and guesses b from his outcome. Exact probabilities and a sampled run. P(Bob sees 0 | b) is 1/2 for
    both bits, so every guessing rule is right half the time."""
    rho = dm(bell("phi+")); bases = {0: I2, 1: H}
    p0 = {b: float(bob_view(rho, "measure", bases[b])[0, 0].real) for b in (0, 1)}
    r = np.random.default_rng(seed); bits = r.integers(0, 2, rounds)
    seen = (r.random(rounds) >= np.array([p0[b] for b in bits])).astype(int)      # Bob's outcome
    correct = float(np.mean(seen == bits))                                        # rule "guess my outcome" (any rule gives 1/2)
    return {"p_bob0_given_bit": p0, "rounds": rounds, "correct": correct, "se": math.sqrt(0.25 / rounds)}


# ------------------------------------------------------------------ teleportation -----------------------------------
BELL_OUTCOMES = (("phi+", (0, 0)), ("psi+", (0, 1)), ("phi-", (1, 0)), ("psi-", (1, 1)))   # Bell state, bits (m1, m2)


def teleport(psi: np.ndarray, use_bits: bool = True, resource: np.ndarray | None = None) -> list[tuple[float, np.ndarray]]:
    """Qubits: 0 = Alice's unknown state, 1 = Alice's half of the shared pair, 2 = Bob's half. The pair is `resource`
    (default |Phi+><Phi+|; a Werner state models a noisy link). Alice measures qubits 0 and 1 in the Bell basis, which
    gives two classical bits (m1, m2). With the bits Bob applies Z^m1 X^m2; without them he does nothing.
    Returns (probability, Bob's density matrix) per outcome [bennett1993]."""
    res = dm(bell("phi+")) if resource is None else resource
    rho = np.kron(dm(psi), res)
    out = []
    for name, (m1, m2) in BELL_OUTCOMES:
        m = np.kron(bell(name).conj()[None, :], I2)              # (<Bell|_01 (x) I_2), a 2 x 8 map
        bob = m @ rho @ m.conj().T; pr = float(np.trace(bob).real)
        if pr < 1e-15:
            out.append((0.0, np.zeros((2, 2), complex))); continue
        bob = bob / pr
        if use_bits:
            c = np.linalg.matrix_power(Z, m1) @ np.linalg.matrix_power(X, m2); bob = c @ bob @ c.conj().T
        out.append((pr, bob))
    return out


def teleport_fidelity(psi: np.ndarray, use_bits: bool = True, resource: np.ndarray | None = None) -> float:
    """Average fidelity <psi| rho_Bob |psi> over Alice's outcomes. With a Werner pair of visibility v and the bits it is
    (1 + v) / 2 for every input; without the bits it is 1/2."""
    return float(sum(p * np.vdot(psi, s @ psi).real for p, s in teleport(psi, use_bits, resource)))


def measure_and_prepare_fidelity(trials: int = 20_000, seed: int = 2) -> dict:
    """No entanglement: Alice measures her unknown qubit in Z, phones the result, Bob prepares |0> or |1>. Average
    fidelity over random inputs (exact value 2/3 for this strategy) with its sampling error."""
    r = np.random.default_rng(seed); f = np.empty(trials)
    for i in range(trials):
        psi = random_qubit(r); p0 = abs(psi[0]) ** 2
        f[i] = p0 * p0 + (1 - p0) * (1 - p0)                  # outcome k with prob |psi_k|^2, fidelity |psi_k|^2
    return {"trials": trials, "mean": float(f.mean()), "se": float(f.std(ddof=1) / math.sqrt(trials))}


def teleport_check(trials: int = 200, seed: int = 3) -> dict:
    r = np.random.default_rng(seed); w, wo, bob_avg = [], [], 0.0
    for _ in range(trials):
        psi = random_qubit(r); w.append(teleport_fidelity(psi, True)); wo.append(teleport_fidelity(psi, False))
        avg = sum(p * s for p, s in teleport(psi, False)); bob_avg = max(bob_avg, trace_distance(avg, I2 / 2))
    return {"trials": trials, "min_with_bits": min(w), "max_without_bits": max(wo), "min_without_bits": min(wo),
            "bob_without_bits_vs_mixed": bob_avg}


def light_time_s(distance_m: float) -> float:
    """Shortest time for the two classical bits to cover distance_m: the vacuum speed of light (fiber is slower)."""
    return distance_m / C_M_S


def joint_probabilities(rho: np.ndarray, a: float, b: float) -> np.ndarray:
    """P(Alice k, Bob l) when both measure along angles a, b in the X-Z plane (outcome 0 = +1). For a Werner state this
    is (1 + (-1)^(k+l) v cos(a - b)) / 4, so Bob's own column sums are 1/2 whatever Alice chooses."""
    def proj(t, k):
        e = np.array([math.cos(t / 2), math.sin(t / 2)], dtype=complex) if k == 0 else np.array([-math.sin(t / 2), math.cos(t / 2)], dtype=complex)
        return np.outer(e, e.conj())
    return np.array([[float(np.trace(rho @ np.kron(proj(a, k), proj(b, l))).real) for l in (0, 1)] for k in (0, 1)])


# ------------------------------------------------------------------ CHSH --------------------------------------------
def correlator(rho: np.ndarray, a: float, b: float) -> float:
    """E(a, b) = <(cos a Z + sin a X) (x) (cos b Z + sin b X)> for measurement angles in the X-Z plane."""
    A = math.cos(a) * Z + math.sin(a) * X; B = math.cos(b) * Z + math.sin(b) * X
    return float(np.trace(rho @ np.kron(A, B)).real)


def chsh(rho: np.ndarray, a=0.0, a2=math.pi / 2, b=math.pi / 4, b2=-math.pi / 4) -> float:
    """S = E(a,b) + E(a,b') + E(a',b) - E(a',b'); the default angles are optimal for |Phi+> [clauser1969]."""
    return correlator(rho, a, b) + correlator(rho, a, b2) + correlator(rho, a2, b) - correlator(rho, a2, b2)


LOCAL_BOUND = 2.0                            # [clauser1969]
TSIRELSON = 2 * math.sqrt(2)                 # [cirelson1980]


def werner_threshold() -> float:
    """Visibility above which a Werner state violates CHSH at the optimal angles: S = 2 sqrt(2) v > 2."""
    return LOCAL_BOUND / TSIRELSON


# ------------------------------------------------------------------ timeline ----------------------------------------
TIMELINE = [  # (year, ref, what, label); distances and counts as in the cited papers
    (1980, "ghirardi1980", "No-communication theorem: measuring one half of an entangled pair cannot send a signal", "theorem"),
    (1991, "ekert1991", "Entanglement-based key distribution (E91): a shared secret key, with a classical channel to compare settings", "theory proposal, demonstrated since"),
    (1992, "bennett1992", "BBM92 key distribution with entangled pairs, again with a classical channel", "theory proposal, demonstrated since"),
    (1993, "bennett1993", "Teleportation: one shared pair plus two classical bits moves an unknown qubit", "theory proposal, demonstrated since"),
    (2013, "bernien2013", "Heralded entanglement of two NV centers 3 m apart, through photons", "demonstrated, cryogenic"),
    (2015, "hensen2015", "Loophole-free Bell violation with NV electron spins 1.3 km apart", "demonstrated, cryogenic"),
    (2017, "kalb2017", "Entanglement distillation between two NV network nodes", "demonstrated, cryogenic"),
    (2018, "humphreys2018", "Deterministic delivery of remote entanglement (entanglement ready before it is needed)", "demonstrated, cryogenic"),
    (2021, "pompili2021", "Multinode (three-node) network of NV qubits", "demonstrated, cryogenic"),
    (2022, "hermans2022", "Teleportation between non-neighbouring nodes (classical bits still sent)", "demonstrated, cryogenic"),
    (2024, "stolk2024", "Metropolitan-scale heralded entanglement of solid-state qubits", "demonstrated, cryogenic"),
    (None, "maurer2012", "Pre-share entanglement, store it in room-temperature nuclear memories, use it later with a classical message only (the cited source reports more than 1 s of memory for one local ¹³C spin, not a shared pair)", "proposed (this program)"),
]


def pre_shared_reach_km(memory_s: float = 1.0) -> float:
    """How far the classical message can travel while a memory holds its half of a pre-shared pair: c x memory time.
    An upper bound only; storing remote entanglement at room temperature has not been demonstrated."""
    return C_M_S * memory_s / 1e3


def to_json() -> dict:
    ns, game, tp, mp = no_signaling_check(), signaling_game(), teleport_check(), measure_and_prepare_fidelity()
    v = np.linspace(0, 1, 41)
    return {"no_signaling": ns, "game": game, "teleport": tp, "measure_prepare": mp,
            "chsh": {"local": LOCAL_BOUND, "tsirelson": TSIRELSON, "bell": chsh(dm(bell("phi+"))), "threshold": werner_threshold(),
                     "werner_v": v.tolist(), "werner_s": [chsh(werner(x)) for x in v]},
            "timeline": [{"year": y, "ref": k, "what": w, "label": lab} for y, k, w, lab in TIMELINE],
            "light_ms_1300m": 1e3 * light_time_s(1300.0), "pre_shared_reach_km": pre_shared_reach_km()}


def golden() -> dict:
    """Values at fixed inputs for the browser twin (web/assets/sim/entangle.js), computed with density matrices."""
    r = np.random.default_rng(7); vs = (0.0, 0.5, 1 / math.sqrt(2), 0.9, 1.0)
    angles = ((0.0, 0.0), (0.0, math.pi / 4), (math.pi / 2, math.pi / 4), (1.0, -0.3), (math.pi / 2, -math.pi / 4))
    joint = [[v, a, b, joint_probabilities(werner(v), a, b).tolist()] for v in vs for a, b in angles]
    tele = []
    for v in vs:
        psi = random_qubit(r)
        tele.append([v, teleport_fidelity(psi, True, werner(v)), teleport_fidelity(psi, False, werner(v))])
    odd = (0.3, 1.2, -0.4, 2.0)
    return {"joint": joint, "teleport": tele, "chsh": [[v, chsh(werner(v))] for v in vs],
            "chsh_angles": [[v, *odd, chsh(werner(v), *odd)] for v in vs],
            "light_ms": [[km, 1e3 * light_time_s(km * 1e3)] for km in (1.3, 10.0, 1000.0)]}


def write_golden(path: str = "web/tests/entangle_golden.json") -> str:
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / path
    p.write_text(json.dumps(golden(), indent=1) + "\n", encoding="utf-8"); return str(p)


def document() -> str:
    """docs/ENTANGLEMENT.md, with every number computed here."""
    ns, game, tp, mp = no_signaling_check(), signaling_game(), teleport_check(), measure_and_prepare_fidelity()
    rows = "\n".join(f"| {y if y else 'next'} | {w} | {lab} | [{k}] |" for y, k, w, lab in TIMELINE)
    return f"""# Entanglement without a wire: what it can and cannot do

Generated by `adamas.entangle` (`adamas build docs`); do not edit by hand. Every number below is computed by that module
and checked by `tests/test_entangle.py`. Try it in the [Entanglement Lab](../web/labs/entangle.html).

## The short answer

Entanglement alone cannot carry a message. Two parties who share entangled pairs see correlated results, but each one's
own results are random coin flips whatever the other does. The correlation only shows up when the two lists are
compared, and comparing them needs an ordinary (classical) channel, which travels no faster than light. This is the
no-communication theorem [ghirardi1980], and it follows from quantum mechanics itself, not from today's engineering.

What entanglement does give, with a classical channel alongside:

| Use | What it needs besides the shared pairs | Status |
|---|---|---|
| Teleportation of an unknown qubit [bennett1993] | 2 classical bits per qubit | Demonstrated between NV centers, cryogenic only [hermans2022] |
| Entanglement-based key distribution (E91 by Ekert, BBM92 by Bennett, Brassard and Mermin) [ekert1991] [bennett1992] | A public classical channel to compare settings | Proposed for NV nodes here; not built |
| Bell tests [clauser1969] | A classical channel to compare results | Loophole-free with NV centers 1.3 km apart, cryogenic [hensen2015] |
| Sending a message with no classical channel | Impossible [ghirardi1980] | Theorem |

And the entangled pairs themselves have to be delivered first: in every network of nitrogen-vacancy (NV) centers so far by photons through fiber,
heralded by a detection at a station between the nodes [bernien2013] [humphreys2018] [pompili2021] [stolk2024].

## 1. No-signaling, checked numerically

`no_signaling_check` takes {ns['trials']} random two-qubit states and, for each, a random measurement basis and a random unitary
on Alice's side. It compares Bob's density matrix (everything he can ever measure) before and after.

* Largest change, in trace distance: **{ns['max_change']:.1e}** (floating-point round-off; the theorem says exactly 0).
* For contrast, Bob's state *conditioned on Alice's result* changes by up to **{ns['max_conditional_change']:.2f}**: the
  correlation is real, but Bob cannot see it without being told Alice's result.

`signaling_game` plays the natural attempt: Alice measures her half of |Φ⁺⟩ in Z to send 0 and in X to send 1; Bob
measures in Z. P(Bob sees 0) is {game['p_bob0_given_bit'][0]:.3f} for bit 0 and {game['p_bob0_given_bit'][1]:.3f} for bit 1.
Over {game['rounds']:,} simulated rounds Bob guessed right {100 * game['correct']:.1f} % of the time (sampling error
{100 * game['se']:.1f} %). Copying his qubit to take more looks is ruled out too: an unknown quantum state cannot be cloned [wootters1982].

## 2. Teleportation needs the two bits

`teleport` follows [bennett1993] with density matrices. Over {tp['trials']} random input states:

* With Alice's two classical bits and Bob's correction: fidelity at least **{tp['min_with_bits']:.6f}** (exactly 1).
* Without the bits: fidelity between **{tp['min_without_bits']:.4f}** and **{tp['max_without_bits']:.4f}**; Bob's
  state is the maximally mixed state I/2 (largest difference {tp['bob_without_bits_vs_mixed']:.1e}). He learns nothing.
* With a noisy pair (a Werner state of visibility v) and the bits: (1 + v)/2.
* No entanglement at all, measure in Z and phone the result: **{mp['mean']:.4f} ± {mp['se']:.4f}** over {mp['trials']:,}
  random inputs (exactly 2/3 for this strategy). A noisy pair beats it only when v > 1/3.

The bits travel at most at the speed of light, so teleporting across 1.3 km (the [hensen2015] separation) takes at least
{1e6 * light_time_s(1300.0):.2f} µs. Nothing arrives before the classical message does.

## 3. Bell test (CHSH, Clauser–Horne–Shimony–Holt): why the correlation is not a hidden message

Any local hidden-variable account gives |S| ≤ {LOCAL_BOUND:.0f} [clauser1969]; quantum mechanics reaches 2√2 =
{TSIRELSON:.4f} [cirelson1980], which `chsh` reproduces for |Φ⁺⟩ ({chsh(dm(bell("phi+"))):.4f}). A Werner state of
visibility v gives S = 2√2 v, so a violation needs v > {werner_threshold():.4f} (1/√2). Even at the maximum, each side's
results stay 50/50: the violation is a property of the comparison.

## 4. What exists, and what is only proposed

| Year | What | Label | Source |
|---|---|---|---|
{rows}

Every NV network experiment in the table ran at cryogenic temperature; none has been reported at room temperature.
This program's room-temperature devices do not distribute entanglement.

The last row is the only room-temperature idea: distribute pairs ahead of time (still through photons), park each half
in a ¹³C nuclear memory, and later use them with only a classical message. During one second of storage a classical
message can cover at most {pre_shared_reach_km():,.0f} km. It is **proposed**: nobody has stored remote entanglement in a
room-temperature memory, and the more-than-1-s figure [maurer2012] is for a single local spin, not a shared pair.

## Assumptions and validity

* Ideal, instantaneous projective measurements and unitaries on qubits; noise only as a Werner (depolarized) pair.
* No-signaling holds for every operation Alice can do locally, including noisy ones (any completely positive,
  trace-preserving map on her qubit); the check samples measurements and unitaries only.
* Light-time uses the vacuum speed of light, a lower bound; real fiber is slower.
"""


def write(path: str = "docs/ENTANGLEMENT.md") -> str:
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / path
    p.write_text(document(), encoding="utf-8"); write_golden()
    return str(p)
