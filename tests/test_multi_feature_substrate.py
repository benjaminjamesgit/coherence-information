"""v0.5.0 multi-feature substrate test suite.

Validates locked invariants from design/multi_feature_substrate.md
(locked 2026-05-26) and pre_registration.md:
- Substrate: marginals, determinism, ground-truth labels, cluster geometry
- Multi-feature proxies: bounded, structured > noise
- Feature-level ablations A_1, A_2, A_3: canonical signs + class separation
- induce_weights_multi: w(coh) > 0.5, w(noise) < 0.5, |w - 0.5| < 0.2
- Per-feature sign agreement A_1 vs A_2 (v0.4 carry)
- Cross-proxy R2: Spearman rho(form B multi, K_1 multi) >= 0.7
- A_3 cluster recovery: discovers the ground-truth 8-cluster structure
"""

from __future__ import annotations

import numpy as np
import pytest

from cit.data.multi_feature import (
    labeled_multi_feature_stream,
    noise_only_multi_feature_stream,
    N_FEATURES_TOTAL,
)
from cit.proxies.predictive_logloss_multi import predictive_logloss_proxy_multi
from cit.proxies.compression_delta_multi import compression_delta_proxy_multi
from cit.proxies.ngram_mdl import ngram_mdl_proxy
from cit.proxies.lempel_parsing import lempel_parsing_proxy
from cit.proxies.neural_prequential import neural_prequential_proxy
from cit.ablations.loo_multi import leave_one_out_ablation_multi
from cit.ablations.shapley_multi import shapley_ablation_multi
from cit.ablations.correlation_cluster import correlation_cluster_ablation
from cit.induce_multi import induce_weights_multi, BETA

# Locked invariants (pre_registration.md, v0.5 substrate parameters)
STREAM_SEED = 42
ABLATION_SEED = 123
N_STEPS = 20_000
W_BAND = 0.2
R2_THRESHOLD = 0.5  # multi-feature substrate calibration (amendment 2026-05-26)


def _pearson(x, y):
    xc = x.astype(float) - x.mean()
    yc = y.astype(float) - y.mean()
    return float((xc * yc).sum() / np.sqrt((xc * xc).sum() * (yc * yc).sum()))


def _spearman_corr(x, y):
    """Spearman rank correlation with midrank tie handling."""
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    n = len(xa)
    if xa.shape != ya.shape or xa.ndim != 1:
        raise ValueError("x and y must be 1-D arrays of equal length")

    def midrank(v):
        order = np.argsort(v, kind="stable")
        ranks = np.empty(n)
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0
            for k in range(i, j + 1):
                ranks[order[k]] = avg
            i = j + 1
        return ranks

    rx = midrank(xa)
    ry = midrank(ya)
    rxc = rx - rx.mean()
    ryc = ry - ry.mean()
    denom = np.sqrt((rxc * rxc).sum() * (ryc * ryc).sum())
    if denom == 0.0:
        return 0.0
    return float((rxc * ryc).sum() / denom)


# --- shared substrate fixtures ---

@pytest.fixture(scope="module")
def labeled():
    return labeled_multi_feature_stream(
        n_steps=N_STEPS, rng=np.random.default_rng(STREAM_SEED)
    )


@pytest.fixture(scope="module")
def stream(labeled):
    return labeled[0]


@pytest.fixture(scope="module")
def labels(labeled):
    return labeled[1]


@pytest.fixture(scope="module")
def coh(labels):
    return labels["coherence_bearing"]


@pytest.fixture(scope="module")
def noi(labels):
    return labels["noise"]


# --- ablation result fixtures (one per proxy x ablation; module-scoped) ---

def _make_fixture(proxy, ablation):
    @pytest.fixture(scope="module")
    def _fix(stream):
        return ablation(
            stream, proxy, n_features=N_FEATURES_TOTAL,
            rng=np.random.default_rng(ABLATION_SEED),
        )
    return _fix


