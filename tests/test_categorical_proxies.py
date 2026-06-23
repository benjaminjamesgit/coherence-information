"""Tests for the categorical (alphabet-A) proxy generalizations (v0.7.0 slice 2).

The load-bearing claim: coherence on D1 is measured MARGINAL-RELATIVE, so a feature
whose only structure is a skewed marginal (the Zipf / low-frequency distractors)
scores ~0 -- DESPITE its skew -- where a uniform-baseline proxy would credit the skew
as coherence. Each categorical proxy is checked on real D1 features for:

  * distractor flatness marginal-relative (the lock);
  * the fix vs a uniform baseline (distractor reads high under uniform, ~0 under
    marginal-relative -- the precise failure D1 exists to catch);
  * temporal-shuffle invariance (shuffle a coherence feature's time order -> same
    marginal, structure gone -> C collapses to ~0);
  * proxy-level class separation (best coherence feature >> best distractor);
  * recovery of the property the proxy's family is built to read;
  * determinism, alphabet handling, and input validation.

Single-feature streams isolate each property; the full-stream / cross-feature behavior
and per-feature ablation attribution are exercised in slice 3.
"""

import numpy as np
import pytest

from cit.data.hsmm_d1 import generate_stream, ALPHABET, COHERENCE_BEARING, NOISE, REPLICATE_SEEDS
from cit.proxies.categorical import (
    ngram_mdl_proxy_cat,
    neural_prequential_proxy_cat,
    mdl_hmm_proxy_cat,
    _bigram_nll_bits,
    _marginal_entropy_bits,
)

A = ALPHABET
DISTRACTOR_CEIL = 0.02   # marginal-relative distractor flatness (measured ~0.000)


@pytest.fixture(scope="module")
def d1():
    """Two locked replicate streams (full obs) for cross-seed robustness."""
    return {seed: generate_stream(seed)[1] for seed in REPLICATE_SEEDS[:2]}


def _col(obs, j):
    return obs[:, j][:, None]


def _uniform_baseline_k2(col, alphabet):
    """The OLD-style K2: per-feature bigram vs a UNIFORM baseline (the failure mode)."""
    col = np.asarray(col).ravel()
    T = col.shape[0]
    Lb = _bigram_nll_bits(col[:-1], col[1:], alphabet) + 0.5 * alphabet * (alphabet - 1) * np.log2(T)
    Liid = (T - 1) * np.log2(alphabet)
    return float(np.clip(1.0 - Lb / Liid, 0.0, 1.0))


# --------------------------------------------------------------------------- #
# K2 categorical: per-feature bigram MDL, marginal-relative                    #
# --------------------------------------------------------------------------- #

def test_k2_distractors_flat_marginal_relative(d1):
    for seed, obs in d1.items():
        for j in NOISE:
            c = ngram_mdl_proxy_cat(_col(obs, j), alphabet=A)
            assert c < DISTRACTOR_CEIL, f"seed {seed} f{j} C_K2={c:.4f}"


def test_k2_marginal_relative_beats_uniform_on_skew(d1):
    """The lock: the skewed distractors read high under a uniform baseline, ~0 under
    marginal-relative. f7 (low-freq) under uniform even outranks real coherence features."""
    for seed, obs in d1.items():
        for j in (6, 7):  # Zipf, low-frequency: skewed marginals, no structure
            col = _col(obs, j)
            c_marg = ngram_mdl_proxy_cat(col, alphabet=A)
            c_unif = _uniform_baseline_k2(col, A)
            assert c_unif > 0.10, f"seed {seed} f{j} uniform baseline unexpectedly low {c_unif:.4f}"
            assert c_marg < DISTRACTOR_CEIL
            assert c_marg < 0.1 * c_unif, f"seed {seed} f{j} marg {c_marg:.4f} vs unif {c_unif:.4f}"


def test_k2_recovers_drift(d1):
    """f4 (drift) is lag-1 persistence -- K2's family signal -- and is seed-stable."""
    for seed, obs in d1.items():
        assert ngram_mdl_proxy_cat(_col(obs, 4), alphabet=A) > 0.10


def test_k2_temporal_shuffle_kills_coherence(d1):
    """Shuffle f4 in time: marginal preserved, temporal structure destroyed -> C ~ 0."""
    obs = next(iter(d1.values()))
    col = obs[:, 4]
    assert ngram_mdl_proxy_cat(col[:, None], alphabet=A) > 0.10
    perm = np.random.default_rng(0).permutation(col.shape[0])
    shuffled = col[perm]
    assert ngram_mdl_proxy_cat(shuffled[:, None], alphabet=A) < DISTRACTOR_CEIL


