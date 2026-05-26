"""Synthetic stream generators with controlled statistics.

These generators are the test substrate for the CIT pipeline. The Shannon-
recovery test in v0.1 requires only an i.i.d. categorical generator and an
empirical PMF estimator. Later versions will add Markov streams and labelled
coherence-bearing-vs-noise streams for ablation testing.

References
----------
James, B. (2026). Engineering Induced Coherence Weights for Coherence
    Information Theory. PhilPapers.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

__all__ = [
    "iid_categorical_stream",
    "empirical_pmf",
]


def iid_categorical_stream(
    probs: ArrayLike,
    n: int,
    rng: np.random.Generator | None = None,
) -> NDArray[np.int64]:
    """Draw n i.i.d. samples from a categorical distribution.

    Parameters
    ----------
    probs : array-like
        Probability distribution over the alphabet {0, ..., len(probs) - 1}.
        Must be non-negative and sum to 1.
    n : int
        Number of samples to draw.
    rng : np.random.Generator, optional
        Random generator. If None, a fresh default_rng() is created. For
        reproducible output, pass a seeded generator, e.g.
        ``np.random.default_rng(42)``.

    Returns
    -------
    ndarray of shape (n,), dtype int64
        Samples in {0, ..., len(probs) - 1}.
    """
    p = np.asarray(probs, dtype=np.float64)
    if p.ndim != 1:
        raise ValueError(f"probs must be 1D (got ndim={p.ndim}).")
    if np.any(p < 0):
        raise ValueError("Probabilities must be non-negative.")
    total = float(p.sum())
    if not np.isclose(total, 1.0, atol=1e-6):
        raise ValueError(f"Probabilities must sum to 1.0 (got {total:.6f}).")
    if n <= 0:
        raise ValueError(f"n must be positive (got {n}).")
    if rng is None:
        rng = np.random.default_rng()
    return rng.choice(len(p), size=n, p=p).astype(np.int64)


def empirical_pmf(
    samples: ArrayLike,
    alphabet_size: int | None = None,
) -> NDArray[np.float64]:
    """Compute the empirical probability mass function from observed samples.

    Parameters
    ----------
    samples : array-like of integers
        Observed symbols, each in {0, ..., alphabet_size - 1}.
    alphabet_size : int, optional
        Size of the alphabet. If None, inferred as samples.max() + 1.
        Specifying it explicitly ensures the output has the right length
        even when some symbols never appear in the sample.

    Returns
    -------
    ndarray of float
        Empirical PMF of length alphabet_size, summing to 1.
    """
    s = np.asarray(samples, dtype=np.int64)
    if s.ndim != 1:
        raise ValueError(f"samples must be 1D (got ndim={s.ndim}).")
    if s.size == 0:
        raise ValueError("samples is empty.")
    if np.any(s < 0):
        raise ValueError("samples must contain non-negative integers.")
    observed_max = int(s.max())
    if alphabet_size is None:
        alphabet_size = observed_max + 1
    elif alphabet_size <= observed_max:
        raise ValueError(
            f"alphabet_size ({alphabet_size}) is too small for observed "
            f"max symbol ({observed_max})."
        )
    counts = np.bincount(s, minlength=alphabet_size).astype(np.float64)
    return counts / counts.sum()
