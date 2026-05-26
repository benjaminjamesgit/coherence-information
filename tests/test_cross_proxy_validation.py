"""Cross-proxy validation tests for v0.3.

Locks the empirical invariants that establish cross-philosophy
convergence between the two coherence proxies:

- ``predictive_logloss_proxy`` (form B): symbol-level Markov prediction
- ``compression_delta_proxy`` (form A, K₁): byte-level zstd compression

Per Metacoherence §3.1, agreement between coding-based and
predictability-based estimators on which symbols carry structure is
the operational form of cross-philosophy convergence at the
within-domain level. The R2 threshold — Spearman ρ ≥ 0.7 over ρ
vectors — is the locked v0.3 test invariant.
"""

from __future__ import annotations

import numpy as np
import pytest

from cit.ablations.loo import leave_one_out_ablation
from cit.data.synthetic import (
    iid_categorical_stream,
    labeled_coherence_stream,
)
from cit.induce import induce_weights
from cit.proxies.compression_delta import (
    compression_delta_proxy,
    encode_stream_to_bytes,
)
from cit.proxies.predictive_logloss import predictive_logloss_proxy


# Pre-registered v0.2 seeds and stream parameters (reused for v0.3)
STREAM_SEED = 42
ABLATION_SEED = 123

N_STEPS = 20_000
N_COHERENT = 2
N_NOISE = 3
SELF_TRANS = 0.9
NOISE_INJ = 0.2
ALPHABET_SIZE = N_COHERENT + N_NOISE

# Cross-proxy R2 threshold from Metacoherence §3.1
R2_SPEARMAN_THRESHOLD = 0.7


