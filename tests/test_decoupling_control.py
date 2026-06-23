"""Tests for the decoupling-control metric (v0.7.0 pre-reg 2026-06-23).

Pure-logic tests over synthetic w-vectors / Delta lists -- no proxy execution. They lock the
load-bearing properties of the locked rule: (a) the decision Delta EXCLUDES each crossing's
own twin and is cross-functional; (b) the per-proxy 18/20 sign-count x two-band magnitude
assignment (incl. the ~0 guard that demotes a stable-sign-but-tiny-median to UNSTABLE);
(c) the concordance map is TOTAL over all nine (K3b x K2b) cells, with mixed cells routing to
INCONCLUSIVE + a recorded single-crossing lean; (d) twin Spearman is reported, never a decision
input. The heavy full-T x 20-seed run that feeds this metric is a separate CI/very_slow artifact.
"""

import math

import numpy as np
import pytest

from cit.metacoherence import (
    crossing_delta,
    crossing_assignment,
    concordance_verdict,
    twin_spearman,
    decoupling_control_verdict,
    CROSSING_REFS,
    DECOUPLE_STABILITY_N,
)


def _w(values):
    return {f: float(v) for f, v in enumerate(values)}


_IDENT = _w(range(8))                 # ranks 0..7
_REV = _w(range(7, -1, -1))           # reversed ranks -> Spearman(IDENT, REV) = -1


def _asg(label, confidence="CONFIDENT"):
    return {"label": label, "confidence": (None if label == "UNSTABLE" else confidence)}


# --------------------------------------------------------------------------- #
# (a) twin exclusion + cross-functional Delta                                  #
# --------------------------------------------------------------------------- #

def test_crossing_refs_exclude_own_twin():
    for c, ref in CROSSING_REFS.items():
        assert ref["twin"] not in ref["M"], c          # twin never in the modeling mean
        assert set(ref["M"]).isdisjoint(ref["B"])       # M and the byte set are disjoint


def test_crossing_delta_excludes_twin_K3b():
    """K3b aligned with its twin K3 (and {K1,K5}) but ANTI-aligned with cross-functional {K2,K4}:
    the twin-EXCLUDED Delta is -2.0; a twin-INCLUDED mean would have given -4/3. The metric must
    return -2.0 -- i.e. K3 is not in K3b's modeling mean."""
    wbp = {"K3b": _IDENT, "K3": _IDENT, "K1": _IDENT, "K5": _IDENT, "K2": _REV, "K4": _REV}
    d = crossing_delta("K3b", wbp)
    assert abs(d - (-2.0)) < 1e-9                        # mean(K2,K4)=-1 minus mean(K1,K5)=+1
    assert abs(d - (-4.0 / 3.0)) > 0.5                  # NOT the twin-included value


def test_crossing_delta_excludes_twin_K2b():
    wbp = {"K2b": _IDENT, "K2": _IDENT, "K1": _IDENT, "K5": _IDENT, "K3": _REV, "K4": _REV}
    d = crossing_delta("K2b", wbp)
    assert abs(d - (-2.0)) < 1e-9                        # M={K3,K4}=-1 minus B={K1,K5}=+1


def test_crossing_delta_unknown_raises():
    with pytest.raises(ValueError):
        crossing_delta("K9b", {"K9b": _IDENT})


def test_twin_spearman_is_reported_not_in_delta():
    wbp = {"K3b": _IDENT, "K3": _IDENT, "K1": _IDENT, "K5": _IDENT, "K2": _REV, "K4": _REV}
    assert abs(twin_spearman("K3b", wbp) - 1.0) < 1e-12      # K3b == K3 -> +1
    # the +1 twin correlation does NOT enter the decision Delta (still -2.0)
    assert abs(crossing_delta("K3b", wbp) - (-2.0)) < 1e-9


# --------------------------------------------------------------------------- #
# (b) per-proxy assignment: stability sign-count x two-band magnitude          #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("deltas, label, conf", [
    ([0.6] * 20, "MODELING", "CONFIDENT"),
    ([0.2] * 20, "MODELING", "WEAK-LEAN"),
    ([0.05] * 20, "UNSTABLE", None),                    # stable sign but |median| < 0.10 -> ~0 guard
    ([-0.6] * 20, "BYTE", "CONFIDENT"),
    ([-0.2] * 20, "BYTE", "WEAK-LEAN"),
    ([0.5] * 19 + [-0.5], "MODELING", "CONFIDENT"),     # n_M = 19 >= 18
    ([0.5] * 17 + [-0.5] * 3, "UNSTABLE", None),        # n_M = 17 < 18 -> unstable
    ([0.5] * 10 + [-0.5] * 10, "UNSTABLE", None),       # sign split
])
def test_crossing_assignment_bands(deltas, label, conf):
    a = crossing_assignment(deltas)
    assert a["label"] == label
    assert a["confidence"] == conf
    assert a["n_seeds"] == 20


def test_crossing_assignment_ci90():
    pos = crossing_assignment([0.6] * 20)
    assert pos["ci90_excludes_zero"] is True            # all positive -> interval excludes 0
    mixed = crossing_assignment([0.5] * 11 + [-0.5] * 9)
    assert mixed["ci90_excludes_zero"] is False         # straddles 0