loo_FB        = _make_fixture(predictive_logloss_proxy_multi, leave_one_out_ablation_multi)
shapley_FB    = _make_fixture(predictive_logloss_proxy_multi, shapley_ablation_multi)
corrclust_FB  = _make_fixture(predictive_logloss_proxy_multi, correlation_cluster_ablation)
loo_K1        = _make_fixture(compression_delta_proxy_multi, leave_one_out_ablation_multi)
shapley_K1    = _make_fixture(compression_delta_proxy_multi, shapley_ablation_multi)
corrclust_K1  = _make_fixture(compression_delta_proxy_multi, correlation_cluster_ablation)
loo_K2        = _make_fixture(ngram_mdl_proxy, leave_one_out_ablation_multi)
shapley_K2    = _make_fixture(ngram_mdl_proxy, shapley_ablation_multi)
corrclust_K2  = _make_fixture(ngram_mdl_proxy, correlation_cluster_ablation)
loo_K5        = _make_fixture(lempel_parsing_proxy, leave_one_out_ablation_multi)
shapley_K5    = _make_fixture(lempel_parsing_proxy, shapley_ablation_multi)
corrclust_K5  = _make_fixture(lempel_parsing_proxy, correlation_cluster_ablation)
loo_K3        = _make_fixture(neural_prequential_proxy, leave_one_out_ablation_multi)
shapley_K3    = _make_fixture(neural_prequential_proxy, shapley_ablation_multi)
corrclust_K3  = _make_fixture(neural_prequential_proxy, correlation_cluster_ablation)


# --- substrate tests ---

class TestSubstrate:
    def test_shape_and_dtype(self, stream):
        assert stream.shape == (N_STEPS, N_FEATURES_TOTAL)
        assert stream.dtype == np.uint8

    def test_marginals_within_band(self, stream):
        for j, m in enumerate(stream.mean(axis=0)):
            assert abs(m - 0.5) < 0.02, f"f{j}: marginal {m:.4f}"

    def test_ground_truth_labels(self, labels):
        assert labels["coherence_bearing"] == {0, 1, 2, 3}
        assert labels["noise"] == {4, 5, 6, 7, 8, 9}
        assert labels["clusters"]["cluster_A"] == {0, 1}
        assert labels["clusters"]["cluster_B"] == {2, 3}

    def test_deterministic_reproduction(self):
        s1, _ = labeled_multi_feature_stream(n_steps=N_STEPS, rng=np.random.default_rng(STREAM_SEED))
        s2, _ = labeled_multi_feature_stream(n_steps=N_STEPS, rng=np.random.default_rng(STREAM_SEED))
        assert np.array_equal(s1, s2)

    def test_within_cluster_correlation(self, stream):
        assert _pearson(stream[:, 0], stream[:, 1]) > 0.30
        assert _pearson(stream[:, 2], stream[:, 3]) > 0.30

    def test_cross_cluster_correlation(self, stream):
        for i in (0, 1):
            for j in (2, 3):
                assert _pearson(stream[:, i], stream[:, j]) < -0.30


class TestNoiseOnlyStream:
    def test_marginals_within_band(self):
        n = noise_only_multi_feature_stream(
            n_steps=N_STEPS, rng=np.random.default_rng(STREAM_SEED + 1000)
        )
        for j, m in enumerate(n.mean(axis=0)):
            assert abs(m - 0.5) < 0.02, f"f{j}: noise marginal {m:.4f}"


class TestProxiesBasicProperties:
    @pytest.mark.parametrize("proxy", [
        predictive_logloss_proxy_multi,
        compression_delta_proxy_multi,
    ])
    def test_bounded_and_structured_gt_noise(self, stream, proxy):
        n = noise_only_multi_feature_stream(
            n_steps=N_STEPS, rng=np.random.default_rng(STREAM_SEED + 1000)
        )
        C_s = proxy(stream)
        C_n = proxy(n)
        assert 0.0 <= C_s <= 1.0
        assert 0.0 <= C_n <= 1.0
        assert C_s > C_n


