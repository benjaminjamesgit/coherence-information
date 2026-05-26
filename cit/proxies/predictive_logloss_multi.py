"""Form B multi-feature proxy: autoregressive joint factorization.

Implements `predictive_logloss_proxy_multi`, the v0.5 multi-feature
variant of form B (v0.2 `predictive_logloss_proxy`). Predicts each
feature at time t given the entire previous vector v_{t-1}, using
a plug-in bigram estimator with Laplace smoothing.

Per design/multi_feature_substrate.md (Q4, locked 2026-05-26):
- Order-1 (bigram) context: p(v_t^j | v_{t-1})
- Parameter count: n * 2^n = 10,240 probabilities for n=10
- Laplace smoothing (matches v0.2 form B)
- Aggregation: C_hat = 1 - mean_nll / log(2), clipped to [0, 1]
"""

from __future__ import annotations

import numpy as np

__all__ = ["predictive_logloss_proxy_multi"]


def predictive_logloss_proxy_multi(stream, n_features=None):
    """Form B multi-feature: autoregressive joint factorization proxy.

    Parameters
    ----------
    stream : ndarray of shape (n_steps, n_features), binary uint8
        Multi-feature substrate stream.
    n_features : int, optional
        Must match stream.shape[1] if provided. Inferred otherwise.

    Returns
    -------
    C_hat : float in [0, 1]
        Coherence estimate. 1 = perfectly predictable; 0 = uniform random.
    """
    arr = np.asarray(stream, dtype=np.int64)
    if arr.ndim != 2:
        raise ValueError(f"stream must be 2-D; got ndim={arr.ndim}")
    T, n = arr.shape
    if n_features is not None and n_features != n:
        raise ValueError(f"n_features={n_features} != stream.shape[1]={n}")
    if T < 2:
        raise ValueError(f"need at least 2 steps; got T={T}")
    if n < 1:
        raise ValueError(f"need at least 1 feature; got n={n}")

    # Encode each step as an integer in [0, 2^n).  Feature 0 is the LSB.
    weights = (1 << np.arange(n)).astype(np.int64)
    stream_int = (arr * weights).sum(axis=1)
    n_states = 1 << n

    # Count tables: counts[prev_int, j, v] is the number of (t-1, t)
    # transitions where the previous vector encoded to prev_int and
    # feature j at time t took value v.
    counts = np.zeros((n_states, n, 2), dtype=np.int64)
    prev_int = stream_int[:-1]            # length T-1
    curr_vec = arr[1:]                    # shape (T-1, n)

    # Vectorized count update via np.add.at on per-feature views.
    for j in range(n):
        sub = counts[:, j, :]             # view of shape (n_states, 2)
        np.add.at(sub, (prev_int, curr_vec[:, j]), 1)

    # Laplace-smoothed conditional probabilities.
    smoothed = (counts + 1).astype(np.float64)
    totals = smoothed.sum(axis=2, keepdims=True)
    p_one_given_prev = (smoothed[:, :, 1] / totals[:, :, 0])  # (n_states, n)

    # Per-step, per-feature negative log-likelihood under the smoothed estimator.
    p_one_steps = p_one_given_prev[prev_int]             # (T-1, n)
    likelihood = np.where(curr_vec == 1, p_one_steps, 1.0 - p_one_steps)
    nll = -np.log(likelihood)

    mean_nll = float(nll.mean())
    log2 = float(np.log(2.0))
    C_hat = 1.0 - mean_nll / log2
    return float(np.clip(C_hat, 0.0, 1.0))