def test_k2_proxy_level_class_separation(d1):
    """Best coherence-bearing feature ranks clearly above the best distractor."""
    for seed, obs in d1.items():
        coh = max(ngram_mdl_proxy_cat(_col(obs, j), alphabet=A) for j in COHERENCE_BEARING)
        dist = max(ngram_mdl_proxy_cat(_col(obs, j), alphabet=A) for j in NOISE)
        assert coh > dist + 0.05, f"seed {seed} coh {coh:.4f} vs dist {dist:.4f}"


def test_k2_short_context_misses_b_and_c(d1):
    """Characterization (expected, not failure): a bigram misses lag-12 B and per-feature
    cannot see the C coalition -- both read ~0 single-feature."""
    obs = next(iter(d1.values()))
    assert ngram_mdl_proxy_cat(_col(obs, 1), alphabet=A) < DISTRACTOR_CEIL   # B: lag-12
    assert ngram_mdl_proxy_cat(_col(obs, 2), alphabet=A) < DISTRACTOR_CEIL   # C: individually uniform
    assert ngram_mdl_proxy_cat(_col(obs, 3), alphabet=A) < DISTRACTOR_CEIL


def test_k2_determinism(d1):
    obs = next(iter(d1.values()))
    assert ngram_mdl_proxy_cat(obs, alphabet=A) == ngram_mdl_proxy_cat(obs, alphabet=A)


def test_k2_alphabet_inference_and_binary():
    """alphabet inferred = explicit; binary (A=2) is a valid special case."""
    rng = np.random.default_rng(1)
    cat = rng.integers(0, A, size=(2000, 3))
    assert ngram_mdl_proxy_cat(cat) == ngram_mdl_proxy_cat(cat, alphabet=A)
    binary = rng.integers(0, 2, size=(2000, 3))
    c = ngram_mdl_proxy_cat(binary, alphabet=2)
    assert 0.0 <= c <= 1.0


def test_k2_validation():
    rng = np.random.default_rng(2)
    with pytest.raises(ValueError):
        ngram_mdl_proxy_cat(rng.integers(0, A, size=10))            # 1-D
    with pytest.raises(ValueError):
        ngram_mdl_proxy_cat(rng.integers(0, A, size=(1, 3)))        # T < 2
    with pytest.raises(ValueError):
        ngram_mdl_proxy_cat(np.full((10, 2), -1))                   # negative
    with pytest.raises(ValueError):
        ngram_mdl_proxy_cat(rng.integers(0, A, size=(10, 2)), alphabet=3)  # alphabet too small


# --------------------------------------------------------------------------- #
# K3 categorical: GRU prequential cross-entropy, marginal-relative (slow tier) #
# --------------------------------------------------------------------------- #

_K3_T = 15000   # representative length; the grid (slice 3) runs the locked T=50_000
_K3_SEED = 7000


@pytest.fixture(scope="module")
def k3_single():
    """Single-feature C_K3 per probed D1 feature at a representative T (seed 7000).

    ~6 GRU runs; only requested by slow tests, so the fast suite never pays for it.
    """
    obs = generate_stream(_K3_SEED)[1][:_K3_T]
    return {j: neural_prequential_proxy_cat(obs[:, j][:, None], alphabet=A) for j in (0, 1, 4, 5, 6, 7)}


@pytest.mark.slow
def test_k3_distractors_flat_marginal_relative(k3_single):
    for j in NOISE:
        assert k3_single[j] < DISTRACTOR_CEIL, f"f{j} C_K3={k3_single[j]:.4f}"


@pytest.mark.slow
def test_k3_marginal_relative_beats_uniform_on_skew(k3_single):
    """Reconstruct the uniform-baseline score from C and H_marginal: the skewed
    distractors read high under uniform, ~0 under marginal-relative."""
    obs = generate_stream(_K3_SEED)[1][:_K3_T]
    for j in (6, 7):
        h_marg = _marginal_entropy_bits(obs[:, j], A)
        h_pred = h_marg * (1.0 - k3_single[j])
        c_unif = float(np.clip(1.0 - h_pred / np.log2(A), 0.0, 1.0))
        assert c_unif > 0.10, f"f{j} uniform baseline {c_unif:.4f}"
        assert k3_single[j] < DISTRACTOR_CEIL


@pytest.mark.slow
def test_k3_recovers_drift_and_regime(k3_single):
    assert k3_single[4] > 0.10   # D: drift
    assert k3_single[0] > 0.03   # A: regime (seed 7000 mid-I_A)


@pytest.mark.slow
def test_k3_proxy_level_class_separation(k3_single):
    coh = max(k3_single[0], k3_single[4])
    dist = max(k3_single[5], k3_single[6], k3_single[7])
    assert coh > dist + 0.05, f"coh {coh:.4f} vs dist {dist:.4f}"


