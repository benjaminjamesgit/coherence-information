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
    "partition_diagnostic",
    "recovered_properties",
    "build_cross_tab",
    "crossing_delta",
    "crossing_assignment",
    "concordance_verdict",
    "twin_spearman",
    "decoupling_control_verdict",
    "CROSSING_REFS",
    "DECOUPLE_STABILITY_N",
    "DECOUPLE_CONFIDENT",
    "DECOUPLE_WEAK",
    "compute_cell",
    "compute_grid",
    "compute_a1_cell",
    "compute_decoupling_run",
    "DECOUPLE_PROXIES",
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


def partition_diagnostic(w_a, w_b, k=5):
    """Decompose a pair's Spearman via the shared-top-k-partition bound (read-only).

    Two rank-vectors over n features that BOTH place the same k features on top (and the
    same n-k on the bottom) cannot have an arbitrarily low Spearman: the worst case is
    both sub-orders fully reversed, giving a floor

        partition_floor = 1 - 6 * [k(k^2-1) + m(m^2-1)] / [3 * n(n^2-1)],   m = n - k

    (for n=8, k=5 this is +0.4286). So a Spearman BELOW the floor is a *proof* that the two
    top-k partitions differ -- the proxies are not even ranking the same k features as
    signal. At or above the floor with a shared top-k set, the remaining gap to 1.0 is pure
    within-class reshuffle. This makes the +0.43 bound a permanent diagnostic for splitting
    "different signal sets" from "same set, reordered".

    Pure function over two given w-vectors: no grid, no threshold, no locked constant.
    `partition_floor` is a derived combinatorial value, not a tunable parameter. Top-k ties
    are broken by lower feature index (deterministic); with display-rounded w those ties may
    be rounding artifacts.

    Parameters
    ----------
    w_a, w_b : dict {feature -> w} (keys 0..n-1) or length-n sequence
    k : int, default 5  -- size of the "signal" partition (D1: the 5 coherence-bearing features)

    Returns
    -------
    dict: spearman, k, partition_floor, shared_top_k (bool), top_k_a, top_k_b,
          proves_partitions_differ (spearman < floor), within_class_reshuffle (1 - spearman
          when the top-k sets match, else None).
    """
    a = _w_list(w_a) if isinstance(w_a, dict) else list(w_a)
    b = _w_list(w_b) if isinstance(w_b, dict) else list(w_b)
    n = len(a)
    if len(b) != n:
        raise ValueError(f"length mismatch: {n} vs {len(b)}")
    if not (1 <= k < n):
        raise ValueError(f"k must be in [1, n); got k={k}, n={n}")

    def _top_k(vals):
        order = sorted(range(n), key=lambda i: (-vals[i], i))   # value desc, index asc
        return frozenset(order[:k])

    top_a, top_b = _top_k(a), _top_k(b)
    shared = top_a == top_b

    m = n - k
    max_sum_d2 = (k * (k * k - 1) + m * (m * m - 1)) / 3.0
    floor = 1.0 - 6.0 * max_sum_d2 / (n * (n * n - 1))

    rho = spearman(a, b)
    rho_nan = bool(np.isnan(rho))
    return {
        "spearman": rho,
        "k": k,
        "partition_floor": float(floor),
        "shared_top_k": shared,
        "top_k_a": sorted(top_a),
        "top_k_b": sorted(top_b),
        "proves_partitions_differ": (not rho_nan) and rho < floor,
        "within_class_reshuffle": (float(1.0 - rho) if shared and not rho_nan else None),
    }


def recovered_properties(w):
    """Set of properties in {A,B,C,D} the cell recovers: every feature outranks every distractor."""
    dist_max = max(w[d] for d in NOISE)
    return {p for p, feats in PROPERTY_FEATURES.items() if all(w[f] > dist_max for f in feats)}


def build_cross_tab(w_by_cell):
    """cell_name -> sorted list of recovered properties (the 15x4 deliverable, by cell)."""
    return {cell: sorted(recovered_properties(w)) for cell, w in w_by_cell.items()}


# --------------------------------------------------------------------------- #
# Decoupling control (pre-reg 2026-06-23): twin-excluded nine-cell concordance #
# --------------------------------------------------------------------------- #
#
# Adjudicates whether D1's A1 {K1,K5}|{K2,K3,K4} split tracks coding PHILOSOPHY or stream
# REPRESENTATION, by crossing two MODELING functionals onto the byte stream (K3b, K2b;
# cit.proxies.crossing) and asking which block each joins. The decision Delta is TWIN-EXCLUDED
# and cross-functional: a crossing is compared to the modeling reference set with its OWN twin
# removed (K3b vs {K2,K4}, K2b vs {K3,K4}) minus the byte-stream set {K1,K5}, so the trivial
# same-functional / different-serialization twin correlation never inflates the modeling side.
# Pure functions over given w-vectors -- no grid, no proxy execution here.

