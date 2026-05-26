"""Multi-feature induction pipeline: stream -> C_hat -> rho -> w.

Implements `induce_weights_multi`, the v0.5 multi-feature analog of
v0.2's `induce_weights` (cit.induce). Orchestrates:

    stream_2d
        --> proxy(stream, n_features) gives C_hat (scalar)
        --> ablation(stream, proxy, n_features, rng) gives per-feature rho
        --> w(j) = sigmoid(beta * rho(j))  with beta = 4.0 locked from v0.2

Per design/multi_feature_substrate.md (Q4 + Q7, locked 2026-05-26):
- Default proxy: predictive_logloss_proxy_multi (form B multi).
- Default ablation: leave_one_out_ablation_multi (A_1 multi).
- beta = 4.0, carries from v0.2 pre-registration.
- v0.2 single-symbol induce_weights (cit.induce) is unchanged.
"""

from __future__ import annotations

import numpy as np

from cit.proxies.predictive_logloss_multi import predictive_logloss_proxy_multi
from cit.ablations.loo_multi import leave_one_out_ablation_multi

__all__ = ["induce_weights_multi", "BETA"]

BETA = 4.0


def induce_weights_multi(
    stream,
    n_features=None,
    *,
    proxy=None,
    ablation=None,
    rng=None,
    beta=BETA,
):
    """Multi-feature weight induction: stream -> rho -> w.

    Parameters
    ----------
    stream : ndarray (n_steps, n_features), binary
    n_features : int, optional
        Must match stream.shape[1] if provided.
    proxy : callable, optional
        Multi-feature proxy (stream_2d, n_features) -> float.
        Defaults to predictive_logloss_proxy_multi (form B multi).
    ablation : callable, optional
        Multi-feature ablation. Must accept positional (stream, proxy)
        and keyword (n_features=, rng=). Defaults to
        leave_one_out_ablation_multi (A_1 multi).
    rng : np.random.Generator | None
        Random generator threaded into the ablation operator.
    beta : float, default 4.0
        Sigmoid steepness. Locked at 4.0 by v0.2 pre-registration.

    Returns
    -------
    dict with keys
        "rho":       dict feature_idx -> rho value (centered per the
                     ablation operator's convention)
        "w":         dict feature_idx -> w in (0, 1), via sigmoid(beta * rho)
        "c_ablated": dict feature_idx -> C_hat after ablation (operator-specific)
        "centered":  bool, echoes the ablation's centering choice
    """
    arr = np.asarray(stream)
    if arr.ndim != 2:
        raise ValueError(f"stream must be 2-D; got ndim={arr.ndim}")
    T, n = arr.shape
    if n_features is not None and n_features != n:
        raise ValueError(f"n_features={n_features} != stream.shape[1]={n}")

    if proxy is None:
        proxy = predictive_logloss_proxy_multi
    if ablation is None:
        ablation = leave_one_out_ablation_multi
    if rng is None:
        rng = np.random.default_rng()

    result = ablation(arr, proxy, n_features=n, rng=rng)
    rho = result["rho"]

    # Sigmoid weight map: w(j) = 1 / (1 + exp(-beta * rho(j))).
    w = {f: float(1.0 / (1.0 + np.exp(-beta * v))) for f, v in rho.items()}

    return {
        "rho": rho,
        "w": w,
        "c_ablated": result["c_ablated"],
        "centered": result.get("centered", True),
    }
