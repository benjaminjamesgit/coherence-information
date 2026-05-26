"""Synthetic stream generators with controlled statistics.

These generators are the test substrate for the CIT pipeline.

- ``iid_categorical_stream`` and ``empirical_pmf`` underpin the v0.1
  Shannon-recovery tests.
- ``labeled_coherence_stream`` is the v0.2 falsifiability substrate: it
  generates a stream over a finite alphabet in which a known subset of
  symbols carries Markov-chain structure (coherence-bearing) while the
  remainder is injected i.i.d. (noise). The ground-truth labels enable
  empirical verification that the induction pipeline assigns high ``w``
  to coherence-bearing symbols and low ``w`` to noise symbols.

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
    "labeled_coherence_stream",
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


def labeled_coherence_stream(
    n_steps: int,
    n_coherent: int = 2,
    n_noise: int = 3,
    self_transition_prob: float = 0.9,
    noise_injection_prob: float = 0.2,
    rng: np.random.Generator | None = None,
) -> tuple[NDArray[np.int64], dict[str, list[int]]]:
    """Generate a labeled stream with known coherence-bearing and noise symbols.

    Constructs a stream over the alphabet {0, ..., n_coherent + n_noise - 1}.
    Coherent symbols {0, ..., n_coherent - 1} follow a sticky first-order
    Markov chain with self-transition probability ``self_transition_prob``.
    Noise symbols {n_coherent, ..., n_coherent + n_noise - 1} are injected
    i.i.d. at each step with probability ``noise_injection_prob`` and do
    NOT update the Markov state — the coherent chain resumes from the same
    state after a noise interjection.

    The construction guarantees:

    - Coherent symbols carry temporal structure (Markov predictability).
    - Noise symbols carry no temporal structure (i.i.d., state-independent).
    - Removing a coherent symbol disrupts predictability; removing a noise
      symbol does not.

    This is the ground truth that v0.2's induction pipeline must recover:
    ``ρ(x) > 0`` for x in ``labels['coherence_bearing']``, ``ρ(x) ≈ 0``
    for x in ``labels['noise']``.

    Parameters
    ----------
    n_steps : int
        Number of timesteps in the stream. Must be >= 1.
    n_coherent : int
        Number of coherence-bearing symbols. Must be >= 2 (needed for
        non-trivial transitions).
    n_noise : int
        Number of noise symbols. Must be >= 1.
    self_transition_prob : float
        Self-loop probability of the coherent Markov chain, in [0, 1].
        Higher values produce more predictable coherent runs.
    noise_injection_prob : float
        Per-step probability of injecting a noise symbol instead of taking
        a coherent Markov step, in [0, 1].
    rng : np.random.Generator, optional
        Random generator. If None, a fresh default_rng() is created. Pass
        a seeded generator for reproducibility.

    Returns
    -------
    stream : ndarray of shape (n_steps,), dtype int64
        The symbol stream.
    labels : dict[str, list[int]]
        Keys ``'coherence_bearing'`` and ``'noise'``, each mapping to a
        sorted list of symbol indices in the corresponding class.
    """
    if n_steps < 1:
        raise ValueError(f"n_steps must be positive (got {n_steps}).")
    if n_coherent < 2:
        raise ValueError(f"n_coherent must be >= 2 (got {n_coherent}).")
    if n_noise < 1:
        raise ValueError(f"n_noise must be >= 1 (got {n_noise}).")
    if not 0.0 <= self_transition_prob <= 1.0:
        raise ValueError(
            f"self_transition_prob must be in [0, 1] (got {self_transition_prob})."
        )
    if not 0.0 <= noise_injection_prob <= 1.0:
        raise ValueError(
            f"noise_injection_prob must be in [0, 1] (got {noise_injection_prob})."
        )
    if rng is None:
        rng = np.random.default_rng()

    coherent_symbols = list(range(n_coherent))
    noise_symbols = list(range(n_coherent, n_coherent + n_noise))

    stream = np.empty(n_steps, dtype=np.int64)
    current = int(rng.choice(coherent_symbols))  # initial Markov state

    for t in range(n_steps):
        if rng.random() < noise_injection_prob:
            # Noise step: emit a uniformly chosen noise symbol; do NOT
            # update the Markov state.
            stream[t] = int(rng.choice(noise_symbols))
        else:
            # Coherent step: Markov transition, then emit.
            if rng.random() >= self_transition_prob:
                # Transition to a different coherent symbol uniformly.
                others = [s for s in coherent_symbols if s != current]
                current = int(rng.choice(others))
            stream[t] = current

    labels = {
        "coherence_bearing": coherent_symbols,
        "noise": noise_symbols,
    }
    return stream, labels