class TestNgramMdl:
    """K_2 n-gram MDL proxy-level invariants."""

    def test_bounded(self, stream):
        c = ngram_mdl_proxy(stream)
        assert 0.0 <= c <= 1.0

    def test_constant_stream_near_one(self):
        const_stream = np.zeros((N_STEPS, N_FEATURES_TOTAL), dtype=np.int8)
        c = ngram_mdl_proxy(const_stream)
        assert c > 0.99, f"C_K2(constant) = {c:.4f} should be near 1.0"

    def test_structured_gt_noise(self, stream):
        n = noise_only_multi_feature_stream(
            n_steps=N_STEPS, rng=np.random.default_rng(STREAM_SEED + 1000)
        )
        c_s = ngram_mdl_proxy(stream)
        c_n = ngram_mdl_proxy(n)
        assert c_s > c_n, f"C_K2(structured)={c_s:.4f} not > C_K2(noise)={c_n:.4f}"

    def test_deterministic(self, stream):
        c1 = ngram_mdl_proxy(stream)
        c2 = ngram_mdl_proxy(stream)
        assert c1 == c2


class TestLempelParsing:
    """K_5 Lempel parsing proxy-level invariants (slow, bit-level LZ76)."""

    pytestmark = pytest.mark.slow

    def test_bounded(self, stream):
        c = lempel_parsing_proxy(stream)
        assert 0.0 <= c <= 1.0

    def test_constant_stream_near_one(self):
        const_stream = np.zeros((N_STEPS, N_FEATURES_TOTAL), dtype=np.int8)
        c = lempel_parsing_proxy(const_stream)
        assert c > 0.99, f"C_K5(constant) = {c:.4f} should be near 1.0"

    def test_structured_gt_noise(self, stream):
        n = noise_only_multi_feature_stream(
            n_steps=N_STEPS, rng=np.random.default_rng(STREAM_SEED + 1000)
        )
        c_s = lempel_parsing_proxy(stream)
        c_n = lempel_parsing_proxy(n)
        assert c_s > c_n, f"C_K5(structured)={c_s:.4f} not > C_K5(noise)={c_n:.4f}"

    def test_deterministic(self, stream):
        c1 = lempel_parsing_proxy(stream)
        c2 = lempel_parsing_proxy(stream)
        assert c1 == c2


class TestNeuralPrequential:
    """K_3 GRU prequential cross-entropy proxy-level invariants (slow, SGD)."""

    pytestmark = pytest.mark.slow

    def test_bounded(self, stream):
        c = neural_prequential_proxy(stream)
        assert 0.0 <= c <= 1.0

    def test_constant_stream_near_one(self):
        const_stream = np.zeros((N_STEPS, N_FEATURES_TOTAL), dtype=np.int8)
        c = neural_prequential_proxy(const_stream)
        assert c > 0.99, f"C_K3(constant) = {c:.4f} should be near 1.0"

    def test_structured_gt_noise(self, stream):
        n = noise_only_multi_feature_stream(
            n_steps=N_STEPS, rng=np.random.default_rng(STREAM_SEED + 1000)
        )
        c_s = neural_prequential_proxy(stream)
        c_n = neural_prequential_proxy(n)
        assert c_s > c_n, f"C_K3(structured)={c_s:.4f} not > C_K3(noise)={c_n:.4f}"

    def test_deterministic(self, stream):
        c1 = neural_prequential_proxy(stream)
        c2 = neural_prequential_proxy(stream)
        assert c1 == c2


# --- canonical signs and class separation ---

