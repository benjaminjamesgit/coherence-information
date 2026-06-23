"""Categorical (alphabet-A) proxy generalizations for the cross-domain program (v0.7).

The v0.5 multi-feature proxies (K2 `ngram_mdl`, K3 `neural_prequential`, K4 `mdl_hmm`)
are BINARY: each scores a stream against a UNIFORM baseline (`L_iid = T*n` bits, or
`H_iid = 1.0` bit/feature). That is sound only when feature marginals are ~uniform
(the v0.5 substrate was marginal-matched). On D1 the distractors carry SKEWED marginals
by design (Zipf, low-frequency); a uniform baseline credits the marginal skew as
coherence -- the precise failure D1 exists to catch.

These categorical generalizations measure coherence MARGINAL-RELATIVE (the v0.7.0 lock,
pre_registration.md 2026-06-23): the baseline is each feature's OWN empirical marginal,
so a feature whose only structure is a skewed marginal scores ~0.

    compression (K2, K4): C = 1 - L_structural / L_marginal     (code length beyond the marginal)
    predictive   (K3):    C = 1 - H_pred / H_marginal           (predictive gain over the marginal)

All return C_hat in [0, 1], the same contract the v0.5 proxies expose to the induction
pipeline (`stream (T, n) -> C_hat scalar`), so the existing ablation/sigmoid machinery
(categorical variants, slice 3) attributes per-feature rho unchanged. Streams are integer
arrays in [0, alphabet); `alphabet` may be passed explicitly (D1 uses 8) or inferred.

K1 (compression-delta) and K5 (Lempel) are alphabet-agnostic via their byte/bit encoders
and are NOT re-implemented here.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "ngram_mdl_proxy_cat",
    "neural_prequential_proxy_cat",
    "mdl_hmm_proxy_cat",
    "NEURAL_SEED",
    "HMM_SEED",
]

_LOG2 = float(np.log(2.0))

# K3 locked hyperparameters (carry the v0.5.3 binary K3 discipline)
NEURAL_SEED = 7
_HIDDEN_DIM = 64
_LEARNING_RATE = 0.01

# K4 locked hyperparameters (carry the v0.5.4 binary K4 discipline)
HMM_SEED = 0                 # EM initialization seed
_H_CANDIDATES = (1, 2, 3, 4)  # hidden-state cardinality grid
_HMM_MAX_ITER = 100          # Baum-Welch iteration cap
_HMM_TOL = 1e-4              # convergence tol on per-step mean log-likelihood
_SELF_TRANS = 0.9           # sticky self-transition for EM init
_EMIT_EPS = 1e-6            # emission-probability clip
_TRANS_EPS = 1e-12         # transition-probability clip


def _validate(stream, n_features, alphabet):
    """Shared shape/range validation; returns (arr int64, T, n, alphabet)."""
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
    arr = np.ascontiguousarray(arr, dtype=np.int64)
    if arr.min() < 0:
        raise ValueError("stream values must be non-negative integers")
    inferred = int(arr.max()) + 1
    if alphabet is None:
        alphabet = inferred
    elif alphabet < inferred:
        raise ValueError(f"alphabet={alphabet} < observed max+1={inferred}")
    return arr, T, n, alphabet


def _marginal_nll_bits(symbols, alphabet):
    """Laplace-smoothed marginal NLL of `symbols` in bits (the marginal-only data cost)."""
    counts = np.bincount(symbols, minlength=alphabet).astype(np.float64)
    sm = counts + 1.0
    p = sm / sm.sum()
    return float(-(counts * np.log2(p)).sum())


def _marginal_entropy_bits(symbols, alphabet):
    """Empirical (plug-in) marginal entropy of `symbols` in bits -- the predictive baseline."""
    counts = np.bincount(symbols, minlength=alphabet).astype(np.float64)
    p = counts / counts.sum()
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def _bigram_nll_bits(prev, curr, alphabet):
    """Laplace-smoothed per-feature bigram NLL of `curr` given `prev`, in bits."""
    counts = np.zeros((alphabet, alphabet), dtype=np.float64)
    np.add.at(counts, (prev, curr), 1)
    sm = counts + 1.0
    p = sm / sm.sum(axis=1, keepdims=True)            # p(curr | prev)
    return float(-(counts * np.log2(p)).sum())


def ngram_mdl_proxy_cat(stream, n_features=None, alphabet=None):
    """K2 categorical: per-feature factorized bigram MDL, marginal-relative.

    For each feature, compare the two-part description length of a per-feature
    bigram model p(v_t | v_{t-1}) against the per-feature MARGINAL model p(v) --
    both on the same T-1 transition targets, both Rissanen-penalized:

        L_bigram(j)   = bigram NLL(j)   + 0.5 * A*(A-1) * log2(T)
        L_marginal(j) = marginal NLL(j) + 0.5 * (A-1)   * log2(T)
        C_K2 = 1 - sum_j L_bigram(j) / sum_j L_marginal(j)   (clipped to [0, 1])

    Reads lag-1 temporal predictability BEYOND each feature's marginal. A feature
    whose only structure is a skewed marginal (no autocorrelation) has
    L_bigram ~ L_marginal and contributes ~0 -- the marginal-relative fix.

    Parameters
    ----------
    stream : ndarray (n_steps, n_features), integer in [0, alphabet)
    n_features : int, optional   -- must match stream.shape[1] if given
    alphabet : int, optional     -- alphabet size; inferred (max+1) if None

    Returns
    -------
    C_hat : float in [0, 1]
    """
    arr, T, n, A = _validate(stream, n_features, alphabet)
    log2T = float(np.log2(T))
    pen_bigram = 0.5 * A * (A - 1) * log2T
    pen_marg = 0.5 * (A - 1) * log2T

    prev = arr[:-1]
    curr = arr[1:]
    L_bigram = 0.0
    L_marg = 0.0
    for j in range(n):
        L_bigram += _bigram_nll_bits(prev[:, j], curr[:, j], A) + pen_bigram
        L_marg += _marginal_nll_bits(curr[:, j], A) + pen_marg

    if L_marg <= 0.0:
        return 0.0
    C_hat = 1.0 - L_bigram / L_marg
    return float(np.clip(C_hat, 0.0, 1.0))


def neural_prequential_proxy_cat(stream, n_features=None, alphabet=None):
    """K3 categorical: GRU prequential cross-entropy, marginal-relative.

    Strict cumulative prequential SGD over a single-layer GRU, generalized from the
    v0.5.3 binary K3: each feature is one-hot encoded (input dim n*A) and predicted by
    its own softmax head (output dim n*A, per-feature CrossEntropy). At each step t,
    predict x_t from h_{t-1}, accumulate per-feature cross-entropy in bits, take one SGD
    step, then advance the hidden state with one-hot(x_t) (TBPTT(1) via h.detach()).

        H_pred     = (1 / (T*n)) * sum_t sum_j CE_bits(x_t^j, head_j)
        H_marginal = (1 / n) * sum_j H_hat(marginal_j)        (the marginal-relative baseline)
        C_K3 = 1 - H_pred / H_marginal                        (clipped to [0, 1])

    A feature with only a skewed marginal is predicted at best at its marginal entropy
    (plus online learning overhead), so C_K3 ~ 0 -- the marginal-relative lock. Carries
    NEURAL_SEED=7, CPU-only, use_deterministic_algorithms(True) (saved/restored).

    Parameters
    ----------
    stream : ndarray (n_steps, n_features), integer in [0, alphabet)
    n_features : int, optional   -- must match stream.shape[1] if given
    alphabet : int, optional     -- alphabet size; inferred (max+1) if None

    Returns
    -------
    C_hat : float in [0, 1]
    """
    arr, T, n, A = _validate(stream, n_features, alphabet)

    H_marg = float(np.mean([_marginal_entropy_bits(arr[:, j], A) for j in range(n)]))
    if H_marg <= 0.0:
        return 0.0

    import torch  # lazy: keep K2 numpy-only on import

    prev_deterministic = torch.are_deterministic_algorithms_enabled()
    torch.use_deterministic_algorithms(True)
    try:
        torch.manual_seed(NEURAL_SEED)
        gru = torch.nn.GRU(input_size=n * A, hidden_size=_HIDDEN_DIM, num_layers=1)
        linear = torch.nn.Linear(_HIDDEN_DIM, n * A)
        ce_loss = torch.nn.CrossEntropyLoss(reduction="sum")
        optimizer = torch.optim.SGD(
            list(gru.parameters()) + list(linear.parameters()),
            lr=_LEARNING_RATE, momentum=0.0, weight_decay=0.0,
        )

        idx = torch.from_numpy(arr)                          # (T, n) int64 class indices
        onehot = torch.zeros(T, n, A)
        onehot.scatter_(2, idx.unsqueeze(2), 1.0)            # (T, n, A)
        x_in = onehot.reshape(T, n * A).to(torch.float32)    # (T, n*A) GRU input

        h = torch.zeros(1, 1, _HIDDEN_DIM)
        total_loss_bits = 0.0
        for t in range(T):
            logits_t = linear(h.squeeze(0)).view(n, A)       # (n, A): n per-feature heads
            loss_nats = ce_loss(logits_t, idx[t])            # summed over the n features
            total_loss_bits += loss_nats.item() / _LOG2

            optimizer.zero_grad()
            loss_nats.backward()
            optimizer.step()

            _, h = gru(x_in[t:t + 1].unsqueeze(0), h.detach())  # advance with one-hot(x_t)

        H_pred = total_loss_bits / (T * n)
        C_K3 = 1.0 - H_pred / H_marg
        return float(np.clip(C_K3, 0.0, 1.0))
    finally:
        torch.use_deterministic_algorithms(prev_deterministic)


# --------------------------------------------------------------------------- #
# K4 categorical: factorized-categorical-emission HMM, marginal-relative       #
# --------------------------------------------------------------------------- #

def _emission_loglik_cat(X, logp):
    """Per-step per-state emission log-lik (nats): logB[t,h] = sum_j logp[h, j, X[t,j]]."""
    T, n = X.shape
    H = logp.shape[0]
    logB = np.zeros((T, H))
    for j in range(n):
        logB += logp[:, j, X[:, j]].T            # (H, T).T -> (T, H)
    return logB


def _forward_logP_cat(logB, A_trans, pi):
    """Scaled forward pass; returns log P(data) in nats on the given params."""
    T, H = logB.shape
    rowmax = logB.max(axis=1, keepdims=True)
    Bs = np.exp(logB - rowmax)
    a = pi * Bs[0]
    s = a.sum(); a /= s
    logP = float(np.log(s) + rowmax[0, 0])
    for t in range(1, T):
        a = (a @ A_trans) * Bs[t]
        s = a.sum(); a /= s
        logP += float(np.log(s) + rowmax[t, 0])
    return logP


def _fit_hmm_cat(X, H, A):
    """Fit a factorized-categorical HMM with H states; return L_data in bits.

    H=1 is the closed-form per-feature categorical marginal MLE (no EM) -- this IS the
    marginal-relative baseline. H>=2 runs Baum-Welch EM from one deterministic seeded
    init, then recomputes L_data via an independent forward pass.
    """
    T, n = X.shape

    if H == 1:
        L = 0.0
        for j in range(n):
            counts = np.bincount(X[:, j], minlength=A).astype(np.float64)
            p = np.clip(counts / T, _EMIT_EPS, None); p /= p.sum()
            L += -(counts * np.log2(p)).sum()
        return float(L)

    rng = np.random.default_rng(HMM_SEED)
    base = np.empty((n, A))
    for j in range(n):
        base[j] = np.bincount(X[:, j], minlength=A).astype(np.float64) / T
    p = np.empty((H, n, A))
    for h in range(H):
        pj = np.clip(base + rng.uniform(-0.1, 0.1, size=(n, A)), _EMIT_EPS, None)
        p[h] = pj / pj.sum(axis=1, keepdims=True)
    A_trans = np.full((H, H), (1.0 - _SELF_TRANS) / (H - 1))
    np.fill_diagonal(A_trans, _SELF_TRANS)
    pi = np.full(H, 1.0 / H)

    prev = -np.inf
    for _ in range(_HMM_MAX_ITER):
        logB = _emission_loglik_cat(X, np.log(p))
        rowmax = logB.max(axis=1, keepdims=True)
        Bs = np.exp(logB - rowmax)

        alpha = np.empty((T, H)); c = np.empty(T)
        alpha[0] = pi * Bs[0]; c[0] = alpha[0].sum(); alpha[0] /= c[0]
        for t in range(1, T):
            alpha[t] = (alpha[t - 1] @ A_trans) * Bs[t]
            c[t] = alpha[t].sum(); alpha[t] /= c[t]
        logP = float(np.log(c).sum() + rowmax.sum())

        beta = np.empty((T, H)); beta[T - 1] = 1.0
        for t in range(T - 2, -1, -1):
            beta[t] = (A_trans @ (Bs[t + 1] * beta[t + 1])) / c[t + 1]

        gamma = alpha * beta
        U = (Bs[1:] * beta[1:]) / c[1:, None]
        xi_sum = A_trans * (alpha[:-1].T @ U)

        pi = gamma[0] / gamma[0].sum()
        denom_A = gamma[:-1].sum(axis=0)[:, None]
        A_trans = xi_sum / np.maximum(denom_A, _TRANS_EPS)
        A_trans = np.maximum(A_trans, _TRANS_EPS)
        A_trans /= A_trans.sum(axis=1, keepdims=True)

        gsum = gamma.sum(axis=0)                          # (H,)
        for j in range(n):
            onehot = np.zeros((T, A)); onehot[np.arange(T), X[:, j]] = 1.0
            num = gamma.T @ onehot                        # (H, A)
            pj = np.clip(num / np.maximum(gsum[:, None], _EMIT_EPS), _EMIT_EPS, None)
            p[:, j, :] = pj / pj.sum(axis=1, keepdims=True)

        mean_ll = logP / T
        if mean_ll - prev < _HMM_TOL:
            break
        prev = mean_ll

    logP = _forward_logP_cat(_emission_loglik_cat(X, np.log(p)), A_trans, pi)
    return float(-logP / _LOG2)


def mdl_hmm_proxy_cat(stream, n_features=None, alphabet=None):
    """K4 categorical: factorized-categorical HMM with cardinality selection, marginal-relative.

    Fits a factorized-categorical-emission HMM at each H in {1,2,3,4}, scores each by
    two-part description length (data + Rissanen penalty), and measures the selected
    length against the H=1 baseline -- which IS the per-feature categorical marginal:

        L(H)         = L_data(H) + 0.5 * num_params(H) * log2(T)
        num_params(H)= H*(H-1) [transition] + H*n*(A-1) [emission] + (H-1) [initial]
        C_K4 = 1 - min_H L(H) / L(1)            (clipped to [0, 1])

    Marginal-relative by construction: H=1 is the marginal model, so a stream with no
    latent structure (a distractor) has min at H=1 and scores exactly 0, regardless of
    how skewed its marginal is. Carries HMM_SEED=0, CPU/numpy, deterministic.

    Parameters
    ----------
    stream : ndarray (n_steps, n_features), integer in [0, alphabet)
    n_features : int, optional   -- must match stream.shape[1] if given
    alphabet : int, optional     -- alphabet size; inferred (max+1) if None

    Returns
    -------
    C_hat : float in [0, 1]
    """
    arr, T, n, A = _validate(stream, n_features, alphabet)
    log2T = float(np.log2(T))

    L_by_H = {}
    for H in _H_CANDIDATES:
        L_data = _fit_hmm_cat(arr, H, A)
        num_params = H * (H - 1) + H * n * (A - 1) + (H - 1)
        L_by_H[H] = L_data + 0.5 * num_params * log2T

    L_baseline = L_by_H[1]                                  # H=1 = per-feature marginal
    if L_baseline <= 0.0:
        return 0.0
    C_hat = 1.0 - min(L_by_H.values()) / L_baseline
    return float(np.clip(C_hat, 0.0, 1.0))
