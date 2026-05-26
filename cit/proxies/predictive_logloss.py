"""Predictive log-loss coherence proxy (form B from cit_engineering.pdf).

Implements the predictability-based coherence proxy:

    Ĉ_t = 1 − (−log p̂(x_{t+1} | x_t)) / log|X|

bounded to [0, 1]. Uses a first-order Markov predictor with Laplace
(add-one) smoothing as a minimal, transparent estimator. The proxy
returns ~0 for uniformly random streams and ~1 for fully predictable ones.

Per the v0.2 pre-registration, this is the primary proxy on synthetic
streams. The compression-delta proxy (form A) lands later as a secondary
sanity check; more sophisticated estimators (K₃ transformer-prequential,
K₄ MDL-HMM) come in v0.3.

References
----------
James, B. (2026). Engineering Induced Coherence Weights for Coherence
    Information Theory. PhilPapers, §"Coherence proxy".
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

__all__ = [
    "fit_first_order_transitions",
    "next_step_logloss",
    "predictive_logloss_proxy",
]

_EPS = 1e-300  # guard log(0) without affecting valid probabilities


def fit_first_order_transitions(
    stream: ArrayLike,
    alphabet_size: int,
    pseudocount: float = 1.0,
) -> NDArray[np.float64]:
    """Estimate first-order transition probabilities with add-one smoothing.

    Parameters
    ----------
    stream : array-like of int
        Symbol stream of length >= 2.
    alphabet_size : int
        Size of the alphabet K. Symbols must be in [0, K).
    pseudocount : float
        Smoothing pseudocount added to each (i, j) count cell. Default 1.0
        (Laplace smoothing). Must be > 0 to keep all rows normalizable
        even when a symbol never appears as a predecessor.

    Returns
    -------
    P : ndarray of shape (K, K)
        Row-stochastic matrix where ``P[i, j]`` is the estimated
        ``P(x_{t+1} = j | x_t = i)``.
    """
    s = np.asarray(stream, dtype=np.int64)
    if s.ndim != 1 or s.size < 2:
        raise ValueError(f"stream must be 1D with length >= 2 (got shape {s.shape}).")
    if alphabet_size < 2:
        raise ValueError(f"alphabet_size must be >= 2 (got {alphabet_size}).")
    if pseudocount <= 0:
        raise ValueError(f"pseudocount must be > 0 (got {pseudocount}).")
    if int(s.min()) < 0 or int(s.max()) >= alphabet_size:
        raise ValueError(
            f"stream contains symbols outside [0, {alphabet_size})."
        )

    counts = np.full(
        (alphabet_size, alphabet_size), fill_value=pseudocount, dtype=np.float64
    )
    np.add.at(counts, (s[:-1], s[1:]), 1.0)
    row_totals = counts.sum(axis=1, keepdims=True)
    return counts / row_totals


def next_step_logloss(
    stream: ArrayLike,
    transition_matrix: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Per-step negative log-likelihood under a first-order transition matrix.

    Parameters
    ----------
    stream : array-like of int
        Symbol stream of length n >= 2.
    transition_matrix : ndarray of shape (K, K)
        Row-stochastic matrix; ``transition_matrix[i, j]`` is
        ``P(x_{t+1} = j | x_t = i)``.

    Returns
    -------
    ndarray of shape (n - 1,)
        Entry t is ``-log P(x_{t+1} | x_t)`` (natural log).
    """
    s = np.asarray(stream, dtype=np.int64)
    p = transition_matrix[s[:-1], s[1:]]
    return -np.log(np.maximum(p, _EPS))


def predictive_logloss_proxy(
    stream: ArrayLike,
    alphabet_size: int | None = None,
    pseudocount: float = 1.0,
) -> float:
    """Compute coherence proxy Ĉ via predictive log-loss (form B).

    Fits a first-order Markov predictor with Laplace smoothing on the
    given stream, then computes the average normalized predictive
    log-loss over the same stream:

        Ĉ = 1 − mean_t[ -log p̂(x_{t+1} | x_t) ] / log(K)

    A fully predictable stream gives Ĉ → 1 (log-loss → 0).
    A uniformly random stream gives Ĉ → 0 (log-loss → log K).

    Parameters
    ----------
    stream : array-like of int
        Symbol stream of length >= 2.
    alphabet_size : int, optional
        Size of the alphabet K. If None, inferred as ``stream.max() + 1``.
        Pass explicitly when some alphabet symbols may not appear in the
        stream — for example, after ablation, where keeping ``K`` fixed
        is what makes Ĉ comparable across original and ablated streams.
    pseudocount : float
        Laplace smoothing pseudocount, default 1.0.

    Returns
    -------
    float
        Coherence proxy Ĉ in [0, 1]. Higher = more predictable structure.

    Notes
    -----
    "Fit on the stream, evaluate on the stream" prequential mode.
    Sophisticated estimators (transformer prequential coding, MDL-HMM,
    Lempel parsing) are pre-registered as K₃, K₄, K₅ for v0.3.
    """
    s = np.asarray(stream, dtype=np.int64)
    if s.ndim != 1 or s.size < 2:
        raise ValueError(f"stream must be 1D with length >= 2 (got shape {s.shape}).")
    if alphabet_size is None:
        alphabet_size = int(s.max()) + 1
    if alphabet_size < 2:
        raise ValueError(f"alphabet_size must be >= 2 (got {alphabet_size}).")

    P = fit_first_order_transitions(
        s, alphabet_size=alphabet_size, pseudocount=pseudocount
    )
    nll = next_step_logloss(s, P)
    max_nll = float(np.log(alphabet_size))
    mean_nll = float(nll.mean())
    c_hat = 1.0 - mean_nll / max_nll
    # Smoothing can push mean_nll slightly above log K in pathological
    # cases (e.g., extreme ablations); clip into [0, 1] for safety.
    return float(np.clip(c_hat, 0.0, 1.0))