DECOUPLE_STABILITY_N = 18      # per-proxy sign-count supermajority out of N_REPLICATES (=20)
DECOUPLE_CONFIDENT = 0.40      # |median Delta| >= -> CONFIDENT band
DECOUPLE_WEAK = 0.10          # |median Delta| >= -> WEAK-LEAN band (else NONE / ~0)

# twin-excluded cross-functional reference sets (the crossing's OWN twin is excluded from M)
CROSSING_REFS = {
    "K3b": {"twin": "K3", "M": ("K2", "K4"), "B": ("K1", "K5")},
    "K2b": {"twin": "K2", "M": ("K3", "K4"), "B": ("K1", "K5")},
}


def _mean_spearman_to(w_p, w_by_proxy, names):
    """Mean Spearman of w_p against each named proxy's w-vector; NaN (zero-variance) cells dropped."""
    rs = [spearman(_w_list(w_p), _w_list(w_by_proxy[x])) for x in names]
    rs = [r for r in rs if not np.isnan(r)]
    return float(np.mean(rs)) if rs else float("nan")


def crossing_delta(crossing, w_by_proxy):
    """One seed's twin-excluded cross-functional decision Delta for a crossing proxy.

        Delta = mean Spearman(w[crossing], w[M\\twin]) - mean Spearman(w[crossing], w[{K1,K5}])

    w_by_proxy maps proxy name -> {feature -> w} and must contain the crossing, its modeling
    reference set, and {K1, K5}. NaN if a needed side is entirely zero-variance.
    """
    if crossing not in CROSSING_REFS:
        raise ValueError(f"unknown crossing {crossing!r}; expected {tuple(CROSSING_REFS)}")
    ref = CROSSING_REFS[crossing]
    w_p = w_by_proxy[crossing]
    return _mean_spearman_to(w_p, w_by_proxy, ref["M"]) - _mean_spearman_to(w_p, w_by_proxy, ref["B"])


def crossing_assignment(deltas):
    """Per-proxy assignment from the per-seed Delta list (stability sign-count x two-band magnitude).

    deltas : sequence of per-seed Delta (length N_REPLICATES; NaN entries are allowed, ignored
             in the median, and counted toward NEITHER sign). Returns label in
             {MODELING, BYTE, UNSTABLE} + confidence sub-band + the Delta 90% interval (a
             REPORTED corroborator, NOT the locked decision -- that is the sign-count).
    """
    d = np.asarray(deltas, dtype=np.float64)
    finite = d[~np.isnan(d)]
    n_M = int(np.sum(d > 0.0))            # NaN > 0 is False
    n_B = int(np.sum(d < 0.0))            # NaN < 0 is False
    median_delta = float(np.median(finite)) if finite.size else float("nan")
    if finite.size:
        p5, p95 = float(np.percentile(finite, 5)), float(np.percentile(finite, 95))
    else:
        p5 = p95 = float("nan")
    ci90_excludes_zero = bool(finite.size and (p5 > 0.0 or p95 < 0.0))

    mag = abs(median_delta)
    confidence = ("CONFIDENT" if mag >= DECOUPLE_CONFIDENT
                  else "WEAK-LEAN" if mag >= DECOUPLE_WEAK else None)

    if n_M >= DECOUPLE_STABILITY_N and median_delta >= DECOUPLE_WEAK:
        label = "MODELING"
    elif n_B >= DECOUPLE_STABILITY_N and median_delta <= -DECOUPLE_WEAK:
        label = "BYTE"
    else:
        label, confidence = "UNSTABLE", None

    return {"label": label, "confidence": confidence, "n_M": n_M, "n_B": n_B,
            "n_seeds": int(d.size), "median_delta": median_delta,
            "ci90": (p5, p95), "ci90_excludes_zero": ci90_excludes_zero}


def _weaker(c_a, c_b):
    """The weaker of two confidence sub-bands (WEAK-LEAN dominates CONFIDENT)."""
    return "WEAK-LEAN" if ("WEAK-LEAN" in (c_a, c_b)) else "CONFIDENT"


