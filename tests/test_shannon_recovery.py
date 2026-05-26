"""The Shannon-recovery test.

This is the spine the rest of the repository hangs from. It verifies the
boundary condition that licenses Coherence Information Theory as a
generalization of Shannon information theory rather than a replacement:

    H_w(X)    == H(X)     when w(x) == 1 for all x
    I_w(X; Y) == I(X; Y)  when w(x) == 1 for all x

Every future estimator, ablation, weight derivation, or coder must preserve
this collapse. If this test fails, nothing downstream is meaningful.

References
----------
James, B. (2025). Formal Foundations of Coherence Information Theory:
    Capacity and Compression Theorems. PhilPapers.
"""

from __future__ import annotations

import numpy as np
import pytest

from cit.data.synthetic import empirical_pmf, iid_categorical_stream
from cit.information import (
    H,
    H_w,
    I_w,
    coherence_weighted_entropy,
    coherence_weighted_mutual_information,
    shannon_entropy,
)


# Fixed seed for any test using stochastic samples. Locked here so that
# failures are bit-reproducible across machines.
SEED = 42


# ---------------------------------------------------------------------------
# H_w with unit weights collapses to Shannon H, exactly
# ---------------------------------------------------------------------------

def test_unit_weights_recover_shannon_uniform():
    """Uniform-4: H_w(p, w=1) == H(p) == log2(4) == 2.0 bits."""
    p = np.full(4, 0.25)
    w = np.ones(4)
    assert H_w(p, w) == pytest.approx(2.0, abs=1e-12)
    assert H_w(p, w) == pytest.approx(H(p), abs=1e-12)


def test_unit_weights_recover_shannon_skewed():
    """Skewed binary: H_w(p, w=1) == H(p) for an asymmetric distribution."""
    p = np.array([0.9, 0.1])
    w = np.ones(2)
    assert H_w(p, w) == pytest.approx(H(p), abs=1e-12)


@pytest.mark.parametrize("alphabet_size", [2, 3, 5, 8, 16, 64])
def test_unit_weights_recover_shannon_random(alphabet_size):
    """H_w(p, w=1) == H(p) across a range of random distributions."""
    rng = np.random.default_rng(SEED + alphabet_size)
    raw = rng.exponential(scale=1.0, size=alphabet_size)
    p = raw / raw.sum()
    w = np.ones(alphabet_size)
    assert H_w(p, w) == pytest.approx(H(p), abs=1e-12)


# ---------------------------------------------------------------------------
# H_w scales linearly in a constant weight
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("c", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_constant_weight_scales_linearly(c):
    """H_w(p, w == c) == c * H(p) for any constant c in [0, 1]."""
    p = np.array([0.1, 0.2, 0.3, 0.4])
    w = np.full(p.shape, c)
    assert H_w(p, w) == pytest.approx(c * H(p), abs=1e-12)


def test_zero_weights_give_zero_entropy():
    """H_w(p, w == 0) == 0 regardless of p (the all-noise limit)."""
    p = np.array([0.1, 0.2, 0.3, 0.4])
    w = np.zeros(4)
    assert H_w(p, w) == 0.0


# ---------------------------------------------------------------------------
# Empirical recovery: samples -> empirical PMF -> H approaches true H
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "true_p, atol",
    [
        (np.array([0.25, 0.25, 0.25, 0.25]), 1e-3),  # uniform
        (np.array([0.5, 0.3, 0.15, 0.05]), 5e-3),    # skewed (higher variance)
        (np.array([0.99, 0.01]), 5e-3),              # near-deterministic (higher variance)
    ],
)
def test_empirical_entropy_converges_to_true_entropy(true_p, atol):
    """Empirical H from 100k samples lies within atol of the true H."""
    rng = np.random.default_rng(SEED)
    samples = iid_categorical_stream(true_p, n=100_000, rng=rng)
    emp_p = empirical_pmf(samples, alphabet_size=len(true_p))
    assert H(emp_p) == pytest.approx(H(true_p), abs=atol)