@pytest.mark.slow
def test_k3_single_feature_misses_b(k3_single):
    """Characterization: single-feature f1 carries no self-history of (f0,f2,f4) at lag L,
    so B is invisible here -- full-stream cross-feature B-recovery is a slice-3 question."""
    assert k3_single[1] < DISTRACTOR_CEIL


@pytest.mark.slow
def test_k3_determinism():
    obs = generate_stream(_K3_SEED)[1][:1500]
    assert neural_prequential_proxy_cat(obs, alphabet=A) == neural_prequential_proxy_cat(obs, alphabet=A)


@pytest.mark.slow
def test_k3_alphabet_inference():
    cat = np.random.default_rng(3).integers(0, A, size=(1200, 2))
    assert neural_prequential_proxy_cat(cat) == neural_prequential_proxy_cat(cat, alphabet=A)


def test_k3_validation():
    """Validation raises before any GRU work (fast: no torch run)."""
    rng = np.random.default_rng(4)
    with pytest.raises(ValueError):
        neural_prequential_proxy_cat(rng.integers(0, A, size=10))        # 1-D
    with pytest.raises(ValueError):
        neural_prequential_proxy_cat(np.full((10, 2), -1))              # negative


# --------------------------------------------------------------------------- #
# K4 categorical: factorized-categorical-emission HMM, marginal-relative (slow)#
# --------------------------------------------------------------------------- #

_K4_T = 8000   # representative length; the grid (slice 3) runs the locked T=50_000
_K4_SEED = 7000


@pytest.fixture(scope="module")
def k4_obs():
    return generate_stream(_K4_SEED)[1][:_K4_T]


@pytest.fixture(scope="module")
def k4_single(k4_obs):
    """Single-feature C_K4 per probed D1 feature at a representative T (seed 7000)."""
    return {j: mdl_hmm_proxy_cat(k4_obs[:, j][:, None], alphabet=A) for j in (0, 1, 2, 3, 4, 5, 6, 7)}


@pytest.mark.slow
def test_k4_baseline_is_h1_so_distractors_are_exactly_flat(k4_single):
    """H=1 IS the marginal model; a distractor's best H is 1, so C_K4 = 0 exactly."""
    for j in NOISE:
        assert k4_single[j] < DISTRACTOR_CEIL, f"f{j} C_K4={k4_single[j]:.4f}"


@pytest.mark.slow
def test_k4_marginal_relative_beats_uniform_on_skew(k4_obs, k4_single):
    for j in (6, 7):
        h_marg = _marginal_entropy_bits(k4_obs[:, j], A)
        c_unif = float(np.clip(1.0 - h_marg * (1.0 - k4_single[j]) / np.log2(A), 0.0, 1.0))
        assert c_unif > 0.10, f"f{j} uniform baseline {c_unif:.4f}"
        assert k4_single[j] < DISTRACTOR_CEIL


@pytest.mark.slow
def test_k4_recovers_regime_and_drift(k4_single):
    assert k4_single[0] > 0.10   # A: latent state = regime (K4's strongest recovery)
    assert k4_single[4] > 0.10   # D: discrete states approximate drift modes


@pytest.mark.slow
def test_k4_partially_recovers_coalition_via_shared_latent(k4_obs, k4_single):
    """The shared latent picks up the C coalition jointly, where per-feature proxies cannot:
    f2,f3 score ~0 individually but the (f2,f3) pair clears the distractor ceiling."""
    c_pair = mdl_hmm_proxy_cat(k4_obs[:, [2, 3]], alphabet=A)
    assert k4_single[2] < DISTRACTOR_CEIL and k4_single[3] < DISTRACTOR_CEIL
    assert c_pair > 0.03, f"pair C_K4={c_pair:.4f}"


@pytest.mark.slow
def test_k4_proxy_level_class_separation(k4_single):
    coh = max(k4_single[0], k4_single[4])
    dist = max(k4_single[5], k4_single[6], k4_single[7])
    assert coh > dist + 0.05, f"coh {coh:.4f} vs dist {dist:.4f}"


@pytest.mark.slow
def test_k4_determinism(k4_obs):
    assert mdl_hmm_proxy_cat(k4_obs[:2000], alphabet=A) == mdl_hmm_proxy_cat(k4_obs[:2000], alphabet=A)


def test_k4_validation():
    """Validation raises before any EM work (fast)."""
    rng = np.random.default_rng(5)
    with pytest.raises(ValueError):
        mdl_hmm_proxy_cat(rng.integers(0, A, size=10))         # 1-D
    with pytest.raises(ValueError):
        mdl_hmm_proxy_cat(np.full((10, 2), -1))               # negative
    with pytest.raises(ValueError):
        mdl_hmm_proxy_cat(rng.integers(0, A, size=(10, 2)), alphabet=3)  # alphabet too small
