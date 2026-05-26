"""Tests for the v0.2 induction pipeline.

Locks the empirical behavior of:

- ``predictive_logloss_proxy`` (form B)
- ``leave_one_out_ablation`` (operator A₁ with replace-with-uniform)
- ``induce_weights`` (full orchestration with locked β = 4.0)

All seeds and stream parameters reflect the v0.2 commitments in
``pre_registration.md``.
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
from cit.proxies.predictive_logloss import predictive_logloss_proxy


# Pre-registered v0.2 seeds
STREAM_SEED = 42
ABLATION_SEED = 123

# Pre-registered v0.2 synthetic-stream parameters
N_STEPS = 20_000
N_COHERENT = 2
N_NOISE = 3
SELF_TRANS = 0.9
NOISE_INJ = 0.2
ALPHABET_SIZE = N_COHERENT + N_NOISE


@pytest.fixture
def labeled_stream_and_labels():
    """The standard labeled synthetic stream used across pipeline tests."""
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
# Predictive log-loss proxy (form B)
# ---------------------------------------------------------------------------


class TestPredictiveLoglossProxy:
    def test_proxy_near_zero_on_uniform_iid(self):
        """Ĉ near 0 for a uniform i.i.d. stream (no temporal structure)."""
        rng = np.random.default_rng(STREAM_SEED)
        stream = iid_categorical_stream(
            np.full(ALPHABET_SIZE, 1.0 / ALPHABET_SIZE),
            n=N_STEPS, rng=rng,
        )
        c = predictive_logloss_proxy(stream, alphabet_size=ALPHABET_SIZE)
        assert c < 0.02

    def test_proxy_near_one_on_constant_stream(self):
        """Ĉ near 1 for a constant stream (perfectly predictable)."""
        stream = np.zeros(N_STEPS, dtype=np.int64)
        c = predictive_logloss_proxy(stream, alphabet_size=ALPHABET_SIZE)
        assert c > 0.99

    def test_proxy_ordering(self, labeled_stream_and_labels):
        """Ĉ(uniform) < Ĉ(labeled) < Ĉ(constant)."""
        labeled, _ = labeled_stream_and_labels
        rng = np.random.default_rng(STREAM_SEED)
        uniform = iid_categorical_stream(
            np.full(ALPHABET_SIZE, 1.0 / ALPHABET_SIZE),
            n=N_STEPS, rng=rng,
        )
        constant = np.zeros(N_STEPS, dtype=np.int64)
        c_u = predictive_logloss_proxy(uniform, alphabet_size=ALPHABET_SIZE)
        c_l = predictive_logloss_proxy(labeled, alphabet_size=ALPHABET_SIZE)
        c_c = predictive_logloss_proxy(constant, alphabet_size=ALPHABET_SIZE)
        assert c_u < c_l < c_c

    def test_proxy_bounded_in_unit_interval(self, labeled_stream_and_labels):
        stream, _ = labeled_stream_and_labels
        c = predictive_logloss_proxy(stream, alphabet_size=ALPHABET_SIZE)
        assert 0.0 <= c <= 1.0

    def test_proxy_rejects_too_short_stream(self):
        with pytest.raises(ValueError, match="length >= 2"):
            predictive_logloss_proxy(np.array([0]), alphabet_size=3)


# ---------------------------------------------------------------------------
# Labeled synthetic stream
# ---------------------------------------------------------------------------


class TestLabeledCoherenceStream:
    def test_labels_match_alphabet_structure(self, labeled_stream_and_labels):
        _, labels = labeled_stream_and_labels
        assert labels["coherence_bearing"] == list(range(N_COHERENT))
        assert labels["noise"] == list(range(N_COHERENT, ALPHABET_SIZE))

    def test_structural_signal_above_baseline(self, labeled_stream_and_labels):
        """Self-transition rate substantially exceeds the uniform baseline."""
        stream, _ = labeled_stream_and_labels
        self_trans = float((stream[1:] == stream[:-1]).mean())
        baseline = 1.0 / ALPHABET_SIZE
        assert self_trans > 2.0 * baseline

    def test_alphabet_completeness(self, labeled_stream_and_labels):
        stream, _ = labeled_stream_and_labels
        assert set(np.unique(stream).tolist()) == set(range(ALPHABET_SIZE))

    @pytest.mark.parametrize(
        "bad_kwargs, msg",
        [
            ({"n_steps": 0}, "n_steps"),
            ({"n_coherent": 1}, "n_coherent"),
            ({"n_noise": 0}, "n_noise"),
            ({"self_transition_prob": -0.1}, "self_transition_prob"),
            ({"self_transition_prob": 1.1}, "self_transition_prob"),
            ({"noise_injection_prob": -0.1}, "noise_injection_prob"),
            ({"noise_injection_prob": 1.1}, "noise_injection_prob"),
        ],
    )
    def test_validation_errors(self, bad_kwargs, msg):
        defaults = dict(n_steps=100, n_coherent=2, n_noise=2)
        defaults.update(bad_kwargs)
        with pytest.raises(ValueError, match=msg):
            labeled_coherence_stream(**defaults)


# ---------------------------------------------------------------------------
# Leave-one-out ablation (operator A₁, replace-with-uniform)
# ---------------------------------------------------------------------------


class TestLeaveOneOutAblation:
    def test_canonical_signs(self, labeled_stream_and_labels):
        """ρ > 0 for coherence-bearing symbols, ρ < 0 for noise symbols."""
        stream, labels = labeled_stream_and_labels
        result = leave_one_out_ablation(
            stream,
            alphabet_size=ALPHABET_SIZE,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        for x in labels["coherence_bearing"]:
            assert result["rho"][x] > 0, f"rho({x}) should be > 0"
        for x in labels["noise"]:
            assert result["rho"][x] < 0, f"rho({x}) should be < 0"

    def test_separation_invariant(self, labeled_stream_and_labels):
        """min rho(coherent) strictly > max rho(noise)."""
        stream, labels = labeled_stream_and_labels
        result = leave_one_out_ablation(
            stream,
            alphabet_size=ALPHABET_SIZE,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        rho_coh = [result["rho"][x] for x in labels["coherence_bearing"]]
        rho_noi = [result["rho"][x] for x in labels["noise"]]
        assert min(rho_coh) > max(rho_noi)

    def test_baseline_matches_direct_proxy_call(self, labeled_stream_and_labels):
        stream, _ = labeled_stream_and_labels
        result = leave_one_out_ablation(
            stream,
            alphabet_size=ALPHABET_SIZE,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        direct = predictive_logloss_proxy(stream, alphabet_size=ALPHABET_SIZE)
        assert result["c_baseline"] == pytest.approx(direct, abs=1e-12)

    def test_default_symbols_are_unique_observed(self, labeled_stream_and_labels):
        stream, _ = labeled_stream_and_labels
        result = leave_one_out_ablation(
            stream,
            alphabet_size=ALPHABET_SIZE,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        assert result["symbols"] == sorted(int(x) for x in np.unique(stream))

    def test_missing_symbol_gives_zero_rho(self):
        """Ablating a symbol that never appears is a no-op (rho == 0)."""
        stream = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.int64)
        result = leave_one_out_ablation(
            stream,
            symbols_to_ablate=[4],
            alphabet_size=5,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        assert result["rho"][4] == 0.0
        assert result["c_ablated"][4] == result["c_baseline"]


# ---------------------------------------------------------------------------
# Full induction pipeline (induce_weights)
# ---------------------------------------------------------------------------


class TestInduceWeights:
    def test_separates_classes_around_half(self, labeled_stream_and_labels):
        """w(coherent) > 0.5, w(noise) < 0.5."""
        stream, labels = labeled_stream_and_labels
        result = induce_weights(
            stream,
            alphabet_size=ALPHABET_SIZE,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        for x in labels["coherence_bearing"]:
            assert result["w"][x] > 0.5
        for x in labels["noise"]:
            assert result["w"][x] < 0.5

    def test_strict_separation(self, labeled_stream_and_labels):
        stream, labels = labeled_stream_and_labels
        result = induce_weights(
            stream,
            alphabet_size=ALPHABET_SIZE,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        w_coh = [result["w"][x] for x in labels["coherence_bearing"]]
        w_noi = [result["w"][x] for x in labels["noise"]]
        assert min(w_coh) > max(w_noi)

    def test_default_beta_is_locked_value(self, labeled_stream_and_labels):
        """Default beta must be 4.0 per pre_registration.md."""
        stream, _ = labeled_stream_and_labels
        result = induce_weights(
            stream,
            alphabet_size=ALPHABET_SIZE,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        assert result["beta"] == 4.0

    def test_custom_beta_recorded(self, labeled_stream_and_labels):
        stream, _ = labeled_stream_and_labels
        result = induce_weights(
            stream,
            alphabet_size=ALPHABET_SIZE,
            beta=8.0,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        assert result["beta"] == 8.0

    def test_returns_all_diagnostic_keys(self, labeled_stream_and_labels):
        stream, _ = labeled_stream_and_labels
        result = induce_weights(
            stream,
            alphabet_size=ALPHABET_SIZE,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        for key in ("w", "rho", "c_baseline", "c_ablated", "symbols", "beta"):
            assert key in result

    def test_weights_bounded_in_unit_interval(self, labeled_stream_and_labels):
        stream, _ = labeled_stream_and_labels
        result = induce_weights(
            stream,
            alphabet_size=ALPHABET_SIZE,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        for w_x in result["w"].values():
            assert 0.0 <= w_x <= 1.0

    def test_uniform_iid_gives_near_half_weights(self):
        """No temporal structure: rho near 0 and w near 0.5 across symbols."""
        rng = np.random.default_rng(STREAM_SEED)
        stream = iid_categorical_stream(
            np.full(ALPHABET_SIZE, 1.0 / ALPHABET_SIZE),
            n=N_STEPS, rng=rng,
        )
        result = induce_weights(
            stream,
            alphabet_size=ALPHABET_SIZE,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        for w_x in result["w"].values():
            assert abs(w_x - 0.5) < 0.2

    def test_reproducibility_under_fixed_seeds(self, labeled_stream_and_labels):
        stream, _ = labeled_stream_and_labels
        r1 = induce_weights(
            stream,
            alphabet_size=ALPHABET_SIZE,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        r2 = induce_weights(
            stream,
            alphabet_size=ALPHABET_SIZE,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        for x in r1["w"]:
            assert r1["w"][x] == r2["w"][x]

    def test_rejects_invalid_beta(self, labeled_stream_and_labels):
        stream, _ = labeled_stream_and_labels
        with pytest.raises(ValueError, match="beta"):
            induce_weights(
                stream,
                alphabet_size=ALPHABET_SIZE,
                beta=float("nan"),
                rng=np.random.default_rng(ABLATION_SEED),
            )

    def test_rejects_too_short_stream(self):
        with pytest.raises(ValueError, match="length >= 2"):
            induce_weights(np.array([0]), alphabet_size=3)
