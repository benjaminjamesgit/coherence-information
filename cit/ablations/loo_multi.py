"""A_1 (leave-one-out) multi-feature variant.

Per design/multi_feature_substrate.md (Q4 + Q7, locked 2026-05-26):
- Feature-level LOO: ablate one feature at a time by replace-with-uniform.
- Replacement: i.i.d. Bernoulli(0.5) per (t, ablated_feature).
- Centering: cohort-mean subtraction default on (v0.5.0 convention).
  Necessary because Bernoulli(0.5) replacement of noise features is
  statistically identical to their original distribution, leaving raw
  noise rho ~ 0; centering recovers canonical signs (rho < 0 for noise).
- v0.4 single-symbol LOO (cit.ablations.loo) is unchanged.
"""

from __future__ import annotations

import numpy as np

__all__ = ["leave_one_out_ablation_multi"]


def leave_one_out_ablation_multi(
    stream,
    proxy,
    n_features=None,
    *,
    rng=None,
    center=True,
):
    """A_1 leave-one-out ablation on a multi-feature substrate.

    Parameters
    ----------
    stream : ndarray (n_steps, n_features), binary
    proxy : callable
        Multi-feature proxy with signature `proxy(stream_2d, n_features) -> float`.
    n_features : int, optional
        Must match stream.shape[1] if provided.
    rng : np.random.Generator | None
        Random generator for replace-with-uniform draws.
    center : bool, default True
        If True, subtract cohort-mean raw rho (recovers canonical signs).

    Returns
    -------
    dict with keys "rho", "c_ablated", "centered".
    """
    arr = np.asarray(stream)
    if arr.ndim != 2:
        raise ValueError(f"stream must be 2-D; got ndim={arr.ndim}")
    T, n = arr.shape
    if n_features is not None and n_features != n:
        raise ValueError(f"n_features={n_features} != stream.shape[1]={n}")
    if rng is None:
        rng = np.random.default_rng()

    c_full = proxy(arr, n)

    rho_raw = {}
    c_ablated = {}

    for j in range(n):
        ablated = arr.copy()
        ablated[:, j] = (rng.random(T) < 0.5).astype(arr.dtype)
        c_after = proxy(ablated, n)
        rho_raw[j] = c_full - c_after
        c_ablated[j] = c_after

    if center:
        mean_rho = float(np.mean(list(rho_raw.values())))
        rho = {f: v - mean_rho for f, v in rho_raw.items()}
    else:
        rho = dict(rho_raw)

    return {"rho": rho, "c_ablated": c_ablated, "centered": center}
