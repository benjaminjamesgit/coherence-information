"""A_3 correlation-cluster ablation: feature-stream Pearson clustering.

Implements `correlation_cluster_ablation`, the v0.5 multi-feature-native
ablation operator per Metacoherence section 3.2. Groups features by
positive Pearson correlation above threshold; ablates each cluster
collectively via replace-with-uniform; computes per-feature rho via
C_hat differential.

Per design/multi_feature_substrate.md (Q5 implication, Q7 lock):
- Clustering: signed positive correlation above threshold (default 0.15).
  Signed (not absolute) so anti-correlated clusters stay separate --
  matches the Q3 ground-truth geometry where cluster_A and cluster_B
  are anti-correlated yet structurally distinct.
- Operator: replace-with-uniform per cluster (matches A_1, A_2 form).
- Centering: cohort-mean subtraction default on, matches A_2 convention.
- Output: per-feature rho with canonical signs (positive for coherent,
  negative for noise) under structured multi-feature streams.
"""

from __future__ import annotations

import numpy as np

__all__ = ["correlation_cluster_ablation", "DEFAULT_CORRELATION_THRESHOLD"]

DEFAULT_CORRELATION_THRESHOLD = 0.15


def _pearson_matrix(arr):
    """Pairwise Pearson correlation between columns of arr."""
    s = arr.astype(np.float64)
    s_c = s - s.mean(axis=0, keepdims=True)
    std = s.std(axis=0, ddof=0, keepdims=True)
    std = np.where(std == 0, 1.0, std)
    z = s_c / std
    return (z.T @ z) / s.shape[0]


def _connected_components(adjacency):
    """Connected components of an undirected boolean adjacency matrix."""
    n = adjacency.shape[0]
    visited = [False] * n
    components = []
    for start in range(n):
        if visited[start]:
            continue
        component = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if visited[node]:
                continue
            visited[node] = True
            component.add(node)
            for nb in range(n):
                if (not visited[nb]) and adjacency[node, nb]:
                    stack.append(nb)
        components.append(component)
    return components


def correlation_cluster_ablation(
    stream,
    proxy,
    n_features=None,
    correlation_threshold=DEFAULT_CORRELATION_THRESHOLD,
    rng=None,
    center=True,
):
    """A_3 correlation-cluster ablation.

    Parameters
    ----------
    stream : ndarray (n_steps, n_features), binary
    proxy : callable
        Multi-feature proxy with signature `proxy(stream_2d, n_features) -> float`.
    n_features : int, optional
        Must match stream.shape[1] if provided.
    correlation_threshold : float
        Minimum positive Pearson correlation for two features to be
        clustered together. Default 0.15.
    rng : np.random.Generator | None
        Random generator for replace-with-uniform ablation.
    center : bool
        If True (default), subtract cohort-mean raw rho. Matches A_2.

    Returns
    -------
    dict with keys
        "rho":       dict feature_idx -> rho (centered if center=True)
        "c_ablated": dict feature_idx -> C_hat after the cluster ablation
        "clusters":  list of sets of feature indices
        "centered":  bool (echoes the centering choice)
    """
    arr = np.asarray(stream)
    if arr.ndim != 2:
        raise ValueError(f"stream must be 2-D; got ndim={arr.ndim}")
    T, n = arr.shape
    if n_features is not None and n_features != n:
        raise ValueError(f"n_features={n_features} != stream.shape[1]={n}")
    if rng is None:
        rng = np.random.default_rng()

    corr = _pearson_matrix(arr)
    adjacency = (corr > correlation_threshold) & ~np.eye(n, dtype=bool)
    clusters = _connected_components(adjacency)

    c_full = proxy(arr, n)

    rho_raw = {}
    c_ablated = {}

    for cluster in clusters:
        idx = sorted(cluster)
        ablated = arr.copy()
        # Replace-with-uniform: independent Bernoulli(0.5) per (t, feature).
        replacement = (rng.random((T, len(idx))) < 0.5).astype(arr.dtype)
        ablated[:, idx] = replacement

        c_after = proxy(ablated, n)
        delta = c_full - c_after

        for f in idx:
            rho_raw[f] = delta
            c_ablated[f] = c_after

    if center:
        mean_rho = float(np.mean(list(rho_raw.values())))
        rho = {f: v - mean_rho for f, v in rho_raw.items()}
    else:
        rho = dict(rho_raw)

    return {
        "rho": rho,
        "c_ablated": c_ablated,
        "clusters": clusters,
        "centered": center,
    }
