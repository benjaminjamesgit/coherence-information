"""Decoupling-control crossing proxies (v0.7.0 pre-reg 2026-06-23): MODELING
functionals on the BYTE-STREAM representation.

The v0.7.0 A1 grid populates only two of the four (representation x philosophy)
corners -- byte-stream x {coding/parsing} (K1, K5) and categorical-native x
{modeling} (K2, K3, K4) -- which lie on the same diagonal, so representation and
philosophy are confounded. These two proxies fill the empty `byte-stream x modeling`
corner, making representation and philosophy independent axes (pre_registration.md
2026-06-23 decoupling-control entry).

Both apply a MODELING/predictive complexity functional to the IDENTICAL feature-major
byte-stream encoding K1 consumes (`packbits(_encode_bits_cat(...))`) and the IDENTICAL
time-shuffle surrogate baseline (`SHUFFLE_SEED`) K1/K5 use, so {K1, K5, K3b, K2b} share
representation, encoder, baseline, and ablation EXACTLY and differ ONLY in the complexity
functional. complexity = a penalty-free predictive CODE LENGTH (bits) of the byte sequence:

    K3b  -- online single-layer GRU over bytes (the K3 neural-prequential functional), NEURAL_SEED
    K2b  -- online (KT/prequential) bigram over bytes (the K2 bigram-MDL functional), deterministic
    C = 1 - complexity(real) / complexity(time_shuffled_surrogate)        (clipped to [0, 1])

Per the pre-reg, K2b carries MORE model-change than K3b: K3b is genuinely the K3 functional
re-serialized (n=1, alphabet=256), whereas K2b's factorization unit shifts feature -> byte
(a byte-bigram, not a feature-bigram) -- exactly what targets the K2 coalition-blindness, and
the reason a PROXY-SPECIFIC-SPLIT verdict is weighted accordingly.

Proxy contract is identical to the categorical proxies (`stream (T, n) -> C_hat in [0, 1]`,
optional n_features / alphabet), so `induce_weights_cat` + the categorical A1 ablation drive
them unchanged.
"""

from __future__ import annotations

import math

import numpy as np

from cit.proxies.categorical import (
    _validate,
    _encode_bits_cat,
    _time_shuffle,
    SHUFFLE_SEED,
    NEURAL_SEED,
    _LOG2,
    _HIDDEN_DIM,
    _LEARNING_RATE,
)

__all__ = [
    "bigram_mdl_byte_proxy",
    "neural_prequential_byte_proxy",
    "SHUFFLE_SEED",
    "NEURAL_SEED",
]

_BYTE_ALPHABET = 256
_gammaln = np.vectorize(math.lgamma, otypes=[np.float64])


def _byte_stream(arr, alphabet):
    """The feature-major byte serialization K1 consumes: packbits of the bit-tight encoding.

    Returns a 1-D uint8 array (MSB-first bytes); identical to what `compression_delta_proxy_cat`
    hands to zstd, so the crossing proxies share K1's representation EXACTLY.
    """
    return np.packbits(_encode_bits_cat(arr, alphabet))


# --------------------------------------------------------------------------- #
# K2b: online (KT) bigram code length over bytes -- the K2 bigram-MDL functional #
# --------------------------------------------------------------------------- #

def _prequential_bigram_bits(byte_seq):
    """Total prequential (KT) code length in bits of a byte sequence under an online bigram.

    Per context c (previous byte), the symbols following c are coded by the
    Krichevsky-Trofimov sequential estimator; KT is exchangeable, so the per-context code
    length is order-independent and equals the prequential cost. No Rissanen penalty (the
    sequential code length IS the MDL description length), so the alphabet-256 two-part
    penalty -- which would dominate at this alphabet -- never appears.

        -ln P_KT(context) = -sum_a[gammaln(n_a + 1/2) - gammaln(1/2)] + gammaln(N + A/2) - gammaln(A/2)

    summed over contexts (A = 256, N = context count), + log2(A) for the context-free first byte.
    """
    L = int(byte_seq.shape[0])
    if L < 2:
        return float(L) * math.log2(_BYTE_ALPHABET)
    A = _BYTE_ALPHABET
    prev = byte_seq[:-1].astype(np.int64)
    curr = byte_seq[1:].astype(np.int64)
    M = np.zeros((A, A), dtype=np.float64)
    np.add.at(M, (prev, curr), 1.0)

    nz = M > 0
    half = 0.5
    term_emit = float(_gammaln(M[nz] + half).sum()) - float(nz.sum()) * math.lgamma(half)
    Nc = M.sum(axis=1)
    act = Nc > 0
    term_norm = float(_gammaln(Nc[act] + A * half).sum()) - float(act.sum()) * math.lgamma(A * half)

    bits_rest = (term_norm - term_emit) / _LOG2          # = -ln P_KT / ln2 >= 0
    return float(bits_rest + math.log2(A))                # + first byte (uniform-KT start)