def _spearman_corr(x, y):
    """Spearman rank correlation between two same-length sequences.

    Implemented via numpy.argsort to avoid a scipy dependency. Equivalent
    to scipy.stats.spearmanr for tie-free inputs.
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    x_rank = np.argsort(np.argsort(x))
    y_rank = np.argsort(np.argsort(y))
    return float(np.corrcoef(x_rank, y_rank)[0, 1])


@pytest.fixture
def labeled_stream_and_labels():
    rng = np.random.default_rng(STREAM_SEED)
    stream, labels = labeled_coherence_stream(
        n_steps=N_STEPS,
        n_coherent=N_COHERENT,
        n_noise=N_NOISE,
        self_transition_prob=SELF_TRANS,
        noise_injection_prob=NOISE_INJ,
        rng=rng,
    )
    return stream, labels


# ---------------------------------------------------------------------------
# Compression-delta proxy (K₁) in isolation
# ---------------------------------------------------------------------------


class TestCompressionDeltaProxy:
    def test_bounded_in_unit_interval(self, labeled_stream_and_labels):
        stream, _ = labeled_stream_and_labels
        c = compression_delta_proxy(stream, alphabet_size=ALPHABET_SIZE)
        assert 0.0 <= c <= 1.0

    def test_constant_stream_near_one(self):
        stream = np.zeros(N_STEPS, dtype=np.int64)
        c = compression_delta_proxy(stream, alphabet_size=ALPHABET_SIZE)
        assert c > 0.99

    def test_ordering_invariant(self, labeled_stream_and_labels):
        """K₁ preserves uniform < labeled < constant."""
        labeled, _ = labeled_stream_and_labels
        rng = np.random.default_rng(STREAM_SEED)
        uniform = iid_categorical_stream(
            np.full(ALPHABET_SIZE, 1.0 / ALPHABET_SIZE),
            n=N_STEPS, rng=rng,
        )
        constant = np.zeros(N_STEPS, dtype=np.int64)
        c_u = compression_delta_proxy(uniform, alphabet_size=ALPHABET_SIZE)
        c_l = compression_delta_proxy(labeled, alphabet_size=ALPHABET_SIZE)
        c_c = compression_delta_proxy(constant, alphabet_size=ALPHABET_SIZE)
        assert c_u < c_l < c_c

    def test_rejects_too_short_stream(self):
        with pytest.raises(ValueError, match="length >= 2"):
            compression_delta_proxy(np.array([0]), alphabet_size=3)

    def test_rejects_out_of_range_symbol(self):
        with pytest.raises(ValueError, match="outside"):
            compression_delta_proxy(np.array([0, 1, 5]), alphabet_size=3)

    def test_encode_uses_smallest_dtype(self):
        """uint8 for K ≤ 256, uint16 for larger alphabets."""
        small = encode_stream_to_bytes([0, 1, 2], alphabet_size=4)
        assert len(small) == 3  # uint8: 1 byte per symbol
        big = encode_stream_to_bytes([0, 1, 100], alphabet_size=1000)
        assert len(big) == 6  # uint16: 2 bytes per symbol


# ---------------------------------------------------------------------------
# LOO ablation under K₁
# ---------------------------------------------------------------------------


class TestLeaveOneOutUnderK1:
    def test_canonical_signs(self, labeled_stream_and_labels):
        """K₁ + LOO: rho > 0 for coherent, rho < 0 for noise."""
        stream, labels = labeled_stream_and_labels
        result = leave_one_out_ablation(
            stream,
            alphabet_size=ALPHABET_SIZE,
            proxy=compression_delta_proxy,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        for x in labels["coherence_bearing"]:
            assert result["rho"][x] > 0
        for x in labels["noise"]:
            assert result["rho"][x] < 0

    def test_separation_invariant(self, labeled_stream_and_labels):
        """min rho(coherent) > max rho(noise) under K₁."""
        stream, labels = labeled_stream_and_labels
        result = leave_one_out_ablation(
            stream,
            alphabet_size=ALPHABET_SIZE,
            proxy=compression_delta_proxy,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        rho_coh = [result["rho"][x] for x in labels["coherence_bearing"]]
        rho_noi = [result["rho"][x] for x in labels["noise"]]
        assert min(rho_coh) > max(rho_noi)


# ---------------------------------------------------------------------------
# induce_weights under K₁
# ---------------------------------------------------------------------------


class TestInduceWeightsUnderK1:
    def test_separates_classes_around_half(self, labeled_stream_and_labels):
        """Under K₁: w(coherent) > 0.5, w(noise) < 0.5."""
        stream, labels = labeled_stream_and_labels
        result = induce_weights(
            stream,
            alphabet_size=ALPHABET_SIZE,
            proxy=compression_delta_proxy,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        for x in labels["coherence_bearing"]:
            assert result["w"][x] > 0.5
        for x in labels["noise"]:
            assert result["w"][x] < 0.5


# ---------------------------------------------------------------------------
# Cross-proxy convergence — the R2 invariant
# ---------------------------------------------------------------------------


class TestCrossProxyConvergence:
    def test_rho_rank_correlation_meets_r2_threshold(
        self, labeled_stream_and_labels
    ):
        """Spearman rank correlation of rho across proxies >= 0.7."""
        stream, _ = labeled_stream_and_labels

        r_b = leave_one_out_ablation(
            stream,
            alphabet_size=ALPHABET_SIZE,
            proxy=predictive_logloss_proxy,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        r_a = leave_one_out_ablation(
            stream,
            alphabet_size=ALPHABET_SIZE,
            proxy=compression_delta_proxy,
            rng=np.random.default_rng(ABLATION_SEED),
        )

        symbols = r_b["symbols"]
        rho_b = [r_b["rho"][x] for x in symbols]
        rho_a = [r_a["rho"][x] for x in symbols]
        rho_s = _spearman_corr(rho_b, rho_a)
        assert rho_s >= R2_SPEARMAN_THRESHOLD, (
            f"Cross-proxy Spearman {rho_s:.3f} below R2 threshold "
            f"{R2_SPEARMAN_THRESHOLD}"
        )

    def test_both_proxies_agree_on_sign(self, labeled_stream_and_labels):
        """Every symbol gets the same canonical sign under both proxies."""
        stream, _ = labeled_stream_and_labels

        r_b = leave_one_out_ablation(
            stream,
            alphabet_size=ALPHABET_SIZE,
            proxy=predictive_logloss_proxy,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        r_a = leave_one_out_ablation(
            stream,
            alphabet_size=ALPHABET_SIZE,
            proxy=compression_delta_proxy,
            rng=np.random.default_rng(ABLATION_SEED),
        )

        for x in r_b["symbols"]:
            sign_b = np.sign(r_b["rho"][x])
            sign_a = np.sign(r_a["rho"][x])
            assert sign_b == sign_a, (
                f"Sign disagreement on symbol {x}: B={sign_b}, A={sign_a}"
            )

    def test_both_proxies_class_separation_through_induce_weights(
        self, labeled_stream_and_labels
    ):
        """Independently of proxy choice, induce_weights separates classes."""
        stream, labels = labeled_stream_and_labels

        for proxy in (predictive_logloss_proxy, compression_delta_proxy):
            result = induce_weights(
                stream,
                alphabet_size=ALPHABET_SIZE,
                proxy=proxy,
                rng=np.random.default_rng(ABLATION_SEED),
            )
            for x in labels["coherence_bearing"]:
                assert result["w"][x] > 0.5, (
                    f"{proxy.__name__}: w({x})={result['w'][x]} not > 0.5"
                )
            for x in labels["noise"]:
                assert result["w"][x] < 0.5, (
                    f"{proxy.__name__}: w({x})={result['w'][x]} not < 0.5"
                )