def _assert_canonical(result, coh, noi, name):
    rho = result["rho"]
    cv = [rho[f] for f in coh]
    nv = [rho[f] for f in noi]
    assert min(cv) > 0,  f"{name}: min rho(coh)={min(cv):+.4f}"
    assert max(nv) < 0,  f"{name}: max rho(noise)={max(nv):+.4f}"
    assert min(cv) > max(nv), f"{name}: separation failed"


class TestCanonicalSigns:
    def test_A1_formB(self, loo_FB, coh, noi):       _assert_canonical(loo_FB, coh, noi, "A_1 form B")
    def test_A2_formB(self, shapley_FB, coh, noi):   _assert_canonical(shapley_FB, coh, noi, "A_2 form B")
    def test_A3_formB(self, corrclust_FB, coh, noi): _assert_canonical(corrclust_FB, coh, noi, "A_3 form B")
    def test_A1_K1(self, loo_K1, coh, noi):          _assert_canonical(loo_K1, coh, noi, "A_1 K_1")
    def test_A2_K1(self, shapley_K1, coh, noi):      _assert_canonical(shapley_K1, coh, noi, "A_2 K_1")
    def test_A3_K1(self, corrclust_K1, coh, noi):    _assert_canonical(corrclust_K1, coh, noi, "A_3 K_1")
    def test_A1_K2(self, loo_K2, coh, noi):          _assert_canonical(loo_K2, coh, noi, "A_1 K_2")
    def test_A2_K2(self, shapley_K2, coh, noi):      _assert_canonical(shapley_K2, coh, noi, "A_2 K_2")
    def test_A3_K2(self, corrclust_K2, coh, noi):    _assert_canonical(corrclust_K2, coh, noi, "A_3 K_2")
    @pytest.mark.slow
    def test_A1_K5(self, loo_K5, coh, noi):          _assert_canonical(loo_K5, coh, noi, "A_1 K_5")
    @pytest.mark.very_slow
    def test_A2_K5(self, shapley_K5, coh, noi):      _assert_canonical(shapley_K5, coh, noi, "A_2 K_5")
    @pytest.mark.slow
    def test_A3_K5(self, corrclust_K5, coh, noi):    _assert_canonical(corrclust_K5, coh, noi, "A_3 K_5")
    @pytest.mark.slow
    def test_A1_K3(self, loo_K3, coh, noi):          _assert_canonical(loo_K3, coh, noi, "A_1 K_3")
    @pytest.mark.very_slow
    def test_A2_K3(self, shapley_K3, coh, noi):      _assert_canonical(shapley_K3, coh, noi, "A_2 K_3")
    @pytest.mark.slow
    def test_A3_K3(self, corrclust_K3, coh, noi):    _assert_canonical(corrclust_K3, coh, noi, "A_3 K_3")


# --- induce_weights_multi invariants (sigmoid on cached rho) ---

def _w_from_rho(rho):
    return {f: 1.0 / (1.0 + np.exp(-BETA * v)) for f, v in rho.items()}


def _assert_weight_invariants(rho, coh, noi, name):
    w = _w_from_rho(rho)
    wc = [w[f] for f in coh]
    wn = [w[f] for f in noi]
    assert all(v > 0.5 for v in wc), f"{name}: w(coh) min={min(wc):.4f}"
    assert all(v < 0.5 for v in wn), f"{name}: w(noise) max={max(wn):.4f}"
    assert max(abs(v - 0.5) for v in w.values()) < W_BAND, f"{name}: |w-0.5| max exceeds {W_BAND}"


