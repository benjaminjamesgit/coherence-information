"""v0.6.0 coherence-capacity estimator tests.

Locks (pre_registration.md, 2026-06-23 amendment):

  - the w = 1 Shannon-capacity boundary (the spine; Cor 4.4),
  - the CORRECTED Binary Coherence Channel fixture (the paper's Sec 6
    0.5(1+eps) is I_w at the uniform input -- a lower bound, not the capacity),
  - the lower-bound relation C_C(eps) >= 0.5(1+eps),
  - the P2 bound 0 <= C_C <= C_Shannon,
  - determinism (bit-identical), monotonicity in a uniform weight scale,
  - and an analytic-gradient finite-difference check.

All fast tier (small DMCs, sub-second per call); no slow marker.

References
----------
James, B. (2025). Capacity and Compression Theorems. PhilPapers.
"""

from __future__ import annotations

import numpy as np
import pytest

from cit.capacity import _iw_input_gradient, coherence_capacity
from cit.information import coherence_weighted_mutual_information

LN2 = np.log(2.0)


def binary_entropy(p: float) -> float:
    if p in (0.0, 1.0):
        return 0.0
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


def bsc(p: float) -> np.ndarray:
    return np.array([[1 - p, p], [p, 1 - p]])


def zchannel(f: float) -> np.ndarray:
    return np.array([[1.0, 0.0], [f, 1.0 - f]])


IDENTITY = np.eye(2)


# ---------------------------------------------------------------------------
# The boundary spine: w = 1  =>  C_C == Shannon channel capacity (Cor 4.4)
# ---------------------------------------------------------------------------
class TestBoundarySpine:
    @pytest.mark.parametrize("p", [0.1, 0.25])
    def test_bsc_recovers_shannon(self, p):
        out = coherence_capacity(bsc(p))  # weights default to all-ones
        assert out["C_C"] == pytest.approx(1.0 - binary_entropy(p), abs=1e-6)
        # symmetric channel: capacity-achieving input is uniform
        assert out["argmax_input"] == pytest.approx([0.5, 0.5], abs=1e-3)

    def test_zchannel_recovers_shannon(self):
        # Z-channel f=0.5: Shannon capacity = log2(5/4) = 0.321928...
        out = coherence_capacity(zchannel(0.5))
        assert out["C_C"] == pytest.approx(np.log2(1.25), abs=1e-6)

    def test_identity_w1_is_one_bit(self):
        out = coherence_capacity(IDENTITY)  # w=1: capacity 1 bit at uniform
        assert out["C_C"] == pytest.approx(1.0, abs=1e-9)
        assert out["argmax_input"] == pytest.approx([0.5, 0.5], abs=1e-4)


# ---------------------------------------------------------------------------
# Corrected Binary Coherence Channel fixture: identity channel, w = (1, eps)
# ---------------------------------------------------------------------------
class TestCorrectedFixture:
    def test_eps0_closed_form(self):
        # I_w = -q log2 q (w(1)=0 kills the other term); max at q*=1/e
        out = coherence_capacity(IDENTITY, [1.0, 0.0])
        # atol 1e-8: locked tol=1e-10 floors at ~1e-9 on this flat max (q*=1/e);
        # solver verified correct -- tighter tol converges to the exact value.
        assert out["C_C"] == pytest.approx(1.0 / (np.e * LN2), abs=1e-8)
        assert out["argmax_input"][0] == pytest.approx(1.0 / np.e, abs=1e-4)

    def test_eps1_closed_form(self):
        out = coherence_capacity(IDENTITY, [1.0, 1.0])
        assert out["C_C"] == pytest.approx(1.0, abs=1e-8)

    @pytest.mark.parametrize(
        "eps,expected",
        [(0.25, 0.639687), (0.50, 0.755588), (0.75, 0.876210)],
    )
    def test_grid_verified_interior(self, eps, expected):
        out = coherence_capacity(IDENTITY, [1.0, eps])
        assert out["C_C"] == pytest.approx(expected, abs=1e-5)
        # uniform is NOT optimal for eps<1: the maximizer tilts to q* < 0.5
        assert out["argmax_input"][0] < 0.5

    @pytest.mark.parametrize("eps", [0.0, 0.25, 0.5, 0.75, 1.0])
    def test_lower_bound_relation(self, eps):
        out = coherence_capacity(IDENTITY, [1.0, eps])
        at_uniform = 0.5 * (1.0 + eps)
        # C_C >= I_w@uniform always; strict for eps<1, equality at eps=1
        assert out["C_C"] >= at_uniform - 1e-9
        if eps < 1.0:
            assert out["C_C"] > at_uniform + 1e-4
        else:
            assert out["C_C"] == pytest.approx(at_uniform, abs=1e-8)

    def test_paper_value_is_iw_at_uniform(self):
        # The demotion, made concrete: 0.5(1+eps) IS exactly I_w at uniform.
        for eps in (0.0, 0.25, 0.5, 0.75, 1.0):
            joint = np.array([[0.5, 0.0], [0.0, 0.5]])  # uniform input, identity
            val = coherence_weighted_mutual_information(joint, [1.0, eps])
            assert val == pytest.approx(0.5 * (1.0 + eps), abs=1e-12)


