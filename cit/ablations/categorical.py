"""Categorical (alphabet-A) ablation generalizations for the cross-domain program (v0.7).

The v0.5 multi-feature ablations (A1 LOO, A2 Shapley, A3 correlation-cluster) ablate a
feature by replace-with-uniform drawn as Bernoulli(0.5) -- binary-specific. On D1 the
features are alphabet-A categorical, so the replacement is uniform over {0,...,A-1}.
That is the ONLY change: the attribution logic, coalition sampling, Pearson clustering,
and cohort-mean centering are identical to the v0.5 operators (which are left untouched).

These pair with the marginal-relative categorical proxies (cit.proxies.categorical): a
distractor replaced by uniform-over-A still has zero structure-beyond-its-marginal, so its
rho ~ 0, while a coherence-bearing feature loses structure under ablation and gets rho > 0
-- the class separation that drives R2. Because the proxies are marginal-relative, changing
a skewed distractor's marginal to uniform does NOT manufacture spurious rho.

Each ablation takes the proxy as a callable `proxy(stream_2d, n_features) -> float` (the
induction wrapper fixes its alphabet) and an explicit `alphabet` used only for replacement.
"""

from __future__ import annotations

import numpy as np

from cit.ablations.correlation_cluster import (
    _pearson_matrix,
    _connected_components,
    DEFAULT_CORRELATION_THRESHOLD,
)

__all__ = [
    "leave_one_out_ablation_cat",
    "shapley_ablation_cat",
    "correlation_cluster_ablation_cat",
    "DEFAULT_K_COALITIONS",
    "DEFAULT_CORRELATION_THRESHOLD",
]

DEFAULT_K_COALITIONS = 64


def _check(stream, n_features):
    arr = np.asarray(stream)
    if arr.ndim != 2:
        raise ValueError(f"stream must be 2-D; got ndim={arr.ndim}")
    T, n = arr.shape
    if n_features is not None and n_features != n:
        raise ValueError(f"n_features={n_features} != stream.shape[1]={n}")
    return arr, T, n


def _center(rho_raw, center):
    if center:
        mean_rho = float(np.mean(list(rho_raw.values())))
        return {f: v - mean_rho for f, v in rho_raw.items()}
    return dict(rho_raw)


def leave_one_out_ablation_cat(stream, proxy, n_features=None, *, alphabet, rng=None, center=True):
    """A1 leave-one-out (categorical): ablate each feature by replace-with-uniform over A."""
    arr, T, n = _check(stream, n_features)
    if rng is None:
        rng = np.random.default_rng()
    c_full = proxy(arr, n)
    rho_raw, c_ablated = {}, {}
    for j in range(n):
        ablated = arr.copy()
        ablated[:, j] = rng.integers(0, alphabet, size=T, dtype=arr.dtype)
        c_after = proxy(ablated, n)
        rho_raw[j] = c_full - c_after
        c_ablated[j] = c_after
    return {"rho": _center(rho_raw, center), "c_ablated": c_ablated, "centered": center}


def _ablate_outside_cat(stream, kept, alphabet, rng):
    """Return a copy with features NOT in `kept` replaced by uniform over A."""
    T, n = stream.shape
    to_ablate = sorted(set(range(n)) - set(kept))
    if not to_ablate:
        return stream.copy()
    ablated = stream.copy()
    ablated[:, to_ablate] = rng.integers(0, alphabet, size=(T, len(to_ablate)), dtype=stream.dtype)
    return ablated


def shapley_ablation_cat(stream, proxy, n_features=None, *, alphabet, rng=None,
                         k=DEFAULT_K_COALITIONS, center=True):
    """A2 Shapley (categorical): k sampled coalitions per feature, uniform-over-A ablation."""
    arr, T, n = _check(stream, n_features)
    if rng is None:
        rng = np.random.default_rng()
    if k < 1:
        raise ValueError(f"k must be positive; got k={k}")
    all_feats = list(range(n))
    rho_raw, c_ablated_mean = {}, {}
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
            c_S = proxy(_ablate_outside_cat(arr, S, alphabet, rng), n)
            c_S_plus_j = proxy(_ablate_outside_cat(arr, S + [j], alphabet, rng), n)
            marginals[s] = c_S_plus_j - c_S
            c_S_vals[s] = c_S
        rho_raw[j] = float(marginals.mean())
        c_ablated_mean[j] = float(c_S_vals.mean())
    return {"rho": _center(rho_raw, center), "c_ablated": c_ablated_mean, "centered": center}


def correlation_cluster_ablation_cat(stream, proxy, n_features=None, *, alphabet,
                                     correlation_threshold=DEFAULT_CORRELATION_THRESHOLD,
                                     rng=None, center=True):
    """A3 correlation-cluster (categorical): cluster by positive Pearson, ablate clusters with uniform-over-A."""
    arr, T, n = _check(stream, n_features)
    if rng is None:
        rng = np.random.default_rng()
    corr = _pearson_matrix(arr)
    adjacency = (corr > correlation_threshold) & ~np.eye(n, dtype=bool)
    clusters = _connected_components(adjacency)
    c_full = proxy(arr, n)
    rho_raw, c_ablated = {}, {}
    for cluster in clusters:
        idx = sorted(cluster)
        ablated = arr.copy()
        ablated[:, idx] = rng.integers(0, alphabet, size=(T, len(idx)), dtype=arr.dtype)
        delta = c_full - proxy(ablated, n)
        c_after = c_full - delta
        for f in idx:
            rho_raw[f] = delta
            c_ablated[f] = c_after
    return {"rho": _center(rho_raw, center), "c_ablated": c_ablated, "clusters": clusters, "centered": center}