def concordance_verdict(assign_k3b, assign_k2b):
    """Total nine-cell concordance verdict over (assignment(K3b), assignment(K2b)).

    The map is TOTAL over {MODELING, BYTE, UNSTABLE}^2 (pre-reg, fixed before any cell runs):
      (M, M) -> PHILOSOPHY                both join the modeling class despite the byte stream
      (B, B) -> REPRESENTATION_ARTIFACT   both join the byte block despite the modeling philosophy
      (M, B) / (B, M) -> PROXY_SPECIFIC_SPLIT
      any UNSTABLE    -> INCONCLUSIVE     concordance cannot rest on one crossing; a lone
                                          decisive crossing's lean is RECORDED, not terminal
    Same-direction confidence = the weaker of the two crossings' sub-bands.
    """
    a, b = assign_k3b["label"], assign_k2b["label"]
    lean = None
    if a == "MODELING" and b == "MODELING":
        verdict = "PHILOSOPHY"
        confidence = _weaker(assign_k3b["confidence"], assign_k2b["confidence"])
    elif a == "BYTE" and b == "BYTE":
        verdict = "REPRESENTATION_ARTIFACT"
        confidence = _weaker(assign_k3b["confidence"], assign_k2b["confidence"])
    elif {a, b} == {"MODELING", "BYTE"}:
        verdict, confidence = "PROXY_SPECIFIC_SPLIT", None
    else:
        verdict, confidence = "INCONCLUSIVE", None
        decisive = [(name, asg) for name, asg in (("K3b", assign_k3b), ("K2b", assign_k2b))
                    if asg["label"] in ("MODELING", "BYTE")]
        if len(decisive) == 1:
            name, asg = decisive[0]
            lean = {"proxy": name, "direction": asg["label"], "confidence": asg["confidence"]}
    return {"verdict": verdict, "confidence": confidence, "lean": lean,
            "assignments": {"K3b": assign_k3b, "K2b": assign_k2b}}


def twin_spearman(crossing, w_by_proxy):
    """Spearman(w[crossing], w[its twin]) -- the representation-invariance sanity check, REPORTED
    and NEVER a decision input. High = the functional is representation-stable (low-distortion)."""
    ref = CROSSING_REFS[crossing]
    return spearman(_w_list(w_by_proxy[crossing]), _w_list(w_by_proxy[ref["twin"]]))


def decoupling_control_verdict(per_seed_w):
    """Full decoupling-control verdict from the per-seed A1 w-vectors of all seven proxies.

    Parameters
    ----------
    per_seed_w : list over seeds of {proxy_name -> {feature -> w}}, each holding
                 K1,K2,K3,K4,K5 plus the crossings K3b,K2b (the A1 column at full-T).

    Returns
    -------
    dict: verdict / confidence / lean / assignments (from concordance_verdict), plus per-seed
          `deltas` {crossing -> [Delta per seed]} and `twin_sanity` {crossing -> median Spearman
          to its twin} (reported, not a decision input).
    """
    deltas = {c: [crossing_delta(c, w) for w in per_seed_w] for c in CROSSING_REFS}
    assignments = {c: crossing_assignment(deltas[c]) for c in CROSSING_REFS}
    out = concordance_verdict(assignments["K3b"], assignments["K2b"])
    twin = {}
    for c in CROSSING_REFS:
        ts = [twin_spearman(c, w) for w in per_seed_w]
        ts = [t for t in ts if not np.isnan(t)]
        twin[c] = float(np.median(ts)) if ts else float("nan")
    out["deltas"] = deltas
    out["twin_sanity"] = twin
    return out


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
    from cit.proxies.crossing import neural_prequential_byte_proxy, bigram_mdl_byte_proxy
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
        "K3b": neural_prequential_byte_proxy,    # decoupling-control crossing (modeling-on-byte)
        "K2b": bigram_mdl_byte_proxy,            # decoupling-control crossing (modeling-on-byte)
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


DECOUPLE_PROXIES = PROXIES + ("K3b", "K2b")    # the 5 grid proxies + the 2 decoupling crossings


def compute_decoupling_run(seeds=None, T=None):
    """Run the A1 decoupling control end-to-end: per seed -> 7-proxy w-vectors -> nine-cell verdict.

    For each seed, computes the A1 (LOO) induced-w vector for each of DECOUPLE_PROXIES
    ({K1..K5} + the crossings K3b, K2b) on the D1 stream, then feeds the per-seed
    {proxy -> w} list to `decoupling_control_verdict`. HEAVY at locked T (K3b ~ tens of
    minutes/seed -> ~20h over the 20-seed ensemble), so this is the CI/very_slow overnight
    artifact -- run it out-of-process via scripts/run_decoupling_control.py, NOT inline.

    Parameters
    ----------
    seeds : iterable of int, optional   -- defaults to the locked replicate ensemble (7000..7019)
    T : int, optional                   -- stream length; locked 50000 if None

    Returns
    -------
    dict: seeds, T, per_seed_w (list of {proxy -> {feature -> w}}), verdict
          (the full decoupling_control_verdict output).
    """
    from cit.data.hsmm_d1 import REPLICATE_SEEDS
    if seeds is None:
        seeds = REPLICATE_SEEDS
    seeds = list(seeds)
    per_seed_w = []
    for seed in seeds:
        per_seed_w.append({p: compute_cell(p, "A1", seed=seed, T=T)["w"] for p in DECOUPLE_PROXIES})
    return {"seeds": seeds, "T": T, "per_seed_w": per_seed_w,
            "verdict": decoupling_control_verdict(per_seed_w)}
