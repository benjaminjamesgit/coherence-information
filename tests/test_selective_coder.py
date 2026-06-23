"""v0.6.1 selective compression coder tests.

Locks (pre_registration.md, 2026-06-23 v0.6.1 amendment -- the corrected
Selective Compression Theorem, compress to the merged-source entropy H(Z)):

  - bit-exact round-trip of the arithmetic coder (the safety net),
  - lossless reproduction of every must-preserve symbol (w(x) > delta),
  - achievability: arithmetic rate <= H(Z) + TOL_RATE at N,
  - floor ordering H(Z) <= H(X),
  - the coherence saving vs the weight-blind coder,
  - boundary spine: S_delta = X collapses to Shannon (rate -> H(X)),
  - determinism,
  - and H_w retained as a MEASURE (not a rate), distinct from H(Z).

All fast tier.

References
----------
James, B. (2025). Capacity and Compression Theorems. PhilPapers. (Thm 5.1,
    repaired -- see the 2026-06-23 v0.6.1 amendment.)
"""

from __future__ import annotations

import numpy as np
import pytest

from cit.coders.selective import (
    merged_source_entropy,
    must_preserve_indices,
    rate_bits_per_symbol,
    selective_decode,
    selective_decode_zstd,
    selective_encode,
    selective_encode_zstd,
)
from cit.information import coherence_weighted_entropy, shannon_entropy

STREAM_SEED = 42
N_ACHIEVE = 200_000
TOL_RATE = 0.02  # bits/symbol, locked v0.6.1

# canonical sources: (probs, weights, delta)
SRC_ONE = (  # 1 important symbol, 4 distinct noise symbols
    np.array([0.5, 0.2, 0.15, 0.1, 0.05]),
    np.array([1.0, 0.0, 0.0, 0.0, 0.0]),
    0.5,
)
SRC_GRADED = (  # graded weights: S_delta(0.5) = {0, 1}, 3 noise symbols
    np.array([0.3, 0.25, 0.2, 0.15, 0.1]),
    np.array([1.0, 0.6, 0.3, 0.1, 0.0]),
    0.5,
)


def make_stream(p, n, seed=STREAM_SEED):
    return np.random.default_rng(seed).choice(len(p), size=n, p=p)


# ---------------------------------------------------------------------------
# Bit-exact round-trip -- the safety net for the hand-rolled arithmetic coder
# ---------------------------------------------------------------------------
class TestRoundTrip:
    @pytest.mark.parametrize("K,N", [(2, 1), (2, 7), (5, 33), (3, 1000), (8, 9999)])
    def test_arithmetic_roundtrip_exact(self, K, N):
        rng = np.random.default_rng(100 + K * N)
        p = rng.dirichlet(np.ones(K))
        w = (rng.random(K) > 0.5).astype(float)  # random 0/1 weights
        x = make_stream(p, N, seed=7 + N)
        delta = 0.5
        S = must_preserve_indices(w, delta)
        placeholder = next((s for s in range(K) if s not in set(S)), 0)
        x_hat = selective_decode(selective_encode(x, w, delta))
        # exact reconstruction: S symbols verbatim, everything else -> placeholder
        expected = np.where(np.isin(x, S), x, placeholder)
        assert np.array_equal(x_hat, expected)


# ---------------------------------------------------------------------------
# Lossless on the must-preserve set (both coders)
# ---------------------------------------------------------------------------
class TestLosslessOnS:
    @pytest.mark.parametrize("src", [SRC_ONE, SRC_GRADED])
    def test_arithmetic_lossless_on_S(self, src):
        p, w, delta = src
        x = make_stream(p, 20_000)
        S = must_preserve_indices(w, delta)
        must = np.isin(x, S)
        x_hat = selective_decode(selective_encode(x, w, delta))
        assert np.all(x_hat[must] == x[must])

    @pytest.mark.parametrize("src", [SRC_ONE, SRC_GRADED])
    def test_zstd_lossless_on_S(self, src):
        p, w, delta = src
        x = make_stream(p, 20_000)
        S = must_preserve_indices(w, delta)
        must = np.isin(x, S)
        x_hat = selective_decode_zstd(selective_encode_zstd(x, w, delta))
        assert np.all(x_hat[must] == x[must])


# ---------------------------------------------------------------------------
# Achievability: arithmetic rate approaches H(Z)
# ---------------------------------------------------------------------------
class TestAchievability:
    @pytest.mark.parametrize("src", [SRC_ONE, SRC_GRADED])
    def test_rate_approaches_HZ(self, src):
        p, w, delta = src
        x = make_stream(p, N_ACHIEVE)
        blob = selective_encode(x, w, delta)
        rate = rate_bits_per_symbol(blob, N_ACHIEVE)
        H_Z = merged_source_entropy(p, w, delta)
        assert rate <= H_Z + TOL_RATE
        assert rate >= H_Z - TOL_RATE  # also not implausibly below the floor