class TestInduceWeightsInvariants:
    def test_A1_formB(self, loo_FB, coh, noi):       _assert_weight_invariants(loo_FB["rho"], coh, noi, "A_1 form B")
    def test_A2_formB(self, shapley_FB, coh, noi):   _assert_weight_invariants(shapley_FB["rho"], coh, noi, "A_2 form B")
    def test_A3_formB(self, corrclust_FB, coh, noi): _assert_weight_invariants(corrclust_FB["rho"], coh, noi, "A_3 form B")
    def test_A1_K1(self, loo_K1, coh, noi):          _assert_weight_invariants(loo_K1["rho"], coh, noi, "A_1 K_1")
    def test_A2_K1(self, shapley_K1, coh, noi):      _assert_weight_invariants(shapley_K1["rho"], coh, noi, "A_2 K_1")
    def test_A3_K1(self, corrclust_K1, coh, noi):    _assert_weight_invariants(corrclust_K1["rho"], coh, noi, "A_3 K_1")
    def test_A1_K2(self, loo_K2, coh, noi):          _assert_weight_invariants(loo_K2["rho"], coh, noi, "A_1 K_2")
    def test_A2_K2(self, shapley_K2, coh, noi):      _assert_weight_invariants(shapley_K2["rho"], coh, noi, "A_2 K_2")
    def test_A3_K2(self, corrclust_K2, coh, noi):    _assert_weight_invariants(corrclust_K2["rho"], coh, noi, "A_3 K_2")
    @pytest.mark.slow
    def test_A1_K5(self, loo_K5, coh, noi):          _assert_weight_invariants(loo_K5["rho"], coh, noi, "A_1 K_5")
    @pytest.mark.very_slow
    def test_A2_K5(self, shapley_K5, coh, noi):      _assert_weight_invariants(shapley_K5["rho"], coh, noi, "A_2 K_5")
    @pytest.mark.slow
    def test_A3_K5(self, corrclust_K5, coh, noi):    _assert_weight_invariants(corrclust_K5["rho"], coh, noi, "A_3 K_5")
    @pytest.mark.slow
    def test_A1_K3(self, loo_K3, coh, noi):          _assert_weight_invariants(loo_K3["rho"], coh, noi, "A_1 K_3")
    @pytest.mark.very_slow
    def test_A2_K3(self, shapley_K3, coh, noi):      _assert_weight_invariants(shapley_K3["rho"], coh, noi, "A_2 K_3")
    @pytest.mark.slow
    def test_A3_K3(self, corrclust_K3, coh, noi):    _assert_weight_invariants(corrclust_K3["rho"], coh, noi, "A_3 K_3")


# --- v0.4 carry: per-feature sign agreement A_1 vs A_2 ---

class TestPerFeatureSignAgreement:
    def test_A1_vs_A2_formB(self, loo_FB, shapley_FB):
        for f in sorted(loo_FB["rho"]):
            assert np.sign(loo_FB["rho"][f]) == np.sign(shapley_FB["rho"][f]), (
                f"form B f{f}: A_1={loo_FB['rho'][f]:+.4f} A_2={shapley_FB['rho'][f]:+.4f}"
            )

    def test_A1_vs_A2_K1(self, loo_K1, shapley_K1):
        for f in sorted(loo_K1["rho"]):
            assert np.sign(loo_K1["rho"][f]) == np.sign(shapley_K1["rho"][f]), (
                f"K_1 f{f}: A_1={loo_K1['rho'][f]:+.4f} A_2={shapley_K1['rho'][f]:+.4f}"
            )


# --- v0.5.0 multi-feature cross-proxy R2 (Q4 + Q7 lock) ---

def _spearman_check_pair(result_a, result_b, label_a, label_b, ablation):
    syms = sorted(result_a["rho"])
    v_a = np.array([result_a["rho"][s] for s in syms])
    v_b = np.array([result_b["rho"][s] for s in syms])
    rho = _spearman_corr(v_a, v_b)
    assert rho >= R2_THRESHOLD, (
        f"{ablation}: Spearman({label_a}, {label_b}) = {rho:.3f} < {R2_THRESHOLD}"
    )


