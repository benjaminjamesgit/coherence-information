"""Coherence channel capacity estimator (v0.6.0).

Implements the Coherence Capacity Theorem (James, 2025, Capacity and
Compression Theorems, Thm 4.1):

    C_C = max_{p(x)} I_w(X; Y)

for a fixed discrete memoryless channel p(y | x) and fixed coherence weights
w(x) in [0, 1], maximized over the input simplex. When w(x) = 1 for all x,
C_C collapses exactly to the Shannon channel capacity (Cor 4.4) -- the
boundary condition that licenses CIT as a generalization, not a replacement.

The objective is the repository's coherence-weighted mutual information
(``cit.information.coherence_weighted_mutual_information``) evaluated at the
candidate input distribution, so the estimator inherits the boundary-condition
spine unchanged.

Solver (pre-registered v0.6.0, see pre_registration.md 2026-06-23): projected
-gradient ascent on the probability simplex from a *deterministic* multi-start
set (centroid + vertices + a resolution-m simplex lattice), taking the best
local optimum. The gradient is analytic (``_iw_input_gradient``), verified
against finite differences in the test suite. There is no RNG, so the
estimator is bit-exact reproducible. The deterministic-lattice multi-start is
locked for small alphabets only; larger alphabets raise (a seeded-sampling
amendment would be required and is out of v0.6.0 scope).

Concavity of I_w in p(x) is OPEN: the w(x) factor breaks the standard
I(X; Y)-concavity argument, and no source document proves it. Multi-start
agreement is the empirical uniqueness stand-in, surfaced as
``argmax_agreement_linf`` in the return dict.

Note on the Binary Coherence Channel fixture: the paper's Sec 6 closed form
C_C(eps) = 0.5(1 + eps) is I_w evaluated at the *uniform* input, which is NOT
the capacity-achieving input for eps < 1. It is a lower bound on C_C (equal
only at eps = 1). See the 2026-06-23 v0.6.0 amendment for the corrected curve.

References
----------
James, B. (2025). Formal Foundations of Coherence Information Theory:
    Capacity and Compression Theorems. PhilPapers.
"""

from __future__ import annotations

from math import comb, log

import numpy as np
from numpy.typing import ArrayLike, NDArray

from cit.information import coherence_weighted_mutual_information

__all__ = ["coherence_capacity"]

# Pre-registered solver constants (v0.6.0).
_TOL = 1e-10          # objective-improvement stop, per start
_MAX_ITER = 2000      # outer projected-gradient iterations, per start
_LATTICE_M = 20       # simplex-lattice resolution
_LATTICE_CAP = 10000  # max lattice points; beyond this the alphabet is "large"

# Armijo backtracking line-search constants (standard optimizer defaults, not
# tuned to any data; the pre-registered step rule is "projected-gradient
# ascent" with an adaptive step, so no learning-rate magic constant is locked).
_LS_SHRINK = 0.5
_LS_C1 = 1e-4
_LS_MAX_BACKTRACK = 60

# Objective band defining "near-optimal" starts for the agreement diagnostic.
_AGREE_BAND = 1e-6
# Numerical guard: keep starts strictly interior so p(y) > 0 at the first
# gradient even when a start is a simplex vertex.
_INTERIOR = 1e-12


def _check_channel(P: NDArray[np.float64]) -> None:
    if P.ndim != 2:
        raise ValueError(f"Channel must be 2D (n_x, n_y); got ndim={P.ndim}.")
    if np.any(P < 0):
        raise ValueError("Channel probabilities must be non-negative.")
    rows = P.sum(axis=1)
    if not np.allclose(rows, 1.0, atol=1e-9):
        raise ValueError("Each channel row p(y | x) must sum to 1.")


def _objective(p: NDArray, channel: NDArray, weights: NDArray, base: float) -> float:
    """I_w(X; Y) at input pmf ``p`` -- the repo's coherence-weighted MI."""
    return coherence_weighted_mutual_information(p[:, None] * channel, weights, base=base)


def _iw_input_gradient(
    p: ArrayLike, channel: ArrayLike, weights: ArrayLike, base: float = 2.0
) -> NDArray[np.float64]:
    """Analytic gradient of I_w(X; Y) with respect to the input pmf p(x).

    dI_w/dp(k) = w(k) * D( p(.|k) || p_Y )  -  (1 / ln base) * sum_y p(y|k) g(y)/p_Y(y)

    where p_Y(y) = sum_x p(x) p(y|x) and g(y) = sum_x p(x) w(x) p(y|x). At
    w = 1 this reduces to D(p(.|k) || p_Y) - log_base(e), the classical
    mutual-information capacity gradient.
    """
    p = np.asarray(p, dtype=np.float64)
    P = np.asarray(channel, dtype=np.float64)
    w = np.asarray(weights, dtype=np.float64)
    ln_base = log(base)

    py = p @ P                       # p_Y(y), shape (n_y,)
    g = (p * w) @ P                  # g(y),   shape (n_y,)
    safe_py = np.maximum(py, 1e-300)
    log_py = np.log(safe_py) / ln_base

    log_P = np.where(P > 0, np.log(np.maximum(P, 1e-300)) / ln_base, 0.0)
    D = np.where(P > 0, P * (log_P - log_py[None, :]), 0.0).sum(axis=1)  # (n_x,)
    correction = (P @ (g / safe_py)) / ln_base                          # (n_x,)
    return w * D - correction


