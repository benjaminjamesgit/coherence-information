"""v0.7.1 R1 (persistence) on D1 -- structure + calibration tests.

Validates the R1 apparatus against D1's full-transparency ground truth (the locked
generator). The load-bearing checks: the sibling generator reproduces the locked
stream BIT-EXACTLY; the perturbation is RNG-preserving (states + non-target features
unchanged); the validation gate (distractors ~0, f0/A above them); the documented
nulls (f2/f5); determinism. Fast tier (reduced T); the full-T x 20-seed grid is a
gated driver run.
"""

import numpy as np
import pytest

from cit.data.hsmm_d1 import generate_stream, N_FEATURES, ALPHABET, NOISE
from cit import persistence_d1 as r1


# --- bit-exact sibling generator -------------------------------------------
@pytest.mark.parametrize("seed", [7000, 7001, 7005])
def test_sibling_reproduces_locked_stream_bit_exact(seed):
    T = 2000
    _, obs_locked = generate_stream(seed, T)
    states, obs, P = r1.stream_with_emission_dists(seed, T)
    assert np.array_equal(obs, obs_locked), "sibling obs must equal generate_stream obs exactly"
    # P is a valid set of categorical distributions
    sums = P.sum(axis=2)
    assert np.allclose(sums, 1.0, atol=1e-9), "every per-step emission row must normalize to 1"
    assert (P >= 0.0).all()


def test_sibling_states_match_locked():
    T = 2000
    states_locked, _ = generate_stream(7000, T)
    states, _, _ = r1.stream_with_emission_dists(7000, T)
    assert np.array_equal(states, states_locked)


# --- generative perturbation: RNG-preserving, single feature ----------------
def test_perturbation_is_rng_preserving():
    T, onset, feat = 2000, 1000, 0
    states_b, obs_b = generate_stream(7000, T)
    states_p, obs_p = r1.generate_perturbed_stream(7000, feat, alpha=0.3, onset=onset, T=T)
    # states bit-identical
    assert np.array_equal(states_p, states_b)
    # every NON-target feature bit-identical
    for f in range(N_FEATURES):
        if f == feat:
            continue
        assert np.array_equal(obs_p[:, f], obs_b[:, f]), f"non-target feature {f} must be unchanged"
    # target feature unchanged before onset
    assert np.array_equal(obs_p[:onset, feat], obs_b[:onset, feat])


def test_perturbation_corrupts_target_after_onset():
    T, onset, feat = 4000, 2000, 0
    _, obs_b = generate_stream(7000, T)
    _, obs_p = r1.generate_perturbed_stream(7000, feat, alpha=0.3, onset=onset, T=T)
    changed = np.mean(obs_p[onset:, feat] != obs_b[onset:, feat])
    # convex-uniform mix at alpha=0.3 changes ~ alpha * (A-1)/A of post-onset steps
    assert 0.15 < changed < 0.40, f"post-onset change fraction {changed:.3f} off expected ~0.26"


def test_perturbation_deterministic():
    T, onset, feat = 2000, 1000, 4
    _, a = r1.generate_perturbed_stream(7000, feat, alpha=0.3, onset=onset, T=T)
    _, b = r1.generate_perturbed_stream(7000, feat, alpha=0.3, onset=onset, T=T)
    assert np.array_equal(a, b)


# --- the measure: documented nulls + determinism ----------------------------
def test_cost_table_deterministic():
    a = r1.persistence_cost_table(seeds=(7000, 7001), T=2000, onset=1000)
    b = r1.persistence_cost_table(seeds=(7000, 7001), T=2000, onset=1000)
    assert np.array_equal(a, b)


def test_uniform_features_are_documented_nulls():
    # f2 (C, uniform marginal) and f5 (uniform distractor) carry no per-feature
    # emission structure -> corrupting them costs ~0.
    cost = r1.persistence_cost_table(seeds=(7000, 7001, 7002), T=6000, onset=3000)
    mean_cost = cost.mean(axis=0)
    assert abs(mean_cost[2]) < 0.05, f"f2 (uniform C member) cost {mean_cost[2]:.4f} not ~0"
    assert abs(mean_cost[5]) < 0.05, f"f5 (uniform distractor) cost {mean_cost[5]:.4f} not ~0"


# --- the validation gate (calibration deliverable) --------------------------
def test_validation_gate_distractors_zero_and_A_present():
    cost = r1.persistence_cost_table(seeds=(7000, 7001, 7002), T=6000, onset=3000)
    gate = r1.validation_gate(cost)
    # (a) marginal-relative correctness: the skewed-marginal distractors stay ~0
    assert gate["distractors_near_zero"], f"distractor_max {gate['distractor_max']:.4f} not ~0"
    # (b) f0 (A, the direct regime cue) carries cost above every distractor
    assert gate["A_above_distractors"], (
        f"f0/A cost {gate['f0_A_cost']:.4f} not above distractor_max {gate['distractor_max']:.4f}"
    )
    assert gate["ok"]


# --- Cohen's d helper -------------------------------------------------------
def test_cohens_d_sign_and_zero():
    rng = np.random.default_rng(0)
    high = rng.normal(1.0, 1.0, size=200)
    low = rng.normal(0.0, 1.0, size=200)
    d = r1.cohens_d(high, low)
    assert 0.7 < d < 1.3, f"Cohen's d {d:.3f} off expected ~1.0"
    assert r1.cohens_d([1.0], [0.0]) == 0.0  # degenerate -> 0
    assert r1.cohens_d(np.ones(5), np.ones(5)) == 0.0  # zero variance -> 0
