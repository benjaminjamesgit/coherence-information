"""R2 (cross-philosophy convergence) + property-recovery cross-tab for D1 (v0.7.0 slice 3b).

Given the induced w-vectors of grid cells (proxy x ablation), this module computes:

  * R2 -- the cross-philosophy median Spearman rank correlation of the w-vectors over
    decoupled estimator pairs (pre-reg threshold: median > 0.6, lower 95% CI > 0.4); and
  * the property-recovery cross-tab -- which of {A, B, C, D} each cell recovers, where a
    property is RECOVERED iff every one of its features outranks every distractor in w
    (the pre-registered rank-based "signal above distractors" criterion, margin-free).

Spearman is implemented here (no scipy dependency). A cell whose w-vector has zero
variance (e.g. a null proxy: all w = 0.5) yields an undefined Spearman -> NaN, excluded
from the median and reported as n_valid -- the honest treatment of the K1-null / A3-singleton
seams (findings F1/F2), not a silent drop.

`compute_a1_cell` runs one A1 (LOO) cell end-to-end; it is the unit the slice-3b grid fans
out over (the heavy K3/K4/K5 cells at locked T are run out-of-process and collected).
"""

from __future__ import annotations

import numpy as np

from cit.data.hsmm_d1 import ALPHABET, COHERENCE_BEARING, NOISE  # noqa: F401

__all__ = [
    "spearman",
    "cross_philosophy_r2",
    "recovered_properties",
    "build_cross_tab",
    "compute_cell",
    "compute_grid",
    "compute_a1_cell",
    "PROPERTY_FEATURES",
    "PROXIES",
    "ABLATIONS",
    "GRID_ABLATION_SEED",
]

# D1 property -> its feature index/indices (the M5 coherence-bearing partition)
PROPERTY_FEATURES = {"A": (0,), "B": (1,), "C": (2, 3), "D": (4,)}
GRID_ABLATION_SEED = 123

# grid axes (names; proxy/ablation callables resolved lazily in compute_cell)
PROXIES = ("K1", "K2", "K3", "K4", "K5")
ABLATIONS = ("A1", "A2", "A3")


def _avg_rank(a):
    """Average ranks (ties shared), 1-based."""
    a = np.asarray(a, dtype=np.float64)
    n = a.shape[0]
    order = np.argsort(a, kind="mergesort")
    sa = a[order]
    ranks = np.empty(n, dtype=np.float64)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sa[j + 1] == sa[i]:
            j += 1
        ranks[i:j + 1] = (i + j) / 2.0 + 1.0
        i = j + 1
    out = np.empty(n, dtype=np.float64)
    out[order] = ranks
    return out


def spearman(x, y):
    """Spearman rank correlation; NaN if either input has zero rank-variance."""
    rx, ry = _avg_rank(x), _avg_rank(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    denom = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    if denom == 0.0:
        return float("nan")
    return float((rx * ry).sum() / denom)


def _w_list(w):
    """w-dict (int feature -> value) as an ordered length-N_FEATURES list."""
    return [w[f] for f in range(len(w))]


def cross_philosophy_r2(w_by_cell, pairs=None):
    """Median Spearman over decoupled cell pairs.

    Parameters
    ----------
    w_by_cell : dict cell_name -> (dict feature -> w)
    pairs : list of (cell_a, cell_b), optional
        Decoupled pairs to correlate. Defaults to all unordered cell pairs.

    Returns
    -------
    dict: pair_rhos (name -> rho|nan), median (over valid pairs), n_valid, n_pairs.
    """
    cells = list(w_by_cell)
    if pairs is None:
        pairs = [(cells[i], cells[j]) for i in range(len(cells)) for j in range(i + 1, len(cells))]
    pair_rhos = {}
    for a, b in pairs:
        pair_rhos[f"{a}|{b}"] = spearman(_w_list(w_by_cell[a]), _w_list(w_by_cell[b]))
    valid = [r for r in pair_rhos.values() if not np.isnan(r)]
    return {
        "pair_rhos": pair_rhos,
        "median": float(np.median(valid)) if valid else float("nan"),
        "n_valid": len(valid),
        "n_pairs": len(pairs),
    }


def recovered_properties(w):
    """Set of properties in {A,B,C,D} the cell recovers: every feature outranks every distractor."""
    dist_max = max(w[d] for d in NOISE)
    return {p for p, feats in PROPERTY_FEATURES.items() if all(w[f] > dist_max for f in feats)}


def build_cross_tab(w_by_cell):
    """cell_name -> sorted list of recovered properties (the 15x4 deliverable, by cell)."""
    return {cell: sorted(recovered_properties(w)) for cell, w in w_by_cell.items()}


def compute_cell(proxy_name, ablation_name="A1", seed=7000, T=None):
    """Run one grid cell (proxy x ablation) end-to-end on a D1 stream; return w/rho vectors.

    Heavy cells (K3/K4/K5, and any A2 Shapley cell) at locked T are the very_slow / CI tier;
    this is the importable unit the grid driver and the CI verdict job call.
    """
    import numpy as _np
    from cit.data.hsmm_d1 import generate_stream
    from cit.proxies.categorical import (
        ngram_mdl_proxy_cat, neural_prequential_proxy_cat, mdl_hmm_proxy_cat,
        compression_delta_proxy_cat, lempel_parsing_proxy_cat,
    )
    from cit.ablations.categorical import (
        leave_one_out_ablation_cat, shapley_ablation_cat, correlation_cluster_ablation_cat,
    )
    from cit.induce_cat import induce_weights_cat

    proxies = {
        "K1": compression_delta_proxy_cat,
        "K2": ngram_mdl_proxy_cat,
        "K3": neural_prequential_proxy_cat,
        "K4": mdl_hmm_proxy_cat,
        "K5": lempel_parsing_proxy_cat,
    }
    ablations = {
        "A1": leave_one_out_ablation_cat,
        "A2": shapley_ablation_cat,
        "A3": correlation_cluster_ablation_cat,
    }
    obs = generate_stream(seed)[1]
    if T is not None:
        obs = obs[:T]
    res = induce_weights_cat(
        obs, ALPHABET, proxy=proxies[proxy_name],
        ablation=ablations[ablation_name], rng=_np.random.default_rng(GRID_ABLATION_SEED),
    )
    return {
        "cell": f"{proxy_name}x{ablation_name}",
        "seed": int(seed),
        "T": int(obs.shape[0]),
        "w": {int(k): float(v) for k, v in res["w"].items()},
        "rho": {int(k): float(v) for k, v in res["rho"].items()},
    }


def compute_a1_cell(proxy_name, seed=7000, T=None):
    """Back-compat shim for the A1 column (see compute_cell)."""
    return compute_cell(proxy_name, "A1", seed=seed, T=T)


def compute_grid(proxies=PROXIES, ablations=("A1",), seed=7000, T=None):
    """Compute a (proxies x ablations) grid; return {cell_name -> w-dict}.

    Default `ablations=("A1",)` is the feasible inline column; the full `ABLATIONS`
    (incl. A2 Shapley) at locked T is the very_slow CI verdict (hours for K3/K5 A2).
    """
    grid = {}
    for k in proxies:
        for a in ablations:
            res = compute_cell(k, a, seed=seed, T=T)
            grid[res["cell"]] = res["w"]
    return grid
