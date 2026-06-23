"""Structure tests for the D1 HSMM substrate (v0.7.0 slice 1).

Verifies the LOCKED structural invariants of `cit.data.hsmm_d1` -- the seed-stable
claims of the v0.7.0 pre-registration, NOT a cherry-pickable point tuple. Two of the
four properties (A regime, C coalition) are set by a single random structure draw per
seed, so their recoverable MI is seed-variable (recorded honestly in the pre-reg
amendment). What IS locked and robust on every seed:

  * determinism (bit-exact per seed);
  * distractor flatness measured MARGINAL-RELATIVE despite skewed marginals
    (the load-bearing lock -- the precise failure D1 exists to catch);
  * class separation (every coherence property MI >> every distractor's structural MI);
  * no single property dominates: max single-property share < 0.40 (Sec 5.4 ceiling);
  * the two stable properties (B long-range, D drift) track their calibration values;
  * each property's defining structural signature (A regime / B long-range / C synergy /
    D persistence).

MI is the plug-in (empirical) estimator -- inherently marginal-relative -- matching the
calibration. Fast tests share a module-scoped 3-seed sample at the locked T; the full
20-replicate ensemble is a `slow` test.
"""

import numpy as np
import pytest

from cit.data.hsmm_d1 import (
    generate_stream,
    ALPHABET as A,
    B_LAG as L,
    T_DEFAULT,
    N_REPLICATES,
    REPLICATE_SEEDS,
    COHERENCE_BEARING,
    NOISE,
    FEATURE_PROPERTY,
    N_FEATURES,
    N_STATES,
)

# --- locked structural thresholds (seed-stable; margins from the 20-replicate sweep) ---
SHARE_CEIL = 0.40          # Sec 5.4: no single property dominates
DISTRACTOR_CEIL = 0.01     # distractor structural MI floor (measured ~0.001)
PROPERTY_FLOOR = 0.10      # every coherence property recoverable above this (min measured 0.143)
SEPARATION_FACTOR = 10.0   # property MI / max distractor structural MI (measured ~200x)
I_B_BAND = (0.40, 0.52)    # stable (measured 0.455-0.476)
I_D_BAND = (0.48, 0.66)    # stable (measured 0.527-0.627)

FAST_SEEDS = REPLICATE_SEEDS[:3]