def test_crossing_assignment_nan_seeds_reduce_stability():
    """NaN Delta (a zero-variance cell that seed) counts toward NEITHER sign, so it lowers the
    sign-count -- conservative, the locked treatment."""
    a = crossing_assignment([float("nan")] * 2 + [0.5] * 18)
    assert a["n_M"] == 18 and a["label"] == "MODELING"  # exactly 18 positive -> just clears
    b = crossing_assignment([float("nan")] * 5 + [0.5] * 15)
    assert b["n_M"] == 15 and b["label"] == "UNSTABLE"  # NaN seeds drop it below 18
    assert not math.isnan(b["median_delta"])            # median over the finite seeds


# --------------------------------------------------------------------------- #
# (c) total nine-cell concordance verdict                                      #
# --------------------------------------------------------------------------- #

def test_concordance_verdict_is_total_over_nine_cells():
    """Every (K3b, K2b) in {MODELING,BYTE,UNSTABLE}^2 maps to exactly one verdict; mixed
    (one decisive, one UNSTABLE) -> INCONCLUSIVE with the single-crossing lean recorded."""
    labels = ("MODELING", "BYTE", "UNSTABLE")
    expected = {
        ("MODELING", "MODELING"): "PHILOSOPHY",
        ("BYTE", "BYTE"): "REPRESENTATION_ARTIFACT",
        ("MODELING", "BYTE"): "PROXY_SPECIFIC_SPLIT",
        ("BYTE", "MODELING"): "PROXY_SPECIFIC_SPLIT",
        ("MODELING", "UNSTABLE"): "INCONCLUSIVE",
        ("UNSTABLE", "MODELING"): "INCONCLUSIVE",
        ("BYTE", "UNSTABLE"): "INCONCLUSIVE",
        ("UNSTABLE", "BYTE"): "INCONCLUSIVE",
        ("UNSTABLE", "UNSTABLE"): "INCONCLUSIVE",
    }
    seen = set()
    for a in labels:
        for b in labels:
            v = concordance_verdict(_asg(a), _asg(b))
            assert v["verdict"] == expected[(a, b)], (a, b)
            seen.add((a, b))
            # mixed (exactly one decisive) records a lean; pure cases do not
            decisive = [x for x in (a, b) if x != "UNSTABLE"]
            if len(decisive) == 1:
                assert v["lean"] is not None and v["lean"]["direction"] == decisive[0]
            else:
                assert v["lean"] is None
    assert seen == set(expected)                        # all nine covered, none missing


def test_concordance_confidence_is_weaker_of_two():
    assert concordance_verdict(_asg("MODELING", "CONFIDENT"),
                               _asg("MODELING", "CONFIDENT"))["confidence"] == "CONFIDENT"
    assert concordance_verdict(_asg("MODELING", "CONFIDENT"),
                               _asg("MODELING", "WEAK-LEAN"))["confidence"] == "WEAK-LEAN"
    assert concordance_verdict(_asg("BYTE", "WEAK-LEAN"),
                               _asg("BYTE", "WEAK-LEAN"))["confidence"] == "WEAK-LEAN"


def test_inconclusive_lean_proxy_identity():
    v = concordance_verdict(_asg("UNSTABLE"), _asg("BYTE"))
    assert v["verdict"] == "INCONCLUSIVE"
    assert v["lean"] == {"proxy": "K2b", "direction": "BYTE", "confidence": "CONFIDENT"}


# --------------------------------------------------------------------------- #
# (d) end-to-end: per-seed w-vectors -> verdict                                #
# --------------------------------------------------------------------------- #

def _seed_w(modeling_vec, byte_vec, k3b_vec, k2b_vec):
    return {"K1": byte_vec, "K5": byte_vec, "K2": modeling_vec, "K3": modeling_vec,
            "K4": modeling_vec, "K3b": k3b_vec, "K2b": k2b_vec}


def test_decoupling_control_verdict_philosophy():
    """Both crossings track the modeling block across 20 seeds -> PHILOSOPHY CONFIDENT."""
    per_seed = [_seed_w(_IDENT, _REV, _IDENT, _IDENT) for _ in range(20)]
    out = decoupling_control_verdict(per_seed)
    assert out["verdict"] == "PHILOSOPHY" and out["confidence"] == "CONFIDENT"
    assert out["assignments"]["K3b"]["label"] == "MODELING"
    assert out["assignments"]["K2b"]["label"] == "MODELING"
    assert all(abs(d - 2.0) < 1e-9 for d in out["deltas"]["K3b"])   # +2 each seed
    assert out["twin_sanity"]["K3b"] == 1.0 and out["twin_sanity"]["K2b"] == 1.0


def test_decoupling_control_verdict_proxy_specific_split():
    """K3b tracks modeling, K2b tracks the byte block -> PROXY_SPECIFIC_SPLIT (a finding)."""
    per_seed = [_seed_w(_IDENT, _REV, _IDENT, _REV) for _ in range(20)]
    out = decoupling_control_verdict(per_seed)
    assert out["verdict"] == "PROXY_SPECIFIC_SPLIT"
    assert out["assignments"]["K3b"]["label"] == "MODELING"
    assert out["assignments"]["K2b"]["label"] == "BYTE"
