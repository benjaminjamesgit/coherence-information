"""Tests for the R2 + property-recovery cross-tab machinery (v0.7.0 slice 3b).

Fast tests lock the estimator-agnostic machinery (Spearman incl. the zero-variance NaN
seam, the rank-based recovery criterion, R2's exclusion of null cells). One slow test runs
a real A1 cell end-to-end (K2, the fast proxy) and checks it recovers its family property.
The full locked-T 5x3 grid (esp. A2 Shapley on K3/K4/K5) is a CI/very_slow artifact.
"""

import math

import numpy as np
import pytest

from cit.metacoherence import (
    spearman,
    cross_philosophy_r2,
    partition_diagnostic,
    recovered_properties,
    build_cross_tab,
    compute_a1_cell,
    compute_cell,
    compute_grid,
    PROXIES,
)

_PREVIEW_T = 8000


def test_spearman_perfect_anti_and_degenerate():
    assert abs(spearman([1, 2, 3, 4], [1, 2, 3, 4]) - 1.0) < 1e-12
    assert abs(spearman([1, 2, 3, 4], [4, 3, 2, 1]) + 1.0) < 1e-12
    assert abs(spearman([1, 2, 3, 4], [1, 3, 2, 4]) - 0.8) < 1e-9   # one swap
    assert math.isnan(spearman([1, 1, 1, 1], [1, 2, 3, 4]))        # zero variance -> NaN


def test_recovered_properties_rank_based():
    base = {i: 0.5 for i in range(8)}
    base[5] = 0.51  # a distractor sets the bar
    w = {**base, 0: 0.6, 4: 0.7}
    assert recovered_properties(w) == {"A", "D"}
    # C needs BOTH f2 and f3 above every distractor
    assert recovered_properties({**base, 2: 0.6, 3: 0.6}) == {"C"}
    assert recovered_properties({**base, 2: 0.6, 3: 0.5}) == set()   # only half the pair


def test_r2_excludes_null_cells():
    """A null cell (all w equal) yields NaN pairs, excluded from the median, counted in n_valid."""
    signal = {i: (0.6 if i in (0, 4) else 0.5) for i in range(8)}
    wbc = {"A": dict(signal), "B": dict(signal), "NULL": {i: 0.5 for i in range(8)}}
    r = cross_philosophy_r2(wbc)
    assert r["n_pairs"] == 3 and r["n_valid"] == 1
    assert r["median"] == 1.0
    assert math.isnan(r["pair_rhos"]["A|NULL"])


def test_build_cross_tab_shape():
    wbc = {"K2xA1": {i: (0.6 if i == 4 else 0.5) for i in range(8)}}
    tab = build_cross_tab(wbc)
    assert tab["K2xA1"] == ["D"]


def test_partition_diagnostic_bound_and_decomposition():
    """The +0.43 shared-partition bound, as a read-only diagnostic over given w-vectors."""
    # derived floor for n=8, k=5
    floor = partition_diagnostic({i: 0.5 for i in range(8)}, {i: 0.5 for i in range(8)})["partition_floor"]
    assert abs(floor - 0.4285714285) < 1e-9

    # identical vectors: shared top-k, spearman 1, no reshuffle, no proof of difference
    wa = {0: 0.9, 1: 0.8, 2: 0.7, 3: 0.6, 4: 0.55, 5: 0.4, 6: 0.3, 7: 0.2}
    d = partition_diagnostic(wa, wa)
    assert d["shared_top_k"] and d["top_k_a"] == [0, 1, 2, 3, 4]
    assert abs(d["spearman"] - 1.0) < 1e-12
    assert d["proves_partitions_differ"] is False
    assert abs(d["within_class_reshuffle"] - 0.0) < 1e-12

    # saved K1xA1 vs K3xA1 (3dp): spearman << floor -> PROVES the top-k partitions differ
    K1 = {0: 0.503, 1: 0.494, 2: 0.512, 3: 0.512, 4: 0.483, 5: 0.494, 6: 0.501, 7: 0.501}
    K3 = {0: 0.51, 1: 0.496, 2: 0.496, 3: 0.496, 4: 0.514, 5: 0.496, 6: 0.496, 7: 0.496}
    d = partition_diagnostic(K1, K3)
    assert d["spearman"] < d["partition_floor"]
    assert d["proves_partitions_differ"] is True
    assert d["shared_top_k"] is False           # K1 top-5 includes f6/f7; K3's is {f0,f4,f1,f2,f3}
    assert d["within_class_reshuffle"] is None   # undefined when partitions differ

    # validation
    import pytest as _pytest
    with _pytest.raises(ValueError):
        partition_diagnostic([0.1, 0.2], [0.1, 0.2, 0.3])   # length mismatch
    with _pytest.raises(ValueError):
        partition_diagnostic(wa, wa, k=8)                   # k must be < n


@pytest.mark.slow
def test_a1_cell_runs_and_recovers_family_property():
    """K2 x A1 end-to-end recovers D (drift, K2's family signal) and yields a valid w-vector."""
    res = compute_a1_cell("K2", seed=7000, T=15000)
    assert res["cell"] == "K2xA1" and res["T"] == 15000
    assert set(res["w"]) == set(range(8)) and all(0.0 < v < 1.0 for v in res["w"].values())
    assert "D" in recovered_properties(res["w"])


@pytest.fixture(scope="module")
def a1_grid():
    """The 5-proxy A1 column at a reduced, deterministic T (~3 min; only slow tests use it)."""
    return compute_grid(proxies=PROXIES, ablations=("A1",), seed=7000, T=_PREVIEW_T)


@pytest.mark.slow
def test_a1_column_is_complementary_not_convergent(a1_grid):
    """The recorded R2 seam: on D1's A1 column the modeling trio (K2/K3/K4) converges, but
    the compression/parsing proxies (K1/K5) recover DIFFERENT properties and diverge, so the
    cross-philosophy median falls far below the locked 0.6. Asserts structural facts (robust),
    not fragile per-feature rankings of near-0.5 weights."""
    wl = lambda cell: [a1_grid[f"{cell}xA1"][f] for f in range(8)]
    assert spearman(wl("K2"), wl("K4")) > 0.5          # modeling trio self-agrees
    assert spearman(wl("K1"), wl("K3")) < 0.3          # K1 diverges from a modeling proxy
    assert spearman(wl("K2"), wl("K5")) < 0.5          # K5 diverges (recovers more/other props)
    r2 = cross_philosophy_r2(a1_grid)
    assert r2["median"] < 0.4, r2["median"]            # far below the locked 0.6 -> the seam
    assert r2["n_valid"] == r2["n_pairs"] == 10        # post-fix: no null cells (K1 has variance)


@pytest.mark.slow
def test_a3_degenerates_to_a1_on_d1(a1_grid):
    """A3 correlation-clustering finds only singletons on D1 (couplings nonlinear/lagged),
    so K x A3 reproduces K x A1."""
    a3 = compute_cell("K2", "A3", seed=7000, T=_PREVIEW_T)
    w_a1 = [a1_grid["K2xA1"][f] for f in range(8)]
    w_a3 = [a3["w"][f] for f in range(8)]
    assert spearman(w_a1, w_a3) > 0.9
