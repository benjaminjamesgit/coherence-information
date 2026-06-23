"""Tests for the decoupling-control crossing proxies (v0.7.0 pre-reg 2026-06-23).

K3b / K2b apply a MODELING functional to the IDENTICAL byte-stream encoding + time-shuffle
surrogate baseline that K1/K5 use (cit.proxies.crossing). These lock: (a) they consume K1's
EXACT byte representation; (b) the contract + determinism; (c) the marginal-relative property
(the load-bearing lock -- a skewed-but-iid feature scores ~0, temporal structure scores > 0);
(d) the pre-reg audit criterion -- recover the A/D structure single-feature tests already prove
present -- via the A1 LOO column on D1. K3b's recovery is the one slow test (the GRU is heavy);
the full-T x 20-seed control run is a separate CI/very_slow artifact.
"""

import numpy as np
import pytest

from cit.proxies.crossing import (
    bigram_mdl_byte_proxy as K2b,
    neural_prequential_byte_proxy as K3b,
    _byte_stream,
)
from cit.proxies.categorical import _encode_bits_cat
from cit.data.hsmm_d1 import generate_stream
from cit.ablations.categorical import leave_one_out_ablation_cat
from cit.induce_cat import induce_weights_cat
from cit.metacoherence import recovered_properties

_LOO_SEED = 123


def _col(x):
    return np.asarray(x, dtype=np.int64).reshape(-1, 1)


def _streams(T, seed=42):
    """Single-feature (T, 1) streams: iid-uniform, skewed-iid, sticky (temporal structure)."""
    rng = np.random.default_rng(seed)
    uniform = _col(rng.integers(0, 8, T))
    p = np.array([0.5, 0.2, 0.1, 0.08, 0.05, 0.04, 0.02, 0.01])
    skewed = _col(rng.choice(8, T, p=p))
    s = np.empty(T, dtype=np.int64)
    s[0] = rng.integers(0, 8)
    for t in range(1, T):
        s[t] = s[t - 1] if rng.random() < 0.9 else rng.integers(0, 8)
    return uniform, skewed, _col(s)


def test_byte_stream_is_k1_representation():
    """The crossing proxies consume K1's EXACT bytes: packbits of the feature-major encoding."""
    arr = np.random.default_rng(0).integers(0, 8, (300, 8))
    assert _byte_stream(arr, 8).tobytes() == np.packbits(_encode_bits_cat(arr, 8)).tobytes()


def test_k2b_contract_and_determinism():
    _, _, sticky = _streams(1500)
    c = K2b(sticky, alphabet=8)
    assert 0.0 <= c <= 1.0
    assert K2b(sticky, alphabet=8) == c                      # deterministic (no RNG)
    assert K2b(sticky, n_features=1, alphabet=8) == c        # n_features path agrees
    assert K2b(sticky) == c                                  # alphabet inferred (max+1 == 8)


def test_k3b_contract_and_determinism():
    _, _, sticky = _streams(250)
    c = K3b(sticky, alphabet=8)
    assert 0.0 <= c <= 1.0
    assert K3b(sticky, alphabet=8) == c                      # deterministic (NEURAL_SEED=7)


def test_k2b_marginal_relative():
    """The lock: a skewed-but-iid feature scores ~0 (surrogate preserves its marginal);
    temporal structure scores clearly above zero."""
    uniform, skewed, sticky = _streams(1500)
    c_u, c_s, c_st = (K2b(x, alphabet=8) for x in (uniform, skewed, sticky))
    assert c_u < 0.05                                        # iid-uniform -> ~0
    assert c_s < 0.05                                        # skewed marginal, iid in time -> ~0
    assert c_st > 0.15                                       # temporal structure -> > 0
    assert c_st > c_u + 0.10 and c_st > c_s + 0.10


def test_k3b_marginal_relative():
    """Same lock for the GRU crossing, at tiny T (the GRU barely trains, so assert ordering)."""
    uniform, skewed, sticky = _streams(250)
    c_u, c_s, c_st = (K3b(x, alphabet=8) for x in (uniform, skewed, sticky))
    assert c_u < 0.01                                        # iid-uniform -> ~0
    assert c_st > 0.005                                      # temporal structure -> positive
    assert c_st > c_u and c_st > c_s                         # structure ranks above both noises


def test_k2b_recovers_A_and_D_on_d1():
    """Audit criterion (K2b, fast): the A1 LOO column on D1 recovers A and D above distractors."""
    obs = generate_stream(7000)[1][:4000]
    res = induce_weights_cat(obs, 8, proxy=K2b, ablation=leave_one_out_ablation_cat,
                             rng=np.random.default_rng(_LOO_SEED))
    w = res["w"]
    assert set(w) == set(range(8)) and all(0.0 < v < 1.0 for v in w.values())
    assert min(w[0], w[4]) > max(w[5], w[6], w[7])           # A (f0) and D (f4) above every distractor
    assert {"A", "D"} <= recovered_properties(w)


@pytest.mark.slow
def test_k3b_recovers_property_A_on_d1():
    """Audit criterion (K3b, slow -- the GRU is heavy): the A1 LOO column on D1 recovers A,
    the banked cross-decoupled survivor, above every distractor."""
    obs = generate_stream(7000)[1][:1500]
    res = induce_weights_cat(obs, 8, proxy=K3b, ablation=leave_one_out_ablation_cat,
                             rng=np.random.default_rng(_LOO_SEED))
    w = res["w"]
    assert set(w) == set(range(8)) and all(0.0 < v < 1.0 for v in w.values())
    assert "A" in recovered_properties(w)
    assert w[0] > max(w[5], w[6], w[7])                      # property A (f0) above every distractor
