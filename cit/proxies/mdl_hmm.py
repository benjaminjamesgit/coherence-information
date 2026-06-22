"""K_4 multi-feature proxy: MDL hidden Markov model with cardinality selection.

Implements mdl_hmm_proxy per the v0.5.4 amended specification
(2026-06-22 amendment in pre_registration.md). A factorized Bernoulli
emission HMM is fit by Baum-Welch EM at each hidden-state cardinality
H in {1, 2, 3, 4}; a two-part MDL score selects H*.

Formulation (all quantities in bits):
    L_data(H)     = -log2 P(stream | fitted HMM_H)      (forward algorithm)
    L_model(H)    = 0.5 * num_params(H) * log2(T)        (Rissanen prior)
    num_params(H) = H*(H-1) [transition] + H*n [emission] + (H-1) [initial]
    L_iid         = T * n                                (uniform Bernoulli baseline)
    H*            = argmin_H [L_data(H) + L_model(H)]
    C_K4          = 1 - (L_data(H*) + L_model(H*)) / L_iid    (clipped to [0, 1])

The emission family is FIXED (factorized Bernoulli, each feature
conditionally independent given the hidden state, one free p[h, j] per
(state h, feature j)). The MDL search ranges only over hidden-state
cardinality, never over emission structure (narrow scope, locked).

Family identity: the only proxy with a latent variable AND an explicit
MDL complexity penalty over a searched cardinality. Emissions are
factorized (matching K_2's per-feature factorization), so a K_4 vs K_2
comparison isolates the latent-state / model-selection difference; the
cross-feature coupling K_4 adds via the shared hidden state is exactly
what K_2 lacks. Distinct from form B (joint conditioning on the previous
full vector, no latent, no penalty), K_1 (zstd, implicit model), K_3
(neural online cross-entropy, no penalty), K_5 (LZ76 phrase parsing,
no probability model).

Determinism: a single deterministic seeded EM initialization (HMM_SEED),
CPU/numpy, vectorized -- bit-exact reproducible, mirroring the K_3
NEURAL_SEED discipline.
"""

from __future__ import annotations

import numpy as np

__all__ = ["mdl_hmm_proxy", "HMM_SEED"]

HMM_SEED = 0                 # EM initialization seed (locked v0.5.4)
H_CANDIDATES = (1, 2, 3, 4)  # hidden-state cardinality grid
MAX_ITER = 100               # Baum-Welch iteration cap
TOL = 1e-4                   # convergence tol on per-step mean log-likelihood
_SELF_TRANS = 0.9            # sticky self-transition for EM init
_EPS = 1e-6                  # emission-probability clip
_TRANS_EPS = 1e-12           # transition-probability clip
_LN2 = float(np.log(2.0))


def _emission_loglik(X, p):
    """Per-step per-state emission log-likelihood (natural log).

    logB[t, h] = sum_j x[t,j]*log p[h,j] + (1-x[t,j])*log(1-p[h,j]).
    p must already be clipped to [_EPS, 1-_EPS] so the logs are finite.
    """
    return X @ np.log(p).T + (1.0 - X) @ np.log1p(-p).T


def _forward_logP(logB, A, pi):
    """Scaled forward pass; returns log P(data) in nats on the given params.

    Uses a per-row max offset (rowmax) for numerical stability: the scaled
    recursion runs on Bs = exp(logB - rowmax), and the offsets are folded
    back into the marginal log-likelihood so the result is exact.
    """
    T, H = logB.shape
    rowmax = logB.max(axis=1, keepdims=True)
    Bs = np.exp(logB - rowmax)

    a = pi * Bs[0]
    s = a.sum()
    a /= s
    logP = float(np.log(s) + rowmax[0, 0])
    for t in range(1, T):
        a = (a @ A) * Bs[t]
        s = a.sum()
        a /= s
        logP += float(np.log(s) + rowmax[t, 0])
    return logP