def bigram_mdl_byte_proxy(stream, n_features=None, alphabet=None):
    """K2b: prequential byte-bigram code length BEYOND the per-feature marginal (surrogate baseline).

        C_K2b = 1 - bigram_bits(real_bytes) / bigram_bits(time_shuffled_bytes)   (clipped to [0, 1])

    The K2 bigram-MDL philosophy on the byte stream; deterministic (no RNG). A feature whose
    only structure is a (skewed) marginal has real_bytes ~ surrogate_bytes -> C ~ 0; temporal /
    cross-time byte structure compresses the bigram code beyond the surrogate -> C > 0.

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
    real = _prequential_bigram_bits(_byte_stream(arr, A))
    surr = _prequential_bigram_bits(_byte_stream(_time_shuffle(arr, SHUFFLE_SEED), A))
    if surr <= 0.0:
        return 0.0
    return float(np.clip(1.0 - real / surr, 0.0, 1.0))


# --------------------------------------------------------------------------- #
# K3b: online GRU code length over bytes -- the K3 neural-prequential functional #
# --------------------------------------------------------------------------- #

def _prequential_gru_bits(byte_seq):
    """Total online-GRU prequential code length (bits) over a 1-D byte sequence (alphabet 256).

    The K3 neural-prequential functional with n=1 feature, A=256: at each step predict byte_t
    from h_{t-1} (256-way softmax), accumulate CE in bits, take one SGD step, then advance the
    hidden state with one-hot(byte_t) (TBPTT(1) via h.detach()). Carries NEURAL_SEED, CPU-only,
    use_deterministic_algorithms(True) (saved/restored) -- the v0.5.3 K3 discipline.
    """
    A = _BYTE_ALPHABET
    L = int(byte_seq.shape[0])
    if L < 2:
        return float(L) * math.log2(A)

    import torch  # lazy: keep K2b numpy-only on import

    prev_det = torch.are_deterministic_algorithms_enabled()
    torch.use_deterministic_algorithms(True)
    try:
        torch.manual_seed(NEURAL_SEED)
        gru = torch.nn.GRU(input_size=A, hidden_size=_HIDDEN_DIM, num_layers=1)
        linear = torch.nn.Linear(_HIDDEN_DIM, A)
        ce_loss = torch.nn.CrossEntropyLoss(reduction="sum")
        optimizer = torch.optim.SGD(
            list(gru.parameters()) + list(linear.parameters()),
            lr=_LEARNING_RATE, momentum=0.0, weight_decay=0.0,
        )

        idx = torch.from_numpy(np.ascontiguousarray(byte_seq, dtype=np.int64))   # (L,)
        onehot = torch.zeros(L, A)
        onehot.scatter_(1, idx.unsqueeze(1), 1.0)            # (L, A)
        x_in = onehot.to(torch.float32)                      # (L, A)

        h = torch.zeros(1, 1, _HIDDEN_DIM)
        total_bits = 0.0
        for t in range(L):
            logits_t = linear(h.squeeze(0))                  # (1, A)
            loss_nats = ce_loss(logits_t, idx[t:t + 1])      # scalar (one byte)
            total_bits += loss_nats.item() / _LOG2

            optimizer.zero_grad()
            loss_nats.backward()
            optimizer.step()

            _, h = gru(x_in[t:t + 1].unsqueeze(0), h.detach())  # advance with one-hot(byte_t)

        return float(total_bits)
    finally:
        torch.use_deterministic_algorithms(prev_det)


def neural_prequential_byte_proxy(stream, n_features=None, alphabet=None):
    """K3b: prequential GRU byte code length BEYOND the per-feature marginal (surrogate baseline).

        C_K3b = 1 - gru_bits(real_bytes) / gru_bits(time_shuffled_bytes)   (clipped to [0, 1])

    The K3 neural-prequential philosophy on the byte stream -- the lowest-distortion crossing
    (genuinely "same functional, different serialization"). Carries NEURAL_SEED=7, CPU-only,
    deterministic. Runs the GRU TWICE per call (real + surrogate), so this is the heavy crossing:
    the full-T x 20-seed A1 control run is a CI/very_slow artifact.

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
    real = _prequential_gru_bits(_byte_stream(arr, A))
    surr = _prequential_gru_bits(_byte_stream(_time_shuffle(arr, SHUFFLE_SEED), A))
    if surr <= 0.0:
        return 0.0
    return float(np.clip(1.0 - real / surr, 0.0, 1.0))