# ---------------------------------------------------------------------------
# Floor ordering H(Z) <= H(X)
# ---------------------------------------------------------------------------
class TestFloorOrdering:
    @pytest.mark.parametrize("src", [SRC_ONE, SRC_GRADED])
    def test_HZ_below_HX_strict(self, src):
        p, w, delta = src
        H_Z = merged_source_entropy(p, w, delta)
        H_X = shannon_entropy(p)
        S = must_preserve_indices(w, delta)
        n_dont_care = len(p) - len(S)
        assert H_Z <= H_X + 1e-12
        if n_dont_care >= 2:
            assert H_Z < H_X - 1e-9  # strict when >= 2 symbols are merged

    def test_HZ_equals_HX_when_one_or_zero_merged(self):
        # exactly one don't-care symbol => merging it changes nothing => H(Z)=H(X)
        p = np.array([0.6, 0.4])
        w = np.array([1.0, 0.0])  # S_delta = {0}, one don't-care
        H_Z = merged_source_entropy(p, w, 0.5)
        assert H_Z == pytest.approx(shannon_entropy(p), abs=1e-12)


# ---------------------------------------------------------------------------
# The coherence saving vs the weight-blind coder
# ---------------------------------------------------------------------------
class TestCoherenceSaving:
    @pytest.mark.parametrize("src", [SRC_ONE, SRC_GRADED])
    def test_merged_beats_weight_blind(self, src):
        p, w, delta = src
        x = make_stream(p, 50_000)
        rate_merged = rate_bits_per_symbol(selective_encode(x, w, delta), len(x))
        # weight-blind == delta below all weights => S_delta = X => no merge
        rate_blind = rate_bits_per_symbol(selective_encode(x, w, -0.1), len(x))
        assert rate_merged < rate_blind  # both sources have >= 2 don't-cares


# ---------------------------------------------------------------------------
# Boundary spine: S_delta = X collapses to Shannon
# ---------------------------------------------------------------------------
class TestBoundarySpine:
    def test_w_all_ones_collapses(self):
        p, _, _ = SRC_ONE
        w = np.ones(len(p))
        x = make_stream(p, 50_000)
        H_Z = merged_source_entropy(p, w, 0.5)  # S_delta = X
        H_X = shannon_entropy(p)
        assert H_Z == pytest.approx(H_X, abs=1e-12)
        rate = rate_bits_per_symbol(selective_encode(x, w, 0.5), len(x))
        assert abs(rate - H_X) <= TOL_RATE  # reduces to ordinary lossless coding

    def test_delta_below_all_weights_collapses(self):
        p, w, _ = SRC_GRADED
        x = make_stream(p, 50_000)
        H_Z = merged_source_entropy(p, w, -0.1)  # S_delta = X
        H_X = shannon_entropy(p)
        assert H_Z == pytest.approx(H_X, abs=1e-12)
        rate = rate_bits_per_symbol(selective_encode(x, w, -0.1), len(x))
        assert abs(rate - H_X) <= TOL_RATE


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------
class TestDeterminism:
    def test_arithmetic_bit_identical(self):
        p, w, delta = SRC_GRADED
        x = make_stream(p, 20_000)
        assert selective_encode(x, w, delta) == selective_encode(x, w, delta)

    def test_zstd_bit_identical(self):
        p, w, delta = SRC_GRADED
        x = make_stream(p, 20_000)
        assert selective_encode_zstd(x, w, delta) == selective_encode_zstd(x, w, delta)


# ---------------------------------------------------------------------------
# H_w is retained as a MEASURE, distinct from the compression rate H(Z)
# ---------------------------------------------------------------------------
class TestHwIsMeasure:
    @pytest.mark.parametrize("src", [SRC_ONE, SRC_GRADED])
    def test_Hw_is_a_measure_not_a_rate(self, src):
        p, w, delta = src
        H_w = coherence_weighted_entropy(p, w)  # the "bits that matter" measure
        H_X = shannon_entropy(p)
        H_Z = merged_source_entropy(p, w, delta)
        assert H_w <= H_X + 1e-12          # weighting never increases entropy
        assert H_w != pytest.approx(H_Z)   # measure is NOT the compression floor

    def test_Hw_collapses_to_shannon_at_unit_weights(self):
        p, _, _ = SRC_GRADED
        w = np.ones(len(p))
        assert coherence_weighted_entropy(p, w) == pytest.approx(
            shannon_entropy(p), abs=1e-12
        )