# ---------------------------------------------------------------------------
# Property P2: 0 <= C_C <= C_Shannon on every channel
# ---------------------------------------------------------------------------
class TestP2Bound:
    CHANNELS = [
        (IDENTITY, 1.0),
        (bsc(0.1), 1.0 - binary_entropy(0.1)),
        (zchannel(0.5), float(np.log2(1.25))),
    ]

    @pytest.mark.parametrize("channel,shannon", CHANNELS)
    @pytest.mark.parametrize("w", [[1.0, 0.5], [0.3, 0.9], [0.0, 0.0]])
    def test_bounded(self, channel, shannon, w):
        cc = coherence_capacity(channel, w)["C_C"]
        assert cc >= -1e-12
        assert cc <= shannon + 1e-9


# ---------------------------------------------------------------------------
# Determinism: no RNG, bit-identical across calls
# ---------------------------------------------------------------------------
class TestDeterminism:
    def test_bit_identical(self):
        a = coherence_capacity(bsc(0.2), [1.0, 0.4])
        b = coherence_capacity(bsc(0.2), [1.0, 0.4])
        assert a["C_C"] == b["C_C"]  # exact equality, no tolerance
        assert np.array_equal(a["argmax_input"], b["argmax_input"])


# ---------------------------------------------------------------------------
# Monotonicity: scaling all weights up toward 1 cannot decrease C_C
# ---------------------------------------------------------------------------
class TestMonotonicity:
    def test_cc_nondecreasing_in_weight_scale(self):
        w0 = np.array([0.2, 0.6])
        prev = -np.inf
        for s in np.linspace(0.0, 1.0, 6):
            w = (1 - s) * w0 + s * 1.0  # w(s) -> 1 as s -> 1
            cc = coherence_capacity(IDENTITY, w)["C_C"]
            assert cc >= prev - 1e-9
            prev = cc


# ---------------------------------------------------------------------------
# Multi-start agreement: the empirical concavity / uniqueness stand-in
# ---------------------------------------------------------------------------
class TestUniquenessStandIn:
    @pytest.mark.parametrize("w", [[1.0, 0.0], [1.0, 0.5]])
    def test_near_optimal_starts_agree(self, w):
        out = coherence_capacity(IDENTITY, w)
        assert out["n_starts"] >= 20
        assert out["argmax_agreement_linf"] < 1e-3


# ---------------------------------------------------------------------------
# Analytic input gradient vs central finite differences along the simplex
# ---------------------------------------------------------------------------
class TestGradient:
    @staticmethod
    def _fd_dir(channel, w, p, i, j, h=1e-6):
        d = np.zeros_like(p)
        d[i], d[j] = 1.0, -1.0
        fp = coherence_weighted_mutual_information((p + h * d)[:, None] * channel, w)
        fm = coherence_weighted_mutual_information((p - h * d)[:, None] * channel, w)
        return (fp - fm) / (2 * h)

    @pytest.mark.parametrize("w", [[1.0, 1.0], [1.0, 0.3], [0.7, 0.2]])
    def test_binary_gradient(self, w):
        channel = bsc(0.15)
        p = np.array([0.4, 0.6])
        g = _iw_input_gradient(p, channel, w)
        fd = self._fd_dir(channel, np.asarray(w, float), p, 0, 1)
        # only gradient differences are identifiable on the simplex
        assert (g[0] - g[1]) == pytest.approx(fd, abs=1e-6)

    def test_ternary_gradient(self):
        channel = np.array([[0.7, 0.2, 0.1], [0.1, 0.8, 0.1], [0.2, 0.2, 0.6]])
        w = np.array([1.0, 0.5, 0.25])
        p = np.array([0.3, 0.3, 0.4])
        g = _iw_input_gradient(p, channel, w)
        for (i, j) in [(0, 1), (1, 2), (0, 2)]:
            fd = self._fd_dir(channel, w, p, i, j)
            assert (g[i] - g[j]) == pytest.approx(fd, abs=1e-6)
