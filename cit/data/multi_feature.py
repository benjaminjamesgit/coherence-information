"""Multi-feature synthetic substrate for v0.5.

See design/multi_feature_substrate.md (locked 2026-05-26) for the
full specification. This module implements:

    labeled_multi_feature_stream
        Shared-HMM-generated stream with ground-truth labels. Coherent
        features depend on a 2-state hidden Markov chain; noise features
        are i.i.d. Bernoulli(0.5). All features have marginal p=0.5;
        discrimination is purely structural.

    noise_only_multi_feature_stream
        Matched-marginal counterfactual: all features i.i.d. Bernoulli(0.5).
        The structure-absent baseline used at v0.5.5 capstone.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "labeled_multi_feature_stream",
    "noise_only_multi_feature_stream",
    "C_HIDDEN_STATES",
    "SELF_TRANSITION_PROB",
    "N_COHERENT_FEATURES",
    "N_NOISE_FEATURES",
    "N_FEATURES_TOTAL",
    "COHERENT_EMISSION",
    "NOISE_EMISSION_PROB",
    "GROUND_TRUTH_CLUSTERS",
]

C_HIDDEN_STATES = 2
SELF_TRANSITION_PROB = 0.9
N_COHERENT_FEATURES = 4
N_NOISE_FEATURES = 6
N_FEATURES_TOTAL = N_COHERENT_FEATURES + N_NOISE_FEATURES

COHERENT_EMISSION = np.array(
    [
        [0.8, 0.2],
        [0.8, 0.2],
        [0.2, 0.8],
        [0.2, 0.8],
    ],
    dtype=np.float64,
)

NOISE_EMISSION_PROB = 0.5

GROUND_TRUTH_CLUSTERS = {
    "cluster_A": frozenset({0, 1}),
    "cluster_B": frozenset({2, 3}),
}


def labeled_multi_feature_stream(
    n_steps: int = 20_000,
    n_coherent: int = N_COHERENT_FEATURES,
    n_noise: int = N_NOISE_FEATURES,
    rng: np.random.Generator | None = None,
):
    """Shared-HMM substrate stream with ground-truth labels.

    Returns
    -------
    stream : ndarray (n_steps, n_coherent + n_noise), uint8
    labels : dict with keys 'coherence_bearing', 'noise', 'clusters'
    """
    if rng is None:
        rng = np.random.default_rng()
    if n_coherent != N_COHERENT_FEATURES:
        raise ValueError(
            f"v0.5.0 locks n_coherent = {N_COHERENT_FEATURES}; got {n_coherent}"
        )
    if n_noise < 1:
        raise ValueError(f"n_noise must be positive; got {n_noise}")
    if n_steps < 1:
        raise ValueError(f"n_steps must be positive; got {n_steps}")

    n_features = n_coherent + n_noise

    hidden_states = np.empty(n_steps, dtype=np.uint8)
    hidden_states[0] = rng.integers(0, C_HIDDEN_STATES)
    for t in range(1, n_steps):
        if rng.random() < SELF_TRANSITION_PROB:
            hidden_states[t] = hidden_states[t - 1]
        else:
            hidden_states[t] = 1 - hidden_states[t - 1]

    stream = np.empty((n_steps, n_features), dtype=np.uint8)

    coherent_probs = COHERENT_EMISSION[:, hidden_states]
    coherent_draws = rng.random((n_steps, n_coherent))
    stream[:, :n_coherent] = (coherent_draws < coherent_probs.T).astype(np.uint8)

    noise_draws = rng.random((n_steps, n_noise))
    stream[:, n_coherent:] = (noise_draws < NOISE_EMISSION_PROB).astype(np.uint8)

    labels = {
        "coherence_bearing": set(range(n_coherent)),
        "noise": set(range(n_coherent, n_features)),
        "clusters": {
            "cluster_A": set(GROUND_TRUTH_CLUSTERS["cluster_A"]),
            "cluster_B": set(GROUND_TRUTH_CLUSTERS["cluster_B"]),
        },
    }

    return stream, labels


def noise_only_multi_feature_stream(
    n_steps: int = 20_000,
    n_features: int = N_FEATURES_TOTAL,
    rng: np.random.Generator | None = None,
):
    """Matched-marginal counterfactual: all features i.i.d. Bernoulli(0.5).

    Returns
    -------
    stream : ndarray (n_steps, n_features), uint8
    """
    if rng is None:
        rng = np.random.default_rng()
    if n_features < 1:
        raise ValueError(f"n_features must be positive; got {n_features}")
    if n_steps < 1:
        raise ValueError(f"n_steps must be positive; got {n_steps}")

    draws = rng.random((n_steps, n_features))
    return (draws < NOISE_EMISSION_PROB).astype(np.uint8)