def _mi(x, y):
    """Plug-in mutual information I(x;y) in bits (marginal-relative by construction)."""
    x = np.asarray(x); y = np.asarray(y)
    Kx, Ky = int(x.max()) + 1, int(y.max()) + 1
    j = np.zeros((Kx, Ky))
    np.add.at(j, (x, y), 1)
    j /= j.sum()
    px = j.sum(1, keepdims=True)
    py = j.sum(0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        terms = j * (np.log2(j) - np.log2(px) - np.log2(py))
    return float(np.nansum(terms[j > 0]))


def _entropy(x):
    x = np.asarray(x)
    counts = np.bincount(x, minlength=int(x.max()) + 1).astype(float)
    p = counts / counts.sum()
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def _properties(states, obs):
    """The four properties' recoverable marginal-relative MI (calibration diagnostics)."""
    I_A = _mi(obs[:, 0], states)
    key = (obs[:-L, 0] * A + obs[:-L, 2]) * A + obs[:-L, 4]
    I_B = _mi(obs[L:, 1], key)
    f23 = obs[:, 2] * A + obs[:, 3]
    I_C = _mi(f23, states) - _mi(obs[:, 2], states) - _mi(obs[:, 3], states)
    I_D = _mi(obs[1:, 4], obs[:-1, 4])
    return dict(A=I_A, B=I_B, C=I_C, D=I_D)


def _distractor_structural_mi(states, obs):
    """Max over distractors of max(regime MI, lag-1 local MI) -- the structural channels."""
    out = {}
    for j in NOISE:
        out[j] = max(_mi(obs[:, j], states), _mi(obs[1:, j], obs[:-1, j]))
    return out


@pytest.fixture(scope="module")
def streams():
    """Three locked replicate streams at the locked T (generated once, reused)."""
    return [(seed, *generate_stream(seed)) for seed in FAST_SEEDS]


# --------------------------------------------------------------------------- #
# generator mechanics (cheap -- small T)                                       #
# --------------------------------------------------------------------------- #

def test_shapes_and_ranges():
    states, obs = generate_stream(REPLICATE_SEEDS[0], T=2000)
    assert states.shape == (2000,)
    assert obs.shape == (2000, N_FEATURES)
    assert states.dtype == np.int64 and obs.dtype == np.int64
    assert states.min() >= 0 and states.max() < N_STATES
    assert obs.min() >= 0 and obs.max() < A
    # HSMM regime path visits all states and actually dwells (not i.i.d. labels)
    assert set(np.unique(states)) == set(range(N_STATES))
    runs = np.diff(np.flatnonzero(np.diff(states) != 0))
    assert runs.mean() > 50  # mean dwell ~200; well above a memoryless label process


def test_determinism_bit_exact():
    s1, o1 = generate_stream(REPLICATE_SEEDS[0], T=3000)
    s2, o2 = generate_stream(REPLICATE_SEEDS[0], T=3000)
    assert np.array_equal(s1, s2) and np.array_equal(o1, o2)
    # distinct seeds give distinct streams
    s3, o3 = generate_stream(REPLICATE_SEEDS[1], T=3000)
    assert not np.array_equal(o1, o3)


def test_m5_partition_is_exact_and_total():
    assert set(COHERENCE_BEARING) == {0, 1, 2, 3, 4}
    assert set(NOISE) == {5, 6, 7}
    assert set(COHERENCE_BEARING).isdisjoint(NOISE)
    assert set(COHERENCE_BEARING) | set(NOISE) == set(range(N_FEATURES))
    # the partition agrees with the per-feature property labels
    assert all(FEATURE_PROPERTY[j] is not None for j in COHERENCE_BEARING)
    assert all(FEATURE_PROPERTY[j] is None for j in NOISE)


# --------------------------------------------------------------------------- #
# the load-bearing lock: marginal-relative distractor flatness                 #
# --------------------------------------------------------------------------- #

def test_distractor_marginals_are_skewed():
    """The flatness claim is non-trivial only because the distractor marginals ARE skewed."""
    _, states, obs = (REPLICATE_SEEDS[0], *generate_stream(REPLICATE_SEEDS[0]))
    h5, h6, h7 = _entropy(obs[:, 5]), _entropy(obs[:, 6]), _entropy(obs[:, 7])
    uniform = np.log2(A)  # 3.0 bits
    assert h5 > uniform - 0.05          # f5 uniform
    assert h6 < uniform - 0.10          # f6 Zipf: skewed below uniform
    assert h7 < uniform - 0.40          # f7 low-frequency: strongly skewed


def test_distractor_flatness_marginal_relative(streams):
    """Every distractor carries ~0 structural coherence on every seed, despite skew."""
    for seed, states, obs in streams:
        dmax = _distractor_structural_mi(states, obs)
        for j, mi in dmax.items():
            assert mi < DISTRACTOR_CEIL, f"seed {seed} f{j} structural MI {mi:.4f}"


# --------------------------------------------------------------------------- #
# class separation + no domination (the shared signal driving R2)              #
# --------------------------------------------------------------------------- #

def test_class_separation(streams):
    """Every coherence property ranks far above every distractor on every seed."""
    for seed, states, obs in streams:
        props = _properties(states, obs)
        dmax = max(_distractor_structural_mi(states, obs).values())
        for name, mi in props.items():
            assert mi > PROPERTY_FLOOR, f"seed {seed} property {name} MI {mi:.3f}"
            assert mi > SEPARATION_FACTOR * dmax, (
                f"seed {seed} property {name} ({mi:.3f}) not >> distractor ({dmax:.4f})"
            )


def test_no_single_property_dominates(streams):
    """Sec 5.4 ceiling: the largest property carries < 40% of the recoverable MI."""
    for seed, states, obs in streams:
        props = _properties(states, obs)
        share = max(props.values()) / sum(props.values())
        assert share < SHARE_CEIL, f"seed {seed} max-share {share:.3f}"


# --------------------------------------------------------------------------- #
# each property's defining structural signature                                #
# --------------------------------------------------------------------------- #

def test_property_A_regime(streams):
    for seed, states, obs in streams:
        assert _mi(obs[:, 0], states) > PROPERTY_FLOOR


def test_property_B_is_genuinely_long_range(streams):
    """f1 couples to (f0,f2,f4) at lag L, not at lag 0."""
    for seed, states, obs in streams:
        key_lag = (obs[:-L, 0] * A + obs[:-L, 2]) * A + obs[:-L, 4]
        mi_lag = _mi(obs[L:, 1], key_lag)
        key_same = (obs[:, 0] * A + obs[:, 2]) * A + obs[:, 4]
        mi_same = _mi(obs[:, 1], key_same)
        assert mi_lag > 0.20, f"seed {seed} lag-L MI {mi_lag:.3f}"
        assert mi_lag > 3.0 * mi_same, f"seed {seed} lag-L {mi_lag:.3f} vs lag-0 {mi_same:.3f}"


def test_property_C_is_coalitional(streams):
    """f2,f3 individually uninformative about the regime; jointly informative (synergy)."""
    for seed, states, obs in streams:
        mi2 = _mi(obs[:, 2], states)
        mi3 = _mi(obs[:, 3], states)
        mi_joint = _mi(obs[:, 2] * A + obs[:, 3], states)
        assert mi2 < 0.05 and mi3 < 0.05, f"seed {seed} individual leak {mi2:.3f}/{mi3:.3f}"
        assert mi_joint > 0.10, f"seed {seed} joint MI {mi_joint:.3f}"


def test_property_D_persists(streams):
    """Drift carrier: lag-1 temporal persistence."""
    for seed, states, obs in streams:
        assert _mi(obs[1:, 4], obs[:-1, 4]) > 0.30


def test_stable_properties_in_band(streams):
    """B and D are seed-stable and track their calibration values."""
    for seed, states, obs in streams:
        props = _properties(states, obs)
        assert I_B_BAND[0] <= props["B"] <= I_B_BAND[1], f"seed {seed} I_B {props['B']:.3f}"
        assert I_D_BAND[0] <= props["D"] <= I_D_BAND[1], f"seed {seed} I_D {props['D']:.3f}"


# --------------------------------------------------------------------------- #
# full locked ensemble (slow -- generates all 20 replicates)                   #
# --------------------------------------------------------------------------- #

@pytest.mark.slow
def test_full_replicate_ensemble():
    """All 20 locked seeds: per-seed invariants hold; ensemble means in recorded bands."""
    per = {k: [] for k in "ABCD"}
    for seed in REPLICATE_SEEDS:
        states, obs = generate_stream(seed)
        props = _properties(states, obs)
        dmax = max(_distractor_structural_mi(states, obs).values())
        # per-seed invariants on every replicate
        assert max(props.values()) / sum(props.values()) < SHARE_CEIL
        assert dmax < DISTRACTOR_CEIL
        for name, mi in props.items():
            assert mi > PROPERTY_FLOOR and mi > SEPARATION_FACTOR * dmax
        for k in "ABCD":
            per[k].append(props[k])
    means = {k: float(np.mean(v)) for k, v in per.items()}
    # recorded across-replicate distribution (honest bands around the measured means)
    assert 0.45 <= means["A"] <= 0.70, means
    assert 0.44 <= means["B"] <= 0.49, means
    assert 0.36 <= means["C"] <= 0.58, means
    assert 0.55 <= means["D"] <= 0.62, means
    assert len(REPLICATE_SEEDS) == N_REPLICATES