def test_empirical_h_w_recovers_empirical_h():
    """On observed samples, H_w with w=1 equals H exactly."""
    rng = np.random.default_rng(SEED)
    true_p = np.array([0.5, 0.3, 0.15, 0.05])
    samples = iid_categorical_stream(true_p, n=10_000, rng=rng)
    emp_p = empirical_pmf(samples, alphabet_size=4)
    w = np.ones(4)
    assert H_w(emp_p, w) == pytest.approx(H(emp_p), abs=1e-12)


# ---------------------------------------------------------------------------
# Edge cases and structural bounds for H_w
# ---------------------------------------------------------------------------

def test_deterministic_distribution_has_zero_entropy():
    """A point mass has H == 0 and H_w == 0 for any weights in [0, 1]."""
    p = np.array([1.0, 0.0, 0.0, 0.0])
    assert H(p) == pytest.approx(0.0, abs=1e-12)
    for w in [np.ones(4), np.zeros(4), np.array([0.0, 1.0, 1.0, 1.0])]:
        assert H_w(p, w) == pytest.approx(0.0, abs=1e-12)


def test_h_w_upper_bounded_by_h():
    """For w(x) in [0, 1], H_w(p, w) <= H(p) always.

    This is a direct consequence of the formula: each term of H_w is the
    corresponding term of H scaled by w(x) <= 1, and surprisal is non-negative.
    """
    rng = np.random.default_rng(SEED)
    for _ in range(20):
        n = int(rng.integers(2, 16))
        raw = rng.exponential(size=n)
        p = raw / raw.sum()
        w = rng.uniform(0, 1, size=n)
        assert H_w(p, w) <= H(p) + 1e-12


# ---------------------------------------------------------------------------
# I_w with unit weights collapses to classical mutual information
# ---------------------------------------------------------------------------

def test_iw_unit_weights_recovers_classical_mi():
    """I_w(X; Y) with w=1 equals the classical I(X; Y) = H(X)+H(Y)-H(X,Y)."""
    pxy = np.array([[0.4, 0.1], [0.1, 0.4]])
    w = np.ones(2)
    px = pxy.sum(axis=1)
    py = pxy.sum(axis=0)
    classical_mi = H(px) + H(py) - H(pxy.flatten())
    assert I_w(pxy, w) == pytest.approx(classical_mi, abs=1e-12)


def test_iw_zero_for_independent_variables():
    """If X and Y are independent, p(x,y) == p(x)p(y), so I == 0 for any w."""
    px = np.array([0.3, 0.7])
    py = np.array([0.4, 0.6])
    pxy = np.outer(px, py)
    assert pxy.sum() == pytest.approx(1.0, abs=1e-12)
    assert I_w(pxy, np.ones(2)) == pytest.approx(0.0, abs=1e-12)
    assert I_w(pxy, np.array([0.5, 0.8])) == pytest.approx(0.0, abs=1e-12)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def test_negative_probabilities_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        H(np.array([0.5, -0.1, 0.6]))


def test_non_normalized_probabilities_rejected():
    with pytest.raises(ValueError, match="sum to 1.0"):
        H(np.array([0.3, 0.3, 0.3]))


def test_out_of_bound_weights_rejected():
    p = np.array([0.5, 0.5])
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        H_w(p, np.array([0.5, 1.5]))


def test_weight_length_mismatch_rejected():
    p = np.array([0.25, 0.25, 0.25, 0.25])
    with pytest.raises(ValueError, match="!="):
        H_w(p, np.array([1.0, 1.0]))


# ---------------------------------------------------------------------------
# Alias parity
# ---------------------------------------------------------------------------

def test_aliases_match_full_function_names():
    """The H / H_w / I_w aliases must be the same callables as the long names."""
    assert H is shannon_entropy
    assert H_w is coherence_weighted_entropy
    assert I_w is coherence_weighted_mutual_information