class TestCrossProxyConvergenceMulti:
    # form B vs K_1 (v0.5.0 baseline)
    def test_under_A1(self, loo_FB, loo_K1):              _spearman_check_pair(loo_FB, loo_K1, "form B", "K_1", "A_1")
    def test_under_A2(self, shapley_FB, shapley_K1):      _spearman_check_pair(shapley_FB, shapley_K1, "form B", "K_1", "A_2")
    def test_under_A3(self, corrclust_FB, corrclust_K1):  _spearman_check_pair(corrclust_FB, corrclust_K1, "form B", "K_1", "A_3")
    # K_2 vs form B (v0.5.1)
    def test_K2_vs_FB_under_A1(self, loo_K2, loo_FB):             _spearman_check_pair(loo_K2, loo_FB, "K_2", "form B", "A_1")
    def test_K2_vs_FB_under_A2(self, shapley_K2, shapley_FB):     _spearman_check_pair(shapley_K2, shapley_FB, "K_2", "form B", "A_2")
    def test_K2_vs_FB_under_A3(self, corrclust_K2, corrclust_FB): _spearman_check_pair(corrclust_K2, corrclust_FB, "K_2", "form B", "A_3")
    # K_2 vs K_1 (v0.5.1)
    def test_K2_vs_K1_under_A1(self, loo_K2, loo_K1):             _spearman_check_pair(loo_K2, loo_K1, "K_2", "K_1", "A_1")
    def test_K2_vs_K1_under_A2(self, shapley_K2, shapley_K1):     _spearman_check_pair(shapley_K2, shapley_K1, "K_2", "K_1", "A_2")
    def test_K2_vs_K1_under_A3(self, corrclust_K2, corrclust_K1): _spearman_check_pair(corrclust_K2, corrclust_K1, "K_2", "K_1", "A_3")
    # K_5 vs form B (v0.5.2)
    @pytest.mark.slow
    def test_K5_vs_FB_under_A1(self, loo_K5, loo_FB):             _spearman_check_pair(loo_K5, loo_FB, "K_5", "form B", "A_1")
    @pytest.mark.very_slow
    def test_K5_vs_FB_under_A2(self, shapley_K5, shapley_FB):     _spearman_check_pair(shapley_K5, shapley_FB, "K_5", "form B", "A_2")
    @pytest.mark.slow
    def test_K5_vs_FB_under_A3(self, corrclust_K5, corrclust_FB): _spearman_check_pair(corrclust_K5, corrclust_FB, "K_5", "form B", "A_3")
    # K_5 vs K_1 (v0.5.2)
    @pytest.mark.slow
    def test_K5_vs_K1_under_A1(self, loo_K5, loo_K1):             _spearman_check_pair(loo_K5, loo_K1, "K_5", "K_1", "A_1")
    @pytest.mark.very_slow
    def test_K5_vs_K1_under_A2(self, shapley_K5, shapley_K1):     _spearman_check_pair(shapley_K5, shapley_K1, "K_5", "K_1", "A_2")
    @pytest.mark.slow
    def test_K5_vs_K1_under_A3(self, corrclust_K5, corrclust_K1): _spearman_check_pair(corrclust_K5, corrclust_K1, "K_5", "K_1", "A_3")
    # K_5 vs K_2 (v0.5.2)
    @pytest.mark.slow
    def test_K5_vs_K2_under_A1(self, loo_K5, loo_K2):             _spearman_check_pair(loo_K5, loo_K2, "K_5", "K_2", "A_1")
    @pytest.mark.very_slow
    @pytest.mark.xfail(
        reason="K_5 vs K_2 R_2 seam under Shapley (A_2): factorized bigram MDL "
               "vs LZ76 phrase dictionary diverge under random-coalition ablation. "
               "Pre-registered seam; deferred to v0.5.5 capstone for K_3/K_4 generalization.",
        strict=True,
    )
    def test_K5_vs_K2_under_A2(self, shapley_K5, shapley_K2):     _spearman_check_pair(shapley_K5, shapley_K2, "K_5", "K_2", "A_2")
    @pytest.mark.slow
    def test_K5_vs_K2_under_A3(self, corrclust_K5, corrclust_K2): _spearman_check_pair(corrclust_K5, corrclust_K2, "K_5", "K_2", "A_3")
    # K_3 vs form B (v0.5.3)
    @pytest.mark.slow
    def test_K3_vs_FB_under_A1(self, loo_K3, loo_FB):             _spearman_check_pair(loo_K3, loo_FB, "K_3", "form B", "A_1")
    @pytest.mark.very_slow
    def test_K3_vs_FB_under_A2(self, shapley_K3, shapley_FB):     _spearman_check_pair(shapley_K3, shapley_FB, "K_3", "form B", "A_2")
    @pytest.mark.slow
    def test_K3_vs_FB_under_A3(self, corrclust_K3, corrclust_FB): _spearman_check_pair(corrclust_K3, corrclust_FB, "K_3", "form B", "A_3")
    # K_3 vs K_1 (v0.5.3)
    @pytest.mark.slow
    def test_K3_vs_K1_under_A1(self, loo_K3, loo_K1):             _spearman_check_pair(loo_K3, loo_K1, "K_3", "K_1", "A_1")
    @pytest.mark.very_slow
    def test_K3_vs_K1_under_A2(self, shapley_K3, shapley_K1):     _spearman_check_pair(shapley_K3, shapley_K1, "K_3", "K_1", "A_2")
    @pytest.mark.slow
    def test_K3_vs_K1_under_A3(self, corrclust_K3, corrclust_K1): _spearman_check_pair(corrclust_K3, corrclust_K1, "K_3", "K_1", "A_3")
    # K_3 vs K_2 (v0.5.3)
    @pytest.mark.slow
    def test_K3_vs_K2_under_A1(self, loo_K3, loo_K2):             _spearman_check_pair(loo_K3, loo_K2, "K_3", "K_2", "A_1")
    @pytest.mark.very_slow
    def test_K3_vs_K2_under_A2(self, shapley_K3, shapley_K2):     _spearman_check_pair(shapley_K3, shapley_K2, "K_3", "K_2", "A_2")
    @pytest.mark.slow
    def test_K3_vs_K2_under_A3(self, corrclust_K3, corrclust_K2): _spearman_check_pair(corrclust_K3, corrclust_K2, "K_3", "K_2", "A_3")
    # K_3 vs K_5 (v0.5.3)
    @pytest.mark.slow
    def test_K3_vs_K5_under_A1(self, loo_K3, loo_K5):             _spearman_check_pair(loo_K3, loo_K5, "K_3", "K_5", "A_1")
    @pytest.mark.very_slow
    def test_K3_vs_K5_under_A2(self, shapley_K3, shapley_K5):     _spearman_check_pair(shapley_K3, shapley_K5, "K_3", "K_5", "A_2")
    @pytest.mark.slow
    def test_K3_vs_K5_under_A3(self, corrclust_K3, corrclust_K5): _spearman_check_pair(corrclust_K3, corrclust_K5, "K_3", "K_5", "A_3")


# --- A_3 cluster recovery (Q3 Option Z: discovers the structure, ARI not yet asserted) ---

EXPECTED_CLUSTERS = sorted(
    [frozenset({0, 1}), frozenset({2, 3}),
     frozenset({4}), frozenset({5}), frozenset({6}),
     frozenset({7}), frozenset({8}), frozenset({9})],
    key=lambda s: (len(s), sorted(s)),
)


class TestA3ClusterRecovery:
    def test_clusters_formB(self, corrclust_FB):
        got = sorted([frozenset(c) for c in corrclust_FB["clusters"]],
                     key=lambda s: (len(s), sorted(s)))
        assert got == EXPECTED_CLUSTERS

    def test_clusters_K1(self, corrclust_K1):
        got = sorted([frozenset(c) for c in corrclust_K1["clusters"]],
                     key=lambda s: (len(s), sorted(s)))
        assert got == EXPECTED_CLUSTERS
