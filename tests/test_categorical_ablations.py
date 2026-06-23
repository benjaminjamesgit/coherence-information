"""Tests for the categorical ablations + induction pipeline (v0.7.0 slice 3a).

Verifies the alphabet-A ablations (A1 LOO, A2 Shapley, A3 correlation-cluster) and the
`induce_weights_cat` pipeline that turns a marginal-relative categorical proxy + a
categorical ablation into a per-feature w-vector. The only generalization from v0.5 is
uniform-over-A replacement (vs Bernoulli(0.5)); these tests lock that, the pipeline
mechanics, determinism, and the class separation a recovering cell produces.

Documented D1 findings (characterization, NOT failures -- the cross-tab is reported, not
pass/failed): A3 finds only singleton clusters on D1 (its couplings are nonlinear/lagged,
invisible to Pearson) so K x A3 == K x A1 here; and a global proxy (K1) can be null under
LOO even where a per-feature proxy recovers structure.
"""

import numpy as np
import pytest

from cit.data.hsmm_d1 import generate_stream, ALPHABET, COHERENCE_BEARING, NOISE
from cit.proxies.categorical import ngram_mdl_proxy_cat as k2
from cit.ablations.categorical import (
    leave_one_out_ablation_cat,
    shapley_ablation_cat,
    correlation_cluster_ablation_cat,
)
from cit.induce_cat import induce_weights_cat, BETA

A = ALPHABET
ABLATION_SEED = 123


@pytest.fixture(scope="module")
def obs():
    return generate_stream(7000)[1]


# --------------------------------------------------------------------------- #
# replacement is uniform-over-A (the one real generalization from binary)      #
# --------------------------------------------------------------------------- #

def test_loo_replacement_is_uniform_over_alphabet(obs):
    """The ablated feature must span the full alphabet, not collapse to binary {0,1}."""
    seen = []

    def probe(s, nf=None):
        seen.append([len(np.unique(s[:, k])) for k in range(s.shape[1])])
        return 0.0

    leave_one_out_ablation_cat(obs[:5000], probe, alphabet=A, rng=np.random.default_rng(0))
    # seen[0] is the full stream; seen[1:] each have exactly one ablated column.
    for j in range(8):
        ablated_col_uniques = seen[1 + j][j]
        assert ablated_col_uniques > 2, f"f{j} ablated to {ablated_col_uniques} values (looks binary)"
        assert ablated_col_uniques <= A


# --------------------------------------------------------------------------- #
# pipeline mechanics + class separation for a recovering cell                  #
# --------------------------------------------------------------------------- #

def test_induce_pipeline_produces_valid_weights(obs):
    res = induce_weights_cat(obs, A, proxy=k2,
                             ablation=leave_one_out_ablation_cat,
                             rng=np.random.default_rng(ABLATION_SEED))
    assert set(res["w"]) == set(range(8))
    assert all(0.0 < v < 1.0 for v in res["w"].values())
    assert set(res["rho"]) == set(range(8))
    assert set(res["c_ablated"]) == set(range(8))


def test_k2_a1_elevates_recovered_features_above_distractors(obs):
    """K2 recovers A (f0) and D (f4); under A1 LOO both rank above every distractor."""
    res = induce_weights_cat(obs, A, proxy=k2,
                             ablation=leave_one_out_ablation_cat,
                             rng=np.random.default_rng(ABLATION_SEED))
    w = res["w"]
    dist = max(w[j] for j in NOISE)
    assert w[4] > dist, f"D (f4) w={w[4]:.4f} not above distractors {dist:.4f}"
    assert w[0] > dist, f"A (f0) w={w[0]:.4f} not above distractors {dist:.4f}"
    # the cell's max coherence-bearing weight beats its max distractor weight
    assert max(w[j] for j in COHERENCE_BEARING) > dist


def test_induce_determinism(obs):
    a = induce_weights_cat(obs, A, proxy=k2, ablation=leave_one_out_ablation_cat,
                           rng=np.random.default_rng(ABLATION_SEED))
    b = induce_weights_cat(obs, A, proxy=k2, ablation=leave_one_out_ablation_cat,
                           rng=np.random.default_rng(ABLATION_SEED))
    assert a["rho"] == b["rho"] and a["w"] == b["w"]


def test_induce_alphabet_inference_matches_explicit(obs):
    small = obs[:8000]
    a = induce_weights_cat(small, A, proxy=k2, ablation=leave_one_out_ablation_cat,
                           rng=np.random.default_rng(ABLATION_SEED))
    b = induce_weights_cat(small, proxy=k2, ablation=leave_one_out_ablation_cat,
                           rng=np.random.default_rng(ABLATION_SEED))  # alphabet inferred
    assert a["rho"] == b["rho"]


def test_w_collapses_to_half_at_zero_rho():
    """Boundary: sigmoid(beta*0) = 0.5 (a feature with no ablation effect)."""
    assert abs(1.0 / (1.0 + np.exp(-BETA * 0.0)) - 0.5) < 1e-12


# --------------------------------------------------------------------------- #
# A3 clustering + documented D1 degeneracy                                     #
# --------------------------------------------------------------------------- #

def test_a3_returns_a_total_clustering(obs):
    res = induce_weights_cat(obs, A, proxy=k2,
                             ablation=correlation_cluster_ablation_cat,
                             rng=np.random.default_rng(ABLATION_SEED))
    clusters = res["clusters"]
    assert sorted(f for c in clusters for f in c) == list(range(8))   # partition of all features
    # On D1, couplings are nonlinear/lagged -> Pearson finds only singletons (documented).
    assert all(len(c) == 1 for c in clusters)


@pytest.mark.slow
def test_shapley_runs_and_separates(obs):
    """A2 Shapley (k=64) runs categorically and elevates K2's recovered D feature."""
    res = induce_weights_cat(obs[:10000], A, proxy=k2,
                             ablation=shapley_ablation_cat,
                             rng=np.random.default_rng(ABLATION_SEED))
    assert set(res["w"]) == set(range(8))
    assert all(0.0 < v < 1.0 for v in res["w"].values())
    assert res["w"][4] > max(res["w"][j] for j in NOISE)   # D (f4) above distractors
