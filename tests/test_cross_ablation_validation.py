"""Cross-ablation validation: A₁ (LOO) vs A₂ (Shapley).

v0.4 locks the ablation axis of the Metacoherence §3.1 robustness grid.
Two structurally different ablation operators — leave-one-out (A₁,
replace-with-uniform single-symbol removal) and Shapley (A₂, k=64 sampled
coalitions with cohort-mean centering) — must agree on which symbols
carry coherence-bearing structure when applied to the same stream under
the same proxy (form B). Agreement at the rank-correlation level is the
operational form of cross-philosophy convergence at the ablation axis.

Invariants verified
-------------------
1. A₂ canonical signs: ρ > 0 for coherence-bearing, ρ < 0 for noise.
2. A₂ class separation: min ρ(coherent) > max ρ(noise).
3. induce_weights under A₂: w(coherent) > 0.5, w(noise) < 0.5,
   |w − 0.5| < 0.2 (locked invariant from pre_registration.md).
4. Per-symbol sign agreement between A₁ and A₂.
5. Spearman rank correlation of ρ vectors across A₁ and A₂ ≥ 0.7
   (Metacoherence §3.1 R2 threshold, operationalized at the
   ablation axis).

Seeds and stream parameters are reused from v0.2 / v0.3 per
pre_registration.md.
"""

from __future__ import annotations

import numpy as np
import pytest

from cit.ablations.loo import leave_one_out_ablation
from cit.ablations.shapley import shapley_ablation
from cit.data.synthetic import labeled_coherence_stream
from cit.induce import induce_weights

# Locked invariants (pre_registration.md)
STREAM_SEED = 42
ABLATION_SEED = 123
N_STEPS = 20_000
N_COHERENT = 2
N_NOISE = 3
ALPHABET_SIZE = N_COHERENT + N_NOISE
W_BAND = 0.2          # |w − 0.5| < 0.2
R2_THRESHOLD = 0.7    # Spearman ρ ≥ 0.7


def _spearman_corr(x, y):
    """Spearman rank correlation, numpy-only.

    Uses ordinal ranks (np.argsort twice). Adequate for the v0.4 substrate
    where the ρ vectors have no exact ties; for tied data a midrank
    implementation would be required.
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    if x_arr.shape != y_arr.shape or x_arr.ndim != 1:
        raise ValueError("inputs must be 1-D arrays of equal length")
    rx = np.argsort(np.argsort(x_arr)).astype(float)
    ry = np.argsort(np.argsort(y_arr)).astype(float)
    rx -= rx.mean()
    ry -= ry.mean()
    denom = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    if denom == 0.0:
        return 0.0
    return float((rx * ry).sum() / denom)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def labeled_stream():
    """The canonical falsifiability substrate."""
    stream, labels = labeled_coherence_stream(
        n_steps=N_STEPS,
        n_coherent=N_COHERENT,
        n_noise=N_NOISE,
        rng=np.random.default_rng(STREAM_SEED),
    )
    return stream, labels


@pytest.fixture(scope="module")
def rho_a1(labeled_stream):
    """A₁ leave-one-out ρ vector under form B."""
    stream, _ = labeled_stream
    result = leave_one_out_ablation(
        stream,
        alphabet_size=ALPHABET_SIZE,
        rng=np.random.default_rng(ABLATION_SEED),
    )
    return result["rho"]


@pytest.fixture(scope="module")
def rho_a2(labeled_stream):
    """A₂ Shapley ρ vector (centered) under form B."""
    stream, _ = labeled_stream
    result = shapley_ablation(
        stream,
        alphabet_size=ALPHABET_SIZE,
        rng=np.random.default_rng(ABLATION_SEED),
    )
    return result["rho"]


# ---------------------------------------------------------------------------
# A₂ in isolation — canonical signs and class separation
# ---------------------------------------------------------------------------

class TestA2CanonicalSigns:
    def test_rho_positive_for_coherent_symbols(self, rho_a2, labeled_stream):
        _, labels = labeled_stream
        for x in labels["coherence_bearing"]:
            assert rho_a2[x] > 0, (
                f"A₂ ρ({x}) = {rho_a2[x]:+.4f}, expected > 0 (coherent)"
            )

    def test_rho_negative_for_noise_symbols(self, rho_a2, labeled_stream):
        _, labels = labeled_stream
        for x in labels["noise"]:
            assert rho_a2[x] < 0, (
                f"A₂ ρ({x}) = {rho_a2[x]:+.4f}, expected < 0 (noise)"
            )

    def test_strict_class_separation(self, rho_a2, labeled_stream):
        _, labels = labeled_stream
        min_coh = min(rho_a2[x] for x in labels["coherence_bearing"])
        max_noi = max(rho_a2[x] for x in labels["noise"])
        assert min_coh > max_noi, (
            f"A₂ class separation failed: "
            f"min ρ(coherent) = {min_coh:+.4f} !> "
            f"max ρ(noise) = {max_noi:+.4f}"
        )


# ---------------------------------------------------------------------------
# induce_weights under A₂ — the integration test
# ---------------------------------------------------------------------------

class TestInduceWeightsUnderA2:
    @pytest.fixture(scope="class")
    def induced(self, labeled_stream):
        stream, labels = labeled_stream
        result = induce_weights(
            stream,
            alphabet_size=ALPHABET_SIZE,
            ablation=shapley_ablation,
            rng=np.random.default_rng(ABLATION_SEED),
        )
        return result, labels

    def test_coherent_weights_above_half(self, induced):
        result, labels = induced
        for x in labels["coherence_bearing"]:
            assert result["w"][x] > 0.5, (
                f"w({x}) = {result['w'][x]:.3f}, expected > 0.5 (coherent)"
            )

    def test_noise_weights_below_half(self, induced):
        result, labels = induced
        for x in labels["noise"]:
            assert result["w"][x] < 0.5, (
                f"w({x}) = {result['w'][x]:.3f}, expected < 0.5 (noise)"
            )

    def test_weights_within_locked_band(self, induced):
        result, _ = induced
        for x, wx in result["w"].items():
            assert abs(wx - 0.5) < W_BAND, (
                f"|w({x}) − 0.5| = {abs(wx - 0.5):.3f}, "
                f"expected < {W_BAND} (locked invariant)"
            )


# ---------------------------------------------------------------------------
# Cross-ablation convergence — the v0.4 R2 invariant
# ---------------------------------------------------------------------------

class TestCrossAblationConvergence:
    def test_sign_agreement_per_symbol(self, rho_a1, rho_a2):
        for x in sorted(rho_a1.keys()):
            assert np.sign(rho_a1[x]) == np.sign(rho_a2[x]), (
                f"Sign disagreement on symbol {x}: "
                f"A₁ ρ = {rho_a1[x]:+.4f}, A₂ ρ = {rho_a2[x]:+.4f}"
            )

    def test_spearman_rank_correlation_meets_r2_threshold(
        self, rho_a1, rho_a2
    ):
        symbols = sorted(rho_a1.keys())
        v1 = np.array([rho_a1[x] for x in symbols])
        v2 = np.array([rho_a2[x] for x in symbols])
        rho = _spearman_corr(v1, v2)
        assert rho >= R2_THRESHOLD, (
            f"Cross-ablation Spearman ρ(A₁, A₂) = {rho:.3f}, "
            f"expected >= {R2_THRESHOLD} (Metacoherence §3.1 R2)"
        )