def _project_simplex(v: NDArray[np.float64]) -> NDArray[np.float64]:
    """Euclidean projection of v onto {x >= 0, sum x = 1} (Duchi et al.)."""
    n = v.shape[0]
    u = np.sort(v)[::-1]
    css = np.cumsum(u) - 1.0
    ind = np.arange(1, n + 1)
    cond = u - css / ind > 0
    rho = ind[cond][-1]
    theta = css[cond][-1] / rho
    return np.maximum(v - theta, 0.0)


def _ascend(p0, channel, weights, base, tol, max_iter):
    """Projected-gradient ascent with Armijo backtracking from one start."""
    n = p0.shape[0]
    p = _project_simplex(np.asarray(p0, dtype=np.float64))
    p = (1.0 - _INTERIOR) * p + _INTERIOR * np.full(n, 1.0 / n)  # interior guard
    f = _objective(p, channel, weights, base)
    for _ in range(max_iter):
        grad = _iw_input_gradient(p, channel, weights, base)
        t = 1.0
        stepped = False
        for _ in range(_LS_MAX_BACKTRACK):
            p_new = _project_simplex(p + t * grad)
            f_new = _objective(p_new, channel, weights, base)
            inner = float(grad @ (p_new - p))
            if f_new > f and f_new - f >= _LS_C1 * inner:
                stepped = True
                break
            t *= _LS_SHRINK
        if not stepped:
            break
        gain = f_new - f
        p, f = p_new, f_new
        if gain < tol:
            break
    return p, f


def _start_points(n: int, m: int, cap: int):
    """Deterministic multi-start: centroid + vertices + resolution-m lattice."""
    n_lattice = comb(m + n - 1, n - 1)
    if n_lattice > cap:
        raise ValueError(
            f"Deterministic-lattice multi-start would need {n_lattice} starts "
            f"for n={n} inputs at resolution m={m} (cap {cap}); this estimator "
            "is locked for small alphabets only. Larger alphabets require a "
            "seeded-sampling amendment (pre_registration.md v0.6.0)."
        )

    def compositions(k, total):
        if k == 1:
            yield (total,)
            return
        for first in range(total + 1):
            for rest in compositions(k - 1, total - first):
                yield (first,) + rest

    starts: dict = {}

    def add(vec: NDArray[np.float64]) -> None:
        key = tuple(np.round(vec, 9))
        if key not in starts:
            starts[key] = np.asarray(vec, dtype=np.float64)

    for comp in compositions(n, m):
        add(np.asarray(comp, dtype=np.float64) / m)
    add(np.full(n, 1.0 / n))                       # centroid
    for k in range(n):                             # vertices
        e = np.zeros(n)
        e[k] = 1.0
        add(e)
    return list(starts.values())


def coherence_capacity(
    channel: ArrayLike,
    weights: ArrayLike | None = None,
    *,
    base: float = 2.0,
    tol: float = _TOL,
    max_iter: int = _MAX_ITER,
    lattice_m: int = _LATTICE_M,
) -> dict:
    """Coherence channel capacity C_C = max_{p(x)} I_w(X; Y).

    Parameters
    ----------
    channel : array-like, shape (n_x, n_y)
        Discrete memoryless channel; row x is p(y | x), each row summing to 1.
    weights : array-like, shape (n_x,), optional
        Coherence weights w(x) in [0, 1]. Default (None) is all-ones, which
        returns the Shannon channel capacity (the boundary condition).
    base : float, optional
        Logarithm base for I_w. Default 2 (bits).
    tol, max_iter, lattice_m : solver controls (pre-registered defaults).

    Returns
    -------
    dict
        ``"C_C"`` : float -- the capacity (maximum over the input simplex).
        ``"argmax_input"`` : ndarray -- a capacity-achieving input pmf.
        ``"n_starts"`` : int -- number of deterministic multi-starts.
        ``"argmax_agreement_linf"`` : float -- max L-inf spread of the argmax
        over near-optimal starts (objective within 1e-6 of the best); the
        empirical uniqueness / concavity stand-in. Small => unimodal here.
    """
    P = np.asarray(channel, dtype=np.float64)
    _check_channel(P)
    n_x = P.shape[0]

    if weights is None:
        w = np.ones(n_x)
    else:
        w = np.asarray(weights, dtype=np.float64)
    if w.shape != (n_x,):
        raise ValueError(f"weights must have shape ({n_x},); got {w.shape}.")
    if np.any(w < 0) or np.any(w > 1):
        raise ValueError("weights must lie in [0, 1].")

    starts = _start_points(n_x, lattice_m, _LATTICE_CAP)
    results = [_ascend(p0, P, w, base, tol, max_iter) for p0 in starts]
    vals = np.array([f for _, f in results])
    best_idx = int(np.argmax(vals))
    best_p, best_f = results[best_idx]

    near = [p for (p, f) in results if f >= best_f - _AGREE_BAND]
    spread = 0.0
    for i in range(len(near)):
        for j in range(i + 1, len(near)):
            spread = max(spread, float(np.max(np.abs(near[i] - near[j]))))

    return {
        "C_C": float(best_f),
        "argmax_input": best_p,
        "n_starts": len(starts),
        "argmax_agreement_linf": spread,
    }
