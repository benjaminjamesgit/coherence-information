"""A_2 Shapley multi-feature variant.

Per design/multi_feature_substrate.md (Q4 + Q7, locked 2026-05-26):
- Feature-level Shapley with k=64 sampled coalitions per feature.
- Marginal contribution: c(S union {j}) - c(S) where S is a random
  subset of features excluding j, ablated via replace-with-uniform
  (Bernoulli(0.5)) on features outside the coalition.
- Centering: cohort-mean default on (matches v0.4 A_2 convention).
- v0.4 single-symbol Shapley (cit.ablations.shapley) is unchanged.
"""

from __future__ import annotations

import numpy as np

__all__ = ["shapley_ablation_multi", "DEFAULT_K_COALITIONS"]

DEFAULT_K_COALITIONS = 64


def _ablate_outside(stream, kept, rng):
    """Return a copy with features NOT in `kept` replaced by Bernoulli(0.5)."""
    T, n = stream.shape
    kept_set = set(kept)
    to_ablate = sorted(set(range(n)) - kept_set)
    if not to_ablate:
        return stream.copy()
    ablated = stream.copy()
    replacement = (rng.random((T, len(to_ablate))) < 0.5).astype(stream.dtype)
    ablated[:, to_ablate] = replacement
    return ablated


def shapley_ablation_multi(
    stream,
    proxy,
    n_features=None,
    *,
    rng=None,
    k=DEFAULT_K_COALITIONS,
    center=True,
):
    """A_2 Shapley ablation on a multi-feature substrate.

    For each feature j, samples k coalitions S subset of (features - {j})
    uniformly over coalition size, then averages the marginal contribution
    c(S union {j}) - c(S) across the k samples.

    Parameters
    ----------
    stream : ndarray (n_steps, n_features), binary
    proxy : callable (stream_2d, n_features) -> float
    n_features : int, optional
    rng : np.random.Generator | None
    k : int, default 64
        Coalitions sampled per feature.
    center : bool, default True
        Cohort-mean centering. Matches v0.4 A_2 default.

    Returns
    -------
    dict with keys "rho", "c_ablated", "centered".
    "c_ablated" is the per-feature mean of c(S) across sampled coalitions
    (the operator's baseline for that feature).
    """
    arr = np.asarray(stream)
    if arr.ndim != 2:
        raise ValueError(f"stream must be 2-D; got ndim={arr.ndim}")
    T, n = arr.shape
    if n_features is not None and n_features != n:
        raise ValueError(f"n_features={n_features} != stream.shape[1]={n}")
    if rng is None:
        rng = np.random.default_rng()
    if k < 1:
        raise ValueError(f"k must be positive; got k={k}")

    all_feats = list(range(n))
    rho_raw = {}
    c_ablated_mean = {}

    for j in range(n):
        others = [i for i in all_feats if i != j]
        marginals = np.empty(k)
        c_S_vals = np.empty(k)
        for s in range(k):
            size = int(rng.integers(0, len(others) + 1))
            if size == 0:
                S = []
            elif size == len(others):
                S = list(others)
            else:
                S = list(rng.choice(others, size=size, replace=False))
            ablated_S = _ablate_outside(arr, S, rng)
            ablated_S_plus_j = _ablate_outside(arr, S + [j], rng)
            c_S = proxy(ablated_S, n)
            c_S_plus_j = proxy(ablated_S_plus_j, n)
            marginals[s] = c_S_plus_j - c_S
            c_S_vals[s] = c_S
        rho_raw[j] = float(marginals.mean())
        c_ablated_mean[j] = float(c_S_vals.mean())

    if center:
        mean_rho = float(np.mean(list(rho_raw.values())))
        rho = {f: v - mean_rho for f, v in rho_raw.items()}
    else:
        rho = dict(rho_raw)

    return {"rho": rho, "c_ablated": c_ablated_mean, "centered": center}