def _fit_hmm(X, H):
    """Fit a factorized-Bernoulli HMM with H states; return L_data in bits.

    L_data = -log2 P(X | fitted params). H=1 is the closed-form independent
    per-feature Bernoulli MLE (no EM). H>=2 runs Baum-Welch EM from a single
    deterministic seeded init, then recomputes L_data via an independent
    forward pass on the fitted params.
    """
    T, n = X.shape

    if H == 1:
        mu = np.clip(X.mean(axis=0), _EPS, 1.0 - _EPS)
        ones = X.sum(axis=0)
        zeros = T - ones
        return float(-(ones * np.log2(mu) + zeros * np.log2(1.0 - mu)).sum())

    # Deterministic seeded init: emissions = per-feature MLE + fixed jitter,
    # sticky self-transition, uniform initial distribution.
    rng = np.random.default_rng(HMM_SEED)
    mu = X.mean(axis=0)
    p = np.clip(mu[None, :] + rng.uniform(-0.25, 0.25, size=(H, n)),
                _EPS, 1.0 - _EPS)
    A = np.full((H, H), (1.0 - _SELF_TRANS) / (H - 1))
    np.fill_diagonal(A, _SELF_TRANS)
    pi = np.full(H, 1.0 / H)

    prev = -np.inf
    for _ in range(MAX_ITER):
        logB = _emission_loglik(X, p)
        rowmax = logB.max(axis=1, keepdims=True)
        Bs = np.exp(logB - rowmax)

        # Forward (scaled)
        alpha = np.empty((T, H))
        c = np.empty(T)
        alpha[0] = pi * Bs[0]
        c[0] = alpha[0].sum()
        alpha[0] /= c[0]
        for t in range(1, T):
            alpha[t] = (alpha[t - 1] @ A) * Bs[t]
            c[t] = alpha[t].sum()
            alpha[t] /= c[t]
        logP = float(np.log(c).sum() + rowmax.sum())

        # Backward (scaled with the same per-step constants)
        beta = np.empty((T, H))
        beta[T - 1] = 1.0
        for t in range(T - 2, -1, -1):
            beta[t] = (A @ (Bs[t + 1] * beta[t + 1])) / c[t + 1]

        gamma = alpha * beta                       # (T, H), rows ~ sum to 1
        U = (Bs[1:] * beta[1:]) / c[1:, None]      # (T-1, H)
        xi_sum = A * (alpha[:-1].T @ U)            # (H, H) summed over t

        # M-step
        pi = gamma[0] / gamma[0].sum()
        denom_A = gamma[:-1].sum(axis=0)[:, None]
        A = xi_sum / np.maximum(denom_A, _TRANS_EPS)
        A = np.maximum(A, _TRANS_EPS)
        A /= A.sum(axis=1, keepdims=True)
        gsum = gamma.sum(axis=0)[:, None]
        p = np.clip((gamma.T @ X) / np.maximum(gsum, _EPS), _EPS, 1.0 - _EPS)

        mean_ll = logP / T
        if mean_ll - prev < TOL:
            break
        prev = mean_ll

    logB = _emission_loglik(X, p)
    logP = _forward_logP(logB, A, pi)
    return float(-logP / _LN2)


def mdl_hmm_proxy(stream, n_features=None):
    """K_4 multi-feature proxy: MDL HMM with hidden-state cardinality selection.

    Fits a factorized-Bernoulli HMM at each H in {1, 2, 3, 4}, scores each by
    two-part description length (data + Rissanen model penalty), selects the
    minimizing H, and maps the selected description length to [0, 1] against
    the uniform-Bernoulli baseline.

    Parameters
    ----------
    stream : ndarray (n_steps, n_features), binary uint8 or float in {0, 1}
    n_features : int, optional
        Must match stream.shape[1] if provided.

    Returns
    -------
    C_K4 : float in [0, 1]
        Coherence estimate. 1 = perfectly compressible by the selected HMM
        (after MDL cost); 0 = no description-length gain over the uniform
        Bernoulli baseline.
    """
    arr = np.asarray(stream)
    if arr.ndim != 2:
        raise ValueError(f"stream must be 2-D; got ndim={arr.ndim}")
    T, n = arr.shape
    if n_features is not None and n_features != n:
        raise ValueError(f"n_features={n_features} != stream.shape[1]={n}")
    if T < 2:
        raise ValueError(f"need at least 2 steps; got T={T}")
    if n < 1:
        raise ValueError(f"need at least 1 feature; got n={n}")

    X = np.ascontiguousarray(arr, dtype=np.float64)
    log2T = float(np.log2(T))
    L_iid = float(T * n)

    best_total = None
    for H in H_CANDIDATES:
        L_data = _fit_hmm(X, H)
        num_params = H * (H - 1) + H * n + (H - 1)
        L_model = 0.5 * num_params * log2T
        total = L_data + L_model
        if best_total is None or total < best_total:
            best_total = total

    C_hat = 1.0 - best_total / L_iid
    return float(np.clip(C_hat, 0.0, 1.0))
