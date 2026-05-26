"""K_2 multi-feature proxy: per-feature factorized n-gram MDL.

Implements ngram_mdl_proxy per the v0.5.1 amended specification
(2026-05-26 amendment in pre_registration.md). Per-feature factorized
bigram: condition each feature on its own previous value with 2-part
MDL coding.

Formulation (all quantities in bits):
    L(model) = (1/2) * num_params * log2(T)         (Rissanen prior)
    L(data)  = -sum_{t, j} log2 p(v_t^j | v_{t-1}^j) (Laplace-smoothed NLL)
    L_iid    = T * n_features                       (uniform Bernoulli baseline)
    C_K2     = 1 - (L_data + L_model) / L_iid       (clipped to [0, 1])

num_params = 2 * n_features: one Bernoulli emission probability per
(previous_value, feature) pair. Free parameters since p(curr=0 | prev)
= 1 - p(curr=1 | prev).

Family identity: per-feature marginal temporal predictability with
explicit MDL penalty. Reads lag-1 autocorrelation per feature ignoring
cross-feature joint structure (which form B captures). Distinct from
form B (joint conditioning, no penalty) and K_1 (universal compression,
implicit model).
"""

from __future__ import annotations

import numpy as np

__all__ = ["ngram_mdl_proxy"]


def ngram_mdl_proxy(stream, n_features=None):
    """K_2 multi-feature proxy: per-feature factorized bigram MDL.

    Parameters
    ----------
    stream : ndarray (n_steps, n_features), binary uint8
    n_features : int, optional
        Must match stream.shape[1] if provided.

    Returns
    -------
    C_hat : float in [0, 1]
        Coherence estimate. 1 = perfectly predictable (after MDL cost);
        0 = no predictability gain over uniform Bernoulli baseline.
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

    # Per-feature bigram counts: counts[j, prev_val, curr_val].
    # prev_val, curr_val each in {0, 1}; per-feature parameter space is 4 cells.
    counts = np.zeros((n, 2, 2), dtype=np.int64)
    prev_vec = arr[:-1]  # (T-1, n)
    curr_vec = arr[1:]   # (T-1, n)

    for j in range(n):
        sub = counts[j]  # view, shape (2, 2)
        np.add.at(sub, (prev_vec[:, j], curr_vec[:, j]), 1)

    # Laplace-smoothed p(curr=1 | prev_val) per (feature, prev_val).
    smoothed = (counts + 1).astype(np.float64)
    totals = smoothed.sum(axis=2, keepdims=True)
    p_one_given_prev = smoothed[:, :, 1] / totals[:, :, 0]  # (n, 2)

    # Per-step per-feature NLL using fancy indexing:
    # p_one_steps[t, j] = p_one_given_prev[j, prev_vec[t, j]]
    feat_idx = np.arange(n)[None, :]  # (1, n)
    p_one_steps = p_one_given_prev[feat_idx, prev_vec]  # (T-1, n)
    likelihood = np.where(curr_vec == 1, p_one_steps, 1.0 - p_one_steps)

    log2 = float(np.log(2.0))
    L_data_bits = float(-np.log(likelihood).sum() / log2)

    # Rissanen model penalty
    num_params = 2 * n
    L_model_bits = 0.5 * num_params * float(np.log2(T))

    # Uniform Bernoulli baseline: T * n bits (since log2(2) = 1)
    L_iid_bits = float(T * n)

    L_total_bits = L_data_bits + L_model_bits
    C_hat = 1.0 - L_total_bits / L_iid_bits
    return float(np.clip(C_hat, 0.0, 1.0))
