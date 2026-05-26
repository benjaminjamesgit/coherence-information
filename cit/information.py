"""Coherence-weighted information quantities.

Implements the core formal objects from Coherence Information Theory:

    H(X)       = -sum_x p(x) log p(x)                           (Shannon)
    H_w(X)     = sum_x p(x) w(x) [-log p(x)]                    (coherence entropy)
    I_w(X; Y)  = sum_{x,y} p(x,y) w(x) log[p(x,y) / p(x) p(y)]  (coherence MI)

H_w and I_w collapse exactly to their Shannon counterparts when w(x) = 1 for
all x. That boundary condition is what licenses CIT as a generalization, not
a replacement, of classical information theory.

References
----------
James, B. (2025). Formal Foundations of Coherence Information Theory:
    Capacity and Compression Theorems. PhilPapers.
James, B. (2025). Beyond Shannon: Coherence Information Theory and the
    Future of Communication. PhilPapers.
James, B. (2026). Formal Foundation of Induced Coherence Weights.
    PhilPapers.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

__all__ = [
    "shannon_entropy",
    "coherence_weighted_entropy",
    "coherence_weighted_mutual_information",
    "pmf_from_counts",
    "H",
    "H_w",
    "I_w",
]

# Smallest positive double; guards log(0) without distorting valid probs
# because the limit p * log(p) -> 0 as p -> 0 anyway.
_EPS = 1e-300


def _log(x: NDArray[np.float64], base: float) -> NDArray[np.float64]:
    """Logarithm in the requested base; dispatches to stable ufuncs."""
    if base == 2.0:
        return np.log2(x)
    if base == 10.0:
        return np.log10(x)
    return np.log(x) / np.log(base)


def _check_probs_1d(probs: NDArray[np.float64]) -> None:
    if probs.ndim != 1:
        raise ValueError(f"Distribution must be 1D (got ndim={probs.ndim}).")
    if np.any(probs < 0):
        raise ValueError("Probabilities must be non-negative.")
    total = float(probs.sum())
    if not np.isclose(total, 1.0, atol=1e-6):
        raise ValueError(f"Probabilities must sum to 1.0 (got {total:.6f}).")


def _check_weights(weights: NDArray[np.float64], n: int) -> None:
    if weights.ndim != 1:
        raise ValueError(f"Weights must be 1D (got ndim={weights.ndim}).")
    if weights.shape[0] != n:
        raise ValueError(
            f"Weight length {weights.shape[0]} != distribution length {n}."
        )
    if np.any(weights < 0) or np.any(weights > 1):
        raise ValueError("Weights must lie in [0, 1].")


def pmf_from_counts(counts: ArrayLike) -> NDArray[np.float64]:
    """Normalize a non-negative count vector to a probability mass function.

    Parameters
    ----------
    counts : array-like
        Symbol counts, all non-negative.

    Returns
    -------
    ndarray of float
        Normalized probabilities summing to 1.
    """
    c = np.asarray(counts, dtype=np.float64)
    if np.any(c < 0):
        raise ValueError("Counts must be non-negative.")
    total = c.sum()
    if total <= 0:
        raise ValueError("Counts must sum to a positive number.")
    return c / total


def shannon_entropy(probs: ArrayLike, base: float = 2.0) -> float:
    """Shannon entropy H(X) = -sum_x p(x) log p(x).

    Parameters
    ----------
    probs : array-like
        Probability distribution over a finite alphabet.
    base : float, optional
        Logarithm base. 2 -> bits (default), e -> nats, 10 -> dits.

    Returns
    -------
    float
        Entropy in the units determined by ``base``.
    """
    p = np.asarray(probs, dtype=np.float64)
    _check_probs_1d(p)
    surprisal = -_log(np.maximum(p, _EPS), base)
    return float(np.sum(p * surprisal))


def coherence_weighted_entropy(
    probs: ArrayLike,
    weights: ArrayLike,
    base: float = 2.0,
) -> float:
    """Coherence-weighted entropy H_w(X) = sum_x p(x) w(x) [-log p(x)].

    Reduces exactly to Shannon entropy when w(x) = 1 for all x.

    Parameters
    ----------
    probs : array-like
        Probability distribution over a finite alphabet of size n.
    weights : array-like
        Coherence weights w(x) in [0, 1], one per symbol. Length n.
    base : float, optional
        Logarithm base. Default 2 (bits).

    Returns
    -------
    float
        Coherence-weighted entropy in the units determined by ``base``.

    Notes
    -----
    The convention w(x) in [0, 1] is the admissibility constraint M1
    (boundedness) from James (2026).
    """
    p = np.asarray(probs, dtype=np.float64)
    w = np.asarray(weights, dtype=np.float64)
    _check_probs_1d(p)
    _check_weights(w, n=p.shape[0])
    surprisal = -_log(np.maximum(p, _EPS), base)
    return float(np.sum(p * w * surprisal))


def coherence_weighted_mutual_information(
    joint: ArrayLike,
    weights: ArrayLike,
    base: float = 2.0,
) -> float:
    """Coherence-weighted mutual information I_w(X; Y).

    I_w(X; Y) = sum_{x,y} p(x, y) w(x) log[p(x, y) / (p(x) p(y))]

    The weight w(x) attaches to the source symbol x. Reduces to classical
    mutual information when w(x) = 1 for all x.

    Parameters
    ----------
    joint : array-like of shape (n_x, n_y)
        Joint probability distribution p(x, y). Non-negative; sums to 1.
    weights : array-like of length n_x
        Coherence weights w(x) over the source alphabet, in [0, 1].
    base : float, optional
        Logarithm base. Default 2 (bits).

    Returns
    -------
    float
        Coherence-weighted mutual information.
    """
    pxy = np.asarray(joint, dtype=np.float64)
    w = np.asarray(weights, dtype=np.float64)
    if pxy.ndim != 2:
        raise ValueError(f"Joint distribution must be 2D (got ndim={pxy.ndim}).")
    if np.any(pxy < 0):
        raise ValueError("Joint probabilities must be non-negative.")
    total = float(pxy.sum())
    if not np.isclose(total, 1.0, atol=1e-6):
        raise ValueError(f"Joint must sum to 1.0 (got {total:.6f}).")
    _check_weights(w, n=pxy.shape[0])

    px = pxy.sum(axis=1, keepdims=True)
    py = pxy.sum(axis=0, keepdims=True)

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(
            pxy > 0,
            pxy / np.maximum(px * py, _EPS),
            1.0,  # log(1) = 0; these positions contribute nothing
        )
        log_ratio = _log(np.maximum(ratio, _EPS), base)

    contribution = pxy * w[:, None] * log_ratio
    return float(contribution.sum())


# Aliases matching the paper notation.
H = shannon_entropy
H_w = coherence_weighted_entropy
I_w = coherence_weighted_mutual_information
