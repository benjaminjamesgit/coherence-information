"""Induction pipeline: stream → baseline Ĉ → ρ → w.

The central orchestration from cit_engineering.pdf and Metacoherence
Appendix A.2. Given a symbol stream, this module:

1. Computes the baseline coherence proxy Ĉ(X).
2. For each symbol, applies the ablation operator to obtain ρ(x).
3. Maps relevance to bounded weights via w(x) = σ(β · ρ(x)) per
   Step D of formal_3.pdf.

Per the v0.2 pre-registration, β = 4.0 is the locked sensitivity;
calibration via cross-validation on a held-out segment under a fixed
rate budget is deferred to v0.3.

References
----------
James, B. (2026). Engineering Induced Coherence Weights for Coherence
    Information Theory. PhilPapers, §"Induction pipeline".
James, B. (2026). Formal Foundation of Induced Coherence Weights.
    PhilPapers, Step D.
James, B. (2026). Metacoherence. PhilPapers, Appendix A.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from cit.ablations.loo import leave_one_out_ablation
from cit.proxies.predictive_logloss import predictive_logloss_proxy

__all__ = ["induce_weights"]


def _stable_sigmoid(z: float) -> float:
    """Numerically stable logistic σ(z) = 1 / (1 + exp(-z))."""
    if z >= 0.0:
        return float(1.0 / (1.0 + np.exp(-z)))
    exp_z = float(np.exp(z))
    return exp_z / (1.0 + exp_z)


def induce_weights(
    stream: ArrayLike,
    alphabet_size: int | None = None,
    proxy: Callable[[Any, int], float] = predictive_logloss_proxy,
    ablation: Callable[..., dict[str, Any]] = leave_one_out_ablation,
    beta: float = 4.0,
    rng: np.random.Generator | None = None,
) -> dict[str, Any]:
    """The induction pipeline: stream → Ĉ → ρ → w.

    Composes the proxy and ablation into the full data-to-weights
    pipeline. Returns induced weights together with all intermediate
    diagnostics so downstream consumers (and tests) can interrogate
    every step.

    Parameters
    ----------
    stream : array-like of int
        Symbol stream of length >= 2.
    alphabet_size : int, optional
        Size of the alphabet K. If None, inferred as ``stream.max() + 1``.
        Pass explicitly when the alphabet may exceed observed symbols.
    proxy : callable, optional
        Coherence proxy accepting ``(stream, alphabet_size)`` returning a
        float in [0, 1]. Default: predictive_logloss_proxy (v0.2 form B).
    ablation : callable, optional
        Ablation operator. Must accept ``(stream, alphabet_size, proxy,
        rng)`` as keyword arguments and return a dict with keys
        ``'c_baseline'``, ``'c_ablated'``, ``'rho'``, ``'symbols'``.
        Default: leave_one_out_ablation.
    beta : float, optional
        Sensitivity for the logistic weight mapping w(x) = σ(β · ρ(x)).
        Default 4.0 — the v0.2 pre-registered initial value, locked in
        pre_registration.md. Calibration deferred to v0.3.
    rng : np.random.Generator, optional
        Random generator threaded into the ablation. Pass a seeded
        generator for reproducibility.

    Returns
    -------
    dict with keys:
        ``'w'`` : dict[int, float]
            Induced coherence weights in [0, 1] for each symbol.
        ``'rho'`` : dict[int, float]
            Coherence relevance ρ(x) for each symbol.
        ``'c_baseline'`` : float
            Baseline coherence proxy Ĉ(X).
        ``'c_ablated'`` : dict[int, float]
            Coherence proxy on each ablated stream.
        ``'symbols'`` : list[int]
            Sorted symbols that were processed.
        ``'beta'`` : float
            β value used (recorded for reproducibility).

    Notes
    -----
    The sigmoid σ(z) = 1 / (1 + exp(-z)) maps real-valued ρ to weights
    in [0, 1]: ρ ≈ 0 yields w ≈ 0.5; strongly positive ρ pushes w toward
    1; strongly negative ρ pushes w toward 0. With β = 4.0 and ρ in the
    typical synthetic-stream range of [-0.2, 0.2], weights span roughly
    [0.3, 0.7], with coherence-bearing symbols above 0.5 and noise below.
    """
    s = np.asarray(stream, dtype=np.int64)
    if s.ndim != 1 or s.size < 2:
        raise ValueError(
            f"stream must be 1D with length >= 2 (got shape {s.shape})."
        )
    if not np.isfinite(beta):
        raise ValueError(f"beta must be finite (got {beta}).")

    result = ablation(
        s,
        alphabet_size=alphabet_size,
        proxy=proxy,
        rng=rng,
    )
    rho: dict[int, float] = result["rho"]

    w: dict[int, float] = {}
    for x, rho_x in rho.items():
        if np.isnan(rho_x):
            w[x] = float("nan")
        else:
            w[x] = _stable_sigmoid(beta * rho_x)

    return {
        "w": w,
        "rho": rho,
        "c_baseline": result["c_baseline"],
        "c_ablated": result["c_ablated"],
        "symbols": result["symbols"],
        "beta": float(beta),
    }
